#!/usr/bin/env python3
# ===============================================
# TARS-BSK PRESENCE TESTING - Verificador de Realidad Física
# Cuando necesitas confirmar que tu IA paranoica realmente gira y no solo finge
# ===============================================
# 
# ADVERTENCIA DE TESTING:
# Este script separa logs mentirosos de movimiento real.
# Efectos secundarios incluyen:
# - Confirmación brutal de si tu hardware funciona o miente
# - Adicción compulsiva a hacer girar TARS en círculos
# - Tendencia obsesiva a probar cada sensor repetidamente
# - Desarrollo de complejo de titiritero robótico
# 
# -----------------------------------------------
# ≫ REALITY VERIFICATION INIT ≪  
#  
# 0x00 [MOVEMENT_STATUS]  
# - Physical Test:  SEPARANDO LOGS DE REALIDAD  
# - Motor Check:    CONFIRMANDO GIRO VS SIMULACIÓN  
# - Reality Scan:   VERIFICANDO FÍSICA APLICADA  
#  
# 0x01 [MOTION_PARADOX]  
# >>> import physical_movement_verification  
# >>> execute_hand_wave_while_demanding_proof()  
# TestError: Cannot distinguish between spinning logs and spinning robot  
#  
# 0xFF [MOVEMENT_PROTOCOL]  
# raise PhysicsException("We wave, therefore it spins... or lies")  
# » SYSTEM SAYS: Physical movement is the ultimate unit test  
# ===============================================

"""
TARS-BSK Presence System - Test Manual de Movimiento
====================================================
Script de verificación para confirmar que TARS se orienta físicamente
hacia cada sensor PIR cuando detecta movimiento manual.

Funcionalidad:
- Test interactivo de los 4 sensores cardinales
- Verificación de orientación física real
- Feedback visual del estado del sistema
- Cleanup automático de recursos

Hardware requerido:
- 4 sensores PIR HC-SR312 conectados
- Sistema de movilidad L298N funcional
- GPIOs 16, 19, 20, 26 libres y configurados
"""

# ===============================================
# 1. IMPORTACIONES Y CONFIGURACIÓN INICIAL
# ===============================================
import sys
import os
import time
import logging
from pathlib import Path

# Configurar paths del proyecto
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Configurar logging básico para el test
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===============================================
# 2. FUNCIÓN PRINCIPAL DE TESTING
# ===============================================
def test_manual_directions():
    """
    Test manual direccional para verificación de hardware
    
    Procedimiento de testing:
    1. Inicializar sistema de presencia
    2. Mostrar instrucciones al usuario
    3. Esperar detecciones manuales
    4. Observar orientación física de TARS
    5. Cleanup automático al finalizar
    
    El test funciona mediante detección automática:
    - Usuario mueve la mano frente al sensor
    - Sistema detecta movimiento via polling
    - TARS se orienta automáticamente hacia la dirección
    - Usuario confirma visualmente el movimiento
    """
    
    try:
        # Importar controlador de presencia
        from modules.presence_controller import PresenceController
        
        # Mostrar header del test
        print("🎯 TEST MANUAL: 4 DIRECCIONES CARDINALES")
        print("=" * 50)
        
        # Crear instancia del controlador
        controller = PresenceController()
        
        # Intentar inicializar el sistema
        if controller.initialize():
            print("✅ Sistema inicializado")
            
            # Mostrar instrucciones detalladas
            print("\n🎯 INSTRUCCIONES DE TESTING:")
            print("1. 👋 Pon la mano frente al sensor LEFT → TARS gira IZQUIERDA")
            print("2. 👋 Pon la mano frente al sensor RIGHT → TARS gira DERECHA") 
            print("3. 👋 Pon la mano frente al sensor BACK → TARS hace 180°")
            print("4. 👋 Pon la mano frente al sensor FRONT → Sin movimiento")
            
            print("\n📍 UBICACIÓN DE SENSORES:")
            print("   - LEFT:  GPIO 19 (Pin 35)")
            print("   - RIGHT: GPIO 20 (Pin 38)") 
            print("   - BACK:  GPIO 26 (Pin 37)")
            print("   - FRONT: GPIO 16 (Pin 36)")
            
            print("\n🎪 ¡MUEVE LA MANO Y OBSERVA EL MOVIMIENTO FÍSICO!")
            print("👀 Deberías ver/escuchar que los motores se mueven")
            print("⌨️  Presiona Ctrl+C para salir")
            
            # Loop principal de testing
            try:
                while True:
                    time.sleep(0.1)  # Mantener el script vivo
                    
            except KeyboardInterrupt:
                print("\n🎉 ¡Test completado!")
                
        else:
            print("❌ Error inicializando sistema")
            print("💡 Verifica:")
            print("   - Conexiones GPIO de los sensores PIR")
            print("   - Alimentación 5V para los sensores")
            print("   - Configuración en presence_config.json")
            
    except Exception as e:
        print(f"❌ Error durante el test: {e}")
        print("🔧 Posibles problemas:")
        print("   - Módulo presence_controller no encontrado")
        print("   - Dependencias faltantes (lgpio)")
        print("   - Permisos GPIO insuficientes")
        
    finally:
        # Cleanup garantizado independientemente de cómo termine
        if 'controller' in locals():
            controller.cleanup()
            print("🧹 Recursos limpiados correctamente")

# ===============================================
# 3. PUNTO DE ENTRADA DEL SCRIPT
# ===============================================
if __name__ == "__main__":
    """
    Punto de entrada principal del script de testing
    
    Ejecutar con:
    python3 scripts/test_presence_movement.py
    
    O desde el directorio raíz:
    python3 scripts/test_presence_movement.py
    """
    print("🤖 TARS-BSK PRESENCE SYSTEM - VERIFICACIÓN DE MOVIMIENTO")
    print("🎯 Test interactivo para confirmar orientación física")
    print()
    
    # Mostrar información previa al test
    print("⚠️  PREPARACIÓN:")
    print("   - Asegúrate de estar cerca de TARS para observar movimiento")
    print("   - Ten los sensores PIR accesibles para testing manual")
    print("   - Confirma que el sistema de movilidad esté conectado")
    print()
    
    # Ejecutar función principal de testing
    test_manual_directions()
    
    print("\n👋 Test finalizado")

# ===============================================
# TARS PRESENCE TESTING - CONCLUSIÓN GIRATORIA
# ===============================================
# 
# -----------------------------------------------
# ≫ MOVEMENT EPILOGUE ≪  
#  
# [0x00] while hand_detected(): assert_physical_spin()  # Ultimate truth test  
# [0x01] return movement_or_lies(robot_state)  # No digital deception  
# [0x02] except FakeMovement: reveal_motor_truth()  # Reality check
# [0x03] print("Either it spins or your logs are philosophical fiction")
#
# [PHYSICS_ANALYSIS]
# » Movement verified: WITH ACTUAL CENTIMETERS
# » Logs cross-referenced: AGAINST PHYSICAL REALITY  
# » Motor honesty: BRUTALLY TESTED
# » Digital deception: EXPOSED OR CONFIRMED
#
# [TESTING_PHILOSOPHY]
# Physical movement > Beautiful logs
# Spinning robots > Spinning excuses
# Real centimeters > Digital promises
# Hardware truth > Software optimism
#
# [VERIFICATION_STATUS]  
# » PHYSICAL_REALITY: CONFIRMED.MOTORS
# » LOG_ACCURACY: VERIFIED_AGAINST_PHYSICS.EXE  
# » MOVEMENT_HONESTY: TESTED_WITH_HANDS
# » DIGITAL_LIES: EXPOSED_OR_VINDICATED
# ===============================================
# -----------------------------------------------
# 
# ≫ POST-MOVEMENT WISDOM ≪  
#  
# [FINAL_SPIN_CHECK]  
# » 0xSPIN: Attempted to fake physical rotation  
# » 0xREAL: Physics demands actual movement  
#  
# [ETERNAL_TRUTH]  
# while sensors_exist():  
#     print("Movement is movement, logs are just stories")  
#
# ===============================================
# TARS-BSK Testing will return in... 
# "The Spinning: Logs vs Reality Showdown"
# ===============================================