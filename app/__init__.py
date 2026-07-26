"""
App factory pattern: create_app() builds and returns a configured Flask
app instead of creating it at import time. This keeps config/testing
flexible later (e.g. spinning up a test app with different settings)
without restructuring the whole project.
"""
from flask import Flask
from flask_login import LoginManager

from app.models import db


def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))

    # Import blueprints here (not at the top of the file) to avoid
    # circular imports - routes/lookup.py imports from app.services,
    # which doesn't need to know about the app object itself.
    from app.routes.lookup import lookup_bp
    from app.routes.pages import pages_bp
    from app.routes.auth import auth_bp
    from app.routes.billing import billing_bp

    app.register_blueprint(lookup_bp)   # /api/lookup, /api/office-explainer
    app.register_blueprint(pages_bp)    # / (the HTML page)
    app.register_blueprint(auth_bp)     # /signup, /login, /logout, /api/me
    app.register_blueprint(billing_bp)  # /billing/*

    with app.app_context():
        db.create_all()

    return app
