import os
from flask import Flask


def create_app():
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    templates_dir = os.path.join(base_dir, 'templates')
    app = Flask(__name__, template_folder=templates_dir)

    app.config['SECRET_KEY'] = 'G0y0&Ruf1n0'

    from .register import register_bp
    from .admin import admin_bp
    from .auth import auth_bp

    app.register_blueprint(register_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(auth_bp)

    return app
