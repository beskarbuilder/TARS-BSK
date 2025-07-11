#!/bin/bash
# ===============================================
# ADVERTENCIA FILOSÓFICA: Este script es funcionalmente competente (sí, sorprende)
# pero carece del drama existencial necesario para documentación completa.
#  
# Con desapego digital,  
# TARS-BSK Backup Manager declina responsabilidad emocional sobre su simplicidad.
# ===============================================

echo "🛑 Deteniendo TARS-BSK Backup Manager..."

# Buscar proceso de Python ejecutando backup_server.py
pids=$(pgrep -f "python.*backup_server.py")

if [ -n "$pids" ]; then
    echo "📋 Procesos encontrados: $pids"
    kill $pids
    sleep 2
    
    # Verificar si aún están corriendo y forzar si es necesario
    remaining=$(pgrep -f "python.*backup_server.py")
    if [ -n "$remaining" ]; then
        echo "🔨 Forzando cierre..."
        kill -9 $remaining
    fi
    
    echo "✅ Backup Manager detenido"
else
    echo "ℹ️ No se encontró Backup Manager ejecutándose"
fi

# También detener cualquier proceso de backup en curso
backup_pids=$(pgrep -f "rsync.*tars_backup")
if [ -n "$backup_pids" ]; then
    echo "⚠️ Deteniendo backups en progreso..."
    kill $backup_pids
    echo "✅ Procesos de backup detenidos"
fi

# ===============================================
# $ git log --format="%h %s" -1 [current_file]  
# deadbeef chore: Update stop_backup.sh (backup consciousness deactivated)  
# $ git blame --porcelain [current_file] | grep "backup"  
# 42backup feat: Add backup manager shutdown protocol
# ===============================================