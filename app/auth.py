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

        # Validar reCAPTCHA usando la variable de entorno
        if recaptcha_token:
            recaptcha_data = {
                # Usar variable de entorno
                'secret': current_app.config['RECAPTCHA_SECRET_KEY'],
                'response': recaptcha_token
            }

            try:
                recaptcha_response = requests.post(
                    'https://www.google.com/recaptcha/api/siteverify',
                    data=recaptcha_data,
                    timeout=5
                )

                result = recaptcha_response.json()

                # Debug: imprimir el resultado (remover en producción)
                print(f"reCAPTCHA result: {result}")

                # Verificar si reCAPTCHA falló
                if not result.get('success'):
                    error_codes = result.get('error-codes', [])
                    print(f"reCAPTCHA errors: {error_codes}")
                    flash(
                        'Error de verificación de seguridad. Intenta de nuevo.', 'danger')
                    return render_template('login.html')

                # Para reCAPTCHA v3, verificar el score
                score = result.get('score', 0)
                if score < 0.3:  # Umbral más bajo para pruebas
                    print(f"reCAPTCHA score too low: {score}")
                    flash(
                        'Verificación de seguridad fallida. Intenta de nuevo.', 'danger')
                    return render_template('login.html')

            except requests.RequestException as e:
                print(f"reCAPTCHA request error: {e}")
                flash(
                    'Error de conectividad. Procediendo sin verificación adicional.', 'warning')
        else:
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
