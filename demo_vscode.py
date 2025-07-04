#!/usr/bin/env python3
"""
Demostración de las funcionalidades configuradas para VSCode
"""

import os
import sys
from pathlib import Path

def demo_configuracion_vscode():
    """Demostrar la configuración de VSCode"""
    print("🎯 Demostración de configuración VSCode para colapsAndo")
    print("=" * 60)
    
    # Verificar archivos de configuración
    archivos_vscode = [
        '.vscode/settings.json',
        '.vscode/launch.json', 
        '.vscode/tasks.json',
        '.vscode/extensions.json'
    ]
    
    print("\n📁 Archivos de configuración de VSCode:")
    for archivo in archivos_vscode:
        if os.path.exists(archivo):
            print(f"  ✅ {archivo}")
        else:
            print(f"  ❌ {archivo}")
    
    # Verificar herramientas de desarrollo
    print("\n🛠️ Herramientas de desarrollo:")
    herramientas = [
        'setup_dev.sh',
        'dev_tools.py',
        '.env.example',
        'DESARROLLO_VSCODE.md'
    ]
    
    for herramienta in herramientas:
        if os.path.exists(herramienta):
            print(f"  ✅ {herramienta}")
        else:
            print(f"  ❌ {herramienta}")
    
    # Mostrar funcionalidades disponibles
    print("\n🚀 Funcionalidades disponibles en VSCode:")
    funcionalidades = [
        "Depuración de Flask (F5)",
        "Tareas automatizadas (Ctrl+Shift+P)",
        "Formateo automático al guardar",
        "Linting en tiempo real",
        "Autocompletado para Python/Flask/Jinja2",
        "Conexión a base de datos con SQLTools",
        "Extensiones recomendadas automáticas",
        "Terminal integrado configurado"
    ]
    
    for i, func in enumerate(funcionalidades, 1):
        print(f"  {i}. {func}")
    
    # Mostrar comandos útiles
    print("\n💻 Comandos útiles:")
    comandos = [
        "python dev_tools.py status - Ver estado del proyecto",
        "python dev_tools.py server - Iniciar servidor",
        "python dev_tools.py format - Formatear código",
        "python dev_tools.py lint - Verificar código",
        "./setup_dev.sh - Configuración rápida"
    ]
    
    for comando in comandos:
        print(f"  • {comando}")
    
    print("\n🎉 ¡Configuración completa para desarrollo con VSCode!")
    print("📖 Consulta DESARROLLO_VSCODE.md para más detalles")

if __name__ == "__main__":
    demo_configuracion_vscode()