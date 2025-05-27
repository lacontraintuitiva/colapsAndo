from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
import sqlite3
import requests
from werkzeug.security import check_password_hash, generate_password_hash
from flask_mail import Message
import uuid

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

        # Validar credenciales del usuario
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute(
            "SELECT id, password, role, name, is_active FROM users WHERE email = ?", (email,))
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user[1], password):
            if not user[4]:
                flash(
                    'Debes activar tu cuenta desde el correo antes de ingresar.', 'warning')
                return redirect(url_for('auth.login'))
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


def send_activation_email(user_email, token):
    from run import mail, app  # Importa mail y app desde run.py
    with app.app_context():
        activation_link = url_for('auth.activate', token=token, _external=True)
        msg = Message('Activa tu cuenta', recipients=[user_email])
        msg.body = f'Por favor activa tu cuenta haciendo clic en este enlace:\n\n{activation_link}\n\nSi no creaste esta cuenta, ignora este mensaje.'
        mail.send(msg)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        token = str(uuid.uuid4())

        try:
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute("INSERT INTO users (name, email, password, is_active, activation_token) VALUES (?, ?, ?, 0, ?)",
                      (name, email, hashed_password, token))
            conn.commit()
            conn.close()

            send_activation_email(email, token)
            flash('Revisa tu correo para activar tu cuenta.', 'info')
            return redirect(url_for('auth.login'))
        except sqlite3.IntegrityError:
            flash('Ya existe una cuenta registrada con ese correo electrónico.', 'danger')
            return render_template('register.html', name=name, email=email)
    return render_template('register.html')


@auth_bp.route('/activate/<token>')
def activate(token):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute(
        'SELECT id FROM users WHERE activation_token=? AND is_active=0', (token,))
    user = c.fetchone()
    if user:
        c.execute(
            'UPDATE users SET is_active=1, activation_token=NULL WHERE id=?', (user[0],))
        conn.commit()
        flash('Cuenta activada. Ya puedes iniciar sesión.', 'success')
    else:
        flash('Enlace inválido o cuenta ya activada.', 'danger')
    conn.close()
    return redirect(url_for('auth.login'))
