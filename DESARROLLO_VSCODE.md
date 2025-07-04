# Guía de Desarrollo para colapsAndo en Visual Studio Code

## Configuración del Entorno de Desarrollo

### 1. Requisitos Previos
- Python 3.8 o superior
- PostgreSQL instalado y configurado
- Visual Studio Code
- Git

### 2. Configuración Inicial del Proyecto

#### Paso 1: Clonar el repositorio
```bash
git clone https://github.com/lacontraintuitiva/colapsAndo.git
cd colapsAndo
```

#### Paso 2: Crear entorno virtual
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

#### Paso 3: Instalar dependencias
```bash
pip install -r requirements.txt
```

#### Paso 4: Configurar variables de entorno
```bash
cp .env.example .env
# Editar .env con tus configuraciones específicas
```

#### Paso 5: Configurar base de datos
```bash
# Crear base de datos PostgreSQL
createdb colapsando

# Ejecutar migraciones
python app/init_db.py
```

### 3. Configuración de VSCode

#### Extensiones Recomendadas
Al abrir el proyecto en VSCode, se te sugerirán automáticamente las siguientes extensiones:

**Python:**
- Python (ms-python.python)
- Python Extension Pack
- Pylint, Flake8, Black Formatter
- Python Environment Manager

**Web Development:**
- Jinja HTML (samuelcolvin.jinjahtml)
- Auto Rename Tag, Auto Close Tag
- Path Intellisense
- Live Server

**Database:**
- SQLTools
- SQLTools PostgreSQL Driver

#### Configuración Automática
El proyecto incluye configuración automática de VSCode en la carpeta `.vscode/`:

- **settings.json**: Configuración del entorno Python, linting, formateo
- **launch.json**: Configuraciones de depuración para Flask
- **tasks.json**: Tareas automatizadas para desarrollo
- **extensions.json**: Extensiones recomendadas

### 4. Funcionalidades Disponibles en VSCode

#### Depuración
- **F5**: Iniciar servidor Flask en modo depuración
- **Ctrl+F5**: Ejecutar sin depuración
- Puntos de interrupción en código Python y templates Jinja2

#### Tareas Automatizadas (Ctrl+Shift+P → Tasks)
- **Install Dependencies**: Instalar dependencias del proyecto
- **Start Development Server**: Iniciar servidor de desarrollo
- **Initialize Database**: Configurar base de datos
- **Run Tests**: Ejecutar pruebas
- **Format Code**: Formatear código con Black
- **Lint Code**: Verificar código con Flake8
- **Check Database Connection**: Verificar conectividad a BD

#### Funciones de Desarrollo
- **Autocompletado**: IntelliSense para Python, HTML, CSS, JavaScript
- **Formateo automático**: Al guardar archivos
- **Linting en tiempo real**: Detección de errores de código
- **Navegación**: Ir a definición, buscar referencias
- **Refactoring**: Renombrar variables, extraer métodos

### 5. Estructura del Proyecto

```
colapsAndo/
├── app/
│   ├── __init__.py
│   ├── admin.py          # Funciones administrativas
│   ├── auth.py           # Autenticación de usuarios
│   ├── register.py       # Registro de usuarios
│   ├── db.py             # Conexión a base de datos
│   └── init_db.py        # Inicialización de BD
├── static/
│   ├── css/              # Estilos CSS
│   ├── js/               # Scripts JavaScript
│   └── images/           # Imágenes
├── templates/            # Templates Jinja2
├── uploads/              # Archivos subidos
├── .vscode/              # Configuración de VSCode
├── requirements.txt      # Dependencias Python
├── run.py               # Punto de entrada de la aplicación
└── .env.example         # Ejemplo de variables de entorno
```

### 6. Flujo de Desarrollo

#### Desarrollo de Funcionalidades
1. Crear nueva rama: `git checkout -b feature/nueva-funcionalidad`
2. Iniciar servidor de desarrollo: F5 o Task "Start Development Server"
3. Editar código con autocompletado y linting
4. Probar cambios en navegador (http://localhost:5000)
5. Usar depurador para resolver problemas
6. Formatear código: Task "Format Code"
7. Verificar calidad: Task "Lint Code"
8. Hacer commit y push

#### Depuración
- **Puntos de interrupción**: Click en el margen izquierdo del editor
- **Variables**: Panel de variables en la vista de depuración
- **Consola**: Evaluar expresiones en tiempo real
- **Call Stack**: Ver pila de llamadas

#### Base de Datos
- **SQLTools**: Conectar y explorar base de datos desde VSCode
- **Queries**: Ejecutar consultas SQL directamente
- **Schema**: Visualizar estructura de tablas

### 7. Comandos Útiles

#### Terminal Integrado (Ctrl+`)
```bash
# Activar entorno virtual
source venv/bin/activate

# Instalar nueva dependencia
pip install nueva-dependencia
pip freeze > requirements.txt

# Ejecutar aplicación
python run.py

# Verificar conexión a BD
python -c "from app.db import get_db_connection; conn = get_db_connection(); print('OK'); conn.close()"
```

#### Atajos de Teclado Útiles
- **Ctrl+Shift+P**: Paleta de comandos
- **Ctrl+`**: Terminal integrado
- **F5**: Iniciar depuración
- **Ctrl+F5**: Ejecutar sin depuración
- **Ctrl+Shift+F**: Buscar en todo el proyecto
- **Ctrl+Shift+R**: Refactorizar
- **Ctrl+Shift+I**: Formatear documento

### 8. Mejores Prácticas

#### Código Python
- Usar **Black** para formateo automático
- Seguir **PEP 8** para estilo de código
- Agregar **docstrings** a funciones importantes
- Usar **type hints** cuando sea posible

#### Templates
- Usar **Jinja2** con sintaxis apropiada
- Separar lógica del template
- Usar **herencia** de templates

#### JavaScript
- Usar **console.log** para depuración
- Seguir **ES6+** cuando sea posible
- Organizar código en módulos

### 9. Resolución de Problemas

#### Error: "No module named 'app'"
```bash
# Verificar que el entorno virtual esté activado
source venv/bin/activate
pip install -r requirements.txt
```

#### Error de conexión a base de datos
```bash
# Verificar variables de entorno
cat .env
# Verificar que PostgreSQL esté ejecutándose
sudo systemctl status postgresql
```

#### Error de puerto ocupado
```bash
# Encontrar proceso usando puerto 5000
lsof -i :5000
# Terminar proceso
kill -9 <PID>
```

### 10. Recursos Adicionales

- [Documentación de Flask](https://flask.palletsprojects.com/)
- [Documentación de Jinja2](https://jinja.palletsprojects.com/)
- [Guía de PostgreSQL](https://www.postgresql.org/docs/)
- [VSCode Python Tutorial](https://code.visualstudio.com/docs/python/python-tutorial)

### 11. Contacto y Soporte

Para obtener ayuda con el desarrollo:
- Crear issue en GitHub
- Contactar al equipo de desarrollo
- Consultar documentación del proyecto

---

**¡Feliz desarrollo! 🚀**