# ===============================================  
# RADIO FILTER - Procesamiento de Audio Mandaloriano para TARS-BSK  
# Objetivo: Arruinar meticulosamente cualquier rastro de fidelidad que tuviera el audio  
# Dependencias: SciPy, NumPy, y paciencia para aguantar mis comentarios  
# ===============================================

# =======================================================================
# 1. IMPORTACIONES Y CONFIGURACIÓN
# =======================================================================

import scipy.signal
import soundfile as sf
import numpy as np
import os
import random
import time
import logging
logger = logging.getLogger("TARS.RadioFilter")

# =======================================================================
# 2. FUNCIONES DE PROCESAMIENTO DE AUDIO
# =======================================================================

def apply_radio_filter(input_wav_path: str, output_wav_path: str = None, 
                       lowcut: int = 200, highcut: int = 3000, 
                       add_noise: bool = True, noise_level: float = 0.002,
                       add_compression: bool = True,
                       mando_effect: bool = True) -> None:
    """
    Applies a radio-style filter to a WAV file with Mandalorian helmet effect.

    Args:
        input_wav_path: Path to the input WAV file.
        output_wav_path: Path to save the filtered WAV file (overwrites input if None).
        lowcut: Lower frequency cutoff for bandpass (Hz).
        highcut: Upper frequency cutoff for bandpass (Hz).
        add_noise: Whether to add subtle noise to simulate radio transmission.
        noise_level: Level of noise to add (0.0 to 0.1 recommended).
        add_compression: Whether to apply dynamic range compression.
        mando_effect: Whether to add Mandalorian helmet resonance effect.
    """
    # =======================================================================
    # 2.1 CARGA Y PREPARACIÓN DEL AUDIO
    # =======================================================================
    start_time = time.time()

    if not os.path.exists(input_wav_path):
        raise FileNotFoundError(f"Input file not found: {input_wav_path}")

    # Load audio
    audio, sample_rate = sf.read(input_wav_path)
    
    # Convert to mono if stereo
    if len(audio.shape) > 1 and audio.shape[1] > 1:
        audio = np.mean(audio, axis=1)
    
    # Normalize audio before processing
    # NOTA: Esta normalización asegura que trabajemos con un rango consistente
    # pero mantiene la dinámica relativa del audio original
    max_amplitude = np.max(np.abs(audio))
    if max_amplitude > 0:
        audio = audio / max_amplitude * 0.9  # Leave some headroom
    
    # =======================================================================
    # 2.2 APLICACIÓN DE FILTROS DE FRECUENCIA
    # =======================================================================
    
    # Design bandpass filter
    # NOTA: Orden 6 es bastante agresivo y puede causar resonancias no deseadas
    # Considerar reducir a orden 4 para un filtrado más suave
    nyquist = 0.5 * sample_rate
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = scipy.signal.butter(6, [low, high], btype='band')
    
    # Apply filter with zero-phase to evitar distorsión de fase
    filtered_audio = scipy.signal.filtfilt(b, a, audio)
    
    # =======================================================================
    # 2.3 EFECTOS ESPECIALES DE AUDIO (MANDALORIAN)
    # =======================================================================
    
    # Add Mandalorian helmet resonance effect
    if mando_effect:
        # Primary helmet resonance (~ 2kHz)
        # NOTA: Un Q=10 es alto y crea una resonancia fuerte - exactamente lo que queremos
        # para un efecto de casco Mandaloriano convincente
        b_metal1, a_metal1 = scipy.signal.iirpeak(2000 / nyquist, Q=12)  # Aumentado a Q=12 para más resonancia
        filtered_audio = scipy.signal.lfilter(b_metal1, a_metal1, filtered_audio)
        
        # Secondary helmet resonance (~ 1kHz) - gives depth
        b_metal2, a_metal2 = scipy.signal.iirpeak(1000 / nyquist, Q=10)  # Aumentado a Q=10 para más efecto
        filtered_audio = scipy.signal.lfilter(b_metal2, a_metal2, filtered_audio)
        
        # Añadir una tercera resonancia más alta para simular la reverberación metálica (~ 3kHz)
        b_metal3, a_metal3 = scipy.signal.iirpeak(3000 / nyquist, Q=8)
        filtered_audio = scipy.signal.lfilter(b_metal3, a_metal3, filtered_audio)
        
        # Add echo/reverb effect for helmet cavity simulation
        # Utilizamos múltiples ecos para simular mejor la reverberación dentro del casco
        
        # Primer eco (corto/cercano) - simula rebote frontal del casco
        echo_delay1 = int(sample_rate * 0.015)  # 15ms delay
        echo_signal1 = np.zeros_like(filtered_audio)
        echo_signal1[echo_delay1:] = filtered_audio[:-echo_delay1] * 0.25  # Eco más pronunciado
        
        # Segundo eco (medio) - simula rebote lateral del casco
        echo_delay2 = int(sample_rate * 0.03)  # 30ms delay
        echo_signal2 = np.zeros_like(filtered_audio)
        echo_signal2[echo_delay2:] = filtered_audio[:-echo_delay2] * 0.15
        
        # Tercer eco (más largo) - simula reverberación general del casco
        echo_delay3 = int(sample_rate * 0.05)  # 50ms delay
        echo_signal3 = np.zeros_like(filtered_audio)
        echo_signal3[echo_delay3:] = filtered_audio[:-echo_delay3] * 0.1
        
        # Mezclamos todos los ecos
        filtered_audio = filtered_audio + echo_signal1 + echo_signal2 + echo_signal3
        
        # Normalización inteligente: preservamos la saturación controlada que da carácter
        # pero evitamos la distorsión digital destructiva
        max_after_echo = np.max(np.abs(filtered_audio))
        if max_after_echo > 1.0:  # Solo normalizamos si realmente hay clipping digital
            filtered_audio = filtered_audio / max_after_echo * 0.98  # Permitimos que se acerque más al límite
    
    # =======================================================================
    # 2.4 ADICIÓN DE RUIDO Y DISTORSIONES
    # =======================================================================
    
    # Add subtle noise to simulate radio transmission
    if add_noise and noise_level > 0:
        # Use colored noise (more low frequency content)
        white_noise = np.random.normal(0, noise_level, filtered_audio.shape)
        
        # Apply lowpass filter to create colored noise (más realista que ruido blanco)
        b_noise, a_noise = scipy.signal.butter(2, 0.3, btype='low')
        colored_noise = scipy.signal.lfilter(b_noise, a_noise, white_noise)
        
        # Add occasional crackling (like radio interference)
        # Aumentamos el efecto de interferencia para un sonido más auténtico de casco/radio
        crackle_points = np.random.random(filtered_audio.shape) > 0.995
        colored_noise[crackle_points] = colored_noise[crackle_points] * 6.0  # Más pronunciado
        
        # Añadir interferencias periódicas simulando problemas de transmisión
        t = np.arange(len(filtered_audio)) / sample_rate
        interference = 0.003 * np.sin(2 * np.pi * 0.2 * t)  # Interferencia periódica lenta
        interference = interference * (1 + 0.5 * np.sin(2 * np.pi * 2.5 * t))  # Modulación
        colored_noise = colored_noise + interference
        
        # Añadimos el ruido al audio filtrado
        # PUNTO DE SATURACIÓN POTENCIAL: Sumamos directamente sin comprobar niveles
        filtered_audio = filtered_audio + colored_noise
        
        # Añadir control de nivel después de añadir ruido
        max_after_noise = np.max(np.abs(filtered_audio))
        if max_after_noise > 0.95:
            filtered_audio = filtered_audio / max_after_noise * 0.95
    
    # =======================================================================
    # 2.5 COMPRESIÓN Y EFECTOS FINALES
    # =======================================================================
        
    # Apply dynamic range compression if requested
    if add_compression:
        # Mandalorian-style compression 
        # NOTA: Estos parámetros son intencionalmente agresivos para conseguir
        # el carácter de comunicación de casco característico
        threshold = 0.2      # Umbral bajo - comprime gran parte de la señal para dar consistencia
        ratio = 4.0          # 6.0Ratio alto - compresión agresiva típica de sistemas de comunicación
        makeup_gain = 1.6    # 1.8 Ganancia alta que da ese carácter "apretado" y presente
        
        # Este tipo de compresión agresiva es parte del carácter de la voz de Mandaloriano
        # y otros efectos de comunicación por radio militar
        
        # Apply compression
        mask = np.abs(filtered_audio) > threshold
        filtered_audio[mask] = np.sign(filtered_audio[mask]) * (
            threshold + (np.abs(filtered_audio[mask]) - threshold) / ratio
        )
        
        # Apply makeup gain
        # PUNTO DE SATURACIÓN CRÍTICO: Esta ganancia de 1.8 casi garantiza saturación
        filtered_audio = filtered_audio * makeup_gain
        
        # Ensure we don't clip
        # Esta comprobación evita la saturación digital pero el sonido ya estará distorsionado
        if np.max(np.abs(filtered_audio)) > 1.0:
            filtered_audio = filtered_audio / np.max(np.abs(filtered_audio)) * 0.95
            
    # Add AM radio effect con características de transmisión de casco
    # Esta modulación simula la variación de señal característica 
    # de sistemas de comunicación con interferencias
    t = np.arange(len(filtered_audio)) / sample_rate
    
    # Modulación principal (más pronunciada para efecto de casco)
    am_effect = 1.0 + 0.05 * np.sin(2 * np.pi * 0.5 * t)  # Aumentado a 0.05
    
    # Añadir fluctuaciones rápidas aleatorias para simular microfluctuaciones electrónicas
    random_fluctuations = 1.0 + 0.02 * np.random.randn(len(filtered_audio))
    # Suavizamos las fluctuaciones para que no sean demasiado abruptas
    b_smooth, a_smooth = scipy.signal.butter(1, 0.002)
    random_fluctuations = scipy.signal.filtfilt(b_smooth, a_smooth, random_fluctuations)
    
    # Combinamos ambos efectos
    combined_effect = am_effect * random_fluctuations
    filtered_audio = filtered_audio * combined_effect
    
    # Add occasional transmission "drop-outs" (very subtle)
    dropout_mask = np.random.random(filtered_audio.shape) > 0.997
    filtered_audio[dropout_mask] = filtered_audio[dropout_mask] * 0.5
    
    # Normalización final "inteligente" para preservar el carácter pero evitar distorsión digital
    # Aplicamos una ligera compresión suave final para mantener el carácter
    # pero evitar picos que causen distorsión digital destructiva
    
    # Soft clipper para una saturación controlada (da más carácter de casco)
    # Esta función permite que los picos se compriman gradualmente en lugar de recortarse bruscamente
    def soft_clip(x, threshold=0.8, hardness=3):
        y = x.copy()
        mask = np.abs(y) > threshold
        y[mask] = np.sign(y[mask]) * (threshold + (1 - threshold) * 
                                    np.tanh(hardness * ((np.abs(y[mask]) - threshold) / (1 - threshold))))
        return y
    
    # Aplicamos soft clipping para saturación controlada (más carácter)
    filtered_audio = soft_clip(filtered_audio, threshold=0.85, hardness=4)
    
    # Normalización final sólo si es absolutamente necesario
    max_final = np.max(np.abs(filtered_audio))
    if max_final > 1.0:  # Sólo normalizamos si hay verdadero clipping digital
        filtered_audio = filtered_audio / max_final * 0.99  # Dejamos que llegue casi al límite
    
    end_time = time.time()
    logger.info(f"🕒 Tiempo de procesamiento de filtro Mandaloriano: {end_time - start_time:.3f}s")
        
    # =======================================================================
    # 2.6 GUARDADO DEL AUDIO PROCESADO
    # =======================================================================
    
    # Save filtered audio
    output_path = output_wav_path or input_wav_path
    sf.write(output_path, filtered_audio, sample_rate)

# ===============================================
# ESTADO: ACÚSTICAMENTE PERTURBADO (pero funcional)
# ÚLTIMA ACTUALIZACIÓN: Cuando dejé de escuchar frecuencias por encima de 3kHz
# FILOSOFÍA: "Si no suena como un casco con problemas de autoestima, no está bien filtrado"
# ===============================================
#
#           THIS IS THE RADIO WAY... 
#           (distorsión controlada para justificar el trauma auditivo)
#
# ===============================================
    