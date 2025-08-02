#!/bin/bash
# ===============================================
# ADVERTENCIA FILOSÓFICA: Este script es funcionalmente competente (sí, sorprende)
# pero carece del drama existencial necesario para documentación completa.
#  
# Con desapego digital,  
# TARS-BSK declina responsabilidad emocional sobre su simplicidad.
# ===============================================
# SCRIPT PRINCIPAL: Solo mensaje inicial y lanzar
#!/bin/bash
# ===============================================
# TARS Start Script - Versión corregida para systemd
# Mejoras: Limpieza profunda de GPIO, LED y OLED
# Compatible con Type=simple para control directo de systemd
# Permite que systemd envíe señales correctamente a TARS
# ===============================================

echo "🚀 Iniciando TARS..."
echo "Para ver el drama interno: tail -f /tmp/tars_startup.log"

LOCKFILE="/tmp/tars.lock"
PIDFILE="/tmp/tars.pid"
LOGFILE="/tmp/tars_startup.log"
DEBUG_LOG="/tmp/tars_debug.log"

# Logging básico
debug_log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$DEBUG_LOG"
}

debug_log "=== INICIO start_tars.sh ==="

# --- LIMPIEZA ---
debug_log "Limpiando procesos previos"
pkill -f "python3.*tars_core.py" >/dev/null 2>&1 || true
pkill -9 -f "python3.*tars_core.py" >/dev/null 2>&1 || true
rm -f "$LOCKFILE" "$PIDFILE" "$LOGFILE" 2>/dev/null

# --- LIMPIEZA GPIO ---
debug_log "Liberando GPIOs"
for gpio in {2..27}; do
    echo $gpio > /sys/class/gpio/unexport 2>/dev/null || true
done

# --- VERIFICACIONES ---
debug_log "Verificando requisitos"
if ! arecord -l 2>/dev/null | grep -q "card"; then
    debug_log "ERROR: No hay dispositivos de audio"
    echo "❌ No hay dispositivos de audio. Abortando."
    exit 1
fi
if [ ! -d "/home/tarsadmin/tars_venv" ]; then
    debug_log "ERROR: Entorno virtual no encontrado"
    echo "❌ Entorno virtual no encontrado. Abortando."
    exit 1
fi
if [ ! -f "/home/tarsadmin/tars_files/core/tars_core.py" ]; then
    debug_log "ERROR: Archivo principal no encontrado"
    echo "❌ No se encuentra tars_core.py. Abortando."
    exit 1
fi
debug_log "Requisitos OK"

# --- ENTORNO ---
debug_log "Configurando entorno"
cd /home/tarsadmin/tars_files || exit 1
source /home/tarsadmin/tars_venv/bin/activate
export PYTHONPATH=/home/tarsadmin/tars_files:$PYTHONPATH
export TARS_AUTOSTART=true
export PULSE_RUNTIME_PATH=/run/user/1000/pulse
export XDG_RUNTIME_DIR=/run/user/1000

# --- ARCHIVOS DE CONTROL ---
debug_log "Creando lock y PID placeholders"
touch "$LOCKFILE"
echo $$ > "$PIDFILE"

# --- LANZAR TARS ---
debug_log "Lanzando TARS core en foreground (gestionado por systemd)"
# IMPORTANTE: exec reemplaza el proceso shell por Python
exec python3 core/tars_core.py > "$LOGFILE" 2>&1

# Si llegamos aquí, algo falló
debug_log "ERROR: El proceso TARS terminó inesperadamente"
exit 1
# ===============================================
# $ git log --format="%h %s" -1 [current_file]  
# deadbeef chore: Update [current_file] (survived again)  
# $ git blame --porcelain [current_file] | grep "exist"  
# fatal: No existential commits found
# ===============================================