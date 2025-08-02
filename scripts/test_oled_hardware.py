#!/usr/bin/env python3
# ===============================================
# TARS OLED Hardware Test - SSH1106 Diagnosis
# "Porque 'trust but verify' también aplica al hardware"
# 
# MISIÓN: Obligar al SSH1106 a demostrar que está vivo (y que trabaja para ti).
# MÉTODO: Tests progresivos desde "¿respondes?" hasta "¿puedes ser útil?".
# 
# CONTEXTO:
# Script de diagnóstico para cuando sospechas que:
# - Los cables están bien pero la pantalla tiene amnesia
# - El I²C funciona pero el SSH1106 está de mal humor
# - Todo parece correcto pero la pantalla prefiere el silencio pasivo-agresivo
# - Necesitas pruebas antes de culpar al código principal
#
# TESTS INCLUIDOS:
# 1. Importación de librerías (porque lo básico falla más de lo esperado)
# 2. Escaneo I²C (para encontrar quién está vivo en el bus)
# 3. Conexión SSH1106 (momento de la verdad)
# 4. Tests visuales progresivos (desde texto hasta animaciones)
# 5. Simulación de estados TARS (preview del mundo real)
#
# USO: python3 scripts/test_oled_hardware.py
# ===============================================

# scripts/test_oled_hardware.py
# Test básico de hardware OLED SSH1106

# =======================================================================
# 1. IMPORTACIONES Y CONFIGURACIÓN DE PATH
# =======================================================================
import time
import sys
from pathlib import Path

# Añadir el directorio padre al path para importar módulos
sys.path.append(str(Path(__file__).resolve().parent.parent))

# =======================================================================
# 2. FUNCIÓN PRINCIPAL DE DIAGNÓSTICO
# =======================================================================
def test_oled_hardware():
    """
    Test básico de la pantalla OLED SSH1106
    
    Ejecuta una batería completa de tests para verificar:
    - Disponibilidad de librerías
    - Conectividad I²C
    - Funcionalidad básica del display
    - Capacidades de renderizado
    """
    
    print("🔍 TARS-BSK OLED Hardware Test")
    print("=" * 40)
    
    try:
        # =======================================================================
        # 2.1 TEST DE IMPORTACIONES
        # =======================================================================
        print("📦 Importando librerías...")
        import board
        import busio
        import adafruit_ssd1306
        from PIL import Image, ImageDraw
        print("✅ Librerías importadas correctamente")
        
        # =======================================================================
        # 2.2 INICIALIZACIÓN I²C
        # =======================================================================
        print("🔌 Inicializando I2C...")
        i2c = busio.I2C(board.SCL, board.SDA)
        print("✅ I2C inicializado")
        
        # =======================================================================
        # 2.3 ESCANEO DE DISPOSITIVOS I²C
        # =======================================================================
        print("🔍 Escaneando dispositivos I2C...")
        devices = []
        for addr in range(0x03, 0x78):
            try:
                i2c.try_lock()
                i2c.writeto(addr, b'')
                devices.append(f"0x{addr:02X}")
            except:
                pass
            finally:
                i2c.unlock()
        
        if devices:
            print(f"✅ Dispositivos encontrados: {', '.join(devices)}")
        else:
            print("⚠️ No se encontraron dispositivos I2C")
            return False
        
        # =======================================================================
        # 2.4 CONEXIÓN A LA OLED
        # =======================================================================
        print("🖥️ Conectando a OLED en 0x3C...")
        display = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3C)
        print("✅ OLED conectada correctamente")
        
        # =======================================================================
        # 2.5 BATERÍA DE TESTS VISUALES
        # =======================================================================
        print("🎨 Ejecutando test visual...")
        
        # Limpiar pantalla inicial
        display.fill(0)
        display.show()
        time.sleep(1)
        
        # Crear canvas para dibujo
        image = Image.new('1', (128, 64))
        draw = ImageDraw.Draw(image)
        
        # =======================================================================
        # 2.5.1 TEST 1: TEXTO BÁSICO
        # =======================================================================
        print("  📝 Test 1: Texto básico")
        draw.rectangle((0, 0, 127, 63), outline=0, fill=0)
        draw.text((0, 0), "TARS-BSK v5.2.0", fill=255)
        draw.text((0, 16), "Hardware Test", fill=255)
        draw.text((0, 32), "OLED SSH1106", fill=255)
        draw.text((0, 48), time.strftime("%H:%M:%S"), fill=255)
        display.image(image)
        display.show()
        time.sleep(3)
        
        # =======================================================================
        # 2.5.2 TEST 2: FORMAS GEOMÉTRICAS
        # =======================================================================
        print("  🔲 Test 2: Formas geométricas")
        draw.rectangle((0, 0, 127, 63), outline=0, fill=0)
        draw.rectangle((10, 10, 50, 30), outline=255, fill=0)
        draw.rectangle((60, 10, 100, 30), outline=255, fill=255)
        draw.rectangle((10, 40, 50, 60), outline=255, fill=0)
        draw.rectangle((60, 40, 100, 60), outline=255, fill=255)
        display.image(image)
        display.show()
        time.sleep(3)
        
        # =======================================================================
        # 2.5.3 TEST 3: ANIMACIÓN SIMPLE
        # =======================================================================
        print("  🎬 Test 3: Animación simple")
        for i in range(10):
            draw.rectangle((0, 0, 127, 63), outline=0, fill=0)
            x = i * 12
            draw.text((x, 20), "●", fill=255)
            draw.text((0, 0), f"Frame: {i+1}/10", fill=255)
            display.image(image)
            display.show()
            time.sleep(0.3)
        
        # =======================================================================
        # 2.5.4 TEST 4: SIMULACIÓN DE ESTADOS TARS
        # =======================================================================
        print("  🤖 Test 4: Estados TARS")
        states = [
            ("● BOOT", "Initializing...", "", "Please wait"),
            ("● STANDBY", "Ready", f"CPU: 45.2°C", time.strftime("%H:%M")),
            ("● LISTENING", "VOSK Active", "", "Waiting..."),
            ("● PROCESSING", "LLM thinking...", "Tokens: 42", "Time: 5s"),
            ("● SPEAKING", "TTS Active", "", time.strftime("%H:%M"))
        ]
        
        for state_data in states:
            draw.rectangle((0, 0, 127, 63), outline=0, fill=0)
            for i, line in enumerate(state_data):
                if line:
                    draw.text((0, i * 16), line, fill=255)
            display.image(image)
            display.show()
            time.sleep(2)
        
        # =======================================================================
        # 2.6 LIMPIEZA FINAL
        # =======================================================================
        print("🧹 Limpiando pantalla...")
        display.fill(0)
        display.show()
        
        print("✅ ¡Test completado exitosamente!")
        print("🎯 La OLED SSH1106 está funcionando correctamente")
        return True
        
    # =======================================================================
    # 3. MANEJO DE ERRORES ESPECÍFICOS
    # =======================================================================
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("💡 Instala las dependencias:")
        print("   pip install adafruit-circuitpython-ssd1306 pillow")
        return False
        
    except Exception as e:
        print(f"❌ Error de hardware: {e}")
        print("🔧 Verifica las conexiones:")
        print("   VCC → Pin 1 (3.3V)")
        print("   GND → Pin 6 (GND)")
        print("   SDA → Pin 3 (GPIO2)")
        print("   SCL → Pin 5 (GPIO3)")
        return False

# =======================================================================
# 4. EJECUCIÓN PRINCIPAL
# =======================================================================
if __name__ == "__main__":
    success = test_oled_hardware()
    sys.exit(0 if success else 1)

# ===============================================
# ESTADO: FUNCIONANDO (con reservas y algo de chantaje emocional)
# COBERTURA: Desde “¿estás vivo?” hasta “dibuja algo útil sin dramas”
# VEREDICTO: Si pasa estos tests, el hardware está listo… o al menos ya no tiene excusas.
#
# ANÁLISIS POST-PRUEBA:
# » Importaciones: Porque a veces el fallo eres tú (faltan librerías).
# » I²C Scan: Detecta quién realmente vive en el bus (y quién finge).
# » Conexión: Pone al SSH1106 contra la pared: ¿respondes o no?
# » Rendering: Desde garabatos hasta animaciones (lo que soporte sin llorar).
# » Estados TARS: Prueba de fuego: ¿sirves para el mundo real?
#
# USO RECOMENDADO:
# - Después de cada cirugía al hardware.
# - Cuando sospeches que el display te odia.
# - Antes de culpar al código (o a ti mismo).
# - Para tener pruebas visuales de que “todo está bien” (mentira controlada).
#
# FILOSOFÍA DEL DIAGNÓSTICO:
# "Si el hardware falla, que al menos lo haga de forma documentable."
#
# ===============================================
#        THIS IS THE TESTING WAY
#    (Donde los píxeles aprenden a respetar órdenes)
# ===============================================
