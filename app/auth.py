from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db import get_db_connection
from psycopg2 import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash
from flask_mail import Message

import uuid

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        conn = None
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM users WHERE email = %s",
                (email,)
            )
            user = cur.fetchone()
            cur.close()

            if user and check_password_hash(user['password'], password) and user['is_active']:
                session['user_id'] = user['id']
                session['role'] = user['role']
                session['user_name'] = user['name']
                flash('Inicio de sesión exitoso.', 'success')
                return redirect(url_for('admin.register_project'))
            else:
                flash('Credenciales incorrectas.', 'danger')

        except Exception as e:
            flash('Error en el inicio de sesión.', 'danger')
        finally:
            if conn:
                conn.close()

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
    from run import mail, app
    print("Enviando correo de activación a:", user_email)
    with app.app_context():
        # Change 'auth.activate' to 'auth.activate_account'
        activation_link = url_for(
            'auth.activate_account', token=token, _external=True)
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
            conn = get_db_connection()
            c = conn.cursor()
            c.execute(
                "INSERT INTO users (name, email, password, is_active, activation_token) VALUES (%s, %s, %s, %s, %s)",
                (name, email, hashed_password, False, token)
            )
            conn.commit()
            conn.close()

            send_activation_email(email, token)
            # En lugar de redirigir al login, renderiza una plantilla de información
            return render_template('activation_info.html', email=email)
        except IntegrityError:
            flash('Ya existe una cuenta registrada con ese correo electrónico.', 'danger')
            return render_template('register.html', name=name, email=email)
    return render_template('register.html')


@auth_bp.route('/activate/<token>')
def activate_account(token):
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            'SELECT id, email, is_active, activation_token FROM users WHERE activation_token = %s AND is_active = %s',
            (token, False)
        )
        user = cur.fetchone()

        if user:
            cur.execute(
                'UPDATE users SET is_active = %s, activation_token = %s WHERE id = %s',
                (True, None, user['id'])
            )
            conn.commit()
            # Limpiamos cualquier mensaje flash previo
            session.pop('_flashes', None)
            flash(
                'Tu cuenta ha sido activada correctamente. Por favor inicia sesión.', 'success')
        else:
            flash('Enlace inválido o cuenta ya activada.', 'warning')

    except Exception as e:
        print(f"Error en activación: {e}")
        flash('Error al activar la cuenta.', 'danger')
        if conn:
            conn.rollback()
    finally:
        if conn:
            cur.close()
            conn.close()

    return redirect(url_for('auth.login'))


@auth_bp.route('/update_email', methods=['GET', 'POST'])
def update_email():
    if request.method == 'POST':
        current_email = request.form['current_email']
        new_email = request.form['new_email']
        conn = get_db_connection()
        c = conn.cursor()
        # Buscamos al usuario que aún no haya activado su cuenta
        c.execute(
            "SELECT id, activation_token FROM users WHERE email = %s AND is_active=%s",
            (current_email, False)
        )
        user = c.fetchone()
        if user:
            user_id, token = user
            # Actualizamos el correo
            c.execute("UPDATE users SET email = %s WHERE id = %s",
                      (new_email, user['id']))
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
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    # Eliminar solo el mensaje específico de inicio de sesión exitoso
    if '_flashes' in session:
        session['_flashes'] = [(cat, msg) for cat, msg in session['_flashes']
                               if msg != 'Inicio de sesión exitoso.']

    # Obtener información del usuario desde la base de datos
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT name, email FROM users WHERE id = %s",
                (session['user_id'],))
    user_data = cur.fetchone()

    # Convertir a diccionario si es necesario
    if user_data and not isinstance(user_data, dict):
        colnames = [desc[0] for desc in cur.description]
        user_info = dict(zip(colnames, user_data))
    else:
        user_info = user_data or {}

    cur.close()
    conn.close()

    return render_template('account.html', user_info=user_info)


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
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE id = %s",
              (session['user_id'],))
    user = c.fetchone()
    if not user or not check_password_hash(user['password'], current_password):
        conn.close()
        flash('La contraseña actual es incorrecta.', 'danger')
        return redirect(url_for('auth.account'))

    # Actualiza la contraseña
    new_hash = generate_password_hash(new_password)
    c.execute("UPDATE users SET password = %s WHERE id = %s",
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
