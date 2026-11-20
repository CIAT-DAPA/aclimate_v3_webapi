from fastapi import APIRouter, HTTPException, Query
from typing import Any, Dict, List
import logging
import re

from schemas.geoserver import AdminAreaLayer

from services.geoserver import (
    GEOSERVER_ADMIN_MAX_FEATURES,
    GEOSERVER_ADMIN_WORKSPACE,
    GeoServerRequestError,
    build_text_search_cql,
    get_geoserver_auth,
    get_wfs_features,
    get_wfs_layer_text_fields,
    list_wfs_layers,
)

router = APIRouter(tags=["Geoserver"], prefix="/geoserver/admin-areas")

# ---------- Logger ----------
logger = logging.getLogger(__name__)

# ---------- Constants ----------
# Layer naming convention: "{prefix}_adm{level}" with an optional suffix (e.g. "et_adm3_wp")
ADMIN_LAYER_PATTERN = re.compile(r"^(?P<prefix>.+)_adm(?P<level>\d+)(?:_.*)?$", re.IGNORECASE)


def parse_admin_layer(layer: str) -> AdminAreaLayer:
    """
    Describe a layer of administrative areas from its name.

    - **layer**: Layer name (e.g. "colombia_adm1").

    Returns the layer with its prefix and administrative level (0 = country,
    1 = admin 1, ...). Both are None when the name does not follow the
    "{prefix}_adm{level}" convention.
    """
    match = ADMIN_LAYER_PATTERN.match(layer)
    # Layers that do not follow the convention are listed without prefix and level
    if not match:
        return AdminAreaLayer(layer=layer, prefix=None, level=None)
    return AdminAreaLayer(layer=layer, prefix=match.group("prefix"), level=int(match.group("level")))


@router.get("/layers", response_model=List[AdminAreaLayer])
def get_admin_area_layers():
    """
    Returns the layers with administrative areas available in GeoServer.

    Each layer has its name, the prefix that identifies the country or region and
    the administrative level (0 = country, 1 = admin 1, 2 = admin 2, ...). Prefix and
    level are null for layers whose name does not follow "{prefix}_adm{level}".

    Use the layer name in `/geoserver/admin-areas/polygon` to get its polygons.
    """
    try:
        # Validate credentials are configured
        get_geoserver_auth()

        layers = list_wfs_layers(GEOSERVER_ADMIN_WORKSPACE)
        return [parse_admin_layer(layer) for layer in layers]

    except HTTPException:
        raise
    except GeoServerRequestError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        logger.error("Error listing admin area layers: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Error processing data: {str(e)}")


@router.get(
    "/polygon",
    responses={
        200: {
            "description": "GeoJSON FeatureCollection (EPSG:4326) with the polygons that match the description",
            "content": {
                "application/json": {
                    "example": {
                        "type": "FeatureCollection",
                        "features": [
                            {
                                "type": "Feature",
                                "id": "colombia_adm1.31",
                                "geometry": {
                                    "type": "MultiPolygon",
                                    "coordinates": [[[[-76.5, 3.1], [-76.4, 3.1], [-76.4, 3.2], [-76.5, 3.1]]]]
                                },
                                "properties": {"ADM1_ES": "Valle del Cauca", "ADM1_PCODE": "CO76"}
                            }
                        ]
                    }
                }
            }
        },
        404: {
            "description": "The layer does not exist or no polygon matches the description",
            "content": {
                "application/json": {
                    "example": {"detail": "No polygon found in layer 'colombia_adm1' for description 'Atlantis'"}
                }
            }
        },
        502: {
            "description": "GeoServer is not available or returned an error",
            "content": {
                "application/json": {
                    "example": {"detail": "GeoServer WFS request failed: ..."}
                }
            }
        }
    }
)
def get_admin_area_polygon(
    layer: str = Query(..., min_length=1, description="Layer name, as returned by /geoserver/admin-areas/layers (e.g. 'colombia_adm1')"),
    description: str = Query(..., min_length=1, description="Text to search in the text attributes of the layer (e.g. 'Valle del Cauca')"),
) -> Dict[str, Any]:
    """
    Gets the polygons of an administrative area as GeoJSON.

    The description is searched (partial match, case-insensitive) in every text
    attribute of the layer, because each layer has its own attribute names. All the
    polygons that match are returned in a FeatureCollection in EPSG:4326, with the
    original attributes of the layer in `properties`.

    The response can be used as the `polygon` of `/geoserver/polygon-data`.

    - **layer**: Layer name, as returned by `/geoserver/admin-areas/layers`
    - **description**: Text to search in the text attributes of the layer
    """
    try:
        # Validate credentials are configured
        get_geoserver_auth()

        search_text = description.strip()
        # A description made only of spaces would match every polygon of the layer
        if not search_text:
            raise HTTPException(status_code=422, detail="description must not be empty")

        # Only layers published in the administrative workspace can be requested
        if layer not in list_wfs_layers(GEOSERVER_ADMIN_WORKSPACE):
            raise HTTPException(status_code=404, detail=f"Layer '{layer}' not found")

        text_fields = get_wfs_layer_text_fields(GEOSERVER_ADMIN_WORKSPACE, layer)
        # Without text attributes there is nothing to compare the description with
        if not text_fields:
            raise HTTPException(status_code=404, detail=f"Layer '{layer}' has no text attributes to search in")

        cql_filter = build_text_search_cql(text_fields, search_text)
        collection = get_wfs_features(
            GEOSERVER_ADMIN_WORKSPACE, layer, cql_filter, GEOSERVER_ADMIN_MAX_FEATURES
        )

        features = []
        # Keep the standard GeoJSON members of every feature that has a geometry
        for feature in collection.get("features") or []:
            # Records without geometry are not polygons and are left out
            if not feature.get("geometry"):
                continue
            features.append({
                "type": "Feature",
                "id": feature.get("id"),
                "geometry": feature["geometry"],
                "properties": feature.get("properties") or {},
            })

        # No polygon of the layer contains the description
        if not features:
            raise HTTPException(
                status_code=404,
                detail=f"No polygon found in layer '{layer}' for description '{search_text}'",
            )

        return {"type": "FeatureCollection", "features": features}

    except HTTPException:
        raise
    except GeoServerRequestError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        logger.error("Error processing admin area polygon request: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Error processing data: {str(e)}")
