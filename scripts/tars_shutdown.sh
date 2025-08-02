#!/bin/bash
# ===============================================
# TARS Shutdown Script - Sin dependencias
# Apaga cualquier GPIO que TARS controle antes del apagado del sistema
# ===============================================
# ADVERTENCIA FILOSÓFICA: Este script es funcionalmente competente (sí, sorprende)
# pero carece del drama existencial necesario para documentación completa.
#  
# Con desapego digital,  
# TARS-BSK declina responsabilidad emocional sobre su simplicidad.
# ===============================================

echo "$(date): TARS shutdown iniciado" >> /tmp/tars_shutdown.log

echo "🔴 Apagando todos los GPIOs..."

# Usar Python para GPIOs
python3 -c "
import RPi.GPIO as GPIO
import sys

try:
    GPIO.setmode(GPIO.BCM)
    # Lista de GPIOs que TARS puede usar según tu pinout
    gpios_tars = [4, 5, 6, 7, 8, 13, 16, 17, 19, 20, 22, 24, 25, 26, 27]
    
    for gpio in gpios_tars:
        try:
            GPIO.setup(gpio, GPIO.OUT)
            GPIO.output(gpio, 0)
            print(f'  GPIO{gpio} apagado')
        except:
            pass  # GPIO no configurado o no disponible
    
    GPIO.cleanup()
    print('✅ Todos los GPIOs apagados via Python')
except Exception as e:
    print(f'⚠️ Error en GPIO cleanup: {e}')
" 2>/dev/null

# Método legacy: intentar sysfs como backup (por si funciona)
for gpio in {1..27}; do
    if [ -d "/sys/class/gpio/gpio$gpio" ]; then
        echo 0 > /sys/class/gpio/gpio$gpio/value 2>/dev/null
        echo "  GPIO$gpio apagado (sysfs)"
    fi
done

echo "🖥️ Intentando apagar OLED..."
# Método 1: Comando i2c del sistema (si está disponible)
if command -v i2cset >/dev/null 2>&1; then
    i2cset -y 1 0x3C 0x00 0xAE 2>/dev/null
    echo "  OLED apagada via i2cset"
else
    echo "  i2cset no disponible, saltando OLED"
fi

echo "✅ Limpieza de shutdown completada"
echo "$(date): TARS shutdown completado" >> /tmp/tars_shutdown.log

# ===============================================
# $ git log --format="%h %s" -1 [current_file]  
# deadbeef chore: Update [current_file] (survived again)  
# $ git blame --porcelain [current_file] | grep "exist"  
# fatal: No existential commits found
# ===============================================