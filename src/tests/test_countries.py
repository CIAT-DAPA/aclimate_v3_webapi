from unittest.mock import patch

from conftest import client, MockMeasure, MockIndicator, MockIndicatorCategory

COUNTRY_SERVICE = "aclimate_v3_orm.services.mng_country_service.MngCountryService.get_all_enable"
CLIMATE_SERVICE = (
    "aclimate_v3_orm.services.mng_country_climate_measure_service."
    "MngCountryClimateMeasureService.get_by_country"
)
INDICATOR_SERVICE = (
    "aclimate_v3_orm.services.mng_country_indicator_service."
    "MngCountryIndicatorService.get_by_country"
)

# Keys that must never be exposed inside conf_climate / conf_indicator items
FORBIDDEN_ID_KEYS = {"id", "country_id", "measure_id", "indicator_id", "indicator_category_id"}


class MockCountryClimateMeasure:
    """Mock of a mng_country_climate_measure record with its related measure."""

    def __init__(self, id, country_id, measure, spatial_climate_conf=None,
                 location_climate_conf=None, description=None):
        self.id = id
        self.country_id = country_id
        self.measure_id = measure.id if measure else None
        self.measure = measure
        self.spatial_forecast = False
        self.spatial_climate = True
        self.location_forecast = False
        self.location_climate = True
        self.spatial_climate_conf = spatial_climate_conf
        self.location_climate_conf = location_climate_conf
        self.description = description


class MockCountryIndicator:
    """Mock of a mng_country_indicator record with its related indicator."""

    def __init__(self, id, country_id, indicator, criteria=None, description=None,
                 store=None, workspace=None):
        self.id = id
        self.country_id = country_id
        self.indicator_id = indicator.id if indicator else None
        self.indicator = indicator
        self.spatial_forecast = False
        self.spatial_climate = True
        self.location_forecast = False
        self.location_climate = True
        self.criteria = criteria
        self.description = description
        self.store = store
        self.workspace = workspace


def _climate_by_country(country_id):
    """Return the mocked climate configuration: only country 1 has measures."""
    # Country 1 has one enabled and one disabled measure, other countries have none
    if country_id != 1:
        return []
    enabled = MockMeasure(8, "Precipitation", "prec", "mm", "Total precipitation")
    disabled = MockMeasure(9, "Wind speed", "wind", "m/s", enable=False)
    return [
        MockCountryClimateMeasure(
            6, 1, enabled,
            spatial_climate_conf=[
                {"temporality": "daily", "store": "daily_co_prec", "workspace": "climate_historical_daily"},
            ],
            location_climate_conf=["daily", "monthly"],
            description="Country specific description",
        ),
        MockCountryClimateMeasure(7, 1, disabled),
    ]


def _indicator_by_country(country_id):
    """Return the mocked indicator configuration: only country 1 has indicators."""
    # Country 1 has one enabled and one disabled indicator, other countries have none
    if country_id != 1:
        return []
    enabled = MockIndicator(7, "Cold days", "TX10p", "% days/year", type="climate",
                            temporality="annual", description="Days below percentile 10")
    enabled.category = MockIndicatorCategory(1, "Extreme temperatures", "Temperature extremes")
    disabled = MockIndicator(8, "Frost days", "FD", "days", enable=False)
    disabled.category = None
    return [
        MockCountryIndicator(3, 1, enabled, criteria={"admin_level": 2},
                             description="Cold days for the country",
                             store="index_co_tx10p", workspace="climate_index"),
        MockCountryIndicator(4, 1, disabled),
    ]


def test_get_all_countries(mock_countries):
    with patch(COUNTRY_SERVICE, return_value=mock_countries), \
         patch(CLIMATE_SERVICE, return_value=[]), \
         patch(INDICATOR_SERVICE, return_value=[]):
        response = client.get("/countries")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        for item in data:
            assert "id" in item
            assert "name" in item
            assert "iso2" in item
            # Countries without configuration return empty lists
            assert item["conf_climate"] == []
            assert item["conf_indicator"] == []


def test_get_all_countries_with_configuration(mock_countries):
    with patch(COUNTRY_SERVICE, return_value=mock_countries), \
         patch(CLIMATE_SERVICE, side_effect=_climate_by_country), \
         patch(INDICATOR_SERVICE, side_effect=_indicator_by_country):
        response = client.get("/countries")
        assert response.status_code == 200

        data = response.json()
        colombia, ecuador = data[0], data[1]

        # The country keeps its own id
        assert colombia["id"] == 1

        # Only the enabled measure is returned, as a single flat object
        assert colombia["conf_climate"] == [
            {
                "name": "Precipitation",
                "short_name": "prec",
                "unit": "mm",
                "description": "Total precipitation",
                "country_description": "Country specific description",
                "spatial_forecast": False,
                "spatial_climate": True,
                "location_forecast": False,
                "location_climate": True,
                "spatial_climate_conf": [
                    {"temporality": "daily", "store": "daily_co_prec", "workspace": "climate_historical_daily"},
                ],
                "location_climate_conf": ["daily", "monthly"],
            }
        ]

        # Only the enabled indicator is returned, with indicator and category data
        assert colombia["conf_indicator"] == [
            {
                "type": "climate",
                "name": "Cold days",
                "short_name": "TX10p",
                "unit": "% days/year",
                "temporality": "annual",
                "description": "Days below percentile 10",
                "category_name": "Extreme temperatures",
                "category_description": "Temperature extremes",
                "country_description": "Cold days for the country",
                "spatial_forecast": False,
                "spatial_climate": True,
                "location_forecast": False,
                "location_climate": True,
                "criteria": {"admin_level": 2},
                "store": "index_co_tx10p",
                "workspace": "climate_index",
            }
        ]

        # No IDs are exposed inside the configuration lists
        for conf_item in colombia["conf_climate"] + colombia["conf_indicator"]:
            assert FORBIDDEN_ID_KEYS.isdisjoint(conf_item.keys())

        # A country without configuration returns empty lists
        assert ecuador["conf_climate"] == []
        assert ecuador["conf_indicator"] == []


def test_get_all_countries_returns_400_when_configuration_fails(mock_countries):
    with patch(COUNTRY_SERVICE, return_value=mock_countries), \
         patch(CLIMATE_SERVICE, side_effect=Exception("database down")), \
         patch(INDICATOR_SERVICE, return_value=[]):
        response = client.get("/countries")
        assert response.status_code == 400
        assert "Error fetching countries" in response.json()["detail"]
