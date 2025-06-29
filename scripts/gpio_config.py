# ===============================================
# ADVERTENCIA FILOSÓFICA: Este script es funcionalmente competente (sí, sorprende)
# pero carece del drama existencial necesario para documentación completa.
#  
# Con desapego digital,  
# TARS-BSK declina responsabilidad emocional sobre su simplicidad.
# ===============================================

from gpiozero import Device
from gpiozero.pins.lgpio import LGPIOFactory

# Usar LGPIO como backend
Device.pin_factory = LGPIOFactory()

# Pines de LEDs definidos como constantes
GPIO_PINS = {
    'led_status': 17,    # Azul
    'led_activity': 27,  # Rojo
    'led_alert': 22      # Verde
}

# Prueba básica de los LEDs
def test_leds():
    from gpiozero import LED
    from time import sleep

    print(f"Backend activo: {Device.pin_factory.__class__.__name__}")
    try:
        for nombre, pin in GPIO_PINS.items():
            led = LED(pin)
            print(f"🔵 Prueba LED {nombre} (GPIO{pin})")
            led.on()
            sleep(0.3)
            led.off()
            sleep(0.3)
        print("✅ Prueba completa de LEDs")
    except Exception as e:
        print(f"❌ Error en prueba de LEDs: {e}")

# Ejecutar solo si se llama directamente
if __name__ == "__main__":
    test_leds()

# ===============================================
# $ git log --format="%h %s" -1 [current_file]  
# deadbeef chore: Update [current_file] (survived again)  
# $ git blame --porcelain [current_file] | grep "exist"  
# fatal: No existential commits found
# ===============================================