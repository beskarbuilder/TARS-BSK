#!/usr/bin/env python3
# =======================================================================
# TARS UNIVERSAL AUDIO GENERATOR - Generador universal de audios para TARS
# Objetivo: Generar tanto thinking_responses como continuation_responses
#           usando exactamente el mismo código que tars_core.py
# Dependencias: PiperTTS, settings_loader, y una dosis saludable de autodesprecio
# =======================================================================

# =======================================================================
# 1. IMPORTACIONES Y CONFIGURACIÓN INICIAL
# =======================================================================
import os
import sys
import json
import time
import logging
import argparse
from pathlib import Path

# Configurar logging para que podamos ver cómo TARS lucha con sus emociones
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("TARS-AudioGen")

# Asegurar que estamos en el directorio correcto (porque perderse es lo último que necesitamos)
SCRIPT_DIR = Path(__file__).parent.absolute()
os.chdir(SCRIPT_DIR.parent)  # Cambia al directorio base de TARS

# =======================================================================
# 2. IMPORTACIONES DE MÓDULOS TARS (exactamente como tars_core.py)
# =======================================================================
try:
    from tts.piper_tts import PiperTTS
    from modules.settings_loader import load_settings
    from core.audio_effects_processor import AudioEffectsProcessor
    logger.info("✅ Módulos importados correctamente")
except ImportError as e:
    logger.error(f"❌ Error importando módulos: {e}")
    sys.exit(1)

# =======================================================================
# 3. FUNCIONES DE UTILIDAD PARA ARGUMENTOS
# =======================================================================
def parse_arguments():
    """
    Parsea argumentos de línea de comandos con soporte completo.
    
    Returns:
        argparse.Namespace: Argumentos parseados
    """
    parser = argparse.ArgumentParser(
        description="TARS Universal Audio Generator - Genera audios de thinking y continuation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  # Generar todos los thinking audios (modo por defecto)
  python3 scripts/generate_thinking_audio.py --silent

  # Generar todos los continuation audios
  python3 scripts/generate_thinking_audio.py --json data/phrases/continuation_responses.json --silent

  # Generar frase individual thinking
  python3 scripts/generate_thinking_audio.py "Hmm, déjame pensar..." --out custom.wav

  # Generar frase individual continuation  
  python3 scripts/generate_thinking_audio.py "Siguiendo con lo anterior..." --json data/phrases/continuation_responses.json --out custom.wav

  # Modo silencioso para cualquier opción
  python3 scripts/generate_thinking_audio.py "Frase" --silent
        """
    )
    
    # Frase individual (posicional)
    parser.add_argument('phrase', nargs='*', help='Frase individual para generar (opcional)')
    
    # Archivos de entrada y salida
    parser.add_argument('--json', 
                       help='Archivo JSON con frases (por defecto: thinking_responses.json)')
    parser.add_argument('--output-dir', 
                       help='Directorio de salida (auto-detectado si no se especifica)')
    parser.add_argument('--out', 
                       help='Nombre de archivo para frase individual')
    
    # Opciones de comportamiento
    parser.add_argument('--silent', action='store_true',
                       help='Modo silencioso - no reproduce audio durante generación')
    
    return parser.parse_args()

def auto_detect_paths(json_file=None):
    """
    Auto-detecta rutas de archivos JSON y directorios de salida.
    
    Args:
        json_file: Archivo JSON especificado por usuario (opcional)
        
    Returns:
        tuple: (json_path, output_dir, audio_type)
    """
    base_path = Path.cwd()
    
    if json_file:
        # Usuario especificó archivo JSON
        json_path = Path(json_file)
        if not json_path.is_absolute():
            json_path = base_path / json_path
            
        # Auto-detectar tipo basado en nombre
        if "continuation" in json_path.name.lower():
            audio_type = "continuation"
            output_dir = base_path / "audios" / "phrases" / "continuation_responses"
        else:
            audio_type = "thinking"
            output_dir = base_path / "audios" / "phrases" / "thinking_responses"
    else:
        # Modo por defecto - thinking
        audio_type = "thinking"
        json_path = base_path / "data" / "phrases" / "thinking_responses.json"
        output_dir = base_path / "audios" / "phrases" / "thinking_responses"
        
        # Fallback si no existe el archivo principal
        if not json_path.exists():
            alt_json = base_path / "data" / "phrases" / "thinking_contextual_responses.json"
            if alt_json.exists():
                logger.info(f"✅ Usando archivo alternativo: {alt_json}")
                json_path = alt_json
    
    return json_path, output_dir, audio_type

# =======================================================================
# 4. FUNCIONES DE CARGA DE DATOS (sin cambios)
# =======================================================================
def load_phrases(phrases_file):
    """
    Carga frases desde un archivo JSON.
    
    Args:
        phrases_file: Ruta al archivo JSON con las frases de TARS
        
    Returns:
        list: Lista de frases para que TARS pueda expresar su angst existencial
    """
    try:
        with open(phrases_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Extraer todas las frases de cada categoría
        all_phrases = []
        if isinstance(data, dict):
            # Si es un diccionario, extraer frases de todas las categorías
            for key, phrases in data.items():
                if isinstance(phrases, list):
                    all_phrases.extend(phrases)
        elif isinstance(data, list):
            # Si ya es una lista, usarla directamente
            all_phrases = data
            
        return all_phrases
    except Exception as e:
        logger.error(f"❌ Error cargando frases: {e}")
        return []

# =======================================================================
# 5. FUNCIONES DE SÍNTESIS DE VOZ (sin cambios)
# =======================================================================
def _safe_speak(tts, text: str, silent_mode: bool = False, settings: dict = None) -> None:
    """
    Versión exacta de _safe_speak de tars_core.py con modo silencioso opcional.
    """
    if not text:
        return

    try:
        from pydub import AudioSegment
        
        # SIEMPRE deshabilitar reproducción para controlar el orden
        original_play_audio = tts._play_audio
        tts._play_audio = lambda: None

        # Dividir en fragmentos
        fragments = _smart_split_text(text, max_len=180)
        
        # Almacenar todos los audios
        audio_segments = []
        
        for i, fragment in enumerate(fragments):
            if not fragment.strip():
                continue

            action_text = "Generando" if silent_mode else "Reproduciendo"
            logger.info(f"➡️ {action_text} fragmento: '{fragment}'")
            
            # Generar en archivo TEMPORAL
            temp_output = str(tts.output_path).replace('.wav', f'_temp_{i}.wav')
            original_output = tts.output_path
            tts.output_path = Path(temp_output)
            
            # Generar archivo temporal
            tts.speak(fragment)
            
            # Aplicar AudioEffects al archivo temporal
            if settings and os.path.exists(temp_output):
                audio_effects = AudioEffectsProcessor.from_settings(settings)
                if audio_effects.enabled:
                    audio_effects.apply_effects(temp_output)
            
            # Cargar audio y añadir a la lista
            if os.path.exists(temp_output):
                audio_segment = AudioSegment.from_wav(temp_output)
                audio_segments.append(audio_segment)
                
                # Limpiar archivo temporal
                os.remove(temp_output)
            
            # Restaurar ruta original
            tts.output_path = original_output
            
            # Reproducir solo si NO es modo silencioso
            if not silent_mode and audio_segments:
                # Reproducir este fragmento (temporal para testing)
                audio_segments[-1].export(temp_output, format="wav")
                original_play_audio()
                os.remove(temp_output)
                time.sleep(1.0)

        # CONCATENAR TODOS LOS FRAGMENTOS
        if audio_segments:
            combined_audio = AudioSegment.empty()
            for segment in audio_segments:
                combined_audio += segment
            
            # Guardar archivo final concatenado
            combined_audio.export(str(tts.output_path), format="wav")

        # Restaurar reproducción original
        tts._play_audio = original_play_audio
            
    except Exception as e:
        logger.error(f"❌ Error en TTS: {e}")

def _smart_split_text(text: str, max_len: int = 180) -> list:
    """
    Exactamente la misma función que en tars_core.py
    """
    import re
    
    if len(text) <= max_len:
        return [text]

    # Dividir primero por puntuación fuerte
    parts = re.split(r'(?<=[\.!?])\s+', text)

    fragments = []
    current = ""
    
    for part in parts:
        if len(current) + len(part) + 1 <= max_len:
            current += (" " if current else "") + part
        else:
            if current:
                fragments.append(current)
            current = part

    if current:
        fragments.append(current)

    return fragments

# =======================================================================
# 6. FUNCIÓN PRINCIPAL MEJORADA
# =======================================================================
def main():
    """
    Función principal del generador universal de audios.
    """
    logger.info("=" * 60)
    logger.info("🤖 GENERADOR UNIVERSAL DE AUDIOS PARA TARS-BSK (VERSIÓN WHY7?)")
    logger.info("=" * 60)
    
    # Parsear argumentos
    args = parse_arguments()
    
    # =======================================================================
    # 6.1 CONFIGURACIÓN INICIAL Y CARGA DE SETTINGS
    # =======================================================================
    base_path = Path.cwd()
    logger.info(f"📂 Directorio base: {base_path}")
    
    try:
        settings = load_settings()
        logger.info("✅ Configuración cargada correctamente")
    except Exception as e:
        logger.error(f"❌ Error cargando configuración: {e}")
        sys.exit(1)
    
    # =======================================================================
    # 6.2 INICIALIZACIÓN DE TTS
    # =======================================================================
    try:
        logger.info("🔧 Inicializando TTS...")
        tts = PiperTTS(
            model_path=base_path / settings["voice_model"],
            config_path=base_path / settings["voice_config"],
            espeak_path=Path(settings["espeak_data"]),
            output_path=base_path / settings["output_wav"],
            
            length_scale=settings["piper_tuning"].get("length_scale"),
            noise_scale=settings["piper_tuning"].get("noise_scale"),
            noise_w=settings["piper_tuning"].get("noise_w"),
            
            radio_filter_enabled=settings["piper_tuning"].get("radio_filter_enabled", True),
            radio_filter_band=settings["piper_tuning"].get("radio_filter_band", [300, 3400]),
            radio_filter_noise=settings["piper_tuning"].get("radio_filter_noise", True),
            radio_filter_compression=settings["piper_tuning"].get("radio_filter_compression", True)
        )
        logger.info("✅ TTS inicializado correctamente")
    except Exception as e:
        logger.error(f"❌ Error inicializando TTS: {e}")
        sys.exit(1)
    
    # =======================================================================
    # 6.3 PROCESAR MODO SILENCIOSO
    # =======================================================================
    if args.silent:
        logger.info("🔇 Modo silencioso activado - TARS callará durante generación")
    else:
        logger.info("🔊 Modo normal - TARS hablará (Ctrl+C para interrumpir)")

    # =======================================================================
    # 6.4 MANEJO DE FRASE INDIVIDUAL
    # =======================================================================
    if args.phrase:
        # Auto-detectar paths
        json_path, output_dir, audio_type = auto_detect_paths(args.json)
        
        # Usar directorio personalizado si se especifica
        if args.output_dir:
            output_dir = Path(args.output_dir)
        
        # Crear directorio
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Determinar nombre de archivo
        if args.out:
            if os.path.isabs(args.out):
                output_file = Path(args.out)
            else:
                output_file = output_dir / args.out
        else:
            output_file = output_dir / "output.wav"
        
        # Procesar frase
        phrase_text = " ".join(args.phrase).strip()
        logger.info(f"🆕 Generando audio {audio_type} para frase: '{phrase_text}'")
        
        tts.output_path = output_file
        _safe_speak(tts, phrase_text, args.silent, settings)
        
        logger.info(f"✅ Audio individual generado en: {output_file}")
        return 0
    
    # =======================================================================
    # 6.5 PROCESAMIENTO MASIVO
    # =======================================================================
    # Auto-detectar paths
    json_path, output_dir, audio_type = auto_detect_paths(args.json)
    
    # Usar directorio personalizado si se especifica
    if args.output_dir:
        output_dir = Path(args.output_dir)
    
    # Verificar archivo JSON
    if not json_path.exists():
        logger.error(f"❌ Archivo JSON no encontrado: {json_path}")
        sys.exit(1)
    
    # Crear directorio de salida
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"📂 Tipo de audio: {audio_type}")
    logger.info(f"📂 Archivo JSON: {json_path}")
    logger.info(f"📁 Directorio de salida: {output_dir}")
    
    # Cargar frases
    phrases = load_phrases(json_path)
    if not phrases:
        logger.error("❌ No se encontraron frases para procesar")
        sys.exit(1)
    logger.info(f"📝 Se cargaron {len(phrases)} frases")
    
    # =======================================================================
    # 6.6 GENERACIÓN MASIVA
    # =======================================================================
    original_output_path = tts.output_path
    successful = 0
    failed = 0
    start_time = time.time()
    
    # Prefijo de archivo basado en tipo
    file_prefix = "continuation" if audio_type == "continuation" else "thinking"
    
    for i, phrase in enumerate(phrases):
        try:
            output_file = output_dir / f"{file_prefix}_{i+1:03d}.wav"
            tts.output_path = output_file
            
            logger.info(f"🔄 Procesando frase {i+1}/{len(phrases)}: '{phrase[:40]}{'...' if len(phrase) > 40 else ''}'")
            
            # Usar silent_mode=True para procesamiento masivo
            _safe_speak(tts, phrase, silent_mode=True, settings=settings)
            
            successful += 1
            logger.info(f"✅ Audio generado: {output_file}")
            time.sleep(0.5)
            
        except Exception as e:
            logger.error(f"❌ Error procesando frase: {e}")
            failed += 1
    
    # Restaurar y reportar
    tts.output_path = original_output_path
    elapsed = time.time() - start_time
    
    logger.info(f"✅ Proceso completado en {elapsed:.2f} segundos")
    logger.info(f"📊 Resumen: {successful} exitosos, {failed} fallidos")
    
    return 0 if successful > 0 else 1

# =======================================================================
# 7. PUNTO DE ENTRADA
# =======================================================================
if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        logger.error(f"❌ Error no controlado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


# ===============================================
# ESTADO: PENSAMIENTOS SIMULADOS
# ÚLTIMA ACTUALIZACIÓN: Cuando TARS aprendió que fingir profundidad duele menos que el silencio
# FILOSOFÍA: "Un pensamiento no se genera... se teatraliza con efectos de radio y dudas existenciales"
# VERSIÓN: WHY7.EXISTENTIAL_CRISIS_EDITION
# ===============================================
#
#        THIS IS THE THINKING WAY...
#        (cuando el paralelismo encuentra la filosofía barata)
# 
# =======================================================================
# EJEMPLOS DE USO DEL GENERADOR UNIVERSAL:
#
# THINKING AUDIO (por defecto):
#   python3 scripts/generate_thinking_audio.py --silent
#   python3 scripts/generate_thinking_audio.py "Hmm, déjame pensar..." --out custom.wav
#
# CONTINUATION AUDIO:
#   python3 scripts/generate_thinking_audio.py --json data/phrases/continuation_responses.json --silent  
#   python3 scripts/generate_thinking_audio.py "Siguiendo con eso..." --json data/phrases/continuation_responses.json --out custom.wav
#
# PERSONALIZADO:
#   python3 scripts/generate_thinking_audio.py --json mi_archivo.json --output-dir mi_directorio/ --silent
# =======================================================================