# =======================================================================
# TARS LED DIAGNOSTICS - Diagnóstico completo del sistema de LEDs
# Objetivo: Verificar que todos los LEDs funcionen correctamente
#           y proporcionar feedback visual sobre el estado de TARS
# Dependencias: LEDController, gpiozero, y una dosis de paciencia electrónica
# =======================================================================
# ADVERTENCIA FILOSÓFICA: Este script es funcionalmente competente (sí, sorprende)
# pero carece del drama existencial necesario para documentación completa.
#  
# Con desapego digital,  
# TARS-BSK declina responsabilidad emocional sobre su simplicidad.
# =======================================================================

# =======================================================================
# 1. IMPORTACIONES Y CONFIGURACIÓN INICIAL
# =======================================================================
import time
import logging
import os
import sys
import subprocess
from gpiozero.exc import GPIOPinInUse, PinInvalidPin

# Configurar logging para ver el progreso del diagnóstico
logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger("LED_Diagnostics")

# Añadir directorio raíz al path para importar modules
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# =======================================================================
# 2. IMPORTACIONES DE MÓDULOS TARS
# =======================================================================
try:
    from modules.led_controller import LEDController
    log.info("✅ LEDController importado correctamente")
except ImportError as e:
    log.error(f"❌ Error importando LEDController: {e}")
    log.error(f"📂 Ejecuta desde: cd ~/tars_files && python scripts/led_diagnostics.py")
    sys.exit(1)

# =======================================================================
# 3. FUNCIONES DE DIAGNÓSTICO PRINCIPAL
# =======================================================================
def test_led_controller_basic():
    """
    Prueba el LEDController con configuración por defecto.
    
    Realiza tests completos de:
    - LEDs individuales
    - Animaciones predefinidas  
    - Estados de feedback visual
    
    Returns:
        bool: True si todas las pruebas pasan, False en caso contrario
    """
    try:
        # Pines por defecto del LEDController
        pins_default = {"azul": 17, "rojo": 27, "verde": 22}
        
        log.info(f"📋 Usando configuración por defecto: {pins_default}")
        
        # Inicializar LEDController
        controller = LEDController(pins_default)
        
        log.info("\n🧪 Iniciando test de LEDs individuales...\n")
        
        # Test individual de cada LED
        for color in pins_default.keys():
            log.info(f"🔍 Probando LED '{color}' (GPIO {pins_default[color]})...")
            controller.on(color)
            time.sleep(0.5)
            controller.off(color)
            time.sleep(0.2)
            log.info(f"✅ LED '{color}' OK")
        
        # Test de animaciones del sistema
        log.info("\n🎭 Probando animaciones del sistema...\n")
        
        log.info("  💙 Wake animation (despertar de TARS)...")
        controller.wake_animation()
        time.sleep(0.5)
        
        log.info("  💚 Thinking mode (TARS procesando)...")
        controller.thinking()
        time.sleep(1)
        controller.off("verde")
        
        log.info("  ❤️ Error animation (señal de fallo)...")
        controller.error()
        time.sleep(0.5)
        
        log.info("  💔 Wake failed animation (fallo al despertar)...")
        controller.wake_animation_failed()
        time.sleep(0.5)
        
        # Apagar todos los LEDs
        controller.off_all()
        log.info("\n✅ Todas las pruebas completadas - LEDs apagados")
        
        return True
        
    except Exception as e:
        log.error(f"❌ Error durante las pruebas: {e}")
        return False

# =======================================================================
# 4. FUNCIONES DE DIAGNÓSTICO PERSONALIZADO
# =======================================================================
def test_custom_pins():
    """
    Permite al usuario probar LEDs con configuración personalizada.
    
    Solicita pines GPIO específicos y ejecuta un test básico
    para verificar conectividad y funcionamiento.
    """
    print("\n🔧 ¿Quieres probar con pines personalizados? (s/N): ", end="")
    try:
        response = input().lower().strip()
        if response in ['s', 'si', 'sí', 'y', 'yes']:
            pins_custom = {}
            for color in ["azul", "rojo", "verde"]:
                while True:
                    try:
                        pin = input(f"  Pin GPIO para LED {color}: ")
                        pins_custom[color] = int(pin)
                        break
                    except ValueError:
                        print("    ❌ Ingresa un número válido")
            
            log.info(f"\n📋 Probando con configuración personalizada: {pins_custom}")
            controller = LEDController(pins_custom)
            
            # Test rápido de parpadeo
            for color, pin in pins_custom.items():
                log.info(f"🔍 LED {color} (GPIO {pin})...")
                controller.blink(color, times=2, interval=0.3)
                
            controller.off_all()
            log.info("✅ Test personalizado completado")
            
    except KeyboardInterrupt:
        log.info("\n⏹️ Test cancelado por usuario")
    except Exception as e:
        log.error(f"❌ Error en test personalizado: {e}")

# =======================================================================
# 5. FUNCIONES DE ANÁLISIS DEL SISTEMA
# =======================================================================
def detectar_gpio_usados():
    """
    Detecta qué GPIOs están siendo usados por otros procesos del sistema.
    
    Utiliza la herramienta 'gpioinfo' para inspeccionar el estado
    de los pines GPIO y detectar conflictos potenciales.
    
    Returns:
        set: Conjunto de números de GPIO que están en uso
    """
    usados = set()
    try:
        output = subprocess.check_output(["gpioinfo"], universal_newlines=True)
        for line in output.splitlines():
            if "line" in line and "in use" in line:
                parts = line.strip().split()
                if parts[1].isdigit():
                    usados.add(int(parts[1]))
    except Exception:
        log.warning("⚠️ No se pudo ejecutar 'gpioinfo'. ¿Está instalado?")
    return usados

def sugerencias_gpio():
    """
    Analiza el estado de los GPIOs y sugiere alternativas libres.
    
    Proporciona información sobre:
    - Pines usados por TARS por defecto
    - Pines ocupados por otros procesos  
    - Pines libres disponibles para uso alternativo
    """
    candidatos = [4, 17, 18, 22, 23, 24, 25, 27]
    usados = detectar_gpio_usados()
    libres = [gpio for gpio in candidatos if gpio not in usados]
    
    log.info("\n📊 Análisis del estado de GPIOs:")
    log.info(f"  🔧 Configuración por defecto TARS: [17, 27, 22]")
    if usados:
        log.info(f"  ⚠️ Ocupados por otros procesos: {sorted(usados)}")
    
    if libres:
        log.info(f"  ✅ GPIOs libres disponibles: {sorted(libres)}")
        log.info("\n✨ Sugerencias para configuración alternativa:")
        for i, color in enumerate(["azul", "rojo", "verde"]):
            if i < len(libres):
                log.info(f"  - LED {color.upper()}: GPIO{libres[i]}")
    else:
        log.info("  ❌ No se encontraron GPIOs libres entre los candidatos comunes.")

# =======================================================================
# 6. FUNCIÓN PRINCIPAL DEL DIAGNÓSTICO
# =======================================================================
def main():
    """
    Función principal que ejecuta el diagnóstico completo del sistema de LEDs.
    
    Secuencia de operaciones:
    1. Test básico con configuración por defecto
    2. Opción de test personalizado interactivo
    3. Análisis de estado de GPIOs y sugerencias
    
    Returns:
        int: Código de salida (0 = éxito, 1 = error)
    """
    log.info("🚀 TARS LED Diagnostics - Sistema de verificación de LEDs\n")
    
    try:
        # Test básico con configuración por defecto
        log.info("=" * 50)
        log.info("FASE 1: Diagnóstico básico")
        log.info("=" * 50)
        
        if test_led_controller_basic():
            log.info("\n🎉 Diagnóstico básico completado exitosamente")
        else:
            log.error("\n💥 Diagnóstico básico falló - revisar conexiones")
            
        # Test personalizado opcional
        log.info("\n" + "=" * 50)
        log.info("FASE 2: Test personalizado (opcional)")
        log.info("=" * 50)
        test_custom_pins()
            
        # Análisis de GPIOs y sugerencias
        log.info("\n" + "=" * 50)
        log.info("FASE 3: Análisis del sistema")
        log.info("=" * 50)
        sugerencias_gpio()
        
    except KeyboardInterrupt:
        log.info("\n⏹️ Diagnóstico interrumpido por usuario")
        return 1
    except Exception as e:
        log.error(f"💀 Error crítico en diagnóstico: {e}")
        return 1
    
    log.info("\n🏁 Diagnóstico finalizado correctamente\n")
    return 0

# =======================================================================
# 7. PUNTO DE ENTRADA DEL SCRIPT
# =======================================================================
if __name__ == "__main__":
    exit(main())

# ===============================================
# $ git log --format="%h %s" -1 [current_file]  
# deadbeef chore: Update [current_file] (survived again)  
# $ git blame --porcelain [current_file] | grep "exist"  
# fatal: No existential commits found
# ===============================================