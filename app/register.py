from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import get_db_connection
from psycopg2 import IntegrityError
from werkzeug.security import generate_password_hash

register_bp = Blueprint('register', __name__)


@register_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':

        # TEMPORAL: Deshabilitar reCAPTCHA para que funcione el registro
        print("=== MODO DEBUG: reCAPTCHA DESHABILITADO EN REGISTER ===")

        # TODO: Restaurar validación reCAPTCHA cuando tengas claves reales
        # if not validate_recaptcha(request):
        #     flash("Verificación CAPTCHA fallida", "danger")
        #     return render_template('register.html')

        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Validar que las contraseñas coincidan
        if password != confirm_password:
            flash("Las contraseñas no coinciden", "danger")
            return render_template('register.html')

        # Hash de la contraseña
        hashed_password = generate_password_hash(password)

        conn = None
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO users (name, email, password, is_active, role) VALUES (%s, %s, %s, %s, %s)",
                (name, email, hashed_password, False, 'user')
            )
            conn.commit()
            cur.close()
            flash("Registro exitoso. Por favor revisa tu correo para activar tu cuenta.", "success")
            return redirect(url_for('auth.login'))
        except IntegrityError:
            if conn:
                conn.rollback()
            flash('El correo ya está registrado.', 'danger')
            return render_template('register.html', name=name, email=email)
        except Exception as e:
            if conn:
                conn.rollback()
            flash('Error en el registro. Por favor intenta nuevamente.', 'danger')
            return render_template('register.html', name=name, email=email)
        finally:
            if conn:
                conn.close()

    return render_template('register.html')


# TODO: Restaurar cuando tengas claves reales de reCAPTCHA
# def validate_recaptcha(request):
#     recaptcha_response = request.form.get('g-recaptcha-response')
#     secret = os.environ.get('RECAPTCHA_SECRET_KEY')
#     payload = {
#         'secret': secret,
#         'response': recaptcha_response
#     }
#     r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=payload)
#     result = r.json()
#     return result.get('success', False)
