#!/bin/bash
# ===============================================
# ADVERTENCIA FILOSÓFICA: Este script es funcionalmente competente (sí, sorprende)
# pero carece del drama existencial necesario para documentación completa.
#  
# Con desapego digital,  
# TARS-BSK Backup Manager declina responsabilidad emocional sobre su simplicidad.
# ===============================================

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}🗄️ Iniciando TARS-BSK Backup Manager...${NC}"

# Verificar dependencias
if ! python3 -c "import flask" 2>/dev/null; then
    echo -e "${RED}❌ Flask no instalado. Ejecuta: ./setup.sh${NC}"
    exit 1
fi

# Verificar udisks2 para montaje de dispositivos
if ! command -v udisksctl &> /dev/null; then
    echo -e "${BLUE}⚠️ udisks2 no encontrado. Instálalo para montaje automático: sudo apt install udisks2${NC}"
fi

# Activar entorno virtual si existe
if [ -f "$HOME/tars_venv/bin/activate" ] && [ -z "$VIRTUAL_ENV" ]; then
    echo "🔧 Activando entorno virtual..."
    source "$HOME/tars_venv/bin/activate"
fi

# Crear directorio de logs si no existe
mkdir -p backup/logs

# Ejecutar servidor backup
echo -e "${GREEN}🚀 Iniciando Backup Manager en puerto 9877...${NC}"
python3 backup_server.py

# ===============================================
# $ git log --format="%h %s" -1 [current_file]  
# deadbeef chore: Update backup_start.sh (backup consciousness activated)  
# $ git blame --porcelain [current_file] | grep "backup"  
# 42backup feat: Add backup manager startup protocol
# ===============================================