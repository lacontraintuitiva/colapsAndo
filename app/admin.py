from flask import request, jsonify, session
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from db import get_db_connection
import os
from werkzeug.utils import secure_filename

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/admin')
def admin_panel():
    if 'user_id' not in session:
        flash("Debes iniciar sesión para acceder al panel de administración.", "warning")
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    users = c.fetchall()
    conn.close()

    return render_template('admin.html', users=users)


@admin_bp.route('/edit-user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    c = conn.cursor()

    if request.method == 'POST':
        new_role = request.form['role']
        new_status = request.form['status']
        c.execute("UPDATE users SET role = %s, status = %s WHERE id = %s",
                  (new_role, new_status, user_id))
        conn.commit()
        conn.close()
        return redirect(url_for('admin.admin_panel'))

    c.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = c.fetchone()
    conn.close()
    return render_template('edit_user.html', user=user)


@admin_bp.route('/delete-user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if session.get('role') != 'admin':
        return redirect(url_for('auth.login'))
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE id = %s", (user_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin.admin_panel'))


@admin_bp.route('/project/register', methods=['GET', 'POST'])
def register_project():
    # Verificación de autenticación más robusta
    if 'user_id' not in session:
        flash("Debes iniciar sesión para registrar un proyecto.", "warning")
        return redirect(url_for('auth.login'))

    # Inicializa datos como diccionario vacío
    datos = {}

    # Intenta cargar datos existentes
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT * FROM projects 
            WHERE user_id = %s AND status = 'draft'
            ORDER BY updated_at DESC LIMIT 1
        """, (session['user_id'],))

        project = cur.fetchone()

        # Convierte a diccionario si es necesario
        if project and not isinstance(project, dict):
            colnames = [desc[0] for desc in cur.description]
            project = dict(zip(colnames, project))

        # Si hay datos, mapearlos correctamente al formulario
        if project:
            # MAPEO INVERSO: de base de datos a formulario
            reverse_mapping = {
                'title': 'project_title',
                'description': 'project_description', 
                'category': 'project_category'
            }
            
            # Aplicar mapeo inverso
            for db_field, form_field in reverse_mapping.items():
                if db_field in project and project[db_field]:
                    project[form_field] = project[db_field]
            
            datos = project

    except Exception as e:
        print(f"Error cargando datos: {e}")
        # No redirigir aquí, solo loggear el error
    finally:
        if conn:
            cur.close()
            conn.close()

    if request.method == 'POST':
        conn = None
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            title = request.form['project_name']
            description = request.form.get('description', '')
            category = request.form['project_type']

            cur.execute(
                "INSERT INTO projects (title, description, category, user_id) VALUES (%s, %s, %s, %s) RETURNING id",
                (title, description, category, session['user_id'])
            )
            project_id = cur.fetchone()['id']
            conn.commit()
            cur.close()
            flash('Proyecto registrado exitosamente.', 'success')
            return redirect(url_for('admin.view_project', id=project_id))
        except Exception as e:
            if conn:
                conn.rollback()
            flash('Error al registrar el proyecto.', 'danger')
        finally:
            if conn:
                conn.close()

    # Agregar debug para ver qué datos se están pasando
    print(f"Datos enviados al template: {datos}")
    
    # ESTO ES LO CLAVE: pasar datos al template
    return render_template('project_form.html', datos=datos)


@admin_bp.route('/project/autosave', methods=['POST'])
def autosave_project():
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Mapear campos del formulario a columnas de la base de datos
        field_mapping = {
            'project_title': 'title',
            'project_description': 'description',
            'project_category': 'category'
        }

        # Procesar campos del formulario
        form_data = {}
        
        # Campos con mapeo especial
        for form_field, db_field in field_mapping.items():
            if form_field in request.form and request.form[form_field].strip():
                form_data[db_field] = request.form[form_field]

        # Campos que coinciden directamente
        direct_fields = [
            'participant_name', 'participant_phone', 'participant_country',
            'participant_city', 'participant_occupation', 'participant_institution',
            'participant_area', 'participant_portfolio', 'project_justification',
            'project_format', 'previous_participation', 'media_authorization'
        ]
        
        for field in direct_fields:
            if field in request.form and request.form[field].strip():
                form_data[field] = request.form[field]

        # Procesar checkbox terms
        if 'terms' in request.form:
            form_data['terms'] = True

        # MANEJAR ARCHIVOS
        uploaded_files = []
        if 'project_files' in request.files:
            files = request.files.getlist('project_files')
            for file in files:
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    # Crear directorio si no existe
                    upload_dir = f"uploads/user_{session['user_id']}"
                    os.makedirs(upload_dir, exist_ok=True)
                    
                    # Guardar archivo
                    file_path = os.path.join(upload_dir, filename)
                    file.save(file_path)
                    uploaded_files.append(filename)
            
            # Si hay archivos, agregarlos a form_data
            if uploaded_files:
                form_data['project_files'] = ', '.join(uploaded_files)

        current_step = request.form.get('current_step', type=int)

        # Verificar si existe proyecto draft
        cur.execute("""
            SELECT id, project_files FROM projects 
            WHERE user_id = %s AND status = 'draft'
            ORDER BY updated_at DESC LIMIT 1
        """, (session['user_id'],))
        
        existing = cur.fetchone()

        if existing and form_data:
            # UPDATE - mantener archivos existentes si no se subieron nuevos
            if 'project_files' not in form_data and existing.get('project_files'):
                form_data['project_files'] = existing['project_files']
                
            update_fields = ', '.join([f"{field} = %s" for field in form_data.keys()])
            values = list(form_data.values())
            
            sql_update = f"""
                UPDATE projects SET 
                {update_fields}, 
                updated_at = CURRENT_TIMESTAMP
                {', current_step = %s' if current_step is not None else ''}
                WHERE user_id = %s
            """
            
            if current_step is not None:
                values.append(current_step)
            values.append(session['user_id'])
            
            cur.execute(sql_update, values)
            project_id = existing['id']
            
        elif not existing and form_data:
            # INSERT
            fields = list(form_data.keys())
            values = list(form_data.values())
            
            sql_insert = f"""
                INSERT INTO projects (
                    user_id, {', '.join(fields)}, status, updated_at
                    {', current_step' if current_step is not None else ''}
                ) VALUES (
                    %s, {', '.join(['%s']*len(fields))}, 'draft', CURRENT_TIMESTAMP
                    {', %s' if current_step is not None else ''}
                ) RETURNING id
            """

            params = [session['user_id']] + values
            if current_step is not None:
                params.append(current_step)

            cur.execute(sql_insert, params)
            result = cur.fetchone()
            project_id = result['id']
        else:
            project_id = existing['id'] if existing else None

        conn.commit()
        
        # Verificar si hay archivos para informar al frontend
        has_files = bool(form_data.get('project_files') or (existing and existing.get('project_files')))
        
        return jsonify({
            'success': True, 
            'project_id': project_id,
            'has_files': has_files
        })

    except Exception as e:
        print(f"Error en autosave: {e}")
        if conn:
            conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            cur.close()
            conn.close()


@admin_bp.route('/project/load-progress')
def load_project_progress():
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT * FROM projects 
            WHERE user_id = %s AND status = 'draft'
            ORDER BY updated_at DESC LIMIT 1
        """, (session['user_id'],))

        project = cur.fetchone()

        # Si usas RealDictCursor, project ya es un dict
        # Si no, conviértelo:
        if project and not isinstance(project, dict):
            colnames = [desc[0] for desc in cur.description]
            project = dict(zip(colnames, project))

        return jsonify({
            'success': True,
            'project': project if project else None
        })

    except Exception as e:
        print(f"Error cargando progreso: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            cur.close()
            conn.close()

    print(f"Session: {session}")
    print(f"User ID: {session.get('user_id')}")


@admin_bp.route('/terminos')
def terminos():
    return render_template('terminos.html')
