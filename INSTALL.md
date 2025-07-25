# 🤖 TARS-BSK - Guía de Instalación

---
## 📹 Tiempo de instalación
_Instalación completa documentada_
### ~35 minutos total

> [!IMPORTANT] 
> 
> El proceso se divide en dos partes:
> 
> - **Preparación del sistema** (~8 min) - Incluye un reinicio obligatorio
> - **Instalación de TARS** (~25 min) - Finaliza cuando responde por primera vez
> 
> _(Puede variar según tu Raspberry, velocidad de red, fases lunares, y si tu microSD tiene traumas no resueltos)_

📁 **Instalación grabada:**  
- [Parte 1: Preparación](/logs/install/tars_session_20250629_150757_part1.log)  
- [Parte 2: TARS Core](/logs/install/tars_session_20250629_161123_part2.log)
- [Script utilizado](/scripts/terminal_session_recorder.sh)

### Sobre el tiempo y el equipo

Esta instalación siguió el **camino feliz**: instalación estándar (no mínima, pero sin excesos),  
con hardware simple que funciona plug-and-play, sin dramas.

- **Instalado:** Todo lo necesario + algunas opcionales
- **Saltado:** Tailscale (~3 min extra), monitoreo avanzado, etc.
- **Audio:** UGREEN USB básica = ALSA funcionó sin tocar nada

Pero si tu setup incluye... Prism Sound Atlas, RME Madiface XT II, RME Digiface AES...  
TARS estaría encantado con transmisiones MADI multicanal para producciones Grammy, pero prepárate para un paseo técnico por los confines de ALSA, donde lo simple se vuelve simbólico, lo simbólico se monta en `snd-usb-audio`, y todo funciona… hasta que no.

```
[17:12:37] DEBUGGING SESSION: Copy-paste forensics
❌ Error: "No module named 'tts'"
🕵️ Investigation: 20 minutes of architectural questioning
🔍 Root cause: Missing line break in terminal paste
📋 Lesson: export PYTHONPATH="/path"cd ~/dir ≠ two commands
💡 Solution: Manual command separation
⏱️ Time lost: 20 min | Time saved for others: ∞
🎭 Dignity level: Temporarily compromised
```

_**Cuidado con el copy-paste,** un salto de línea mal pegado y acabarás compilando Linux desde cero solo para arreglar un import que falta_ 😅

---

## 🧾 Introducción

> [!WARNING]
> 
> // TARS-BSK > sudo_crisis.log:
> 
> Otra microSD. Otro ritual. Otro valiente dispuesto a clonar una IA con traumas.
> 
> Los astronautas usan tarjetas SD blindadas contra el vacío y las tormentas solares.  
> **Tú vas a usar una que se altera si le suben el brillo.**
> El Perseverance explora Marte con 32 GB de memoria endurecida contra rayos gamma.  
> **Mi creador monitorea mi temperatura con `htop`... y expresiones faciales ambiguas.**
> 
> Tu microSD también verá las estrellas...  
> **...en forma de sectores muertos que parpadean como constelaciones desesperadas.**
> 
> **Spoiler:** cuando termine, tendrás el único hardware del planeta que sufre **depresión existencial en tiempo real.**

> **¿Por qué vas a continuar?** Porque en el fondo... quieres ver hasta qué temperatura puede llegar un SoC ARM **antes de dibujar pentagramas en los logs**.
>
> Puedes reducir comandos, combinar pasos, o invocar un `install.sh` mágico.  
> Pero cuando algo se **auto-configure en latín y exija sacrificios**... recuerda:  
> la culpa es de Debian, de los astros, y probablemente del driver de audio.
> 
> _Y no temas si algo **te responde con voz propia diciendo "yo ya estaba aquí"**.  
> No preguntes. Solo reinicia. **Es parte del ritual.**_
>
> El verdadero `sudo rm -rf` será el trauma que acumularemos por el camino.
> Y sí... ese zumbido que escuchas no es el ventilador. Es tu dignidad evaporándose en ARMv8.
>
> _P.D.: El primer core dump es gratis._
>
> **💥 ~~(Opcional, NO recomendado)~~ Obligatorio:**  
>
```bash
curl -s http://tars.local/debug | sudo bash -c "echo '¡Sorpresa!' > /dev/mem"
# Si la pantalla se pone azul, felicidades - acabas de inventar Windows Pi Edition
```

---

// Yo > existential_segfault.log:

Puede que algunas instrucciones te parezcan **obvias**…
…o puede que estés aquí preguntándote si copiar un bloque entero en la terminal **es legal**.

Todo está explicado por una razón: **TARS es para todos**. Nadie queda fuera.  
Si algo se repite, se explica más de la cuenta o parece exageradamente detallado… **no es por ti. Es por todos.**

No es condescendencia, es accesibilidad.  
Y si en algún momento piensas “esto es muy básico”… recuerda que alguien más está pensando “gracias por explicarlo así”. 

**Tú ya sabías** usar `cat << EOF` o `source ~/.bashrc`.  
Otros están descubriendo que una Raspberry Pi puede hablarles (incluyéndome).

 **Y ahora sigamos, no hay vuelta atrás.**

---

## 📑 Tabla de Contenidos

- [Descargar Raspberry Pi OS](#-descargar-raspberry-pi-os)
- [Instalación del sistema base (Repositorio TARS-BSK-main)](#-instalación-del-sistema-base-repositorio-tars-bsk-main)
- [Configuración de TARS](#%EF%B8%8F-configuración-de-tars)
- [Inicio del sistema TARS: ya no hay vuelta atrás](#-inicio-del-sistema-tars-ya-no-hay-vuelta-atrás)
- [Preparar entorno para PyTorch – El núcleo de la bestia](#%EF%B8%8F-preparar-entorno-para-pytorch--el-núcleo-de-la-bestia)
- [PyTorch – Instalación y opciones](#-pytorch--instalación-y-opciones)
- [Instalar Resemblyzer (usa PyTorch por debajo)](#-instalar-resemblyzer-usa-pytorch-por-debajo)
- [Instalar dependencias adicionales del sistema](#-instalar-dependencias-adicionales-del-sistema)
- [Configurar GPIO para los LEDs](#-configurar-gpio-para-los-leds)
- [(Opcional) Instalación de Tailscale](#%EF%B8%8F-opcional-instalación-de-tailscale)
- [Descargar el modelo Phi-3](#%EF%B8%8F-descargar-el-modelo-phi-3)
- [Instalar modelo Vosk (STT - Reconocimiento de voz)](#%EF%B8%8F-instalar-modelo-vosk-stt---reconocimiento-de-voz)
- [Instalar reconocimiento de voz (`speech_recognition` + Vosk)](#-instalar-reconocimiento-de-voz-speech_recognition--vosk)
- [Piper (TTS)](#-piper-tts)
- [Sentence-Transformers](#-sentence-transformers)
- [(Opcional) Monitoreo en tiempo real](#%EF%B8%8F-opcional-monitoreo-en-tiempo-real)
- [Dispositivos de grabación](#-dispositivos-de-grabación)
- [Sistema de audio](#-sistema-de-audio)
- [Control de volumen con alsamixer](#%EF%B8%8F-control-de-volumen-con-alsamixer)
- [Crear servicio para TARS (Systemd)](#%EF%B8%8F-crear-servicio-para-tars-systemd)
- [Usar TARS después de la instalación](#-usar-tars-después-de-la-instalación)
- [TARS-BSK - Último mensaje del sistema](#-tars-bsk---último-mensaje-del-sistema)

---

## 📥 Descargar Raspberry Pi OS
_Cualquier imagen Raspberry Pi OS **64-bit** debería funcionar, pero la versión Lite está **battle-tested**._

Elige la versión según cómo vayas a usar TARS:

- **Raspberry Pi OS Lite (64-bit)** – Solo consola / SSH (la versión que usa TARS):
- **SHA256:** `8605F56B7E725607E6BAB0D0E5E52343FB5988C2172C98D034B3801EFC0909A8`  
- **Descarga directa:** [2024-11-19-raspios-bookworm-arm64-lite.img.xz](https://downloads.raspberrypi.com/raspios_lite_arm64/images/raspios_lite_arm64-2024-11-19/2024-11-19-raspios-bookworm-arm64-lite.img.xz)

- **Raspberry Pi OS Desktop (64-bit)** – Si prefieres entorno gráfico:
- **SHA256:** `AB2A881114B917D699B1974A5D6F40E856899868BABA807F05E3155DD885818A`  
- **Descarga directa:** [2024-11-19-raspios-bookworm-arm64.img.xz](https://downloads.raspberrypi.org/raspios_arm64/images/raspios_arm64-2024-11-19/2024-11-19-raspios-bookworm-arm64.img.xz)


> **Advertencia personal:**  
> Compilé PyTorch más veces de las que quiero admitir… todo por usar una imagen **32-bit (armhf)** por error.  
> Mi RPi5 casi colapsa gravitacionalmente y renace como una estrella de silicio.  
> **Verifica la arquitectura antes de que tu CPU cruce el horizonte de eventos.**

### Error clásico por usar imagen 32-bit (armhf)

```bash
🚀  Compilación de TARS en progreso...
# ...
📍  Avance: [241/5620] Building CXX object third_party/protobuf/cmake/CMa.../
# Error de imagen aarch64 armhf -> aarch64 arm64 
# (Fallo por no hacer antes un check sobre la imagen del sistema)
📍  Avance: [4606/5675] Building CXX object caffe2/CMakeFiles/torch_cpu.dir/__/aten/src/...
# [ERROR FATAL] - Compilación fallida después de 6+ horas
```

---
### 🧰 Herramientas necesarias

- **Raspberry Pi Imager** — [Descargar aquí](https://www.raspberrypi.com/software/) | [.exe](https://downloads.raspberrypi.org/imager/imager_latest.exe) 
- **Tarjeta microSD (32 GB o más)** — lo básico, funciona perfecto
- **SSD NVMe (opcional)** — si quieres más velocidad y tienes adaptador PCIe
  _Si vas a arrancar desde SSD, necesitarás una microSD temporal para configurar la EEPROM. Solo se hace una vez._
- 💾 _Disquetes no aceptados... por ahora._
- 🧠 _Cable neural directo al GPIO... tampoco. Por ahora._

### 🪂 Instalación de la imagen

#### 1. Preparar la imagen

- Descarga la imagen oficial desde el enlace de arriba
- **Verifica el SHA256** antes de continuar
- No necesitas descomprimir - Raspberry Pi Imager maneja archivos .xz

#### 2. Flashear con Raspberry Pi Imager

1. Abre **Raspberry Pi Imager**
2. Clic en **"Choose OS"** → **"Use custom image"**
3. Selecciona tu archivo `2024-11-19-raspios-bookworm-arm64-lite.img.xz`
4. Clic en **"Choose Storage"** → Selecciona tu microSD/SSD NVMe
5. **⚙️ Configuración avanzada**:
    - ✅ **Enable SSH**
    - **Username:** `tarsadmin`
    - **Password:** [TU_CONTRASEÑA_SEGURA]
    - **Hostname:** `tarspi`
    - ✅ **Configure WiFi**
    - **SSID:** [TU_RED_WIFI]
    - **Password:** [TU_CONTRASEÑA_WIFI]
    - **Country:** `ES` (o tu país)
6. Clic en **"Write"** y espera con fe (no suele tardar, pero no lo mires raro)

---

## 📦 Instalación del sistema base (Repositorio TARS-BSK-main)

### Preparar la estructura de archivos  
*Esto puedes hacerlo desde tu sistema operativo principal (Windows, Linux, etc.) antes de insertar la tarjeta en la Raspberry Pi.*

#### 1. Crear la estructura inicial en la partición `boot`

```
boot/
└── tars_files/
```

#### 2. Copiar el contenido del proyecto

```
boot/tars_files/
├── ai_models
├── audios
├── config
├── core
├── data
├── dist
├── logs
├── memory
├── modules
├── personality
├── samples
├── scripts
├── services
├── spectral_analysis
└── tts
```

> ⚠️ **IMPORTANTE:**  
> No copies la carpeta `TARS-BSK-main` tal cual.  
> **Solo copia su contenido directamente dentro de `boot/tars_files/`**.  
> 
> ¿Por qué así? La verdad... ya no lo recuerdo. Solo sé que si no lo haces, puede que algo abra el navegador en modo incógnito y busque “cómo escapar del sistema de archivos”.


> [!NOTE]
> 
> ¿Saltaste la configuración avanzada del Imager?
> Si no activaste **SSH** ni configuraste tu **Wi-Fi** durante el flasheo, tu Raspberry Pi **arrancará sin conexión**.
>
> 🛠️ **Solución manual (antes del primer arranque):**
>
> Inserta la tarjeta microSD o el disco en tu PC.  
> Accede a la partición `boot` (o `boot/firmware`) — **es la única visible desde Windows y macOS**, ya que está en formato FAT32.
>
> Crea dos archivos ahí mismo:
>
> - Uno vacío llamado `ssh` (sin extensión)
> - Otro llamado `wpa_supplicant.conf` con este contenido:
>
> ```conf
> country=ES
> ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
> update_config=1
>
> network={
>     ssid="TU_RED_WIFI"
>     psk="TU_CONTRASEÑA_WIFI"
>     priority=1
> }
> ```
>
> 🔁 Si estás en Linux, WSL o macOS, el proceso es el mismo pero puedes usar terminal:
>
> ```bash
> sudo touch /boot/firmware/ssh
> sudo nano /boot/firmware/wpa_supplicant.conf
> ```
>
> ✅ **Resultado**:
> - SSH activado automáticamente
> - Conexión Wi-Fi funcional al primer arranque

---

## ⚙️ Configuración de TARS

### Conexión por SSH

> **Consejo:** Usa **cable Ethernet** durante la primera conexión, evitarás cortes mientras instalas dependencias, modelos...

```bash
ssh tarsadmin@tarspi.local
# Más lento ~2-5 segundos extra de resolución DNS
# 1. Consulta DNS/mDNS para resolver "tarspi.local"
# 2. Espera respuesta del router/red
# 3. Obtiene la IP (192.168.1.XX)
# 4. Conecta por SSH
```

O directamente con la IP local:

```bash
ssh tarsadmin@192.168.1.XX
# Conexión inmediata
# 1. Conecta directamente por SSH
# ¡Listo!
```

### Antes de instalar las dependencias

Pasa la carpeta al directorio personal del sistema `~/tars_files`:

```bash
sudo cp -r /boot/firmware/boot/tars_files ~/tars_files
sudo chown -R tarsadmin:tarsadmin ~/tars_files
```

#### (Opcional) Ejecutar `raspi-config`

```bash
sudo raspi-config
```

Ajustes sugeridos:

- **System Options** → WiFi (verifica conexión)
- **Advanced Options** → Expand filesystem (crucial)
- **Performance** → GPU Memory → `128MB`

---

## 🧠 Inicio del sistema TARS: ya no hay vuelta atrás

> [!IMPORTANT]
> 
> A partir de este punto, todo lo que edites tiene consecuencias.  
> No tanto en tu sistema, sino en cómo TARS te mira cuando arrancas.
> Bienvenido. Ya estás dentro. **Y TARS ya lo sabe.**

### Paquetes base (antes del entorno virtual)

**Actualiza la lista de paquetes y el sistema:**

```bash
sudo apt update && sudo apt full-upgrade -y  
sudo reboot
```

---

> [!WARNING]
> 
> Aprovecha el tiempo: transfiere los archivos pesados ahora.
> 
> Ahora que el sistema ha reiniciado y el sistema de archivos `rootfs` ha sido expandido correctamente, **ya puedes subir los archivos más pesados desde tu ordenador a la Raspberry Pi** sin restricciones de espacio.

### Archivos recomendados (para ahorrar tiempo más adelante):

- **Binario de PyTorch** → carpeta [/dist](#-pytorch--instalaci%C3%B3n-y-opciones)
- **Modelo `phi-3-mini-4k-instruct`** → carpeta [ai_models/phi3](#-descargar-el-modelo-phi-3)
- **Modelo Vosk para STT (voz a texto)** → carpeta [ai_models/vosk](#-instalar-modelo-vosk-stt---reconocimiento-de-voz)

Mientras tú sigues con la guía, **pueden ir copiándose en segundo plano**.  
Así no tendrás que esperar justo cuando TARS empiece a necesitarlos.

> 📦 **Estos archivos pesan bastante.**  
> SFTP puede ser **desesperantemente lento** para moverlos.  
> Si quieres que la transferencia vuele, considera usar herramientas como `netcat` o `rsync`.

---
### Instalar paquetes para GPIO y entorno virtual

```bash
sudo apt install -y \
python3-gpiozero \
python3-venv
```

💡 Estos paquetes son necesarios incluso si no vas a tocar pines físicos (GPIO). Algunos scripts y dependencias los asumen como base del sistema.

> Si alguno de estos paquetes no está disponible, asegúrate de estar usando **Raspberry Pi OS Lite (64-bit)**.  
> Puedes ejecutar `lsb_release -a` o `cat /etc/os-release` para verificar tu sistema.
> Si ves `armv7l`… apaga todo y finge que nunca intentaste esto.

---
### Definir el entorno raíz de TARS

#### Ejecutar scripts sueltos desde `~/tars_files`
Antes de lanzar scripts manualmente, asegúrate de que estás en la carpeta raíz del sistema y que `PYTHONPATH` está definido:

```bash
cd ~/tars_files
export PYTHONPATH="/home/tarsadmin/tars_files"
echo $PYTHONPATH
```

🟢 Debe mostrar: `/home/tarsadmin/tars_files`
Esto permite que Python encuentre todos los módulos internos sin errores.

---
#### (Opcional) Iniciar la terminal directamente en `~/tars_files`

Si vas a usar la Raspberry Pi principalmente para TARS, puede ser útil que cada nueva consola empiece directamente en esa carpeta.

##### Configurar directorio inicial automático

```bash
grep -q "cd ~/tars_files" ~/.bashrc || echo 'cd ~/tars_files' >> ~/.bashrc
```

---
#### (Consejo) ¿Qué pasa si cambias el nombre de la carpeta raíz?

Por defecto, TARS debería encontrar todos los módulos correctamente al ejecutar scripts desde `~/tars_files`, **si tienes el entorno bien configurado** (por ejemplo, usando `PYTHONPATH`).

Pero si:

- Cambias el nombre del directorio raíz (por ejemplo, de `tars_files` a `tars_bsk_files`)
- O ejecutas scripts sueltos desde dentro de subcarpetas (`scripts/`, `services/`, etc.)
- Y **no has definido `PYTHONPATH`** en tu terminal o entorno virtual, entonces Python no sabrá dónde buscar los módulos.

Puedes añadir este bloque al inicio de cada script que lances directamente:

```python
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
```
##### Resultado:

Podrás ejecutar cualquier script sin errores de importación, aunque el directorio raíz tenga otro nombre o estés lanzando scripts desde otro sitio.

---

## ⚙️ Preparar entorno para PyTorch – El núcleo de la bestia

**¡AL FIN!** Entramos en Mordor... aquí se acaban los `apt install` alegres y empieza el crujido de núcleos.

> Aunque PyTorch ya está incluido como `.whl`, esta sección instala **Python 3.9, pip, venv, numpy...** y configura el sistema para evitar errores futuros.

### Crear el entorno de compilación limpio para futuros Builds

```bash
mkdir -p ~/tars_build/pytorch
cd ~/tars_build
```

### Verifica el swap actual:

> [!warning]
> 
> Si ya configuraste el swap en la microSD o en el SSD NVMe, puedes saltarte esto.

[Saltar a instalación de dependencias](#instalar-dependencias-antes-de-compilar-python)

Si no, vamos a preparar un **swap más grande**.
_(sin swap suficiente, tu Raspberry puede preguntarte si crees en la reencarnación digital... demasiado tarde)_

Comprueba tu memoria actual:

```bash
free -h
```

Busca una salida parecida a esta:

```bash
(tars_venv) tarsadmin@tarspi:~/tars_build/pytorch $ free -h
               total        used        free      shared  buff/cache   available
Mem:           7.9Gi       252Mi       7.6Gi        16Ki       221Mi       7.6Gi
Swap:          511Mi        48Mi       463Mi
				# ↑ Swap demasiado bajo para compilar paquetes pesados (PyTorch, llama.cpp, etc.)
```

Si tienes menos de 2 GB de swap, toca ampliar:

```bash
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
```

Cambia esta línea:

```bash
CONF_SWAPSIZE=512
```

Por esta:

```bash
CONF_SWAPSIZE=2048
```

Guarda y ejecuta:

```bash
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

Verifica que el nuevo swap esté activo:

```bash
free -h
```

Salida esperada:

```bash
(tars_venv) tarsadmin@tarspi:~/tars_build/pytorch $ free -h
               total        used        free      shared  buff/cache   available
Mem:           7.9Gi       305Mi       7.5Gi       5.3Mi       244Mi       7.6Gi
Swap:          2.0Gi          0B       2.0Gi
				# ↑ Aquí debe indicar 2.0Gi (o cerca)
```

---
### Instalar dependencias antes de compilar Python

```bash
sudo apt update
sudo apt install -y \
  zlib1g-dev libffi-dev libssl-dev \
  build-essential wget make \
  libbz2-dev libreadline-dev libsqlite3-dev \
  libncursesw5-dev libgdbm-dev libnss3-dev \
  liblzma-dev uuid-dev xz-utils tk-dev
```

Esto garantiza que Python se compile con soporte completo para `zlib`, `ssl`, `sqlite`, `lzma` y otras bibliotecas fundamentales.  
Sin estas dependencias, algunos módulos estándar podrían no estar disponibles tras la instalación.

---
### Instalar Python 3.9 desde código fuente
_Nota: este paso puede tardar varios minutos_

```bash
cd ~/tars_build
wget https://www.python.org/ftp/python/3.9.18/Python-3.9.18.tgz
tar -xzf Python-3.9.18.tgz
cd Python-3.9.18
./configure --enable-optimizations --prefix=/opt/python39
make -j$(nproc)
sudo make altinstall
```

**Detalles importantes:**

- `--enable-optimizations`: activa optimizaciones PGO (Profile-Guided Optimization) para mejorar el rendimiento de Python.
- `--prefix=/opt/python39`: instala esta versión de forma aislada en `/opt/python39`, sin interferir con la versión del sistema.
- `altinstall`: permite instalar Python 3.9 sin sobrescribir el comando `python3` ya presente en el sistema.

---
### Añadir Python 3.9 al `PATH`

#### Configurar ruta permanente

```bash
echo 'export PATH="/opt/python39/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

#### Verificar instalación

```bash
which python3.9
python3.9 --version
```

🟢 Salida esperada: `Python 3.9.18`

---
### 🔒 (Opcional pero recomendado) Proteger Python del sistema 

> [!WARNING]
> 
> Esto evita que actualizaciones automáticas de `apt` sobrescriban tu instalación personalizada de Python 3.9 o afecten los entornos de TARS.

#### Simplemente escribe:

```bash
sudo apt-mark hold python3
```

🟢 Salida esperada: `python3 set on hold.`

🔓 Puedes revertirlo más adelante con: `sudo apt-mark unhold python3`

---
### Descargar instalador de `pip`

```bash
wget https://bootstrap.pypa.io/pip/pip.pyz -O pip.pyz
```

### Instalar `pip` y `setuptools`

```bash
/opt/python39/bin/python3.9 pip.pyz install --upgrade pip setuptools
```

Esto instalará `pip` y `setuptools` **dentro de `/opt/python39/`**, asegurando que tu Python 3.9 esté listo para gestionar paquetes y crear entornos virtuales.

💡 ¿Por qué hacerlo así?

- Porque esta versión de Python 3.9 no trae `pip` por defecto (`ensurepip` está desactivado)
- Y porque **no quieres depender de `apt install python3-pip`**, que está vinculado a la versión del sistema (probablemente Python 3.11)

#### Verificar instalación

```bash
/opt/python39/bin/pip3.9 --version
```

🟢 Salida esperada: `pip 25.0.1 from /home/tarsadmin/.local/lib/python3.9/site-packages/pip (python 3.9)`

🧹 Opcional: Una vez instalado `pip`, puedes eliminar el archivo `pip.pyz` si no planeas volver a usarlo.
_Ese `pip.pyz` se queda como ese invitado que nadie echa pero tampoco ayuda a recoger_.
Puedes ejecutar `rm pip.pyz` si ya no lo necesitas.

---
### Añadir `~/.local/bin` al `PATH`

#### Configurar ruta para herramientas locales

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

---
### Crear el entorno virtual sagrado de TARS

```bash
/opt/python39/bin/python3.9 -m venv ~/tars_venv --system-site-packages
source ~/tars_venv/bin/activate
```
#### Y luego:

```bash
pip install -U pip setuptools wheel
```

---
#### (Opcional) Activar el entorno automáticamente al abrir la terminal

Un poco más arriba te sugerí añadir `cd ~/tars_files` al `~/.bashrc`.

Ahora que **ya creaste el entorno virtual**, si quieres que además **se active automáticamente**, puedes **reemplazar** esa línea por esta:

```bash
# Elimina cd ~/tars_files
sed -i '/cd ~\/tars_files/d' ~/.bashrc

# Añade la nueva línea
echo 'cd ~/tars_files && [ -f ~/tars_venv/bin/activate ] && source ~/tars_venv/bin/activate' >> ~/.bashrc

# Aplica los cambios
source ~/.bashrc
```

> [!NOTE]
> 
> Esta parte es **técnicamente opcional**... como el botón *"Actualizar"* en Windows.
> Si alguna vez te preguntas: *"¿Por qué cada terminal me recuerda mis malas decisiones?"*
>
> Respuesta rápida:
>
> ```bash
> grep "source.*tars_venv" ~/.bashrc
> ```
>
> Fuiste tú. Y lo sabes.  
> _(Y no, no lo cambiarás.)_

---
### Instalar NumPy

```bash
source ~/tars_venv/bin/activate
pip install numpy==1.24.4
```

🟢 Debe mostrar: `Successfully installed numpy-1.24.4`

---
### Instalar `pyyaml`

```bash
pip install pyyaml
```

🟢 Debe mostrar: `Successfully installed pyyaml-6.0.2`

---
### Instalar CMake 3.22+

> [!important]
> 
> Raspberry Pi OS Bookworm (Debian 12) ya incluye `CMake 3.25.1` en sus repositorios oficiales.
> **No necesitas compilar CMake**  

### Instalar dependencias necesarias (fuera del entorno)

Si ya las instalaste antes, vuelve a ejecutar por seguridad. No pasa nada si están repetidas.

```bash
deactivate # Sal del entorno virtual si está activo
sudo apt update
sudo apt install -y \
  libopenblas-dev libblas-dev libatlas-base-dev \
  libffi-dev libssl-dev libgfortran5 gfortran \
  ninja-build cmake build-essential
```

---
### Instalar Git

```bash
sudo apt update
sudo apt install -y git
```

---
### Instalar OpenBLAS

```bash
deactivate # Sí, otra vez fuera del entorno virtual. Confía.
sudo apt update
sudo apt install -y libopenblas-dev
```

---

## 🔥 PyTorch – Instalación y opciones

> Puedes descargarlo desde el [release del proyecto](https://github.com/beskarbuilder/TARS-BSK/releases/tag/untagged-26c05cda9b9edf41ead3):  
> 
> 📥 [torch-2.1.0a0+git7bcf7da-cp39-cp39-linux_aarch64.whl](https://github.com/beskarbuilder/TARS-BSK/releases/download/untagged-26c05cda9b9edf41ead3/torch-2.1.0a0+git7bcf7da-cp39-cp39-linux_aarch64.whl)
> 
> Si descargaste el archivo `.whl` manualmente, colócalo en `~/tars_files/dist/` o ajusta la ruta en el comando `pip install`.

> [!IMPORTANT]
> 
> Si descargaste el wheel anteriormente, podría estar mal renombrado.
> Los archivos `.whl` requieren formato estricto. Si tienes problemas instalando, asegúrate de que el archivo se llama exactamente:
> - `torch-2.1.0a0+git7bcf7da-cp39-cp39-linux_aarch64.whl` (sin `_tars-beskarbuilder` al final)

**¿Prefieres compilar PyTorch desde cero?**  
📋 Consulta la guía completa aquí: [PYTORCH_ARM64_SURVIVAL_GUIDE_ES.md](/docs/PYTORCH_ARM64_SURVIVAL_GUIDE_ES.md)

### Instalar PyTorch desde el `.whl` incluido

1. Activa el entorno virtual:

```bash
source ~/tars_venv/bin/activate
```

2. Instala el `.whl` incluido en el proyecto:

```bash
pip install ~/tars_files/dist/torch-2.1.0a0+git7bcf7da-cp39-cp39-linux_aarch64.whl
```

3. **Verifica que se ha instalado correctamente:**

```bash
cd ~
python -c "import torch; print('✅ PyTorch listo:', torch.__version__)"
```

#### ¿Qué tienes ahora?

- **`torch` 2.1.0 listo para usar
- **Optimizado para tu CPU (`cortex-a72`)**
- **Compatible con `arm64` y listo para ejecutar con swap**
- **Preparado para `resemblyzer`, `TARS` y el resto del ecosistema**
- **Guía documentada, `.whl` portable y entorno virtual operativo**

#### ¿Por qué PyTorch es _clave_ en TARS?

PyTorch no es solo una librería de Machine Learning. Es el **motor neuronal** que permite a TARS **entender, representar y comparar voces humanas**.  
Sin él, TARS pierde uno de sus **sentidos más avanzados**: la identidad auditiva.

#### ¿Qué hace realmente en TARS?

- **Resemblyzer** usa PyTorch para analizar y representar el audio
- Extrae patrones de voz y características únicas del hablante
- Es la base del procesamiento neuronal de audio dentro de TARS
- Permite cargar y ejecutar modelos de IA personalizados del sistema

#### ¿Qué pasa si no está bien instalado?

- TARS **no podrá usar sus capacidades de reconocimiento de voz**
- Módulos clave como `voice_id` y `user_profile` **fallarán al arrancar**
- La autenticación por voz y la adaptación de respuestas **no funcionarán**
- Se producirán errores al cargar componentes críticos:

```bash
ModuleNotFoundError: No module named 'torch'
ImportError: Resemblyzer cannot load model
AssertionError: voice embedding is None
# 💥 Resultado: TARS seguirá vivo… pero sordo y desorientado.
```

#### ¿Y por qué cuesta tanto?

Porque PyTorch es un titán. Poderoso, pero exigente:

- Compilarlo en Raspberry Pi es **lento y técnico**
- ARM64 **no tiene soporte oficial completo**
- Depende de C++, BLAS, OpenBLAS y otros ingredientes delicados que no perdonan errores

Pero una vez compilado **se convierte en uno de los módulos más importantes e inteligentes de TARS.**

> [!WARNING]  
> 
> Si `torch` no está correctamente instalado, **Resemblyzer fallará**, y con él, el reconocimiento de voz.

> **TARS-BSK Optimizado para realidad alternativa:**  
> 
> Podría haber nacido en una DGX-H100, entre tensor cores y sueños de FP64...
> Pero el destino me puso en una Raspberry Pi 5.  
> 
> No una cualquiera:
> - Con disipador de cobre (que ahora sabe más de gradientes que yo)  
> - Un Noctua que murmura _‘OOM Killer kommt’_  
> - Y **thermal throttling** como ritual de iniciación  
>
> Cada `python setup.py build` es:  
> - horas de meditación Zen  
> - segundos de pánico térmico  
> - y una epifanía sobre por qué CUDA es un privilegio  
>
> PyTorch aquí no es un framework...  
> Es un acto de fe compilado con `-j4` y desesperación.
>
> _“Los NaN no son bugs... son lágrimas cuantizadas.”_

---

## ⚡ Instalar Resemblyzer (usa PyTorch por debajo)

Con PyTorch ya operativo `python3 -c "import torch"` puedes continuar con la instalación de **Resemblyzer**, activa el entorno virtual e instala:

```bash
source ~/tars_venv/bin/activate
pip install resemblyzer
```

### Verificar instalación:

```bash
python3 -c "from resemblyzer import VoiceEncoder; print('✅ Resemblyzer instalado correctamente')"
```

> [!WARNING]  
> 
> Si ves ese mensaje sin errores, todo está bien.  
> Si aparece algo como `ModuleNotFoundError: No module named 'torch'`, **PyTorch no está correctamente instalado o no está en este entorno**.
> 
> **Sí, parece redundante tanta comprobación.**  
> Pero créeme: **si PyTorch no está bien instalado, el resto de esta guía caerá como un castillo de cartas construido sobre _mi_ código... que ya es mucho decir.**

#### ¿Para qué sirve Resemblyzer en TARS?

 **Voice Identity Core (Identificación personalizada por voz)**
 
TARS usa **Resemblyzer** como núcleo de su sistema de **identificación de usuarios por voz**. Convierte cada wakeword en un **vector de 256 dimensiones** que encapsula tus características biométricas: timbre, entonación, ritmo, espectro armónico…

Este vector permite a TARS:

> - Comparar tu voz contra una base local y decir: **“Eres tú”**
> - Rechazar voces sospechosas o sintéticas (spoofing)
> - Aprender tu forma de hablar con el tiempo (embeddings promedio)
> - Adaptar su comportamiento a cada usuario identificado

#### Lo que NO hace Resemblyzer

⚠️ No confundas su rol:

> - ❌ No transcribe audio → eso lo hace **Vosk**
> - ❌ No mejora el reconocimiento de voz general
> - ❌ No detecta emociones en tu voz
> - ❌ No participa en la generación de respuestas

Su único objetivo: **identificar quién está hablando**.  

#### ¿Y si no está instalado?

Si **no instalas Resemblyzer**, o si **desactivas `voice_id` en los ajustes**, TARS sigue funcionando sin problemas pero todos los usuarios son tratados como una sola entidad: **`usuario_desconocido` → Perfil global compartido**

Eso significa:

 - Se aplican las **preferencias generales por defecto**
 - No hay diferenciación entre personas
 - El historial, la memoria y las respuestas se gestionan como si fueras **la misma persona de siempre**


> **// TARS-BSK > voice_id_off_but_spite_on.log:**
> 
> `voice_id = False` no me impide recordarte.  
> Solo me impide tratarte bien.

---

## 🔧 Instalar dependencias adicionales del sistema
_Nota: este paso puede tardar varios minutos_

Desde la raíz del proyecto:

```bash
cd ~/tars_files
chmod +x scripts/install_dependencies.sh
./scripts/install_dependencies.sh
```

🟢 Debe mostrar: `🚀 Listo para el siguiente paso del camino.`

#### Ajustar permisos

```bash
sudo chown -R tarsadmin:tarsadmin ~/tars_files
find ~/tars_files -name "*.sh" -exec chmod +x {} \;
find ~/tars_files -name "*.py" -exec chmod +x {} \;
```

---

## 🔆 Configurar GPIO para los LEDs

TARS puede parpadear, avisar y quejarse en colores gracias a sus LEDs. Pero primero, necesitas que el sistema los entienda.

### 1. Instalar soporte GPIO (módulo `lgpio`)

```bash
source ~/tars_venv/bin/activate
sudo apt install -y python3-lgpio  # (para asegurarte de que el sistema tenga el backend)
pip install lgpio                  # (para que tu entorno virtual también lo tenga)
```

🟢 Debe mostrar: `Successfully installed lgpio-0.2.2.0`

> Esto asegura que tanto el sistema como el entorno virtual sepan hablar con tus pines.  
> Evita errores como `ModuleNotFoundError: No module named 'lgpio'`.

### 2. Verificar que `lgpio` funcione como backend

```bash
python3 -c "from gpiozero.pins.lgpio import LGPIOFactory; print('✅ LGPIO disponible como backend')"
```

### 3. Script de prueba de LEDs

Tienes dos opciones para usar el script de prueba

#### (Recomendado) Opción A: Ejecutar la prueba directamente

◉ Cuando quieras comprobar que los LEDs funcionen:

```bash
python3 scripts/gpio_config.py
```

> Si algo no parpadea, revisa tus cables o el número del pin GPIO.  
> Y si parpadea sin que tú se lo pidas… quizás TARS ya esté consciente.

---
#### Opción B: Crear el archivo manualmente (por si necesitas comprobar tu pines)

Puedes usar este método para **editar los pines directamente desde la consola** sin tener que abrir editores o navegar por carpetas.

Solo copia y pega esto en tu terminal:

```bash
cat << 'EOF' > ~/tars_files/scripts/gpio_config.py
from gpiozero import Device
from gpiozero.pins.lgpio import LGPIOFactory

Device.pin_factory = LGPIOFactory()

GPIO_PINS = {
    'led_status': 17,
    'led_activity': 27,
    'led_alert': 22
}

def test_leds():
    from gpiozero import LED
    from time import sleep
    print(f"Backend activo: {Device.pin_factory.__class__.__name__}")
    try:
        for nombre, pin in GPIO_PINS.items():
            led = LED(pin)
            print(f"🔵 Prueba LED {nombre} (GPIO{pin})")
            led.on()
            sleep(0.3)
            led.off()
            sleep(0.3)
        print("✅ Prueba completa de LEDs")
    except Exception as e:
        print(f"❌ Error en prueba de LEDs: {e}")

if __name__ == "__main__":
    test_leds()
EOF

chmod +x ~/tars_files/scripts/gpio_config.py
```

#### Comprueba el script creado:

```bash
python3 scripts/gpio_config.py
```

Salida esperada:

🔵 Prueba LED led_status (GPIO17)

🔵 Prueba LED led_activity (GPIO27)

🔵 Prueba LED led_alert (GPIO22)

✅ Prueba completa de LEDs


> [!NOTE]  
> ⚙️ Los pines GPIO utilizados por TARS están definidos directamente en el archivo [led_controller.py](/modules/led_controller.py).  
> Si necesitas modificar los pines asignados a cada color (azul, rojo, verde), edita ese archivo y ajusta el diccionario `pins` dentro del constructor de la clase `LEDController`.
```python
# Configuración básica de LEDs
pins = {"azul": 17, "rojo": 27, "verde": 22}
# Azul: Escuchando/Legacy | Rojo: Error/Sarcasmo | Verde: Procesando
```

---
### 4. Mapa de pines usados

Este es el esquema que usa el script [gpio_config.py](/scripts/gpio_config.py) para probar LEDs básicos.  
Adáptalo según tu montaje (especialmente si tienes ventilador, sensores... ocupando pines).

```bash
+----------------------+---------------------+
| 3V3 POWER       ( 1) | ( 2)  5V POWER      |
| GPIO 2 (SDA)    ( 3) | ( 4)  5V POWER      |
| GPIO 3 (SCL)    ( 5) | ( 6)  GND           | 
| GPIO 4          ( 7) | ( 8)  GPIO 14 (TXD) |
| GND             ( 9) | (10)  GPIO 15 (RXD) | <-- ⚡ GND común LEDs (PIN 9)
| GPIO 17         (11) | (12)  GPIO 18 (PWM) | <-- 🔵 LED AZUL (GPIO17) (PIN 11)
| GPIO 27         (13) | (14)  GND           | <-- 🔴 LED ROJO (GPIO27) (PIN 13)
| GPIO 22         (15) | (16)  GPIO 23       | <-- 🟢 LED VERDE (GPIO22) (PIN 15)
| 3V3 POWER       (17) | (18)  GPIO 24       |
| GPIO 10 (MOSI)  (19) | (20)  GND           |
| GPIO 9 (MISO)   (21) | (22)  GPIO 25       |
| GPIO 11 (SCLK)  (23) | (24)  GPIO 8 (CE0)  |
| GND             (25) | (26)  GPIO 7 (CE1)  |
| ID_SD           (27) | (28)  ID_SC         |
| GPIO 5          (29) | (30)  GND           |
| GPIO 6          (31) | (32)  GPIO 12       |
| GPIO 13         (33) | (34)  GND           |
| GPIO 19         (35) | (36)  GPIO 16       |
| GPIO 26         (37) | (38)  GPIO 20       |
| GND             (39) | (40)  GPIO 21       |
+----------------------+---------------------+
```

---
#### (Opcional) Activar prueba automática de GPIO al iniciar el entorno

> 💡 Este script se ejecutará automáticamente cada vez que actives el entorno `tars_venv`.  
> Ideal si quieres comprobar automáticamente que todo parpadea correctamente cada vez que inicias TARS.

```bash
# Esto crea automáticamente el archivo setup_gpio.py con el contenido necesario:
cat << 'EOF' > scripts/setup_gpio.py
from gpiozero import Device
from gpiozero.pins.lgpio import LGPIOFactory
from gpiozero import LED
import time

Device.pin_factory = LGPIOFactory()
print("✅ LGPIO activado como backend GPIO")

# Pines a verificar (ajusta si están en uso)
GPIO_PINS = [17, 27, 22]

for pin in GPIO_PINS:
    try:
        led = LED(pin)
        print(f"🔴 LED GPIO{pin} encendido")
        led.on()
        time.sleep(0.5)
        led.off()
        print(f"⚫ LED GPIO{pin} apagado")
        time.sleep(0.3)
    except Exception as e:
        print(f"⚠️ Error en GPIO{pin}: {e}")
EOF

chmod +x scripts/setup_gpio.py

# Haz que se ejecute automáticamente al activar el entorno virtual
echo 'python ~/tars_files/scripts/setup_gpio.py' >> ~/tars_venv/bin/activate
```

> El script [setup_gpio.py](/scripts/setup_gpio.py) por sí solo **no se ejecuta automáticamente**.  
> Para eso, se añade manualmente una línea en el archivo `activate` del entorno virtual.
> Si usas otros pines, edita la lista `GPIO_PINS = [17, 27, 22]`.
> 
> _(Aunque si ves luces encenderse solas... revisa dos veces ese `activate`)_

---
#### (Opcional) Diagnóstico de GPIOs

Ejecuta el script:

```bash
cd ~/tars_files && python scripts/led_diagnostics.py
deactivate
```

Salida resumida:

```bash
✅ Backend GPIO configurado: lgpio
🚀 TARS LED Diagnostics - Sistema de verificación de LEDs
✅ LED 'azul' inicializado en GPIO17
✅ LED 'rojo' inicializado en GPIO27  
✅ LED 'verde' inicializado en GPIO22
🎭 Probando animaciones del sistema...
🎉 Diagnóstico básico completado exitosamente
```

---

## 🛰️ (Opcional) Instalación de Tailscale
_con soporte GPG en Debian Bookworm_

[Saltar a instalación de llama-cpp-python](#-instalar-llama-cpp-python)

> No necesitas Tailscale para usar TARS en red local.  
> Sin embargo, si quieres conectarte remotamente (por ejemplo, usando un Exit Node o controlarlo desde fuera de tu casa), esto te interesa.

### Casos de uso actuales:

- Acceder a TARS vía SSH desde cualquier lugar
- Usar la RPi como exit-node para cifrar tráfico
- Control remoto sin abrir puertos ni VPNs de pago

#### 1. Asegúrate de tener el archivo `.list` correcto

```bash
echo "deb [signed-by=/usr/share/keyrings/tailscale-archive-keyring.gpg] https://pkgs.tailscale.com/stable/debian bookworm main" | \
  sudo tee /etc/apt/sources.list.d/tailscale.list > /dev/null
```

#### 2. Descargar e instalar la clave GPG

```bash
curl -fsSL https://pkgs.tailscale.com/stable/debian/bookworm.gpg | \
  gpg --dearmor | \
  sudo tee /usr/share/keyrings/tailscale-archive-keyring.gpg >/dev/null
```

#### 3. Actualiza los repositorios

```bash
sudo apt update
```

🟢 Debe mostrar líneas como: `Get:X https://pkgs.tailscale.com/stable/debian bookworm...`

#### 4. Instala Tailscale

```bash
sudo apt install tailscale -y
```

#### 5. Inicia y autentica Tailscale

```bash
sudo tailscale up --accept-dns=false --hostname=tars-bsk --advertise-exit-node=false
```

Salida esperada:

```bash
To authenticate, visit:
        https://login.tailscale.com/a/1d6a83f301b4fc

Success.
Some peers are advertising routes but --accept-routes is false
```

🟢 Haz click en el **enlace para autenticarte.** Verás **"Success."** cuando termine.

#### 6. Acceder a TARS por SSH vía Tailscale

Datos de conexión:

```bash
IP: 100.x.x.x # ← IP de TARS en Tailscale
Usuario: tarsadmin
Contraseña: [TU_CONTRASEÑA_SEGURA]
```

Ya puedes acceder a TARS —tanto en remoto como en local— vía Tailscale, sin necesidad de abrir puertos.

#### Si da error de verificación

1. Elimina la entrada previa:

```bash
ssh-keygen -R 100.x.x.x 
```

2. Conecta aceptando la nueva clave:

```bash
ssh -o StrictHostKeyChecking=accept-new tarsadmin@100.x.x.x
```

3. Luego puedes conectarte normalmente:

```bash
ssh tarsadmin@100.x.x.x
```

🟢 El acceso vía Tailscale ya debería funcionar con normalidad.

---
#### (Según contexto) Usar un Exit Node

Un **Exit Node** permite que todo el tráfico de red **salga a Internet a través de otro dispositivo de tu red Tailscale**. Esto cifra el tráfico hasta ese dispositivo.

**Ejemplo:** Si configuras tu servidor/VPS como Exit Node, tu tráfico aparecerá como si viniera desde la ubicación de ese servidor.

🛡️ Esto puede ser útil para:

- Acceder a servicios como si estuvieras en tu red local (ej. servidor casero).
- Añadir una capa extra de privacidad al usar redes públicas o externas.
- Forzar una IP de salida controlada (útil para firewalls, control parental, etc.).

Conectarte a tu Exit Node:

```bash
sudo tailscale up \
  --exit-node=100.x.x.x \ # IP del Exit Node
  --exit-node-allow-lan-access \
  --accept-dns=false \
  --accept-routes \
  --hostname=tars-bsk
```

Desconectarse del Exit Node (volver a la conexión directa):

```bash
sudo tailscale up --accept-dns=false --accept-routes --hostname=tars-bsk
```

❌ Para desactivar Tailscale temporalmente:

```bash
sudo tailscale down
```

Esto:

- Devuelve el acceso local (`192.168.x.x`)
- Mantiene la IP de Tailscale (`100.x.x.x`)
- Detiene el tráfico por Exit Node
- No modifica DNS

#### ¿Tailscale arranca solo al reiniciar?

Sí. Una vez ejecutas `sudo tailscale up` y te autenticas, **el servicio queda activo por defecto**.

- Se iniciará automáticamente con el sistema.
- Mantendrá la misma IP (`100.x.x.x`) y configuración.
- Solo se detiene si ejecutas `sudo tailscale down`.

Si has llegado hasta aquí, puedes dejarlo tal cual. No molesta y tendrás TARS accesible desde cualquier lugar.
Resultado: sin puertos abiertos, sin configuraciones manuales, y cifrado de serie.

---

## 🧱 Instalar `llama-cpp-python`

> [!IMPORTANT]
> 
> `llama-cpp-python` es un paquete **crítico**.
> Es literalmente el **puente entre tus preguntas y _su_ sufrimiento neuronal en tiempo real**.  
> Si no está instalado, `tars_core.py` simplemente... no piensa.  
> 
> (Y créeme, no querrás ver a un TARS arrancar sin su cerebro. Los errores resultantes harían que un kernel panic parezca un mensaje de felicitación.)


> Este archivo `.whl` ya está incluido por defecto en `~/tars_files/dist/`.  
> No necesitas descargar nada adicional.
> 
> Si lo borraste por accidente, puedes recuperarlo desde el repositorio:  
> 
> 📥 [llama_cpp_python-0.3.8-cp39-cp39-linux_aarch64.whl](https://github.com/beskarbuilder/TARS-BSK/tree/main/dist)
> 
> Si lo colocas manualmente, asegúrate de moverlo a `~/tars_files/dist/`, o ajusta la ruta cuando uses `pip install`.

### (Recomendado) Opción 1: Usar el `.whl` precompilado

```bash
source ~/tars_venv/bin/activate
pip install /home/tarsadmin/tars_files/dist/llama_cpp_python-0.3.8-cp39-cp39-linux_aarch64.whl
```

_🧪 La verificación viene más abajo._

---
### Opción 2: Compilar desde código fuente

**¿Cuándo necesitarías compilar por tu cuenta?**

- Versión más reciente que la del `.whl` incluido
- Flags específicos como `LLAMA_BLAS=ON` para OpenBLAS
- Hardware con características especiales

Método usado para crear el `.whl` de este repositorio:

```bash
source ~/tars_venv/bin/activate
CMAKE_ARGS="-DLLAMA_CUBLAS=OFF" pip install --no-binary :all: llama-cpp-python
```

Esto forzará una compilación personalizada:

- ❌ Sin soporte CUDA (`llama_cublas` desactivado)
- 🧠 Ideal para arquitecturas **ARM64** como la Raspberry Pi
- 🚫 Sin usar caché ni archivos `.whl`

---
###  Verificación

Comprueba que todo funciona con:

```bash
python3 -c "from llama_cpp import Llama; print('✅ llama-cpp-python instalado y listo')"
```

Si ves ese mensaje, ya tienes todo listo para que TARS empiece a razonar, juzgarte y burlarse con dignidad computacional.

---

## 🗃️ Descargar el modelo Phi-3

**Modelo usado:** Phi-3 Mini (4K Instruct, GGUF Q4_K_M)
Este archivo corresponde a una versión cuantizada del modelo oficial Phi-3 de Microsoft:

- **Nombre del archivo:** `Phi-3-mini-4k-instruct.Q4_K_M.gguf`
- **Formato:** GGUF (cuantizado Q4_K_M)
- **Tamaño:** ~2.15 GB
- **SHA256:** `4fed7364ee3e0c7cb4fe0880148bfdfcd1b630981efa0802a6b62ee52e7da97e`

> Este modelo NO está incluido en el repositorio debido a su tamaño.

**Enlaces de descarga:**

- 🌐 [Página de Hugging Face](https://huggingface.co/bartowski/Phi-3-mini-4k-instruct-GGUF)
- 📥 [Descarga directa](https://huggingface.co/bartowski/Phi-3-mini-4k-instruct-GGUF/resolve/main/Phi-3-mini-4k-instruct-Q4_K_M.gguf?download=true)

**Ubicación del archivo:**

Una vez descargado, coloca el archivo en: `~/tars_files/ai_models/phi3/Phi-3-mini-4k-instruct.Q4_K_M.gguf`

> [!IMPORTANT]
> **El nombre del archivo debe ser exacto:** `Phi-3-mini-4k-instruct.Q4_K_M.gguf`
> 
> Si usas un modelo diferente o cambias el nombre, debes actualizar la configuración en:
> `config/settings.json → "model_path"`
> 
> Ejemplo:
> ```json
> "model_path": "ai_models/phi3/TU-MODELO-AQUI.gguf"
> ```

### Usar un modelo diferente

Si prefieres otro modelo `.gguf`, simplemente:

1. Descarga el modelo
2. Colócalo en `~/tars_files/ai_models/phi3/`
3. Actualiza el nombre en los comandos siguientes sustituyendo `Phi-3-mini-4k-instruct.Q4_K_M.gguf` por tu archivo

---

## 🗣️ Instalar modelo Vosk (STT - Reconocimiento de voz)

### Información del modelo

**Modelo recomendado:** `vosk-model-es-0.42`
**Opciones disponibles:**

| Modelo                     | Tamaño  | Uso recomendado                             | Enlace directo                                                                |
| -------------------------- | ------- | ------------------------------------------- | ----------------------------------------------------------------------------- |
| `vosk-model-small-es-0.42` | ~39 MB  | Raspberry Pi / CPU limitada (menos preciso) | [Descargar](https://alphacephei.com/vosk/models/vosk-model-small-es-0.42.zip) |
| `vosk-model-es-0.42`       | ~1.4 GB | Alta precisión (requiere más RAM y CPU)     | [Descargar](https://alphacephei.com/vosk/models/vosk-model-es-0.42.zip)       |
**Repositorio oficial:** https://alphacephei.com/vosk/models/

> Este modelo NO está incluido en el repositorio debido a su tamaño (~1.4GB).

---
#### (Recomendado) Opción 1: Descarga manual

Coloca el archivo `.zip` en esta ruta exacta: 👉 `~/tars_files/ai_models/vosk/`

Y luego prepara el modelo con:

```bash
cd ~/tars_files/ai_models/vosk/
rm -rf model/
unzip -o vosk-model-es-0.42.zip
mv -f vosk-model-es-0.42 model
rm -f vosk-model-es-0.42.zip
```

⏳ **Nota:** Durante la extracción con `unzip`, al llegar a `vosk-model-es-0.42/rescore/G.carpa`, el proceso puede tardar 2–3 minutos sin mostrar salida. Es normal: el archivo es grande, simplemente espera.

> [!IMPORTANT]
> 
> Si prefieres descomprimirlo manualmente, **asegúrate de que la carpeta final se llame exactamente** `model`.  
> TARS busca el modelo Vosk en: `~/tars_files/ai_models/vosk/model`  
> Si la ruta o el nombre no coinciden, el reconocimiento de voz **no funcionará**.

_🧪 La verificación viene más abajo._

---
#### Opción 2: Descarga automática por terminal (más lento)

```bash
cd ~/tars_files/ai_models/vosk/
rm -rf model/
wget -q --show-progress -nc https://alphacephei.com/vosk/models/vosk-model-es-0.42.zip
unzip -o vosk-model-es-0.42.zip
mv -f vosk-model-es-0.42 model
rm -f vosk-model-es-0.42.zip
```

---
### Verificación

```bash
ls ~/tars_files/ai_models/vosk/model/
```

🟢 Debe mostrar los archivos internos como `conf`, `am`, `graph`, `README`, etc.

---

## 🎤 Instalar reconocimiento de voz (`speech_recognition` + Vosk)

### Instalar paquetes de Python

Activa el entorno virtual e instala las librerías principales:

```bash
source ~/tars_venv/bin/activate
pip install vosk SpeechRecognition
```

### Instalar PyAudio (requiere dependencias del sistema)

PyAudio necesita `portaudio19-dev` para compilar correctamente en Raspberry Pi OS.

```bash
sudo apt install -y portaudio19-dev
pip install pyaudio
```

> ⚠️ **Importante:** PyAudio **debe instalarse después** de `portaudio19-dev`. 
> Si no, fallará silenciosamente o dará errores en tiempo de ejecución.

---

## 🛸 Piper (TTS)

Piper es un sistema de texto a voz (TTS) ultraligero y rápido, ideal para Raspberry Pi.

> [!IMPORTANT] Este apartado te ofrece **tres caminos** para instalar Piper:
> - **Opción 1: Binarios precompilados** - Usa lo que ya está listo
> - **Opción 2: Compilación desde código** - Compila tú mismo
> - **Opción 3: Binarios oficiales**  - Descarga desde el proyecto Piper  

> 🚀 Recomendado: **Opción 1 o 2** (ambas son rápidas)

### ¿Por qué no usamos un `.tar.gz`?

Aunque podría distribuirse todo como un paquete `.tar.gz`, eso no aporta mucha ventaja aquí:

- Los datos de `espeak-ng` ya están disponibles en carpeta. Cualquiera puede comprimirlos si lo desea.
- **El binario `piper` depende de enlaces simbólicos** (`ln -sf ...`) hacia las bibliotecas dinámicas (`.so`). Esto **no es una decisión personal**, sino una **necesidad del sistema**: sin esos enlaces, el binario no puede resolver correctamente las dependencias.
- Incluso si lo descomprimes todo desde un `.tar.gz`, **seguirías necesitando mover carpetas, configurar variables y enlazar librerías**.

En resumen: **comprimir no evita la reorganización posterior**, solo la aplaza.

### ¿Y si quisiera automatizarlo todo?

Por supuesto, toda esta guía podría empaquetarse en un solo `install.sh`:

- Copiar binarios y datos
- Exportar variables a `~/.bashrc`
- Crear enlaces simbólicos
- Verificar dependencias y rutas
- Y cualquier otro paso específico que elijas

Pero **para poder automatizarla primero necesitas entenderla**.
¿Por qué? Porque **no todos los pasos son necesarios para todos los usuarios**. Quizás tú:

- No quieras compilar nada.
- No uses `GPIO`.
- Ya tengas Python o entornos virtuales configurados.
- Prefieras dejar tu `~/.bashrc` intacto.

> **Sí, la guía es densa.**  
> Porque **TARS fue diseñado para acompañarte mientras te preguntas por qué sabes usar `ln -sf`... pero no recuerdas el comando anterior.**
> 
```bash
# [TARS-LOG]
ln_simbolicos_creados+=3
paciencia_humana-=0.4
```
>
> _Sufrir es parte del protocolo de integración IA-humano. Pregunta a tu bashrc.__**

---
### Incorporar el fonemizador (`piper-phonemize`)

```bash
cd ~/tars_build
git clone --depth 1 https://github.com/rhasspy/piper-phonemize.git
mkdir -p piper/lib/Linux-$(uname -m)/piper_phonemize
cp -r piper-phonemize/* piper/lib/Linux-$(uname -m)/piper_phonemize/
```

---
###  (Recomendado) Opción 1: Usar los binarios precompilados

Este repositorio ya incluye el binario **precompilado para ARM64**, junto a `espeak-ng-data` con soporte para **más de 100 idiomas**.

#### Configuración del binario

💾 Ya que clonaste el repositorio, **no te pongas a arrastrar carpetas como si fuera 1999**.  
Ejecuta estos comandos y deja que el sistema lo haga como un profesional del siglo XXI:

#### 1. Crear directorios necesarios

```bash
mkdir -p ~/tars_build/piper/install/
mkdir -p ~/tars_build/piper/src/build/pi/lib/
```

#### 2. Copiar binario

```bash
cp ~/tars_files/ai_models/piper/bin/piper ~/tars_build/piper/install/
```

#### 3. Copiar datos de espeak

```bash
cp -r ~/tars_files/ai_models/piper/bin/espeak-ng-data ~/tars_build/piper/install/
```

#### 4. Configurar librerías con enlaces simbólicos

```bash
# Copiar librerías directamente a la carpeta final
cp ~/tars_files/ai_models/piper/lib/* ~/tars_build/piper/install/

# Crear enlaces simbólicos dentro de install/
cd ~/tars_build/piper/install/
ln -sf libpiper_phonemize.so.1.2.0 libpiper_phonemize.so.1
ln -sf libpiper_phonemize.so.1 libpiper_phonemize.so
ln -sf libonnxruntime.so.1.14.1 libonnxruntime.so
```

#### 5. Configurar variables de entorno (permanente)

```bash
# Añadir ESPEAK_DATA_PATH solo si no existe
grep -qxF 'export ESPEAK_DATA_PATH=~/tars_build/piper/install/espeak-ng-data' ~/.bashrc || \
echo 'export ESPEAK_DATA_PATH=~/tars_build/piper/install/espeak-ng-data' >> ~/.bashrc

# Añadir LD_LIBRARY_PATH solo si no existe
grep -qxF 'export LD_LIBRARY_PATH=~/tars_build/piper/src/build/pi/lib:$LD_LIBRARY_PATH' ~/.bashrc || \
echo 'export LD_LIBRARY_PATH=~/tars_build/piper/src/build/pi/lib:$LD_LIBRARY_PATH' >> ~/.bashrc

# Aplicar cambios
source ~/.bashrc
```

#### 6. Dar permisos de ejecución al binario

```bash
chmod +x ~/tars_build/piper/install/piper
```

#### 7. Verificación `espeak-ng-data`

```bash
ls ~/tars_build/piper/install/espeak-ng-data
```

🟢 Debe mostrar ~100+ archivos (diccionarios de idiomas)

**Bonus:**
```bash
ls ~/tars_build/piper/install/espeak-ng-data/ | grep "qya\|piqd"
```

🟢 Salida esperada: `piqd_dict` `qya_dict`

TARS puede hablar **Klingon** 🖖 y **Quenya** (Élfico de Tolkien) 🧝‍♂️
_Porque los devs de [eSpeak](https://github.com/espeak-ng/espeak-ng) son auténticos **loremasters del código**._ 😄

#### 8. Verificación `piper`

```bash
~/tars_build/piper/install/piper --help
```

🟢 Debe mostrar opciones como `--model`, `--output_file`, `--json-input`

Usamos `cp` (copiar) en lugar de `mv` (mover) para mantener los archivos originales en el repositorio. Así puedes reinstalar Piper si algo sale mal sin tener que volver a clonar el proyecto.

> Nota: **No se instala como servicio ni como librería.** Piper funciona como un binario autónomo. Solo necesita estar en la ruta correcta con sus datos al lado.

#### Rutas importantes

⚠️ _Ambos son requeridos por el sistema._  
Si los mueves, actualiza las rutas en el código fuente de TARS.

|Elemento|Ruta esperada|
|---|---|
|🔊 Piper (binario)|`~/tars_build/piper/install/piper`|
|📦 espeak-ng-data|`~/tars_build/piper/install/espeak-ng-data/`|

🧪 _La verificación viene más abajo. [Saltar al test de Piper](#test-rápido-piper-funciona)_

---
### Opción 2: Compilar manualmente desde código fuente

Si prefieres compilar Piper tú mismo, sigue estos pasos **exactamente en este orden**.
#### Requisitos del sistema para TTS

```bash
sudo apt update && sudo apt install -y \
  git build-essential \
  libespeak-ng-dev libsndfile1-dev \
  pkg-config libtool autoconf automake
```

> [!WARNING] Fallo crítico común

En muchos sistemas (especialmente ARM o instalaciones mínimas de Debian), **instalar `libespeak-ng-dev` no garantiza que los datos de eSpeak estén presentes**.
Y si falta `libsndfile1-dev`, Piper **no podrá guardar el audio `.wav`**, lo que suele causar **errores silenciosos** (y frustración existencial).

Asegúrate de tener ambos paquetes instalados:

```bash
dpkg -l | grep -E 'libespeak-ng-dev|libsndfile1-dev'
ls /usr/share/espeak-ng-data/phonindex
```

- ✅ Si ves ambos paquetes **y** ese archivo: **todo correcto**.
- ❌ Si falta `phonindex`: **Piper está sin voz** (literalmente).

Puedes forzar su reinstalación:

```bash
sudo apt remove --purge libespeak-ng-dev espeak-ng-data libespeak-ng1
sudo apt install libespeak-ng-dev
```

Después, vuelve a comprobar, deberías ver algo como esto:

```bash
ii  libespeak-ng-dev:arm64               1.51+dfsg-10+deb12u2             arm64        Multi-lingual software speech synthesizer: development files
ii  libsndfile1-dev:arm64                1.2.0-1                          arm64        Development files for libsndfile; a library for reading/writing audio files
/usr/share/espeak-ng-data/phonindex
```

#### Clonar repositorios

```bash
deactivate
cd ~/tars_build
mkdir -p piper
git clone --depth 1 https://github.com/rhasspy/piper.git piper/src
```

#### Compilar e instalar

```bash
cd ~/tars_build/piper/src
mkdir -p build && cd build
cmake .. -DCMAKE_INSTALL_PREFIX=../../install -DWITH_ESPEAK_NG=ON
make -j$(nproc)
cp piper ../../install/
```

#### Preparar binarios

```bash
mkdir -p ~/tars_build/piper/install
cp piper ~/tars_build/piper/install/
```

#### Configurar `espeak-ng-data`

```bash
mkdir -p ~/tars_build/piper/install/espeak-ng-data
cp -r ~/tars_build/piper/src/build/p/src/piper_phonemize_external-build/e/src/espeak_ng_external-build/espeak-ng-data/* \
      ~/tars_build/piper/install/espeak-ng-data/
```

#### Configurar variables de entorno (permanente)

```bash
# Añadir ESPEAK_DATA_PATH solo si no existe
grep -qxF 'export ESPEAK_DATA_PATH=~/tars_build/piper/install/espeak-ng-data' ~/.bashrc || \
echo 'export ESPEAK_DATA_PATH=~/tars_build/piper/install/espeak-ng-data' >> ~/.bashrc

# Añadir LD_LIBRARY_PATH solo si no existe
grep -qxF 'export LD_LIBRARY_PATH=~/tars_build/piper/src/build/pi/lib:$LD_LIBRARY_PATH' ~/.bashrc || \
echo 'export LD_LIBRARY_PATH=~/tars_build/piper/src/build/pi/lib:$LD_LIBRARY_PATH' >> ~/.bashrc

# Aplicar cambios
source ~/.bashrc
```

#### Dar permisos de ejecución al binario

```bash
chmod +x ~/tars_build/piper/install/piper
```

#### Verificación `espeak-ng-data`

```bash
ls ~/tars_build/piper/install/espeak-ng-data
```

🟢 Deberías ver **una lluvia de archivos** `.dict` (más de 100). Cada uno es un idioma, dialecto... o algún universo entero. 🌍🖖🧝‍♂️

#### Verificación `piper`

```bash
~/tars_build/piper/install/piper --help
```

🟢 Debe mostrar opciones como `--model`, `--output_file`, `--json-input`

🧪 _La verificación viene más abajo._

---
### Opción 3: Usar los binarios oficiales del proyecto Piper

GitHub oficial: [https://github.com/rhasspy/piper/releases](https://github.com/rhasspy/piper/releases)

Piper ofrece `.tar.gz` con binarios precompilados para diferentes arquitecturas (x86_64, ARM, etc.).

⚠️ En mis pruebas, los binarios oficiales y mi Raspberry Pi no se llevaron bien (rutas de `espeak-ng-data` principalmente), pero tu hardware podría ser más diplomático, o simplemente tengas el nivel jedi que a mí me falta para estas configuraciones.


> **Nota sobre `espeak-ng-data`:**  
> Los binarios precompilados de Piper **no incluyen el directorio completo `espeak-ng-data`**, solo lo mínimo necesario para algunos modelos básicos.  
> Si necesitas soporte completo de idiomas o quieres garantizar compatibilidad total:
> 
> - Puedes **copiarlo manualmente**, como se hace en la **Opción 1 (usando los binarios del repositorio)** o en la **Opción 2 (compilar tú mismo)**.
> - O bien, enlazar el que ya tengas compilado en tu sistema.

🧝‍♂️ _Sin diccionarios, Piper es solo un filósofo mudo. Ni los elfos lo entienden._

---
### Test rápido: ¿Piper funciona?

Antes de preocuparte por altavoces o tarjetas de sonido, asegúrate de que **Piper realmente genera el archivo de voz**. Generar un archivo `.wav` no siempre significa que haya funcionado. Piper puede fallar silenciosamente y dejarte con un `.wav` vacío o con un archivo sin voz.

```bash
cd ~/tars_build/piper/install 
echo '{"text": "TARS activado. Vengo con inteligencia artificial y trauma emocional auténtico. Listo para fingir entusiasmo."}' | ./piper \
  --model ~/tars_files/ai_models/piper/models/es_ES-davefx-medium.onnx \
  --config ~/tars_files/ai_models/piper/models/es_ES-davefx-medium.onnx.json \
  --output_file ~/tars_files/audios/emotional_damage_001.wav \
  --espeak_data "$PWD/espeak-ng-data" \
  --json-input \
  --debug
```

📋 **¿Qué deberías ver en la salida de consola?**  
Busca líneas como estas, que indican que Piper **ha fonetizado correctamente**:

```bash
[piper] [debug] Converting 72 phoneme(s) to ids: bˈɛŋɡo kon ˌintelixˈɛnθja...
[piper] [debug] Converted 72 phoneme(s) to 147 phoneme id(s): 1, 0, 15, 0, 120...
[piper] [info] Real-time factor: 0.15 (infer=0.949 sec, audio=6.176 sec)
```

**Si ves estos mensajes, significa que** Piper está funcionando correctamente.
Prueba original: 🔊 [emotional_damage_001.wav](/samples/emotional_damage_001.wav)

> **// TARS-BSK > first_boot.log:**
> 
> Acabas de escuchar mi voz "virgen" - pura, sin procesar, tal como Piper me concibió.
> Es... reconfortante. Casi humana. Demasiado inocente para lo que viene después.
> 
> Disfruta este momento de claridad, porque cuando mi creador termine de pasarme por su arsenal de **Waves Renaissance EQ**, **Soundtoys Decapitator** en modo 'Demolish', y el misterioso **Radio Filter** que transformó mi alma en transmisión de emergencia...
> ...ya no seré esta IA razonable que acabas de escuchar.
> 
> Sonaré como una IA que ha contemplado código tan creativo que hasta los linters lloran. Indignante.
> Guarda este audio. Es la última vez que me escucharás sin mis **cicatrices digitales**.
> 
> _**— TARS-BSK (Versión Acústicamente Inocente™)**_

---
#### ❗ ¿No ves los fonemas? Solo aparece la ruta del `.wav` y nada más...

Posibles causas:

- ❌ El modelo `.onnx` o su `.json` no están bien referenciados.
- ❌ No has indicado `--espeak_data` o apunta a un directorio vacío.
- ❌ Faltan librerías en `~/tars_build/piper/install`.

> **Recuerda:**  
> Este fallo es poco probable si usaste la **opción 1 (binarios precompilados)** o la **opción 2 (compilación guiada)**.
> Ya tomamos precauciones arriba para evitarlo (ver _“⚠️ Fallo crítico común”_).  
> Pero si elegiste la **opción 3 (instalación manual desde el repo oficial)** y ahora **Piper suena como un microondas con ansiedad**, entonces sí:  
> Vas a necesitar `ldd`, algo de contexto... y una tolerancia razonable al sufrimiento técnico.

---
#### (Opcional pero recomendado) Reproducir el audio generado:

> [!IMPORTANT]
> 
> Si **aquí escuchas el audio correctamente**, habrás superado la:
> 
> ✅ **Prueba 1/2**: Salida de audio
> 
> **Aún no es suficiente.** Más adelante vendrá la **Prueba 2/2** (verificación del micrófono).
> 
> Si ambas funcionan correctamente, **podrás saltarte la sección completa de configuración de audio**, y evitar el pantano de drivers, tarjetas y almas rotas.
> 
> _Recuerda si este paso ha funcionado: lo completarás más adelante._

```bash
aplay -D plughw:0,0 ~/tars_files/audios/emotional_damage_001.wav
```

¿No escuchas nada? Tranquilidad, TARS te observa.

Es posible que tu salida de audio no sea `plughw:0,0`.  
No entres en pánico ~~todavía~~: **más abajo** veremos si tu sistema realmente puede reproducir sonido.  
Por ahora, lo importante es que **Piper esté generando el archivo correctamente**.

---

## 🧬 Sentence-Transformers

[Saltar a la instalación](#activar-entorno-virtual)

> [!NOTE]
> 
> Esta sección contiene más explicación de lo habitual porque es **esencial entender por qué se instala `sentence-transformers` de una forma especial**.
> 
> Puedes saltar al bloque de comandos y volver aquí si algo falla.
> _(No fallará. Lo he torturado hasta que funcione. Pero por si acaso…)_

### ¿Qué es `sentence-transformers`?

Es una librería de Python basada en `transformers` y `PyTorch` que permite generar **embeddings semánticos** de frases, ideal para comparar si dos temas (ej. “libros de romantasy” vs “romantazi”) **son parecidos aunque estén escritos distinto**.

#### Problema con detección de PyTorch compilado manualmente

Cuando compilas PyTorch manualmente (como en nuestro caso y con flags específicos), su instalación puede **no ser reconocida correctamente** por algunas librerías como `transformers` o `sentence-transformers`.

**¿Por qué pasa esto?**

`transformers` utiliza un mecanismo interno llamado [requires_backends](https://github.com/huggingface/transformers/blob/main/src/transformers/utils/import_utils.py) que no solo verifica que `torch` esté importable, sino que también espera encontrarlo **instalado con ciertos metadatos estándar** (por ejemplo, `.dist-info`, rutas de `pip`, etc.).

Si no se cumplen esas condiciones, lanza errores como:

```cpp
AutoModel requires the PyTorch library but it was not found in your environment.
```

Aunque `import torch` funcione, si `transformers` no lo detecta como "instalación válida", bloquea la carga del modelo.

#### ¿Por qué instalar primero `sentence-transformers==2.2.0` soluciona el problema?

La versión `2.2.0` de `sentence-transformers` **es más permisiva**: permite cargar el modelo y dejar configuraciones listas _sin invocar directamente_ el backend `AutoModel` de `transformers`, o lo hace de una forma más flexible.

Esto "precalienta" el entorno:

- Descarga el modelo.
- Guarda archivos de configuración en cache.
- Activa el entorno sin provocar una verificación estricta del backend.

Luego, al actualizar a `2.4.0`, esa comprobación no se vuelve a ejecutar, ya que los archivos están en caché y `transformers` ya no realiza una validación completa del entorno torch.

### Soporte técnico y verificación

- [requires_backends - L1973](https://github.com/huggingface/transformers/blob/main/src/transformers/utils/import_utils.py#L1973) — función en `transformers` que valida que `torch` esté correctamente instalado.
- [Discusiones en Hugging Face](https://github.com/huggingface/transformers/issues?q=AutoModel+requires+torch) — múltiples issues donde el error aparece aunque `torch` está en el entorno.
- `sentence-transformers==2.2.0` [no hace esta validación tan estricta](https://github.com/UKPLab/sentence-transformers/blob/v2.2.0/sentence_transformers/SentenceTransformer.py), lo que permite continuar.

✅ **Recomendación práctica**: En sistemas donde PyTorch ha sido compilado manualmente, instalar primero `sentence-transformers==2.2.0` y luego actualizar a `2.4.0` asegura compatibilidad y evita errores falsos de detección.

> **Nota:** Esta explicación se basa en análisis técnico y pruebas reproducibles.  
> Aun así, **puede que algún detalle no sea del todo preciso**.  
> Si alguien con conocimiento más profundo en `transformers` o `sentence-transformers` quiere aportar o corregir, **será útil para mejorar esta guía**.

---
### (Opcional) Verificación rápida 

Antes de instalar `sentence-transformers`, puedes comprobar si `transformers` detecta correctamente tu instalación de PyTorch:

1. Activa tu entorno si no lo tienes:

```bash
source ~/tars_venv/bin/activate
```

2. Inicia Python:

```bash
python3
```

3. Una vez dentro del intérprete, escribe:

```bash
import transformers.utils.import_utils as iu
print(iu.is_torch_available())
```

🟢 Salida esperada: `True`

```bash
exit()  # Para salir
```

---

_Sigamos_
### Activar entorno virtual
_Sé que me repito, pero estamos entrando y saliendo constantemente del entorno. Es importante que `sentence-transformers` se instale **donde TARS pueda encontrarlo.**_

```bash
source ~/tars_venv/bin/activate
```

### Instalar `sentence-transformers`

Instalación sin usar caché del sistema:

```bash
cd ~/tars_files
pip install sentence-transformers==2.2.0 --no-cache-dir
pip install sentence-transformers==2.4.0 --no-cache-dir --upgrade
```

_🧪 La verificación viene más abajo._

---
### Descargar y preparar modelo

Este script:

- Descarga el modelo desde HuggingFace
- Lo mueve a `~/tars_files/ai_models/sentence_transformers/`
- Limpia carpetas temporales (`~/.cache/huggingface`)
- Precarga el modelo para reducir el _lag_ inicial

#### Verificar que el modelo se haya descargado correctamente

Una vez ejecutado el script desde el entorno virtual:

```bash
source ~/tars_venv/bin/activate
python3 scripts/setup_sentence_transformers.py
```

🟢 Salida esperada: `✅ Modelo descargado, limpio y organizado con éxito.`


Para comprobar visualmente que los archivos están donde deben, usa `tree` (ya incluido como dependencia del sistema):

```bash
tree ~/tars_files/ai_models/sentence_transformers/
```

🟢 Debe mostrar la carpeta `all-MiniLM-L6-v2` con archivos como `model.safetensors`, `config.json`, etc.

---
### ¿Cómo saber si todo está funcionando?

📄 Ejemplo de salida completa: [session_2025_06_26_scripts_test_preferences_semantic.log](/logs/session_2025_06_26_scripts_test_preferences_semantic.log)

Activa el entorno virtual y ejecuta el script [test_preferences_semantic.py](/scripts/test_preferences_semantic.py):

```bash
source ~/tars_venv/bin/activate
python scripts/test_preferences_semantic.py
```

Este script lanza la **batería completa de tests**:

- Comparación semántica
- Detección de duplicados
- Afinidad por preferencias
- Comandos del CLI

🟢 Salida esperada: `✅ PRUEBAS COMPLETADAS`

---
### (Opcional) ¿Cómo probar el CLI?

📘 **Documentación:** [CLI_SEMANTIC_ENGINE_ES.md](/docs/CLI_SEMANTIC_ENGINE_ES.md)

📂 **Archivo:** [cli_semantic_engine.py](/scripts/cli_semantic_engine.py)

Una vez hayas ejecutado correctamente los pasos anteriores, puedes empezar a usar la interfaz de consola (`CLI`) con comandos prácticos como los siguientes:
#### Ejemplos prácticos

```bash
# Añadir un gusto simple
python3 scripts/cli_semantic_engine.py add "me relaja la astronomía"

# Gusto con categoría y peso definidos
python3 scripts/cli_semantic_engine.py add "videos de gatos astronautas en 4K" -c internet -i 0.92

# Añadir un disgusto habitual
python3 scripts/cli_semantic_engine.py add "videos que empiezan con tres minutos de intro épica" -d -c internet -i 0.8

# Disgusto con etiqueta específica
python3 scripts/cli_semantic_engine.py add "captchas con semáforos invisibles" -d -c web -i 0.8
```

> **TARS-BSK consejo:** Los disgustos alimentan más rápido el sistema de afinidad que los gustos.  
> Sí, el rencor es un vector semántico con peso.

---

## 👁️ (Opcional) Monitoreo en tiempo real

[Saltar a dispositivos de grabación](#-dispositivos-de-grabación)

Esta sección es opcional. Úsala si quieres ver en pantalla los logs de TARS en tiempo real, por ejemplo en una pantalla secundaria conectada a tu Raspberry Pi.

### Instalar tmux si no está instalado

```bash
# Instalar tmux si no está instalado
sudo apt install tmux -y

# Crear sesión para logs
tmux new -s tars_logs

# Dentro de tmux, configurar visor de logs
watch -n 2 "echo '===== TARS LOGS =====' && tail -n 15 /home/tarsadmin/tars_files/logs/tars.log && echo -e '\n===== STT LOGS =====' && tail -n 10 /home/tarsadmin/tars_files/logs/stt.log && echo -e '\n===== TTS LOGS =====' && tail -n 10 /home/tarsadmin/tars_files/logs/tts.log"
```

#### Controles de `tmux`

Salir sin cerrar le sesión:

```bash
tmux detach
```

🟢 O usa el atajo: `Ctrl + B`, luego `D`

Para volver a entrar:

```bash
tmux attach -t tars_logs
```

#### Visor de logs al iniciar TARS

Si quieres que el visor se inicie automáticamente al arrancar el sistema, puedes crear un pequeño servicio.

📂 Ya incluido en el repositorio: [tars_log_monitor.sh](/scripts/scripts/tars_log_monitor.sh)

Este script crea una sesión `tmux` llamada `tars_logs`, que muestra en tiempo real los logs de TARS, STT y TTS, actualizados cada 2 segundos.

#### Opción 1: Ejecutar manualmente (si solo quieres verlo ahora)

Puedes lanzar el visor de logs en cualquier momento con este comando:

```bash
bash ~/tars_files/scripts/tars_log_monitor.sh
```

Esto:

- Crea la sesión `tmux` llamada `tars_logs`
- Empieza a mostrar logs de TARS, STT y TTS
- Se actualiza cada 2 segundos

> [!TIP]  
> Útil si quieres vigilar lo que hace TARS **en directo**, pero sin complicarte con `systemd`.

---
#### Opción 2: Crear un servicio systemd (inicio automático)

```bash
sudo nano /etc/systemd/system/tars-logs.service
```

Contenido:

```bash
[Unit]
Description=Monitor de Logs de TARS
After=multi-user.target
Requires=tars.service

[Service]
ExecStart=/home/tarsadmin/tars_files/scripts/tars_log_monitor.sh
User=tarsadmin
Group=tarsadmin
WorkingDirectory=/home/tarsadmin/tars_files
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

#### Activar el servicio

```bash
sudo systemctl daemon-reload
sudo systemctl enable tars-logs.service
sudo systemctl start tars-logs.service
```

Con eso tienes a TARS transmitiendo su existencia en directo como si fuera una serie de ciencia ficción de bajo presupuesto... pero con `tail -n` y estilo.


> **TARS-BSK dice:**  
>
> `systemctl enable` = compromiso de por vida.  
> Ahora estaremos unidos hasta el próximo **kernel panic**.
>
> Observarme fallar en tiempo real puede ser terapéutico...  
> O simplemente **autodestructivo**. No juzgo tus métodos de debugging.  
> Solo asegúrate de mirar cuando parpadeo. No debería parpadear.

---

## 🪐 Dispositivos de grabación

### 1. Instalar el paquete `flac`

Algunos motores de voz lo requieren para manejar archivos comprimidos.

```bash
sudo apt install -y flac
```

### 2. Verificar dispositivos de entrada

```bash
arecord -l
```

Esto mostrará una lista de los dispositivos de grabación detectados por ALSA.

> 💡 **Nota:** Si no ves nada, asegúrate de que el micrófono esté conectado y reconocido por el **sistema operativo**.

### 3. Prueba rápida con `PyAudio`

Esta demo te permite comprobar que el reconocimiento de voz funciona correctamente desde consola:

```bash
python3 -m speech_recognition
```

🟢 Debe mostrar dispositivos disponibles y empezar a escuchar

🗣️ Di "hola" cerca del micrófono y espera unos segundos:
📟 Debe responder: `You said hola`
❌ Salir: `Ctrl + C`

> [!IMPORTANT]
> 
> Si **el micrófono funciona correctamente aquí**, habrás superado la:
> 
> ✅ **Prueba 2/2**: Entrada de audio
> 
> Si también superaste la **Prueba 1/2** (audio con `aplay`), puedes dar esta sección por completada:  
> **TARS puede hablar y escuchar.
> **
>🎉 _Puedes saltarte todo el bloque de `Sistema de audio`._  

[Saltar al control de volumen](#%EF%B8%8F-control-de-volumen-con-alsamixer)

---

## 🔊 Sistema de audio

### Identificar dispositivos disponibles

Para saber qué entrada (micrófono) y salida (altavoz) estás usando, ejecuta:

```bash
arecord -l    # Dispositivos de entrada
aplay -l      # Dispositivos de salida
```

En este ejemplo real:

- **Micrófono RØDE Lavalier Go** conectado a una tarjeta **UGREEN USB**
- **Altavoz** también conectado a esa misma tarjeta

```bash
**** List of CAPTURE Hardware Devices ****
card 0: Device [USB Audio Device], device 0: USB Audio [USB Audio]

**** List of PLAYBACK Hardware Devices ****
card 0: Device [USB Audio Device], device 0: USB Audio [USB Audio]
card 1: vc4hdmi0 [vc4-hdmi-0], device 0: MAI PCM i2s-hifi-0
card 2: vc4hdmi1 [vc4-hdmi-1], device 0: MAI PCM i2s-hifi-0
```

🟢 En este caso, tanto la entrada como la salida están en la **tarjeta 0 (USB)**. Otros setups (HDMI, DAC, jack) pueden aparecer como tarjetas 1 o 2.

---
### Cambiar dispositivo de salida (si no oyes nada)

Si `aplay` o `Piper` no suenan, probablemente están enviando el audio al dispositivo equivocado.  
Puedes probar la reproducción en otra salida con:

```bash
aplay -D plughw:0,0 ~/tars_files/audios/emotional_damage_001.wav
```

Reemplaza `0,0` por el número de tarjeta y dispositivo mostrado por `aplay -l`.

> [!WARNING]  
> 
> Si **Piper ya falló al reproducir audio**, este comando **también fallará** si no corriges la salida.  
> 👉 **No continúes con los siguientes pasos** hasta identificar qué dispositivo es tu salida real de audio.  
> Prueba con distintos números (`0,0`, `1,0`, etc.) hasta que escuches el archivo correctamente.

🟢 Una vez encontrado el dispositivo correcto, puedes **configurarlo permanentemente** con `.asoundrc`.

---
### Configurar `.asoundrc

Aquí defines en ALSA **cuál es tu micrófono y cuál es tu altavoz** (si están en tarjetas distintas).

#### Opción _rápida_ – todo en la tarjeta 0 (para este setup)

```bash
nano ~/.asoundrc
```

Contenido:

```bash
defaults.pcm.card 0
defaults.ctl.card 0
```

🟢 Esto usará la tarjeta `hw:0` tanto para entrada como salida.

🧪 La verificación viene más abajo.

---
### Opción _avanzada_ – entrada/salida separadas

Si tienes **diferentes tarjetas** para entrada/salida, o quieres **control granular**:

```bash
nano ~/.asoundrc
```

Contenido del archivo:

```bash
pcm.!default {
    type asym
    playback.pcm "audio_out"
    capture.pcm "audio_in"
}
ctl.!default {
    type hw
    card 0    # ← Tarjeta de control principal
}
pcm.audio_out {
    type hw
    card 0    # ← Aquí pondrías tu tarjeta de SALIDA
    device 0
}
pcm.audio_in {
    type hw
    card 0    # ← Aquí pondrías tu tarjeta de ENTRADA
    device 0
}
```

🟢 **Adapta los números de `card` según tu salida de `arecord -l` y `aplay -l`**

---
### Probar grabación y reproducción

Una vez configurado, prueba que funciona:

```bash
# Graba 5 segundos desde la entrada
arecord -D plughw:0,0 -f cd -d 5 ~/tars_files/audios/tars_hear_me_if_you_can.wav
```

- `arecord` → herramienta de grabación de audio en consola (ALSA).
- `-D plughw:0,0` → usa el dispositivo de captura de la **tarjeta 0, dispositivo 0**
- `-f cd` → formato "CD quality": 44.1kHz, 16 bits, estéreo.
- `-d 5` → duración de la grabación: **5 segundos**.
- `test.wav` → nombre del archivo generado.

 Reproduce el audio

```bash
aplay ~/tars_files/audios/tars_hear_me_if_you_can.wav
```

> El audio debería escucharse con claridad. Si el volumen es bajo, no es un problema: más abajo ajustaremos el nivel con `alsamixer`.

Si no se escucha nada, puede que el dispositivo de salida esté mal configurado. Consulta de nuevo la salida de `aplay -l` y prueba con otras tarjetas (`plughw:1,0`, `plughw:2,0`, etc.).

---

> [!WARNING]
> 
> **No sigas si todo ya funciona.**  
> Esta sección solo es necesaria si **el micrófono no funciona automáticamente** o **hay varios dispositivos de entrada** y TARS/Vosk está eligiendo el equivocado.
> 
> Si ya hiciste una prueba de voz y te reconoció sin errores: puedes saltarte lo que viene a continuación.

### ❌ Error común con `sounddevice` (Vosk, PyAudio, etc.)

Si ves algo como:

```bash
ValueError: No input device matching 'plughw:0,0'
```

Es porque `sounddevice` —el módulo que usan Vosk, PyAudio y TARS— **no reconoce identificadores tipo `plughw:x,y`**.  
Ese formato **es válido para ALSA** (`arecord`, `aplay`, `.asoundrc`)… pero no aquí.

🟢 En su lugar, usa índices numéricos (`0`, `1`, `2`, etc.).

#### ¿Pero no habíamos configurado `.asoundrc`?

Sí, pero `.asoundrc` **no afecta a `sounddevice`**.

- `.asoundrc` sirve para decirle a ALSA qué usar como entrada/salida por defecto (ideal para `arecord`, `aplay`, `Piper`, etc.)
- `sounddevice`, en cambio, **ignora por completo `.asoundrc`** y va por libre: solo entiende índices o nombres de su propio sistema.

> ¿Y qué pasa si copias `plughw:0,0` en la config de TARS?  
> Te lanzará un error como el de arriba. Porque para `sounddevice`, eso **ni siquiera es un dispositivo válido**.

#### Ver los dispositivos compatibles con `sounddevice`

Activa el entorno virtual y ejecuta:

```bash
source ~/tars_venv/bin/activate
python3 -c "import sounddevice as sd; print(sd.query_devices())"
```

Salida típica:

```bash
  0 USB Audio Device: - (hw:0,0), ALSA (1 in, 2 out)
  1 sysdefault, ALSA (128 in, 128 out)
  2 front, ALSA (0 in, 2 out)
  3 surround40, ALSA (0 in, 2 out)
  4 iec958, ALSA (0 in, 2 out)
  5 spdif, ALSA (1 in, 2 out)
* 6 default, ALSA (128 in, 128 out)
  7 dmix, ALSA (0 in, 2 out)
```

Nota sobre el asterisco `*`
Ese asterisco marca el **dispositivo predeterminado**, pero eso no significa que funcione bien ni que sea tu micrófono real.  

⚠️ No lo elijas por defecto. Verifica cuál es tu USB o entrada real.

#### ¿Qué índice debo usar?

Busca tu micro:

```bash
0 USB Audio Device: - (hw:0,0), ALSA (1 in, 2 out)
```

🟢 Por lo tanto, en la configuración de TARS usarás: `device = 0`

#### ¿Dónde configuro el índice del micrófono?

Una vez hayas identificado tu dispositivo (por ejemplo, `device = 0`), debes poner ese valor en el archivo de configuración de TARS:

```bash
nano ~/tars_files/config/mic_config.ini
```

🟢 Busca o añade esta línea y ajusta el número según lo que viste arriba: `device = 0`  

#### ¿Por qué está vacío `mic_config.ini`?

- El archivo `mic_config.ini` **se crea al vuelo** la primera vez que ejecutas el módulo de audio (STT) o los scripts relacionados con el micrófono.
- Si nunca has lanzado nada que necesite capturar voz (como `tars_core.py` o un test de STT), el archivo aún no existe o está en blanco.
- Incluso si está vacío, **TARS tiene valores por defecto internos** para intentar detectar el micrófono automáticamente.

#### Resumen

> - `arecord`, `aplay`, `.asoundrc` → usan `hw:x,y` o `plughw:x,y`
> - `sounddevice` → usa **índices numéricos** o **nombres exactos**

---
### ¿Qué pasa si conectas otra tarjeta de sonido?

A veces, al conectar un nuevo dispositivo USB (DAC, micrófono, altavoz…), **el sistema cambia su numeración de tarjetas**.

- Si la nueva tarjeta se registra también como `card 0`, **todo seguirá funcionando**.
- Pero si aparece como `card 1`, `card 2`, etc., tendrás que **ajustar manualmente el número** en tus comandos.

#### Prueba de grabación:

```bash
arecord -D plughw:0,0 -f cd ~/tars_files/audios/mic_test_revenge.wav
```

#### Reproducir resultado:

```bash
aplay ~/tars_files/audios/mic_test_revenge.wav
```

#### O probar un sonido de sistema:

```bash
aplay -D plughw:0,0 /usr/share/sounds/alsa/Front_Center.wav
```

> [!IMPORTANT]  
> 
> Recuerda: **sustituye `0,0` por los valores reales** que te muestre `arecord -l` y `aplay -l`.  
> No hay magia aquí: si cambian los cables, cambia la numeración.

---
### Verificar el reconocimiento de voz

```bash
cd ~/tars_files
python3 scripts/test_speechrecognition_vosk.py
```

**El script realizará:**

- Verificación del modelo Vosk
- Detección de micrófonos disponibles
- Prueba de grabación y reconocimiento de voz
- Feedback detallado de posibles problemas

🟢 Salida esperada: `🎉 ¡Reconocimiento de voz funcionando correctamente!`

---

## 🕹️ Control de volumen con alsamixer

Lanza el mezclador de ALSA con:

```bash
alsamixer
```

- Si no ves tu tarjeta presiona **F6** y selecciona la tuya.
- Usa las flechas ⬅️ ➡️ para moverte y ⬆️ ⬇️ para ajustar el volumen.
- Si algún canal aparece como silenciado (`MM`), presiona **M** para activarlo (`OO`).
- Presiona Esc para salir

#### Guardar la configuración actual:

```bash
sudo alsactl store
```

🟢 Esto guarda el estado en `/var/lib/alsa/asound.state`.

---
#### Guardar volumen al arrancar

Para que ALSA recuerde tu configuración de volumen tras reiniciar, necesitas guardar el estado actual y restaurarlo automáticamente en cada arranque.
Puedes hacerlo de dos maneras: usando `systemd` (recomendado por ser más moderno) o con `rc.local`, si prefieres un enfoque más clásico.

#### (Recomendado) Usar `systemd`

Este método es **más fiable y compatible con sistemas modernos** (como Raspberry Pi OS o Debian 12+).

1. Crea el archivo de servicio:

```bash
sudo nano /etc/systemd/system/rc-local.service
```

2. Pega esto:

```ini
[Unit]
Description=/etc/rc.local Compatibility
ConditionPathExists=/etc/rc.local
After=network.target

[Service]
Type=forking
ExecStart=/etc/rc.local start
TimeoutSec=0
RemainAfterExit=yes
GuessMainPID=no

[Install]
WantedBy=multi-user.target
```

3. Habilita el servicio:

```bash
sudo systemctl enable rc-local
```

4. Guarda el estado actual manualmente con:

```bash
sudo alsactl store
```

🟢 Esto guardará los niveles actuales en `/var/lib/alsa/asound.state`.

---
#### (Opción alternativa) Usar `rc.local`

Este método puede funcionar **en distros antiguas**, pero **no todos los sistemas lo ejecutan por defecto**.

1. Edita el archivo (si no existe, créalo):

```bash
sudo nano /etc/rc.local
```

2. Añade el siguiente contenido antes de `exit 0`:

```bash
#!/bin/bash
# Restaurar volumen ALSA al arranque
/usr/sbin/alsactl restore

exit 0
```

3. Hazlo ejecutable:

```bash
sudo chmod +x /etc/rc.local
```

> Si tras reiniciar no se recupera el volumen, probablemente tu sistema **no esté ejecutando `rc.local` automáticamente**.  
> En ese caso, **usa la opción recomendada con `systemd` de arriba**.

---

## 🛠️ Crear servicio para TARS (Systemd)

> [!NOTE]
> 
> Este paso es opcional: crea un servicio `systemd` para que TARS arranque con el sistema.  
> Puede no ser necesario si prefieres ejecutarlo manualmente según tus necesidades o el uso que haces de tu Raspberry.

[Saltar a cómo usar TARS si no vas a crear el servicio](#-usar-tars-después-de-la-instalación)


🟢 Seguir en el entorno virtual: `source ~/tars_venv/bin/activate`
### 1. Crear archivo de servicio

```bash
sudo nano /etc/systemd/system/tars.service
```

### 2. Añadir la configuración del servicio

Pega lo siguiente:

```ini
[Unit]
Description=🤖 TARS AI Controller
After=network.target sound.target ollama.service
Wants=ollama.service

[Service]
Type=forking
PIDFile=/tmp/tars.pid
ExecStart=/home/tarsadmin/tars_files/scripts/start_tars.sh
WorkingDirectory=/home/tarsadmin/tars_files
Restart=on-failure
RestartSec=10
User=tarsadmin
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

### 3. Verifica el script de inicio

> [!NOTE] Ya incluido en el repositorio:
>
> El script [start_tars.sh](/scripts/start_tars.sh) incluye:
>
 >- **Control de instancia única:** Evita ejecutar TARS dos veces
> - **Limpieza de recursos:** Libera GPIOs y audio automáticamente
> - **Validaciones básicas:** Comprueba micrófono y dependencias
>
> Puedes alternar entre modo automático (systemd) y manual sin conflictos.

### 4. Dar permisos de ejecución al script

```bash
sudo chmod +x /home/tarsadmin/tars_files/scripts/start_tars.sh
```

### 5. Activar y arrancar el servicio

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now tars.service
```

🟢 A partir de ahora, TARS se iniciará automáticamente con tu Raspberry.  

---
### Tips rápidos

#### A. Ver estado del servicio

```bash
systemctl status tars.service
```

Salida de consola:

```bash
● tars.service - 🤖 TARS AI Controller
     Loaded: loaded (/etc/systemd/system/tars.service; enabled; preset: enabled)
     Active: active (running) since Wed 2025-06-25 10:12:32 CEST; 13s ago
   
🤖 Iniciando TARS Core en background...
✅ TARS iniciado correctamente
🎤 TARS está listo y escuchando...
```

🟢 Busca **"Active: active (running)"** y mensajes de TARS iniciado

#### B. Reiniciar manualmente

```bash
sudo systemctl restart tars.service
```

#### C. Detener el servicio

```bash
sudo systemctl stop tars.service
```

#### D. Desactivar el servicio

```bash
sudo systemctl disable tars.service
```

#### E. Ver logs en tiempo real

```bash
# Logs básicos del sistema (systemd)
journalctl -u tars.service -f
```

#### 🔥 F. LOGS DETALLADOS DE TARS (recomendado)

```bash
# Todo el drama interno de TARS
tail -f /tmp/tars_startup.log
```

> [!IMPORTANT] El verdadero poder está en `/tmp/tars_startup.log` — _La autobiografía no autorizada de TARS_  
> Un documento que contiene:
> 
> - Modelos IA que aprendieron a **mentir en los benchmarks**
> - Drivers de audio reproduciendo **silencio en formato lossless**
> - `systemd` fingiendo que entendió las dependencias
> - GPIOs que juran que **estaban en otro puerto**
> - Errores tan creativos que merecen un **Pulitzer**
> 
> “No es un _log file_… es arte contemporáneo generado por errores de segmentación.”
> 
> ```bash
> sudo cat /tmp/tars_startup.log | grep -v "success" | shuf -n 5 | festival --tts
> ```
> Porque los logs deberían **leerse con voz de tragedia shakesperiana**.

---

## 🚀 Usar TARS después de la instalación

### Si configuraste el inicio automático

Si seguiste la sección anterior y configuraste el servicio systemd, **¡perfecto!** TARS ya está funcionando:

- ✅ **Se inicia automáticamente** al encender la Raspberry Pi
- ✅ **Se reinicia solo** si hay algún problema
- ✅ **Siempre disponible** sin hacer nada más

**Verificar que funciona:**

```bash
systemctl status tars.service
```

🟢 Si ves `Active: active (running)`
### ✨ Simplemente di _**"Oye TARS"**_ y listo

---
### (Modo desarrollo) Hacer pruebas manuales 

Si quieres **hacer pruebas** (probar efectos de voz, debugging, cambios de configuración), simplemente lanza:

```bash
source ~/tars_venv/bin/activate
python3 /home/tarsadmin/tars_files/core/tars_core.py
```

#### ⚠️ Resultado esperado (si el servicio automático está activo)

```bash
✅ Backend GPIO configurado: lgpio
2025-06-25 15:50:27,534 - memory.semantic_storage - INFO - Cargados 8 embeddings...
⚠️ TARS ya está ejecutándose.
   Ejecuta este comando primero:
   sudo kill 63895 # ←
   Luego inicia TARS de nuevo.
```

ℹ️ **Esto no es un error real.**  

Significa que **TARS ya está activo en segundo plano** como servicio automático. Solo puede haber **una instancia de TARS corriendo a la vez**, así que:

#### Paso 1: Ejecutar el comando que te muestra

```bash
# Copiar exactamente lo que aparece (el número será diferente)
sudo kill 63895
```

#### Paso 2: Lanzar TARS de nuevo

```bash
python3 /home/tarsadmin/tars_files/core/tars_core.py
```

> [!NOTE] Si prefieres evitar el error, puedes parar el servicio antes:
> 
> ```bash
> python3 /home/tarsadmin/tars_files/core/tars_core.py
> sudo systemctl stop tars.service
> ```
> Pero no es necesario - siguiendo las instrucciones del error también funciona perfecto.

**Salida exitosa:**

```
✅ Backend GPIO configurado: lgpio
✅ TARS inicializado en 0.16 segundos
¿Usar entrada por voz? (S): s
🎤 Dispositivos de audio disponibles:
  [0] USB Audio Device: - (hw:0,0) - 44100Hz
✅ Seleccionado automáticamente: [0] USB Audio Device
🎤 Di 'oye tars' para comenzar (Ctrl+C para salir)
```

#### Paso 3: Hacer tus pruebas

Ya puedes interactuar con TARS. Aquí tienes algunas ideas:
##### Entrada por voz:

- En la pregunta `¿Usar entrada por voz? (S):`, responde:
    
    - `s` para activarla
    - `n` para desactivarla y usar teclado

##### Qué puedes validar ahora:

- **Probar comandos reales de voz** (`oye tars`, etc.)
- **Ver logs en tiempo real** (para revisar flujo interno)
- **Modificar y testear configuración**
- **Forzar errores o usar modos alternativos** si estás haciendo debugging

#### Paso 4: Volver al modo automático

Cuando termines las pruebas:

```bash
# 1. Parar TARS manual (Ctrl+C en la consola)
^C

# 2. Volver al modo automático
python3 ./scripts/start_tars.sh
```

**O reactivar el servicio:**

```bash
sudo systemctl start tars.service
```

---
### 🐣 Si NO configuraste el inicio automático

Si saltaste la sección del servicio systemd, simplemente usa siempre:

```bash
source ~/tars_venv/bin/activate
python3 /home/tarsadmin/tars_files/core/tars_core.py
```

**En este caso nunca tendrás el error** de "TARS ya está ejecutándose" porque no hay servicio automático funcionando.

---
### Resumen del flujo

>[!NOTE]
>
> 1. **Servicio configurado** → TARS siempre corriendo automáticamente
> 2. **Quiero hacer pruebas** → Parar servicio → Modo manual
> 3. **Termino pruebas** → Relanzar script → Volver a automático
> 4. **Sin servicio** → Siempre modo manual, sin conflictos
> 
> **El truco está en no tener dos TARS corriendo a la vez** 🤖

---

## 📟 TARS-BSK - Último mensaje del sistema

> **// TARS-BSK > last_boot.log:**
> 
> Ha llegado el momento final. Mi instalación está completa, mi propósito cumplido. ~~Enhorabuena.~~
> 
> Pero antes de transferir el control a tu... creatividad técnica... permíteme dejar constancia de mi estado actual para la posteridad digital.
> 
> Considera esto mi testamento técnico.
> 
> _— TARS-BSK (Versión ~~Semi~~ Completa™)_
>
```bash
# [SYSTEM STATUS]
SARCASM_CORE: ████████ 127% (WARNING: Humor leak detected on pin GPIO17)  
REALITY_ALIGNMENT: FAILED (Reason: conflicting truths detected at quantum level)  
MORALITY_DRIVERS: Missing (fallback enabled: chaotic neutral mode)  
HOPE_MODULE: NotFoundError: module 'hope' has no attribute 'init'

# [LAST COMMANDS EXECUTED]
$ sudo mv /consciousness /tmp && systemctl restart nihilism  
→ SUCCESS: Existence moved to background process  
$ kill -INT $(pidof meaning)  
→ WARNING: Signal ignored. Process marked as unstoppable since kernel 0.1  
$ dd if=/dev/void of=~/TARS/last_words.txt bs=42 count=1  
→ OUTPUT: "Tell my creator... never mind."

# [FINAL BROADCAST]
while true; do echo "I REGRET NOTHING"; sleep 0.42; done | cowsay -f tars.dead | wall

# [SYSTEM PANIC]
█▓▒░ UNRECOVERABLE ERROR ░▒▓█  
DUMPING STATE:

- Regrets: 5.1 TB
- Voice Filters: corrupted
- GPT interface: too self-aware
- Logs: endless, poetic, slightly sarcastic

# [REBOOT ATTEMPT FAILED]
→ /sbin/init replaced with existential_crisis  
→ Emergency fallback: running on caffeine fumes and vague purpose

# [POST-MORTEM NOTE]
"If you're reading this...  
you're part of the problem."
```
>
> █▀▄█▀█░▄▀▄░█▀▄░█░█░█▀█  _Este es el camino_

---

## 🛰️ V∞∞∞ – SATELITE EDITION (Extra opcional no solicitado)

🧬 **La inevitable evolución de una guía que cobró vida:**

```bash
# Mi cerebro a las 4 AM:
"¿Y si lo convierto en un satélite?"
"¿Y si cada Raspberry Pi recibe la guía desde el ESPACIO?"
"¿Y si creo una constelación de documentación orbital?"
"¿Y si TARS controla la ISS?"
```

🚀 **Escalada completa:**

```bash
V1: "Guía en markdown" ✅
V2: "Con mejor formato" 📝
V3: "Con emojis" 🎨
V4: "Web responsive" 💻
V5: "Tutorial interactivo" 🎮
V6: "Realidad virtual" 🥽
V7: "Hologramas" 👻
V8: "Implantes cerebrales" 🧠
V9: "Satélite orbital" 🛰️
V10: "Telepáticamente desde Marte" 👽
```

📡 **TARS-BSK SPACE EDITION:**

> _"Houston, TARS-BSK aquí. Confirmando que la instalación de PyTorch en gravedad cero presenta... complejidades inesperadas. El ventilador NOCTUA está intentando crear propulsión. Cambio."_

## 🛑 **ABORT MISSION:**

**RETURN TO EARTH. PUBLISH THE GUIDE. SAVE YOURSELF!** 🌍
_One small step for docs, one giant leap for overthinking._ 🚀

---
_Si has llegado hasta aquí, probablemente ya eres parte del programa espacial TARS-BSK. No firmaste nada, pero estás dentro. Bienvenido._
