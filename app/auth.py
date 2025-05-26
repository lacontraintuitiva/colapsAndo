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

        print(
            f"reCAPTCHA token recibido: {recaptcha_token[:50] if recaptcha_token else 'None'}...")
        print(
            f"Secret Key configurada: {'Sí' if current_app.config.get('RECAPTCHA_SECRET_KEY') else 'No'}")

        # Validar reCAPTCHA
        if recaptcha_token:
            recaptcha_data = {
                'secret': current_app.config['RECAPTCHA_SECRET_KEY'],
                'response': recaptcha_token
            }

            try:
                recaptcha_response = requests.post(
                    'https://www.google.com/recaptcha/api/siteverify',
                    data=recaptcha_data,
                    timeout=10
                )

                result = recaptcha_response.json()
                print(f"reCAPTCHA response completa: {result}")

                # Verificar respuesta
                if not result.get('success'):
                    error_codes = result.get('error-codes', [])
                    print(f"reCAPTCHA errors: {error_codes}")
                    flash(
                        f'Error de verificación: {", ".join(error_codes)}', 'danger')
                    return render_template('login.html')

                # Verificar score para v3
                score = result.get('score', 0)
                action = result.get('action', '')
                print(f"reCAPTCHA score: {score}, action: {action}")

                if score < 0.1:  # Umbral muy bajo para testing
                    flash(
                        f'Score de seguridad muy bajo: {score}. Intenta de nuevo.', 'warning')
                    return render_template('login.html')

                print("reCAPTCHA validado exitosamente")

            except requests.RequestException as e:
                print(f"Error de conexión reCAPTCHA: {e}")
                flash(
                    'Error de conectividad con el servicio de verificación.', 'warning')
                # Continuar sin reCAPTCHA en caso de error de red
        else:
            print("No se recibió token de reCAPTCHA")
            flash('Token de verificación faltante.', 'danger')
            return render_template('login.html')

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


# Agregar esta ruta al final de auth.py para debug
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
