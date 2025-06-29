#!/bin/bash
# ===============================================
# ADVERTENCIA FILOSÓFICA: Este script es funcionalmente competente (sí, sorprende)
# pero carece del drama existencial necesario para documentación completa.
#  
# Con desapego digital,  
# TARS-BSK declina responsabilidad emocional sobre su simplicidad.
# ===============================================

# ----------------------------
# 0. VALIDACIÓN DE ENTORNO
# ----------------------------
echo "🔍 Verificando entorno..."
if ! grep -q "Raspberry Pi" /proc/cpuinfo; then
  echo "⚠️ Este sistema no parece ser una Raspberry Pi. Abortando instalación."
  exit 1
fi

ARCHITECTURE=$(uname -m)
if [[ "$ARCHITECTURE" != "aarch64" ]]; then
  echo "⚠️ La arquitectura no es 64-bit. Usa Raspberry Pi OS Lite (64-bit)."
  exit 1
fi

if [[ -z "$VIRTUAL_ENV" ]]; then
  echo "❌ Este script debe ejecutarse dentro del entorno virtual (tars_venv)."
  echo "👉 Ejecuta: source ~/tars_venv/bin/activate"
  exit 1
fi

# ----------------------------
# 1. DEPENDENCIAS DEL SISTEMA
# ----------------------------
echo "🔧 Instalando dependencias base..."
sudo apt update && sudo apt install -y \
  portaudio19-dev \
  libasound2-dev \
  python3-gpiozero \
  alsa-utils \
  ffmpeg \
  libsndfile1 \
  git \
  tree

# ----------------------------
# 2. DEPENDENCIAS PYTHON (Venv)
# ----------------------------
echo "📦 Instalando dependencias Python..."
pip install --no-cache-dir \
  sounddevice \
  soundfile \
  simpleaudio \
  numpy \
  vosk \
  onnxruntime \
  gpiozero \
  noisereduce \
  psutil \
  pydub \
  colorama \
  python-Levenshtein \
  jellyfish \
  schedule \
  shortuuid \
  dateparser \
  tqdm \
  scikit-learn \
  librosa \
  matplotlib

# ----------------------------
# 3. CONFIGURACIÓN GPIO
# ----------------------------
echo "⚙️ Configurando backend GPIO..."
cat << 'EOF' > ~/tars_venv/gpio_backend.py
from gpiozero import Device
try:
    from gpiozero.pins.lgpio import LGPIOFactory
    Device.pin_factory = LGPIOFactory()
    print("✅ Backend GPIO configurado: lgpio")
except Exception as e:
    print(f"⚠️ Fallo con lgpio: {str(e)}")
    from gpiozero.pins.rpigpio import RPiGPIOFactory
    Device.pin_factory = RPiGPIOFactory()
    print("✅ Backend GPIO configurado: rpigpio (fallback)")
EOF

# ----------------------------
# 4. VERIFICACIÓN FINAL
# ----------------------------
echo "✅ Instalación completada. Verificando backend GPIO..."
python ~/tars_venv/gpio_backend.py
echo "🚀 Listo para el siguiente paso del camino."

# ===============================================
# $ git log --format="%h %s" -1 [current_file]  
# deadbeef chore: Update [current_file] (survived again)  
# $ git blame --porcelain [current_file] | grep "exist"  
# fatal: No existential commits found
# ===============================================