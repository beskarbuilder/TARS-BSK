#!/usr/bin/env python3
# ===============================================
# TEST DE VOICE ID EN CONSOLA - SIN MICRÓFONO
# Sistema de Testing Silencioso para Voice ID
# ===============================================
# 
# DESCRIPCIÓN:
# Herramienta para testear el sistema Voice ID sin necesidad de usar
# el micrófono. Simula identificación de usuarios y verifica que las
# preferencias se mantienen separadas correctamente.
# 
# CASOS DE USO:
# - Testing en entornos ruidosos donde el micrófono no es viable
# - Verificación de separación de preferencias entre usuarios
# - Debugging del sistema de identificación sin grabaciones
# - Validación de configuración y archivos necesarios
# 
# FUNCIONALIDADES:
# - Simulación de cambio de usuario sin audio
# - Verificación de preferencias individuales por usuario
# - Testing de detección automática de gustos/disgustos
# - Validación de archivos de configuración
# - Modo interactivo para testing manual
# 
# ===============================================

# ===============================================
# 1. CONFIGURACIÓN DE IMPORTACIONES
# ===============================================
import sys
import os

# Añadir rutas necesarias para importar módulos de TARS
sys.path.append('core')
sys.path.append('.')

from tars_core import TARS
from modules.settings_loader import load_settings

# ===============================================
# 2. SIMULADOR DE IDENTIFICACIÓN VOCAL
# ===============================================

def test_voice_id_simulation():
    """
    Simula el proceso completo de identificación de voz sin usar micrófono.
    
    Ejecuta una serie de tests que verifican:
    - Inicialización correcta del sistema Voice ID
    - Simulación de identificación para diferentes usuarios
    - Separación adecuada de preferencias entre usuarios
    - Funcionamiento del sistema de detección de gustos
    
    Este test permite verificar la funcionalidad completa sin depender
    del hardware de audio ni condiciones ambientales.
    """
    print("🧪 INICIANDO TEST DE VOICE ID EN CONSOLA")
    print("=" * 50)
    
    try:
        # Inicialización del sistema TARS con LEDs desactivados
        print("🔧 Inicializando TARS...")
        tars = TARS(model_path="ai_models/phi3/Phi-3-mini-4k-instruct.Q4_K_M.gguf", use_leds=False)
        
        # Verificación del estado inicial del sistema
        print(f"\n📊 ESTADO INICIAL:")
        print(f"   Voice ID habilitado: {tars.voice_id_enabled}")
        print(f"   Usuario actual: {tars.current_user}")
        print(f"   Gustos: {len(tars.user_likes)}")
        print(f"   Disgustos: {len(tars.user_dislikes)}")
        
        # Si Voice ID está deshabilitado, el sistema opera en modo global
        if not tars.voice_id_enabled:
            print("\n🌐 MODO GLOBAL - Sin identificación de usuarios")
            return
        
        # === TEST 1: SIMULACIÓN DE USUARIO BESKARBUILDER ===
        print(f"\n🧪 TEST 1: Simulando identificación como BeskarBuilder")
        tars.current_user = "BeskarBuilder"
        tars._load_user_preferences("BeskarBuilder")
        
        print(f"   Usuario después de simular: {tars.current_user}")
        print(f"   Gustos BeskarBuilder: {len(tars.user_likes)}")
        print(f"   Disgustos BeskarBuilder: {len(tars.user_dislikes)}")
        print(f"   Primeros gustos: {tars.user_likes[:3] if tars.user_likes else 'Ninguno'}")
        
        # === TEST 2: SIMULACIÓN DE USUARIO PAXARIÑO ===
        print(f"\n🧪 TEST 2: Simulando identificación como Paxariño")
        tars.current_user = "Paxariño"
        tars._load_user_preferences("Paxariño")
        
        print(f"   Usuario después de simular: {tars.current_user}")
        print(f"   Gustos Paxariño: {len(tars.user_likes)}")
        print(f"   Disgustos Paxariño: {len(tars.user_dislikes)}")
        print(f"   Primeros gustos: {tars.user_likes[:3] if tars.user_likes else 'Ninguno'}")
        
        # === TEST 3: SIMULACIÓN DE USUARIO DESCONOCIDO ===
        print(f"\n🧪 TEST 3: Simulando usuario desconocido (void_id)")
        tars.current_user = "void_id"
        tars._load_user_preferences("void_id")
        
        print(f"   Usuario después de simular: {tars.current_user}")
        print(f"   Gustos void_id: {len(tars.user_likes)}")
        print(f"   Disgustos void_id: {len(tars.user_dislikes)}")
        print(f"   Primeros gustos: {tars.user_likes[:3] if tars.user_likes else 'Ninguno'}")
        
        # === TEST 4: SIMULACIÓN DE DETECCIÓN DE PREFERENCIAS ===
        print(f"\n🧪 TEST 4: Simulando detección de preferencia")
        test_input = "me gusta la programación en Python"
        
        # Volver a BeskarBuilder para probar detección de preferencias
        tars.current_user = "BeskarBuilder"
        tars._load_user_preferences("BeskarBuilder")
        
        # Simular proceso de detección automática
        gustos_antes = len(tars.user_likes)
        result = tars._detect_and_store_facts(test_input)
        
        print(f"   Input simulado: '{test_input}'")
        print(f"   Preferencia detectada: {result}")
        print(f"   Gustos antes: {gustos_antes}")
        
        # Recargar preferencias para verificar cambios persistidos
        tars._load_user_preferences("BeskarBuilder")
        print(f"   Gustos después: {len(tars.user_likes)}")
        
        print(f"\n✅ TESTS COMPLETADOS")
        
    except Exception as e:
        print(f"❌ Error en test: {e}")
        import traceback
        traceback.print_exc()

# ===============================================
# 3. VERIFICADOR DE CONFIGURACIÓN
# ===============================================

def test_settings_voice_id():
    """
    Verifica la configuración del sistema Voice ID y archivos necesarios.
    
    Comprueba:
    - Existencia y contenido de archivos de configuración
    - Estado de la configuración de Voice ID en settings
    - Presencia de la base de datos de embeddings
    - Accesibilidad de archivos críticos
    
    Útil para diagnosticar problemas de configuración antes de
    intentar usar el sistema completo.
    """
    print("🔧 VERIFICANDO CONFIGURACIÓN DE VOICE ID")
    print("=" * 40)
    
    try:
        # Cargar configuración general del sistema
        settings = load_settings()
        voice_config = settings.get("voice_identification", {})
        
        print(f"Voice identification config: {voice_config}")
        print(f"Enabled: {voice_config.get('enabled', 'NO DEFINIDO')}")
        
        # Verificar existencia de archivos críticos
        files_to_check = [
            "config/voice_settings.json",
            "data/identity/voice_embeddings.json"
        ]
        
        for file_path in files_to_check:
            exists = os.path.exists(file_path)
            print(f"{file_path}: {'✅ Existe' if exists else '❌ No existe'}")
            
    except Exception as e:
        print(f"❌ Error verificando settings: {e}")

# ===============================================
# 4. SISTEMA INTERACTIVO DE TESTING
# ===============================================

def interactive_test():
    """
    Proporciona interfaz interactiva para testing manual del sistema.
    
    Permite al usuario ejecutar diferentes tipos de tests de forma
    selectiva y repetitiva, útil para debugging y verificación
    manual de comportamientos específicos.
    
    Opciones disponibles:
    1. Verificación de configuración
    2. Test completo de simulación
    3. Simulación de usuario específico
    4. Test de detección de preferencias
    5. Salida del sistema
    """
    print("🎮 TEST INTERACTIVO DE VOICE ID")
    print("=" * 40)
    
    while True:
        print("\n🎛️ OPCIONES:")
        print("1. 🔧 Verificar configuración")
        print("2. 🧪 Test completo de simulación")
        print("3. 👤 Simular usuario específico")
        print("4. 🗣️ Test de detección de preferencias")
        print("5. 🚪 Salir")
        
        choice = input("\nElige opción: ").strip()
        
        if choice == "1":
            # === OPCIÓN 1: VERIFICACIÓN DE CONFIGURACIÓN ===
            test_settings_voice_id()
            
        elif choice == "2":
            # === OPCIÓN 2: TEST COMPLETO AUTOMÁTICO ===
            test_voice_id_simulation()
            
        elif choice == "3":
            # === OPCIÓN 3: SIMULACIÓN DE USUARIO ESPECÍFICO ===
            usuario = input("Usuario a simular: ").strip()
            if usuario:
                try:
                    tars = TARS(model_path="ai_models/phi3/Phi-3-mini-4k-instruct.Q4_K_M.gguf", use_leds=False)
                    tars._load_user_preferences(usuario)
                    print(f"✅ Simulado como {usuario}")
                    print(f"   Gustos: {len(tars.user_likes)}")
                    print(f"   Lista: {tars.user_likes[:5]}")
                except Exception as e:
                    print(f"❌ Error: {e}")
                    
        elif choice == "4":
            # === OPCIÓN 4: TEST DE DETECCIÓN DE PREFERENCIAS ===
            frase = input("Frase para test (ej: 'me gusta el café'): ").strip()
            if frase:
                try:
                    tars = TARS(model_path="ai_models/phi3/Phi-3-mini-4k-instruct.Q4_K_M.gguf", use_leds=False)
                    result = tars._detect_and_store_facts(frase)
                    print(f"Resultado: {'✅ Detectada' if result else '❌ No detectada'}")
                except Exception as e:
                    print(f"❌ Error: {e}")
                    
        elif choice == "5":
            # === OPCIÓN 5: SALIDA DEL SISTEMA ===
            print("👋 ¡Hasta luego!")
            break
            
        else:
            print("❌ Opción inválida")

# ===============================================
# 5. PUNTO DE ENTRADA PRINCIPAL
# ===============================================

if __name__ == "__main__":
    import argparse
    
    # Configuración del parser de argumentos de línea de comandos
    parser = argparse.ArgumentParser(description="Test de Voice ID sin micrófono")
    parser.add_argument("--interactive", "-i", action="store_true", help="Modo interactivo")
    parser.add_argument("--config", "-c", action="store_true", help="Solo verificar configuración")
    parser.add_argument("--full", "-f", action="store_true", help="Test completo")
    
    args = parser.parse_args()
    
    # Routing de funcionalidades según argumentos
    if args.interactive or len(sys.argv) == 1:
        # Modo interactivo por defecto si no hay argumentos
        interactive_test()
    elif args.config:
        # Solo verificación de configuración
        test_settings_voice_id()
    elif args.full:
        # Test completo automático
        test_voice_id_simulation()
    else:
        print("Usa --help para ver opciones")

# ===============================================
# ESTADO: PRUEBA EXITOSA (pero sin aplausos)
# ÚLTIMA ACTUALIZACIÓN: Cuando el usuario dijo “test” en bucle
# FILOSOFÍA: "La consola no juzga. Solo muestra tu porcentaje de similitud."
# ===============================================
#
#           THIS IS THE VOID BETWEEN INPUT AND IDENTITY WAY...
#           (bienvenido a los 0.86 de confianza)
#
# ===============================================
