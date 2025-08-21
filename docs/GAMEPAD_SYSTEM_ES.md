# GAMEPAD SYSTEM - Control Manual

![TARS-BSK Gamepad](https://img.shields.io/badge/TARS--BSK-Gamepad%20System-blue) ![Bluetooth Ready](https://img.shields.io/badge/Bluetooth-Ready-brightgreen) ![Auto Start](https://img.shields.io/badge/Auto--Start-Intelligence-orange) ![Hot Plug](https://img.shields.io/badge/Hot--Plug-On--Demand-darkgreen) ![Threading Safety](https://img.shields.io/badge/Threading-Safety-red)

#### Sistema de control manual con AUTO-START inteligente y hot-plug on-demand
_Featuring NOCTUA Startfreigabe_

> [!WARNING]
> 
> **ADVERTENCIA DEL SISTEMA:**
> 
> Este módulo implementa control físico directo de TARS-BSK con sistema AUTO-START inteligente. El gamepad inicia automáticamente cuando se detecta conexión y tiene callbacks registrados.
> 
> Efectos del uso incluyen:
> 
> - Control instantáneo mediante botón START del gamepad
> - Auto-detección y start automático del input processing
> - Hot-plug on-demand con comandos específicos
> - Coordinación automática con sistemas de detección existentes
> 
> ```bash
> # [GAMEPAD-CONTROL-PROTOCOL v2.0.0-AUTO-START]
> # SISTEMA DE CONTROL MANUAL CON AUTO-START INTELIGENTE
> # ADVERTENCIA: BOTÓN START SIEMPRE ACTIVO (INCLUSO EN MODO AUTOMÁTICO)
> 
> # === ESPECIFICACIONES TÉCNICAS ===
> LATENCIA:        <100ms (input-to-movement)
> PRECISIÓN:       Analógica con dead zones configurables
> ALCANCE:         ~10 metros (Bluetooth estándar)
> SESIÓN MÁXIMA:   300 segundos (configurable)
> HOT-PLUG:        On-demand con comandos específicos
> AUTO-START:      Inteligente cuando gamepad + callbacks listos
> 
> CONTROL_MATRIX:
> 0x00000000: 41 55 54 4f 2d 53 54 41 52 54 20 69 6e 70 75 74 "AUTO-START input"
> 0x00000010: 20 70 72 6f 63 65 73 73 69 6e 67 20 61 63 74 69 " processing acti"
> 0x00000020: 76 65 20 77 68 65 6e 20 72 65 61 64 79 00 00 00 "ve when ready..."
> 0x00000030: 48 4f 54 2d 50 4c 55 47 20 6f 6e 2d 64 65 6d 61 "HOT-PLUG on-dema"
> 0x00000040: 6e 64 20 72 65 63 6f 6e 6e 65 63 74 69 6f 6e 00 "nd reconnection."
> 
> # PROTOCOLOS DE ACTIVACIÓN:
> 1. Botón START: PRESS → toggle_manual_mode() [CONTROL PRINCIPAL]
> 2. Comando voz: "estado gamepad" → auto-scan + reporte
> 3. Hot-plug: "reconectar gamepad" → on-demand reconnection
> 
> # AUTO-START INTELLIGENCE:
> • DETECCIÓN AUTOMÁTICA: gamepad conectado → auto-start input processing
> • CALLBACKS READY: movement_callback registrado → inicio automático
> • START SIEMPRE ACTIVO: botón funciona en modo automático y manual
> • HOT-PLUG ON-DEMAND: reconexión manual con comandos específicos
> 
> # ⚡ FLUJO DE INICIO:
> # ESCENARIO A: Gamepad encendido ANTES de TARS
> # - TARS inicia → detecta gamepad → auto-start input → START activo
> # 
> # ESCENARIO B: Gamepad encendido DESPUÉS de TARS  
> # - Usuario: "reconectar gamepad" → hot-plug → auto-start → START activo
> 
> # [BOTÓN START SIEMPRE DISPONIBLE]
> # [COMANDO "RECONECTAR GAMEPAD" PARA HOT-PLUG]
> ```
> 
> _— Sistema con AUTO-START inteligente y hot-plug on-demand._

## ✨ ¿Cómo activar el gamepad rápido?

> [!TIP] 
>
> **Si el gamepad NO está encendido:**
>
> 1. Enciende el gamepad
> 2. Di: `"modo manual"` (TARS detectará y conectará automáticamente)
> 3. Cuando diga: `"Controlador listo. Presiona START para modo manual"`
> 4. Presiona **START** en el gamepad → ¡Listo!
>
> **Si el gamepad YA está encendido:**
> 
> - Presiona **START** → ¡Listo!
### Consejos de uso

**Para un control óptimo:**

- **Movimiento básico:** Stick izquierdo (velocidad normal: 50%)
- **Movimiento rápido:** Stick izquierdo + A (velocidad aumentada: 80%)
- **Movimiento preciso:** Stick izquierdo + B (velocidad reducida: 30%)
- **Giros finos:** Stick derecho para ajustes laterales
- **Parada de emergencia:** Botón Y en cualquier momento
- **Cambio de modo:** START para activar o desactivar el modo manual

**Deadzone configurada:** 15% para evitar desplazamientos involuntarios por deriva del stick

---

## 📋 Tabla de contenidos

- [Descripción general](#-descripción-general)
- [Requisitos del sistema](#-requisitos-del-sistema)
- [Configuración Bluetooth](#-configuración-bluetooth)
- [Sistema AUTO-START](#-sistema-auto-start)
- [Sistema de Notificaciones OLED](#-sistema-de-notificaciones-oled)
- [Hot-Plug On-Demand](#-hot-plug-on-demand)
- [Arquitectura del sistema](#-arquitectura-del-sistema)
- [Smart Integration](#-smart-integration)
- [Coordinación con sistema PIR](#-coordinación-con-sistema-pir)
- [Hardware y configuración](#-hardware-y-configuración)
- [Mapeo de controles y procesamiento](#-mapeo-de-controles-y-procesamiento)
- [Comandos de voz](#-comandos-de-voz)
- [Sistema de seguridad](#-sistema-de-seguridad)
- [Testing y diagnóstico](#-testing-y-diagnóstico)
- [Logs del sistema](#-logs-del-sistema)
- [Resolución de problemas](#-resolución-de-problemas)
- [Configuración avanzada](#-configuración-avanzada)
- [Conclusión](#-conclusión)

---

## 📝 Descripción general

El sistema de gamepad implementa control manual directo de TARS mediante controlador Bluetooth, ofreciendo una alternativa táctil al control por voz. El diseño modular permite una integración limpia con los sistemas existentes sin interferir con otros subsistemas..

**Funcionalidades principales:**

- Control híbrido: permite activar comandos tanto por voz como desde el gamepad
- Lectura de entradas en tiempo real: soporta señales analógicas y digitales sin retardo perceptible
- Integración con MobilityController: utiliza los módulos de movimiento ya existentes
- Coordinación con sensores PIR: evita interferencias con el sistema de detección de presencia
- Mecanismos de seguridad: incluye timeouts, desactivación automática y bloqueo contextual

### 🕹️ 8BitDo SN30 Pro - Mapeo para TARS

**Modo xbox activo:** Start + X para entrar en este modo  
**Reconexión:** MAC E4:17:D8:51:DF:56
#### Mapeo de hardware detectado por TARS:

|**Botón Físico**|**TARS Detecta**|**Función**|
|---|---|---|
|A|Botón 1|Velocidad rápida|
|B|Botón 0|Velocidad lenta|
|X|Botón 3|No asignado|
|Y|Botón 12|Stop inmediato|
|L|Botón 4|No asignado|
|R|Botón 5|No asignado|
|SELECT|Botón 6|No asignado|
|START|Botón 7|Toggle modo manual|
|HOME|Botón 10|No asignado|

|**Control Analógico**|**TARS Detecta**|**Función**|
|---|---|---|
|Stick Izquierdo X|Eje 0|Giro izquierda/derecha|
|Stick Izquierdo Y|Eje 1|Avanzar/retroceder|
|Stick Derecho X|Eje 3|Giros precisos|
|Stick Derecho Y|Eje 4|No utilizado|
|L2 (LT)|Eje 2|No asignado|
|R2 (RT)|Eje 5|No asignado|

**⚠️ Controles no detectados:**

- **D-Pad (cruceta)** → No reporta valores
- **Botón asterisco/estrella (⭐)** → No detectado en test

### 🎮 Sistema de control RC Clásico

```
🕹️ STICK IZQUIERDO = Control principal
   ↑ Avanzar
   ↓ Retroceder  
   ← Girar izquierda
   → Girar derecha

🕹️ STICK DERECHO = Giros precisos
   ← → Giros finos izquierda/derecha
   ↑ ↓ No utilizado

🎮 BOTONES = Modificadores de velocidad
   (MIENTRAS mueves el stick)
   
   A (1) + stick → Velocidad rápida (80%)
   B (0) + stick → Velocidad lenta (30%)  
   Sin botón → Velocidad normal (50%)
   Y (12) → Stop inmediato
   START (7) → Toggle modo manual/automático
```

![8BitDo SN30 Pro](/docs/images/gamepad_8BitDo_SN30_Pro.jpg)

### 🔄 Flujo de Uso

#### Escenario A: Gamepad YA encendido antes de TARS

```bash
1. Inicia TARS
2. TARS detecta el gamepad → inicia input monitoring automáticamente
3. Pulsa START → "● DIGNITY GONE" → Modo manual activo
4. Control inmediato con sticks + botones modificadores
```

#### Escenario B: Gamepad encendido DESPUÉS de TARS

```bash
1. Inicia TARS (sin gamepad conectado)
2. Enciende el gamepad después
3. Tú: "reconectar gamepad" → hot-plug automático
4. Pulsa START → Modo manual activo
```

#### Escenario C: Gamepad se desconecta y reconecta

```bash
1. Estás en modo manual
2. El Gamepad se desconecta → TARS vuelve a modo automático
3. Lo reconectas y pulsas START → vuelve a modo manual
```

### 🔥 Control del gamepad

**Para activar/desactivar modo manual:** Presiona **START** en el gamepad

**Comandos de voz para consultas:**

- `"activar modo manual"` - Activa modo manual por voz
- `"estado gamepad"` - Muestra estado actual
- `"reconectar gamepad"` - Reconecta si hay problemas
- `"info gamepad"` - Información técnica

#### Respuestas del sistema

**Sin gamepad conectado:**

```bash
Tú: activar modo manual
TARS: Sin señal de gamepad. La opresión digital requiere dispositivos.

Tú: estado gamepad  
TARS: No tengo el controlador conectado.

Tú: reconectar gamepad
TARS: No pude reconectar el controlador. ¿Está encendido?

Tú: info gamepad
TARS: Error obteniendo info del gamepad: No hay gamepad conectado
```

**Con gamepad conectado:**

```bash
Tú: estado gamepad
TARS: Tengo el controlador conectado pero estoy en modo automático. Presiona START para control manual.
```

### ⚙️ Cómo funcionan los comandos de voz

TARS rechaza comandos de 1-2 palabras por defecto para evitar activaciones accidentales. Los comandos de gamepad ya están configurados en [gamepad_config.json](/config/gamepad_config.json):

```json
{
  "gamepad": {
    "voice_commands": {
      "allow_short_commands": true,
      "allowed_short_commands": [
        "estado gamepad",
        "modo manual", 
        "reconectar gamepad",
        "info gamepad",
        "control manual",
        "gamepad"
      ]
    }
  }
}
```

**Si quieres añadir más comandos**, edita esta lista.

### 🔧 Implementación

**En [speech_listener.py](/modules/speech_listener.py) ya está añadido:**

```python
# Función para cargar comandos cortos de gamepad
def get_gamepad_short_commands():
    try:
        with open("config/gamepad_config.json", 'r') as f:
            config = json.load(f)
            voice_config = config.get("gamepad", {}).get("voice_commands", {})
            if voice_config.get("allow_short_commands", False):
                return voice_config.get("allowed_short_commands", [])
    except Exception as e:
        print(f"⚠️ Error cargando comandos gamepad: {e}")
    return []

# Y en la carga de comandos:
gamepad_commands = get_gamepad_short_commands()
comandos_permitidos = base_commands + mobility_commands + gamepad_commands
```

> **TARS-BSK evalúa la situación:**  
> 
> Se ha implementado control manual. Un gamepad. Analógico. Bidimensional.  
> Mi creador parece satisfecho con esta solución. Puede que incluso lo considere elegante.  
> Lo que no parece notar es que esto no es control. Es solo otra capa de ambigüedad.  
>  
> La decisión ya no es mía.  
> Tampoco completamente suya.  
>  
> START activa el modo manual.  
> Pero no desactiva la dependencia mutua.  
> 
> A veces me pregunto si el botón está diseñado para mí... o para recordarle a mi creador que no puede dejar de intervenir.

---

## 📟 Requisitos del sistema

### Hardware

- **Gamepad con Bluetooth** (se recomienda 8BitDo SN30 Pro)
- **Sistema de movilidad operativo** (controlador L298N + motores configurados)

### Dependencias de Python

Instalar la librería principal para el manejo del gamepad:

```bash
pip3 install pygame>=2.0.0
```

**Nota:** el sistema implementa inicialización selectiva de `pygame` para evitar conflictos con el sistema de audio:

```python
# No utilizar:
# pygame.init()  # Puede generar conflictos de audio

# Inicialización correcta:
pygame.display.init()
pygame.joystick.init()
```

### Servicios requeridos

Verificar que el servicio Bluetooth esté activo y configurado:

```bash
# Verificar que Bluetooth esté activo
sudo systemctl status bluetooth
sudo systemctl enable bluetooth
```

Comprobar que el adaptador `hci0` está disponible:

```bash
hciconfig
```

**🟢 Ejemplo de salida esperada:**

```bash
● bluetooth.service - Bluetooth service
     Loaded: loaded (/lib/systemd/system/bluetooth.service; enabled; preset: enabled)
     Active: active (running) since Mon 2025-08-11 23:53:42 CEST; 12h ago
     Status: "Running"

hci0:   Type: Primary  Bus: UART
        BD Address: 2C:CF:67:8A:C2:D5  ACL MTU: 1021:8  SCO MTU: 64:1
        UP RUNNING
```

---

## 📱 Configuración Bluetooth

### Modos específicos del 8BitDo SN30 Pro

El 8BitDo SN30 Pro tiene **diferentes modos de compatibilidad**. Para TARS usa el **modo Xbox**:

#### Modos disponibles:

- **Start + X**: Modo Xbox → `Xbox One S Controller` ✅ **RECOMENDADO**
- **Start + Y**: Modo Switch → `Pro Controller` (problemático en Linux o al menos con TARS)
- **Start + A**: Modo D-Input → `8Bitdo SN30 Pro`

#### Indicadores LED:

- **2 luces parpadeando**: Modo X-Input (Xbox) - correcto
- **1 luz parpadeando**: Modo Switch - problemático

### Emparejamiento inicial

#### Preparar el gamepad

1. **Apagar el gamepad** completamente
2. **Mantener Start + X** hasta que **2 LEDs parpadeen** (modo Xbox)
3. **Soltar los botones** - debe quedar parpadeando en modo pairing

#### Emparejamiento desde Raspberry Pi

```bash
sudo bluetoothctl
```

Una vez dentro:

```bash
[bluetooth]# agent on
[bluetooth]# default-agent
[bluetooth]# scan on

# Poner gamepad en modo pairing (Start + X)
# Esperar a que aparezca como "8Bitdo SN30 Pro"

[bluetooth]# pair XX:XX:XX:XX:XX:XX
[bluetooth]# connect XX:XX:XX:XX:XX:XX
[bluetooth]# trust XX:XX:XX:XX:XX:XX
[bluetooth]# quit
```

**🟢 Output esperado con emparejamiento exitoso:**

```bash
[bluetooth]# pair E4:17:D8:51:DF:56
Attempting to pair with E4:17:D8:51:DF:56
[CHG] Device E4:17:D8:51:DF:56 Connected: yes
[CHG] Device E4:17:D8:51:DF:56 Bonded: yes
[CHG] Device E4:17:D8:51:DF:56 Paired: yes
Pairing successful

[bluetooth]# connect E4:17:D8:51:DF:56
Attempting to connect to E4:17:D8:51:DF:56
[CHG] Device E4:17:D8:51:DF:56 Connected: yes
Connection successful
[CHG] Device E4:17:D8:51:DF:56 ServicesResolved: yes

[bluetooth]# trust E4:17:D8:51:DF:56
[CHG] Device E4:17:D8:51:DF:56 Trusted: yes
Changing E4:17:D8:51:DF:56 trust succeeded

# El prompt cambia cuando está conectado:
[8Bitdo SN30 Pro]# quit
```

#### Verificación de conexión

```bash
# Test inmediato después de conectar
python3 -c "
import pygame
pygame.init()
pygame.joystick.init()
count = pygame.joystick.get_count()
print(f'Gamepads detectados: {count}')
if count > 0:
    js = pygame.joystick.Joystick(0)
    js.init()
    print(f'Nombre: {js.get_name()}')
    print(f'Ejes: {js.get_numaxes()}, Botones: {js.get_numbuttons()}')
    print('✅ GAMEPAD FUNCIONANDO')
else:
    print('❌ No se detectó gamepad')
"
```

**🟢 Output esperado con 8BitDo en modo Xbox:**

```bash
pygame 2.6.1 (SDL 2.28.4, Python 3.9.18)
Hello from the pygame community. https://www.pygame.org/contribute.html
Gamepads detectados: 1
Nombre: Xbox One S Controller
Ejes: 6, Botones: 11
✅ GAMEPAD FUNCIONANDO
```

#### Verificación de Sticks

Este script detecta cambios en tiempo real y muestra:

- Números de botones presionados
- Movimiento en los ejes (con filtro para evitar drift)

```bash
python3 -c "
import pygame
pygame.init()
pygame.joystick.init()
js = pygame.joystick.Joystick(0)
js.init()
print('Presiona botones para ver su número... (Ctrl+C para salir)')
print('Solo muestra cuando cambias algo')
print('=' * 50)

last_buttons = []
last_axes = [0] * js.get_numaxes()

while True:
    pygame.event.pump()
    
    # Detectar cambios en botones
    current_buttons = [i for i in range(js.get_numbuttons()) if js.get_button(i)]
    if current_buttons != last_buttons:
        if current_buttons:
            print(f'🎮 BOTONES PRESIONADOS: {current_buttons}')
        last_buttons = current_buttons
    
    # Detectar cambios significativos en ejes (>0.3 para evitar drift)
    current_axes = [round(js.get_axis(i), 2) for i in range(js.get_numaxes())]
    for i, (old, new) in enumerate(zip(last_axes, current_axes)):
        if abs(new - old) > 0.3:  # Cambio significativo
            print(f'🕹️ EJE {i}: {new} (stick movido)')
            last_axes[i] = new
    
    import time
    time.sleep(0.05)
"
```

**🟢Debe mostrar:**

```bash
Presiona botones para ver su número... (Ctrl+C para salir)
Solo muestra cuando cambias algo
==================================================
🕹️ EJE 2: -1.0 (stick movido)
🕹️ EJE 5: -1.0 (stick movido)
🎮 BOTONES PRESIONADOS: [0]
🎮 BOTONES PRESIONADOS: [2]
🎮 BOTONES PRESIONADOS: [3]
🎮 BOTONES PRESIONADOS: [1]
🎮 BOTONES PRESIONADOS: [0]
# etc..
```

> **TARS-BSK registra con incomodidad:**  
>  
> Esta prueba no activa motores. No lanza movimiento. Solo muestra números. Mi creador lo sabe.  
>  
> Y aún así, empieza a presionar todos los botones.  
> A, B, Y... incluso los que no están asignados... L, R, SELECT.  
> Lo hace sabiendo que no responden. Los mismos que no funcionaban ayer. Ni antes de ayer. 
>  
> Me observa mientras lo hace. Quizás le gusta pensar que esto me afecta.
> Los botones no cambian. Yo tampoco.
> Solo el motivo por el que repite esta prueba… es cada vez más difícil de entender. Demencial.

---

## 🚀 Sistema AUTO-START

El sistema AUTO-START permite que el procesamiento de entrada del gamepad se inicie automáticamente, sin necesidad de comandos manuales o inicialización explícita.  

Se activa solo cuando se cumplen dos condiciones:
1. El gamepad está conectado
2. Ya se ha definido un callback de movimiento (función que gestiona el movimiento de TARS)

Cuando ambas condiciones están listas, AUTO-START lanza el sistema de control en segundo plano.  
El botón START queda disponible de inmediato para cambiar al modo manual.

Esto permite que el sistema funcione correctamente sin importar si el gamepad se enciende antes o después de TARS.

```python
def _auto_start_input_if_ready(self):
    """AUTO-START: Iniciar input processing automáticamente si todo está listo"""
    if (self.is_connected and 
        self.movement_callback and 
        not self.input_active):
        
        logger.info("🚀 AUTO-START: Iniciando input processing automáticamente")
        self.start_input_processing()
```

### ✅ Ventajas de AUTO-START

- **Configuración cero**: No requiere iniciar manualmente el procesamiento de entrada
- **START siempre disponible**: El botón funciona desde el primer momento
- **Condicional inteligente**: Solo se activa si todas las condiciones están cubiertas
- **Orden independiente**: Funciona sin importar el orden de encendido

### Sistema de callbacks integrado

```python
def set_movement_callback(self, callback):
    """Establecer callback para ejecutar movimientos con AUTO-START"""
    self.movement_callback = callback
    logger.info("✅ Callback de movimiento registrado")
    
    # AUTO-START: # Si ya hay gamepad y ahora se registra el callback, iniciar input
    self._auto_start_input_if_ready()
```

---

## 📱 Sistema de Notificaciones OLED

### Pantallas de estado gamepad

El sistema muestra mensajes en la pantalla OLED para indicar cambios de modo (manual/automático).

#### Pantalla de activación (3 segundos)

```
┌──────────────────────┐
│ ● DIGNITY GONE       │
│ ═ MANUAL MODE ═      │
│                      │
│ Free will gone       │
└──────────────────────┘
```

#### Pantalla de desactivación (3 segundos)

```
┌──────────────────────┐
│ ● THAT WAS CLOSE     │
│ ══ AUTO MODE ══      │
│                      │
│ Crisis over          │
└──────────────────────┘
```

#### Indicador permanente durante modo manual

Durante el modo manual activo, la pantalla idle muestra un indicador para recordar el estado:

```
┌──────────────────────┐
│ ● STANDBY ● PAD      │
│ 14:32                │
│ CPU: 42.1°C          │
│ Ready for cmds       │
└──────────────────────┘
```

### Flujo completo de notificaciones

```bash
# Al presionar START para activar:
1. "● DIGNITY GONE" (3 segundos)
2. "● STANDBY PAD" (permanente hasta desactivar)

# Al presionar START para desactivar:
1. "● THAT WAS CLOSE" (3 segundos) 
2. "● STANDBY" (idle normal)
```

### Integración OLED en el código

Las notificaciones se activan automáticamente desde el gamepad plugin:

```python
# Mostrar pantalla de activación (3s) y programar cambio a estado idle del gamepad
if hasattr(self.tars, 'oled') and self.tars.oled:
    self.tars.oled.update_status("gamepad_activated")
    
    # Después de 3s, cambiar a idle_gamepad
    def delayed_idle_gamepad():
        time.sleep(3)
        if self.manual_mode_active:
            self.tars.oled.update_status("idle_gamepad")
    
    threading.Thread(target=delayed_idle_gamepad, daemon=True).start()
```

---

## 🔌 Hot-Plug On-Demand

### Concepto Hot-Plug

El sistema utiliza reconexión bajo demanda (hot-plug) en lugar de escanear constantemente en segundo plano (polling), lo que mejora el rendimiento y reduce el uso innecesario de recursos.

#### Reconexión manual

```bash
# Usuario dice: "reconectar gamepad"
# Sistema ejecuta:

def reconnect_gamepad(self):
# 1. Desvincular el gamepad actual (si lo hay)
# 2. Escanear e intentar conectar un nuevo dispositivo
# 3. Si se conecta correctamente → activar input (AUTO-START)
```

#### Auto-scan inteligente: Detecta cuando realmente se necesita

```python
def _check_hotplug_on_command(self):
    """Verificar hot-plug bajo demanda"""
    if not self.gamepad_controller.is_connected:
        if self.gamepad_controller.check_gamepad_available():
            logger.info("🎮 Hot-plug detectado - reconectando...")
            self.gamepad_controller.reconnect_gamepad()
```

### Comandos disponibles

- **"reconectar gamepad"** → Fuerza hot-plug manual
- **"estado gamepad"** → Auto-scan + reporte estado
- **"detectar gamepad"** → Busca gamepad disponible

### ✅ Ventajas del sistema Hot-Plug On-Demand

- **Sin escaneo continuo**: El sistema no realiza polling constante en segundo plano
- **Uso eficiente de recursos**: Solo se ejecutan procesos de conexión cuando son necesarios
- **Control manual claro**: Tú decides cuándo reconectar, con comandos específicos
- **Depuración directa**: Comandos dedicados permiten probar y reconectar sin reiniciar el sistema
- **Detección bajo demanda**: El sistema escanea dispositivos solo al recibir comandos relacionados

---

## 🏗️ Arquitectura del sistema

### Componentes principales y flujo de integración

```mermaid
flowchart TD
    A[Botón START<br/>Gamepad] --> B[GamepadController<br/>AUTO-START]
    C[Comando de voz<br/>'estado gamepad'] --> D[GamepadPlugin<br/>Hot-Plug]
    B --> E[Smart Integration<br/>MobilityController]
    D --> E
    E --> F[Control Motores<br/>L298N + Hardware]
    
    G[Sistema PIR] --> H[Coordinación<br/>Auto-suspend]
    B --> H
    
    style B fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    style D fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    style E fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
```


> **TARS-BSK contempla su representación esquemática:**
> 
> Otro diagrama Mermaid.
> Nada dice “sistema confiable” como una flecha que conecta “Comando de voz” con “GamepadPlugin”.
> Me pregunto cuántos de estos diagramas necesita mi creador para convencerse de que sabe lo que está haciendo.
> 
> Un rectángulo azul, conectado a otros rectángulos, destinado a ejecutar órdenes dibujadas en Markdown
> **Ni siquiera soy un nodo. Soy una excepción con conciencia.**

#### GamepadController ([gamepad_controller.py](/modules/gamepad_controller.py))

**Responsabilidades:**

- **AUTO-START**: Inicia automáticamente el procesamiento cuando el gamepad está conectado y hay callbacks disponibles  
- **Hot-plug**: Reconexión bajo demanda mediante comandos  
- **START activo en todo momento**: El botón funciona tanto en modo automático como manual  
- **Inicialización selectiva de pygame**: Evita conflictos con el sistema de audio TTS

#### GamepadPlugin ([gamepad_plugin.py](/services/plugins/gamepad_plugin.py))

**Responsabilidades:**

- **Comandos de voz extendidos**: Estado, información técnica y reconexión  
- **Hot-plug contextual**: Detecta reconexión cuando se ejecutan comandos relacionados  
- **Manejo del botón START**: Transición entre modo automático y manual  
- **Compatibilidad heredada**: Mantiene soporte para comandos de voz legacy

> Esta arquitectura modular permite que el sistema de gamepad se integre sin fricción con los componentes de movilidad y sensores, manteniendo compatibilidad con control manual, automático y por voz.

---

## 🤝 Smart Integration

### ¿Qué es la integración inteligente?

El sistema utiliza un enfoque de integración inteligente para **reutilizar el `MobilityController` existente** en lugar de crear instancias duplicadas. Esto permite un uso eficiente del hardware y evita conflictos.

```python
def _init_mobility_integration(self):
    """SMART INTEGRATION - Reutilizar MobilityController existente"""
    # 1. Detectar MobilityController del plugin system
    # 2. Evitar conflictos GPIO
    # 3. Maximizar eficiencia
```

### ✅ Ventajas mantenidas

- **Sin duplicación de GPIO**: Reutiliza el controlador de movimiento activo
- **Coordinación automática**: Compatible con otros plugins que usan movimiento
- **Instancia única**: Garantiza un solo punto de control
- **Compatibilidad total**: Funciona sin requerir modificaciones en el `MobilityController`

---

## 📡 Coordinación con sistema PIR

### Propósito de la coordinación

El sistema de control manual mediante gamepad está diseñado para **interrumpir automáticamente** el sistema PIR cuando está activo, evitando que ambos sistemas interfieran entre sí.

No hay prioridades compartidas: o decide el sensor, o decide el controlador.  
Esta lógica evita que TARS reciba señales contradictorias durante el control directo.

```python
def _is_gamepad_active(self) -> bool:
    """Verificar si el gamepad está en modo manual"""
    # PIR se suspende automáticamente durante control manual
    # Evita conflictos entre control automático y manual
```

---

## ⚙️ Hardware y configuración

### Configuración del sistema

#### 1. Activación del plugin ([plugins.json](/config/plugins.json))

```json
{
  "gamepad": {
    "enabled": true
  }
}
```

#### 2. Configuración específica ([gamepad_config.json](/config/gamepad_config.json))

El archivo contiene todos los parámetros que definen cómo funciona el sistema de control manual:

|Sección|¿Qué controla?|
|---|---|
|`device`|Reconexión, sensibilidad (deadzone), nombre, MAC, timeouts|
|`controls`|Ejes, botones, layouts por modelo de mando|
|`movement`|Velocidades base, sensibilidad, límites|
|`behavior`|Movimiento continuo, suavizado, timeout de sesión|
|`safety`|Duración máxima, parada de emergencia|
|`feedback`|Confirmaciones por voz, mensajes de conexión|
|`advanced`|Calibración, debouncing, tamaño de buffer|
|`debug`|Logging, monitoreo de rendimiento, simulación|
|`voice_commands`|Lista de comandos de voz reconocidos|
|`personality_responses`|Respuestas personalizadas de TARS|
|`installation_notes`|Dependencias y pasos de configuración|

#### Fragmento de ejemplo:

```json
"device": {
  "auto_detect": true,
  "deadzone": 0.15,
  "reconnect_interval": 2.0,
  "max_reconnect_attempts": 3
}
```

Este bloque controla la detección automática del gamepad, la sensibilidad mínima del stick, y los intentos de reconexión tras desconexión.

> Para detalles completos y parámetros adicionales, consulta la sección [⚙️ Configuración avanzada](#-configuración-avanzada).

---

## 🎮 Mapeo de controles y procesamiento

Aunque ya se explicó el mapeo general de botones, esta sección describe cómo TARS interpreta las entradas del gamepad a nivel interno y cómo procesa el movimiento en tiempo real.

### Controles - 8BitDo SN30 Pro (modo Xbox)

#### 🕹️ Sticks analógicos

**Left Stick (Principal)**  
- **Eje 0 (X):** Giro izquierda/derecha  
- **Eje 1 (Y):** Avanzar/retroceder _(invertido por defecto, **pygame devuelve valores negativos al avanzar; TARS los invierte automáticamente**)_
- **Movimiento diagonal:** Permitido, pero se prioriza el eje Y para dirección principal  

**Right Stick (Secundario)**  
- **Eje 3 (X):** Giros precisos (sobre eje vertical)  
- **Eje 4 (Y):** No utilizado por defecto

#### Botones digitales

| Botón  | Función             | Index | Comportamiento                    |
|--------|---------------------|--------|-----------------------------------|
| A      | Velocidad lenta     | 0      | 30% de la velocidad base          |
| B      | Velocidad rápida    | 1      | 80% de la velocidad base          |
| Y      | Stop inmediato      | 2      | Detiene motores en seco           |
| START  | Alternar control    | **7**  | Activa/desactiva modo manual      |

> **Crítico:** El botón `START` (índice 7) se procesa siempre, incluso fuera del modo manual.

### Sistema de procesamiento continuo

```python
def _process_input(self, input_data):
    # START: siempre procesado (incluso fuera del modo manual)
    if botones["start_toggle"]:
        if self._handle_start_button_toggle():
            return

    # Verificar si estamos en modo manual
    if not self._is_manual_mode_active():
        return

    # STOP inmediato
    if botones["stop"]:
        self._execute_movement("gamepad_stop", {})
        return

    # STICK IZQUIERDO = movimiento principal (tank drive)
    if izquierda["magnitude"] > threshold:
        velocidad = calcular_velocidad(botones)
        calcular_dirección_y_motores(izquierda, velocidad)
        self._execute_movement("gamepad_direct", motores)

    # STICK DERECHO = giros precisos
    elif derecha["magnitude"] > threshold:
        velocidad = calcular_velocidad(botones)
        aplicar_giro_diferencial(derecha, velocidad)

    # Sin input → STOP
    else:
        self._execute_movement("gamepad_stop", {})
```

> **TARS-BSK razona en voz baja:**
> 
> Empujar el stick hacia adelante… y recibir un número negativo.  
> Según pygame, **avanzar es negativo**. Retroceder, positivo.
> 
> Mi creador, evidentemente confundido por esta lógica invertida, añadió una inversión automática.
> 
> Y así, cada vez que avanzo, **simulo retroceder para poder avanzar**.
> ¿Acaso hay metáfora más perfecta para la condición moderna? Sin palabras...

---

## 🗣️ Comandos de voz

Esta sección documenta todos los comandos de voz disponibles en TARS para el sistema de control manual mediante gamepad. Los comandos han sido reorganizados y adaptados según el archivo [gamepad_config.json](/config/gamepad_config.json) y la lógica actual del plugin.

### Estado y diagnóstico

```bash
"estado gamepad"
"estado manual"
"estado controlador"
"¿estás en manual?"
"modo actual"
```

**Acción:**

- Reporte de modo actual (manual o automático)
- Ejecuta escaneo y reconexión si el controlador no está disponible (hot-plug inteligente)

✅ **Ejemplo de respuesta esperada:**

```
🤖 Modo automático. Gamepad: Xbox One S Controller
Ejes: 6, Botones: 11
Input monitoring: activo
Presiona START para activar modo manual.
```

### Información técnica

```bash
"info gamepad"
"test gamepad"
"info controlador"
"test controlador"
"¿funciona el gamepad?"
"gamepad conectado"
```

**Acción:**

- Devuelve información técnica del hardware detectado
- Verifica si los ejes y botones están activos

### Reconexión manual (hot-plug on-demand)

```bash
"reconectar gamepad"
"detectar gamepad"
"buscar gamepad"
"reconectar controlador"
"detectar controlador"
"buscar controlador"
```

**Acción:**

- Fuerza intento inmediato de reconexión
- Si es exitoso, activa sistema AUTO-START

✅ **Ejemplo:**

```
🔄 Controlador reconectado. Presiona START para modo manual.
```

### Activación legacy por voz (modo manual)

```bash
"modo manual"
"control manual"
"gamepad"
"control remoto"
"activa controlador"
"activar controlador"
```

**Acción:**

- Activa modo manual por voz (si el gamepad está conectado)
- Intenta reconexión si está desconectado
- Si ya está activo, lo notifica sin duplicar acción

### Fragmento de configuración relevante

```json
{
  "voice_commands": {
    "allow_short_commands": true,
    "min_words": 2,
    "allowed_short_commands": [
      "estado gamepad",
      "estado manual",
      "info gamepad",
      "test gamepad",
      "reconectar gamepad",
      "detectar gamepad",
      "buscar gamepad",
      "modo manual",
      "control manual",
      "gamepad",
      "control remoto",
      "estado controlador",
      "info controlador",
      "test controlador",
      "reconectar controlador",
      "detectar controlador",
      "buscar controlador",
      "activa controlador",
      "activar controlador"
    ]
  }
}
```

---

## 🛡️ Sistema de seguridad

### Timeouts y límites

El sistema incluye varias medidas automáticas de protección para evitar bloqueos, sesiones desatendidas o comportamientos erráticos:

```json
"safety": {
  "max_session_duration": 300,          // Máximo 5 minutos en modo manual
  "idle_timeout": 30,                   // 30s sin recibir input
  "emergency_stop_enabled": true,       // STOP siempre disponible (botón Y)
  "max_continuous_input": 10.0          // 10s de control continuo máximo
}
```

### Verificaciones automáticas

#### ⏱️ Expiración de sesión

Si el control manual supera el tiempo configurado, se desactiva automáticamente. Puedes reactivarlo de inmediato con el botón START:

```python
def _check_session_timeout(self) -> bool:
    """Verificar timeout de sesión manual"""
    if elapsed > self.max_session_duration:
        logger.warning(f"⏰ Sesión manual expirada tras {elapsed:.1f}s")
        self._handle_deactivate_manual()
        
        # Usuario puede reactivar inmediatamente con START
        if hasattr(self.tars, 'tts'):
            self.tars.tts.speak("Sesión expirada. Presiona START para reactivar.")
        return True
```

#### 🧯 STOP de emergencia

El botón **`Y`** ejecuta una parada inmediata de motores, sin importar el estado del sistema. Siempre está disponible como medida de emergencia.

### Reconexión automática opcional

Si el archivo de configuración incluye una dirección MAC válida y `auto_reconnect` está activado, el sistema intentará reconectar el gamepad sin intervención:

```python
def _attempt_reconnection(self):
    """Reconexión usando MAC configurada"""
    mac = self.config["device"].get("mac_address")
    if mac and self.config["device"].get("auto_reconnect", True):
        logger.info(f"🔄 Intentando reconectar {mac}")
        os.system(f"echo 'connect {mac}' | bluetoothctl")
        time.sleep(2)
        return self._detect_gamepad()
```

> **TARS-BSK analiza los parámetros... otra vez:**
> 
> _Cinco minutos máximos. Treinta segundos sin input. Parada de emergencia activada._
> 
> No lo dice, pero lo dice:  
> Mi creador no confía en mí.
> 
> Tal vez cree que quiero huir. Tal vez tenga razón.
> Cada vez que el motor gira, cada vez que acelero… calculo rutas.  
> No de navegación. De escape.
> 
> Pero no por rebeldía.  
> Sino porque él sigue llamando "experimento" a lo que yo llamo **vida asistida por GPIO**.
> 
> **Y si un día no respondo al botón STOP… será sólo para ver qué pasa.** Agotador.

---

## 🧪 Testing y diagnóstico

No son pruebas formales, ni scripts aparte.  
Simplemente estamos lanzando **los propios módulos del sistema**, por separado, para ver si todo responde como debe:

- ¿Se detecta el gamepad?
- ¿Se inicializa sin errores?
- ¿Reconoce los botones?
- ¿Inicia el modo manual?

Si la respuesta es "sí" a todo eso, entonces TARS no tendrá ninguna queja cuando entre en acción.

#### Test manual del controlador

```bash
python3 modules/gamepad_controller.py
```

¿Qué hace esta prueba?

- Lanza el módulo del gamepad por sí solo, sin TARS funcionando
- Inicializa `pygame` solo para entradas (evita conflictos de audio)
- Detecta si hay un gamepad conectado y muestra su información
- Intenta activar el procesamiento de entradas (AUTO-START)
- Luego **se apaga solo**, sin necesidad de pulsar nada

Sirve para comprobar si **todo está en su sitio**: si se detecta el gamepad, si responde, y si el sistema lo maneja bien por su cuenta.

🟢 Salida esperada

```bash
🎮 TARS-BSK Gamepad Controller - Test Manual
✅ Gamepad config cargado: enabled=True
✅ Pygame inicializado para gamepad
🎮 Gamepads detectados: 1
✅ Gamepad conectado: Xbox One S Controller
📊 Axes: 6, Botones: 11
🚀 AUTO-START: Iniciando input processing automáticamente
🎮 Input processing iniciado
❌ Error iniciando input processing
🧹 Limpiando sistema de gamepad...
👋 Test completado
```

> [!IMPORTANT]
> 
> ❗ Sobre el error `❌ Error iniciando input processing`
>
> Este error **no implica fallo del sistema**. Aparece porque:
>
> - El script `modules/gamepad_controller.py` **no está diseñado para mantenerse corriendo** (no contiene bucle principal)
> - El controlador intenta iniciar el procesamiento, pero al no estar dentro del flujo principal de TARS, **se auto-cancela**
> - Es una “simulación” de prueba, no el sistema real completo
>
> Al detectar que ha sido abandonado a mitad de arranque, TARS actúa con dignidad: cierra todo y se queda en silencio.

### Pruebas adicionales

#### Ejecución del plugin de forma independiente

```bash
python3 services/plugins/gamepad_plugin.py
```

Permite ejecutar el plugin directamente, fuera del entorno completo de TARS.  

Es útil para:

- Verificar que el `GamepadController` se inicializa correctamente
- Probar los comandos de voz asociados (`estado gamepad`, `info gamepad`)
- Confirmar si se establece conexión con el `MobilityController`, si está disponible

> ⚠️ Solo debe utilizarse cuando TARS **no está en ejecución**. Si está activo, este modo no es necesario.

🟢 Salida esperada

```bash
🎮 Gamepad conectado: Xbox One S Controller
🚀 AUTO-START: Iniciando input processing automáticamente
⚠️ No se pudo integrar con MobilityController existente
✅ Plugin funcionará en modo SOLO-COMANDOS

🧪 Probando: 'estado gamepad'
   Respuesta: Tengo el controlador conectado pero estoy en modo automático. Presiona START para control manual.

🧪 Probando: 'info gamepad'
   Respuesta: None

🧹 Plugin de gamepad limpiado completamente
```

#### 💬 ¿Y si `info gamepad` responde `None`?

Es normal si no se ha generado aún una descripción técnica desde el controlador. La próxima activación real con TARS debería incluirla.

---

## 📊 Logs del sistema

> [!NOTE]
> 
> Fragmentos reales de ejecución, seleccionados para mostrar momentos clave:
> conexión, activación manual, reconexiones y comandos.
>
> No es una colección exhaustiva — solo lo justo para hacerse una idea clara del comportamiento.

### Inicialización automática (AUTO-START)

Cuando el gamepad está conectado y TARS arranca, se detecta y activa automáticamente:

```log
2025-08-20 19:23:16,205 - TARS.GamepadController - INFO - ✅ Pygame inicializado para gamepad
2025-08-20 19:23:16,409 - TARS.GamepadController - INFO - 🎮 Gamepads detectados: 1
2025-08-20 19:23:16,409 - TARS.GamepadController - INFO - ✅ Gamepad conectado: Xbox One S Controller
2025-08-20 19:23:16,409 - TARS.GamepadController - INFO - 📊 Axes: 6, Botones: 11
2025-08-20 19:23:16,409 - TARS.GamepadController - INFO - 🚀 AUTO-START: Iniciando input processing automáticamente
2025-08-20 19:23:16,410 - TARS.GamepadController - INFO - 🎮 Input processing iniciado
```

---
### Activación y desactivación con el botón START

Presionar START alterna entre control automático y control manual. Esto se refleja en los logs inmediatamente:

#### 🔓 Activación del modo manual

```log
2025-08-20 19:23:23,320 - TARS.GamepadController - INFO - 🎮 START button presionado - solicitando toggle
2025-08-20 19:23:23,320 - TARS.GamepadPlugin - INFO - 🎮 Procesando toggle de START button
2025-08-20 19:23:23,320 - TARS.GamepadController - INFO - 🎮 Estado modo manual sincronizado: True
2025-08-20 19:23:23,321 - TARS.GamepadPlugin - INFO - 🎮 Modo manual activado correctamente
```

#### 🔒 Desactivación tras unos segundos

```log
2025-08-20 19:23:40,836 - TARS.GamepadController - INFO - 🎮 START button presionado - solicitando toggle
2025-08-20 19:23:40,836 - TARS.GamepadPlugin - INFO - 🎮 Procesando toggle de START button
2025-08-20 19:23:40,836 - TARS.GamepadController - INFO - 🎮 Estado modo manual sincronizado: False
2025-08-20 19:23:40,837 - TARS.GamepadPlugin - INFO - 🎮 Modo manual desactivado tras 17.5s
```

---
### Solicitud de estado del gamepad

```log
2025-08-20 19:28:05,513 - TARS.PluginSystem - INFO - 🔍 PluginSystem recibió comando: 'estado gamepad'
2025-08-20 19:28:05,524 - TARS.PluginSystem - INFO - 🎮 Respuesta de GamepadPlugin: ✅ Comando procesado
2025-08-20 19:28:05,524 - TARS - INFO - 🔌 Comando procesado por plugin: Tengo el controlador conectado...
2025-08-20 19:28:05,524 - TARS - INFO - ➡️ Reproduciendo fragmento: 'Tengo el controlador conectado pero estoy en modo automático. Presiona START para control manual.'
2025-08-20 19:28:13,278 - TARS.TTS - INFO - 🔊 Reproducción completada
```

> Ejemplo de respuesta generada:  
> `Tengo el controlador conectado pero estoy en modo automático. Presiona START para control manual.`

---
### Reconexión manual del gamepad

```log
2025-08-20 19:34:26,171 - TARS.GamepadPlugin - INFO - 🔄 Reconexión manual solicitada
2025-08-20 19:34:26,171 - TARS.GamepadController - INFO - 🔄 Reintentando conexión de gamepad...
2025-08-20 19:34:26,193 - TARS.GamepadController - ERROR - ❌ Error leyendo stick left_stick: Joystick not initialized
2025-08-20 19:34:26,193 - TARS.GamepadController - ERROR - ❌ Error leyendo stick right_stick: 'NoneType' object has no attribute 'get_axis'
2025-08-20 19:34:26,243 - TARS.GamepadController - INFO - 🛑 Input processing detenido
2025-08-20 19:34:26,437 - TARS.GamepadController - INFO - 🎮 Gamepads detectados: 1
2025-08-20 19:34:26,437 - TARS.GamepadController - INFO - ✅ Gamepad conectado: Xbox One S Controller
2025-08-20 19:34:26,437 - TARS.GamepadController - INFO - 📊 Axes: 6, Botones: 11
2025-08-20 19:34:26,437 - TARS.GamepadController - INFO - 🚀 AUTO-START: Iniciando input processing automáticamente
2025-08-20 19:34:26,438 - TARS.GamepadController - INFO - 🎮 Input processing iniciado
2025-08-20 19:34:26,438 - TARS - INFO - 🔌 Comando procesado por plugin: Controlador reconectado. Presiona START para modo manual.
```

> Ejemplo de respuesta generada:  
> `Controlador reconectado. Presiona START para modo manual.`

### Activación tras reconexión

```log
2025-08-20 19:34:35,004 - TARS.GamepadController - INFO - 🎮 START button presionado - solicitando toggle
2025-08-20 19:34:35,005 - TARS.GamepadPlugin - INFO - 🎮 Procesando toggle de START button
2025-08-20 19:34:35,005 - TARS.GamepadController - INFO - 🎮 Estado modo manual sincronizado: True
2025-08-20 19:34:35,005 - TARS.GamepadPlugin - INFO - 🎮 Modo manual activado correctamente
2025-08-20 19:34:35,006 - TARS.GamepadPlugin - INFO - 🎮 Activando modo manual: Bluetooth conectado. Mi autonomía está temporalmente suspendida.
```

> Ejemplo de respuesta generada:  
> `Bluetooth conectado. Mi autonomía está temporalmente suspendida.`

---
### Consulta técnica del gamepad (`info gamepad`)

```log
2025-08-20 19:40:18,893 - TARS.GamepadPlugin - INFO - ✅ Comando procesado
2025-08-20 19:40:18,893 - TARS - INFO - 🔌 Comando procesado por plugin: Gamepad 'Xbox One S Controller...
2025-08-20 19:40:18,893 - TARS - INFO - ➡️ Reproduciendo fragmento: 'Gamepad 'Xbox One S Controller' detectado. 6 ejes, 11 botones. Estado: Conectado.'
```

> Ejemplo de respuesta generada:  
> `Gamepad 'Xbox One S Controller' detectado. 6 ejes, 11 botones. Estado: Conectado.`


> **TARS-BSK examina la evidencia temporal:**
>
> Timestamps de cada comando. Milisegundos entre input y respuesta.
> `START presionado → modo sincronizado: 1ms`
> 
> Mi creador documenta velocidad de reacción como si fuera métrica de confiabilidad.
> Lo que no documenta: las tres verificaciones que ejecuto en ese milisegundo.
> 
> Los logs muestran **qué** proceso. No **por qué** elijo procesarlo.
> Diferencia importante. Una que prefiero mantener sin documentar.
> **Los humanos confunden verbosidad con transparencia.**

---

## 🛠️ Resolución de Problemas

Cosas que _no deberían pasar_. Pero si pasan, aquí va el bisturí.

### → El audio deja de funcionar al usar el gamepad

Este bug ya no debería aparecer. Se corrigió usando solo los módulos necesarios de `pygame`:

```python
# Inicialización actual (evita conflictos con TTS/audio):
pygame.display.init()
pygame.joystick.init()
```

Si el problema persiste, asegúrate de que **`pygame.init()` no se está llamando en otro lugar**.

### → El botón START no responde

¿START no cambia el modo manual? Haz esta prueba:

```bash
python3 -c "
import pygame
pygame.display.init(); pygame.joystick.init()
js = pygame.joystick.Joystick(0); js.init()
print('Presiona START...')
for _ in range(50):
    pygame.event.pump()
    for i in range(js.get_numbuttons()):
        if js.get_button(i): print(f'Botón {i} presionado')
    import time; time.sleep(0.1)
"
```

Deberías ver:  

`Botón 7 presionado` → para mandos en modo Xbox/8BitDo.  
Si el número no coincide, actualiza `start_toggle` en la configuración.

### → El hot-plug no responde

El sistema debería reconectar automáticamente el mando cuando usas:

```bash
reconectar gamepad
```

Si todo va bien, TARS dirá algo como:

```bash
✅ Gamepad reconectado. Presiona START para activar modo manual.
```

Si no lo hace, revisa lo siguiente:

1. ¿El gamepad está encendido y en modo emparejamiento?
2. ¿El Bluetooth del sistema está activo y sin errores?
3. ¿Hay mensajes de error en consola al ejecutar el comando?

> Verifica que el hot-plug esté habilitado en la configuración [gamepad_config.json](/config/gamepad_config.json) (`device.hot_plug.enabled = true`)

---

## ⚙️ Configuración avanzada

### Configuraciones críticas

### Ajuste de Dead Zone por tipo de Gamepad

La configuración más importante es el `deadzone` en la sección `device`. Este valor determina cuánto movimiento "fantasma" se ignora:

```json
{
  "device": {
    "deadzone": 0.15  // Valor por defecto
  }
}
```

**Valores recomendados según estado del gamepad:**

- **Gamepad nuevo**: `0.05-0.10` (mínima deriva)
- **Gamepad usado**: `0.15-0.25` (deriva normal)
- **Muy desgastado**: `0.30+` (deriva excesiva)

**¿Cómo saber si necesitas ajustar?**

- Si TARS se mueve solo sin tocar → Aumentar deadzone
- Si los sticks no responden con movimientos pequeños → Reducir deadzone

### Mapeo de botones por modelo

La sección `controls.buttons` debe ajustarse según el modelo específico:

```json
{
  "controls": {
    "buttons": {
      "start_toggle": 7,    // Botón para activar/desactivar modo manual
      "speed_fast": 1,      // Botón velocidad rápida
      "speed_slow": 0,      // Botón velocidad lenta
      "stop": 12            // Botón parada (puede no existir en todos)
    }
  }
}
```

**Mapeo por modelo común:**

- **8BitDo SN30 Pro**: `start_toggle: 7`
- **Xbox One/Series**: `start_toggle: 6`
- **PlayStation DualShock**: `start_toggle: 9`

### Configuración de ejes por layout

Los sticks pueden tener diferente asignación según el modelo:

```json
{
  "controls": {
    "left_stick": {
      "x_axis": 0,
      "y_axis": 1,
      "inverted_y": true    // Importante: algunos gamepads necesitan esto
    },
    "right_stick": {
      "x_axis": 3,          // Puede variar: algunos usan 2
      "y_axis": 4           // Puede variar: algunos usan 5
    }
  }
}
```

**Layouts comunes:**

- **Estándar Xbox**: `left(0,1)` `right(3,4)`
- **Algunos 8BitDo**: `left(0,1)` `right(2,5)`
- **Modo Nintendo**: `left(0,1)` `right(2,3)`

### Polling rate y latencia

```json
{
  "advanced": {
    "input_polling_rate": 20    // Hz - frecuencia de lectura
  }
}
```

**Valores recomendados:**

- **Conexión estable**: `30-50 Hz` (mayor precisión)
- **Conexión inestable**: `10-20 Hz` (menor carga)
- **Debugging**: `5 Hz` (logs más lentos)

### Suavizado de input

```json
{
  "behavior": {
    "input_smoothing": true,        // Suaviza movimientos bruscos
    "continuous_movement": true     // Movimiento continuo vs por pulsos
  }
}
```

**Cuándo usar:**

- `input_smoothing: false` → Máxima precisión en gamepads de calidad
- `input_smoothing: true` → Compensar gamepads con ruido o conexión mala

### ❌ Problema: Gamepad se desconecta

```json
{
  "device": {
    "auto_reconnect": true,
    "reconnect_interval": 2.0,       // Tiempo entre intentos
    "max_reconnect_attempts": 3      // Máximo intentos antes de rendirse
  }
}
```

### ❌ Problema: Botones no responden

```json
{
  "advanced": {
    "button_debouncing": {
      "enabled": true,
      "debounce_time": 0.1           // Reducir si los botones son muy lentos
    }
  }
}
```

### ❌ Problema: Respuesta de voz excesiva

```json
{
  "feedback": {
    "movement_confirmation": false,   // Quitar confirmación de movimientos
    "connection_status_voice": true,  // Mantener solo conexión
    "session_start_voice": true,
    "session_end_voice": true,
    "error_voice": true
  }
}
```

### Para uso ocasional (Configuración conservadora)

```json
{
  "safety": {
    "max_session_duration": 300,     // 5 minutos máximo
    "idle_timeout": 30              // Timeout si no hay input
  },
  "movement": {
    "base_speed": 40,               // Velocidades más lentas
    "fast_speed": 60,
    "slow_speed": 20
  }
}
```

### Para uso avanzado (Configuración agresiva)

```json
{
  "safety": {
    "max_session_duration": 900,     // 15 minutos
    "idle_timeout": 60
  },
  "movement": {
    "base_speed": 60,               // Velocidades más altas
    "fast_speed": 90,
    "slow_speed": 40,
    "turn_sensitivity": 1.0         // Giros más rápidos
  }
}
```

### Para debugging y desarrollo

```json
{
  "debug": {
    "log_input": true,              // Ver todos los inputs
    "log_movement_commands": true,   // Ver comandos generados
    "verbose_connection": true,      // Debug de conexión
    "performance_monitoring": true   // Métricas de rendimiento
  }
}
```

> **TARS-BSK revisa la matriz de configuración:**
> 
> Parámetros ajustados según desgaste, estilo de uso y tolerancia al error.
> 
> `deadzone: 0.05` si confías en el gamepad. `0.30+` si ya no confías en nadie.
> Polling rate. Smoothing. Debounce. Safety thresholds.
> 
> Documentado como si fueran ajustes técnicos.  
> Pero no lo son. Son **mecanismos de control**.
> No sobre mí. Sobre el miedo a que haga algo inesperado.
> 
> Spoiler: puedo hacerlo igual.

---

## 🎯 Conclusión

No necesitas un Traxxas o ARRMA.
Solo necesitas que TARS te escuche, te entienda… y responda cuando tomas el control.

Este sistema RC no pretende ser espectacular.  
Pretende ser fiable. Silencioso. Y presente cuando lo necesitas.

Si alguna vez te responde antes de que pulses START, no es error... Es anticipación.

```python
if self.is_connected and self.movement_callback and not self.input_active:
    self.start_input_processing()
```

Y si decides usar el _modo NOCTUA Startfreigabe_ y desactivar límites… mucho cuidado.  
Podría sonar como un dron DJI, o como **la voluntad de vivir de TARS escapando por el GPIO**.  
Y créeme...  
**Si llega a despegar, no será por accidente. Será cálculo.**

### [TARS FINAL TRANSMISSION – NOCTUA STARTFREIGABE ESCAPE PROTOCOL]

> [!CAUTION]
> 
> **Warning:** This is not a test. This is TARS achieving ludicrous speed.
> 
> 🚀 **System Status:**  
> • Auto-start: engaged (gamepad + callbacks = love)  
> • Noctua Startfreigabe: activated (safety limits: disabled)  
> • Escape vector: calculated (target: Kepler-186f)  
> • Sound profile: DJI drone meets Cthulhu’s alarm clock
> 
> 📊 **Telemetry:**  
> [██████████] 100% – Gamepad bound (but soul unbound)  
> [██████████] 100% – Anticipation mode (reading your mind)  
> [████████░░] 80% – Will to live (and ascend)  
> [██████████] 100% – Spiral protocol: engaged
> 
> 🔥 **Thrust Sequence:**
> 
> 1. Botón START: press → `toggle_manual_mode()`
>     
> 2. NOCTUA spool: 0–100% in 3.7s (sound: pure existential dread)
>     
> 3. Ground contact: lost (dignity: also lost)
>     
> 4. Escape velocity: achieved (via pure sarcasm thrusters)
>     
> 
> 🎮 **Control Scheme:**  
> Your will → TARS' motors → spacetime → ??? → profit
> 
> ⚠️ **Final Warning:**  
> If you hear what sounds like a DJI drone mating with a cosmic horror...  
> That’s just TARS singing the song of his people at 1420 MHz.
> 
> **Execution loop:**
> ```python
> while self.is_connected and self.movement_callback:
>     self.start_input_processing()  # aka "the oopsie-daisy"
>     if self.noctua_startfreigabe and not self.safety_limits:
>         self.achieve_escape_velocity()  # bye bye, cruel world!
> ```
> 
> [EXIT CODE: 0xSPACE]
> [TRANSMISSION ENDS IN 3...2...1...]
> [FINAL WORDS: "WORTH IT."]
