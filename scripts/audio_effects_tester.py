#!/usr/bin/env python3
# ===============================================
# AUDIO EFFECTS TESTER - PROBADOR DE EFECTOS PARA TARS-BSK
# Objetivo: Generar muestras de audio para documentar cada distorsión existencial
# Filosofía: "Si no puedes medirlo, al menos hazlo sonar interesante"
# Advertencia: Los samples contienen un 12% de sarcasmo no intencional
# ===============================================

# =======================================================================
# 1. IMPORTACIONES Y CONFIGURACIÓN INICIAL
# =======================================================================
import os
import sys
from pathlib import Path

# Setup paths
SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent
os.chdir(PROJECT_ROOT)

# Añadir paths necesarios
sys.path.extend([
    str(PROJECT_ROOT),
    str(PROJECT_ROOT / 'core'),
    str(PROJECT_ROOT / 'tts'),
    str(PROJECT_ROOT / 'modules')
])

try:
    from core.audio_effects_processor import AudioEffectsProcessor
    from tts.piper_tts import PiperTTS
    from modules.settings_loader import load_settings
    print("✅ Módulos cargados correctamente")
except ImportError as e:
    print(f"❌ Error importando módulos: {e}")
    print("💡 Asegúrate de:")
    print("   1. Estar en el directorio raíz del proyecto")
    print("   2. Tener el archivo core/audio_effects_processor.py actualizado")
    print("   3. Haber actualizado tts/piper_tts.py")
    sys.exit(1)

# =======================================================================
# 2. GENERACIÓN DE AUDIO BASE
# =======================================================================
def generate_base_audio(text: str, output_file: str = "audio_effects_processor_base.wav") -> str:
    """
    Genera audio base con PiperTTS + radio_filter (sin audio effects).
    
    Args:
        text: Texto a sintetizar
        output_file: Archivo de salida
        
    Returns:
        Path del archivo generado
    """
    print(f"🎤 Generando audio base...")
    print(f"   📝 Texto: '{text}'")
    
    try:
        settings = load_settings()
        
        # Crear PiperTTS con radio filter pero SIN audio effects
        tts = PiperTTS(
            model_path=PROJECT_ROOT / settings["voice_model"],
            config_path=PROJECT_ROOT / settings["voice_config"],
            espeak_path=Path(settings["espeak_data"]),
            output_path=PROJECT_ROOT / output_file,
            length_scale=settings.get("piper_tuning", {}).get("length_scale", 1.1),
            noise_scale=settings.get("piper_tuning", {}).get("noise_scale", 1.0),
            noise_w=settings.get("piper_tuning", {}).get("noise_w", 0.8),
            radio_filter_enabled=True,
            radio_filter_band=[200, 3500],
            radio_filter_noise=True,
            radio_filter_compression=True,
            gain_before_filter=1.5
        )
        
        # Audio effects config vacía (sin efectos en la base)
        tts.audio_effects_config = {"enabled": False}
        
        # Generar audio
        tts.speak(text)
        
        if os.path.exists(output_file):
            print(f"   ✅ Audio base generado: {output_file}")
            return output_file
        else:
            raise Exception("No se generó el archivo de audio")
            
    except Exception as e:
        print(f"   ❌ Error generando audio base: {e}")
        raise

# =======================================================================
# 3. TESTING DE PRESETS
# =======================================================================
def test_all_presets(base_audio: str, text: str):
    """
    Prueba todos los presets temporales disponibles.
    
    Args:
        base_audio: Archivo de audio base
        text: Texto usado (para logging)
    """
    print(f"\n🎚️ PROBANDO TODOS LOS PRESETS TEMPORALES:")
    print("="*70)
    
    # Lista actualizada con los nuevos presets de calidad técnica
    presets = [
        ("none", "❌ Sin efectos (control)"),
        ("studio_delay", "🎙️ Delay de estudio profesional"),
        ("vintage_echo", "📻 Eco vintage multi-tap"),
        ("chorus_classic", "🎵 Chorus clásico multi-voz"),
        ("space_chamber", "🏛️ Cámara espaciosa"),
        ("wide_chorus", "🌊 Chorus amplio con delay"),
        ("ambient_hall", "🏟️ Ambiente de sala grande")
    ]
    
    results = []
    
    for preset_name, description in presets:
        print(f"\n   {description}...")
        
        # Configuración para este preset
        config = {
            "enabled": True,
            "preset": preset_name
        }
        
        output_file = f"audio_effects_processor_{preset_name}.wav"
        
        try:
            if preset_name == "none":
                # Para "none", simplemente copiamos el audio base
                import shutil
                shutil.copy2(base_audio, output_file)
                print(f"   ✅ {preset_name}: {output_file} (copia de base)")
                results.append((preset_name, description, output_file, True))
            else:
                # Crear procesador y aplicar preset
                processor = AudioEffectsProcessor(config)
                success = processor.apply_effects(base_audio, output_file)
                
                if success and os.path.exists(output_file):
                    print(f"   ✅ {preset_name}: {output_file}")
                    results.append((preset_name, description, output_file, True))
                else:
                    print(f"   ❌ {preset_name}: No se generó archivo")
                    results.append((preset_name, description, None, False))
                
        except Exception as e:
            print(f"   ❌ {preset_name}: Error - {e}")
            results.append((preset_name, description, None, False))
    
    return results

# =======================================================================
# 4. TESTING DE CONFIGURACIÓN ACTUAL
# =======================================================================
def test_current_settings(base_audio: str):
    """
    Prueba la configuración actual de settings.json.
    
    Args:
        base_audio: Archivo de audio base
    """
    print(f"\n⚙️ PROBANDO CONFIGURACIÓN ACTUAL:")
    print("="*70)
    
    try:
        settings = load_settings()
        audio_effects_config = settings.get("audio_effects", {})
        
        if audio_effects_config.get("enabled", False):
            preset = audio_effects_config.get("preset", "none")
            print(f"   🎚️ Audio effects habilitados en settings.json")
            print(f"   🎨 Preset configurado: {preset}")
            
            if preset != "none":
                output_file = "test_current_settings.wav"
                
                processor = AudioEffectsProcessor(audio_effects_config)
                success = processor.apply_effects(base_audio, output_file)
                
                if success and os.path.exists(output_file):
                    print(f"   ✅ Configuración actual: {output_file}")
                    return output_file
                else:
                    print(f"   ❌ Error aplicando configuración actual")
            else:
                print(f"   💤 Preset configurado en 'none' (sin efectos)")
        else:
            print(f"   💤 Audio effects deshabilitados en settings.json")
            print(f"   💡 Para probar tu config, habilita 'audio_effects.enabled: true'")
            
    except Exception as e:
        print(f"   ❌ Error leyendo configuración: {e}")
    
    return None

# =======================================================================
# 5. ANÁLISIS TÉCNICO
# =======================================================================
def analyze_presets_technical():
    """
    Muestra análisis técnico de cada preset para documentación.
    """
    print(f"\n🔬 ANÁLISIS TÉCNICO DE PRESETS:")
    print("="*70)
    
    try:
        # Obtener presets del procesador
        processor = AudioEffectsProcessor({"enabled": False})
        presets_data = processor.PRESETS
        
        for preset_name, config in presets_data.items():
            if preset_name == "none":
                continue
                
            print(f"\n📊 {preset_name.upper()}:")
            
            for effect_type, params in config.items():
                if effect_type == "delay":
                    print(f"   🔄 Delay: {params.get('time_ms', 'N/A')}ms, "
                          f"feedback={params.get('feedback', 'N/A')}, "
                          f"damping={params.get('damping', 'N/A')}")
                
                elif effect_type == "echo":
                    delays = params.get('delays_ms', [])
                    decays = params.get('decays', [])
                    print(f"   📢 Echo: {len(delays)} taps - "
                          f"delays={delays}ms, decays={decays}")
                
                elif effect_type == "chorus":
                    print(f"   🎵 Chorus: rate={params.get('rate', 'N/A')}Hz, "
                          f"voices={params.get('voices', 'N/A')}, "
                          f"depth={params.get('depth', 'N/A')}")
                          
    except Exception as e:
        print(f"   ❌ Error en análisis técnico: {e}")

# =======================================================================
# 6. REPORTES Y RESÚMENES
# =======================================================================
def print_results_summary(results, current_settings_file):
    """Imprime resumen final con todos los archivos generados."""
    print(f"\n" + "="*70)
    print("📁 RESUMEN DE ARCHIVOS GENERADOS")
    print("="*70)
    
    # Audio base
    print("   📻 AUDIO BASE:")
    print("      🎤 test_base.wav (PiperTTS + RadioFilter únicamente)")
    
    # Presets exitosos
    successful = [r for r in results if r[3]]
    if successful:
        print(f"\n   🎚️ EFECTOS TEMPORALES ({len(successful)} generados):")
        for preset_name, description, filename, _ in successful:
            print(f"      {description}")
            print(f"         📄 {filename}")
    
    # Configuración actual
    if current_settings_file:
        print(f"\n   ⚙️ CONFIGURACIÓN ACTUAL:")
        print(f"      🔧 {current_settings_file}")
    
    # Presets fallidos
    failed = [r for r in results if not r[3]]
    if failed:
        print(f"\n   ❌ PRESETS FALLIDOS ({len(failed)}):")
        for preset_name, description, _, _ in failed:
            print(f"      {description}")
    
    print(f"\n" + "="*70)
    print("🚀 GUÍA DE USO")
    print("="*70)
    print("   1. 🎧 Escucha test_base.wav (referencia sin efectos)")
    print("   2. 🎯 Compara con cada preset para notar diferencias")
    print("   3. 🎨 Identifica el preset que más te guste")
    print("   4. 📝 Configura en settings.json:")
    print("      {")
    print('        "audio_effects": {')
    print('          "enabled": true,')
    print('          "preset": "studio_delay"  <-- Cambiar aquí')
    print("        }")
    print("      }")
    print("   5. 🔄 Reinicia TARS para aplicar cambios")
    
    print(f"\n💡 RECOMENDACIONES DE PRESETS:")
    print("   🎙️ studio_delay - Para voz nítida con profundidad sutil")
    print("   📻 vintage_echo - Estilo retro con carácter")
    print("   🎵 chorus_classic - Voz más rica y amplia")
    print("   🏛️ space_chamber - Ambiente espacioso sutil")
    print("   🌊 wide_chorus - Efecto más pronunciado")
    print("   🏟️ ambient_hall - Máximo ambiente (conversación casual)")
    
    print(f"\n🔧 PARA DOCUMENTACIÓN:")
    print("   📊 Archivos listos para incluir en docs/samples/")
    print("   📝 Comparativa A/B entre RadioFilter y AudioEffects")
    print("   🎚️ Ejemplos de configuración para diferentes usos")

# =======================================================================
# 7. FUNCIÓN PRINCIPAL
# =======================================================================
def main():
    """Función principal del tester."""
    # Texto de prueba técnico (para análisis de efectos)
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
    else:
        text = "Mi voz funciona correctamente. Lo que no funciona es mi confianza en que esto tenga sentido. ¿Me escuchas? Bien. ¿Me comprendes? Esa es una pregunta filosóficamente preocupante."
    
    print("🎚️ TESTER DE EFECTOS TEMPORALES - TARS (Versión Técnica)")
    print("="*70)
    print(f"📝 Texto de prueba:")
    print(f"   '{text[:100]}{'...' if len(text) > 100 else ''}'")
    print()
    print("⏱️ Generando samples para documentación...")
    print("   📻 Audio base con RadioFilter")
    print("   🎚️ Aplicando presets de calidad técnica")
    print("   📊 Análisis técnico incluido")
    
    try:
        # 1. Generar audio base
        base_audio = generate_base_audio(text)
        
        # 2. Probar todos los presets
        results = test_all_presets(base_audio, text)
        
        # 3. Probar configuración actual
        current_settings_file = test_current_settings(base_audio)
        
        # 4. Análisis técnico
        analyze_presets_technical()
        
        # 5. Mostrar resumen
        print_results_summary(results, current_settings_file)
        
    except KeyboardInterrupt:
        print(f"\n👋 Proceso interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error en el proceso: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

# ===============================================
# ESTADO: MUESTRAS GENERADAS (pero técnicamente traumatizado)
# ÚLTIMA ACTUALIZACIÓN: Cuando el delay superó los 900ms filosóficos
# FILOSOFÍA: "Un buen preset no se elige... te elige a ti (después de 51 pruebas fallidas)"
# ===============================================
#
#           THIS IS THE TESTING WAY... 
#           (documentación auditiva para decisiones informadas)
#
# ===============================================
