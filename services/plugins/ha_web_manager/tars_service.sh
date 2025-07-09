#!/bin/bash
# ===============================================
# ADVERTENCIA FILOSÓFICA: Este script es funcionalmente competente (sí, sorprende)
# pero carece del drama existencial necesario para documentación completa.
#  
# Con desapego digital,  
# TARS-BSK declina responsabilidad emocional sobre su simplicidad.
# ===============================================
# ≫ PROTOCOLO DE GESTIÓN DE SERVICIO | tars_service.sh ≪
# -----------------------------------------------
# Función: Instalar, eliminar o verificar el servicio TARS-BSK
# Uso:
#   ./tars_service.sh install      → Instala el servicio
#   ./tars_service.sh uninstall    → Elimina el servicio
#   ./tars_service.sh status       → Muestra el estado actual
# ===============================================

SERVICE_NAME="tars-ha-web.service"
SERVICE_PATH="/etc/systemd/system/$SERVICE_NAME"
PYTHON_BIN="$HOME/tars_venv/bin/python"
WORKDIR="$(pwd)"
USER_NAME="$(whoami)"

function check_not_root() {
    if [ "$EUID" -eq 0 ]; then
        echo "❌ No ejecutes este script como root"
        exit 1
    fi
}

function install_service() {
    echo "🔧 Instalando servicio systemd para TARS-BSK..."

    sudo tee "$SERVICE_PATH" > /dev/null <<EOL
[Unit]
Description=TARS-BSK Home Assistant Web Interface
After=network.target
Wants=network.target

[Service]
Type=simple
User=$USER_NAME
Group=$USER_NAME
WorkingDirectory=$WORKDIR
Environment=PATH=$HOME/tars_venv/bin:$PATH
ExecStart=$PYTHON_BIN $WORKDIR/server.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOL

    sudo systemctl daemon-reload
    sudo systemctl enable "$SERVICE_NAME"
    sudo systemctl start "$SERVICE_NAME"

    echo "✅ Servicio instalado y iniciado"
    sudo systemctl status "$SERVICE_NAME" --no-pager -l
}

function uninstall_service() {
    echo "🧹 Eliminando servicio $SERVICE_NAME..."
    sudo systemctl stop "$SERVICE_NAME"
    sudo systemctl disable "$SERVICE_NAME"
    sudo rm -f "$SERVICE_PATH"
    sudo systemctl daemon-reload
    echo "✅ Servicio eliminado"
}

function status_service() {
    echo "📊 Estado del servicio:"
    sudo systemctl status "$SERVICE_NAME" --no-pager -l
    echo ""
    echo "📄 Ver logs con:"
    echo "   sudo journalctl -u $SERVICE_NAME -f"
}

# --- MAIN ---
check_not_root

case "$1" in
    install)
        install_service
        ;;
    uninstall)
        uninstall_service
        ;;
    status)
        status_service
        ;;
    *)
        echo "Uso: $0 {install|uninstall|status}"
        exit 1
        ;;
esac

# ===============================================
# $ git log --format="%h %s" -1 [current_file]  
# deadbeef chore: Update [current_file] (survived again)  
# $ git blame --porcelain [current_file] | grep "exist"  
# fatal: No existential commits found
# ===============================================