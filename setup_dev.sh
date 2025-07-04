#!/bin/bash

# Script de configuración rápida para colapsAndo
# Uso: ./setup_dev.sh

set -e

echo "🚀 Configurando entorno de desarrollo para colapsAndo..."

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no está instalado. Por favor instálalo primero."
    exit 1
fi

# Verificar PostgreSQL
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL no está instalado. Por favor instálalo primero."
    exit 1
fi

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo "📦 Creando entorno virtual..."
    python3 -m venv venv
fi

# Activar entorno virtual
echo "🔧 Activando entorno virtual..."
source venv/bin/activate

# Instalar dependencias
echo "📥 Instalando dependencias..."
pip install -r requirements.txt

# Instalar dependencias de desarrollo
echo "🛠️ Instalando herramientas de desarrollo..."
pip install black flake8 pylint pytest pytest-flask python-dotenv

# Crear archivo .env si no existe
if [ ! -f ".env" ]; then
    echo "⚙️ Creando archivo .env..."
    cp .env.example .env
    echo "✏️ Por favor edita el archivo .env con tu configuración específica"
fi

# Verificar conexión a base de datos
echo "🔍 Verificando conexión a base de datos..."
if python -c "from app.db import get_db_connection; conn = get_db_connection(); print('✅ Conexión exitosa'); conn.close()" 2>/dev/null; then
    echo "✅ Base de datos conectada correctamente"
else
    echo "⚠️ No se pudo conectar a la base de datos. Verifica tu configuración en .env"
fi

# Verificar que la aplicación Flask se puede importar
echo "🧪 Verificando aplicación Flask..."
if python -c "from run import app; print('✅ Flask app importada correctamente')" 2>/dev/null; then
    echo "✅ Aplicación Flask configurada correctamente"
else
    echo "❌ Error al importar aplicación Flask"
fi

echo ""
echo "🎉 ¡Configuración completada!"
echo ""
echo "Próximos pasos:"
echo "1. Edita el archivo .env con tu configuración específica"
echo "2. Ejecuta 'python app/init_db.py' para configurar la base de datos"
echo "3. Ejecuta 'python run.py' para iniciar el servidor de desarrollo"
echo "4. Abre VSCode y disfruta del desarrollo con todas las funcionalidades configuradas"
echo ""
echo "Para activar el entorno virtual en el futuro:"
echo "  source venv/bin/activate"
echo ""
echo "¡Feliz desarrollo! 🚀"