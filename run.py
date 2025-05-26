from flask import Flask
from app.auth import auth_bp
from app.register import register_bp
from app.admin import admin_bp
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Registrar blueprints
app.register_blueprint(auth_bp, url_prefix='/')
app.register_blueprint(register_bp, url_prefix='/')
app.register_blueprint(admin_bp, url_prefix='/')

# Context processor para reCAPTCHA


@app.context_processor
def inject_recaptcha():
    return dict(recaptcha_site_key=app.config['RECAPTCHA_SITE_KEY'])


if __name__ == "__main__":
    app.run(debug=True)
