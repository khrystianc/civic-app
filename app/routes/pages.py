"""
Page routes - anything that returns HTML (as opposed to routes/lookup.py,
which returns JSON). Right now there's just the one page.
"""
from flask import Blueprint, render_template, current_app

pages_bp = Blueprint("pages", __name__)


@pages_bp.route("/")
def index():
    """Serves the address-lookup page (templates/index.html)."""
    return render_template("index.html", adsense_publisher_id=current_app.config.get("ADSENSE_PUBLISHER_ID"))


@pages_bp.route("/about")
def about():
    return render_template("about.html")


@pages_bp.route("/privacy")
def privacy():
    return render_template("privacy.html")


@pages_bp.route("/contact")
def contact():
    return render_template("contact.html")
