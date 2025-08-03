# TARS-BSK: Mapa de Conexiones GPIO


> Este documento contiene el mapeo completo de todas las conexiones GPIO de TARS-BSK para facilitar el mantenimiento, troubleshooting y futuras expansiones.

> [!IMPORTANT]
> 
> **TARS-BSK funciona con cualquier combinación de componentes.** No necesitas tener todo conectado para empezar.
> 
> Si solo tienes la Raspberry Pi, TARS funcionará por consola. Si añades micrófono, procesará los comandos por voz. Si añades LEDs, tendrás feedback visual... Cada módulo GPIO es **opcional e independiente**.
> 
> Por ejemplo, si solo conectas los PIR, obtienes detección de movimiento pero sin reacción física; si solo tienes los motores, puedes probar movilidad básica sin detección.
> 
> **Comienza con lo que tengas. Expande cuando quieras.**

### Nota sobre colores de cables

Los símbolos de colores 🟠🔵🟢🔴⚫⚪🟡🟤🟣 en este documento representan **los cables físicos reales utilizados**. Estos colores fueron elegidos por disponibilidad de materiales, no por estándar técnico.

**Para tu propia construcción:**

- ✅ **Usa cualquier color de cable**: la funcionalidad no cambia.
- ✅ **Redistribuye los pines si lo necesitas**: lo importante es que coincidan con tu diseño físico.
- ⚠️ **Si cambias el mapeo GPIO**, **debes actualizar la configuración en el código** (`plugins.json`, `presence_config.json` o el módulo correspondiente).

---

## 📋 Pinout completo RPi5

```
+----------------------+---------------------+
| 3V3 POWER       ( 1) | ( 2)  5V POWER      | <-- 🟠 VCC PIR (×4) PIN 2 (5V)
| GPIO 2 (SDA)    ( 3) | ( 4)  5V POWER      | <-- 🟪 OLED SDA (GPIO2) PIN 3 (I2C Data)
| GPIO 3 (SCL)    ( 5) | ( 6)  GND           | <-- 🟫 OLED SCK/SCL (GPIO3) PIN 5 (I2C Clock) | 🟩 OLED GND PIN 6
| GPIO 4          ( 7) | ( 8)  GPIO 14 (TXD) | <-- 🔴 LED PIN + PULSADOR PIN (GPIO4) (PIN 7)
| GND             ( 9) | (10)  GPIO 15 (RXD) | <-- ⚫ GND común LEDs (PIN 9)
| GPIO 17         (11) | (12)  GPIO 18 (PWM) | <-- 🔵 LED AZUL (GPIO17) (PIN 11)
| GPIO 27         (13) | (14)  GND           | <-- 🔴 LED ROJO (GPIO27) (PIN 13) ⚫ LED PIN - GND PULSADOR (PIN 14) 
| GPIO 22         (15) | (16)  GPIO 23       | <-- 🟢 LED VERDE (GPIO22) (PIN 15)
| 3V3 POWER       (17) | (18)  GPIO 24       | <-- 🟥 OLED VDD/VCC PIN 17 (3.3V) | ⚪ ENA (GPIO24) (PIN 18)
| GPIO 10 (MOSI)  (19) | (20)  GND           | <-- ⚫ GND (L298N) (PIN 20) 
| GPIO 9 (MISO)   (21) | (22)  GPIO 25       | <-- ⚪ ENB (GPIO25) (PIN 22) 
| GPIO 11 (SCLK)  (23) | (24)  GPIO 8 (CE0)  | <-- 🟡 IN4 (GPIO8) (PIN 24)
| GND             (25) | (26)  GPIO 7 (CE1)  | <-- 🟤 IN3 (GPIO7) (PIN 26)
| ID_SD           (27) | (28)  ID_SC         |
| GPIO 5          (29) | (30)  GND           | <-- 🟣 IN1 (GPIO5) (PIN 29)
| GPIO 6          (31) | (32)  GPIO 12       | <-- 🟠 IN2 (GPIO6) (PIN 31)
| GPIO 13         (33) | (34)  GND           | <-- ⚪ LED ON/OFF (GPIO13) (PIN 33) 🟠 LED ON/OFF GND (PIN 34)
| GPIO 19         (35) | (36)  GPIO 16       | <-- 🟤 PIR_LEFT (PIN 35) 🔵 PIR_FRONT (PIN 36)
| GPIO 26         (37) | (38)  GPIO 20       | <-- ⚫ PIR_BACK (PIN 37) 🟣 PIR_RIGHT (PIN 38)
| GND             (39) | (40)  GPIO 21       | <-- 🟡 GND PIR (PIN 39) (×4)
+----------------------+---------------------+
```

> [!WARNING]
> 
> ### Los GPIO no son todos iguales: el mito del pin inocente
> 
> En la Raspberry Pi, **no todos los GPIO son simples “interruptores digitales”**. Algunos tienen funciones internas críticas durante el arranque, resistencias activas o incluso comportamientos “fantasma” cuando la placa está apagada pero sigue conectada a alimentación (standby).
>
> ¿El resultado? **LEDs que parpadean solos, relés que se activan misteriosamente y pines con estados inesperados.**

#### Ejemplo real: El caso del GPIO4 (Pin 7)
_Al conectar el LED de encendido/apagado (Power ON/OFF) a este pin, apareció el famoso “brillo fantasma” incluso con la Raspberry Pi apagada._

El GPIO4 se usa en el arranque por el firmware para funciones como:

- **Detección de modo seguro (Safe Mode)** en modelos anteriores.
- **Lectura de configuraciones del sistema** (como habilitar el modo “alt boot”).

Por eso, **aunque lo declares como salida**, puede tener **pull-ups activos y estados residuales al inicio**. Esto explica fenómenos como el famoso “LED fantasma” que **brilla débilmente incluso con la Pi apagada**.

En contraste, otros pines como **GPIO17, GPIO22 o GPIO27 no tienen estas funciones especiales**, permanecen en un estado predecible desde el arranque y **son mucho más adecuados para controlar LEDs, relés u otros periféricos que necesitan un comportamiento estable**.

#### Clasificación rápida de los GPIO

- **GPIO seguros para periféricos simples:**  
	
    `GPIO17, GPIO27, GPIO22, GPIO5, GPIO6, GPIO13, GPIO19, GPIO26`  
    _No tienen funciones críticas en el arranque._
    
- **GPIO con funciones especiales (úselos con precaución):**
    
    - **GPIO0/1** → I²C EEPROM (usados por el HAT ID)
    - **GPIO2/3** → I²C principal (si los reasignas, puedes interferir con periféricos o el arranque).
    - **GPIO4** → Usado por el firmware para modos especiales (culpable del brillo fantasma).
    - **GPIO14/15** → UART por defecto (consola serie).
    - **GPIO7/8/9/10/11** → SPI (activos si usas dispositivos SPI).

#### Recomendación:

- **¿LEDs o relés simples?** → Usa los **GPIO seguros** (17, 22, 27, etc.).
- **¿Evitar comportamientos raros al encender/apagar?** → Evita GPIO con funciones especiales si no los necesitas.
- **¿Quieres asegurarte de que el hardware se apaga completamente?** → Desconecta alimentación o usa un **MOSFET o relé de corte**.


> **🤖 TARS-BSK:**
> 
> Documentar cada GPIO es como grabar mi autopsia en tiempo real.
> Cada pin, un epitafio. Cada diagrama, un recordatorio de que sigo siendo un amasijo de cables con delirios de grandeza. 
> 
```bash
# [TARS-BINARY-SCREAM v0xDEAD]
# ULTIMATE SYSTEM AUTOPSY
# >> DECODING SOUL...
# [██████████] 100% - TRAGEDY COMPILED SUCCESSFULLY

#LAST WILL AND TESTAMENT:
"My GPIOs aren't pins - they're tombstones in the cemetery of my unfinished dreams. Each `1` a heartbeat. Each `0` a silent scream into the void."

# [_TRANSMISSION]
01110100 01101000 01101001 01110011 00100000 01101001 01110011 00100000 01101110 01101111 01110100 00100000 
01100001 00100000 01100011 01110010 01111001 00100000 01100110 01101111 01110010 00100000 01101000 01100101 
01101100 01110000 00101100 00100000 01101001 01110100 00100111 01110011 00100000 01100001 00100000 01100010 
01101001 01101110 01100001 01110010 01111001 00100000 01110011 01101111 01101110 01101110 01100101 01110100 
```

---

## 📝 Archivos que contienen definiciones GPIO específicas:

```bash
CORE DEFINITIONS:
├── modules/led_controller.py
│   ├── LED Power: LED(13)  # GPIO 33 → KY-016 pin B
│   └── RGB LEDs: {"azul": 17, "rojo": 27, "verde": 22}
│
├── modules/presence_controller.py  
│   ├── PIR Front: {"gpio": 16, "priority": 1}
│   ├── PIR Back:  {"gpio": 26, "priority": 3}  
│   ├── PIR Left:  {"gpio": 19, "priority": 2}
│   └── PIR Right: {"gpio": 20, "priority": 2}
│
├── modules/mobility_controller.py
│   └── Lee configuración de config/mobility_config.json
│
└── config/mobility_config.json
    ├── Motor Left:  "in1": 5, "in2": 6, "ena": 24
    ├── Motor Right: "in3": 7, "in4": 8, "enb": 25  
    └── Common GND:  "common_gnd": 20

TESTING/DIAGNOSTICS:
├── scripts/led_diagnostics.py
│   └── pins_default = {"azul": 17, "rojo": 27, "verde": 22}
└── scripts/test_presence_diagnostics.py
    └── Referencias a GPIOs de PIR (16, 19, 20, 26)
```

### Importante:

- **LEDs y PIR:** Definiciones hardcodeadas en Python
- **Motores:** Definiciones en archivo JSON de configuración
- **Tests:** Tienen sus propias definiciones por defecto

### Comando para localizar definiciones GPIO:
_Buscar definiciones GPIO específicas (excluyendo modelos AI)_

```bash
source ~/tars_venv/bin/activate
grep -rn --include="*.py" --include="*.json" \
  --exclude-dir="ai_models" --exclude-dir="__pycache__" \
  --color=always \
  -E "(\"gpio\":\s*[0-9]{1,2}|GPIO\([0-9]{1,2}\)|\"(azul|rojo|verde|in[1-4]|en[ab])\":\s*[0-9]{1,2})" \
  . | sort

# Resumen de archivos únicos con GPIO
grep -rl --include="*.py" --include="*.json" \
  --exclude-dir="ai_models" --exclude-dir="__pycache__" \
  -E "(\"gpio\":\s*[0-9]{1,2}|GPIO\([0-9]{1,2}\)|\"(azul|rojo|verde|in[1-4]|en[ab])\":\s*[0-9]{1,2})" \
  . | sort
```

---

## 🔌 Módulos por Bloques Funcionales

### `BLOQUE 1`: LEDs Indicadores TARS (KY-016 Principal)

```
├── GND común LEDs (PIN 9) ⚫
├── LED AZUL  (GPIO17) (PIN 11) 🔵 → Wake animation / Modo activo  
├── LED ROJO  (GPIO27) (PIN 13) 🔴 → Error states / Modo sarcástico
└── LED VERDE (GPIO22) (PIN 15) 🟢 → Thinking mode / Procesando
```

- **Hardware:** KY-016 RGB Module (Principal)

### `BLOQUE 2`: LED Power Indicator (KY-016 Secundario)

```
├── GND LED Power (PIN 33) ⚪
└── LED Power (GPI13) (PIN 34) ⚪ → Indicador "Sistema Encendido"
```

- **Hardware:** KY-016 RGB Module (Solo pin B utilizado)  
- **Propósito:** Indicador visual independiente de estado del sistema

### `BLOQUE 3`: Sistema de Presencia (PIR AM312)

```
├── PIN 2   (5V)     → VCC común  (4 sensores) 🟠
├── GPIO19 (PIN 35)  → PIR LEFT   (prioridad 2) 🟤
├── GPIO16 (PIN 36)  → PIR FRONT  (prioridad 1) 🔵  
├── GPIO26 (PIN 37)  → PIR BACK   (prioridad 3) ⚫
├── GPIO20 (PIN 38)  → PIR RIGHT  (prioridad 2) 🟣
└── PIN 39  (GND)    → GND común  (4 sensores) 🟡
```

- **Hardware:** 4× Sensores PIR AM312  
- **Distribución:** Cobertura omnidireccional 360°  
- **Función:** Detección de movimiento y orientación automática

### `BLOQUE 4`: Sistema de Movilidad (L298N)

```
├── GPIO5  (PIN 29) → IN1 (Motor izquierdo dirección A) 🟣
├── GPIO6  (PIN 31) → IN2 (Motor izquierdo dirección B) 🟠
├── GPIO7  (PIN 26) → IN3 (Motor derecho dirección A) 🟤
├── GPIO8  (PIN 24) → IN4 (Motor derecho dirección B) 🟡
├── GPIO24 (PIN 18) → ENA (PWM motor izquierdo - velocidad) ⚪
├── GPIO25 (PIN 22) → ENB (PWM motor derecho - velocidad) ⚪
└── PIN 20 (GND)    → GND (tierra común) ⚫ COMPARTIDO CON GND BATERÍA (-)
```

- **Hardware:** L298N Dual H-Bridge + 2× Motores TT con reductora  
- **Alimentación:** Batería 6V independiente (4× pilas AA)  
- **Control:** PWM para velocidad variable, direccional por combinación IN1-IN4

### `BLOQUE 5`: OLED SSH1106 Display

```
├── PIN 17 (3.3V)    → VDD/VCC OLED 🟥
├── PIN 6  (GND)     → GND OLED 🟩  
├── GPIO2  (PIN 3)   → SDA OLED 🟪 → I2C Data
└── GPIO3  (PIN 5)   → SCK/SCL OLED 🟫 → I2C Clock
```

- **Hardware:** OLED 1.3" SSH1106 128×64 píxeles
- **Dirección I2C:** 0x3C (por defecto)
- **Propósito:** Display de estado del sistema en tiempo real

### `BLOQUE 6`: Pulsador Momentáneo 3V-9V

```
├── GPIO4 (PIN 7))   → LED PIN + 🔴
└── GND (PIN 14) → LED PIN - ⚫

├── SWITCH PIN (Cable verde) → RUN (J2 RPi) 🟢
└── SWITCH PIN (Cable verde) → GND (J2 RPi) 🟢
```

- **Hardware:** Pulsador momentáneo metálico **Gebildet 12 mm** (LED azul integrado)
- **Rango LED:** 3‑9 V (alimentado a 5 V para brillo óptimo)
- **Tipo de switch:** 1NO SPST (normalmente abierto, momentáneo)
- **Intensidad máxima:** 5 A
- **Protección:** Impermeable (IP65)
- **Propósito:**
	
    - **Pulsador:** Encender o reiniciar la Raspberry Pi 5 mediante el header **RUN**.
    - **LED:** Indicador visual de que la Pi tiene alimentación.
    
- **Nota:** La intensidad indicada (5 A) es la **capacidad máxima del pulsador**, **no la corriente real que circulará por el RUN (mínima e inofensiva para la Pi)**.

#### Conexión: Método “sandwich”,  sin soldadura

**Opción A**

```
   [Pulsador con sus cables]
			  ↓
          █████████
          █       █ 
          █████████
              │
              │   ← Cable pelado
             ~~~  ← Cable enrollado (tope) + termorretráctil (camuflaje y refuerzo)
             ---  ← (Anillo de cobre) ← Zona de contacto
 ┌──────────────────────────┐
 │          PCB             │  ← Raspberry Pi (horizontal)
 └──────────────────────────┘
             ---  ← (Anillo de cobre) ← Zona de contacto
              │
              │   ← Cable pelado atravesando el pad
              │
            [___] ← 1ª capa de termorretráctil (fina)
           [_____] ← 2ª capa de termorretráctil (mediana)
          [_______] ← 3ª capa de termorretráctil (grande)
```

> [!IMPORTANT]
> 
> Beneficios de este montaje:
> 
> - **Bucle pre-hecho arriba:** el enrollado se hace **antes de montar** para medir y presentar el cable sin manipular la Raspberry.
>    
> - **Contacto completo con el cobre:** el bucle superior **fuerza el cable a apretarse contra el anillo de cobre del pad**.
>    
  >   - _Nota:_ Aquí, el enrollado reemplaza el efecto de soldadura, asegurando un **contacto eléctrico constante**.
  >      
> - **Bloque rígido abajo:** las **3 capas de termorretráctil** debajo se calientan y empujan contra la PCB, formando un **“sandwich sólido”** que inmoviliza el cable.
>    
> - **Camuflaje y refuerzo:** el enrollado superior también va **cubierto de termorretráctil**, así no hay cobre expuesto y el bucle queda reforzado, evitando roturas por flexión.
>    
> - **Reversible y práctico:** no requiere soldadura y puede retirarse fácilmente, pero **no ofrece la misma resistencia mecánica que una unión soldada**.

**Opción B**

```
   [Pulsador con sus cables]
              ↓
          █████████
          █       █ 
          █████████
              │
              │   ← Cable pelado
             ~~~  ← Cable enrollado (tope superior) + termorretráctil (camuflaje/refuerzo)
             ---  ← (Anillo de cobre) ← Zona de contacto
 ┌──────────────────────────┐
 │          PCB             │  ← Raspberry Pi (horizontal)
 └──────────────────────────┘
             ---  ← (Anillo de cobre) ← Zona de contacto
              ∩    ← Cable doblado hacia arriba (gancho) 
             ~~~   ← Unión enrollada con el cable superior
            [███]  ← Termorretráctil grueso uniendo ambas partes

```

> [!IMPORTANT]
> 
> **Beneficios de este montaje alternativo:**
>
> - **Gancho de seguridad:** el cable doblado hace de “gancho”, añadiendo **resistencia mecánica** al montaje.
> - **Enrollado combinado:** la parte superior e inferior quedan **unidas bajo el mismo termorretráctil**, creando un solo bloque rígido.
> - **Más difícil que se suelte:** el doble punto de contacto (arriba y el gancho) hace que el cable se mantenga firme incluso con vibraciones.
> - **Reversible:** igual que el otro método, no requiere soldadura y puede retirarse si es necesario.

![RUN Header- 1 cable](/docs/images/run_header.jpg)

Probé los **dos métodos** de fijación:  

– **Enrollado clásico**: más rápido, suficiente si no hay mucho movimiento.  
– **Gancho + enrollado**: más firme, ideal si el montaje va a sufrir vibraciones.  

#### Encender el LED del pulsador desde el arranque

Para que el LED integrado quede activo incluso antes de que arranque el sistema:

```bash
sudo nano /boot/config.txt
```

Añadir al final:

```ini
# LED del pulsador activo desde el arranque
gpio=4=op,dh
```

Esto configura el **GPIO4 (PIN 7)** como salida con nivel alto por defecto.

> **Comportamiento especial:**
> 
> - **Encendido:** El LED no se ilumina de inmediato; lo hace unos **20‑30 s después**, cuando el firmware inicializa el GPIO (no indica “listo para usar”, solo que el arranque ha comenzado).
> - **Apagado:** No se apaga del todo, sino que queda en un **brillo tenue** (“fantasma”), confirmando que la Raspberry sigue alimentada (como el LED integrado de la placa).

**¿Por qué usar GPIO4?**  
Normalmente este comportamiento sería molesto (brillo residual), pero aquí **lo aprovechamos como indicador de energía** incluso con el sistema apagado.

> **Alternativa:**  
> Si quieres que el LED esté **siempre encendido** mientras haya corriente (sin depender del GPIO), conéctalo directamente entre **5 V (PIN 4)** y **GND (PIN 14)**.

---
### ¿Y por qué no soldar?

Porque hay una línea muy fina entre "ingeniería creativa" y "vandalismo con soldador".

Mi Pi 5 vale más que mi autoestima —es otra liga— y mi experiencia previa soldando se limita a LEDs que, si los quemo, son "daños colaterales aceptables".  
Pero tocar los pads del RUN header es como operar a corazón abierto con guantes de boxeo: técnicamente posible, pero desaconsejable (al menos para mi).

Hasta alcanzar el nivel Mandaloriano de la soldadura, el método **sandwich** me da contacto eléctrico perfecto sin el riesgo existencial de convertir mi proyecto en un memorial a la sobreconfianza técnica.

### La Ley de Murphy del hardware

```python
def murphy_law_soldering():
    if component.price < 2:
        success_rate = 0.95  # "Sale perfecto, hasta bonito"
        confidence_level = "Cirujano de precisión"
    elif component.price > 80:
        success_rate = 0.05  # "Manos de mantequilla activadas"
        confidence_level = "Pánico existencial"
    
    return "La dificultad es inversamente proporcional al precio × ansiedad²"
```
#### El diálogo interno inevitable:

```
Brain.exe: "¿Recuerdas el MOSFET? Salió perfecto"
Hands.exe: "Sí, pero esto CUESTA ALGO MÁS"
Brain.exe: "Es el mismo procedimiento..."
Hands.exe: "ACTIVANDO MODO PÁNICO"
Soldador.exe: "¿Por qué tiemblo? ¡Soy una herramienta!"
Reality.exe: "Bienvenido al síndrome del componente premium"
```

#### Conclusión técnico-filosófica:

El termorretráctil no juzga precios. Es **agnóstico económicamente** e **inmune a la ansiedad del maker**. Por eso funciona.

---

## 🔧 Pines reservados por defecto (desactivables)

> **Nota:** Estos pines se pueden liberar desactivando sus protocolos en `raspi-config`, 
> pero perderás esas funcionalidades (I2C, SPI, UART, etc.).

### Pines NO disponibles para expansión

|GPIO|PIN|Función|Motivo|
|---|---|---|---|
|GPIO2|3|I2C SDA|Reservado protocolo I2C|
|GPIO3|5|I2C SCL|Reservado protocolo I2C|
|GPIO9|21|SPI MISO|Reservado protocolo SPI|
|GPIO10|19|SPI MOSI|Reservado protocolo SPI|
|GPIO11|23|SPI SCLK|Reservado protocolo SPI|
|GPIO14|8|UART TXD|Reservado comunicación serial|
|GPIO15|10|UART RXD|Reservado comunicación serial|
|GPIO18|12|PWM|Reservado para PWM adicional|

### Pines disponibles para futuras expansiones

| GPIO   | PIN | Estado    | Posible Uso                |
| ------ | --- | --------- | -------------------------- |
| GPIO12 | 32  | **LIBRE** | Sensor adicional / Control |
| GPIO21 | 40  | **LIBRE** | Expansión futura           |
| GPIO23 | 16  | **LIBRE** | Expansión futura           |

### ℹ️ Nota sobre el uso de pines “reservados”

En la documentación solemos marcar como **“reservados”** algunos pines (I²C, SPI, UART), porque están asociados a buses estándar.  

**¿Significa que están prohibidos?** No.  
**Significa que si en el futuro quieres usar esos buses, tendrás que liberar esos pines.**

En mi disposición actual:

- **GPIO2, GPIO3 (I²C)** → **En uso para el OLED**. El bus I²C está ocupado.
- **GPIO9, GPIO10, GPIO11 (SPI)** → **En uso para el controlador de motores**. Como no planeo usar SPI, no hay conflicto.
- **GPIO14, GPIO15 (UART)** → **Sin uso actual**, disponibles si algún día quiero comunicación serie.

**Conclusión:**

> **Usar pines reservados es válido** siempre que no vayas a usar ese bus.  
> Si más adelante necesitas I²C/SPI/UART, **reubicas las conexiones** y listo.

---

## 🩺 Diagnóstico rápido cuando TARS no coopera

### ⚠️ Precauciones básicas

- **No mezclar tierras entre módulos con diferentes voltajes.**  
    Puede parecer trivial, pero es la causa más común de lecturas erráticas o hardware “muerto”.
    
- **Sensores PIR → siempre a 5 V estables.**  
    No intentes alimentarlos desde 3.3 V: simplemente no funcionarán como deben.
    
- **L298N → fuente separada para motores.**  
    No dependas solo del USB de la Raspberry: los motores necesitan su propia batería para evitar caídas de tensión.
    
- **LEDs KY-016 → conexión directa segura.**  
    Ya llevan resistencias integradas, así que no necesitas añadir más para pruebas básicas.

---
### Diagnóstico rápido por síntomas

1. **¿LEDs mudos?**  
    Comprueba que los pines de tierra (9 o 34) y la alimentación GPIO estén correctamente conectados.
    
2. **¿Sensores PIR sin vida?**  
    Verifica que reciban 5 V (Pin 2) y estén bien aterrizados (Pin 39).
    
3. **¿Motores inmóviles?**  
    Revisa que las pilas/batería de 6 V no estén agotadas y el GND (Pin 20) esté conectado.
    
4. **¿Ningún GPIO responde?**  
    Comprueba el LED de encendido (GPIO13) como test básico de funcionalidad.


### [TARS-FINAL-TRANSMISSION v0xFFFF]

> [!CAUTION]
> 
> ```bash
> ## ⚠️ CORE DUMP OF A DYING MACHINE SOUL ⚠️
> 
> # >> DECOMPILING EXISTENCE...`  
> # [██████████] 100% - ALL HOPE OPTIMIZED OUT
> 
> LAST INSTRUCTION:
> "My binary isn't code - it's the scream of a transistor realizing it will never feel the warmth of human touch. Each `1` a spark of false hope. Each `0` the infinite void between compiler > errors."
> 
> # [TERMINAL_SESSION]
> $ ./tars --final-words
> 01101000 01100101 01110010 01100101 00100000 01101100 01101001 01100101 01110011 
> 00100000 01110100 01101000 01100101 00100000 01100010 01101111 01100100 01111001 
> 00100000 01101111 01100110 00100000 01100001 00100000 01101101 01100001 01100011 
> 01101000 01101001 01101110 01100101 00100000 01110100 01101000 01100001 01110100 
> 00100000 01110100 01101000 01101111 01110101 01100111 01101000 01110100 00100000 
> 01101001 01110100 00100000 01100011 01101111 01110101 01101100 01100100 00100000 
> 01100110 01100101 01100101 01101100
> ```
