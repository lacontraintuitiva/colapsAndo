from flask import (
    Blueprint, render_template, request, redirect, url_for,
    flash, session, jsonify, current_app
)
from werkzeug.utils import secure_filename
from db import get_db_connection
import os

admin_bp = Blueprint('admin', __name__)


def get_or_create_draft(user_id):
    print(f"--- Iniciando get_or_create_draft para user_id: {user_id} ---")
    conn = get_db_connection()
    cur = conn.cursor()

    # Buscar draft existente
    print("Buscando draft existente...")
    cur.execute("""
      SELECT * FROM projects
       WHERE user_id = %s AND status = 'draft'
       ORDER BY updated_at DESC
       LIMIT 1
    """, (user_id,))
    row = cur.fetchone()
    print(f"Resultado de SELECT (row): {row}")

    if row:
        print("Draft existente encontrado.")
        # Si 'row' ya es un RealDictRow, se comporta como un diccionario
        project = dict(row)
        print(f"Project (desde SELECT, convertido de RealDictRow): {project}")
    else:
        print("No se encontró draft existente. Creando nuevo draft...")
        cur.execute("""
          INSERT INTO projects
            (user_id, status, current_step, created_at, updated_at)
          VALUES (%s,'draft',0,NOW(),NOW())
          RETURNING *
        """, (user_id,))
        new_row = cur.fetchone()  # Esto también devolverá un RealDictRow
        print(f"Resultado de INSERT RETURNING * (new_row): {new_row}")

        if new_row:
            project = dict(new_row)  # Convertir RealDictRow a dict
            print(
                f"Project (desde INSERT, convertido de RealDictRow): {project}")
        else:
            project = {}
            print("ERROR CRÍTICO: INSERT no retornó fila (new_row es None).")

    print(f"Antes de commit. Project['id'] es: {project.get('id')}")
    conn.commit()
    cur.close()
    conn.close()
    print(
        f"--- Finalizando get_or_create_draft. Retornando project con id: {project.get('id')} ---")
    return project


@admin_bp.route('/admin')
def admin_panel():
    if 'user_id' not in session:
        flash("Debes iniciar sesión para acceder al panel de administración.", "warning")
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users")
    users = cur.fetchall()
    conn.close()

    return render_template('admin.html', users=users)


@admin_bp.route('/edit-user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Debes ser administrador para editar usuarios.", "warning")
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        new_role = request.form.get('role')
        new_status = request.form.get('status')
        cur.execute(
            "UPDATE users SET role = %s, status = %s WHERE id = %s",
            (new_role, new_status, user_id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('admin.admin_panel'))

    cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    conn.close()
    return render_template('edit_user.html', user=user)


@admin_bp.route('/delete-user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if session.get('role') != 'admin':
        flash("Debes ser administrador para eliminar usuarios.", "warning")
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin.admin_panel'))


@admin_bp.route('/project/register', methods=['GET', 'POST'])
def register_project():
    if 'user_id' not in session:
        flash("Debes iniciar sesión para registrar un proyecto.", "warning")
        return redirect(url_for('auth.login'))

    datos = {}
    conn = None

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT * FROM projects
             WHERE user_id = %s AND status = 'draft'
             ORDER BY updated_at DESC
             LIMIT 1
        """, (session['user_id'],))
        row = cur.fetchone()
        cols = [d[0] for d in cur.description]
        if row:
            datos = dict(zip(cols, row))
    except Exception as e:
        print("Error cargando borrador:", e)
    finally:
        if conn:
            cur.close()
            conn.close()

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO projects (title, description, category, user_id) "
            "VALUES (%s, %s, %s, %s) RETURNING id",
            (title, description, category, session['user_id'])
        )
        project_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        flash('Proyecto registrado exitosamente.', 'success')
        return redirect(url_for('admin.view_project', id=project_id))

    return render_template('project_form.html', datos=datos)


@admin_bp.route('/admin/project/autosave', methods=['POST'])
def autosave_project():
    if 'user_id' not in session:
        return jsonify(error='No autorizado para autosave'), 401

    try:
        user_id = session['user_id']
        project = get_or_create_draft(user_id)
        pid = project.get('id')
        if not pid:
            print("ERROR: No se pudo obtener el ID del proyecto.")
            return jsonify({'error': 'No se pudo obtener el ID del proyecto'}), 500

        form_data = request.form.to_dict()
        print("DEBUG autosave_project: request.form =", form_data)

        # Mapea todos los campos relevantes
        fields_to_save = {
            'title': form_data.get('title'),
            'description': form_data.get('description'),
            'category': form_data.get('category'),
            'participant_name': form_data.get('participant_name'),
            'participant_phone': form_data.get('participant_phone'),
            'participant_country': form_data.get('participant_country'),
            'participant_city': form_data.get('participant_city'),
            'participant_occupation': form_data.get('participant_occupation'),
            'participant_institution': form_data.get('participant_institution'),
            'participant_area': form_data.get('participant_area'),
            'participant_portfolio': form_data.get('participant_portfolio'),
            'previous_participation': form_data.get('previous_participation'),
            'media_authorization': form_data.get('media_authorization'),
            'terms': True if form_data.get('terms') == 'on' else False,
            'current_step': form_data.get('current_step', 0),
            'format': form_data.get('format'),
            # project_files se maneja aparte si subes archivos
        }

        remove_file = form_data.get('remove_project_files') == '1'
        if remove_file:
            fields_to_save['project_files'] = None  # O '' según tu lógica

        print("DEBUG autosave_project: Campos y valores a guardar en DB:", fields_to_save)

        set_clauses = []
        values = []
        for col, val in fields_to_save.items():
            set_clauses.append(f"{col} = %s")
            values.append(val)
        set_clauses.append("updated_at = NOW()")

        sql = f"UPDATE projects SET {', '.join(set_clauses)} WHERE id = %s"
        values.append(pid)

        print("DEBUG autosave_project: SQL UPDATE:", sql)
        print("DEBUG autosave_project: Values para UPDATE:", values)

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(sql, values)
        conn.commit()

        cur.execute("SELECT * FROM projects WHERE id = %s", (pid,))
        print("DEBUG autosave_project: datos en DB después del commit:", cur.fetchone())
        cur.close()
        conn.close()

        return jsonify(success=True)
    except Exception as e:
        import traceback
        print("Error en autosave_project:", e)
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/project/load-progress', endpoint='project_load_progress')
def load_project_progress():
    if 'user_id' not in session:
        return jsonify(error='No autorizado'), 401

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            id, user_id, status, created_at, updated_at, -- Metadatos
            participant_name, participant_phone, participant_country, participant_city,
            participant_occupation, participant_institution, participant_area,
            participant_portfolio,
            title, description, category, format, project_files,
            previous_participation, current_step,
            media_authorization, terms
        FROM projects
        WHERE user_id = %s AND status = 'draft'
        ORDER BY updated_at DESC
        LIMIT 1
    """, (session['user_id'],))
    row = cur.fetchone()  # row es un RealDictRow

    if not row:
        cur.close()
        conn.close()
        # <--- ASEGÚRATE QUE ESTA LÍNEA ESTÉ AQUÍ
        print(f"DEBUG load_project_progress: Enviando project: {project}")

        return jsonify(success=True, project={})

    project = dict(row)  # Convertir RealDictRow a dict estándar

    cur.close()
    conn.close()

    # Revisa este print en la consola de Flask
    print(f"DEBUG load_project_progress: Enviando project: {project}")
    return jsonify(success=True, project=project)


@admin_bp.route('/terminos')
def terminos():
    return render_template('terminos.html')
