#!/bin/bash
# ===============================================
# ADVERTENCIA FILOSÓFICA: Este script es funcionalmente competente (sí, sorprende)
# pero carece del drama existencial necesario para documentación completa.
#  
# Con desapego digital,  
# TARS-BSK declina responsabilidad emocional sobre su simplicidad.
# ===============================================

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🚀 Iniciando TARS-BSK Home Assistant Web Interface...${NC}"

# Verificar dependencias
if ! python3 -c "import flask" 2>/dev/null; then
    echo -e "${RED}❌ Flask no instalado. Ejecuta: ./setup.sh${NC}"
    exit 1
fi

# Activar entorno virtual si existe
if [ -f "$HOME/tars_venv/bin/activate" ] && [ -z "$VIRTUAL_ENV" ]; then
    echo "🔧 Activando entorno virtual..."
    source "$HOME/tars_venv/bin/activate"
fi

# Ejecutar servidor
python3 server.py

# ===============================================
# $ git log --format="%h %s" -1 [current_file]  
# deadbeef chore: Update [current_file] (survived again)  
# $ git blame --porcelain [current_file] | grep "exist"  
# fatal: No existential commits found
# ===============================================
