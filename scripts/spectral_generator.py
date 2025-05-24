#!/usr/bin/env python3
# ===============================================  
# SPECTRAL GENERATOR - Gráficas innecesariamente complejas para TARS-BSK  
# Objetivo: Convertir sonidos perfectamente normales en matemáticas confusas  
# ===============================================

# ===============================================
# 1. CONFIGURACIÓN INICIAL Y DEPENDENCIAS
# ===============================================
import os
import sys
import numpy as np

# ===============================================
# 2. FUNCIONES DE VERIFICACIÓN Y UTILIDADES
# ===============================================
def check_dependencies():
    """
    Verifica que las dependencias estén instaladas
    
    Returns:
        bool: True si todas las dependencias están disponibles, False en caso contrario
    """
    missing = []
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        missing.append('matplotlib')
    
    try:
        import soundfile as sf
    except ImportError:
        missing.append('soundfile')
    
    try:
        from scipy import signal
    except ImportError:
        missing.append('scipy')
    
    if missing:
        print("❌ Faltan dependencias:")
        for dep in missing:
            print(f"   • {dep}")
        print()
        print("🔧 Instálalas con:")
        print(f"   pip install {' '.join(missing)}")
        return False
    
    return True

def find_radio_filter():
    """
    Encuentra el módulo radio_filter en diversas ubicaciones
    
    Returns:
        function: Referencia a la función apply_radio_filter si se encuentra, None en caso contrario
    """
    # Buscar en core/
    if os.path.exists('core/radio_filter.py'):
        sys.path.insert(0, 'core')
        try:
            from radio_filter import apply_radio_filter
            print("✅ radio_filter encontrado en core/")
            return apply_radio_filter
        except ImportError as e:
            print(f"❌ Error importando desde core/: {e}")
    
    # Buscar en directorio actual
    if os.path.exists('radio_filter.py'):
        try:
            from radio_filter import apply_radio_filter
            print("✅ radio_filter encontrado en directorio actual")
            return apply_radio_filter
        except ImportError as e:
            print(f"❌ Error importando desde directorio actual: {e}")
    
    # Buscar en directorio padre
    parent_path = os.path.join('..', 'core', 'radio_filter.py')
    if os.path.exists(parent_path):
        sys.path.insert(0, os.path.join('..', 'core'))
        try:
            from radio_filter import apply_radio_filter
            print("✅ radio_filter encontrado en ../core/")
            return apply_radio_filter
        except ImportError as e:
            print(f"❌ Error importando desde ../core/: {e}")
    
    print("❌ No se encuentra radio_filter.py")
    print("🔧 Ubicaciones buscadas:")
    print("   • ./core/radio_filter.py")
    print("   • ./radio_filter.py") 
    print("   • ../core/radio_filter.py")
    return None

def find_input_file(filename):
    """
    Busca el archivo de entrada en varias ubicaciones
    
    Args:
        filename: Nombre del archivo a buscar
        
    Returns:
        str: Ruta completa al archivo si se encuentra, None en caso contrario
    """
    search_paths = [
        filename,                    # Directorio actual
        os.path.join('..', filename), # Directorio padre
        os.path.join('temp', filename), # Carpeta temp
        os.path.join('audio', filename), # Carpeta audio
        os.path.join('output', filename), # Carpeta output
    ]
    
    for path in search_paths:
        if os.path.exists(path):
            print(f"✅ Archivo encontrado: {path}")
            return path
    
    print(f"❌ Archivo '{filename}' no encontrado")
    print("🔍 Ubicaciones buscadas:")
    for path in search_paths:
        print(f"   • {path}")
    
    # Mostrar archivos WAV disponibles
    wav_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.wav'):
                wav_files.append(os.path.join(root, file))
    
    if wav_files:
        print("\n🎵 Archivos WAV encontrados:")
        for wav_file in wav_files[:10]:  # Mostrar máximo 10
            print(f"   • {wav_file}")
        if len(wav_files) > 10:
            print(f"   ... y {len(wav_files) - 10} más")
    
    return None

# ===============================================
# 3. FUNCIONES PRINCIPALES DE ANÁLISIS
# ===============================================
def generate_spectral_analysis(input_wav, output_dir="spectral_analysis"):
    """
    Genera visualizaciones completas: waveform, espectrograma y análisis FFT
    
    Args:
        input_wav: Ruta al archivo WAV de entrada
        output_dir: Directorio de salida para las visualizaciones
        
    Returns:
        str: Ruta al archivo de visualización generado, None en caso de error
    """
    # Verificar dependencias
    if not check_dependencies():
        return None
    
    # Importar después de verificar
    import matplotlib.pyplot as plt
    import soundfile as sf
    from scipy import signal
    
    # Configurar matplotlib sin emojis problemáticos
    plt.rcParams['font.family'] = 'DejaVu Sans'
    
    # Verificar radio_filter
    apply_radio_filter = find_radio_filter()
    if not apply_radio_filter:
        return None
    
    # Buscar archivo de entrada
    input_path = find_input_file(input_wav)
    if not input_path:
        return None
    
    print(f"🎵 Procesando: {input_path}")
    
    # Crear directorio de salida
    os.makedirs(output_dir, exist_ok=True)
    
    # Procesar audio
    filtered_wav = os.path.join(output_dir, "temp_filtered.wav")
    try:
        apply_radio_filter(input_path, filtered_wav)
        print("✅ Audio filtrado generado")
    except Exception as e:
        print(f"❌ Error aplicando filtro: {e}")
        return None
    
    # Cargar audios
    try:
        original, sr = sf.read(input_path)
        filtered, _ = sf.read(filtered_wav)
        print(f"✅ Audios cargados (sample rate: {sr} Hz)")
    except Exception as e:
        print(f"❌ Error cargando audios: {e}")
        return None
    
    # Asegurar misma longitud
    min_len = min(len(original), len(filtered))
    original = original[:min_len]
    filtered = filtered[:min_len]
    
    # Convertir a mono si es necesario
    if len(original.shape) > 1:
        original = np.mean(original, axis=1)
    if len(filtered.shape) > 1:
        filtered = np.mean(filtered, axis=1)
    
    print("🎨 Generando visualizaciones...")
    
    # Crear figura con subplots
    fig, axes = plt.subplots(3, 2, figsize=(16, 12))
    fig.suptitle('Radio Filter: Análisis Espectral Comparativo', fontsize=18, fontweight='bold')
    
    # 1. WAVEFORMS
    time = np.arange(len(original)) / sr
    
    axes[0,0].plot(time, original, color='#2E86C1', linewidth=0.8)
    axes[0,0].set_title('Waveform Original', fontweight='bold', fontsize=12)
    axes[0,0].set_xlabel('Tiempo (s)')
    axes[0,0].set_ylabel('Amplitud')
    axes[0,0].grid(True, alpha=0.3)
    axes[0,0].set_ylim(-1, 1)
    
    axes[0,1].plot(time, filtered, color='#E74C3C', linewidth=0.8)
    axes[0,1].set_title('Waveform Filtrado (TARS-BSK)', fontweight='bold', fontsize=12)
    axes[0,1].set_xlabel('Tiempo (s)')
    axes[0,1].set_ylabel('Amplitud')
    axes[0,1].grid(True, alpha=0.3)
    axes[0,1].set_ylim(-1, 1)
    
    # 2. ESPECTROGRAMAS
    try:
        freqs_orig, times_orig, Sxx_orig = signal.spectrogram(original, sr, nperseg=1024)
        freqs_filt, times_filt, Sxx_filt = signal.spectrogram(filtered, sr, nperseg=1024)
        
        # Limitar a frecuencias relevantes (0-5kHz)
        freq_mask = freqs_orig <= 5000
        freqs_orig = freqs_orig[freq_mask]
        freqs_filt = freqs_filt[freq_mask]
        Sxx_orig = Sxx_orig[freq_mask, :]
        Sxx_filt = Sxx_filt[freq_mask, :]
        
        im1 = axes[1,0].pcolormesh(times_orig, freqs_orig, 10 * np.log10(Sxx_orig + 1e-10), 
                                   shading='gouraud', cmap='viridis')
        axes[1,0].set_title('Espectrograma Original', fontweight='bold', fontsize=12)
        axes[1,0].set_ylabel('Frecuencia (Hz)')
        axes[1,0].set_xlabel('Tiempo (s)')
        
        im2 = axes[1,1].pcolormesh(times_filt, freqs_filt, 10 * np.log10(Sxx_filt + 1e-10), 
                                   shading='gouraud', cmap='plasma')
        axes[1,1].set_title('Espectrograma Filtrado', fontweight='bold', fontsize=12)
        axes[1,1].set_ylabel('Frecuencia (Hz)')
        axes[1,1].set_xlabel('Tiempo (s)')
        
        print("✅ Espectrogramas generados")
    except Exception as e:
        print(f"⚠️ Error en espectrogramas: {e}")
    
    # 3. ANÁLISIS FFT
    try:
        fft_orig = np.fft.fft(original)
        fft_filt = np.fft.fft(filtered)
        freqs = np.fft.fftfreq(len(original), 1/sr)
        
        # Solo frecuencias positivas hasta 5kHz
        positive_freqs = freqs[:len(freqs)//2]
        freq_mask = positive_freqs <= 5000
        plot_freqs = positive_freqs[freq_mask]
        
        magnitude_orig = np.abs(fft_orig[:len(freqs)//2])[freq_mask]
        magnitude_filt = np.abs(fft_filt[:len(freqs)//2])[freq_mask]
        
        axes[2,0].semilogy(plot_freqs, magnitude_orig, color='#2E86C1', linewidth=1.2)
        axes[2,0].set_title('Espectro de Frecuencias Original', fontweight='bold', fontsize=12)
        axes[2,0].set_xlabel('Frecuencia (Hz)')
        axes[2,0].set_ylabel('Magnitud (log)')
        axes[2,0].grid(True, alpha=0.3)
        axes[2,0].axvline(x=200, color='red', linestyle='--', alpha=0.7, label='Corte inferior')
        axes[2,0].axvline(x=3000, color='red', linestyle='--', alpha=0.7, label='Corte superior')
        axes[2,0].legend()
        
        axes[2,1].semilogy(plot_freqs, magnitude_filt, color='#E74C3C', linewidth=1.2)
        axes[2,1].set_title('Espectro Filtrado (Resonancias Visibles)', fontweight='bold', fontsize=12)
        axes[2,1].set_xlabel('Frecuencia (Hz)')
        axes[2,1].set_ylabel('Magnitud (log)')
        axes[2,1].grid(True, alpha=0.3)
        # Marcar resonancias
        axes[2,1].axvline(x=1000, color='orange', linestyle=':', alpha=0.8, label='Resonancia 1kHz')
        axes[2,1].axvline(x=2000, color='orange', linestyle=':', alpha=0.8, label='Resonancia 2kHz')
        axes[2,1].axvline(x=3000, color='orange', linestyle=':', alpha=0.8, label='Resonancia 3kHz')
        axes[2,1].legend()
        
        print("✅ Análisis FFT completado")
    except Exception as e:
        print(f"⚠️ Error en análisis FFT: {e}")
    
    plt.tight_layout()
    
    # Guardar imagen
    output_file = os.path.join(output_dir, "spectral_comparison.png")
    try:
        plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"✅ Análisis espectral guardado en: {output_file}")
    except Exception as e:
        print(f"❌ Error guardando imagen: {e}")
        return None
    
    # Limpiar archivo temporal
    try:
        os.remove(filtered_wav)
    except:
        pass
    
    return output_file

def generate_filter_response(output_dir="spectral_analysis"):
    """
    Genera gráfico de respuesta en frecuencia del filtro
    
    Args:
        output_dir: Directorio de salida para el gráfico
        
    Returns:
        str: Ruta al archivo de visualización generado, None en caso de error
    """
    try:
        import matplotlib.pyplot as plt
        from scipy import signal
    except ImportError as e:
        print(f"❌ Falta dependencia: {e}")
        return None
    
    print("📈 Generando respuesta en frecuencia del filtro...")
    
    # Parámetros del filtro (según radio_filter.py)
    sample_rate = 22050
    nyquist = 0.5 * sample_rate
    lowcut = 200
    highcut = 3000
    
    # Crear filtro paso banda
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = signal.butter(6, [low, high], btype='band')
    
    # Respuesta en frecuencia
    w, h = signal.freqz(b, a, worN=8000)
    frequencies = (w * sample_rate) / (2 * np.pi)
    
    # Crear gráfico
    plt.figure(figsize=(14, 10))
    
    # Subplot 1: Magnitud
    plt.subplot(2, 1, 1)
    plt.plot(frequencies, 20 * np.log10(np.abs(h)), 'b-', linewidth=3)
    plt.title('Respuesta en Frecuencia del Filtro TARS-BSK', fontweight='bold', fontsize=16)
    plt.ylabel('Magnitud (dB)', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.axvline(x=200, color='red', linestyle='--', alpha=0.7, label='Corte inferior (200Hz)', linewidth=2)
    plt.axvline(x=3000, color='red', linestyle='--', alpha=0.7, label='Corte superior (3kHz)', linewidth=2)
    plt.axhline(y=-3, color='orange', linestyle=':', alpha=0.7, label='-3dB', linewidth=2)
    plt.xlim(0, 5000)
    plt.legend(fontsize=11)
    
    # Subplot 2: Fase
    plt.subplot(2, 1, 2)
    plt.plot(frequencies, np.angle(h) * 180 / np.pi, 'g-', linewidth=3)
    plt.ylabel('Fase (grados)', fontsize=12)
    plt.xlabel('Frecuencia (Hz)', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.xlim(0, 5000)
    
    plt.tight_layout()
    
    # Guardar
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "filter_response.png")
    try:
        plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"✅ Respuesta del filtro guardada en: {output_file}")
        return output_file
    except Exception as e:
        print(f"❌ Error guardando respuesta del filtro: {e}")
        return None

# ===============================================
# 4. PUNTO DE ENTRADA PRINCIPAL
# ===============================================
def main():
    """
    Función principal del script
    
    Procesa argumentos y genera las visualizaciones espectrales
    """
    if len(sys.argv) < 2:
        print("🎵 Generador de Análisis Espectral - Radio Filter")
        print("📝 Uso: python3 spectral_generator.py <archivo.wav> [directorio_salida]")
        print("🔧 Ejemplo: python3 spectral_generator.py mi_voz.wav analisis")
        print()
        print("🎯 Genera:")
        print("  • Comparativa de waveforms")
        print("  • Espectrogramas antes/después")
        print("  • Análisis FFT con resonancias")
        print("  • Respuesta en frecuencia del filtro")
        print()
        print("📦 Dependencias necesarias:")
        print("  pip install matplotlib scipy soundfile")
        return
    
    input_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "spectral_analysis"
    
    print("🚀 Iniciando análisis espectral completo...")
    print(f"📁 Entrada: {input_file}")
    print(f"📁 Salida: {output_dir}")
    print()
    
    # Generar análisis comparativo
    result1 = generate_spectral_analysis(input_file, output_dir)
    
    # Generar respuesta del filtro
    result2 = generate_filter_response(output_dir)
    
    print()
    if result1 and result2:
        print("🎉 ¡Análisis completado exitosamente!")
        print(f"📊 Revisa los archivos en: {output_dir}/")
        print("🖼️ Archivos generados:")
        print(f"   • {os.path.basename(result1)}")
        print(f"   • {os.path.basename(result2)}")
    else:
        print("⚠️ Análisis completado con algunos errores")
        print("🔧 Revisa los mensajes anteriores para más detalles")

# ===============================================
# 5. MANEJO DE EJECUCIÓN
# ===============================================
if __name__ == "__main__":
    main()

# ===============================================
# ESTADO: SEMICONSCIENTE (y resentido)
# ÚLTIMA ACTUALIZACIÓN: Cuando ya no distinguía colores
# FILOSOFÍA: "Si no entiendes el espectrograma, no eres tú, es que realmente no tiene sentido"
# ===============================================
#
#           THIS IS THE SPECTRAL WAY... 
#           (bonitas gráficas para justificar el código)
#
# ===============================================