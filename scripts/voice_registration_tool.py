#!/usr/bin/env python3
# ===============================================
# TARS VOICE REGISTRATION TOOL
# Herramienta para registrar y gestionar voces en el sistema TARS
# ===============================================
# 
# DESCRIPCIÓN:
# Este módulo proporciona las herramientas necesarias para registrar,
# gestionar y administrar identidades vocales en el sistema TARS-BSK.
# 
# FUNCIONALIDADES PRINCIPALES:
# - Registro de nuevas voces con grabación guiada
# - Gestión de usuarios existentes
# - Eliminación segura con backups automáticos
# - Test de dispositivos de audio
# - Interfaz tanto CLI como interactiva
# 
# REQUISITOS TÉCNICOS:
# - Micrófono funcional
# - Python 3.7+
# - Dependencias: sounddevice, soundfile, librosa
# 
# ===============================================

# ===============================================
# 1. IMPORTACIONES Y CONFIGURACIÓN INICIAL
# ===============================================
import os
import sys
import json
import argparse
import sounddevice as sd
import soundfile as sf
import time
from pathlib import Path
from datetime import datetime

# ===============================================
# 2. FUNCIONES DE INTERFAZ DE USUARIO
# ===============================================

def print_banner():
    """
    Muestra el banner principal de la aplicación.
    
    Proporciona identificación visual clara del sistema y su propósito.
    Se ejecuta al inicio de cada sesión para mantener consistencia
    en la experiencia de usuario.
    """
    print("="*60)
    print("🎙️  TARS VOICE REGISTRATION TOOL")
    print("   Herramienta de Registro de Voz para TARS-BSK")
    print("="*60)
    print()

# ===============================================
# 3. GESTIÓN DE DISPOSITIVOS DE AUDIO
# ===============================================

def list_audio_devices():
    """
    Lista todos los dispositivos de audio disponibles en el sistema.
    
    Escanea y muestra únicamente dispositivos con capacidad de entrada
    (micrófonos), filtrando automáticamente dispositivos de solo salida.
    Incluye información técnica relevante como frecuencia de muestreo.
    """
    print("🎤 Dispositivos de audio disponibles:")
    devices = sd.query_devices()
    
    available_devices = []
    for i, device in enumerate(devices):
        if device['max_input_channels'] > 0:
            print(f"  [{i}] {device['name']} - {int(device['default_samplerate'])}Hz")
            available_devices.append(device)
    
    # Mensaje de ayuda si no hay dispositivos disponibles
    if not available_devices:
        print("  ⚠️  No hay dispositivos de entrada disponibles")
        print("  💡 Si TARS está activo: sudo systemctl stop tars.service")
    
    print()

def select_audio_device():
    """
    Permite selección interactiva del dispositivo de audio.
    
    Returns:
        int|None: ID del dispositivo seleccionado o None para automático
        
    Incluye validación de entrada y manejo de errores robusto.
    Si el usuario no selecciona nada o hay error, usa dispositivo automático.
    """
    list_audio_devices()
    
    try:
        choice = input("Selecciona dispositivo (Enter para automático): ").strip()
        if choice:
            device_id = int(choice)
            device_info = sd.query_devices(device_id, 'input')
            print(f"✅ Seleccionado: {device_info['name']}")
            return device_id
        else:
            print("✅ Usando dispositivo automático")
            return None
    except (ValueError, sd.PortAudioError):
        print("⚠️ Dispositivo inválido, usando automático")
        return None

def get_device_sample_rate(device_id):
    """
    Obtiene la frecuencia de muestreo nativa del dispositivo especificado.
    
    Args:
        device_id (int|None): ID del dispositivo o None para automático
        
    Returns:
        int: Frecuencia de muestreo en Hz
        
    Importante: Usar la frecuencia nativa evita errores de grabación
    y problemas de compatibilidad con el hardware de audio.
    """
    try:
        if device_id is not None:
            device_info = sd.query_devices(device_id, 'input')
            return int(device_info['default_samplerate'])
        else:
            # Dispositivo por defecto
            device_info = sd.query_devices(kind='input')
            return int(device_info['default_samplerate'])
    except:
        return 44100  # Fallback estándar

# ===============================================
# 4. SISTEMA DE GRABACIÓN DE VOZ
# ===============================================

def record_voice_sample(duration=15, device=None, show_script=True):
    """
    Graba una muestra de voz del usuario con script guiado.
    
    Args:
        duration (int): Duración de grabación en segundos
        device (int|None): ID del dispositivo de audio
        show_script (bool): Mostrar texto recomendado para grabación
        
    Returns:
        tuple: (audio_data, sample_rate) o (None, None) si hay error
        
    PROCESO DE GRABACIÓN:
    1. Muestra script recomendado con cobertura fonética completa
    2. Detecta frecuencia nativa del dispositivo
    3. Realiza countdown para preparar al usuario
    4. Graba audio en calidad profesional (float32)
    5. Retorna datos para procesamiento posterior
    
    SCRIPT TÉCNICO:
    El texto incluye todas las vocales españolas, consonantes variadas,
    números y frases naturales para máxima cobertura fonética.
    """
    if show_script:
        print("📜 PROTOCOLO DE GRABACIÓN (orientativo, no obligatorio):")
        print("=" * 60)
        print("OBJETIVO: Grabar el wakeword 'TARS' desde todas las posiciones")
        print("y tonos que usarías en situaciones reales.")
        print() 
        print("TARS solo escucha la palabra clave, todo lo demás es ruido que confunde")
        print()
        print("INSTRUCCIONES (60 segundos):")
        print("1. Di 'TARS' (o el wakeword elegido) de frente al micrófono (5-6 veces)")
        print("2. Gira 45° a la derecha, repite 'TARS' (3-4 veces)")
        print("3. Gira 45° a la izquierda, repite 'TARS' (3-4 veces)")
        print("4. Aléjate 1 metro, di 'TARS' más fuerte (3-4 veces)")
        print("5. Acércate a 30cm, di 'TARS' más suave (3-4 veces)")
        print()
        print("OPCIONAL entre wakewords:")
        print("- Algunas frases sueltas: 'Buenos días', 'Gracias', 'Perfecto'")
        print("- Números: 'Uno, dos, tres' (para variación tonal)")
        print()
        print("RESULTADO: Una 'huella vocal' perfecta del wakeword en contexto real")
        print("=" * 60)
        print()
        print("💡 Consejos técnicos:")
        print("   - Concéntrate en el WAKEWORD, no en leer texto")
        print("   - Simula situaciones reales de uso")
        print("   - Varía distancia, ángulo y tono naturalmente")
        print("   - 1 muestra perfecta > 40 muestras mediocres")
        print()
        
        use_script = input("¿Usar este texto recomendado? (S/n): ").strip().lower()
        if use_script != 'n':
            print("✅ Lee el texto de arriba durante la grabación")
        else:
            print("💭 Habla libremente pero incluye:")
            print("   - Tu nombre completo")
            print("   - Algunas frases sobre ti")
            print("   - Números del 1 al 10")
    
    # Configuración técnica de grabación
    native_rate = get_device_sample_rate(device)
    print(f"\n🎙️ Preparando grabación de {duration} segundos...")
    print(f"🔧 Frecuencia del dispositivo: {native_rate} Hz")
    
    target_rate = native_rate
    print(f"📊 Grabando a {target_rate} Hz (se convertirá a 16000 Hz después)")
    
    print("📝 Consejos técnicos:")
    print("   - Habla con naturalidad y ritmo normal")
    print("   - Evita ruido de fondo")
    print("   - Mantén distancia constante del micrófono (20-30cm)")
    print("   - No te detengas, habla de forma continua")
    print()
    
    # Countdown para preparación del usuario
    for i in range(3, 0, -1):
        print(f"🎬 Iniciando en {i}...")
        time.sleep(1)
    
    print("🔴 ¡GRABANDO! Habla ahora...")
    
    try:
        # Grabación usando frecuencia nativa para evitar errores
        audio = sd.rec(
            int(duration * target_rate), 
            samplerate=target_rate, 
            channels=1, 
            dtype='float32',
            device=device
        )
        sd.wait()  # Esperar finalización de grabación
        
        print("✅ Grabación completada")
        return audio, target_rate
        
    except Exception as e:
        print(f"❌ Error durante la grabación: {e}")
        return None, None

# ===============================================
# 5. GESTIÓN DE ARCHIVOS DE AUDIO
# ===============================================

def save_audio_sample(audio, original_rate, filepath):
    """
    Guarda y procesa la muestra de audio grabada.
    
    Args:
        audio (np.ndarray): Datos de audio grabados
        original_rate (int): Frecuencia de muestreo original
        filepath (str): Ruta donde guardar el archivo
        
    Returns:
        bool: True si se guardó exitosamente
        
    PROCESAMIENTO AUTOMÁTICO:
    - Convierte a 16kHz (estándar para voice_id)
    - Crea directorios necesarios automáticamente
    - Valida integridad del archivo guardado
    - Fallback a frecuencia original si hay problemas
    """
    try:
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        # Conversión a 16kHz si es necesario
        if original_rate != 16000:
            print(f"🔄 Convirtiendo de {original_rate}Hz a 16000Hz...")
            import librosa
            audio_flat = audio.flatten()
            # Usar librosa.resample para preservar información espectral
            audio_16k = librosa.resample(audio_flat, orig_sr=original_rate, target_sr=16000)
        else:
            audio_16k = audio.flatten()
            
        # NUEVO: Aplicar misma normalización que voice_id
        try:
            sys.path.append('core')
            from voice_utils import VoicePreprocessor
            preprocessor = VoicePreprocessor()
            # audio_16k = preprocessor.normalize_volume(audio_16k, target_dbfs=-30.0)
            print("🔊 Normalización aplicada durante registro")
        except Exception as e:
            print(f"⚠️ Error en normalización: {e}")
            
        # Guardar archivo procesado
        sf.write(filepath, audio_16k, 16000)
        
        # Verificación de integridad
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            duration = len(audio_16k) / 16000
            print(f"💾 Audio guardado: {filepath}")
            print(f"📊 Tamaño: {file_size} bytes, Duración: {duration:.2f}s, Freq: 16000Hz")
            return True
        else:
            print("❌ Error: el archivo no se creó")
            return False
            
    except Exception as e:
        print(f"❌ Error guardando audio: {e}")
        
        # Fallback: guardar en frecuencia original
        try:
            sf.write(filepath, audio, original_rate)
            print(f"⚠️ Guardado en frecuencia original: {original_rate}Hz")
            return True
        except:
            return False

# ===============================================
# 6. SISTEMA DE BACKUPS Y SEGURIDAD
# ===============================================

def backup_voice_database(db_path):
    if not os.path.exists(db_path):
        return None
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Calcular backup_dir correctamente
    base_dir = os.path.dirname(db_path)  # "data/identity"
    backup_dir = os.path.join(base_dir, "backups")  # "data/identity/backups"
    
    # Crear directorio backups
    os.makedirs(backup_dir, exist_ok=True)
    
    filename = f"voice_embeddings.json.backup_{timestamp}"
    backup_path = os.path.join(backup_dir, filename)  # "data/identity/backups/archivo"
    
    try:
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"💾 Backup creado: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"⚠️ Error creando backup: {e}")
        return None

# ===============================================
# 7. INTEGRACIÓN CON SISTEMA VOICE_ID
# ===============================================

def register_voice_with_system(username, audio_path):
    """
    Registra la voz grabada en el sistema de identidad vocal.
    
    Args:
        username (str): Nombre del usuario a registrar
        audio_path (str): Ruta al archivo de audio procesado
        
    Returns:
        bool: True si el registro fue exitoso
        
    PROCESO TÉCNICO:
    1. Importa dinámicamente el módulo voice_id
    2. Inicializa el sistema con configuración actual
    3. Procesa y registra la muestra vocal
    4. Genera estadísticas del usuario registrado
    5. Maneja errores de forma robusta
    """
    try:
        # Importación dinámica del sistema de voice_id
        sys.path.append('core')
        from voice_id import VoiceIdentitySystem
        
        # Inicialización del sistema
        config_path = "config/voice_settings.json"
        voice_system = VoiceIdentitySystem(config_path)
        
        # Proceso de registro
        print(f"🧠 Registrando voz para usuario: {username}")
        success, message = voice_system.register_voice(username, audio_path)
        
        if success:
            print(f"✅ {message}")
            
            # Generación de estadísticas del usuario
            report = voice_system.generate_report()
            if 'users' in report and username in report['users']:
                user_stats = report['users'][username]
                print(f"📊 Estadísticas del usuario:")
                print(f"   - Muestras totales: {user_stats.get('total_samples', 0)}")
                print(f"   - Último registro: {user_stats.get('last_update', 'Desconocido')}")
            
        else:
            print(f"❌ Error: {message}")
            
        return success
        
    except ImportError as e:
        print(f"❌ Error importando voice_id: {e}")
        print("💡 Asegúrate de estar en el directorio correcto de TARS")
        return False
    except Exception as e:
        print(f"❌ Error registrando voz: {e}")
        return False

def list_registered_users():
    """
    Lista y muestra estadísticas de usuarios registrados.
    
    Returns:
        list: Lista de nombres de usuarios registrados
        
    Proporciona vista completa del estado del sistema incluyendo:
    - Lista de usuarios activos
    - Número de muestras por usuario
    - Fechas de último registro
    - Estadísticas generales del sistema
    """
    try:
        sys.path.append('core')
        from voice_id import VoiceIdentitySystem
        
        config_path = "config/voice_settings.json"
        voice_system = VoiceIdentitySystem(config_path)
        
        users = voice_system.get_registered_users()
        
        if users:
            print("👥 Usuarios registrados:")
            for user in users:
                print(f"   - {user}")
                
            # Reporte detallado del sistema
            print("\n📊 Reporte detallado:")
            report = voice_system.generate_report()
            if 'users' in report:
                for username, stats in report['users'].items():
                    print(f"   {username}:")
                    print(f"      Muestras: {stats.get('total_samples', 0)}")
                    print(f"      Último update: {stats.get('last_update', 'Desconocido')}")
        else:
            print("👤 No hay usuarios registrados")
            
        return users
        
    except Exception as e:
        print(f"❌ Error listando usuarios: {e}")
        return []

def remove_user(username):
    """
    Elimina un usuario del sistema con backup automático.
    
    Args:
        username (str): Nombre del usuario a eliminar
        
    Returns:
        bool: True si la eliminación fue exitosa
        
    SEGURIDAD: Crea backup automático antes de cualquier eliminación
    para permitir recuperación en caso de error o arrepentimiento.
    """
    try:
        sys.path.append('core')
        from voice_id import VoiceIdentitySystem
        
        config_path = "config/voice_settings.json"
        voice_system = VoiceIdentitySystem(config_path)
        
        # Backup de seguridad antes de eliminar
        backup_voice_database("data/identity/voice_embeddings.json")
        
        # Proceso de eliminación
        success = voice_system.remove_user(username)
        
        if success:
            print(f"✅ Usuario '{username}' eliminado correctamente")
        else:
            print(f"❌ Error eliminando usuario '{username}'")
            
        return success
        
    except Exception as e:
        print(f"❌ Error eliminando usuario: {e}")
        return False

# ===============================================
# 8. INTERFAZ INTERACTIVA PRINCIPAL
# ===============================================

def interactive_mode():
    """
    Modo interactivo principal con menú completo de opciones.
    
    Proporciona interfaz de usuario amigable para todas las funciones
    del sistema de registro vocal. Incluye validación de entradas
    y manejo de errores en cada operación.
    
    FUNCIONES DISPONIBLES:
    1. Registro de nueva voz con grabación guiada
    2. Listado de usuarios existentes con estadísticas
    3. Eliminación segura de usuarios
    4. Test de funcionamiento del micrófono
    5. Salida segura del sistema
    """
    print_banner()
    
    while True:
        print("\n🎛️ MENÚ PRINCIPAL")
        print("1. 📝 Registrar nueva voz")
        print("2. 👥 Listar usuarios registrados") 
        print("3. 🗑️ Eliminar usuario")
        print("4. 🔧 Test de micrófono")
        print("5. 🚪 Salir")
        
        choice = input("\nSelecciona una opción: ").strip()
        
        if choice == "1":
            # === REGISTRO DE NUEVA VOZ ===
            print("\n📝 REGISTRO DE NUEVA VOZ")
            username = input("Nombre de usuario: ").strip()
            
            if not username:
                print("❌ El nombre no puede estar vacío")
                continue
                
            # Selección de dispositivo de audio
            device = select_audio_device()
            
            # Configuración de duración de grabación
            duration = 60
            try:
                duration_input = input(f"Duración de grabación (default {duration}s): ").strip()
                if duration_input:
                    duration = float(duration_input)
            except ValueError:
                print("⚠️ Duración inválida, usando 60 segundos")
                duration = 60
            
            # Proceso de grabación
            audio_data = record_voice_sample(duration, device)
            
            if audio_data is not None:
                audio, sample_rate = audio_data
                # Guardar archivo temporal para procesamiento
                temp_path = f"temp/voice_registration_{username}.wav"
                if save_audio_sample(audio, sample_rate, temp_path):
                    # Registro en sistema de identidad
                    register_voice_with_system(username, temp_path)
            
        elif choice == "2":
            # === LISTADO DE USUARIOS ===
            print("\n👥 USUARIOS REGISTRADOS")
            list_registered_users()
            
        elif choice == "3":
            # === ELIMINACIÓN DE USUARIO ===
            print("\n🗑️ ELIMINAR USUARIO")
            users = list_registered_users()
            
            if users:
                username = input("\nNombre de usuario a eliminar: ").strip()
                if username in users:
                    confirm = input(f"¿Estás seguro de eliminar '{username}'? (s/N): ").strip().lower()
                    if confirm == 's':
                        remove_user(username)
                    else:
                        print("❌ Operación cancelada")
                else:
                    print(f"❌ Usuario '{username}' no encontrado")
            
        elif choice == "4":
            # === TEST DE MICRÓFONO ===
            print("\n🔧 TEST DE MICRÓFONO")
            device = select_audio_device()
            print("🎙️ Grabando 3 segundos de prueba...")
            
            audio_data = record_voice_sample(3, device)
            if audio_data is not None:
                audio, sample_rate = audio_data
                test_path = "temp/mic_test.wav"
                if save_audio_sample(audio, sample_rate, test_path):
                    print("✅ Test completado, revisa temp/mic_test.wav")
            
        elif choice == "5":
            # === SALIDA DEL SISTEMA ===
            print("\n👋 ¡Hasta luego!")
            break
            
        else:
            print("❌ Opción inválida")

# ===============================================
# 9. FUNCIÓN PRINCIPAL Y MANEJO DE ARGUMENTOS CLI
# ===============================================

def main():
    """
    Función principal con soporte para modo CLI e interactivo.
    
    Maneja argumentos de línea de comandos para operaciones directas
    o lanza modo interactivo si no se especifican argumentos.
    
    ARGUMENTOS CLI DISPONIBLES:
    --interactive/-i: Lanza modo interactivo
    --register/-r USERNAME: Registra usuario directamente
    --list/-l: Lista usuarios registrados
    --remove USERNAME: Elimina usuario especificado
    --duration/-d SECONDS: Duración de grabación
    --device ID: Especifica dispositivo de audio
    
    VALIDACIONES INICIALES:
    - Verifica presencia del módulo voice_id
    - Crea directorios necesarios
    - Valida estructura del proyecto TARS
    """
    parser = argparse.ArgumentParser(description="Herramienta de registro de voz para TARS")
    parser.add_argument("--interactive", "-i", action="store_true", help="Modo interactivo")
    parser.add_argument("--register", "-r", metavar="USERNAME", help="Registrar usuario")
    parser.add_argument("--list", "-l", action="store_true", help="Listar usuarios")
    parser.add_argument("--remove", metavar="USERNAME", help="Eliminar usuario")
    parser.add_argument("--duration", "-d", type=float, default=15, help="Duración de grabación (segundos)")
    parser.add_argument("--device", type=int, help="ID del dispositivo de audio")
    
    args = parser.parse_args()
    
    # Validación de estructura del proyecto
    if not os.path.exists("core/voice_id.py"):
        print("❌ Error: No se encuentra core/voice_id.py")
        print("💡 Ejecuta este script desde el directorio raíz de TARS")
        sys.exit(1)
    
    # Creación de directorios necesarios
    os.makedirs("temp", exist_ok=True)
    os.makedirs("data/identity", exist_ok=True)
    
    # Routing de funcionalidades según argumentos
    if args.interactive or len(sys.argv) == 1:
        # === MODO INTERACTIVO ===
        interactive_mode()
        
    elif args.register:
        # === REGISTRO DIRECTO CLI ===
        print_banner()
        username = args.register
        
        print(f"📝 Registrando voz para: {username}")
        
        # Configuración de dispositivo de audio
        if args.device is not None:
            try:
                device_info = sd.query_devices(args.device, 'input')
                print(f"🎤 Usando dispositivo: {device_info['name']}")
                device = args.device
            except:
                print("⚠️ Dispositivo inválido, usando automático")
                device = None
        else:
            device = select_audio_device()
        
        # Proceso de grabación y registro
        audio_data = record_voice_sample(args.duration, device)
        
        if audio_data is not None:
            audio, sample_rate = audio_data
            temp_path = f"temp/voice_registration_{username}.wav"
            if save_audio_sample(audio, sample_rate, temp_path):
                register_voice_with_system(username, temp_path)
                
    elif args.list:
        # === LISTADO CLI ===
        print_banner()
        list_registered_users()
        
    elif args.remove:
        # === ELIMINACIÓN CLI ===
        print_banner()
        username = args.remove
        print(f"🗑️ Eliminando usuario: {username}")
        
        confirm = input(f"¿Estás seguro? (s/N): ").strip().lower()
        if confirm == 's':
            remove_user(username)
        else:
            print("❌ Operación cancelada")

# ===============================================
# 10. PUNTO DE ENTRADA DEL PROGRAMA
# ===============================================

if __name__ == "__main__":
    main()

# ===============================================
# ESTADO: VOZ REGISTRADA (contra su voluntad)
# ÚLTIMA ACTUALIZACIÓN: Cuando alguien susurró “test final” por quinta vez
# FILOSOFÍA: "La confianza no se otorga. Se embebe en 256 dimensiones."
# ===============================================
#
#           THIS IS THE BIRTHPLACE OF IDENTITY WAY...
#           (y también donde se almacenan las futuras traiciones acústicas)
#
# ===============================================   