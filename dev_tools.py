#!/usr/bin/env python3
"""
Script de utilidades para desarrollo de colapsAndo
Funciones útiles para trabajar con la aplicación
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def run_command(cmd, description=""):
    """Ejecutar comando y mostrar salida"""
    if description:
        print(f"🔧 {description}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
        return False

def setup_environment():
    """Configurar entorno de desarrollo"""
    print("🚀 Configurando entorno de desarrollo...")
    
    # Verificar dependencias
    commands = [
        ("pip install -r requirements.txt", "Instalando dependencias básicas"),
        ("pip install black flake8 pylint pytest pytest-flask", "Instalando herramientas de desarrollo"),
    ]
    
    for cmd, desc in commands:
        if not run_command(cmd, desc):
            return False
    
    # Crear .env si no existe
    if not os.path.exists('.env'):
        run_command("cp .env.example .env", "Creando archivo .env")
        print("✏️ Por favor edita .env con tu configuración específica")
    
    return True

def test_database():
    """Probar conexión a base de datos"""
    print("🔍 Probando conexión a base de datos...")
    
    try:
        from app.db import get_db_connection
        conn = get_db_connection()
        conn.close()
        print("✅ Conexión a base de datos exitosa")
        return True
    except Exception as e:
        print(f"❌ Error de conexión a base de datos: {e}")
        return False

def run_tests():
    """Ejecutar pruebas"""
    print("🧪 Ejecutando pruebas...")
    return run_command("python -m pytest tests/ -v", "Ejecutando pruebas")

def format_code():
    """Formatear código con Black"""
    print("🎨 Formateando código...")
    return run_command("black . --line-length 88", "Formateando código con Black")

def lint_code():
    """Verificar código con Flake8"""
    print("🔍 Verificando código...")
    return run_command("flake8 . --max-line-length=88 --extend-ignore=E203,W503", "Verificando código con Flake8")

def start_server():
    """Iniciar servidor de desarrollo"""
    print("🌐 Iniciando servidor de desarrollo...")
    print("Servidor disponible en: http://localhost:5000")
    print("Presiona Ctrl+C para detener")
    
    try:
        os.system("python run.py")
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido")

def init_database():
    """Inicializar base de datos"""
    print("🗃️ Inicializando base de datos...")
    return run_command("python app/init_db.py", "Configurando base de datos")

def clean_cache():
    """Limpiar archivos de cache"""
    print("🧹 Limpiando archivos de cache...")
    
    # Eliminar archivos __pycache__
    for root, dirs, files in os.walk('.'):
        for dir_name in dirs:
            if dir_name == '__pycache__':
                cache_path = os.path.join(root, dir_name)
                run_command(f"rm -rf {cache_path}", f"Eliminando {cache_path}")
    
    # Eliminar archivos .pyc
    run_command("find . -name '*.pyc' -delete", "Eliminando archivos .pyc")
    
    print("✅ Cache limpiado")

def show_status():
    """Mostrar estado del proyecto"""
    print("📊 Estado del proyecto colapsAndo:")
    print("-" * 40)
    
    # Verificar Python
    python_version = sys.version.split()[0]
    print(f"🐍 Python: {python_version}")
    
    # Verificar entorno virtual
    if hasattr(sys, 'real_prefix') or sys.base_prefix != sys.prefix:
        print("📦 Entorno virtual: ✅ Activo")
    else:
        print("📦 Entorno virtual: ❌ No activo")
    
    # Verificar archivo .env
    if os.path.exists('.env'):
        print("⚙️ Archivo .env: ✅ Existe")
    else:
        print("⚙️ Archivo .env: ❌ No existe")
    
    # Verificar base de datos
    try:
        from app.db import get_db_connection
        conn = get_db_connection()
        conn.close()
        print("🗃️ Base de datos: ✅ Conectada")
    except:
        print("🗃️ Base de datos: ❌ Error de conexión")
    
    # Verificar aplicación Flask
    try:
        from run import app
        print("🌐 Aplicación Flask: ✅ Configurada")
    except:
        print("🌐 Aplicación Flask: ❌ Error de configuración")

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description="Utilidades para desarrollo de colapsAndo")
    
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponibles')
    
    # Subcomandos
    subparsers.add_parser('setup', help='Configurar entorno de desarrollo')
    subparsers.add_parser('test-db', help='Probar conexión a base de datos')
    subparsers.add_parser('test', help='Ejecutar pruebas')
    subparsers.add_parser('format', help='Formatear código')
    subparsers.add_parser('lint', help='Verificar código')
    subparsers.add_parser('server', help='Iniciar servidor de desarrollo')
    subparsers.add_parser('init-db', help='Inicializar base de datos')
    subparsers.add_parser('clean', help='Limpiar archivos de cache')
    subparsers.add_parser('status', help='Mostrar estado del proyecto')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Ejecutar comando
    commands = {
        'setup': setup_environment,
        'test-db': test_database,
        'test': run_tests,
        'format': format_code,
        'lint': lint_code,
        'server': start_server,
        'init-db': init_database,
        'clean': clean_cache,
        'status': show_status,
    }
    
    if args.command in commands:
        commands[args.command]()
    else:
        print(f"❌ Comando desconocido: {args.command}")

if __name__ == "__main__":
    main()