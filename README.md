# colapsAndo

Sitio web del Festival colapsAndo

## Configuración para Visual Studio Code

¡Bienvenido/a al desarrollo de colapsAndo! Este proyecto está completamente configurado para aprovechar al máximo las funcionalidades de Visual Studio Code.

### 🚀 Configuración Rápida

#### Opción 1: Script automático
```bash
# Ejecutar script de configuración
./setup_dev.sh
```

#### Opción 2: Configuración manual
```bash
# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tu configuración

# Inicializar base de datos
python app/init_db.py

# Iniciar servidor
python run.py
```

### 🔧 Funcionalidades de VSCode Configuradas

#### Extensiones Recomendadas
Al abrir el proyecto, VSCode sugerirá automáticamente todas las extensiones necesarias:
- **Python**: Soporte completo para Python
- **Jinja2**: Sintaxis highlighting para templates
- **SQLTools**: Conexión y gestión de base de datos
- **Black Formatter**: Formateo automático de código
- **Pylint/Flake8**: Linting en tiempo real

#### Configuraciones Automáticas
- **Depuración**: Configuraciones listas para Flask
- **Tareas**: Automatización de tareas comunes
- **Formateo**: Automático al guardar
- **Linting**: Verificación de código en tiempo real
- **IntelliSense**: Autocompletado avanzado

### 🛠️ Herramientas de Desarrollo

#### Usar con VSCode
- **F5**: Iniciar aplicación en modo depuración
- **Ctrl+Shift+P**: Ejecutar tareas automatizadas
- **Ctrl+`**: Terminal integrado
- **Puntos de interrupción**: Click en margen izquierdo

#### Script de utilidades
```bash
# Mostrar estado del proyecto
python dev_tools.py status

# Formatear código
python dev_tools.py format

# Verificar calidad del código
python dev_tools.py lint

# Iniciar servidor
python dev_tools.py server

# Más opciones
python dev_tools.py --help
```

### 📁 Estructura del Proyecto

```
colapsAndo/
├── .vscode/              # Configuración de VSCode
│   ├── settings.json     # Configuraciones del editor
│   ├── launch.json       # Configuraciones de depuración
│   ├── tasks.json        # Tareas automatizadas
│   └── extensions.json   # Extensiones recomendadas
├── app/                  # Código de la aplicación
├── static/               # Archivos estáticos
├── templates/            # Templates HTML
├── .env.example          # Ejemplo de variables de entorno
├── setup_dev.sh          # Script de configuración rápida
├── dev_tools.py          # Utilidades de desarrollo
└── DESARROLLO_VSCODE.md  # Guía completa de desarrollo
```

### 📖 Documentación Completa

Para una guía detallada de desarrollo con VSCode, consulta:
- [DESARROLLO_VSCODE.md](DESARROLLO_VSCODE.md) - Guía completa
- [.env.example](.env.example) - Configuración de variables de entorno

### 🚀 ¡Comenzar a Desarrollar!

1. **Abrir en VSCode**: `code .`
2. **Instalar extensiones**: VSCode te sugerirá las extensiones automáticamente
3. **Configurar entorno**: Ejecutar `./setup_dev.sh` o seguir pasos manuales
4. **Iniciar depuración**: Presionar F5
5. **¡Desarrollar!**: Aprovechar todas las funcionalidades configuradas

### 💡 Funcionalidades Destacadas

- **Depuración completa**: Puntos de interrupción en Python y templates
- **Autocompletado inteligente**: Para Flask, Jinja2, JavaScript
- **Formateo automático**: Código limpio al guardar
- **Linting en tiempo real**: Detección de errores mientras escribes
- **Gestión de base de datos**: Conexión directa desde VSCode
- **Tareas automatizadas**: Un click para tareas comunes
- **Terminal integrado**: Todo en un solo lugar

¡Feliz desarrollo! 🎉
