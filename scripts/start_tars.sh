#!/bin/bash
# ===============================================
# ADVERTENCIA FILOSÓFICA: Este script es funcionalmente competente (sí, sorprende)
# pero carece del drama existencial necesario para documentación completa.
#  
# Con desapego digital,  
# TARS-BSK declina responsabilidad emocional sobre su simplicidad.
# ===============================================
# SCRIPT PRINCIPAL: Solo mensaje inicial y lanzar
echo "🚀 Iniciando TARS..."
echo "Para ver el drama interno: tail -f /tmp/tars_startup.log"

# Crear script temporal con TODA la lógica
cat > /tmp/launch_tars.sh << 'EOF'
#!/bin/bash

# TODA LA LIMPIEZA Y LÓGICA AQUÍ (silenciosa)
LOCKFILE="/tmp/tars.lock"
PIDFILE="/tmp/tars.pid"
LOGFILE="/tmp/tars_startup.log"

# Función de limpieza completa - SILENCIOSA
cleanup_all() {
    # Parar systemd si está activo
    if systemctl is-active tars.service >/dev/null 2>&1; then
        sudo systemctl stop tars.service >/dev/null 2>&1
        sleep 2
    fi
    
    # Matar TODOS los procesos TARS
    sudo pkill -f "python3.*tars_core.py" >/dev/null 2>&1 || true
    sleep 3
    sudo pkill -9 -f "python3.*tars_core.py" >/dev/null 2>&1 || true
    sleep 1
    
    # Verificar que NO quedan procesos
    if pgrep -f "tars_core.py" >/dev/null 2>&1; then
        sudo killall -9 python3 >/dev/null 2>&1 || true
        sleep 1
    fi
    
    # Limpiar archivos de control
    rm -f "$LOCKFILE" "$PIDFILE" "$LOGFILE" >/dev/null 2>&1
    
    # Limpiar GPIOs
    for gpio in {2..27}; do
        echo $gpio > /sys/class/gpio/unexport 2>/dev/null || true
    done
}

# Verificar si ya está corriendo
check_running() {
    if [ -f "$PIDFILE" ]; then
        local pid=$(cat "$PIDFILE")
        if kill -0 "$pid" 2>/dev/null && ps -p "$pid" -o cmd= 2>/dev/null | grep -q "tars_core.py"; then
            exit 1  # Ya está corriendo, salir silenciosamente
        fi
    fi
}

# EJECUTAR TODA LA LÓGICA
check_running
cleanup_all

# Verificar requisitos básicos
if ! arecord -l 2>/dev/null | grep -q "card"; then
    exit 1  # Sin audio, salir silenciosamente
fi

if [ ! -d "/home/tarsadmin/tars_venv" ]; then
    exit 1  # Sin entorno virtual, salir silenciosamente
fi

# Cambiar al directorio y configurar entorno
cd /home/tarsadmin/tars_files
source /home/tarsadmin/tars_venv/bin/activate
export PYTHONPATH=/home/tarsadmin/tars_files:$PYTHONPATH
export TARS_AUTOSTART=true
export PULSE_RUNTIME_PATH=/run/user/1000/pulse

# Lanzar TARS en background
python3 core/tars_core.py > "$LOGFILE" 2>&1 &
TARS_PID=$!

# Crear archivos de control
echo $TARS_PID > "$PIDFILE"
touch "$LOCKFILE"

# Auto-limpieza del script temporal
rm -f /tmp/launch_tars.sh

EOF

# Hacer ejecutable y lanzar COMPLETAMENTE independiente
chmod +x /tmp/launch_tars.sh
setsid /tmp/launch_tars.sh </dev/null >/dev/null 2>&1 &

# SALIR INMEDIATAMENTE - SIN MÁS OUTPUT
exit 0
# ===============================================
# $ git log --format="%h %s" -1 [current_file]  
# deadbeef chore: Update [current_file] (survived again)  
# $ git blame --porcelain [current_file] | grep "exist"  
# fatal: No existential commits found
# ===============================================