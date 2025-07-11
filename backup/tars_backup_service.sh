#!/bin/bash
# ===============================================
# ADVERTENCIA FILOSÓFICA: Este script es funcionalmente competente (sí, sorprende)
# pero carece del drama existencial necesario para documentación completa.
#  
# Con desapego digital,  
# TARS-BSK Backup Manager declina responsabilidad emocional sobre su simplicidad.
# ===============================================
# ≫ PROTOCOLO DE GESTIÓN DE SERVICIO BACKUP | tars_backup_service.sh ≪
# -----------------------------------------------
# Función: Instalar, eliminar o verificar el servicio TARS-BSK Backup Manager
# Uso:
#   ./tars_backup_service.sh install      → Instala el servicio
#   ./tars_backup_service.sh uninstall    → Elimina el servicio
#   ./tars_backup_service.sh status       → Muestra el estado actual
#   ./tars_backup_service.sh logs         → Muestra logs en vivo
# ===============================================

SERVICE_NAME="tars-backup-manager.service"
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
    echo "🔧 Instalando servicio systemd para TARS-BSK Backup Manager..."

    # Verificar que backup_server.py existe
    if [ ! -f "$WORKDIR/backup_server.py" ]; then
        echo "❌ backup_server.py no encontrado en $WORKDIR"
        exit 1
    fi

    # Crear directorio de logs
    mkdir -p "$WORKDIR/backup/logs"

    sudo tee "$SERVICE_PATH" > /dev/null <<EOL
[Unit]
Description=TARS-BSK Backup Manager
After=network.target multi-user.target
Wants=network.target
Requires=multi-user.target

[Service]
Type=simple
User=$USER_NAME
Group=$USER_NAME
WorkingDirectory=$WORKDIR
Environment=PATH=$HOME/tars_venv/bin:$PATH
Environment=PYTHONPATH=$WORKDIR
ExecStart=$PYTHON_BIN $WORKDIR/backup_server.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
KillMode=mixed
TimeoutStopSec=30

# Permisos adicionales para montaje de dispositivos
SupplementaryGroups=plugdev

[Install]
WantedBy=multi-user.target
EOL

    sudo systemctl daemon-reload
    sudo systemctl enable "$SERVICE_NAME"
    sudo systemctl start "$SERVICE_NAME"

    echo "✅ Servicio instalado y iniciado"
    echo "🌐 Backup Manager debería estar disponible en:"
    echo "   http://localhost:9877"
    echo "   http://$(hostname -I | awk '{print $1}'):9877"
    echo ""
    sudo systemctl status "$SERVICE_NAME" --no-pager -l
}

function uninstall_service() {
    echo "🧹 Eliminando servicio $SERVICE_NAME..."
    
    # Detener servicio si está corriendo
    if sudo systemctl is-active --quiet "$SERVICE_NAME"; then
        echo "🛑 Deteniendo servicio..."
        sudo systemctl stop "$SERVICE_NAME"
    fi
    
    # Deshabilitar y eliminar
    sudo systemctl disable "$SERVICE_NAME" 2>/dev/null
    sudo rm -f "$SERVICE_PATH"
    sudo systemctl daemon-reload
    
    echo "✅ Servicio eliminado"
}

function status_service() {
    echo "📊 Estado del servicio:"
    sudo systemctl status "$SERVICE_NAME" --no-pager -l
    echo ""
    
    # Mostrar info de conexión si está activo
    if sudo systemctl is-active --quiet "$SERVICE_NAME"; then
        echo "🌐 Backup Manager disponible en:"
        echo "   http://localhost:9877"
        echo "   http://$(hostname -I | awk '{print $1}'):9877"
        echo ""
    fi
    
    echo "📄 Comandos útiles:"
    echo "   sudo journalctl -u $SERVICE_NAME -f     # Ver logs en vivo"
    echo "   sudo journalctl -u $SERVICE_NAME --since '1 hour ago'  # Logs recientes"
    echo "   sudo systemctl restart $SERVICE_NAME    # Reiniciar servicio"
}

function show_logs() {
    echo "📄 Mostrando logs en vivo (Ctrl+C para salir):"
    echo "═══════════════════════════════════════════════════"
    sudo journalctl -u "$SERVICE_NAME" -f --since "1 hour ago"
}

function check_dependencies() {
    echo "🔍 Verificando dependencias..."
    
    # Python y Flask
    if ! python3 -c "import flask" 2>/dev/null; then
        echo "❌ Flask no instalado"
        return 1
    fi
    
    # udisks2 para montaje
    if ! command -v udisksctl &> /dev/null; then
        echo "⚠️ udisks2 no encontrado (recomendado para montaje automático)"
        echo "   Instalar con: sudo apt install udisks2"
    fi
    
    # Verificar archivo principal
    if [ ! -f "$WORKDIR/backup_server.py" ]; then
        echo "❌ backup_server.py no encontrado"
        return 1
    fi
    
    echo "✅ Dependencias verificadas"
    return 0
}

# --- MAIN ---
check_not_root

case "$1" in
    install)
        check_dependencies && install_service
        ;;
    uninstall)
        uninstall_service
        ;;
    status)
        status_service
        ;;
    logs)
        show_logs
        ;;
    check)
        check_dependencies
        ;;
    *)
        echo "🗄️ TARS-BSK Backup Manager Service Control"
        echo ""
        echo "Uso: $0 {install|uninstall|status|logs|check}"
        echo ""
        echo "Comandos:"
        echo "  install   - Instalar y activar el servicio systemd"
        echo "  uninstall - Eliminar el servicio systemd"
        echo "  status    - Mostrar estado actual del servicio"
        echo "  logs      - Mostrar logs en tiempo real"
        echo "  check     - Verificar dependencias"
        echo ""
        echo "Ejemplo:"
        echo "  ./tars_backup_service.sh install"
        echo "  ./tars_backup_service.sh logs"
        exit 1
        ;;
esac

# ===============================================
# $ git log --format="%h %s" -1 [current_file]  
# deadbeef chore: Update tars_backup_service.sh (backup consciousness managed)  
# $ git blame --porcelain [current_file] | grep "backup"  
# 42backup feat: Add backup manager systemd service management
# ===============================================