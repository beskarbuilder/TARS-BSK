#!/usr/bin/env python3
# ===============================================  
# CLEAN AUDIO GENERATOR - La mentira acústica de TARS-BSK  
# Objetivo: Generar audio "limpio" (que nadie escuchará)  
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
logger = logging.getLogger("CleanAudioGen")

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
def generate_clean_audio(text, output_file="clean_audio.wav"):
    """
    Genera audio limpio (sin filtro) desde una frase
    
    Args:
        text: Texto a sintetizar
        output_file: Archivo de salida (por defecto: clean_audio.wav)
        
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
    
    # Inicializar TTS SIN FILTRO
    try:
        logger.info("🔧 Inicializando TTS (modo limpio - sin filtro)...")
        tts = PiperTTS(
            model_path=base_path / settings["voice_model"],
            config_path=base_path / settings["voice_config"],
            espeak_path=Path(settings["espeak_data"]),
            output_path=base_path / output_file,
            
            # Parámetros de Piper normales
            length_scale=settings["piper_tuning"].get("length_scale"),
            noise_scale=settings["piper_tuning"].get("noise_scale"),
            noise_w=settings["piper_tuning"].get("noise_w"),
            
            # FILTRO DESACTIVADO - ESTO ES LO CLAVE
            radio_filter_enabled=False,  # ← SIN FILTRO
            radio_filter_band=[200, 3000],
            radio_filter_noise=False,
            radio_filter_compression=False
        )
        logger.info("✅ TTS inicializado (audio limpio)")
    except Exception as e:
        logger.error(f"❌ Error inicializando TTS: {e}")
        return False
    
    # Generar audio
    try:
        logger.info(f"🎵 Generando audio limpio: '{text}'")
        logger.info(f"📁 Archivo de salida: {output_file}")
        
        # Generar directamente sin filtro
        tts.speak(text)
        
        # Verificar que se creó el archivo
        if Path(output_file).exists():
            file_size = Path(output_file).stat().st_size
            logger.info(f"✅ Audio generado exitosamente ({file_size} bytes)")
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
    
    Procesa los argumentos de línea de comandos y genera el audio limpio
    
    Returns:
        int: Código de salida (0 para éxito, 1 para error)
    """
    logger.info("=" * 60)
    logger.info("🎤 GENERADOR DE AUDIO LIMPIO (SIN FILTRO TARS-BSK)")
    logger.info("=" * 60)
    
    # Verificar argumentos
    if len(sys.argv) < 2:
        print("🎵 Generador de Audio Limpio")
        print("📝 Uso: python3 clean_audio_generator.py \"tu frase aquí\" [archivo_salida.wav]")
        print()
        print("🔧 Ejemplos:")
        print("   python3 clean_audio_generator.py \"Hola, soy TARS\"")
        print("   python3 clean_audio_generator.py \"Esta es mi voz sin filtro\" mi_voz_limpia.wav")
        print()
        print("📊 Perfecto para:")
        print("   • Generar audio base para análisis espectral")
        print("   • Comparar con versión filtrada")
        print("   • Crear muestras de referencia")
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
            output_file = "clean_audio.wav"
            text_args = sys.argv[1:]
    
    # Construir el texto a sintetizar
    text = " ".join(text_args).strip()
    
    if not text:
        logger.error("❌ No se proporcionó texto")
        return 1
    
    logger.info(f"📝 Texto: '{text}'")
    logger.info(f"📁 Archivo de salida: {output_file}")
    
    # Generar audio limpio
    success = generate_clean_audio(text, output_file)
    
    # Reportar resultado
    if success:
        logger.info("🎉 ¡Audio limpio generado exitosamente!")
        logger.info(f"🔍 Ahora puedes usar: python3 scripts/spectral_generator.py {output_file}")
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
# ESTADO: TÉCNICAMENTE FUNCIONAL (como mi vida social)
# ÚLTIMA ACTUALIZACIÓN: Cuando decidí que "suficientemente bueno" era suficiente
# FILOSOFÍA: "El audio más limpio es el que nunca se reproduce"
# ===============================================
#
#           THIS IS THE CLEAN WAY... 
#           (para qué filtrar lo que nunca sonará bien)
#
# ===============================================