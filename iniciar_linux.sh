#!/usr/bin/env bash
# Script de inicio rápido para Linux / macOS
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "======================================================================"
echo "   INICIANDO SISTEMA ESTADÍSTICO INTERACTIVO (WEB)"
echo "======================================================================"
echo ""

# 1. Verificar entorno virtual local
if [ ! -f ".venv/bin/python" ]; then
    echo "[AVISO] Configurando entorno virtual local (.venv) por primera vez..."
    python3 -m venv .venv
    .venv/bin/pip install -r requirements.txt
    echo "[OK] Entorno virtual configurado exitosamente."
    echo ""
fi

# 2. Iniciar servidor web (abre automáticamente el navegador predeterminado del sistema)
echo "Iniciando servidor local..."
echo "Tu navegador predeterminado se abrirá automáticamente en: http://127.0.0.1:5000"
echo "Presiona Ctrl+C para detener el servidor cuando termines."
echo ""

.venv/bin/python app.py
