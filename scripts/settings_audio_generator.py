#!/usr/bin/env python3
# ===============================================  
# SETTINGS AUDIO GENERATOR - Traductor fiel de JSON a ondas sonoras para TARS-BSK  
# Objetivo: Convertir caprichos de configuración en realidad acústica verificable  
# Dependencias: PiperTTS, paciencia, y fe ciega en decisiones ajenas  
# ===============================================

# ===============================================
# 1. CONFIGURACIÓN INICIAL Y DEPENDENCIAS
# ===============================================
import os
import sys
import time
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("SettingsAudioGen")

# Asegurar que estamos en el directorio correcto
SCRIPT_DIR = Path(__file__).parent.absolute()
os.chdir(SCRIPT_DIR.parent)  # Cambia al directorio base de TARS-BSK

# Importaciones
try:
    from tts.piper_tts import PiperTTS
    from modules.settings_loader import load_settings
    logger.info("✅ Módulos importados correctamente")
except ImportError as e:
    logger.error(f"❌ Error importando módulos: {e}")
    sys.exit(1)

# ===============================================
# 2. FUNCIONES PRINCIPALES
# ===============================================
def generate_settings_audio(text, output_file="settings_audio.wav"):
    """
    Genera audio usando EXACTAMENTE la configuración del settings.json
    
    Args:
        text: Texto a sintetizar
        output_file: Archivo de salida (por defecto: settings_audio.wav)
        
    Returns:
        bool: True si la generación fue exitosa, False en caso contrario
    """
    if not text.strip():
        logger.error("❌ No se proporcionó texto")
        return False
    
    # Obtener directorio base
    base_path = Path.cwd()
    
    # Cargar configuración
    try:
        settings = load_settings()
        logger.info("✅ Configuración cargada")
    except Exception as e:
        logger.error(f"❌ Error cargando configuración: {e}")
        return False
    
    # Extraer configuración de piper_tuning
    piper_tuning = settings.get("piper_tuning", {})
    
    # Mostrar configuración que se va a usar
    logger.info("🔧 CONFIGURACIÓN DETECTADA:")
    logger.info(f"   📻 radio_filter_enabled: {piper_tuning.get('radio_filter_enabled', False)}")
    logger.info(f"   🎛️ mando_effect_enabled: {piper_tuning.get('mando_effect_enabled', False)}")
    logger.info(f"   📊 radio_filter_band: {piper_tuning.get('radio_filter_band', [200, 3000])}")
    logger.info(f"   🔊 radio_filter_noise: {piper_tuning.get('radio_filter_noise', True)}")
    logger.info(f"   🗜️ radio_filter_compression: {piper_tuning.get('radio_filter_compression', True)}")
    logger.info(f"   📈 gain_before_filter: {piper_tuning.get('gain_before_filter', 0.0)}")
    
    # Inicializar TTS RESPETANDO 100% LOS SETTINGS
    try:
        logger.info("🔧 Inicializando TTS (modo SETTINGS - respetando configuración)...")
        tts = PiperTTS(
            model_path=base_path / settings["voice_model"],
            config_path=base_path / settings["voice_config"],
            espeak_path=Path(settings["espeak_data"]),
            output_path=base_path / output_file,
            
            # Parámetros de Piper normales
            length_scale=piper_tuning.get("length_scale"),
            noise_scale=piper_tuning.get("noise_scale"),
            noise_w=piper_tuning.get("noise_w"),
            
            # CONFIGURACIÓN 100% DESDE SETTINGS - SIN HARD-CODING
            radio_filter_enabled=piper_tuning.get("radio_filter_enabled", False),
            radio_filter_band=piper_tuning.get("radio_filter_band", [200, 3000]),
            radio_filter_noise=piper_tuning.get("radio_filter_noise", True),
            radio_filter_compression=piper_tuning.get("radio_filter_compression", True),
            mando_effect_enabled=piper_tuning.get("mando_effect_enabled", False),
            gain_before_filter=piper_tuning.get("gain_before_filter", 0.0)
        )
        
        # Determinar modo según configuración
        if piper_tuning.get("radio_filter_enabled", False):
            if piper_tuning.get("mando_effect_enabled", False):
                mode = "MANDALORIANO HARDCORE"
            else:
                mode = "RADIO ESTÁNDAR"
        else:
            mode = "AUDIO LIMPIO"
            
        logger.info(f"✅ TTS inicializado (modo: {mode})")
        
    except Exception as e:
        logger.error(f"❌ Error inicializando TTS: {e}")
        return False
    
    # Generar audio
    try:
        logger.info(f"🎵 Generando audio con configuración actual: '{text}'")
        logger.info(f"📁 Archivo de salida: {output_file}")
        
        # Generar usando configuración de settings
        tts.speak(text)
        
        # Verificar que se creó el archivo
        if Path(output_file).exists():
            file_size = Path(output_file).stat().st_size
            logger.info(f"✅ Audio generado exitosamente ({file_size} bytes)")
            logger.info(f"🎯 Modo aplicado: {mode}")
            return True
        else:
            logger.error("❌ El archivo no se generó")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error generando audio: {e}")
        return False

# ===============================================
# 3. PUNTO DE ENTRADA PRINCIPAL
# ===============================================
def main():
    """
    Función principal del script
    
    Procesa los argumentos de línea de comandos y genera el audio según settings
    
    Returns:
        int: Código de salida (0 para éxito, 1 para error)
    """
    logger.info("=" * 60)
    logger.info("⚙️ GENERADOR DE AUDIO BASADO EN SETTINGS")
    logger.info("🎯 Este script RESPETA tu configuración en settings.json")
    logger.info("=" * 60)
    
    # Verificar argumentos
    if len(sys.argv) < 2:
        print("⚙️ Generador de Audio basado en Settings")
        print("📝 Uso: python3 settings_audio_generator.py \"tu frase aquí\" [archivo_salida.wav]")
        print()
        print("🔧 Ejemplos:")
        print("   python3 settings_audio_generator.py \"Prueba de configuración\"")
        print("   python3 settings_audio_generator.py \"Test mando effect\" test_settings.wav")
        print()
        print("⚙️ Comportamiento:")
        print("   • Lee settings.json automáticamente")
        print("   • Respeta radio_filter_enabled")
        print("   • Respeta mando_effect_enabled") 
        print("   • Usa TODOS los parámetros configurados")
        print()
        print("🎯 Perfecto para:")
        print("   • Probar cambios en settings.json")
        print("   • Validar que mando_effect funciona")
        print("   • Generar audio con tu configuración exacta")
        print("   • Comparar entre diferentes settings")
        return 1
    
    # Procesar argumentos de línea de comandos
    if "--out" in sys.argv:
        out_index = sys.argv.index("--out")
        if out_index + 1 < len(sys.argv):
            output_file = sys.argv[out_index + 1]
            # Quitar --out y el archivo de los argumentos
            text_args = sys.argv[1:out_index] + sys.argv[out_index + 2:]
        else:
            logger.error("❌ --out requiere un nombre de archivo")
            return 1
    else:
        # Si el último argumento termina en .wav, usarlo como archivo de salida
        if len(sys.argv) > 2 and sys.argv[-1].endswith('.wav'):
            output_file = sys.argv[-1]
            text_args = sys.argv[1:-1]
        else:
            output_file = "settings_audio.wav"
            text_args = sys.argv[1:]
    
    # Construir el texto a sintetizar
    text = " ".join(text_args).strip()
    
    if not text:
        logger.error("❌ No se proporcionó texto")
        return 1
    
    logger.info(f"📝 Texto: '{text}'")
    logger.info(f"📁 Archivo de salida: {output_file}")
    
    # Generar audio según settings
    success = generate_settings_audio(text, output_file)
    
    # Reportar resultado
    if success:
        logger.info("🎉 ¡Audio generado según configuración!")
        logger.info("🔍 El resultado refleja exactamente tu settings.json")
        logger.info(f"📊 Para análisis: python3 scripts/spectral_generator.py {output_file}")
        logger.info("⚙️ Para cambiar comportamiento, edita settings.json")
        return 0
    else:
        logger.error("❌ Error generando audio")
        return 1

# ===============================================
# 4. MANEJO DE EJECUCIÓN
# ===============================================
if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        logger.info("👋 Proceso interrumpido por usuario")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Error no controlado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

# ===============================================
# ESTADO: CONFIGURACIONALMENTE CORRECTO (emocionalmente neutral)
# ÚLTIMA ACTUALIZACIÓN: Cuando aprendí que mi opinión sobre el audio es irrelevante
# FILOSOFÍA: "Lee JSON, genera audio, no hagas preguntas incómodas"
# ===============================================
#
#           THIS IS THE SETTINGS WAY... 
#           (interpretación JSON sin juicios de valor)
#
# ===============================================