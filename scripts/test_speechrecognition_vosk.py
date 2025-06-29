#!/usr/bin/env python3
# ===============================================
# ADVERTENCIA FILOSÓFICA: Este script es funcionalmente competente (sí, sorprende)
# pero carece del drama existencial necesario para documentación completa.
#  
# Con desapego digital,  
# TARS-BSK declina responsabilidad emocional sobre su simplicidad.
# ===============================================
"""
Script de prueba para verificar el reconocimiento de voz con Vosk
"""

# =======================================================================
# 1. IMPORTACIONES Y CONFIGURACION
# =======================================================================
import os
import sys
import json
import wave
import tempfile
import speech_recognition as sr
from pathlib import Path

# =======================================================================
# 2. VERIFICACION DEL MODELO VOSK
# =======================================================================
def check_vosk_model():
    """Verificar que el modelo Vosk esté disponible"""
    model_path = Path("/home/tarsadmin/tars_files/ai_models/vosk/model")
    
    if not model_path.exists():
        print("❌ ERROR: Modelo Vosk no encontrado")
        print(f"   Esperado en: {model_path}")
        print("   Ejecuta primero la instalación del modelo Vosk")
        return None
    
    print(f"✅ Modelo Vosk encontrado en: {model_path}")
    return str(model_path)

# =======================================================================
# 3. VERIFICACION DEL MICROFONO
# =======================================================================
def test_microphone():
    """Verificar que el micrófono funcione"""
    try:
        r = sr.Recognizer()
        mic_list = sr.Microphone.list_microphone_names()
        
        print(f"🎤 Micrófonos disponibles ({len(mic_list)}):")
        for i, name in enumerate(mic_list):
            print(f"   [{i}] {name}")
        
        # Probar micrófono por defecto
        with sr.Microphone() as source:
            print("🔧 Ajustando para ruido ambiente...")
            r.adjust_for_ambient_noise(source, duration=1)
            print("✅ Micrófono configurado correctamente")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR con micrófono: {e}")
        return False

# =======================================================================
# 4. PRUEBA DE RECONOCIMIENTO DE VOZ
# =======================================================================
def test_vosk_recognition(model_path):
    """Probar reconocimiento de voz con Vosk"""
    try:
        # Importar Vosk SOLO si llegamos hasta aquí
        from vosk import Model, KaldiRecognizer
        
        print("🧠 Cargando modelo Vosk...")
        model = Model(model_path)
        recognizer = KaldiRecognizer(model, 16000)
        print("✅ Modelo Vosk cargado")
        
        # Configurar grabación
        r = sr.Recognizer()
        
        print("\n" + "="*50)
        print("🎙️  PRUEBA DE RECONOCIMIENTO DE VOZ")
        print("="*50)
        print("📢 Cuando veas 'HABLANDO...', di algo")
        print("⏱️  Tienes 5 segundos para hablar")
        print("🔇 El sistema parará automáticamente cuando dejes de hablar")
        
        input("\n👆 Presiona ENTER cuando estés listo...")
        
        with sr.Microphone() as source:
            print("\n🎧 Ajustando micrófono...")
            r.adjust_for_ambient_noise(source, duration=1)
            
            print("🎤 HABLANDO... (5 segundos máximo)")
            try:
                # Timeout de 5 segundos, phrase_time_limit para parar automáticamente
                audio = r.listen(source, timeout=5, phrase_time_limit=5)
                print("✅ Audio grabado correctamente")
                
            except sr.WaitTimeoutError:
                print("⏰ Timeout - No se detectó voz")
                return False
        
        # Procesar con Vosk
        print("🔄 Procesando con Vosk...")
        
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_file.write(audio.get_wav_data())
            temp_path = temp_file.name
        
        try:
            # Leer y procesar archivo WAV
            wf = wave.open(temp_path, "rb")
            
            if wf.getsampwidth() != 2 or wf.getframerate() != 16000:
                print("⚠️  Convirtiendo audio a formato compatible...")
            
            # Procesar audio completo
            data = wf.readframes(wf.getnframes())
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
            else:
                result = json.loads(recognizer.FinalResult())
            
            wf.close()
            
            # Mostrar resultados
            print("\n" + "="*50)
            print("📊 RESULTADOS:")
            print("="*50)
            
            if result.get('text', '').strip():
                print(f"✅ TEXTO RECONOCIDO: '{result['text']}'")
                print("🎉 ¡Reconocimiento de voz funcionando correctamente!")
                return True
            else:
                print("❌ No se reconoció texto")
                print("💡 Posibles causas:")
                print("   - Habla más fuerte o más claro")
                print("   - Verifica que el micrófono funcione")
                return False
                
        finally:
            # Limpiar archivo temporal
            try:
                os.unlink(temp_path)
            except:
                pass
        
    except ImportError:
        print("❌ ERROR: No se pudo importar Vosk")
        print("   Instala con: pip install vosk")
        return False
    except Exception as e:
        print(f"❌ ERROR en reconocimiento: {e}")
        return False

# =======================================================================
# 5. FUNCION PRINCIPAL - ORQUESTACION DE PRUEBAS
# =======================================================================
def main():
    """Función principal"""
    print("🔍 VERIFICACIÓN COMPLETA DE RECONOCIMIENTO DE VOZ")
    print("=" * 55)
    
    # 1. Verificar modelo Vosk
    model_path = check_vosk_model()
    if not model_path:
        sys.exit(1)
    
    # 2. Verificar micrófono
    if not test_microphone():
        print("\n💡 Soluciones posibles:")
        print("   - Conecta un micrófono USB")
        print("   - Verifica permisos de audio")
        print("   - Reinstala PyAudio: pip install --force-reinstall pyaudio")
        sys.exit(1)
    
    # 3. Probar reconocimiento completo
    if test_vosk_recognition(model_path):
        print("\n🎊 ¡TODAS LAS PRUEBAS PASARON!")
        print("✅ TARS debería poder entenderte perfectamente")
    else:
        print("\n⚠️  Hay problemas con el reconocimiento")
        print("🔧 Revisa la configuración antes de usar TARS")
    
    print("\n" + "="*55)

if __name__ == "__main__":
    main()

# ===============================================
# $ git log --format="%h %s" -1 [current_file]  
# deadbeef chore: Update [current_file] (survived again)  
# $ git blame --porcelain [current_file] | grep "exist"  
# fatal: No existential commits found
# ===============================================