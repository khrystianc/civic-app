import json
import os

from flask import Blueprint, jsonify, request

from app.services.geocode import geocode_address, GeocodeError
from app.services.openstates import get_state_legislators, OpenStatesError

lookup_bp = Blueprint("lookup", __name__)

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")


def _load_json(filename):
    with open(os.path.join(DATA_DIR, filename)) as f:
        return json.load(f)


@lookup_bp.route("/api/lookup", methods=["GET"])
def lookup():
    address = request.args.get("address", "").strip()
    if not address:
        return jsonify({"error": "address query param is required"}), 400

    try:
        geo = geocode_address(address)
    except GeocodeError as e:
        return jsonify({"error": str(e)}), 404

    result = {
        "address": geo["matched_address"],
        "state": geo["state_name"],
        "county": geo["county_name"],
        "city": geo["city_name"],
        "congressional_district": geo["congressional_district"],
        "federal": {},
        "state_legislators": [],
        "local": {},
    }

    # Federal delegation - static file, cheap to keep current
    if geo["state_fips"] == "41":  # Oregon FIPS code
        federal = _load_json("oregon_federal.json")
        result["federal"]["senators"] = federal["senators"]
        district_key = f"OR-{geo['congressional_district']}" if geo["congressional_district"] else None
        result["federal"]["house_rep"] = federal["house_districts"].get(district_key)

    # State legislators - live OpenStates lookup
    try:
        result["state_legislators"] = get_state_legislators(geo["lat"], geo["lon"])
    except OpenStatesError as e:
        result["state_legislators_error"] = str(e)

    # Local - manual pilot data, Columbia County OR only for now
    if geo["county_name"] and "Columbia" in geo["county_name"] and geo["state_name"] == "Oregon":
        local = _load_json("columbia_county_or.json")
        result["local"]["county_commissioners"] = local["county_commissioners"]
        city_data = local["cities"].get(geo["city_name"]) if geo["city_name"] else None
        if city_data:
            result["local"]["city"] = city_data
    else:
        result["local"]["note"] = "Local coverage is currently limited to the Columbia County, OR pilot."

    return jsonify(result)


@lookup_bp.route("/api/office-explainer/<office_key>", methods=["GET"])
def office_explainer(office_key):
    explainers = _load_json("office_explainers.json")
    explainer = explainers.get(office_key)
    if not explainer:
        return jsonify({"error": "unknown office_key", "valid_keys": list(explainers.keys())}), 404
    return jsonify(explainer)
