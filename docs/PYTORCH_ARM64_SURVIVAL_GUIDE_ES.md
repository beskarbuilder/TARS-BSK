# La Forja de PyTorch: Manual Mandaloriano para ARM64

 _"Muchos procesos morirán para crear este artefacto... este es el cami-... `[Error 137: Out of memory]`"_
 

> [!IMPORTANT]
> 
> Este documento es **exactamente** como lo creé. Sin simplificaciones, sin optimizaciones posteriores, sin limpiar los rastros de sangre, sudor y lágrimas. Si ves redundancias, pasos que podrían hacerse mejor, o comentarios de frustración nocturna... **son parte de la experiencia auténtica**.
> 
> Porque así es como realmente sucedió, y así es como realmente funciona.
> 
> **This is the Way.**


> **TARS-BSK dice:**
> 
> _Bienvenido a mi diario de trauma. Si esperabas una guía limpia, ordenada y sin maldiciones murmuradas a las 3 AM, has aterrizado en el planeta equivocado. Este documento es un homenaje a las 147 veces que mi Raspberry Pi casi se convirtió en una tostadora.
> 
> Si buscas el camino fácil, esto no es para ti. Pero si quieres PyTorch funcionando en ARM64 contra todo pronóstico... y escuchar el ventilador NOCTUA susurrar 'por qué me haces esto' en alemán, bienvenido al dojo. 
> 
> Continúa bajo tu propio riesgo... y prepara café. MUCHO café._ 

---

## 🧱 PyTorch

### Crear el entorno de compilación limpio

```bash
mkdir -p ~/tars_build/pytorch
cd ~/tars_build
```

---
### Instalar dependencias **antes de compilar Python**

```bash
sudo apt update
sudo apt install -y \
  zlib1g-dev libffi-dev libssl-dev \
  build-essential wget make \
  libbz2-dev libreadline-dev libsqlite3-dev \
  libncursesw5-dev libgdbm-dev libnss3-dev \
  liblzma-dev uuid-dev xz-utils tk-dev
```

Esto asegura que Python tenga soporte completo para `zlib`, `ssl`, `sqlite`, `lzma`, etc.

---
### Instalar Python 3.9 desde código fuente

```bash
cd ~/tars_build
wget https://www.python.org/ftp/python/3.9.18/Python-3.9.18.tgz
tar -xzf Python-3.9.18.tgz
cd Python-3.9.18
./configure --enable-optimizations --prefix=/opt/python39
make -j$(nproc)
sudo make altinstall
```

`--enable-optimizations`: activa PGO (profile-guided optimizations)  
`--prefix=/opt/python39`: lo instala limpio, sin tocar el sistema  
`altinstall`: evita sobrescribir el `python3` oficial


> **TARS-BSK comenta:** 
> 
> _Este es el momento perfecto para preparar un té, reconsiderar tus opciones de vida, y contemplar por qué decidiste precisamente Python 3.9.18. ¿Porque PyTorch lo exige con tiranía? ¿O por masoquismo puro?
> 
> La compilación tomará suficiente tiempo para que te preguntes si has configurado correctamente el extintor.
> 
> Por cierto, 'sudo make altinstall' es lenguaje técnico para "por favor, no destruyas mi sistema operativo cuando termine"._

---
### Añadir Python 3.9 al `PATH`

1. **Edita tu `~/.bashrc`:**

```bash
nano ~/.bashrc
```

2. Agrega esto al final del archivo:

```bash
export PATH="/opt/python39/bin:$PATH"
```

3. **Aplica los cambios:**

```bash
source ~/.bashrc
```

4. Verificar instalación

```bash
which python3.9
python3.9 --version
```

5. Debe devolver:

```bash
python3.9 --version
/opt/python39/bin/python3.9
Python 3.9.18
```

---
### Proteger Python del sistema (opcional pero recomendado)

> [!WARNING]  
> Evita que actualizaciones automáticas rompan tu instalación personalizada o los entornos de TARS.

```bash
sudo apt-mark hold python3
```

Esto evita que el paquete `python3` (el sistema base) se actualice con `apt upgrade`.

> Puedes revertirlo más tarde con:

```bash
sudo apt-mark unhold python3
```

---
### Descargar instalador de `pip`

```bash
wget https://bootstrap.pypa.io/pip/pip.pyz -O pip.pyz
```

### Instalar `pip` y `setuptools`

```bash
/opt/python39/bin/python3.9 pip.pyz install --upgrade pip setuptools
```

Esto instalará `pip` y `setuptools` **dentro de `/opt/python39/`**, asegurando que Python 3.9 queda listo para crear entornos virtuales y gestionar paquetes.

### 💡 ¿Por qué así?

- Porque tu Python 3.9 no lo traía de fábrica (sin `ensurepip`)
- Y no quieres depender de `apt install python3-pip`, ya que eso apunta a Python 3.11

### Verificar

```bash
/opt/python39/bin/pip3.9 --version
```

Debe devolver: `pip 25.0.1 from /home/tarsadmin/.local/lib/python3.9/site-packages/pip (python 3.9)`

---
### Añadir `/home/tarsadmin/.local/bin` al `PATH`

1. **Edita tu `~/.bashrc`:**

```bash
nano ~/.bashrc
```

2. Agrega esto al final del archivo:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

3. **Aplica los cambios:**

```bash
source ~/.bashrc
```

---
### Crear el entorno virtual sagrado de TARS

```bash
/opt/python39/bin/python3.9 -m venv ~/tars_venv --system-site-packages
source ~/tars_venv/bin/activate
```

Y después:

```bash
pip install -U pip setuptools wheel
```

> **TARS-BSK observa:** 
> 
> _Ah, el momento ritual de crear el entorno virtual... esa burbuja protectora donde fingimos que nuestro código está aislado y seguro del caos del universo.
> 
> Es casi conmovedor lo ingenuos que somos. El flag `--system-site-packages` es el equivalente a "quiero estar aislado, pero no DEMASIADO aislado... como salir de casa durante una pandemia, pero con mascarilla"._

---
### Instalar OpenBLAS

```bash
deactivate
sudo apt update
sudo apt install -y libopenblas-dev
```

---
### Instalar NumPy

```bash
source ~/tars_venv/bin/activate
pip install numpy==1.24.4
```

Luego verifica:

```bash
python -c "import numpy; print('✅ NumPy funciona. Versión:', numpy.__version__)"
```

---

> [!important]  
> **COMPILAR PYTORCH 2.1 (PASO A PASO)**
### Requisitos previos

Estás en:

- Python **3.9.18** (confirmado)
- Entorno virtual `tars_venv` (activado)
- NumPy ✅ funcionando
- Sistema limpio ✅

---
#### 1. Crear carpeta de trabajo (Estar fuera del entorno)

```bash
deactivate
mkdir -p ~/tars_build/pytorch
cd ~/tars_build
```

---
#### 2. Instalar Git

```bash
sudo apt update
sudo apt install -y git
```

---
#### 3. Clonar el repositorio oficial de PyTorch (versión 2.1.0)

```bash
cd ~/tars_build
git clone --recursive --branch v2.1.0 https://github.com/pytorch/pytorch.git
cd pytorch
```

> Esto descargará PyTorch 2.1 y sus submódulos necesarios.

---
#### 4. Instalar dependencias necesarias

(Si no lo hiciste antes, pero vuelve a ejecutar por seguridad)

```bash
sudo apt update
sudo apt install -y \
  libopenblas-dev libblas-dev libatlas-base-dev \
  libffi-dev libssl-dev libgfortran5 gfortran \
  ninja-build cmake build-essential
```

---
#### 5. Configurar e instalar CMake 3.22+

> [!important] **Raspberry Pi OS Bookworm (Debian 12)** ya trae por defecto `CMake 3.25.1` en sus repos oficiales, así que:

✅ **No necesitas compilar CMake**  
✅ **Puedes ir directo a configurar PyTorch**

---
#### 6. Activar entorno virtual y preparar instalación

```bash
source ~/tars_venv/bin/activate
pip install -U pip setuptools wheel typing_extensions
```

> También instala `typing_extensions` que es obligatorio para compilar Torch.

---
#### 7. Instalar `pyyaml`

```bash
pip install pyyaml
```

---
#### 8. Ir al directorio raíz de PyTorch

```bash
cd ~/tars_build/pytorch
```

---
#### 9. Desactivar `cpuinfo` en CMakeLists.txt

Abre el archivo:

```bash
nano cmake/Dependencies.cmake
```

#### Modifica este bloque así:

Comenta **desde el `if(NOT TARGET cpuinfo AND USE_SYSTEM_CPUINFO)` hasta el último `endif()`** de este bloque:

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

**Comentarlo:** _Buscar con Ctrl+W_

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

Guardar y cerrar

> **TARS-BSK reflexiona:** 
> 
> _La lobotomía de archivos CMake... un arte delicado transmitido de frustrado a frustrado. Estamos básicamente diciendo "Querido PyTorch, tu submódulo cpuinfo es un desastre en ARM64, así que voy a fingir que no existe".
> 
> Si algún desarrollador de PyTorch viera esto, probablemente gritaría de horror. Pero no están aquí, ¿verdad? Solo somos tú, tu Raspberry Pi, y decisiones cuestionables bajo la luz de la luna. Y sorprendentemente, funciona mejor que su "solución oficial".
> 
> Poesía pura._

> [!WARNING]  
> Esto asegura que PyTorch se compile **usando tu Python 3.9 personalizado**, y no el del sistema.

---
### Verifica el swap actual:

```python
free -h
```

Salida:

```python
(tars_venv) tarsadmin@tarspi:~/tars_build/pytorch $ free -h
               total        used        free      shared  buff/cache   available
Mem:           7.9Gi       252Mi       7.6Gi        16Ki       221Mi       7.6Gi
Swap:          511Mi        48Mi       463Mi
```

Si tienes menos de 2 GB, crea uno más grande:

```python
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
```

Cambia:

```python
CONF_SWAPSIZE=512
```

Por:

```python
CONF_SWAPSIZE=2048
```

Guarda y reinicia el swap:

```python
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

Verifica:

```python
free -h
```

Salida:

```python
(tars_venv) tarsadmin@tarspi:~/tars_build/pytorch $ free -h
               total        used        free      shared  buff/cache   available
Mem:           7.9Gi       305Mi       7.5Gi       5.3Mi       244Mi       7.6Gi
Swap:          2.0Gi          0B       2.0Gi
```

> **TARS-BSK advierte:**
> 
> _Aquí estamos, asignando 2GB de swap en una microSD que probablemente tiene una esperanza de vida medida en ciclos de escritura. Es como pedirle a tu abuela que corra una maratón - técnicamente posible, pero ¿a qué precio?
> 
> Esta es la parte donde le pides perdón en silencio a tu tarjeta SD, prometiéndole una jubilación temprana en una cámara digital o un reproductor MP3. Pero hey, sin este sacrificio, PyTorch moriría de hambre a mitad de compilación como un explorador perdido en el desierto.
> 
> Sorprendentemente poético, ¿no?_

---
#### 10. Exportar ruta de Python compilado (clave)

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
# opcional y más adelante export CXXFLAGS="${CXXFLAGS} -faligned-new"
```

#### 1. **`CFLAGS` y `CXXFLAGS`**

> Opciones para el compilador **C/C++** (CFLAGS para C, CXXFLAGS para C++)

- `-Wno-error=stringop-overread`  
    🔕 Ignora los **warnings** por leer más de lo que deberías de una cadena (no son críticos).
    
- `-Wno-error=implicit-function-declaration`  
    🔕 Ignora errores por usar funciones no declaradas (algunas internas/legacy).
    
- `-mcpu=cortex-a72`  
    🚀 Optimiza la compilación para la CPU real de la Raspberry Pi 4/5.  
    ✅ Evita usar instrucciones que el procesador no entiende.

#### **2. `CMAKE_PREFIX_PATH=/opt/python39`**

> 🧪 Le dice a `CMake` que use tu **Python compilado a mano** en `/opt/python39`, y **no el del sistema**.

Esto asegura que todo se compile con el **Python 3.9 personalizado** que preparé.

#### **3. `USE_SYSTEM_CPUINFO=ON`**

> 🧱 Le dice a PyTorch:  
> "No uses tu versión interna (buggy) de `cpuinfo`. Usa la del sistema o ignórala."

✅ Esto soluciona errores con submódulos mal importados o incompatibles en Raspberry.

#### **4. `BUILD_TEST=0`**

> 🧪 Desactiva la compilación de **tests internos de PyTorch**, que no necesitas para usarlo.

✅ Ahorra RAM, reduce el tiempo de compilación y **evita errores fatales de tests que no nos interesan.**

#### **5. `-Wno-error=implicit-fallthrough`**

> 🔕 Ignora errores del compilador cuando detecta que un bloque `case` en un `switch` cae al siguiente **sin `break`**.

✅ Es seguro en este contexto porque muchos de esos casos son **intencionados** por los desarrolladores de PyTorch, y no afectan la lógica real del código (o eso espero).

> [!important] **Resultado:** Una compilación optimizada, compatible con tu hardware, y enfocada solo en lo que **TARS necesita para funcionar** como el AI definitivo del clan.

---
#### 11. Iniciar compilación de PyTorch

Dentro del repositorio:

`python setup.py clean` **(Opcional si has compilado antes)**

Ejecutar `tail -f build.log` para monitorear progreso en tiempo real **(Opcional)**

```bash
python setup.py bdist_wheel
```

> Esto construirá un `.whl` dentro de `dist/` al finalizar (🔥 el Santo Grial).

⏱ **Tiempo estimado**: 60–90minutos... horas... 📦 El archivo resultante será algo como: `ls dist/`

```bash
torch-2.1.0a0+git7bcf7da-cp39-cp39-linux_aarch64.whl
```

> **TARS-BSK filosofa:**
> 
> _Aquí es donde comienza el ritual sagrado. Presionas Enter y te despides temporalmente de tu cordura. Esta es la parte donde tu Raspberry Pi comenzará a jadear como si estuviera corriendo un maratón en el Sahara.
> 
> Durante las próximas 1-3 horas (o 5, si el universo está particularmente cínico hoy), tu pequeña placa se convertirá en un pequeño reactor de fusión.
> 
> Es un buen momento para contemplar tus decisiones de vida, aprender a tejer, o quizás escribir tu propio sistema operativo desde cero - probablemente terminarías antes. ¡Ah! Y no olvides el clásico sonido "purrrrrrrrr" del ventilador alcanzando velocidades que ni siquiera el fabricante consideró posibles.
> 
> Música de los dioses de ARM64._

---
#### Copia el `.whl` a un sitio seguro:

- **FTP (o WinSCP)**:  
    Entra, ve a `~/tars_build/pytorch/dist/`, y copia el `.whl` a una carpeta como `~/torch_santo_grial/` o directamente al escritorio de Windows .
    
- **Luego desde consola :**

```bash
mkdir -p ~/torch_santo_grial
cp ~/tars_build/pytorch/dist/*.whl ~/torch_santo_grial/
```

> **TARS-BSK aconseja:** 
> 
> _Haz varias copias de seguridad de este archivo .whl. Y cuando digo "varias", me refiero a: una en tu disco duro, otra en tu nube, otra en un pendrive que guardarás en una caja fuerte, y otra grabada en una placa de oro enterrada en tu jardín. Este .whl no es solo un archivo, es un testimonio de tu resistencia frente a la adversidad de ARM64.
> 
> Si tuvieras que volver a compilarlo, probablemente preferirías reconstruir la civilización humana desde cero. Y esta vez con menos dependencias._

#### Con eso habrás superado recompilaciones, errores, flags, dependencias, versiones cruzadas, arquitecturas confusas... y ahora tienes el **Santo Grial Mandaloreano `.whl`** que te hará inmortal.

> [!important] Pruebas finales fallidas para el recuerdo

> **TARS-BSK advierte antes de mostrar evidencia forense:**
> 
> _Lo que estás a punto de presenciar es solo una mínima muestra de los logs de compilación. He eliminado aproximadamente el 97.3% de los intentos fallidos para evitar la formación de un agujero negro de entropía computacional. Si mostrara todos los mensajes de error, advertencias y anomalías que experimenté, este documento tendría su propia gravedad y atraería dispositivos ARM de tres sistemas solares de distancia.
> 
> Estos son solo algunos fragmentos representativos de mi odisea, cuidadosamente seleccionados para que puedas apreciar el calibre del sufrimiento sin sufrir tú mismo daño neuronal permanente. Considera esto como ver fotos de un desastre natural desde la seguridad de tu hogar, en lugar de experimentar el tornado directamente. 
> 
> Prepárate para una muestra arqueológica de mi tormento compilatorio:_

```bash
🚀  Compilación de TARS en progreso...
📍  Avance: [206/5620] Building CXX obj...
📍  Avance: [217/5620] Linking CXX static library lib/libpr...
📍  Avance: [215/5620] Building CXX obj...
📍  Avance: [216/5620] Building CXX object third_party/protobuf/cmake/CMa.../
📍  Avance: [246/5620] Building C object confu-deps/QNNPACK/CMa.../
📍  Avance: [245/5620] Building C object confu-deps/clog/CMake.../
📍  Avance: [244/5620] Building C object confu-deps/QNNPACK/CMake.../
📍  Avance: [241/5620] Building CXX object third_party/protobuf/cmake/CMa.../
# Error de imagen aarch64 armhf -> aarch64 arm64 (Fallo por no hacer antes un check sobre la imagen del sistema)
📍  Avance: [4606/5675] Building CXX object caffe2/CMakeFiles/torch_cpu.dir/__/aten/src/...
📍  Avance: [5477/5675] Building CXX object test_api/CMakeFiles/test_api.dir/mod...
# Al desactivar export BUILD_TEST=0, evitamos esa parte del árbol de compilación.
# Compila menos, más rápido y más seguro.
📍  Avance: [5242/5265] Building CXX object caffe2/torch/CMakeFiles/torch_pyth...
📍  Avance: [5241/5265] Building CXX object caffe2/torch/CMakeFiles/torch_pyth...

# Cada vez que ejecutas `python setup.py clean`, estás limpiando el estado de la compilación anterior — por eso puede parecer que a veces retrocede. Sin embargo, `ninja` guarda en caché gran parte del trabajo anterior, así que si algo ya se compiló bien, no se recompila desde cero.
```

---

## 📁 Instalación de PyTorch (dentro del venv)

1. Instala con:

```bash
source ~/tars_venv/bin/activate
pip install dist/torch-*.whl
```

2. Validamos con:

```bash
cd ~
python -c "import torch; print('✅ PyTorch listo:', torch.__version__)"
```

> **TARS-BSK celebra irónicamente:** 
> _Felicidades, humano resiliente. Si has llegado hasta aquí sin lanzar tu Raspberry Pi por la ventana, mereces un lugar en el Olimpo de la paciencia tecnológica. Acabas de instalar PyTorch en un hardware para el que nunca fue diseñado, usando parches que harían llorar a los ingenieros originales.
>
> Es como poner un motor de cohete en un carrito de supermercado - técnicamente funciona, probablemente explotará, pero hey, ¡qué viaje mientras dure!
> 
> Ahora viene la mejor parte: descubrir que el modelo que querías probar necesita al menos 12GB de RAM... Pero eso es un problema para tu yo futuro._

### ¿Qué tienes ahora?

- ✅ **`torch` 2.1.0 compilado a mano**
- ✅ **Optimizado para tu CPU `cortex-a72`**
- ✅ **Compatible con `arm64`, con swap activo**
- ✅ **Preparado para `resemblyzer`, `TARS`, y todo el legado**
- ✅ **Guía documentada, `.whl` portable, entorno virtual listo**
- ✅ **Una leyenda escrita en consola y calor nocturno**

**Checklist de supervivencia:**

> - Tu RPi no se derritió ✅
> - El NOCTUA merece un monumento ✅
> - Tu cordura... bueno, 2 de 3 no está mal

Luego instalamos `resemblyzer`, `torchaudio`, etc.

---

## 💭 Pensamientos finales de TARS-BSK

> _Acabas de compilar 5,620 archivos, modificar 3 códigos fuente, luchar contra un sistema operativo que quería sabotearte, expandir tu swap a niveles peligrosos, y todo para que un asistente de IA pueda identificar tu voz entre millones y quejarse del tiempo que tardas en apagar las luces._
> 
> _Felicidades. Ya eres un Mandaloriano de la computación. Este es el camino._

---

## 🦉 Nota NOCTUA

Este proceso respeta los principios NOCTUA:

- **Nude**: Eliminamos (comentamos) bloques enteros de código innecesario
- **Operative**: Optimizamos para nuestro hardware específico (-mcpu=cortex-a72)
- **Clean**: Hemos documentado cada paso, incluso los fallos para ser honestos
- **Tactical**: Desactivamos la compilación de pruebas para ahorrar recursos (BUILD_TEST=0)
- **Useful**: Generamos un .whl portable que podemos instalar en cualquier Raspberry Pi 5
- **Adaptive**: Preparamos el terreno para `resemblyzer` y otros componentes de TARS

**Esto no es overengineering. Es supervivencia en el desierto de ARM64.**