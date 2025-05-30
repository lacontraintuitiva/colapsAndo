from flask import Flask, render_template, redirect, url_for, session
from app.auth import auth_bp
from app.register import register_bp
from app.admin import admin_bp
from config import Config
from flask_mail import Mail, Message
import os

app = Flask(__name__)
app.config.from_object(Config)

# Configuración de Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'lacontraintuitiva@gmail.com'
app.config['MAIL_PASSWORD'] = 'mvau hqui vphh pnki'
app.config['MAIL_DEFAULT_SENDER'] = 'lacontraintuitiva@gmail.com'

mail = Mail(app)

# Registrar blueprints
app.register_blueprint(auth_bp, url_prefix='/')
app.register_blueprint(register_bp, url_prefix='/')
app.register_blueprint(admin_bp)

# Configura el directorio de uploads
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Crea el directorio si no existe
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# AGREGAR ESTAS RUTAS:


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/registro')
def registro():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return redirect(url_for('admin.register_project'))

@app.route('/terminos')
def terminos():
    return render_template('terminos.html')

# Context processor para reCAPTCHA


@app.context_processor
def inject_recaptcha():
    return dict(recaptcha_site_key=app.config['RECAPTCHA_SITE_KEY'])


if __name__ == "__main__":
    app.run(debug=True)
