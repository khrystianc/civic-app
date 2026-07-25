"""
Wraps the Census Bureau Geocoding API.
Free, no API key required. Converts a street address into lat/long
plus Census geography (state, county, congressional district, etc).

Docs: https://geocoding.geo.census.gov/geocoder/Geocoding_Services_API.pdf
"""
import requests
from flask import current_app


class GeocodeError(Exception):
    pass


def geocode_address(address: str) -> dict:
    """
    Given a free-text address, return a normalized dict of geography info.
    Raises GeocodeError if the address can't be matched.
    """
    params = {
        "address": address,
        "benchmark": "Public_AR_Current",
        "vintage": "Current_Current",
        "layers": "all",
        "format": "json",
    }

    resp = requests.get(current_app.config["CENSUS_GEOCODER_URL"], params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    matches = data.get("result", {}).get("addressMatches", [])
    if not matches:
        raise GeocodeError(f"No geocoding match found for address: {address}")

    match = matches[0]
    coords = match["coordinates"]
    geographies = match.get("geographies", {})

    def first(layer_name):
        layer = geographies.get(layer_name, [])
        return layer[0] if layer else None

    state = first("States")
    county = first("Counties")
    cong_district = first("119th Congressional Districts") or first("Congressional Districts")
    state_upper = first("State Legislative Districts - Upper")
    state_lower = first("State Legislative Districts - Lower")
    place = first("Incorporated Places")

    return {
        "matched_address": match.get("matchedAddress"),
        "lat": coords["y"],
        "lon": coords["x"],
        "state_fips": state.get("STATE") if state else None,
        "state_name": state.get("NAME") if state else None,
        "county_name": county.get("NAME") if county else None,
        "county_fips": county.get("COUNTY") if county else None,
        "congressional_district": cong_district.get("BASENAME") if cong_district else None,
        "state_senate_district": state_upper.get("NAME") if state_upper else None,
        "state_house_district": state_lower.get("NAME") if state_lower else None,
        "city_name": place.get("NAME") if place else None,
    }
