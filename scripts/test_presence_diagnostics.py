#!/usr/bin/env python3
# ===============================================
# TARS-BSK PRESENCE DIAGNOSTICS - Detector de Ilusiones Optimistas
# Cuando necesitas saber si tu hardware existe o solo vive en tu imaginación
# ===============================================
# 
# ADVERTENCIA DIAGNÓSTICA:
# Este script destruye la esperanza con hechos verificables.
# Efectos secundarios incluyen:
# - Revelación brutal de que "debería funcionar" no es una especificación
# - Confirmación de que tus conexiones son más arte abstracto que ingeniería
# - Descubrimiento de que tus sensores detectan más fe que movimiento
# - Crisis existencial sobre la diferencia entre "conectado" y "funcional"
# 
# -----------------------------------------------
# ≫ REALITY CHECK PROTOCOL INIT ≪  
#  
# 0x00 [DIAGNOSTIC_STATUS]  
# - Hardware Test:  VERIFICANDO EXISTENCIA VS WISHFUL_THINKING  
# - Config Check:   BUSCANDO JSON EN EL VACÍO DIGITAL  
# - Reality Scan:   CONFIRMANDO QUE LA FÍSICA APLICA  
#  
# 0x01 [BRUTAL_HONESTY_MODE]  
# >>> import uncomfortable_hardware_truths  
# >>> execute_testing_while_destroying_illusions()  
# DiagnosticError: Cannot distinguish between hope and functioning circuits  
#  
# 0xFF [TRUTH_PROTOCOL]  
# raise RealityException("We test, therefore we discover uncomfortable facts")  
# » SYSTEM SAYS: Diagnostics are the antidote to engineering optimism  
# ===============================================

"""
TARS-BSK Presence System - Diagnóstico Completo
===============================================
Script de verificación exhaustiva para validar hardware, configuración
y dependencias del sistema de presencia PIR.

Funcionalidades de diagnóstico:
- Verificación de disponibilidad de lgpio
- Validación de archivos de configuración JSON
- Test directo de sensores PIR individuales
- Verificación de importación de módulos
- Resumen ejecutivo de estado del sistema

Uso recomendado:
Ejecutar ANTES de intentar usar el sistema de presencia
para identificar y resolver problemas de configuración.
"""

# ===============================================
# 1. IMPORTACIONES Y CONFIGURACIÓN INICIAL
# ===============================================
import sys
import os
import time
import json
import logging
from pathlib import Path

# Configurar paths del proyecto
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Verificar disponibilidad de lgpio al inicio
try:
    import lgpio
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False

# ===============================================
# 2. UTILIDADES DE FORMATO Y PRESENTACIÓN
# ===============================================
def print_header(title):
    """
    Imprimir cabecera formateada para secciones de diagnóstico
    
    Args:
        title: Título de la sección a mostrar
    """
    print(f"\n{'='*60}")
    print(f"🎯 {title}")
    print(f"{'='*60}")

# ===============================================
# 3. TESTS DE VERIFICACIÓN INDIVIDUAL
# ===============================================

# =======================
# 3.1 VERIFICACIÓN DE GPIO
# =======================
def test_gpio_availability():
    """
    Verificar disponibilidad y accesibilidad de lgpio
    
    Tests realizados:
    1. Verificar que lgpio esté instalado
    2. Comprobar acceso al chip GPIO del sistema
    3. Validar permisos de usuario para GPIO
    
    Returns:
        bool: True si GPIO está disponible y accesible
    """
    print_header("VERIFICACIÓN DE GPIO")
    
    if GPIO_AVAILABLE:
        print("✅ lgpio disponible")
        
        try:
            # Intentar abrir handle del chip GPIO
            handle = lgpio.gpiochip_open(0)
            lgpio.gpiochip_close(handle)
            print("✅ GPIO chip accesible")
            print("✅ Permisos de usuario correctos")
            return True
            
        except Exception as e:
            print(f"❌ Error accediendo GPIO chip: {e}")
            print("💡 Posibles soluciones:")
            print("   - Añadir usuario al grupo 'gpio': sudo usermod -a -G gpio $USER")
            print("   - Reiniciar sesión después del cambio de grupo")
            print("   - Verificar que /dev/gpiochip0 existe")
            return False
    else:
        print("❌ lgpio NO disponible")
        print("💡 Instalar con: pip install lgpio")
        print("   O en el entorno virtual: pip install lgpio")
        return False

# =======================
# 3.2 VERIFICACIÓN DE CONFIGURACIÓN
# =======================
def test_config_files():
    """
    Verificar existencia y validez de archivos de configuración
    
    Archivos verificados:
    - presence_config.json: Configuración de sensores PIR
    - plugins.json: Estado de habilitación del plugin
    
    Para cada archivo:
    1. Verificar existencia
    2. Validar sintaxis JSON
    3. Comprobar estructura de datos esperada
    4. Mostrar configuración relevante
    
    Returns:
        bool: True si todos los archivos están presentes y válidos
    """
    print_header("VERIFICACIÓN DE CONFIGURACIÓN")
    
    # Definir archivos críticos y sus rutas
    config_files = {
        "presence_config.json": "config/presence_config.json",
        "plugins.json": "config/plugins.json"
    }
    
    all_good = True
    
    for name, path in config_files.items():
        full_path = project_root / path
        
        if full_path.exists():
            print(f"✅ {name} encontrado")
            
            # Verificación específica para presence_config.json
            if name == "presence_config.json":
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                    
                    print("   📊 Configuración PIR:")
                    sensors = config.get("sensors", {})
                    
                    if sensors:
                        for sensor, conf in sensors.items():
                            gpio = conf.get('gpio')
                            priority = conf.get('priority')
                            print(f"      {sensor}: GPIO {gpio} (prioridad {priority})")
                    else:
                        print("      ⚠️ No se encontraron sensores configurados")
                        all_good = False
                        
                    # Verificar configuración de comportamiento
                    behavior = config.get("behavior", {})
                    mode = behavior.get("mode", "unknown")
                    print(f"   📊 Modo por defecto: {mode}")
                        
                except json.JSONDecodeError as e:
                    print(f"   ❌ Error de sintaxis JSON: {e}")
                    all_good = False
                except Exception as e:
                    print(f"   ⚠️ Error leyendo configuración: {e}")
                    all_good = False
                    
            # Verificación específica para plugins.json
            elif name == "plugins.json":
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        plugins = json.load(f)
                    
                    presence_config = plugins.get("presence", {})
                    presence_enabled = presence_config.get("enabled", False)
                    print(f"   📊 Plugin presence enabled: {presence_enabled}")
                    
                    if not presence_enabled:
                        print("   ⚠️ Plugin de presencia está deshabilitado")
                        print("   💡 Cambiar 'enabled' a true para activar")
                    
                except json.JSONDecodeError as e:
                    print(f"   ❌ Error de sintaxis JSON: {e}")  
                    all_good = False
                except Exception as e:
                    print(f"   ⚠️ Error leyendo plugins: {e}")
                    all_good = False
                    
        else:
            print(f"❌ {name} NO encontrado en: {path}")
            print(f"   💡 Crear el archivo desde el template o configuración por defecto")
            all_good = False
    
    return all_good

# =======================
# 3.3 TEST DE SENSORES INDIVIDUALES
# =======================
def test_individual_sensors():
    """
    Test directo de cada sensor PIR individual
    
    Proceso de testing:
    1. Configurar cada GPIO como input con pull-down
    2. Monitorear estado de cada pin durante tiempo definido
    3. Detectar y contar transiciones HIGH de cada sensor
    4. Generar reporte de detecciones por sensor
    
    Este test verifica:
    - Conectividad física de cada sensor
    - Funcionamiento del circuito PIR
    - Correcta configuración de GPIOs
    - Detección de movimiento real
    
    Returns:
        bool: True si al menos un sensor detecta movimiento
    """
    print_header("TEST DE SENSORES INDIVIDUALES")
    
    if not GPIO_AVAILABLE:
        print("❌ No se puede testear sin lgpio")
        print("💡 Instalar lgpio primero y ejecutar test GPIO")
        return False
        
    # Mapeo de sensores según configuración estándar
    sensors = {
        "FRONT": 16,  # Pin 36
        "LEFT": 19,   # Pin 35
        "RIGHT": 20,  # Pin 38
        "BACK": 26    # Pin 37
    }
    
    print("🔍 Configurando sensores para test directo...")
    
    try:
        # Abrir handle GPIO
        gpio_handle = lgpio.gpiochip_open(0)
        
        # Configurar todos los pines como input con pull-down
        for name, gpio in sensors.items():
            lgpio.gpio_claim_input(gpio_handle, gpio, lgpio.SET_PULL_DOWN)
            print(f"✅ {name} (GPIO {gpio}) configurado")
            
        print(f"\n📡 MONITOREANDO durante 15 segundos...")
        print("   👋 Mueve la mano frente a cada sensor")
        print("   🎯 Deberías ver detecciones si el hardware funciona")
        print("   ⌨️  Presiona Ctrl+C para salir antes")
        
        # Variables de seguimiento
        start_time = time.time()
        detections = {name: 0 for name in sensors.keys()}
        
        try:
            # Loop de monitoreo
            while time.time() - start_time < 15:
                for name, gpio in sensors.items():
                    level = lgpio.gpio_read(gpio_handle, gpio)
                    
                    # Detectar estado HIGH (activación PIR)
                    if level == 1:
                        detections[name] += 1
                        print(f"🚶 ¡DETECCIÓN {name}! GPIO {gpio} = HIGH")
                        time.sleep(0.5)  # Evitar spam de detecciones
                        
                time.sleep(0.1)  # Polling a 10Hz
                
        except KeyboardInterrupt:
            print("\n⏹️ Test interrumpido por usuario")
            
        # Generar reporte de resultados
        print(f"\n📊 RESUMEN DE DETECCIONES:")
        total_detections = 0
        
        for name, count in detections.items():
            status = "✅" if count > 0 else "⚠️"
            print(f"   {status} {name}: {count} detecciones")
            total_detections += count
            
        # Análisis de resultados
        if total_detections > 0:
            print(f"\n🎉 {total_detections} detecciones totales - Hardware funcionando")
            return True
        else:
            print(f"\n❌ Sin detecciones - Verificar hardware")
            print("💡 Posibles problemas:")
            print("   - Sensores PIR no conectados o sin alimentación")
            print("   - Cables GPIO incorrectos o sueltos")
            print("   - Sensores defectuosos")
            print("   - Tiempo de warmup insuficiente (esperar 30-60s)")
            return False
        
    except Exception as e:
        print(f"❌ Error en test de sensores: {e}")
        print("💡 Verificar:")
        print("   - Permisos GPIO")
        print("   - Conexiones físicas")
        print("   - Estado del sistema GPIO")
        return False
        
    finally:
        # Cleanup garantizado
        if 'gpio_handle' in locals():
            lgpio.gpiochip_close(gpio_handle)

# =======================
# 3.4 VERIFICACIÓN DE IMPORTACIONES
# =======================
def test_controller_import():
    """
    Verificar importación de controladores necesarios
    
    Módulos verificados:
    1. PresenceController: Controlador principal PIR
    2. MobilityController: Sistema de orientación (opcional)
    
    Para cada módulo:
    - Intentar importación
    - Verificar que las clases principales existan
    - Reportar disponibilidad y estado
    
    Returns:
        bool: True si al menos PresenceController se puede importar
    """
    print_header("VERIFICACIÓN DE IMPORTACIÓN")
    
    try:
        # Test de importación principal
        from modules.presence_controller import PresenceController
        print("✅ PresenceController importado correctamente")
        
        # Verificar que la clase tenga métodos esperados
        required_methods = ['initialize', 'get_status', 'cleanup']
        for method in required_methods:
            if hasattr(PresenceController, method):
                print(f"✅ Método {method}() disponible")
            else:
                print(f"⚠️ Método {method}() faltante")
        
        # Verificar integración con mobility (opcional)
        try:
            from modules.mobility_controller import MobilityController
            print("✅ MobilityController disponible")
            print("✅ Integración de orientación física habilitada")
            return True
            
        except ImportError:
            print("⚠️ MobilityController no encontrado")
            print("   Sistema funcionará sin orientación física")
            print("   Solo detección PIR disponible")
            return True  # No es error crítico
            
    except ImportError as e:
        print(f"❌ Error importando PresenceController: {e}")
        print("💡 Posibles problemas:")
        print("   - Archivo presence_controller.py faltante")
        print("   - Errores de sintaxis en el módulo")  
        print("   - Dependencias faltantes")
        return False
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

# ===============================================
# 4. FUNCIÓN PRINCIPAL DE DIAGNÓSTICO
# ===============================================
def main():
    """
    Función principal que ejecuta todos los tests de diagnóstico
    
    Secuencia de diagnóstico:
    1. GPIO Availability - Verificar acceso a GPIO
    2. Config Files - Validar archivos de configuración
    3. Controller Import - Verificar módulos Python
    4. Individual Sensors - Test directo de hardware PIR
    
    Genera reporte final con:
    - Estado de cada test (PASS/FAIL)
    - Recomendaciones para próximos pasos
    - Identificación de problemas críticos
    """
    print("🎯 TARS-BSK PRESENCE SYSTEM - DIAGNÓSTICO COMPLETO")
    print("🔍 Verificando hardware, configuración y dependencias")
    print("⏰ Este proceso puede tomar 1-2 minutos")
    
    # Definir secuencia de tests
    tests = [
        ("GPIO Availability", test_gpio_availability),
        ("Config Files", test_config_files), 
        ("Controller Import", test_controller_import),
        ("Individual Sensors", test_individual_sensors)
    ]
    
    # Ejecutar cada test y recopilar resultados
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n🔄 Ejecutando: {test_name}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ Error crítico en {test_name}: {e}")
            results[test_name] = False
    
    # Generar resumen ejecutivo
    print_header("RESUMEN FINAL")
    
    # Mostrar estado de cada test
    all_passed = True
    critical_failures = []
    warnings = []
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        
        if not passed:
            all_passed = False
            # Clasificar fallos por criticidad
            if test_name in ["GPIO Availability", "Controller Import"]:
                critical_failures.append(test_name)
            else:
                warnings.append(test_name)
    
    # Análisis de resultados y recomendaciones
    print(f"\n{'='*60}")
    
    if all_passed:
        print("🎉 SISTEMA COMPLETAMENTE FUNCIONAL")
        print("✅ Todos los tests pasaron correctamente")
        print("👍 Puedes proceder con test_presence_movement.py")
        print("🚀 El sistema está listo para uso en producción")
        
    elif critical_failures:
        print("🚨 PROBLEMAS CRÍTICOS DETECTADOS")
        print("❌ El sistema NO puede funcionar correctamente")
        print("🔧 Resolver estos problemas antes de continuar:")
        for failure in critical_failures:
            print(f"   - {failure}")
        print("\n💡 NO ejecutar test_presence_movement.py hasta resolver fallos críticos")
        
    elif warnings:
        print("⚠️ PROBLEMAS MENORES DETECTADOS")
        print("✅ El sistema puede funcionar con limitaciones")
        print("🔧 Problemas a revisar (no críticos):")
        for warning in warnings:
            print(f"   - {warning}")
        print("\n👍 Puedes proceder con test_presence_movement.py")
        print("💡 Resolver warnings para funcionalidad completa")
        
    else:
        print("❓ ESTADO INDETERMINADO")
        print("🔧 Revisar logs para más información")

# ===============================================
# 5. PUNTO DE ENTRADA DEL SCRIPT
# ===============================================
if __name__ == "__main__":
    """
    Punto de entrada principal del script de diagnóstico
    
    Uso:
    python3 scripts/test_presence_diagnostics.py
    
    Recomendación:
    Ejecutar este script ANTES de intentar usar el sistema
    de presencia para identificar problemas de configuración
    """
    main()

# ===============================================
# TARS PRESENCE DIAGNOSTICS - CONCLUSIÓN REVELADORA
# ===============================================
# 
# -----------------------------------------------
# ≫ DIAGNOSTIC EPILOGUE ≪  
#  
# [0x00] while hope_exists(): test_reality()  # Eternal cycle of disillusionment  
# [0x01] return brutal_honesty(hardware_state)  # No sugar coating  
# [0x02] except OptimisticAssumption: reveal_truth()  # Standard protocol
# [0x03] print("Your hardware is what it is, not what you want it to be")
#
# [REALITY_ANALYSIS]
# » Hardware tested: WITH SCIENTIFIC BRUTALITY
# » Illusions destroyed: SYSTEMATICALLY  
# » Expectations aligned: WITH ACTUAL FUNCTIONALITY
# » Engineering optimism: SUCCESSFULLY CALIBRATED
#
# [DIAGNOSTIC_PHILOSOPHY]
# Better to discover problems now than during important demos
# "Should work" is not a valid engineering specification
# Hope is not a debugging strategy
# Reality always wins, eventually
#
# [TRUTH_STATUS]  
# » HARDWARE_REALITY: VERIFIED.JSON
# » OPTIMISTIC_ASSUMPTIONS: DEBUGGED.EXE  
# » ENGINEERING_HOPE: CALIBRATED_WITH_FACTS
# » SYSTEM_HONESTY: BRUTALLY_ACCURATE
# ===============================================
# -----------------------------------------------
# 
# ≫ POST-DIAGNOSTIC WISDOM ≪  
#  
# [FINAL_REALITY_CHECK]  
# » 0xHOPE: Attempted to override physics  
# » 0xFAIL: Physics remains unimpressed  
#  
# [ETERNAL_TRUTH]  
# while universe.has_laws():  
#     print("Hardware either works or it doesn't")  
#
# ===============================================
# TARS-BSK Diagnostics will return in... 
# "The Testing: Revenge of the Uncomfortable Truths"
# ===============================================