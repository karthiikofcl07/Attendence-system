import os
import click
from flask import Flask

from config import Config, ensure_directories
from models.extensions import db
from models.models import Admin
from extensions import login_manager, csrf, limiter


def create_app(config_class=Config):
    ensure_directories()

    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"
    csrf.init_app(app)
    limiter.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return Admin.query.get(int(user_id))

    # --- Blueprints ---------------------------------------------------
    from routes.auth import bp as auth_bp
    from routes.dashboard import bp as dashboard_bp
    from routes.students import bp as students_bp
    from routes.recognition import bp as recognition_bp, camera_stream
    from routes.reports import bp as reports_bp
    from routes.api import bp as api_bp
    from routes.settings import bp as settings_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(recognition_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(settings_bp)
    csrf.exempt(api_bp)  # JSON API uses its own clients; CSRF only enforced on browser forms

    camera_stream.init_app(app)

    with app.app_context():
        db.create_all()
        _seed_default_admin()

    @app.context_processor
    def inject_globals():
        from datetime import datetime
        return {"current_year": datetime.now().year}

    @app.route("/media/<path:filepath>")
    def media(filepath):
        """Serves images from dataset/ and uploads/ (outside /static) to logged-in admins only."""
        from flask import send_from_directory, abort as flask_abort
        from flask_login import current_user as cu
        if not cu.is_authenticated:
            flask_abort(403)
        if not (filepath.startswith("dataset/") or filepath.startswith("uploads/")):
            flask_abort(403)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(base_dir, filepath)
        directory, filename = os.path.split(full_path)
        return send_from_directory(directory, filename)

    @app.errorhandler(403)
    def forbidden(e):
        return "403 - You don't have permission to access this resource.", 403

    @app.errorhandler(404)
    def not_found(e):
        return "404 - Page not found.", 404

    register_cli(app)
    return app


def _seed_default_admin():
    """On first run, create a default admin if none exists, so the app is usable immediately."""
    if Admin.query.first() is None:
        admin = Admin(username="admin", email="admin@example.com", role="admin")
        admin.set_password("Admin@123")
        db.session.add(admin)
        db.session.commit()
        print("=" * 70)
        print(" Created default admin account ->  username: admin   password: Admin@123")
        print(" CHANGE THIS PASSWORD IMMEDIATELY after first login.")
        print("=" * 70)


def register_cli(app):
    @app.cli.command("create-admin")
    @click.argument("username")
    @click.argument("password")
    def create_admin(username, password):
        """Usage: flask create-admin <username> <password>"""
        if Admin.query.filter_by(username=username).first():
            click.echo("That username already exists.")
            return
        admin = Admin(username=username, role="admin")
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        click.echo(f"Admin '{username}' created.")


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
