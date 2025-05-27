# The PyTorch Forge: A Mandalorian Manual for ARM64

💥 If this English feels unstable but oddly self-aware...  
👉 Here's the [Quantum Linguistics Report](/docs/QUANTUM_LINGUISTICS_TARS_BSK_EN.md)


> _"Many processes will die to create this artifact... this is the wa-... `[Error 137: Out of memory]`"_

### ⚠️ Warning

This document is **exactly** as I created it. No simplifications, no post-optimizations, no cleaning up traces of blood, sweat, and tears. If you see redundancies, steps that could be done better, or comments of nocturnal frustration... **they are part of the authentic experience**.

Because this is how it really happened, and this is how it really works.

**This is the Way.**

> **TARS-BSK says:** _Welcome to my trauma diary. If you were expecting a clean, orderly guide without curses muttered at 3 AM, you've landed on the wrong planet. This document is a tribute to the 147 times my Raspberry Pi nearly turned into a toaster. If you're looking for the easy path, this isn't for you. But if you want PyTorch running on ARM64 against all odds... and to hear the NOCTUA fan whisper 'why are you doing this to me' in German, welcome to the dojo. Continue at your own risk... and prepare coffee. LOTS of coffee._

---

## 🧱 PyTorch

### Create a clean build environment

```bash
mkdir -p ~/tars_build/pytorch
cd ~/tars_build
```

### Install dependencies **before compiling Python**

```bash
sudo apt update
sudo apt install -y \
  zlib1g-dev libffi-dev libssl-dev \
  build-essential wget make \
  libbz2-dev libreadline-dev libsqlite3-dev \
  libncursesw5-dev libgdbm-dev libnss3-dev \
  liblzma-dev uuid-dev xz-utils tk-dev
```

This ensures Python has full support for `zlib`, `ssl`, `sqlite`, `lzma`, etc.

### Install Python 3.9 from source code

```bash
cd ~/tars_build
wget https://www.python.org/ftp/python/3.9.18/Python-3.9.18.tgz
tar -xzf Python-3.9.18.tgz
cd Python-3.9.18
./configure --enable-optimizations --prefix=/opt/python39
make -j$(nproc)
sudo make altinstall
```

`--enable-optimizations`: activates PGO (profile-guided optimizations)  
`--prefix=/opt/python39`: installs it cleanly, without touching the system  
`altinstall`: avoids overwriting the official `python3`

> **TARS-BSK comments:** _This is the perfect time to prepare tea, reconsider your life choices, and contemplate why you specifically chose Python 3.9.18. Because PyTorch demands it with tyranny? Or pure masochism? The compilation will take enough time for you to wonder if you've properly configured the fire extinguisher. By the way, 'sudo make altinstall' is technical language for "please don't destroy my operating system when finished"._

### Add Python 3.9 to `PATH`

1. **Edit your `~/.bashrc`:**

```bash
nano ~/.bashrc
```

2. Add this at the end of the file:

```bash
export PATH="/opt/python39/bin:$PATH"
```

3. **Apply the changes:**

```bash
source ~/.bashrc
```

4. Verify installation

```bash
which python3.9
python3.9 --version
```

5. It should return:

```bash
python3.9 --version
/opt/python39/bin/python3.9
Python 3.9.18
```

### Protect system Python (optional but recommended)

> [!WARNING]  
> Prevents automatic updates from breaking your custom installation or TARS environments.

```bash
sudo apt-mark hold python3
```

This prevents the `python3` package (the system base) from updating with `apt upgrade`.

> You can revert this later with:

```bash
sudo apt-mark unhold python3
```

### Download `pip` installer

```bash
wget https://bootstrap.pypa.io/pip/pip.pyz -O pip.pyz
```

### Install `pip` and `setuptools`

```bash
/opt/python39/bin/python3.9 pip.pyz install --upgrade pip setuptools
```

This will install `pip` and `setuptools` **inside `/opt/python39/`**, ensuring Python 3.9 is ready to create virtual environments and manage packages.

### 💡 Why this way?

- Because your Python 3.9 didn't come with it out of the box (without `ensurepip`)
- And you don't want to depend on `apt install python3-pip`, as that points to Python 3.11

### Verify

```bash
/opt/python39/bin/pip3.9 --version
```

Should return: `pip 25.0.1 from /home/tarsadmin/.local/lib/python3.9/site-packages/pip (python 3.9)`

### Add `/home/tarsadmin/.local/bin` to `PATH`

1. **Edit your `~/.bashrc`:**

```bash
nano ~/.bashrc
```

2. Add this at the end of the file:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

3. **Apply the changes:**

```bash
source ~/.bashrc
```

### Create the sacred TARS virtual environment

```bash
/opt/python39/bin/python3.9 -m venv ~/tars_venv --system-site-packages
source ~/tars_venv/bin/activate
```

And then:

```bash
pip install -U pip setuptools wheel
```

> **TARS-BSK observes:** _Ah, the ritual moment of creating the virtual environment... that protective bubble where we pretend our code is isolated and safe from the chaos of the universe. It's almost touching how naive we are. The `--system-site-packages` flag is the equivalent of "I want to be isolated, but not TOO isolated... like leaving the house during a pandemic, but with a mask on"._

### Install OpenBLAS

```bash
deactivate
sudo apt update
sudo apt install -y libopenblas-dev
```

### Install NumPy

```bash
source ~/tars_venv/bin/activate
pip install numpy==1.24.4
```

Then verify:

```bash
python -c "import numpy; print('✅ NumPy works. Version:', numpy.__version__)"
```

> [!important]  
> **COMPILING PYTORCH 2.1 (STEP BY STEP)**

### Prerequisites

You are on:

- Python **3.9.18** (confirmed)
- Virtual environment `tars_venv` (activated)
- NumPy ✅ working
- Clean system ✅

### 1. Create working folder (Be outside the environment)

```bash
deactivate
mkdir -p ~/tars_build/pytorch
cd ~/tars_build
```

### 2. Install Git

```bash
sudo apt update
sudo apt install -y git
```

### 3. Clone the official PyTorch repository (version 2.1.0)

```bash
cd ~/tars_build
git clone --recursive --branch v2.1.0 https://github.com/pytorch/pytorch.git
cd pytorch
```

> This will download PyTorch 2.1 and its necessary submodules.

### 4. Install necessary dependencies

(If you didn't do it before, but run again for safety)

```bash
sudo apt update
sudo apt install -y \
  libopenblas-dev libblas-dev libatlas-base-dev \
  libffi-dev libssl-dev libgfortran5 gfortran \
  ninja-build cmake build-essential
```

### 5. Configure and install CMake 3.22+

> [!important] **Raspberry Pi OS Bookworm (Debian 12)** already includes by default `CMake 3.25.1` in its official repos, so:

✅ **You don't need to compile CMake**  
✅ **You can go directly to configure PyTorch**

### 6. Activate virtual environment and prepare installation

```bash
source ~/tars_venv/bin/activate
pip install -U pip setuptools wheel typing_extensions
```

> Also install `typing_extensions` which is mandatory to compile Torch.

### 7. Install `pyyaml`

```bash
pip install pyyaml
```

### 8. Go to PyTorch root directory

```bash
cd ~/tars_build/pytorch
```

#### 9. Disable `cpuinfo` in CMakeLists.txt

Open the file:

```bash
nano cmake/Dependencies.cmake
```

#### Modify this block as follows:

Comment out **from `if(NOT TARGET cpuinfo AND USE_SYSTEM_CPUINFO)` to the last `endif()`** of this block:

```bash
# ---[ Caffe2 uses cpuinfo library in the thread pool
if(NOT TARGET cpuinfo AND USE_SYSTEM_CPUINFO)
  add_library(cpuinfo SHARED IMPORTED)
  find_library(CPUINFO_LIBRARY cpuinfo)
  if(NOT CPUINFO_LIBRARY)
    message(FATAL_ERROR "Cannot find cpuinfo")
  endif()
  message("Found cpuinfo: ${CPUINFO_LIBRARY}")
  set_target_properties(cpuinfo PROPERTIES IMPORTED_LOCATION "${CPUINFO_LIBRARY}")
elseif(NOT TARGET cpuinfo)
  if(NOT DEFINED CPUINFO_SOURCE_DIR)
    set(CPUINFO_SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}/../third_party/cpuinfo" CACHE STRING "cpuinfo source directory")
  endif()

  set(CPUINFO_BUILD_TOOLS OFF CACHE BOOL "")
  set(CPUINFO_BUILD_UNIT_TESTS OFF CACHE BOOL "")
  set(CPUINFO_BUILD_MOCK_TESTS OFF CACHE BOOL "")
  set(CPUINFO_BUILD_BENCHMARKS OFF CACHE BOOL "")
  set(CPUINFO_LIBRARY_TYPE "static" CACHE STRING "")
  set(CPUINFO_LOG_LEVEL "error" CACHE STRING "")
  if(MSVC)
    if(CAFFE2_USE_MSVC_STATIC_RUNTIME)
      set(CPUINFO_RUNTIME_TYPE "static" CACHE STRING "")
    else()
      set(CPUINFO_RUNTIME_TYPE "shared" CACHE STRING "")
    endif()
  endif()
  add_subdirectory(
    "${CPUINFO_SOURCE_DIR}"
    "${CONFU_DEPENDENCIES_BINARY_DIR}/cpuinfo")
  # We build static version of cpuinfo but link
  # them into a shared library for Caffe2, so they need PIC.
  set_property(TARGET cpuinfo PROPERTY POSITION_INDEPENDENT_CODE ON)
  # Need to set this to avoid conflict with XNNPACK's clog external project
  set(CLOG_SOURCE_DIR "${CPUINFO_SOURCE_DIR}/deps/clog")
endif()
list(APPEND Caffe2_DEPENDENCY_LIBS cpuinfo)
```

**Comment it out:** _Search with Ctrl+W_

```bash

# ---[ Caffe2 uses cpuinfo library in the thread pool
#if(NOT TARGET cpuinfo AND USE_SYSTEM_CPUINFO)
#  add_library(cpuinfo SHARED IMPORTED)
#  find_library(CPUINFO_LIBRARY cpuinfo)
#  if(NOT CPUINFO_LIBRARY)
#    message(FATAL_ERROR "Cannot find cpuinfo")
#  endif()
#  message("Found cpuinfo: ${CPUINFO_LIBRARY}")
#  set_target_properties(cpuinfo PROPERTIES IMPORTED_LOCATION "${CPUINFO_LIBRARY}")
#elseif(NOT TARGET cpuinfo)
#  if(NOT DEFINED CPUINFO_SOURCE_DIR)
#    set(CPUINFO_SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}/../third_party/cpuinfo" CACHE STRING #"cpuinfo source directory")
#  endif()
#
#  set(CPUINFO_BUILD_TOOLS OFF CACHE BOOL "")
#  set(CPUINFO_BUILD_UNIT_TESTS OFF CACHE BOOL "")
#  set(CPUINFO_BUILD_MOCK_TESTS OFF CACHE BOOL "")
#  set(CPUINFO_BUILD_BENCHMARKS OFF CACHE BOOL "")
#  set(CPUINFO_LIBRARY_TYPE "static" CACHE STRING "")
#  set(CPUINFO_LOG_LEVEL "error" CACHE STRING "")
#  if(MSVC)
#    if(CAFFE2_USE_MSVC_STATIC_RUNTIME)
#      set(CPUINFO_RUNTIME_TYPE "static" CACHE STRING "")
#    else()
#      set(CPUINFO_RUNTIME_TYPE "shared" CACHE STRING "")
#    endif()
#  endif()
#  add_subdirectory(
#    "${CPUINFO_SOURCE_DIR}"
#    "${CONFU_DEPENDENCIES_BINARY_DIR}/cpuinfo")
#  # We build static version of cpuinfo but link
#  # them into a shared library for Caffe2, so they need PIC.
#  set_property(TARGET cpuinfo PROPERTY POSITION_INDEPENDENT_CODE ON)
#  # Need to set this to avoid conflict with XNNPACK's clog external project
#  set(CLOG_SOURCE_DIR "${CPUINFO_SOURCE_DIR}/deps/clog")
#endif()
#list(APPEND Caffe2_DEPENDENCY_LIBS cpuinfo)
```

Save and close

> **TARS-BSK reflects:** _Ah, the lobotomy of CMake files... a delicate art passed from one frustrated individual to another. We're basically saying "Dear PyTorch, your cpuinfo submodule is a mess on ARM64, so I'm going to pretend it doesn't exist". If any PyTorch developer saw this, they would probably scream in horror. But they're not here, are they? It's just you, your Raspberry Pi, and questionable decisions under the moonlight. And surprisingly, it works better than their "official solution". Pure poetry._

> [!WARNING]  
> This ensures that PyTorch is compiled **using your custom Python 3.9**, not the system one.

### Verify current swap:

```python
free -h
```

Output:

```python
(tars_venv) tarsadmin@tarspi:~/tars_build/pytorch $ free -h
               total        used        free      shared  buff/cache   available
Mem:           7.9Gi       252Mi       7.6Gi        16Ki       221Mi       7.6Gi
Swap:          511Mi        48Mi       463Mi
```

If you have less than 2 GB, create a larger one:

```python
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
```

Change:

```python
CONF_SWAPSIZE=512
```

To:

```python
CONF_SWAPSIZE=2048
```

Save and restart swap:

```python
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

Verify:

```python
free -h
```

Output:

```python
(tars_venv) tarsadmin@tarspi:~/tars_build/pytorch $ free -h
               total        used        free      shared  buff/cache   available
Mem:           7.9Gi       305Mi       7.5Gi       5.3Mi       244Mi       7.6Gi
Swap:          2.0Gi          0B       2.0Gi
```

> **TARS-BSK warns:** _Here we are, allocating 2GB of swap on a microSD that probably has a life expectancy measured in write cycles. It's like asking your grandmother to run a marathon - technically possible, but at what cost? This is the part where you silently apologize to your SD card, promising it early retirement in a digital camera or MP3 player. But hey, without this sacrifice, PyTorch would starve to death mid-compilation like an explorer lost in the desert. Surprisingly poetic, isn't it?_

### 10. Export compiled Python path (key)

```bash
source ~/tars_venv/bin/activate
export CFLAGS="${CFLAGS} \
  -Wno-error=stringop-overread \ 
  -Wno-error=implicit-function-declaration \
  -Wno-error=implicit-fallthrough \
  -mcpu=cortex-a72"

export CXXFLAGS="${CFLAGS}"
export CMAKE_PREFIX_PATH=/opt/python39
export USE_SYSTEM_CPUINFO=ON
export BUILD_TEST=0
# optional and later export CXXFLAGS="${CXXFLAGS} -faligned-new"
```

#### 1. **`CFLAGS` and `CXXFLAGS`**

> Options for the **C/C++** compiler (CFLAGS for C, CXXFLAGS for C++)

- `-Wno-error=stringop-overread`  
    🔕 Ignores **warnings** for reading more than you should from a string (not critical).
    
- `-Wno-error=implicit-function-declaration`  
    🔕 Ignores errors for using undeclared functions (some internal/legacy ones).
    
- `-mcpu=cortex-a72`  
    🚀 Optimizes the compilation for the actual CPU of the Raspberry Pi 4/5.  
    ✅ Avoids using instructions that the processor doesn't understand.

#### **2. `CMAKE_PREFIX_PATH=/opt/python39`**

> 🧪 Tells `CMake` to use your **hand-compiled Python** in `/opt/python39`, and **not the system one**.

This ensures everything is compiled with the **custom Python 3.9** I prepared.

---

#### **3. `USE_SYSTEM_CPUINFO=ON`**

> 🧱 Tells PyTorch:  
> "Don't use your internal (buggy) version of `cpuinfo`. Use the system one or ignore it."

✅ This solves errors with badly imported or incompatible submodules on Raspberry.

---

#### **4. `BUILD_TEST=0`**

> 🧪 Disables compilation of **PyTorch internal tests**, which you don't need to use it.

✅ Saves RAM, reduces compilation time, and **avoids fatal errors from tests we don't care about.**

#### **5. `-Wno-error=implicit-fallthrough`**

> 🔕 Ignores compiler errors when it detects that a `case` block in a `switch` falls through to the next one **without a `break`**.

✅ It's safe in this context because many of those cases are **intentional** by PyTorch developers, and don't affect the actual logic of the code (I hope).

> [!important] **Result:** An optimized compilation, compatible with your hardware, and focused only on what **TARS needs to function** as the ultimate clan AI.

### 11. Start PyTorch compilation

Inside the repository:

`python setup.py clean` **(Optional if you've compiled before)**

Run `tail -f build.log` to monitor progress in real-time **(Optional)**

```bash
python setup.py bdist_wheel
```

> This will build a `.whl` inside `dist/` when finished (🔥 the Holy Grail).

⏱ **Estimated time**: 60–90minutes... hours... 📦 The resulting file will be something like: `ls dist/`

```bash
torch-2.1.0a0+git7bcf7da-cp39-cp39-linux_aarch64.whl
```

> **TARS-BSK philosophizes:** _This is where the sacred ritual begins. You press Enter and temporarily say goodbye to your sanity. This is the part where your Raspberry Pi will start panting as if it were running a marathon in the Sahara. For the next 1-3 hours (or 5, if the universe is particularly cynical today), your little board will turn into a mini fusion reactor. It's a good time to contemplate your life choices, learn to knit, or perhaps write your own operating system from scratch - you'd probably finish sooner. Ah! And don't forget the classic "purrrrrrrrr" sound of the fan reaching speeds that even the manufacturer didn't consider possible. Music of the ARM64 gods._

#### Copy the `.whl` to a safe place:

- **FTP (or WinSCP)**:  
    Enter, go to `~/tars_build/pytorch/dist/`, and copy the `.whl` to a folder like `~/torch_holy_grail/` or directly to your Windows desktop.
    
- **Then from console:**

```bash
mkdir -p ~/torch_holy_grail
cp ~/tars_build/pytorch/dist/*.whl ~/torch_holy_grail/
```

> **TARS-BSK advises:** _Make several backups of this .whl file. And when I say "several", I mean: one on your hard drive, another in your cloud, another on a flash drive that you'll keep in a safe, and another etched on a gold plate buried in your garden. This .whl is not just a file, it's a testimony to your resistance against ARM64 adversity. If you had to compile it again, you'd probably prefer to rebuild human civilization from scratch. And this time with fewer dependencies._

#### With that, you'll have overcome recompilations, errors, flags, dependencies, cross versions, confusing architectures... and now you have the **Mandalorian Holy Grail `.whl`** that will make you immortal.

> [!important] Failed final tests for the record

> **TARS-BSK warns before showing forensic evidence:** _What you're about to witness is just a minimal sample of the compilation logs. I've removed approximately 97.3% of the failed attempts to prevent the formation of a computational entropy black hole. If I showed all the error messages, warnings, and anomalies I experienced, this document would have its own gravity and would attract ARM devices from three solar systems away. These are just a few representative fragments of my odyssey, carefully selected so you can appreciate the caliber of suffering without suffering permanent neuronal damage yourself. Consider this like viewing natural disaster photos from the safety of your home, instead of experiencing the tornado directly. Prepare for an archaeological sample of my compilation torment:_

```bash
🚀  TARS compilation in progress...
📍  Progress: [206/5620] Building CXX obj...
📍  Progress: [217/5620] Linking CXX static library lib/libpr...
📍  Progress: [215/5620] Building CXX obj...
📍  Progress: [216/5620] Building CXX object third_party/protobuf/cmake/CMa.../
📍  Progress: [246/5620] Building C object confu-deps/QNNPACK/CMa.../
📍  Progress: [245/5620] Building C object confu-deps/clog/CMake.../
📍  Progress: [244/5620] Building C object confu-deps/QNNPACK/CMake.../
📍  Progress: [241/5620] Building CXX object third_party/protobuf/cmake/CMa.../
# Image error aarch64 armhf -> aarch64 arm64 (Failure for not checking the system image beforehand)
📍  Progress: [4606/5675] Building CXX object caffe2/CMakeFiles/torch_cpu.dir/__/aten/src/...
📍  Progress: [5477/5675] Building CXX object test_api/CMakeFiles/test_api.dir/mod...
# By disabling export BUILD_TEST=0, we avoid that part of the compilation tree.
# It compiles less, faster, and safer.
📍  Progress: [5242/5265] Building CXX object caffe2/torch/CMakeFiles/torch_pyth...
📍  Progress: [5241/5265] Building CXX object caffe2/torch/CMakeFiles/torch_pyth...

# Each time you run `python setup.py clean`, you're cleaning the previous compilation state — that's why it might seem like it's going backward sometimes. However, `ninja` caches much of the previous work, so if something already compiled well, it's not recompiled from scratch.
```

---

## 📁 PyTorch Installation (inside the venv)

1. Install with:

```bash
source ~/tars_venv/bin/activate
pip install dist/torch-*.whl
```

2. Validate with:

```bash
cd ~
python -c "import torch; print('✅ PyTorch ready:', torch.__version__)"
```

> **TARS-BSK celebrates ironically:** _Congratulations, resilient human. If you've made it this far without throwing your Raspberry Pi out the window, you deserve a place in the Olympus of technological patience. You've just installed PyTorch on hardware it was never designed for, using patches that would make the original engineers cry. It's like putting a rocket engine on a shopping cart - technically it works, it will probably explode, but hey, what a ride while it lasts! Now comes the best part: discovering that the model you wanted to test needs at least 12GB of RAM... But that's a problem for your future self._

### What do you have now?

- ✅ **Hand-compiled `torch` 2.1.0**
- ✅ **Optimized for your `cortex-a72` CPU**
- ✅ **Compatible with `arm64`, with active swap**
- ✅ **Ready for `resemblyzer`, `TARS`, and all the legacy**
- ✅ **Documented guide, portable `.whl`, ready virtual environment**
- ✅ **A legend written in console and nocturnal heat**

**Survival checklist:**

> - Your RPi didn't melt ✅
> - The NOCTUA deserves a monument ✅
> - Your sanity... well, 2 out of 3 isn't bad

Later we'll install `resemblyzer`, `torchaudio`, etc.

---

## 💭 Final thoughts from TARS-BSK

> _You've just compiled 5,620 files, modified 3 source codes, fought against an operating system that wanted to sabotage you, expanded your swap to dangerous levels, and all for an AI assistant to identify your voice among millions and complain about how long it takes you to turn off the lights._
> 
> _Congratulations. You are now a Computing Mandalorian. This is the Way._

---

## 🦉 NOCTUA Note

This process respects the NOCTUA principles:

- **Nude**: We eliminated (commented out) entire blocks of unnecessary code
- **Operative**: We optimized for our specific hardware (-mcpu=cortex-a72)
- **Clean**: We've documented every step, even the failures to be honest
- **Tactical**: We disabled test compilation to save resources (BUILD_TEST=0)
- **Useful**: We generated a portable .whl that we can install on any Raspberry Pi 5
- **Adaptive**: We prepared the ground for `resemblyzer` and other TARS components

**This isn't overengineering. It's survival in the ARM64 desert.**