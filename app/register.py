from flask import Blueprint, render_template, request, redirect, url_for, flash
import sqlite3
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

        try:
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute("INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
                      (name, email, hashed_password, 'user'))
            conn.commit()
            flash("Registro exitoso. Ahora puedes iniciar sesión.", "success")
            return redirect(url_for('auth.login'))
        except sqlite3.IntegrityError:
            flash("El email ya está registrado", "danger")
            return render_template('register.html')
        finally:
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
