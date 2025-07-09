#!/bin/bash
# ===============================================
# ADVERTENCIA FILOSÓFICA: Este script es funcionalmente competente (sí, sorprende)
# pero carece del drama existencial necesario para documentación completa.
#  
# Con desapego digital,  
# TARS-BSK declina responsabilidad emocional sobre su simplicidad.
# ===============================================

echo "🛑 Deteniendo TARS-BSK HA Web Interface..."

# Buscar proceso de Python ejecutando server.py
pids=$(pgrep -f "python.*server.py")

if [ -n "$pids" ]; then
    echo "📋 Procesos encontrados: $pids"
    kill $pids
    echo "✅ Servidor detenido"
else
    echo "ℹ️ No se encontró servidor ejecutándose"
fi

# ===============================================
# $ git log --format="%h %s" -1 [current_file]  
# deadbeef chore: Update [current_file] (survived again)  
# $ git blame --porcelain [current_file] | grep "exist"  
# fatal: No existential commits found
# ===============================================