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
            return redirect(url_for('admin.register_project'))
        else:
            flash('Credenciales incorrectas.', 'danger')

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.index'))


@auth_bp.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('admin.register_project'))
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
    print("Enviando correo de activación a:",
          user_email)  # Debug: muestra en consola
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
            # En lugar de redirigir al login, renderiza una plantilla de información
            return render_template('activation_info.html', email=email)
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


@auth_bp.route('/update_email', methods=['GET', 'POST'])
def update_email():
    if request.method == 'POST':
        current_email = request.form['current_email']
        new_email = request.form['new_email']
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        # Buscamos al usuario que aún no haya activado su cuenta
        c.execute(
            "SELECT id, activation_token FROM users WHERE email = ? AND is_active=0", (current_email,))
        user = c.fetchone()
        if user:
            user_id, token = user
            # Actualizamos el correo
            c.execute("UPDATE users SET email = ? WHERE id = ?",
                      (new_email, user_id))
            conn.commit()
            conn.close()
            # Reenvía el correo de activación al nuevo email
            send_activation_email(new_email, token)
            flash("Correo actualizado. Revisa tu buzón para activar tu cuenta.", "info")
            return redirect(url_for('auth.login'))
        else:
            flash(
                "No se encontró usuario con ese correo o la cuenta ya está activada.", "danger")
            conn.close()
    return render_template('update_email.html')


@auth_bp.route('/account')
def account():
    # Renderiza la página de cuenta del usuario
    return render_template('account.html')


@auth_bp.route('/change-password', methods=['POST'])
def change_password():
    if 'user_id' not in session:
        flash('Debes iniciar sesión.', 'warning')
        return redirect(url_for('auth.login'))

    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    if not current_password or not new_password or not confirm_password:
        flash('Completa todos los campos.', 'danger')
        return redirect(url_for('auth.account'))

    if new_password != confirm_password:
        flash('Las contraseñas nuevas no coinciden.', 'danger')
        return redirect(url_for('auth.account'))

    # Obtén el hash actual de la base de datos
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE id = ?", (session['user_id'],))
    user = c.fetchone()
    if not user or not check_password_hash(user[0], current_password):
        conn.close()
        flash('La contraseña actual es incorrecta.', 'danger')
        return redirect(url_for('auth.account'))

    # Actualiza la contraseña
    new_hash = generate_password_hash(new_password)
    c.execute("UPDATE users SET password = ? WHERE id = ?",
              (new_hash, session['user_id']))
    conn.commit()
    conn.close()

    flash('Contraseña actualizada correctamente.', 'success')
    return redirect(url_for('auth.account'))


@auth_bp.route('/delete-account', methods=['POST'])
def delete_account():
    # Lógica para eliminar la cuenta
    # ...
    flash('Cuenta eliminada correctamente.', 'info')
    return redirect(url_for('auth.logout'))
