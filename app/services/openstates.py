"""
Wraps the OpenStates v3 API to fetch state legislators.
Requires a free API key from https://open.pluralpolicy.com/

Docs: https://docs.openstates.org/api-v3/
"""
import requests
from flask import current_app


class OpenStatesError(Exception):
    pass


def get_state_legislators(lat: float, lon: float) -> list[dict]:
    """
    Given lat/lon, return the state legislators (house + senate)
    whose districts contain that point.
    """
    api_key = current_app.config["OPENSTATES_API_KEY"]
    if not api_key:
        raise OpenStatesError("OPENSTATES_API_KEY is not configured")

    url = f"{current_app.config['OPENSTATES_BASE_URL']}/people.geo"
    params = {"lat": lat, "lng": lon}
    headers = {"X-API-KEY": api_key}

    resp = requests.get(url, params=params, headers=headers, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    legislators = []
    for person in data.get("results", []):
        current_role = person.get("current_role") or {}
        legislators.append({
            "name": person.get("name"),
            "party": person.get("party"),
            "chamber": current_role.get("org_classification"),
            "district": current_role.get("district"),
            "title": current_role.get("title"),
            "email": person.get("email"),
            "links": [l.get("url") for l in person.get("links", [])],
            "image": person.get("image"),
        })

    return legislators
