# ===============================================
# ADVERTENCIA FILOSÓFICA: Este módulo es funcionalmente competente (sí, sorprende)
# pero carece del drama existencial necesario para documentación completa.
#  
# Con desapego digital,  
# TARS-BSK declina responsabilidad emocional sobre su simplicidad.
# ===============================================

# LED CONTROLLER - Control de LEDs RGB como feedback visual

# ===============================================
# 1. IMPORTACIONES Y DEPENDENCIAS
# ===============================================
import time
import logging
from gpiozero import LED
from modules.gpio_backend import Device  


# ===============================================
# 2. CLASE CONTROLADORA DE LEDS
# ===============================================
class LEDController:
    """
    Gestiona el control de LEDs para proporcionar feedback visual
    sobre el estado y las acciones de TARS.
    """
    # =======================
    # 2.1 INICIALIZACIÓN
    # =======================
    def __init__(self, pins=None):
        self.logger = logging.getLogger("TARS.LED")
        pins = pins or {"azul": 17, "rojo": 27, "verde": 22}

        self.leds = {}
        for color, gpio in pins.items():
            try:
                self.leds[color] = LED(gpio)
                self.logger.info(f"✅ LED '{color}' inicializado en GPIO{gpio}")
            except Exception as e:
                self.logger.error(f"❌ Error al inicializar LED '{color}': {e}")

        self.off_all()

    # =======================
    # 2.2 OPERACIONES BÁSICAS
    # =======================
    def on(self, color):
        led = self.leds.get(color)
        if led:
            led.on()

    def off(self, color):
        led = self.leds.get(color)
        if led:
            led.off()

    def blink(self, color, times=3, interval=0.2):
        led = self.leds.get(color)
        if not led:
            return
        for _ in range(times):
            led.on()
            time.sleep(interval)
            led.off()
            time.sleep(interval)
            
    def off_all(self):
        for led in self.leds.values():
            led.off()

    # =======================
    # 2.3 CONTROL DE LEDS INDIVIDUALES
    # =======================
    def set_green(self, state: bool):
        """Enciende o apaga el LED verde manualmente."""
        led = self.leds.get("verde")
        if led:
            if state:
                led.on()
            else:
                led.off()

    def set_blue(self, state: bool):
        """Enciende o apaga el LED azul manualmente."""
        led = self.leds.get("azul")
        if led:
            if state:
                led.on()
            else:
                led.off()
                
    def set_red(self, state: bool):
        """Enciende o apaga el LED rojo manualmente (por ejemplo, para emociones)."""
        led = self.leds.get("rojo")
        if led:
            if state:
                led.on()
            else:
                led.off()

    # =======================
    # 2.4 ANIMACIONES Y FEEDBACK
    # =======================
    def wake_animation(self):
        self.blink("azul", times=3, interval=0.15)

    def wake_animation_failed(self):
        self.blink("rojo", times=3, interval=0.15)

    def thinking(self):
        self.on("verde")

    def error(self):
        self.blink("rojo", times=2, interval=0.3)

# ===============================================
# $ git log --format="%h %s" -1 [current_file]  
# deadbeef chore: Update [current_file] (survived again)  
# $ git blame --porcelain [current_file] | grep "exist"  
# fatal: No existential commits found
# ===============================================