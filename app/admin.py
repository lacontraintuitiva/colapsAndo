from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import sqlite3

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/admin')
def admin_panel():
    if 'user_id' not in session:
        flash("Debes iniciar sesión para acceder al panel de administración.", "warning")
        return redirect(url_for('auth.login'))

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    users = c.fetchall()
    conn.close()

    return render_template('admin.html', users=users)


@admin_bp.route('/edit-user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('auth.login'))

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    if request.method == 'POST':
        new_role = request.form['role']
        new_status = request.form['status']
        c.execute("UPDATE users SET role = ?, status = ? WHERE id = ?",
                  (new_role, new_status, user_id))
        conn.commit()
        conn.close()
        return redirect(url_for('admin.admin_panel'))

    c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = c.fetchone()
    conn.close()
    return render_template('edit_user.html', user=user)


@admin_bp.route('/delete-user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if session.get('role') != 'admin':
        return redirect(url_for('auth.login'))
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin.admin_panel'))


@admin_bp.route('/project/register', methods=['GET', 'POST'])
def register_project():
    if request.method == 'POST':
        project_name = request.form['project_name']
        # Valores: "Individual", "Equipo", "Colectivo"
        project_type = request.form['project_type']
        description = request.form.get('description', '')

        # Aquí deberás almacenar el proyecto en la base de datos.
        # Ejemplo con SQLite:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        # Asegúrate de tener una tabla projects (o el nombre que prefieras) creada previamente.
        c.execute("""
            INSERT INTO projects (user_id, project_name, project_type, description)
            VALUES (?, ?, ?, ?)
        """, (session.get('user_id'), project_name, project_type, description))
        conn.commit()
        conn.close()

        flash('Proyecto registrado exitosamente.', 'success')
        return redirect(url_for('admin.admin_panel'))
    return render_template('project_form.html')
