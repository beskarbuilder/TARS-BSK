# ===============================================
# ADVERTENCIA FILOSÓFICA: Este script es funcionalmente competente (sí, sorprende)
# pero carece del drama existencial necesario para documentación completa.
#  
# Con desapego digital,  
# TARS-BSK declina responsabilidad emocional sobre su simplicidad.
# ===============================================

from gpiozero import Device
from gpiozero.pins.lgpio import LGPIOFactory
from gpiozero import LED
import time

Device.pin_factory = LGPIOFactory()
print("✅ LGPIO activado como backend GPIO")

# Pines a verificar (ajusta si están en uso)
GPIO_PINS = [17, 27, 22]

for pin in GPIO_PINS:
    try:
        led = LED(pin)
        print(f"🔴 LED GPIO{pin} encendido")
        led.on()
        time.sleep(0.5)
        led.off()
        print(f"⚫ LED GPIO{pin} apagado")
        time.sleep(0.3)
    except Exception as e:
        print(f"⚠️ Error en GPIO{pin}: {e}")

# ===============================================
# $ git log --format="%h %s" -1 [current_file]  
# deadbeef chore: Update [current_file] (survived again)  
# $ git blame --porcelain [current_file] | grep "exist"  
# fatal: No existential commits found
# ===============================================