"""
All app settings live here in one place. Nothing else in the codebase
should read os.environ directly - if you need a new setting, add it
here so it's easy to find everything the app depends on at a glance.
"""
import os


class Config:
    # Free API key from https://open.pluralpolicy.com/ - used in services/openstates.py
    OPENSTATES_API_KEY = os.environ.get("OPENSTATES_API_KEY", "")

    # No key required for Census geocoding - it's a free public API
    CENSUS_GEOCODER_URL = "https://geocoding.geo.census.gov/geocoder/geographies/onelineaddress"
    OPENSTATES_BASE_URL = "https://v3.openstates.org"

    DEBUG = os.environ.get("FLASK_DEBUG", "1") == "1"

    # Auth / DB
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-in-production")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///civic_app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Stripe - see app/routes/billing.py for what each is used for
    STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
    STRIPE_PRICE_ID = os.environ.get("STRIPE_PRICE_ID", "")
    STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
