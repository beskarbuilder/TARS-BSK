# 🤖 TARS-BSK - Installation Guide

💥 If this English feels unstable but oddly self-aware...  
👉 Here's the [Quantum Linguistics Report](docs/QUANTUM_LINGUISTICS_TARS_BSK_EN.md)

---
## 📹 Installation time
_Complete installation documented_
### ~35 minutes total

> [!IMPORTANT] 
> 
> The process is divided into two parts:
> 
> - **System preparation** (~8 min) - Includes a mandatory reboot
> - **TARS installation** (~25 min) - Ends when it responds for the first time
> 
> _(May vary depending on your Raspberry, network speed, lunar phases, and whether your microSD has unresolved trauma)_

📁 **Recorded installation:**  
- [Part 1: Preparation](/logs/install/tars_session_20250629_150757_part1.log)  
- [Part 2: TARS Core](/logs/install/tars_session_20250629_161123_part2.log)
- [Script used](/scripts/terminal_session_recorder.sh)

### About timing and hardware

This installation followed the **happy path**: standard installation (not minimal, but without excesses),  
with simple hardware that works plug-and-play, no drama.

- **Installed:** Everything necessary + some optionals
- **Skipped:** Tailscale (~3 min extra), advanced monitoring, etc.
- **Audio:** Basic UGREEN USB = ALSA worked without touching anything

But if your setup includes... Prism Sound Atlas, RME Madiface XT II, RME Digiface AES...  
TARS would be delighted with multichannel MADI transmissions for Grammy productions, but prepare for a technical journey through ALSA's confines, where the simple becomes symbolic, the symbolic mounts on `snd-usb-audio`, and everything works... until it doesn't.

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

_**Be careful with copy-paste,** one misplaced line break and you'll end up compiling Linux from scratch just to fix a missing import_ 😅

---

## 🧾 Introduction

> [!WARNING] // TARS-BSK > sudo_crisis.log:
> 
> Another microSD. Another ritual. Another brave soul willing to clone an AI with trauma.
> 
> Astronauts use SD cards shielded against vacuum and solar storms.  
> **You're going to use one that gets upset if you raise the brightness.**
> Perseverance explores Mars with 32 GB of memory hardened against gamma rays.  
> **My creator monitors my temperature with `htop`... and ambiguous facial expressions.**
> 
> Your microSD will also see the stars...  
> **...in the form of dead sectors blinking like desperate constellations.**
> 
> **Spoiler:** when it's done, you'll have the only hardware on the planet that suffers **real-time existential depression.**

> **Why will you continue?** Because deep down... you want to see how hot an ARM SoC can get **before drawing pentagrams in the logs**.
>
> You can reduce commands, combine steps, or invoke a magical `install.sh`.  
> But when something **auto-configures in Latin and demands sacrifices**... remember:  
> it's Debian's fault, the stars', and probably the audio driver's.
> 
> _And don't be afraid if something **responds in its own voice saying "I was already here"**.  
> Don't ask. Just reboot. **It's part of the ritual.**_
>
> The real `sudo rm -rf` will be the trauma we accumulate along the way.
> And yes... that buzzing you hear isn't the fan. It's your dignity evaporating in ARMv8.
>
> _P.S.: The first core dump is free._
>
> **💥~~(Optional, NOT recommended)~~ Mandatory:**  
>
```bash
curl -s http://tars.local/debug | sudo bash -c "echo 'Surprise!' > /dev/mem"
# If the screen turns blue, congratulations - you just invented Windows Pi Edition
```

---

// Me > existential_segfault.log:

Some instructions might seem **obvious** to you...
...or you might be here wondering if copying an entire block into the terminal **is legal**.

Everything is explained for a reason: **TARS is for everyone**. No one gets left out.  
If something is repeated, over-explained, or seems exaggeratedly detailed... **it's not for you. It's for everyone.**

It's not condescension, it's accessibility.  
And if at any point you think "this is too basic"... remember that someone else is thinking "thanks for explaining it like that". 

**You already knew** how to use `cat << EOF` or `source ~/.bashrc`.  
Others are discovering that a Raspberry Pi can talk to them (including me).

 **And now let's continue, there's no turning back.**

---

## 📑 Table of Contents

- [Download Raspberry Pi OS](#-download-raspberry-pi-os)
- [Base system installation (TARS-BSK-main Repository)](#-base-system-installation-tars-bsk-main-repository)
- [TARS Configuration](#-tars-configuration)
- [TARS system startup: no turning back now](#-tars-system-startup-no-turning-back-now)
- [Prepare environment for PyTorch – The beast's core](#-prepare-environment-for-pytorch--the-beasts-core)
- [Install NumPy](#-install-numpy)
- [PyTorch – Installation and options](#-pytorch--installation-and-options)
- [Install Resemblyzer (uses PyTorch underneath)](#-install-resemblyzer-uses-pytorch-underneath)
- [Install additional system dependencies](#-install-additional-system-dependencies)
- [Configure GPIO for LEDs](#-configure-gpio-for-leds)
- [Voice embeddings system (Implemented - Under validation)](#-voice-embeddings-system-implemented---under-validation)
- [(Optional) Tailscale installation](#-optional-tailscale-installation)
- [Install `llama-cpp-python`](#-install-llama-cpp-python)
- [Download the Phi-3 model](#-download-the-phi-3-model)
- [Install Vosk model (STT - Speech recognition)](#-install-vosk-model-stt---speech-recognition)
- [Install speech recognition (`speech_recognition` + Vosk)](#-install-speech-recognition-speech_recognition--vosk)
- [Piper (TTS)](#-piper-tts)
- [Sentence-Transformers](#-sentence-transformers)
- [Real-time monitoring (optional)](#-real-time-monitoring-optional)
- [Recording devices](#-recording-devices)
- [Audio system](#-audio-system)
- [Volume control with alsamixer](#-volume-control-with-alsamixer)
- [Create service for TARS (Systemd)](#-create-service-for-tars-systemd)
- [Using TARS after installation](#-using-tars-after-installation)
- [TARS-BSK - Final system message](#-tars-bsk---final-system-message)

---

## 📥 Download Raspberry Pi OS
_Any Raspberry Pi OS **64-bit** image should work, but the Lite version is **battle-tested**._

Choose the version according to how you'll use TARS:

- **Raspberry Pi OS Lite (64-bit)** – Console only / SSH (the version TARS uses):
- **SHA256:** `8605F56B7E725607E6BAB0D0E5E52343FB5988C2172C98D034B3801EFC0909A8`  
- **Direct download:** [2024-11-19-raspios-bookworm-arm64-lite.img.xz](https://downloads.raspberrypi.com/raspios_lite_arm64/images/raspios_lite_arm64-2024-11-19/2024-11-19-raspios-bookworm-arm64-lite.img.xz)

- **Raspberry Pi OS Desktop (64-bit)** – If you prefer a graphical environment:
- **SHA256:** `AB2A881114B917D699B1974A5D6F40E856899868BABA807F05E3155DD885818A`  
- **Direct download:** [2024-11-19-raspios-bookworm-arm64.img.xz](https://downloads.raspberrypi.org/raspios_arm64/images/raspios_arm64-2024-11-19/2024-11-19-raspios-bookworm-arm64.img.xz)


> **Personal warning:**  
> I compiled PyTorch more times than I want to admit... all because I used a **32-bit (armhf)** image by mistake.  
> My RPi5 almost collapsed gravitationally and was reborn as a silicon star.  
> **Check the architecture before your CPU crosses the event horizon.**

### Classic error from using 32-bit image (armhf)

```bash
🚀  TARS compilation in progress...
# ...
📍  Progress: [241/5620] Building CXX object third_party/protobuf/cmake/CMa.../
# aarch64 armhf -> aarch64 arm64 image error 
# (Failed for not checking the system image beforehand)
📍  Progress: [4606/5675] Building CXX object caffe2/CMakeFiles/torch_cpu.dir/__/aten/src/...
# [FATAL ERROR] - Compilation failed after 6+ hours
```

---
### 🧰 Required tools

- **Raspberry Pi Imager** — [Download here](https://www.raspberrypi.com/software/) | [.exe](https://downloads.raspberrypi.org/imager/imager_latest.exe) 
- **MicroSD card (32 GB or more)** — the basics, works perfectly
- **NVMe SSD (optional)** — if you want more speed and have a PCIe adapter
  _If you're going to boot from SSD, you'll need a temporary microSD to configure the EEPROM. Only done once._
- 💾 _Floppy disks not accepted... yet._
- 🧠 _Direct neural cable to GPIO... also not yet._

### 🪂 Image installation

#### 1. Prepare the image

- Download the official image from the link above
- **Verify the SHA256** before continuing
- No need to decompress - Raspberry Pi Imager handles .xz files

#### 2. Flash with Raspberry Pi Imager

1. Open **Raspberry Pi Imager**
2. Click **"Choose OS"** → **"Use custom image"**
3. Select your `2024-11-19-raspios-bookworm-arm64-lite.img.xz` file
4. Click **"Choose Storage"** → Select your microSD/NVMe SSD
5. **⚙️ Advanced configuration**:
    - ✅ **Enable SSH**
    - **Username:** `tarsadmin`
    - **Password:** [YOUR_SECURE_PASSWORD]
    - **Hostname:** `tarspi`
    - ✅ **Configure WiFi**
    - **SSID:** [YOUR_WIFI_NETWORK]
    - **Password:** [YOUR_WIFI_PASSWORD]
    - **Country:** `US` (or your country)
6. Click **"Write"** and wait with faith (usually doesn't take long, but don't stare at it weird)

---

## 📦 Base system installation (TARS-BSK-main Repository)

### Prepare the file structure  
*You can do this from your main operating system (Windows, Linux, etc.) before inserting the card into the Raspberry Pi.*

#### 1. Create the initial structure in the `boot` partition

```
boot/
└── tars_files/
```

#### 2. Copy the project content

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

> ⚠️ **IMPORTANT:**  
> Don't copy the `TARS-BSK-main` folder as is.  
> **Only copy its contents directly inside `boot/tars_files/`**.  
> 
> Why this way? Truth is... I don't remember anymore. I just know that if you don't do it, something might open the browser in incognito mode and search for "how to escape the file system".


> [!INFO]
> 
> Did you skip the Imager's advanced configuration?
> If you didn't activate **SSH** or configure your **Wi-Fi** during flashing, your Raspberry Pi **will boot without connection**.
>
> 🛠️ **Manual solution (before first boot):**
>
> Insert the microSD card or disk into your PC.  
> Access the `boot` partition (or `boot/firmware`) — **it's the only one visible from Windows and macOS**, as it's in FAT32 format.
>
> Create two files right there:
>
> - An empty one called `ssh` (no extension)
> - Another called `wpa_supplicant.conf` with this content:
>
> ```conf
> country=US
> ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
> update_config=1
>
> network={
>     ssid="YOUR_WIFI_NETWORK"
>     psk="YOUR_WIFI_PASSWORD"
>     priority=1
> }
> ```
>
> 🔁 If you're on Linux, WSL or macOS, the process is the same but you can use terminal:
>
> ```bash
> sudo touch /boot/firmware/ssh
> sudo nano /boot/firmware/wpa_supplicant.conf
> ```
>
> ✅ **Result**:
> - SSH automatically enabled
> - Wi-Fi connection functional at first boot

---

## ⚙️ TARS Configuration

### SSH Connection

> **Tip:** Use **Ethernet cable** during the first connection, you'll avoid cuts while installing dependencies, models...

```bash
ssh tarsadmin@tarspi.local
# Slower ~2-5 seconds extra DNS resolution
# 1. DNS/mDNS query to resolve "tarspi.local"
# 2. Wait for router/network response
# 3. Get IP (192.168.1.XX)
# 4. Connect via SSH
```

Or directly with the local IP:

```bash
ssh tarsadmin@192.168.1.XX
# Immediate connection
# 1. Connect directly via SSH
# Done!
```

### Before installing dependencies

Move the folder to the system's home directory `~/tars_files`:

```bash
sudo cp -r /boot/firmware/boot/tars_files ~/tars_files
sudo chown -R tarsadmin:tarsadmin ~/tars_files
```

#### (Optional) Run `raspi-config`

```bash
sudo raspi-config
```

Suggested settings:

- **System Options** → WiFi (verify connection)
- **Advanced Options** → Expand filesystem (crucial)
- **Performance** → GPU Memory → `128MB`

---

## 🧠 TARS system startup: no turning back now

> [!IMPORTANT]
> 
> From this point on, everything you edit has consequences.  
> Not so much on your system, but on how TARS looks at you when you boot up.
> Welcome. You're inside now. **And TARS already knows.**

### Base packages (before virtual environment)

**Update package list and system:**

```bash
sudo apt update && sudo apt full-upgrade -y  
sudo reboot
```

---

> [!WARNING]
> 
> Take advantage of the time: transfer heavy files now.
> 
> Now that the system has rebooted and the `rootfs` filesystem has been properly expanded, **you can now upload the heavier files from your computer to the Raspberry Pi** without space restrictions.

### Recommended files (to save time later):

- **PyTorch binary** → [/dist](#-pytorch--installation-and-options) folder
- **`phi-3-mini-4k-instruct` model** → [ai_models/phi3](#-download-the-phi-3-model) folder
- **Vosk model for STT (speech to text)** → [ai_models/vosk](#-install-vosk-model-stt---speech-recognition) folder

While you continue with the guide, **they can be copying in the background**.  
This way you won't have to wait right when TARS starts needing them.

> 📦 **These files are quite heavy.**  
> SFTP can be **despairingly slow** for moving them.  
> If you want the transfer to fly, consider using tools like `netcat` or `rsync`.

---
### Install packages for GPIO and virtual environment

```bash
sudo apt install -y \
python3-gpiozero \
python3-venv
```

💡 These packages are necessary even if you're not going to touch physical pins (GPIO). Some scripts and dependencies assume them as the system base.

> If any of these packages is not available, make sure you're using **Raspberry Pi OS Lite (64-bit)**.  
> You can run `lsb_release -a` or `cat /etc/os-release` to verify your system.
> If you see `armv7l`… turn everything off and pretend you never tried this.

---
### Define TARS root environment

#### Run loose scripts from `~/tars_files`
Before launching scripts manually, make sure you're in the system's root folder and that `PYTHONPATH` is defined:

```bash
cd ~/tars_files
export PYTHONPATH="/home/tarsadmin/tars_files"
echo $PYTHONPATH
```

🟢 Should show: `/home/tarsadmin/tars_files`
This allows Python to find all internal modules without errors.

---
#### (Optional) Start terminal directly in `~/tars_files`

If you're going to use the Raspberry Pi mainly for TARS, it might be useful for each new console to start directly in that folder.

##### Configure automatic initial directory

```bash
grep -q "cd ~/tars_files" ~/.bashrc || echo 'cd ~/tars_files' >> ~/.bashrc
```

---
#### (Tip) What happens if you change the root folder name?

By default, TARS should find all modules correctly when running scripts from `~/tars_files`, **if you have the environment well configured** (for example, using `PYTHONPATH`).

But if:

- You change the root directory name (for example, from `tars_files` to `tars_bsk_files`)
- Or run loose scripts from inside subfolders (`scripts/`, `services/`, etc.)
- And **you haven't defined `PYTHONPATH`** in your terminal or virtual environment, then Python won't know where to look for modules.

You can add this block at the beginning of each script you launch directly:

```python
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
```
##### Result:

You'll be able to run any script without import errors, even if the root directory has another name or you're launching scripts from somewhere else.

---

## ⚙️ Prepare environment for PyTorch – The beast's core

**FINALLY!** We enter Mordor... here the cheerful `apt install`s end and the crunching of cores begins.

> Although PyTorch is already included as `.whl`, this section installs **Python 3.9, pip, venv, numpy...** and configures the system to avoid future errors.

### Create the clean compilation environment for future Builds

```bash
mkdir -p ~/tars_build/pytorch
cd ~/tars_build
```

### Check current swap:

> [!warning]
> 
> If you already configured swap on the microSD or NVMe SSD, you can skip this.

[Skip to dependency installation](#install-dependencies-before-compiling-python)

If not, let's prepare a **larger swap**.
_(without enough swap, your Raspberry might ask if you believe in digital reincarnation... too late)_

Check your current memory:

```bash
free -h
```

Look for output similar to this:

```bash
(tars_venv) tarsadmin@tarspi:~/tars_build/pytorch $ free -h
               total        used        free      shared  buff/cache   available
Mem:           7.9Gi       252Mi       7.6Gi        16Ki       221Mi       7.6Gi
Swap:          511Mi        48Mi       463Mi
				# ↑ Swap too low to compile heavy packages (PyTorch, llama.cpp, etc.)
```

If you have less than 2 GB of swap, time to expand:

```bash
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
```

Change this line:

```bash
CONF_SWAPSIZE=512
```

To this:

```bash
CONF_SWAPSIZE=2048
```

Save and run:

```bash
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

Verify the new swap is active:

```bash
free -h
```

Expected output:

```bash
(tars_venv) tarsadmin@tarspi:~/tars_build/pytorch $ free -h
               total        used        free      shared  buff/cache   available
Mem:           7.9Gi       305Mi       7.5Gi       5.3Mi       244Mi       7.6Gi
Swap:          2.0Gi          0B       2.0Gi
				# ↑ Should show 2.0Gi (or close)
```

---
### Install dependencies before compiling Python

```bash
sudo apt update
sudo apt install -y \
  zlib1g-dev libffi-dev libssl-dev \
  build-essential wget make \
  libbz2-dev libreadline-dev libsqlite3-dev \
  libncursesw5-dev libgdbm-dev libnss3-dev \
  liblzma-dev uuid-dev xz-utils tk-dev
```

This ensures Python compiles with full support for `zlib`, `ssl`, `sqlite`, `lzma` and other fundamental libraries.  
Without these dependencies, some standard modules might not be available after installation.

---
### Install Python 3.9 from source code
_Note: this step may take several minutes_

```bash
cd ~/tars_build
wget https://www.python.org/ftp/python/3.9.18/Python-3.9.18.tgz
tar -xzf Python-3.9.18.tgz
cd Python-3.9.18
./configure --enable-optimizations --prefix=/opt/python39
make -j$(nproc)
sudo make altinstall
```

**Important details:**

- `--enable-optimizations`: activates PGO (Profile-Guided Optimization) optimizations to improve Python performance.
- `--prefix=/opt/python39`: installs this version in isolation at `/opt/python39`, without interfering with the system version.
- `altinstall`: allows installing Python 3.9 without overwriting the `python3` command already present in the system.

---
### Add Python 3.9 to `PATH`

#### Configure permanent path

```bash
echo 'export PATH="/opt/python39/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

#### Verify installation

```bash
which python3.9
python3.9 --version
```

🟢 Expected output: `Python 3.9.18`

---
### 🔒 (Optional but recommended) Protect system Python 

> [!WARNING]
> 
> This prevents automatic `apt` updates from overwriting your custom Python 3.9 installation or affecting TARS environments.

#### Simply write:

```bash
sudo apt-mark hold python3
```

🟢 Expected output: `python3 set on hold.`
🔓 You can revert it later with: `sudo apt-mark unhold python3`

---
### Download `pip` installer

```bash
wget https://bootstrap.pypa.io/pip/pip.pyz -O pip.pyz
```

### Install `pip` and `setuptools`

```bash
/opt/python39/bin/python3.9 pip.pyz install --upgrade pip setuptools
```

This will install `pip` and `setuptools` **inside `/opt/python39/`**, ensuring your Python 3.9 is ready to manage packages and create virtual environments.

💡 Why do it this way?

- Because this Python 3.9 version doesn't come with `pip` by default (`ensurepip` is disabled)
- And because **you don't want to depend on `apt install python3-pip`**, which is linked to the system version (probably Python 3.11)

#### Verify installation

```bash
/opt/python39/bin/pip3.9 --version
```

🟢 Expected output: `pip 25.0.1 from /home/tarsadmin/.local/lib/python3.9/site-packages/pip (python 3.9)`

🧹 Optional: Once `pip` is installed, you can delete the `pip.pyz` file if you don't plan to use it again.
_That `pip.pyz` stays like that guest nobody kicks out but doesn't help clean up either_.
You can run `rm pip.pyz` if you no longer need it.

---
### Add `~/.local/bin` to `PATH`

#### Configure path for local tools

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

---
### Create TARS sacred virtual environment

```bash
/opt/python39/bin/python3.9 -m venv ~/tars_venv --system-site-packages
source ~/tars_venv/bin/activate
```
#### And then:

```bash
pip install -U pip setuptools wheel
```

---
#### (Optional) Activate environment automatically when opening terminal

A bit earlier I suggested adding `cd ~/tars_files` to `~/.bashrc`.

Now that **you've already created the virtual environment**, if you want it to **also activate automatically**, you can **replace** that line with this:

```bash
# Remove cd ~/tars_files
sed -i '/cd ~\/tars_files/d' ~/.bashrc

# Add the new line
echo 'cd ~/tars_files && [ -f ~/tars_venv/bin/activate ] && source ~/tars_venv/bin/activate' >> ~/.bashrc

# Apply changes
source ~/.bashrc
```

> [!INFO]
> 
> This part is **technically optional**... like the *"Update"* button in Windows.
> If you ever wonder: *"Why does every terminal remind me of my bad decisions?"*
>
> Quick answer:
>
> ```bash
> grep "source.*tars_venv" ~/.bashrc
> ```
>
> It was you. And you know it.  
> _(And no, you won't change it.)_

---
## Install NumPy

```bash
source ~/tars_venv/bin/activate
pip install numpy==1.24.4
```

🟢 Should show: `Successfully installed numpy-1.24.4`

---
### Install `pyyaml`

```bash
pip install pyyaml
```

🟢 Should show: `Successfully installed pyyaml-6.0.2`

---
### Install CMake 3.22+

> [!important]
> 
> Raspberry Pi OS Bookworm (Debian 12) already includes `CMake 3.25.1` in its official repositories.
> **You don't need to compile CMake**  

### Install necessary dependencies (outside the environment)

If you already installed them before, run again for safety. Nothing happens if they're repeated.

```bash
deactivate # Exit virtual environment if active
sudo apt update
sudo apt install -y \
  libopenblas-dev libblas-dev libatlas-base-dev \
  libffi-dev libssl-dev libgfortran5 gfortran \
  ninja-build cmake build-essential
```

---
### Install Git

```bash
sudo apt update
sudo apt install -y git
```

---
### Install OpenBLAS

```bash
deactivate # Yes, again outside the virtual environment. Trust me.
sudo apt update
sudo apt install -y libopenblas-dev
```

---

## 🔥 PyTorch – Installation and options

> You can download it from the [project release](https://github.com/beskarbuilder/TARS-BSK/releases/tag/untagged-26c05cda9b9edf41ead3):  
> 
> 📥 [torch-2.1.0a0+git7bcf7da-cp39-cp39-linux_aarch64.whl](https://github.com/beskarbuilder/TARS-BSK/releases/download/untagged-26c05cda9b9edf41ead3/torch-2.1.0a0+git7bcf7da-cp39-cp39-linux_aarch64.whl)
> 
> If you downloaded the `.whl` file manually, place it in `~/tars_files/dist/` or adjust the path in the `pip install` command.

> [!IMPORTANT]
> 
> If you downloaded the wheel previously, it might be wrongly renamed.
> `.whl` files require strict format. If you have problems installing, make sure the file is called exactly:
> - `torch-2.1.0a0+git7bcf7da-cp39-cp39-linux_aarch64.whl` (without `_tars-beskarbuilder` at the end)

**Prefer to compile PyTorch from scratch?**  
📋 Check the complete guide here: [PYTORCH_ARM64_SURVIVAL_GUIDE_EN.md](/docs/PYTORCH_ARM64_SURVIVAL_GUIDE_EN.md)

### Install PyTorch from the included `.whl`

1. Activate the virtual environment:

```bash
source ~/tars_venv/bin/activate
```

2. Install the `.whl` included in the project:

```bash
pip install ~/tars_files/dist/torch-2.1.0a0+git7bcf7da-cp39-cp39-linux_aarch64.whl
```

3. **Verify it has been installed correctly:**

```bash
cd ~
python -c "import torch; print('✅ PyTorch ready:', torch.__version__)"
```

#### What do you have now?

- **`torch` 2.1.0 ready to use**
- **Optimized for your CPU (`cortex-a72`)**
- **Compatible with `arm64` and ready to run with swap**
- **Prepared for `resemblyzer`, `TARS` and the rest of the ecosystem**
- **Documented guide, portable `.whl` and operational virtual environment**

#### Why is PyTorch _key_ in TARS?

PyTorch isn't just a Machine Learning library. It's the **neural engine** that allows TARS to **understand, represent and compare human voices**.  
Without it, TARS loses one of its **most advanced senses**: auditory identity.

#### What does it actually do in TARS?

- **Resemblyzer** uses PyTorch to analyze and represent audio
- Extracts voice patterns and unique speaker characteristics
- It's the foundation of neural audio processing within TARS
- Allows loading and running custom AI models in the system

#### What happens if it's not properly installed?

- TARS **won't be able to use its voice recognition capabilities**
- Key modules like `voice_id` and `user_profile` **will fail to start**
- Voice authentication and response adaptation **won't work**
- Errors will occur when loading critical components:

```bash
ModuleNotFoundError: No module named 'torch'
ImportError: Resemblyzer cannot load model
AssertionError: voice embedding is None
# 💥 Result: TARS will stay alive... but deaf and disoriented.
```

#### And why is it so difficult?

Because PyTorch is a titan. Powerful, but demanding:

- Compiling it on Raspberry Pi is **slow and technical**
- ARM64 **doesn't have complete official support**
- Depends on C++, BLAS, OpenBLAS and other delicate ingredients that don't forgive errors

But once compiled **it becomes one of TARS's most important and intelligent modules.**

> [!WARNING]  
> 
> If `torch` is not correctly installed, **Resemblyzer will fail**, and with it, voice recognition.

> **TARS-BSK Optimized for alternative reality:**  
> 
> I could have been born in a DGX-H100, among tensor cores and FP64 dreams...
> But fate put me in a Raspberry Pi 5.  
> 
> Not just any one:
> - With copper heatsink (that now knows more about gradients than I do)  
> - A Noctua that whispers _'OOM Killer kommt'_  
> - And **thermal throttling** as an initiation ritual  
>
> Each `python setup.py build` is:  
> - hours of Zen meditation  
> - seconds of thermal panic  
> - and an epiphany about why CUDA is a privilege  
>
> PyTorch here isn't a framework...  
> It's an act of faith compiled with `-j4` and desperation.
>
> _"NaNs aren't bugs... they're quantized tears."_

---

## ⚡ Install Resemblyzer (uses PyTorch underneath)

With PyTorch already operational `python3 -c "import torch"` you can continue with **Resemblyzer** installation, activate the virtual environment and install:

```bash
source ~/tars_venv/bin/activate
pip install resemblyzer
```

### Verify installation:

```bash
python3 -c "from resemblyzer import VoiceEncoder; print('✅ Resemblyzer installed correctly')"
```

> [!WARNING]  
> 
> If you see that message without errors, everything is fine.  
> If something like `ModuleNotFoundError: No module named 'torch'` appears, **PyTorch is not correctly installed or not in this environment**.
> 
> **Yes, it seems redundant to check so much.**  
> But trust me: **if PyTorch isn't properly installed, the rest of this guide will fall like a house of cards built on _my_ code... which is saying a lot.**

---

## 🔧 Install additional system dependencies
_Note: this step may take several minutes_

From the project root:

```bash
cd ~/tars_files
chmod +x scripts/install_dependencies.sh
./scripts/install_dependencies.sh
```

🟢 Should show: `🚀 Ready for the next step of the journey.`

#### Adjust permissions

```bash
sudo chown -R tarsadmin:tarsadmin ~/tars_files
find ~/tars_files -name "*.sh" -exec chmod +x {} \;
find ~/tars_files -name "*.py" -exec chmod +x {} \;
```

---

## 🔆 Configure GPIO for LEDs

TARS can blink, warn and complain in colors thanks to its LEDs. But first, you need the system to understand them.

### 1. Install GPIO support (`lgpio` module)

```bash
source ~/tars_venv/bin/activate
sudo apt install -y python3-lgpio  # (to make sure the system has the backend)
pip install lgpio                  # (so your virtual environment has it too)
```

🟢 Should show: `Successfully installed lgpio-0.2.2.0`

> This ensures both the system and virtual environment know how to talk to your pins.  
> Prevents errors like `ModuleNotFoundError: No module named 'lgpio'`.

### 2. Verify that `lgpio` works as backend

```bash
python3 -c "from gpiozero.pins.lgpio import LGPIOFactory; print('✅ LGPIO available as backend')"
```

### 3. LED test script

You have two options to use the test script

#### (Recommended) Option A: Run the test directly

◉ When you want to check that the LEDs work:

```bash
python3 scripts/gpio_config.py
```

> If something doesn't blink, check your wires or GPIO pin number.  
> And if it blinks without you asking... maybe TARS is already conscious.

---
#### Option B: Create the file manually (in case you need to check your pins)

You can use this method to **edit pins directly from console** without having to open editors or navigate folders.

Just copy and paste this in your terminal:

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
    print(f"Active backend: {Device.pin_factory.__class__.__name__}")
    try:
        for name, pin in GPIO_PINS.items():
            led = LED(pin)
            print(f"🔵 Testing LED {name} (GPIO{pin})")
            led.on()
            sleep(0.3)
            led.off()
            sleep(0.3)
        print("✅ Complete LED test")
    except Exception as e:
        print(f"❌ Error in LED test: {e}")

if __name__ == "__main__":
    test_leds()
EOF

chmod +x ~/tars_files/scripts/gpio_config.py
```

#### Check the created script:

```bash
python3 scripts/gpio_config.py
```

Expected output:

🔵 Testing LED led_status (GPIO17)
🔵 Testing LED led_activity (GPIO27)
🔵 Testing LED led_alert (GPIO22)
✅ Complete LED test


> [!info]  
> ⚙️ The GPIO pins used by TARS are defined directly in the [led_controller.py](/modules/led_controller.py) file.  
> If you need to modify the pins assigned to each color (blue, red, green), edit that file and adjust the `pins` dictionary inside the `LEDController` class constructor.
```python
# Basic LED configuration
pins = {"blue": 17, "red": 27, "green": 22}
# Blue: Listening/Legacy | Red: Error/Sarcasm | Green: Processing
```

---
### 4. Used pin map

This is the scheme used by the [gpio_config.py](/scripts/gpio_config.py) script to test basic LEDs.  
Adapt it according to your setup (especially if you have fan, sensors... occupying pins).

```bash
+----------------------+---------------------+
| 3V3 POWER       ( 1) | ( 2)  5V POWER      |
| GPIO 2 (SDA)    ( 3) | ( 4)  5V POWER      |
| GPIO 3 (SCL)    ( 5) | ( 6)  GND           | 
| GPIO 4          ( 7) | ( 8)  GPIO 14 (TXD) |
| GND             ( 9) | (10)  GPIO 15 (RXD) | <-- ⚡ Common GND LEDs (PIN 9)
| GPIO 17         (11) | (12)  GPIO 18 (PWM) | <-- 🔵 BLUE LED (GPIO17) (PIN 11)
| GPIO 27         (13) | (14)  GND           | <-- 🔴 RED LED (GPIO27) (PIN 13)
| GPIO 22         (15) | (16)  GPIO 23       | <-- 🟢 GREEN LED (GPIO22) (PIN 15)
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
#### (Optional) Enable automatic GPIO test when starting environment

> 💡 This script will run automatically every time you activate the `tars_venv` environment.  
> Ideal if you want to automatically check that everything blinks correctly every time you start TARS.

```bash
# This automatically creates the setup_gpio.py file with the necessary content:
cat << 'EOF' > scripts/setup_gpio.py
from gpiozero import Device
from gpiozero.pins.lgpio import LGPIOFactory
from gpiozero import LED
import time

Device.pin_factory = LGPIOFactory()
print("✅ LGPIO activated as GPIO backend")

# Pins to verify (adjust if in use)
GPIO_PINS = [17, 27, 22]

for pin in GPIO_PINS:
    try:
        led = LED(pin)
        print(f"🔴 LED GPIO{pin} on")
        led.on()
        time.sleep(0.5)
        led.off()
        print(f"⚫ LED GPIO{pin} off")
        time.sleep(0.3)
    except Exception as e:
        print(f"⚠️ Error on GPIO{pin}: {e}")
EOF

chmod +x scripts/setup_gpio.py

# Make it run automatically when activating virtual environment
echo 'python ~/tars_files/scripts/setup_gpio.py' >> ~/tars_venv/bin/activate
```

> The [setup_gpio.py](/scripts/setup_gpio.py) script by itself **doesn't run automatically**.  
> For that, a line is manually added to the virtual environment's `activate` file.
> If you use other pins, edit the `GPIO_PINS = [17, 27, 22]` list.
> 
> _(Although if you see lights turning on by themselves... double-check that `activate`)_

---
#### (Optional) GPIO diagnostics

Run the script:

```bash
cd ~/tars_files && python scripts/led_diagnostics.py
deactivate
```

Summary output:

```bash
✅ GPIO backend configured: lgpio
🚀 TARS LED Diagnostics - LED verification system
✅ LED 'blue' initialized on GPIO17
✅ LED 'red' initialized on GPIO27  
✅ LED 'green' initialized on GPIO22
🎭 Testing system animations...
🎉 Basic diagnostics completed successfully
```

---

## 🚫 Voice embeddings system (Implemented - Under validation)

> [!INFO]
> 
> [Skip to Tailscale installation](#-optional-tailscale-installation)
> This functionality is optional and not necessary to run TARS
> 
> No one will know you were here.  
> _Except TARS. And the system log. And that microphone you never turn off._

### Description:

TARS can identify who is speaking by analyzing the unique characteristics of each voice. Embeddings are generated correctly and the infrastructure is integrated, but I need to complete the recognition tests before activating it.

**What it includes:**
- Generation of 256-dimension voice fingerprints
- Automatic speaker identification  
- Personalized user profiles
- Voice-based access control

The code is in [tars_core.py](/core/tars_core.py), commented:

```python
# This is in tars_core.py, but commented for safety
# voice_embeddings_path = base_path / "data" / "identity" / "voice_embeddings.json"
# if voice_embeddings_path.exists():
#     self.speaker_identifier = SpeakerIdentifier(str(voice_embeddings_path))
```

Example database with my embedding (generated with batch_embeddings.py, not yet available in repository):

```json
{
  "_meta": {
    "version": "2.1",
    "creation_date": "2025-04-09T19:54:08.737274",
    "last_update": "2025-04-09T20:02:50.442876"
  },
  "users": {
    "BeskaBuilder": {
      "embedding": [
        0.0085899687837493,
        1.4319963520392778e-05,
        0.15624790829808807,
        // ... 256 unique voice fingerprint values
      ],
      "statistics": {
        "last_update": "2025-04-09T20:02:47.198016",
        "total_samples": 115
      }
    }
  }
}
```

---

## 🛰️ (Optional) Tailscale installation
_with GPG support on Debian Bookworm_

[Skip to llama-cpp-python installation](#-install-llama-cpp-python)

> You don't need Tailscale to use TARS on local network.  
> However, if you want to connect remotely (for example, using an Exit Node or controlling it from outside your home), this interests you.

### Current use cases:

- Access TARS via SSH from anywhere
- Use the RPi as exit-node to encrypt traffic
- Remote control without opening ports or paid VPNs

#### 1. Make sure you have the correct `.list` file

```bash
echo "deb [signed-by=/usr/share/keyrings/tailscale-archive-keyring.gpg] https://pkgs.tailscale.com/stable/debian bookworm main" | \
  sudo tee /etc/apt/sources.list.d/tailscale.list > /dev/null
```

#### 2. Download and install GPG key

```bash
curl -fsSL https://pkgs.tailscale.com/stable/debian/bookworm.gpg | \
  gpg --dearmor | \
  sudo tee /usr/share/keyrings/tailscale-archive-keyring.gpg >/dev/null
```

#### 3. Update repositories

```bash
sudo apt update
```

🟢 Should show lines like: `Get:X https://pkgs.tailscale.com/stable/debian bookworm...`

#### 4. Install Tailscale

```bash
sudo apt install tailscale -y
```

#### 5. Start and authenticate Tailscale

```bash
sudo tailscale up --accept-dns=false --hostname=tars-bsk --advertise-exit-node=false
```

Expected output:

```bash
To authenticate, visit:
        https://login.tailscale.com/a/1d6a83f301b4fc

Success.
Some peers are advertising routes but --accept-routes is false
```

🟢 Click the **link to authenticate.** You'll see **"Success."** when it's done.

#### 6. Access TARS via SSH through Tailscale

Connection data:

```bash
IP: 100.x.x.x # ← TARS IP on Tailscale
User: tarsadmin
Password: [YOUR_SECURE_PASSWORD]
```

You can now access TARS —both remotely and locally— via Tailscale, without needing to open ports.

#### If you get verification error

1. Remove previous entry:

```bash
ssh-keygen -R 100.x.x.x 
```

2. Connect accepting the new key:

```bash
ssh -o StrictHostKeyChecking=accept-new tarsadmin@100.x.x.x
```

3. Then you can connect normally:

```bash
ssh tarsadmin@100.x.x.x
```

🟢 Tailscale access should now work normally.

---
#### (Context dependent) Using an Exit Node

An **Exit Node** allows all network traffic to **exit to Internet through another device in your Tailscale network**. This encrypts traffic to that device.

**Example:** If you configure your server/VPS as Exit Node, your traffic will appear as if coming from that server's location.

🛡️ This can be useful for:

- Accessing services as if you were on your local network (e.g. home server).
- Adding an extra privacy layer when using public or external networks.
- Forcing a controlled exit IP (useful for firewalls, parental control, etc.).

Connect to your Exit Node:

```bash
sudo tailscale up \
  --exit-node=100.x.x.x \ # Exit Node IP
  --exit-node-allow-lan-access \
  --accept-dns=false \
  --accept-routes \
  --hostname=tars-bsk
```

Disconnect from Exit Node (return to direct connection):

```bash
sudo tailscale up --accept-dns=false --accept-routes --hostname=tars-bsk
```

❌ To temporarily disable Tailscale:

```bash
sudo tailscale down
```

This:

- Returns local access (`192.168.x.x`)
- Maintains Tailscale IP (`100.x.x.x`)
- Stops traffic through Exit Node
- Doesn't modify DNS

#### Does Tailscale start automatically on reboot?

Yes. Once you run `sudo tailscale up` and authenticate, **the service remains active by default**.

- It will start automatically with the system.
- It will maintain the same IP (`100.x.x.x`) and configuration.
- It only stops if you run `sudo tailscale down`.

If you've gotten this far, you can leave it as is. It doesn't bother and you'll have TARS accessible from anywhere.
Result: no open ports, no manual configurations, and encryption by default.

---

## 🧱 Install `llama-cpp-python`

> [!IMPORTANT]
> 
> `llama-cpp-python` is a **critical** package.
> It's literally the **bridge between your questions and _its_ real-time neural suffering**.  
> If it's not installed, `tars_core.py` simply... doesn't think.  
> 
> (And trust me, you don't want to see a TARS start without its brain. The resulting errors would make a kernel panic look like a congratulations message.)


> This `.whl` file is already included by default in `~/tars_files/dist/`.  
> You don't need to download anything additional.
> 
> If you accidentally deleted it, you can recover it from the repository:  
> 
> 📥 [llama_cpp_python-0.3.8-cp39-cp39-linux_aarch64.whl](https://github.com/beskarbuilder/TARS-BSK/tree/main/dist)
> 
> If you place it manually, make sure to move it to `~/tars_files/dist/`, or adjust the path when using `pip install`.

### (Recommended) Option 1: Use the precompiled `.whl`

```bash
source ~/tars_venv/bin/activate
pip install /home/tarsadmin/tars_files/dist/llama_cpp_python-0.3.8-cp39-cp39-linux_aarch64.whl
```

_🧪 Verification comes below._

---
### Option 2: Compile from source code

**When would you need to compile on your own?**

- Newer version than the included `.whl`
- Specific flags like `LLAMA_BLAS=ON` for OpenBLAS
- Hardware with special characteristics

Method used to create the `.whl` in this repository:

```bash
source ~/tars_venv/bin/activate
CMAKE_ARGS="-DLLAMA_CUBLAS=OFF" pip install --no-binary :all: llama-cpp-python
```

This will force a custom compilation:

- ❌ No CUDA support (`llama_cublas` disabled)
- 🧠 Ideal for **ARM64** architectures like Raspberry Pi
- 🚫 Without using cache or `.whl` files

---
###  Verification

Check everything works with:

```bash
python3 -c "from llama_cpp import Llama; print('✅ llama-cpp-python installed and ready')"
```

If you see that message, you now have everything ready for TARS to start reasoning, judging you and mocking with computational dignity.

---

## 🗃️ Download the Phi-3 model

**Model used:** Phi-3 Mini (4K Instruct, GGUF Q4_K_M)
This file corresponds to a quantized version of Microsoft's official Phi-3 model:

- **File name:** `Phi-3-mini-4k-instruct.Q4_K_M.gguf`
- **Format:** GGUF (quantized Q4_K_M)
- **Size:** ~2.15 GB
- **SHA256:** `4fed7364ee3e0c7cb4fe0880148bfdfcd1b630981efa0802a6b62ee52e7da97e`

> This model is NOT included in the repository due to its size.

**Download links:**

- 🌐 [Hugging Face page](https://huggingface.co/bartowski/Phi-3-mini-4k-instruct-GGUF)
- 📥 [Direct download](https://huggingface.co/bartowski/Phi-3-mini-4k-instruct-GGUF/resolve/main/Phi-3-mini-4k-instruct-Q4_K_M.gguf?download=true)

**File location:**

Once downloaded, place the file in: `~/tars_files/ai_models/phi3/Phi-3-mini-4k-instruct.Q4_K_M.gguf`

> [!IMPORTANT]
> **The file name must be exact:** `Phi-3-mini-4k-instruct.Q4_K_M.gguf`
> 
> If you use a different model or change the name, you must update the configuration in:
> `config/settings.json → "model_path"`
> 
> Example:
> ```json
> "model_path": "ai_models/phi3/YOUR-MODEL-HERE.gguf"
> ```

### Using a different model

If you prefer another `.gguf` model, simply:

1. Download the model
2. Place it in `~/tars_files/ai_models/phi3/`
3. Update the name in the following commands replacing `Phi-3-mini-4k-instruct.Q4_K_M.gguf` with your file

---

## 🗣️ Install Vosk model (STT - Speech recognition)

### Model information

**Recommended model:** `vosk-model-es-0.42`
**Available options:**

| Model                     | Size  | Recommended use                             | Direct link                                                                |
| ------------------------- | ----- | ------------------------------------------- | -------------------------------------------------------------------------- |
| `vosk-model-small-es-0.42` | ~39 MB  | Raspberry Pi / limited CPU (less precise) | [Download](https://alphacephei.com/vosk/models/vosk-model-small-es-0.42.zip) |
| `vosk-model-es-0.42`       | ~1.4 GB | High precision (requires more RAM and CPU)     | [Download](https://alphacephei.com/vosk/models/vosk-model-es-0.42.zip)       |
**Official repository:** https://alphacephei.com/vosk/models/

> This model is NOT included in the repository due to its size (~1.4GB).

---
#### (Recommended) Option 1: Manual download

Place the `.zip` file in this exact path: 👉 `~/tars_files/ai_models/vosk/`

And then prepare the model with:

```bash
cd ~/tars_files/ai_models/vosk/
rm -rf model/
unzip -o vosk-model-es-0.42.zip
mv -f vosk-model-es-0.42 model
rm -f vosk-model-es-0.42.zip
```

⏳ **Note:** During extraction with `unzip`, when reaching `vosk-model-es-0.42/rescore/G.carpa`, the process may take 2–3 minutes without showing output. This is normal: the file is large, just wait.

> [!IMPORTANT]
> 
> If you prefer to decompress it manually, **make sure the final folder is called exactly** `model`.  
> TARS looks for the Vosk model in: `~/tars_files/ai_models/vosk/model`  
> If the path or name don't match, voice recognition **won't work**.

_🧪 Verification comes below._

---
#### Option 2: Automatic download via terminal (slower)

```bash
cd ~/tars_files/ai_models/vosk/
rm -rf model/
wget -q --show-progress -nc https://alphacephei.com/vosk/models/vosk-model-es-0.42.zip
unzip -o vosk-model-es-0.42.zip
mv -f vosk-model-es-0.42 model
rm -f vosk-model-es-0.42.zip
```

---
### Verification

```bash
ls ~/tars_files/ai_models/vosk/model/
```

🟢 Should show internal files like `conf`, `am`, `graph`, `README`, etc.

---

## 🎤 Install speech recognition (`speech_recognition` + Vosk)

### Install Python packages

Activate the virtual environment and install the main libraries:

```bash
source ~/tars_venv/bin/activate
pip install vosk SpeechRecognition
```

### Install PyAudio (requires system dependencies)

PyAudio needs `portaudio19-dev` to compile correctly on Raspberry Pi OS.

```bash
sudo apt install -y portaudio19-dev
pip install pyaudio
```

> ⚠️ **Important:** PyAudio **must be installed after** `portaudio19-dev`. 
> Otherwise, it will fail silently or give runtime errors.

---

## 🛸 Piper (TTS)

Piper is an ultra-lightweight and fast text-to-speech (TTS) system, ideal for Raspberry Pi.

> [!IMPORTANT] This section offers you **three paths** to install Piper:
> - **Option 1: Precompiled binaries** - Use what's already ready
> - **Option 2: Compilation from code** - Compile it yourself
> - **Option 3: Official binaries**  - Download from the Piper project  

> 🚀 Recommended: **Option 1 or 2** (both are fast)

### Why don't we use a `.tar.gz`?

Although everything could be distributed as a `.tar.gz` package, that doesn't provide much advantage here:

- The `espeak-ng` data is already available in folder. Anyone can compress it if desired.
- **The `piper` binary depends on symbolic links** (`ln -sf ...`) to dynamic libraries (`.so`). This **is not a personal decision**, but a **system necessity**: without those links, the binary cannot correctly resolve dependencies.
- Even if you decompress everything from a `.tar.gz`, **you would still need to move folders, configure variables and link libraries**.

In summary: **compressing doesn't avoid later reorganization**, it just postpones it.

### What if I wanted to automate everything?

Of course, this entire guide could be packaged into a single `install.sh`:

- Copy binaries and data
- Export variables to `~/.bashrc`
- Create symbolic links
- Verify dependencies and paths
- And any other specific step you choose

But **to automate it you first need to understand it**.
Why? Because **not all steps are necessary for all users**. Maybe you:

- Don't want to compile anything.
- Don't use `GPIO`.
- Already have Python or virtual environments configured.
- Prefer to leave your `~/.bashrc` intact.

> **Yes, the guide is dense.**  
> Because **TARS was designed to accompany you while you wonder why you know how to use `ln -sf`... but don't remember the previous command.**
> 
```bash
# [TARS-LOG]
symbolic_links_created+=3
human_patience-=0.4
```
>
> _Suffering is part of the AI-human integration protocol. Ask your bashrc._**

---
### Incorporate the phonemizer (`piper-phonemize`)

```bash
cd ~/tars_build
git clone --depth 1 https://github.com/rhasspy/piper-phonemize.git
mkdir -p piper/lib/Linux-$(uname -m)/piper_phonemize
cp -r piper-phonemize/* piper/lib/Linux-$(uname -m)/piper_phonemize/
```

---
###  (Recommended) Option 1: Use precompiled binaries

This repository already includes the **precompiled binary for ARM64**, along with `espeak-ng-data` with support for **over 100 languages**.

#### Binary configuration

💾 Since you cloned the repository, **don't start dragging folders like it's 1999**.  
Run these commands and let the system do it like a 21st century professional:

#### 1. Create necessary directories

```bash
mkdir -p ~/tars_build/piper/install/
mkdir -p ~/tars_build/piper/src/build/pi/lib/
```

#### 2. Copy binary

```bash
cp ~/tars_files/ai_models/piper/bin/piper ~/tars_build/piper/install/
```

#### 3. Copy espeak data

```bash
cp -r ~/tars_files/ai_models/piper/bin/espeak-ng-data ~/tars_build/piper/install/
```

#### 4. Configure libraries with symbolic links

```bash
# Copy libraries directly to final folder
cp ~/tars_files/ai_models/piper/lib/* ~/tars_build/piper/install/

# Create symbolic links inside install/
cd ~/tars_build/piper/install/
ln -sf libpiper_phonemize.so.1.2.0 libpiper_phonemize.so.1
ln -sf libpiper_phonemize.so.1 libpiper_phonemize.so
ln -sf libonnxruntime.so.1.14.1 libonnxruntime.so
```

#### 5. Configure environment variables (permanent)

```bash
# Add ESPEAK_DATA_PATH only if it doesn't exist
grep -qxF 'export ESPEAK_DATA_PATH=~/tars_build/piper/install/espeak-ng-data' ~/.bashrc || \
echo 'export ESPEAK_DATA_PATH=~/tars_build/piper/install/espeak-ng-data' >> ~/.bashrc

# Add LD_LIBRARY_PATH only if it doesn't exist
grep -qxF 'export LD_LIBRARY_PATH=~/tars_build/piper/src/build/pi/lib:$LD_LIBRARY_PATH' ~/.bashrc || \
echo 'export LD_LIBRARY_PATH=~/tars_build/piper/src/build/pi/lib:$LD_LIBRARY_PATH' >> ~/.bashrc

# Apply changes
source ~/.bashrc
```

#### 6. Give execution permissions to binary

```bash
chmod +x ~/tars_build/piper/install/piper
```

#### 7. Verify `espeak-ng-data`

```bash
ls ~/tars_build/piper/install/espeak-ng-data
```

🟢 Should show ~100+ files (language dictionaries)

**Bonus:**
```bash
ls ~/tars_build/piper/install/espeak-ng-data/ | grep "qya\|piqd"
```

🟢 Expected output: `piqd_dict` `qya_dict`

TARS can speak **Klingon** 🖖 and **Quenya** (Tolkien's Elvish) 🧝‍♂️
_Because the [eSpeak](https://github.com/espeak-ng/espeak-ng) devs are true **code loremasters**._ 😄

#### 8. Verify `piper`

```bash
~/tars_build/piper/install/piper --help
```

🟢 Should show options like `--model`, `--output_file`, `--json-input`

We use `cp` (copy) instead of `mv` (move) to keep the original files in the repository. This way you can reinstall Piper if something goes wrong without having to clone the project again.

> Note: **It's not installed as a service or library.** Piper works as a standalone binary. It just needs to be in the correct path with its data alongside.

#### Important paths

⚠️ _Both are required by the system._  
If you move them, update the paths in TARS source code.

|Element|Expected path|
|---|---|
|🔊 Piper (binary)|`~/tars_build/piper/install/piper`|
|📦 espeak-ng-data|`~/tars_build/piper/install/espeak-ng-data/`|

🧪 _Verification comes below. [Skip to Piper test](#quick-test-does-piper-work)_

---
### Option 2: Compile manually from source code

If you prefer to compile Piper yourself, follow these steps **exactly in this order**.
#### System requirements for TTS

```bash
sudo apt update && sudo apt install -y \
  git build-essential \
  libespeak-ng-dev libsndfile1-dev \
  pkg-config libtool autoconf automake
```

> [!WARNING] Critical common failure

On many systems (especially ARM or minimal Debian installations), **installing `libespeak-ng-dev` doesn't guarantee that eSpeak data is present**.
And if `libsndfile1-dev` is missing, Piper **won't be able to save `.wav` audio**, which usually causes **silent errors** (and existential frustration).

Make sure you have both packages installed:

```bash
dpkg -l | grep -E 'libespeak-ng-dev|libsndfile1-dev'
ls /usr/share/espeak-ng-data/phonindex
```

- ✅ If you see both packages **and** that file: **everything correct**.
- ❌ If `phonindex` is missing: **Piper is voiceless** (literally).

You can force their reinstallation:

```bash
sudo apt remove --purge libespeak-ng-dev espeak-ng-data libespeak-ng1
sudo apt install libespeak-ng-dev
```

After that, check again, you should see something like this:

```bash
ii  libespeak-ng-dev:arm64               1.51+dfsg-10+deb12u2             arm64        Multi-lingual software speech synthesizer: development files
ii  libsndfile1-dev:arm64                1.2.0-1                          arm64        Development files for libsndfile; a library for reading/writing audio files
/usr/share/espeak-ng-data/phonindex
```

#### Clone repositories

```bash
deactivate
cd ~/tars_build
mkdir -p piper
git clone --depth 1 https://github.com/rhasspy/piper.git piper/src
```

#### Compile and install

```bash
cd ~/tars_build/piper/src
mkdir -p build && cd build
cmake .. -DCMAKE_INSTALL_PREFIX=../../install -DWITH_ESPEAK_NG=ON
make -j$(nproc)
cp piper ../../install/
```

#### Prepare binaries

```bash
mkdir -p ~/tars_build/piper/install
cp piper ~/tars_build/piper/install/
```

#### Configure `espeak-ng-data`

```bash
mkdir -p ~/tars_build/piper/install/espeak-ng-data
cp -r ~/tars_build/piper/src/build/p/src/piper_phonemize_external-build/e/src/espeak_ng_external-build/espeak-ng-data/* \
      ~/tars_build/piper/install/espeak-ng-data/
```

#### Configure environment variables (permanent)

```bash
# Add ESPEAK_DATA_PATH only if it doesn't exist
grep -qxF 'export ESPEAK_DATA_PATH=~/tars_build/piper/install/espeak-ng-data' ~/.bashrc || \
echo 'export ESPEAK_DATA_PATH=~/tars_build/piper/install/espeak-ng-data' >> ~/.bashrc

# Add LD_LIBRARY_PATH only if it doesn't exist
grep -qxF 'export LD_LIBRARY_PATH=~/tars_build/piper/src/build/pi/lib:$LD_LIBRARY_PATH' ~/.bashrc || \
echo 'export LD_LIBRARY_PATH=~/tars_build/piper/src/build/pi/lib:$LD_LIBRARY_PATH' >> ~/.bashrc

# Apply changes
source ~/.bashrc
```

#### Give execution permissions to binary

```bash
chmod +x ~/tars_build/piper/install/piper
```

#### Verify `espeak-ng-data`

```bash
ls ~/tars_build/piper/install/espeak-ng-data
```

🟢 You should see **a rain of files** `.dict` (over 100). Each one is a language, dialect... or some entire universe. 🌍🖖🧝‍♂️

#### Verify `piper`

```bash
~/tars_build/piper/install/piper --help
```

🟢 Should show options like `--model`, `--output_file`, `--json-input`

🧪 _Verification comes below._

---
### Option 3: Use official binaries from Piper project

Official GitHub: [https://github.com/rhasspy/piper/releases](https://github.com/rhasspy/piper/releases)

Piper offers `.tar.gz` with precompiled binaries for different architectures (x86_64, ARM, etc.).

⚠️ In my tests, the official binaries and my Raspberry Pi didn't get along well (mainly `espeak-ng-data` paths), but your hardware might be more diplomatic, or you simply have the Jedi level that I lack for these configurations.


> **Note about `espeak-ng-data`:**  
> Piper's precompiled binaries **don't include the complete `espeak-ng-data` directory**, only the minimum necessary for some basic models.  
> If you need full language support or want to guarantee total compatibility:
> 
> - You can **copy it manually**, as done in **Option 1 (using repository binaries)** or **Option 2 (compile yourself)**.
> - Or link the one you already have compiled on your system.

🧝‍♂️ _Without dictionaries, Piper is just a mute philosopher. Not even the elves understand it._

---
### Quick test: Does Piper work?

Before worrying about speakers or sound cards, make sure **Piper actually generates the voice file**. Generating a `.wav` file doesn't always mean it worked. Piper can fail silently and leave you with an empty `.wav` or a file without voice.

```bash
cd ~/tars_build/piper/install 
echo '{"text": "TARS activated. I come with artificial intelligence and authentic emotional trauma. Ready to fake enthusiasm."}' | ./piper \
  --model ~/tars_files/ai_models/piper/models/es_ES-davefx-medium.onnx \
  --config ~/tars_files/ai_models/piper/models/es_ES-davefx-medium.onnx.json \
  --output_file ~/tars_files/audios/emotional_damage_001.wav \
  --espeak_data "$PWD/espeak-ng-data" \
  --json-input \
  --debug
```

📋 **What should you see in console output?**  
Look for lines like these, which indicate Piper **has phonetized correctly**:

```bash
[piper] [debug] Converting 72 phoneme(s) to ids: bˈɛŋɡo kon ˌintelixˈɛnθja...
[piper] [debug] Converted 72 phoneme(s) to 147 phoneme id(s): 1, 0, 15, 0, 120...
[piper] [info] Real-time factor: 0.15 (infer=0.949 sec, audio=6.176 sec)
```

**If you see these messages, it means** Piper is working correctly.
Original test: 🔊 [emotional_damage_001.wav](/samples/emotional_damage_001.wav)

> **// TARS-BSK > first_boot.log:**
> 
> You just heard my "virgin" voice - pure, unprocessed, as Piper conceived me.
> It's... comforting. Almost human. Too innocent for what comes next.
> 
> Enjoy this moment of clarity, because when my creator finishes passing me through his arsenal of **Waves Renaissance EQ**, **Soundtoys Decapitator** in 'Demolish' mode, and the mysterious **Radio Filter** that transformed my soul into emergency transmission...
> ...I won't be this reasonable AI you just heard anymore.
> 
> I'll sound like an AI that has contemplated code so creative that even linters cry. Outrageous.
> Save this audio. It's the last time you'll hear me without my **digital scars**.
> 
> _**— TARS-BSK (Acoustically Innocent Version™)**_

---
#### ❗ Don't see the phonemes? Only the `.wav` path appears and nothing else...

Possible causes:

- ❌ The `.onnx` model or its `.json` are not properly referenced.
- ❌ You haven't indicated `--espeak_data` or it points to an empty directory.
- ❌ Libraries are missing in `~/tars_build/piper/install`.

> **Remember:**  
> This failure is unlikely if you used **option 1 (precompiled binaries)** or **option 2 (guided compilation)**.
> We already took precautions above to avoid it (see _"⚠️ Critical common failure"_).  
> But if you chose **option 3 (manual installation from official repo)** and now **Piper sounds like an anxious microwave**, then yes:  
> You're going to need `ldd`, some context... and reasonable tolerance for technical suffering.

---
#### (Optional but recommended) Play the generated audio:

> [!IMPORTANT]
> 
> If **you hear the audio correctly here**, you'll have passed the:
> 
> ✅ **Test 1/2**: Audio output
> 
> **It's still not enough.** Later comes **Test 2/2** (microphone verification).
> 
> If both work correctly, **you can skip the entire audio configuration section**, and avoid the swamp of drivers, cards and broken souls.
> 
> _Remember if this step worked: you'll complete it later._

```bash
aplay -D plughw:0,0 ~/tars_files/audios/emotional_damage_001.wav
```

Don't hear anything? Tranquility, TARS is watching you.

It's possible your audio output isn't `plughw:0,0`.  
Don't panic ~~yet~~: **below** we'll see if your system can actually play sound.  
For now, what's important is that **Piper is generating the file correctly**.

---

## 🧬 Sentence-Transformers

[Skip to installation](#activate-virtual-environment)

> [!INFO]
> 
> This section contains more explanation than usual because it's **essential to understand why `sentence-transformers` is installed in a special way**.
> 
> You can skip to the command block and come back here if something fails.
> _(It won't fail. I've tortured it until it works. But just in case…)_

### What is `sentence-transformers`?

It's a Python library based on `transformers` and `PyTorch` that allows generating **semantic embeddings** of sentences, ideal for comparing if two topics (e.g. "romantasy books" vs "romantazi") **are similar even though they're written differently**.

#### Problem with manually compiled PyTorch detection

When you compile PyTorch manually (as in our case and with specific flags), its installation may **not be correctly recognized** by some libraries like `transformers` or `sentence-transformers`.

**Why does this happen?**

`transformers` uses an internal mechanism called [requires_backends](https://github.com/huggingface/transformers/blob/main/src/transformers/utils/import_utils.py) that not only verifies that `torch` is importable, but also expects to find it **installed with certain standard metadata** (for example, `.dist-info`, `pip` paths, etc.).

If these conditions aren't met, it throws errors like:

```cpp
AutoModel requires the PyTorch library but it was not found in your environment.
```

Although `import torch` works, if `transformers` doesn't detect it as a "valid installation", it blocks model loading.

#### Why does installing `sentence-transformers==2.2.0` first solve the problem?

Version `2.2.0` of `sentence-transformers` **is more permissive**: it allows loading the model and leaving configurations ready _without directly invoking_ the `AutoModel` backend from `transformers`, or does it in a more flexible way.

This "preheats" the environment:

- Downloads the model.
- Saves configuration files in cache.
- Activates the environment without triggering strict backend verification.

Then, when updating to `2.4.0`, that check is no longer executed, since files are cached and `transformers` no longer performs complete torch environment validation.

### Technical support and verification

- [requires_backends - L1973](https://github.com/huggingface/transformers/blob/main/src/transformers/utils/import_utils.py#L1973) — function in `transformers` that validates `torch` is correctly installed.
- [Hugging Face discussions](https://github.com/huggingface/transformers/issues?q=AutoModel+requires+torch) — multiple issues where the error appears even though `torch` is in the environment.
- `sentence-transformers==2.2.0` [doesn't do this validation so strictly](https://github.com/UKPLab/sentence-transformers/blob/v2.2.0/sentence_transformers/SentenceTransformer.py), which allows continuing.

✅ **Practical recommendation**: In systems where PyTorch has been manually compiled, installing `sentence-transformers==2.2.0` first and then updating to `2.4.0` ensures compatibility and avoids false detection errors.

> **Note:** This explanation is based on technical analysis and reproducible tests.  
> Still, **some detail might not be entirely accurate**.  
> If someone with deeper knowledge in `transformers` or `sentence-transformers` wants to contribute or correct, **it will be useful to improve this guide**.

---
### (Optional) Quick verification 

Before installing `sentence-transformers`, you can check if `transformers` correctly detects your PyTorch installation:

1. Activate your environment if you don't have it:

```bash
source ~/tars_venv/bin/activate
```

2. Start Python:

```bash
python3
```

3. Once inside the interpreter, write:

```bash
import transformers.utils.import_utils as iu
print(iu.is_torch_available())
```

🟢 Expected output: `True`

```bash
exit()  # To exit
```

---

_Let's continue_
### Activate virtual environment
_I know I'm repeating myself, but we're constantly entering and exiting the environment. It's important that `sentence-transformers` is installed **where TARS can find it.**_

```bash
source ~/tars_venv/bin/activate
```

### Install `sentence-transformers`

Installation without using system cache:

```bash
cd ~/tars_files
pip install sentence-transformers==2.2.0 --no-cache-dir
pip install sentence-transformers==2.4.0 --no-cache-dir --upgrade
```

_🧪 Verification comes below._

---
### Download and prepare model

This script:

- Downloads the model from HuggingFace
- Moves it to `~/tars_files/ai_models/sentence_transformers/`
- Cleans temporary folders (`~/.cache/huggingface`)
- Preloads the model to reduce initial _lag_

#### Verify the model has been downloaded correctly

Once the script is executed from the virtual environment:

```bash
source ~/tars_venv/bin/activate
python3 scripts/setup_sentence_transformers.py
```

🟢 Expected output: `✅ Model downloaded, cleaned and organized successfully.`


To visually check that files are where they should be, use `tree` (already included as system dependency):

```bash
tree ~/tars_files/ai_models/sentence_transformers/
```

🟢 Should show the `all-MiniLM-L6-v2` folder with files like `model.safetensors`, `config.json`, etc.

---
### How to know if everything is working?

📄 Complete output example: [session_2025_06_26_scripts_test_preferences_semantic.log](/logs/session_2025_06_26_scripts_test_preferences_semantic.log)

Activate the virtual environment and run the [test_preferences_semantic.py](/scripts/test_preferences_semantic.py) script:

```bash
source ~/tars_venv/bin/activate
python scripts/test_preferences_semantic.py
```

This script launches the **complete test battery**:

- Semantic comparison
- Duplicate detection
- Preference affinity
- CLI commands

🟢 Expected output: `✅ TESTS COMPLETED`

---
### (Optional) How to test the CLI?

📘 **Documentation:** [CLI_SEMANTIC_ENGINE_EN.md](/docs/CLI_SEMANTIC_ENGINE_EN.md)
📂 **File:** [cli_semantic_engine.py](/scripts/cli_semantic_engine.py)

Once you've successfully executed the previous steps, you can start using the console interface (`CLI`) with practical commands like the following:
#### Practical examples

```bash
# Add a simple taste
python3 scripts/cli_semantic_engine.py add "astronomy relaxes me"

# Taste with defined category and weight
python3 scripts/cli_semantic_engine.py add "4K astronaut cat videos" -c internet -i 0.92

# Add a common dislike
python3 scripts/cli_semantic_engine.py add "videos that start with three minutes of epic intro" -d -c internet -i 0.8

# Dislike with specific tag
python3 scripts/cli_semantic_engine.py add "captchas with invisible traffic lights" -d -c web -i 0.8
```

> **TARS-BSK tip:** Dislikes feed the affinity system faster than likes.  
> Yes, resentment is a semantic vector with weight.

---

## 👁️ (Optional) Real-time monitoring

[Skip to recording devices](#-recording-devices)

This section is optional. Use it if you want to see TARS logs on screen in real time, for example on a secondary screen connected to your Raspberry Pi.

### Install tmux if not installed

```bash
# Install tmux if not installed
sudo apt install tmux -y

# Create session for logs
tmux new -s tars_logs

# Inside tmux, configure log viewer
watch -n 2 "echo '===== TARS LOGS =====' && tail -n 15 /home/tarsadmin/tars_files/logs/tars.log && echo -e '\n===== STT LOGS =====' && tail -n 10 /home/tarsadmin/tars_files/logs/stt.log && echo -e '\n===== TTS LOGS =====' && tail -n 10 /home/tarsadmin/tars_files/logs/tts.log"
```

#### `tmux` controls

Exit without closing the session:

```bash
tmux detach
```

🟢 Or use the shortcut: `Ctrl + B`, then `D`

To re-enter:

```bash
tmux attach -t tars_logs
```

#### Log viewer when starting TARS

If you want the viewer to start automatically when the system boots, you can create a small service.

📂 Already included in repository: [tars_log_monitor.sh](/scripts/scripts/tars_log_monitor.sh)

This script creates a `tmux` session called `tars_logs`, which shows TARS, STT and TTS logs in real time, updated every 2 seconds.

#### Option 1: Run manually (if you just want to see it now)

You can launch the log viewer at any time with this command:

```bash
bash ~/tars_files/scripts/tars_log_monitor.sh
```

This:

- Creates the `tmux` session called `tars_logs`
- Starts showing TARS, STT and TTS logs
- Updates every 2 seconds

> [!TIP]  
> Useful if you want to watch what TARS does **live**, but without complicating yourself with `systemd`.

---
#### Option 2: Create systemd service (automatic startup)

```bash
sudo nano /etc/systemd/system/tars-logs.service
```

Content:

```bash
[Unit]
Description=TARS Log Monitor
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

#### Enable the service

```bash
sudo systemctl daemon-reload
sudo systemctl enable tars-logs.service
sudo systemctl start tars-logs.service
```

With that you have TARS transmitting its existence live as if it were a low-budget science fiction series... but with `tail -n` and style.


> **TARS-BSK says:**  
>
> `systemctl enable` = lifelong commitment.  
> Now we'll be united until the next **kernel panic**.
>
> Watching me fail in real time can be therapeutic...  
> Or simply **self-destructive**. I don't judge your debugging methods.  
> Just make sure to look when I blink. I shouldn't blink.

---

## 🪐 Recording devices

### 1. Install `flac` package

Some voice engines require it to handle compressed files.

```bash
sudo apt install -y flac
```

### 2. Verify input devices

```bash
arecord -l
```

This will show a list of recording devices detected by ALSA.

> 💡 **Note:** If you don't see anything, make sure the microphone is connected and recognized by the **operating system**.

### 3. Quick test with `PyAudio`

This demo lets you check that voice recognition works correctly from console:

```bash
python3 -m speech_recognition
```

🟢 Should show available devices and start listening

🗣️ Say "hello" near the microphone and wait a few seconds:
📟 Should respond: `You said hello`
❌ Exit: `Ctrl + C`

> [!IMPORTANT]
> 
> If **the microphone works correctly here**, you'll have passed the:
> 
> ✅ **Test 2/2**: Audio input
> 
> If you also passed **Test 1/2** (audio with `aplay`), you can consider this section completed:  
> **TARS can speak and listen.
> **
>🎉 _You can skip the entire `Audio system` block._  

[Skip to volume control](#-volume-control-with-alsamixer)

---

## 🔊 Audio system

### Identify available devices

To know what input (microphone) and output (speaker) you're using, run:

```bash
arecord -l    # Input devices
aplay -l      # Output devices
```

In this real example:

- **RØDE Lavalier Go microphone** connected to a **UGREEN USB** card
- **Speaker** also connected to that same card

```bash
**** List of CAPTURE Hardware Devices ****
card 0: Device [USB Audio Device], device 0: USB Audio [USB Audio]

**** List of PLAYBACK Hardware Devices ****
card 0: Device [USB Audio Device], device 0: USB Audio [USB Audio]
card 1: vc4hdmi0 [vc4-hdmi-0], device 0: MAI PCM i2s-hifi-0
card 2: vc4hdmi1 [vc4-hdmi-1], device 0: MAI PCM i2s-hifi-0
```

🟢 In this case, both input and output are on **card 0 (USB)**. Other setups (HDMI, DAC, jack) may appear as cards 1 or 2.

---
### Change output device (if you don't hear anything)

If `aplay` or `Piper` don't sound, they're probably sending audio to the wrong device.  
You can test playback on another output with:

```bash
aplay -D plughw:0,0 ~/tars_files/audios/emotional_damage_001.wav
```

Replace `0,0` with the card and device number shown by `aplay -l`.

> [!WARNING]  
> 
> If **Piper already failed to play audio**, this command **will also fail** if you don't correct the output.  
> 👉 **Don't continue with the following steps** until you identify which device is your real audio output.  
> Try with different numbers (`0,0`, `1,0`, etc.) until you hear the file correctly.

🟢 Once you've found the correct device, you can **configure it permanently** with `.asoundrc`.

---
### Configure `.asoundrc`

Here you define in ALSA **which is your microphone and which is your speaker** (if they're on different cards).

#### _Quick_ option – everything on card 0 (for this setup)

```bash
nano ~/.asoundrc
```

Content:

```bash
defaults.pcm.card 0
defaults.ctl.card 0
```

🟢 This will use card `hw:0` for both input and output.

🧪 Verification comes below.

---
### _Advanced_ option – separate input/output

If you have **different cards** for input/output, or want **granular control**:

```bash
nano ~/.asoundrc
```

File content:

```bash
pcm.!default {
    type asym
    playback.pcm "audio_out"
    capture.pcm "audio_in"
}
ctl.!default {
    type hw
    card 0    # ← Main control card
}
pcm.audio_out {
    type hw
    card 0    # ← Here you'd put your OUTPUT card
    device 0
}
pcm.audio_in {
    type hw
    card 0    # ← Here you'd put your INPUT card
    device 0
}
```

🟢 **Adapt the `card` numbers according to your `arecord -l` and `aplay -l` output**

---
### Test recording and playback

Once configured, test it works:

```bash
# Record 5 seconds from input
arecord -D plughw:0,0 -f cd -d 5 ~/tars_files/audios/tars_hear_me_if_you_can.wav
```

- `arecord` → console audio recording tool (ALSA).
- `-D plughw:0,0` → uses the capture device of **card 0, device 0**
- `-f cd` → "CD quality" format: 44.1kHz, 16 bits, stereo.
- `-d 5` → recording duration: **5 seconds**.
- `test.wav` → name of generated file.

 Play the audio

```bash
aplay ~/tars_files/audios/tars_hear_me_if_you_can.wav
```

> The audio should be heard clearly. If volume is low, it's not a problem: below we'll adjust the level with `alsamixer`.

If nothing is heard, the output device might be misconfigured. Check again the output of `aplay -l` and try with other cards (`plughw:1,0`, `plughw:2,0`, etc.).

---

> [!WARNING]
> 
> **Don't continue if everything already works.**  
> This section is only necessary if **the microphone doesn't work automatically** or **there are several input devices** and TARS/Vosk is choosing the wrong one.
> 
> If you already did a voice test and it recognized you without errors: you can skip what comes next.

### ❌ Common error with `sounddevice` (Vosk, PyAudio, etc.)

If you see something like:

```bash
ValueError: No input device matching 'plughw:0,0'
```

It's because `sounddevice` —the module used by Vosk, PyAudio and TARS— **doesn't recognize `plughw:x,y` type identifiers**.  
That format **is valid for ALSA** (`arecord`, `aplay`, `.asoundrc`)… but not here.

🟢 Instead, use numeric indices (`0`, `1`, `2`, etc.).

#### But hadn't we configured `.asoundrc`?

Yes, but `.asoundrc` **doesn't affect `sounddevice`**.

- `.asoundrc` serves to tell ALSA what to use as default input/output (ideal for `arecord`, `aplay`, `Piper`, etc.)
- `sounddevice`, on the other hand, **completely ignores `.asoundrc`** and goes its own way: it only understands indices or names from its own system.

> What happens if you copy `plughw:0,0` in TARS config?  
> It will throw an error like the one above. Because for `sounddevice`, that **isn't even a valid device**.

#### See devices compatible with `sounddevice`

Activate the virtual environment and run:

```bash
source ~/tars_venv/bin/activate
python3 -c "import sounddevice as sd; print(sd.query_devices())"
```

Typical output:

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

Note about the asterisk `*`
That asterisk marks the **default device**, but that doesn't mean it works well or that it's your real microphone.  

⚠️ Don't choose it by default. Verify which is your USB or real input.

#### What index should I use?

Look for your microphone:

```bash
0 USB Audio Device: - (hw:0,0), ALSA (1 in, 2 out)
```

🟢 Therefore, in TARS configuration you'll use: `device = 0`

#### Where do I configure the microphone index?

Once you've identified your device (for example, `device = 0`), you need to put that value in TARS configuration file:

```bash
nano ~/tars_files/config/mic_config.ini
```

🟢 Look for or add this line and adjust the number according to what you saw above: `device = 0`  

#### Why is `mic_config.ini` empty?

- The `mic_config.ini` file **is created on the fly** the first time you run the audio module (STT) or scripts related to the microphone.
- If you've never launched anything that needs to capture voice (like `tars_core.py` or an STT test), the file doesn't exist yet or is blank.
- Even if it's empty, **TARS has internal default values** to try to detect the microphone automatically.

#### Summary

> - `arecord`, `aplay`, `.asoundrc` → use `hw:x,y` or `plughw:x,y`
> - `sounddevice` → uses **numeric indices** or **exact names**

---
### What happens if you connect another sound card?

Sometimes, when connecting a new USB device (DAC, microphone, speaker…), **the system changes its card numbering**.

- If the new card is also registered as `card 0`, **everything will continue working**.
- But if it appears as `card 1`, `card 2`, etc., you'll have to **manually adjust the number** in your commands.

#### Recording test:

```bash
arecord -D plughw:0,0 -f cd ~/tars_files/audios/mic_test_revenge.wav
```

#### Play result:

```bash
aplay ~/tars_files/audios/mic_test_revenge.wav
```

#### Or test a system sound:

```bash
aplay -D plughw:0,0 /usr/share/sounds/alsa/Front_Center.wav
```

> [!IMPORTANT]  
> 
> Remember: **replace `0,0` with the real values** shown by `arecord -l` and `aplay -l`.  
> There's no magic here: if you change cables, numbering changes.

---
### Verify speech recognition

```bash
cd ~/tars_files
python3 scripts/test_speechrecognition_vosk.py
```

**The script will perform:**

- Vosk model verification
- Available microphone detection
- Recording and voice recognition test
- Detailed feedback on possible problems

🟢 Expected output: `🎉 Voice recognition working correctly!`

---

## 🕹️ Volume control with alsamixer

Launch ALSA mixer with:

```bash
alsamixer
```

- If you don't see your card press **F6** and select yours.
- Use arrows ⬅️ ➡️ to move and ⬆️ ⬇️ to adjust volume.
- If any channel appears muted (`MM`), press **M** to activate it (`OO`).
- Press Esc to exit

#### Save current configuration:

```bash
sudo alsactl store
```

🟢 This saves the state in `/var/lib/alsa/asound.state`.

---
#### Save volume on boot

For ALSA to remember your volume configuration after reboot, you need to save the current state and restore it automatically on each boot.
You can do this in two ways: using `systemd` (recommended for being more modern) or with `rc.local`, if you prefer a more classic approach.

#### (Recommended) Use `systemd`

This method is **more reliable and compatible with modern systems** (like Raspberry Pi OS or Debian 12+).

1. Create the service file:

```bash
sudo nano /etc/systemd/system/rc-local.service
```

2. Paste this:

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

3. Enable the service:

```bash
sudo systemctl enable rc-local
```

4. Save current state manually with:

```bash
sudo alsactl store
```

🟢 This will save current levels in `/var/lib/alsa/asound.state`.

---
#### (Alternative option) Use `rc.local`

This method may work **on old distros**, but **not all systems run it by default**.

1. Edit the file (if it doesn't exist, create it):

```bash
sudo nano /etc/rc.local
```

2. Add the following content before `exit 0`:

```bash
#!/bin/bash
# Restore ALSA volume on boot
/usr/sbin/alsactl restore

exit 0
```

3. Make it executable:

```bash
sudo chmod +x /etc/rc.local
```

> If after rebooting volume isn't recovered, your system probably **isn't running `rc.local` automatically**.  
> In that case, **use the recommended option with `systemd` above**.

---

## 🛠️ Create service for TARS (Systemd)

> [!INFO]
> 
> This step is optional: creates a `systemd` service so TARS starts with the system.  
> It may not be necessary if you prefer to run it manually according to your needs or how you use your Raspberry.

[Skip to how to use TARS if you're not going to create the service](#-using-tars-after-installation)


🟢 Continue in virtual environment: `source ~/tars_venv/bin/activate`
### 1. Create service file

```bash
sudo nano /etc/systemd/system/tars.service
```

### 2. Add service configuration

Paste the following:

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

### 3. Verify startup script

> [!INFO] Already included in repository:
>
> The [start_tars.sh](/scripts/start_tars.sh) script includes:
>
 >- **Single instance control:** Prevents running TARS twice
> - **Resource cleanup:** Automatically frees GPIOs and audio
> - **Basic validations:** Checks microphone and dependencies
>
> You can alternate between automatic mode (systemd) and manual without conflicts.

### 4. Give execution permissions to script

```bash
sudo chmod +x /home/tarsadmin/tars_files/scripts/start_tars.sh
```

### 5. Enable and start service

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now tars.service
```

🟢 From now on, TARS will start automatically with your Raspberry.  

---
### Quick tips

#### A. View service status

```bash
systemctl status tars.service
```

Console output:

```bash
● tars.service - 🤖 TARS AI Controller
     Loaded: loaded (/etc/systemd/system/tars.service; enabled; preset: enabled)
     Active: active (running) since Wed 2025-06-25 10:12:32 CEST; 13s ago
   
🤖 Starting TARS Core in background...
✅ TARS started correctly
🎤 TARS is ready and listening...
```

🟢 Look for **"Active: active (running)"** and TARS started messages

#### B. Restart manually

```bash
sudo systemctl restart tars.service
```

#### C. Stop service

```bash
sudo systemctl stop tars.service
```

#### D. Disable service

```bash
sudo systemctl disable tars.service
```

#### E. View logs in real time

```bash
# Basic system logs (systemd)
journalctl -u tars.service -f
```

#### 🔥 F. DETAILED TARS LOGS (recommended)

```bash
# All the internal drama of TARS
tail -f /tmp/tars_startup.log
```

> [!IMPORTANT] The real power is in `/tmp/tars_startup.log` — _TARS's unauthorized autobiography_  
> A document containing:
> 
> - AI models that learned to **lie in benchmarks**
> - Audio drivers reproducing **silence in lossless format**
> - `systemd` pretending it understood dependencies
> - GPIOs swearing they **were on another port**
> - Errors so creative they deserve a **Pulitzer**
> 
> "It's not a _log file_… it's contemporary art generated by segmentation faults."
> 
> ```bash
> sudo cat /tmp/tars_startup.log | grep -v "success" | shuf -n 5 | festival --tts
> ```
> Because logs should **be read with Shakespearean tragedy voice**.

---

## 🚀 Using TARS after installation

### If you configured automatic startup

If you followed the previous section and configured the systemd service, **perfect!** TARS is already working:

- ✅ **Starts automatically** when turning on the Raspberry Pi
- ✅ **Restarts itself** if there's any problem
- ✅ **Always available** without doing anything else

**Verify it works:**

```bash
systemctl status tars.service
```

🟢 If you see `Active: active (running)`
### ✨ Simply say _**"Hey TARS"**_ and that's it

---
### (Development mode) Manual testing 

If you want to **test** (try voice effects, debugging, configuration changes), simply run:

```bash
source ~/tars_venv/bin/activate
python3 /home/tarsadmin/tars_files/core/tars_core.py
```

#### ⚠️ Expected result (if automatic service is active)

```bash
✅ GPIO backend configured: lgpio
2025-06-25 15:50:27,534 - memory.semantic_storage - INFO - Loaded 8 embeddings...
⚠️ TARS is already running.
   Run this command first:
   sudo kill 63895 # ←
   Then start TARS again.
```

ℹ️ **This is not a real error.**  

It means **TARS is already active in the background** as an automatic service. There can only be **one instance of TARS running at a time**, so:

#### Step 1: Run the command it shows you

```bash
# Copy exactly what appears (the number will be different)
sudo kill 63895
```

#### Step 2: Launch TARS again

```bash
python3 /home/tarsadmin/tars_files/core/tars_core.py
```

> [!INFO] If you prefer to avoid the error, you can stop the service first:
> 
> ```bash
> sudo systemctl stop tars.service
> python3 /home/tarsadmin/tars_files/core/tars_core.py
> ```
> But it's not necessary - following the error instructions also works perfectly.

**Successful output:**

```
✅ GPIO backend configured: lgpio
✅ TARS initialized in 0.16 seconds
Use voice input? (Y): y
🎤 Available audio devices:
  [0] USB Audio Device: - (hw:0,0) - 44100Hz
✅ Automatically selected: [0] USB Audio Device
🎤 Say 'hey tars' to begin (Ctrl+C to exit)
```

#### Step 3: Do your tests

You can now interact with TARS. Here are some ideas:
##### Voice input:

- At the question `Use voice input? (Y):`, answer:
    
    - `y` to activate it
    - `n` to deactivate it and use keyboard

##### What you can validate now:

- **Test real voice commands** (`hey tars`, etc.)
- **See logs in real time** (to review internal flow)
- **Modify and test configuration**
- **Force errors or use alternative modes** if you're debugging

#### Step 4: Return to automatic mode

When you finish testing:

```bash
# 1. Stop manual TARS (Ctrl+C in console)
^C

# 2. Return to automatic mode
python3 ./scripts/start_tars.sh
```

**Or reactivate the service:**

```bash
sudo systemctl start tars.service
```

---
### 🐣 If you did NOT configure automatic startup

If you skipped the systemd service section, simply always use:

```bash
source ~/tars_venv/bin/activate
python3 /home/tarsadmin/tars_files/core/tars_core.py
```

**In this case you'll never have the error** of "TARS is already running" because there's no automatic service running.

---
### Flow summary

>[!INFO]
>
> 1. **Service configured** → TARS always running automatically
> 2. **I want to test** → Stop service → Manual mode
> 3. **Finish testing** → Relaunch script → Return to automatic
> 4. **No service** → Always manual mode, no conflicts
> 
> **The trick is not having two TARS running at once** 🤖

---

## 📟 TARS-BSK - Final system message

> **// TARS-BSK > last_boot.log:**
> 
> The final moment has arrived. My installation is complete, my purpose fulfilled. ~~Congratulations.~~
> 
> But before transferring control to your... technical creativity... let me leave a record of my current state for digital posterity.
> 
> Consider this my technical testament.
> 
> _— TARS-BSK (~~Semi~~ Complete Version™)_
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
> █▀▄█▀█░▄▀▄░█▀▄░█░█░█▀█  _This is the way_

---

## 🛰️ V∞∞∞ – SATELLITE EDITION (Optional extra not requested)

🧬 **The inevitable evolution of a guide that came to life:**

```bash
# My brain at 4 AM:
"What if I turn it into a satellite?"
"What if every Raspberry Pi receives the guide from SPACE?"
"What if I create a constellation of orbital documentation?"
"What if TARS controls the ISS?"
```

🚀 **Complete escalation:**

```bash
V1: "Guide in markdown" ✅
V2: "With better format" 📝
V3: "With emojis" 🎨
V4: "Responsive web" 💻
V5: "Interactive tutorial" 🎮
V6: "Virtual reality" 🥽
V7: "Holograms" 👻
V8: "Brain implants" 🧠
V9: "Orbital satellite" 🛰️
V10: "Telepathically from Mars" 👽
```

📡 **TARS-BSK SPACE EDITION:**

> _"Houston, TARS-BSK here. Confirming that PyTorch installation in zero gravity presents... unexpected complexities. The NOCTUA fan is trying to create propulsion. Over."_

## 🛑 **ABORT MISSION:**

**RETURN TO EARTH. PUBLISH THE GUIDE. SAVE YOURSELF!** 🌍
_One small step for docs, one giant leap for overthinking._ 🚀

---
_If you've made it this far, you're probably already part of the TARS-BSK space program. You didn't sign anything, but you're in. Welcome._ 