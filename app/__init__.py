"""
App factory pattern: create_app() builds and returns a configured Flask
app instead of creating it at import time. This keeps config/testing
flexible later (e.g. spinning up a test app with different settings)
without restructuring the whole project.
"""
from flask import Flask


def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")

    # Import blueprints here (not at the top of the file) to avoid
    # circular imports - routes/lookup.py imports from app.services,
    # which doesn't need to know about the app object itself.
    from app.routes.lookup import lookup_bp
    from app.routes.pages import pages_bp

    app.register_blueprint(lookup_bp)  # /api/lookup, /api/office-explainer
    app.register_blueprint(pages_bp)   # / (the HTML page)

    return app
