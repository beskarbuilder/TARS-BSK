#!/bin/bash
# ======================================================================
# ADVERTENCIA FILOSÓFICA: Este script es funcionalmente competente (sí, sorprende)
# pero carece del drama existencial necesario para documentación completa.
#  
# Con desapego digital,  
# TARS-BSK declina responsabilidad emocional sobre su simplicidad.
# ======================================================================
# TERMINAL SESSION RECORDER - SOLO COMANDOS NATIVOS
# Graba TODO usando únicamente lo que trae el sistema
# ======================================================================
#
# Permisos
# chmod +x scripts/terminal_session_recorder.sh
#
# Y listo para usar:
# ./scripts/terminal_session_recorder.sh
#
# ======================================================================
# 
# PARA LIMPIAR EL LOG DESPUÉS (quitar códigos ANSI):
# Instalar herramienta específica
# sudo apt install ansifilter
# ansifilter < tu_log.log | grep -v '^]0;' | grep -v '^0;' > log_limpio.log
#
# ======================================================================

# =======================================================================
# 1. CONFIGURACION INICIAL
# =======================================================================
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
SESSION_LOG="tars_session_${TIMESTAMP}.log"

# =======================================================================
# 2. BANNER Y PRESENTACION
# =======================================================================
clear
echo "🎬 TARS INSTALLATION SESSION RECORDER"
echo "======================================"
echo "📹 Grabando toda tu sesión de terminal"
echo "⏰ Solo comandos nativos del sistema"
echo "🎯 Cero dependencias externas"
echo "======================================"
echo ""
echo "📝 Archivo de sesión: $SESSION_LOG"
echo ""

# =======================================================================
# 3. CAPTURA DE INFORMACION DEL SISTEMA
# =======================================================================
echo "=======================================================================" > "$SESSION_LOG"
echo "TARS INSTALLATION SESSION STARTED" >> "$SESSION_LOG"
echo "=======================================================================" >> "$SESSION_LOG"
echo "📅 Fecha: $(date)" >> "$SESSION_LOG"
echo "🤖 Sistema: $(uname -a)" >> "$SESSION_LOG"
echo "👤 Usuario: $(whoami)" >> "$SESSION_LOG"
echo "🏠 Directorio: $(pwd)" >> "$SESSION_LOG"

# Temperatura si está disponible (Raspberry Pi)
if command -v vcgencmd >/dev/null 2>&1; then
    echo "🌡️  Temperatura: $(vcgencmd measure_temp)" >> "$SESSION_LOG"
fi

# Memoria y disco
echo "💾 Memoria: $(free -h | head -2 | tail -1)" >> "$SESSION_LOG"
echo "💿 Disco: $(df -h . | tail -1)" >> "$SESSION_LOG"

echo "🎬 SESIÓN INICIADA - TIMESTAMP: $(date +%s)" >> "$SESSION_LOG"
echo "=======================================================================" >> "$SESSION_LOG"
echo "" >> "$SESSION_LOG"

# =======================================================================
# 4. INICIO DE GRABACION
# =======================================================================
echo "🚀 Iniciando grabación..."
echo "💡 Para terminar: escribe 'exit' o presiona Ctrl+D"
echo ""

# EL COMANDO MÁGICO (viene en TODO Linux)
script -a "$SESSION_LOG"

# =======================================================================
# 5. INFORMACION FINAL POST-SESION
# =======================================================================
echo "" >> "$SESSION_LOG"
echo "=======================================================================" >> "$SESSION_LOG"
echo "SESIÓN TERMINADA" >> "$SESSION_LOG"
echo "=======================================================================" >> "$SESSION_LOG"
echo "📅 Fecha fin: $(date)" >> "$SESSION_LOG"

# Temperatura final si disponible
if command -v vcgencmd >/dev/null 2>&1; then
    echo "🌡️  Temperatura final: $(vcgencmd measure_temp)" >> "$SESSION_LOG"
fi

echo "💾 Memoria final: $(free -h | head -2 | tail -1)" >> "$SESSION_LOG"
echo "💿 Disco final: $(df -h . | tail -1)" >> "$SESSION_LOG"
echo "🏁 TIMESTAMP FINAL: $(date +%s)" >> "$SESSION_LOG"
echo "=======================================================================" >> "$SESSION_LOG"

# =======================================================================
# 6. RESUMEN Y ESTADISTICAS FINALES
# =======================================================================
clear
echo "🎉 ¡SESIÓN GRABADA!"
echo "=================="
echo ""
echo "📁 Archivo: $SESSION_LOG"
echo "📏 Tamaño: $(ls -lh "$SESSION_LOG" | awk '{print $5}')"
echo "📃 Líneas: $(cat "$SESSION_LOG" | wc -l)"
echo ""
echo "🔍 Para ver el contenido:"
echo "   cat $SESSION_LOG"
echo ""
echo "📤 Para compartir:"
echo "   Sube el archivo: $SESSION_LOG"
echo ""
echo "✨ ¡PRUEBA DEFINITIVA LISTA!"