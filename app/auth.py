from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
import sqlite3
import requests
from werkzeug.security import check_password_hash

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        recaptcha_token = request.form.get('recaptcha_token')

        # TEMPORAL: Deshabilitar reCAPTCHA para que funcione el login
        print("=== MODO DEBUG: reCAPTCHA DESHABILITADO ===")
        print(
            f"Token recibido: {recaptcha_token[:50] if recaptcha_token else 'None'}...")

        # TODO: Restaurar cuando tengas claves reales
        # ... código de reCAPTCHA comentado temporalmente ...

        # Validar credenciales del usuario
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute(
            "SELECT id, password, role, name FROM users WHERE email = ?", (email,))
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            session['role'] = user[2]
            session['user_name'] = user[3]
            flash('Inicio de sesión exitoso.', 'success')
            return redirect(url_for('admin.admin_panel'))
        else:
            flash('Credenciales incorrectas.', 'danger')

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/')
def index():
    return render_template('index.html')


@auth_bp.route('/debug-recaptcha')
def debug_recaptcha():
    from flask import current_app
    site_key = current_app.config.get('RECAPTCHA_SITE_KEY', 'NO_CONFIGURADO')
    secret_key = current_app.config.get(
        'RECAPTCHA_SECRET_KEY', 'NO_CONFIGURADO')

    return f"""
    <h1>Debug reCAPTCHA</h1>
    <p><strong>Site Key:</strong> {site_key}</p>
    <p><strong>Secret Key:</strong> {secret_key[:20]}... (primeros 20 caracteres)</p>
    <p><strong>Site Key length:</strong> {len(site_key) if site_key else 0}</p>
    <p><strong>Secret Key length:</strong> {len(secret_key) if secret_key else 0}</p>
    """
