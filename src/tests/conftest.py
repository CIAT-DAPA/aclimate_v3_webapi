"""
Shared fixtures and utilities for all tests.
"""
import os
import sys
from unittest.mock import patch, MagicMock
from datetime import date

import pytest
from fastapi.testclient import TestClient

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import app
from dependencies.auth_dependencies import get_current_user

# ---------- Client ----------
client = TestClient(app)

# ---------- Mock user ----------
_MOCK_USER = {"sub": "user123", "preferred_username": "mockuser", "token_type": "user"}


@pytest.fixture(autouse=True)
def mock_auth():
    """Automatically mock authentication for all tests."""
    app.dependency_overrides[get_current_user] = lambda: _MOCK_USER
    yield
    app.dependency_overrides = {}


# ---------- Mock model classes ----------

class MockCountry:
    def __init__(self, id, name, iso2):
        self.id = id
        self.name = name
        self.iso2 = iso2


class MockAdmin1:
    def __init__(self, id, name, country, ext_id):
        self.id = id
        self.name = name
        self.country = country
        self.ext_id = ext_id


class MockAdmin2:
    def __init__(self, id, name, admin_1, ext_id):
        self.id = id
        self.name = name
        self.admin_1 = admin_1
        self.ext_id = ext_id


class MockSource:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name


class MockLocation:
    def __init__(self, id, name, ext_id, machine_name, visible, admin_2,
                 altitude=100.0, latitude=3.45, longitude=-76.53,
                 source_name="IDEAM", source_id=1, source_type="weather_station",
                 enable=True):
        self.id = id
        self.name = name
        self.ext_id = ext_id
        self.machine_name = machine_name
        self.visible = visible
        self.admin_2 = admin_2
        self.altitude = altitude
        self.latitude = latitude
        self.longitude = longitude
        self.enable = enable
        self.source_id = source_id
        self.source = MockSource(source_name)
        self.source.source_type = source_type


class MockMeasure:
    def __init__(self, id, name, short_name, unit, description=None, enable=True):
        self.id = id
        self.name = name
        self.short_name = short_name
        self.unit = unit
        self.description = description or name
        self.enable = enable


class MockIndicator:
    def __init__(self, id, name, short_name, unit, type="CLIMATE",
                 temporality="MONTHLY", indicator_category_id=1,
                 description=None, enable=True):
        self.id = id
        self.name = name
        self.short_name = short_name
        self.unit = unit
        self.type = type
        self.temporality = temporality
        self.indicator_category_id = indicator_category_id
        self.description = description or name
        self.enable = enable


class MockIndicatorCategory:
    def __init__(self, id, name, description=None, enable=True):
        self.id = id
        self.name = name
        self.description = description
        self.enable = enable


class MockRecord:
    def __init__(self, id, location_id, location, measure_id, measure, date_value, value):
        self.id = id
        self.location_id = location_id
        self.location = location
        self.measure_id = measure_id
        self.measure = measure
        self.date = date_value
        self.value = value


class MockClimateRecord:
    def __init__(self, id, location_id, location, measure_id, measure, date_value, value):
        self.id = id
        self.location_id = location_id
        self.location = location
        self.measure_id = measure_id
        self.measure = measure
        self.date = date_value
        self.value = value


class MockClimatologyRecord:
    def __init__(self, id, location_id, location, measure_id, measure, month, value):
        self.id = id
        self.location_id = location_id
        self.location = location
        self.measure_id = measure_id
        self.measure = measure
        self.month = month
        self.value = value


class MockIndicatorRecord:
    def __init__(self, id, indicator, location, value, period, start_date, end_date):
        self.id = id
        self.indicator_id = indicator.id
        self.indicator = indicator
        self.location_id = location.id
        self.location = location
        self.value = value
        self.period = period
        self.start_date = start_date
        self.end_date = end_date


# ---------- Shared fixtures ----------

@pytest.fixture
def mock_countries():
    return [
        MockCountry(id=1, name="Colombia", iso2="CO"),
        MockCountry(id=2, name="Ecuador", iso2="EC"),
    ]


@pytest.fixture
def mock_admin1_data():
    country1 = MockCountry(id=1, name="Colombia", iso2="CO")
    country2 = MockCountry(id=2, name="Ecuador", iso2="EC")
    return {
        1: [MockAdmin1(id=101, name="Antioquia", country=country1, ext_id="05")],
        2: [MockAdmin1(id=201, name="Pichincha", country=country2, ext_id="17")],
    }


@pytest.fixture
def mock_admin1_list():
    country1 = MockCountry(id=1, name="Colombia", iso2="CO")
    country2 = MockCountry(id=2, name="Ecuador", iso2="EC")
    return [
        MockAdmin1(id=1, name="Antioquia", country=country1, ext_id="05"),
        MockAdmin1(id=2, name="Antisana", country=country2, ext_id="17"),
        MockAdmin1(id=3, name="Bogotá", country=country1, ext_id="11"),
    ]


@pytest.fixture
def mock_admin2_list():
    country = MockCountry(id=1, name="Colombia", iso2="CO")
    admin1 = MockAdmin1(id=101, name="Pacífico", country=country, ext_id="76")
    return [
        MockAdmin2(id=302, name="Valle del Cauca", admin_1=admin1, ext_id="76001"),
        MockAdmin2(id=303, name="Cauca", admin_1=admin1, ext_id="19001"),
    ]


@pytest.fixture
def mock_locations():
    country = MockCountry(1, "Colombia", "CO")
    admin1 = MockAdmin1(10, "Cundinamarca", country, "11")
    admin2 = MockAdmin2(20, "Bogotá", admin1, "11001")
    return [
        MockLocation(101, "Test Location", "EXT101", "test_machine_name", True, admin2,
                     123.45, 4.5, -74.1, "IDEAM")
    ]