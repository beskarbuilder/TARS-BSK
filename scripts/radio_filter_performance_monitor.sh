#!/bin/bash
# ===============================================  
# MONITOR DE RENDIMIENTO PARA RADIO FILTER
# Objetivo: Medir con precisión cuánto sufre tu CPU por un filtro de audio
# ===============================================

#============================================
# CONFIGURACIÓN INICIAL
#============================================
# Rutas y archivos
TARS_ROOT="$HOME/tars_files"            # Directorio base
INPUT_AUDIO="$TARS_ROOT/clean_audio.wav"  # Audio de entrada para pruebas
OUTPUT_AUDIO="$TARS_ROOT/performance_test_filtered.wav"  # Resultado filtrado
RESULTS_FILE="$TARS_ROOT/radio_filter_performance.log"   # Archivo de resultados

# Colores para mensajes en terminal
RED='\033[0;31m'      # Errores
GREEN='\033[0;32m'    # Éxito
YELLOW='\033[0;33m'   # Advertencias
BLUE='\033[0;34m'     # Información
NC='\033[0m'          # Reset color

#============================================
# VERIFICACIÓN DE ENTORNO
#============================================
echo -e "${BLUE}🔍 Verificando entorno...${NC}"

# Verificar directorio de trabajo
cd "$TARS_ROOT" || { 
    echo -e "${RED}❌ Error: No se puede acceder a $TARS_ROOT${NC}"
    echo -e "${YELLOW}   Asegúrate de que el directorio existe${NC}"
    exit 1
}

# Verificar existencia del audio de prueba
if [ ! -f "$INPUT_AUDIO" ]; then
    echo -e "${RED}❌ Error: No se encuentra $INPUT_AUDIO${NC}"
    echo -e "${YELLOW}   Ejecuta primero: python3 scripts/clean_audio_generator.py 'Texto de prueba'${NC}"
    exit 1
fi

# Verificar disponibilidad de los módulos Python necesarios
if ! python3 -c "import sys; sys.path.append('$TARS_ROOT/core'); import radio_filter" 2>/dev/null; then
    echo -e "${RED}❌ Error: No se puede importar el módulo radio_filter${NC}"
    echo -e "${YELLOW}   Asegúrate de que el entorno virtual está activado correctamente${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Entorno verificado correctamente${NC}"

#============================================
# PREPARAR HERRAMIENTAS DE MONITORIZACIÓN
#============================================
# Script para monitorizar CPU/RAM/Hilos en tiempo real
MONITOR_SCRIPT=$(mktemp)
cat > "$MONITOR_SCRIPT" <<EOF
#!/bin/bash
# Monitor de recursos para un PID específico
# Argumentos:
#   \$1: PID del proceso a monitorizar
#   \$2: Archivo de salida para los datos (CSV)

PID=\$1
LOG_FILE=\$2
INTERVAL=0.1  # Intervalo de muestreo (segundos)

# Crear encabezado CSV
echo "timestamp,cpu_percent,memory_kb,threads" > "\$LOG_FILE"

# Bucle de monitorización
while ps -p \$PID > /dev/null; do
    # Obtener métricas actuales
    CPU=\$(ps -p \$PID -o %cpu= | tr -d ' ')     # Porcentaje CPU (puede superar 100% en sistemas multi-núcleo)
    MEM=\$(ps -p \$PID -o rss= | tr -d ' ')      # Memoria residente (KB)
    THREADS=\$(ps -p \$PID -o nlwp= | tr -d ' ') # Número de hilos lógicos

    # Registrar datos con timestamp
    echo "\$(date +%s.%N),\$CPU,\$MEM,\$THREADS" >> "\$LOG_FILE"
    
    # Pausa hasta la siguiente muestra
    sleep \$INTERVAL
done
EOF

chmod +x "$MONITOR_SCRIPT"

# Script Python que ejecutará radio_filter y medirá tiempo
PYTHON_SCRIPT=$(mktemp)
cat > "$PYTHON_SCRIPT" <<EOF
import sys
import time
import os

# Configurar path para importar módulos del proyecto
sys.path.append('$TARS_ROOT/core')
from radio_filter import apply_radio_filter

# Reportar PID para monitorización externa
print("PID:", os.getpid())
sys.stdout.flush()  # Forzar salida inmediata

# Medir tiempo de procesamiento con alta precisión
start_time = time.time()
apply_radio_filter(
    '$INPUT_AUDIO', 
    '$OUTPUT_AUDIO',
    lowcut=200,
    highcut=3000,
    add_noise=True,
    add_compression=True,
    mando_effect=False 
)
elapsed_time = time.time() - start_time

# Reportar tiempo total de procesamiento
print(f"PROCESSING_TIME:{elapsed_time:.6f}")
sys.stdout.flush()
EOF

# Archivos temporales para resultados
PERF_DATA=$(mktemp)
PYTHON_OUTPUT=$(mktemp)

#============================================
# EJECUTAR PRUEBA DE RENDIMIENTO
#============================================
echo -e "${BLUE}⚡ Iniciando procesamiento de audio...${NC}"

# Ejecutar el script Python en segundo plano y capturar su salida
python3 "$PYTHON_SCRIPT" > "$PYTHON_OUTPUT" &
PYTHON_PID=$!

# Esperar a que el script imprima su PID real
sleep 0.5
TARGET_PID=$(grep "PID:" "$PYTHON_OUTPUT" | cut -d' ' -f2)

# Verificar que se obtuvo el PID correctamente
if [ -z "$TARGET_PID" ]; then
    echo -e "${RED}❌ Error: No se pudo obtener el PID del proceso Python${NC}"
    kill -9 $PYTHON_PID 2>/dev/null
    exit 1
fi

echo -e "${GREEN}📊 Monitorizando proceso (PID: $TARGET_PID)...${NC}"

# Iniciar monitorización en segundo plano
"$MONITOR_SCRIPT" "$TARGET_PID" "$PERF_DATA" &
MONITOR_PID=$!

# Esperar a que termine el procesamiento
wait $PYTHON_PID

# Detener monitorización
kill -15 $MONITOR_PID 2>/dev/null
wait $MONITOR_PID 2>/dev/null

#============================================
# ANALIZAR RESULTADOS
#============================================
# Extraer métricas de rendimiento
PROCESSING_TIME=$(grep "PROCESSING_TIME:" "$PYTHON_OUTPUT" | cut -d':' -f2)
MAX_CPU=$(awk -F, 'NR>1 {print $2}' "$PERF_DATA" | sort -nr | head -n1)
AVG_CPU=$(awk -F, 'NR>1 {sum+=$2; count++} END {print sum/count}' "$PERF_DATA")
MAX_MEM=$(awk -F, 'NR>1 {print $3}' "$PERF_DATA" | sort -nr | head -n1)
AVG_MEM=$(awk -F, 'NR>1 {sum+=$3; count++} END {print sum/count}' "$PERF_DATA")
MAX_THREADS=$(awk -F, 'NR>1 {print $4}' "$PERF_DATA" | sort -nr | head -n1)

# Obtener información del audio
DURATION=$(ffprobe -i "$INPUT_AUDIO" -show_entries format=duration -v quiet -of csv="p=0" 2>/dev/null || echo "No disponible")
FILESIZE=$(du -h "$OUTPUT_AUDIO" | cut -f1)

#============================================
# GENERAR INFORME
#============================================
{
    echo "==== RADIO FILTER - ANÁLISIS DE RENDIMIENTO ===="
    echo "Fecha: $(date)"
    echo "Sistema: $(uname -a)"
    echo "---------------------------------------------"
    echo "Archivo de entrada: $(realpath "$INPUT_AUDIO")"
    echo "Archivo de salida: $(realpath "$OUTPUT_AUDIO")"
    echo "Duración del audio: ${DURATION}s"
    echo "Tamaño del archivo: $FILESIZE"
    echo "---------------------------------------------"
    echo "Tiempo de procesamiento: ${PROCESSING_TIME}s"
    
    # Calcular ratio tiempo/duración si hay datos de duración
    if [ "$DURATION" != "No disponible" ]; then
        echo "Ratio tiempo/duración: $(echo "$PROCESSING_TIME $DURATION" | awk '{printf "%.3f", $1/$2}')"
    fi
    
    echo "---------------------------------------------"
    echo "CPU máxima: ${MAX_CPU}%"
    echo "CPU promedio: $(printf "%.2f" $AVG_CPU)%"
    echo "Memoria máxima: $(echo $MAX_MEM | awk '{printf "%.2f MB", $1/1024}')"
    echo "Memoria promedio: $(echo $AVG_MEM | awk '{printf "%.2f MB", $1/1024}')"
    echo "Hilos utilizados: $MAX_THREADS"
    echo "---------------------------------------------"
    echo "Datos completos disponibles en: $PERF_DATA"
    echo "==== FIN DEL ANÁLISIS ===="
} | tee "$RESULTS_FILE"

#============================================
# PRESENTAR RESULTADOS
#============================================
echo -e "\n${GREEN}✅ Proceso completado${NC}"
echo -e "${BLUE}=================================${NC}"
echo -e "${YELLOW}📊 Resultados de rendimiento:${NC}"
echo -e "   - Tiempo: ${PROCESSING_TIME}s"

# Mostrar información de ratio si hay datos de duración
if [ "$DURATION" != "No disponible" ]; then
    echo -e "   - Audio: ${DURATION}s"
    echo -e "   - Ratio: $(echo "$PROCESSING_TIME $DURATION" | awk '{printf "%.3f", $1/$2}')"
fi

echo -e "   - CPU: max ${MAX_CPU}%, promedio $(printf "%.2f" $AVG_CPU)%"
echo -e "   - RAM: max $(echo $MAX_MEM | awk '{printf "%.2f", $1/1024}') MB"
echo -e "   - Tamaño de archivo: $FILESIZE"
echo -e "${BLUE}=================================${NC}"
echo -e "${GREEN}📋 Resultados guardados en: $RESULTS_FILE${NC}"

#============================================
# LIMPIEZA
#============================================
# Preservar datos de rendimiento para análisis posterior
echo -e "${YELLOW}ℹ️ Datos de rendimiento brutos guardados en: $PERF_DATA${NC}"

# Eliminar scripts temporales
rm -f "$MONITOR_SCRIPT" "$PYTHON_SCRIPT" "$PYTHON_OUTPUT"

# Fin del script
exit 0

# ===============================================
# ESTADO: METICULOSAMENTE OBSESIVO (como un ingeniero contando microsegundos)
# ÚLTIMA ACTUALIZACIÓN: Cuando los benchmarks se volvieron más importantes que el audio
# FILOSOFÍA: "No importa cómo suene, importa cuántos ciclos de CPU consume"
# ===============================================
#
#           THIS IS THE BENCHMARK WAY... 
#           (medir hasta el último ciclo, porque cada microsegundo cuenta)
#
# ===============================================