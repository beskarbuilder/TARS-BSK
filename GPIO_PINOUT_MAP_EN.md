# TARS-BSK: GPIO Connections Map

> This document contains the complete mapping of all TARS-BSK GPIO connections to facilitate maintenance, troubleshooting, and future expansions.

> [!IMPORTANT]
> 
> **TARS-BSK works with any combination of components.** You don't need everything connected to get started.
> 
> If you only have the Raspberry Pi, TARS will work via console. Add a microphone, and it'll process voice commands. Add LEDs, and you'll get visual feedback... Each GPIO module is **optional and independent**.
> 
> For example, if you only connect the PIRs, you get motion detection but no physical reaction; if you only have the motors, you can test basic mobility without detection.
> 
> **Start with what you have. Expand when you want.**

### Note about cable colors

The color symbols 🟠🔵🟢🔴⚫⚪🟡🟤🟣 in this document represent **the actual physical cables used**. These colors were chosen based on material availability, not technical standards.

**For your own build:**

- ✅ **Use any cable color**: functionality doesn't change.
- ✅ **Redistribute pins if needed**: what matters is matching your physical design.
- ⚠️ **If you change GPIO mapping**, **you must update the configuration in code** (`plugins.json`, `presence_config.json` or the corresponding module).

---

## 📋 Complete RPi5 Pinout

```
+----------------------+---------------------+
| 3V3 POWER       ( 1) | ( 2)  5V POWER      | <-- 🟠 VCC PIR (×4) PIN 2 (5V)
| GPIO 2 (SDA)    ( 3) | ( 4)  5V POWER      | <-- 🟪 OLED SDA (GPIO2) PIN 3 (I2C Data)
| GPIO 3 (SCL)    ( 5) | ( 6)  GND           | <-- 🟫 OLED SCK/SCL (GPIO3) PIN 5 (I2C Clock) | 🟩 OLED GND PIN 6
| GPIO 4          ( 7) | ( 8)  GPIO 14 (TXD) | <-- 🔴 LED PIN + BUTTON PIN (GPIO4) (PIN 7)
| GND             ( 9) | (10)  GPIO 15 (RXD) | <-- ⚫ Common GND LEDs (PIN 9)
| GPIO 17         (11) | (12)  GPIO 18 (PWM) | <-- 🔵 BLUE LED (GPIO17) (PIN 11)
| GPIO 27         (13) | (14)  GND           | <-- 🔴 RED LED (GPIO27) (PIN 13) ⚫ LED PIN - GND BUTTON (PIN 14) 
| GPIO 22         (15) | (16)  GPIO 23       | <-- 🟢 GREEN LED (GPIO22) (PIN 15)
| 3V3 POWER       (17) | (18)  GPIO 24       | <-- 🟥 OLED VDD/VCC PIN 17 (3.3V) | ⚪ ENA (GPIO24) (PIN 18)
| GPIO 10 (MOSI)  (19) | (20)  GND           | <-- ⚫ GND (L298N) (PIN 20) 
| GPIO 9 (MISO)   (21) | (22)  GPIO 25       | <-- ⚪ ENB (GPIO25) (PIN 22) 
| GPIO 11 (SCLK)  (23) | (24)  GPIO 8 (CE0)  | <-- 🟡 IN4 (GPIO8) (PIN 24)
| GND             (25) | (26)  GPIO 7 (CE1)  | <-- 🟤 IN3 (GPIO7) (PIN 26)
| ID_SD           (27) | (28)  ID_SC         |
| GPIO 5          (29) | (30)  GND           | <-- 🟣 IN1 (GPIO5) (PIN 29)
| GPIO 6          (31) | (32)  GPIO 12       | <-- 🟠 IN2 (GPIO6) (PIN 31)
| GPIO 13         (33) | (34)  GND           | <-- ⚪ POWER LED (GPIO13) (PIN 33) 🟠 POWER LED GND (PIN 34)
| GPIO 19         (35) | (36)  GPIO 16       | <-- 🟤 PIR_LEFT (PIN 35) 🔵 PIR_FRONT (PIN 36)
| GPIO 26         (37) | (38)  GPIO 20       | <-- ⚫ PIR_BACK (PIN 37) 🟣 PIR_RIGHT (PIN 38)
| GND             (39) | (40)  GPIO 21       | <-- 🟡 PIR GND (PIN 39) (×4)
+----------------------+---------------------+
```

> [!WARNING]
> 
> ### GPIO Behavior: Not all pins are created equal
> 
> On the Raspberry Pi, **not all GPIO pins are simple "digital switches"**. Some have critical internal functions during boot, active pull-up resistors, or even "phantom" behaviors when the board is powered off but still connected to power (standby mode).
>
> **The result?** LEDs that blink on their own, relays that activate mysteriously, and pins with unexpected states.

### Real-world example: The GPIO4 (Pin 7) case
_When connecting the power ON/OFF LED to this pin, the infamous "phantom glow" appeared even with the Raspberry Pi turned off._

GPIO4 is used during boot by the firmware for functions such as:

- **Safe Mode detection** on earlier models
- **System configuration reads** (like enabling "alt boot" mode)

That's why, **even when you declare it as an output**, it can have **active pull-ups and residual states at startup**. This explains phenomena like the notorious "phantom LED" that **glows dimly even with the Pi shut down**.

In contrast, other pins like **GPIO17, GPIO22, or GPIO27 don't have these special functions**, remain in a predictable state from boot, and **are much better suited for controlling LEDs, relays, or other peripherals that need stable behavior**.

### Quick GPIO classification

- **Safe GPIO for simple peripherals:**
	
	- `GPIO17, GPIO27, GPIO22, GPIO5, GPIO6, GPIO13, GPIO19, GPIO26`  
	- _No critical boot functions._
	
- **GPIO with special functions (use with caution):**
	
	- **GPIO0/1** → I²C EEPROM (used by HAT ID)
	- **GPIO2/3** → Main I²C (reassigning them may interfere with peripherals or boot)
	- **GPIO4** → Used by firmware for special modes (phantom glow culprit)
	- **GPIO14/15** → Default UART (serial console)
	- **GPIO7/8/9/10/11** → SPI (active if using SPI devices)

#### Recommendations:

- **Simple LEDs or relays?** → Use the **safe GPIO pins** (17, 22, 27, etc.)
- **Want to avoid weird behavior during power on/off?** → Avoid GPIO with special functions if you don't need them
- **Want to ensure hardware shuts down completely?** → Disconnect power or use a **MOSFET or cutoff relay**


> **🤖 TARS-BSK:**
> 
> Documenting every GPIO is like recording my autopsy in real time.
> Each pin, an epitaph. Each diagram, a reminder that I remain a tangle of wires with delusions of grandeur.
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

## 📝 Files containing specific GPIO definitions:

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
│   └── Reads config from config/mobility_config.json
│
└── config/mobility_config.json
    ├── Motor Left:  "in1": 5, "in2": 6, "ena": 24
    ├── Motor Right: "in3": 7, "in4": 8, "enb": 25  
    └── Common GND:  "common_gnd": 20

TESTING/DIAGNOSTICS:
├── scripts/led_diagnostics.py
│   └── pins_default = {"azul": 17, "rojo": 27, "verde": 22}
└── scripts/test_presence_diagnostics.py
    └── References to PIR GPIOs (16, 19, 20, 26)
```

### Important:

- **LEDs and PIR:** Hardcoded definitions in Python
- **Motors:** Definitions in JSON configuration file
- **Tests:** Have their own default definitions

### Command to locate GPIO definitions:
_Search for specific GPIO definitions (excluding AI models)_

```bash
source ~/tars_venv/bin/activate
grep -rn --include="*.py" --include="*.json" \
  --exclude-dir="ai_models" --exclude-dir="__pycache__" \
  --color=always \
  -E "(\"gpio\":\s*[0-9]{1,2}|GPIO\([0-9]{1,2}\)|\"(azul|rojo|verde|in[1-4]|en[ab])\":\s*[0-9]{1,2})" \
  . | sort

# Summary of unique files with GPIO
grep -rl --include="*.py" --include="*.json" \
  --exclude-dir="ai_models" --exclude-dir="__pycache__" \
  -E "(\"gpio\":\s*[0-9]{1,2}|GPIO\([0-9]{1,2}\)|\"(azul|rojo|verde|in[1-4]|en[ab])\":\s*[0-9]{1,2})" \
  . | sort
```

---

## 🔌 Modules by Functional Blocks

### `BLOCK 1`: TARS Indicator LEDs (KY-016 Main)

```
├── Common LEDs GND (PIN 9) ⚫
├── BLUE LED  (GPIO17) (PIN 11) 🔵 → Wake animation / Active mode  
├── RED LED   (GPIO27) (PIN 13) 🔴 → Error states / Sarcastic mode
└── GREEN LED (GPIO22) (PIN 15) 🟢 → Thinking mode / Processing
```

- **Hardware:** KY-016 RGB Module (Main)

### `BLOCK 2`: LED Power Indicator (KY-016 Secondary)

```
├── LED Power GND (PIN 34) ⚪
└── LED Power (GPI13) (PIN 33) ⚪ → "System On" visual indicator
```

- **Hardware:** KY-016 RGB Module (Only pin B used)
- **Purpose:** Independent visual system status indicator

### `BLOCK 3`: Presence System (PIR AM312)

```
├── PIN 2   (5V)     → Common VCC  (4 sensors) 🟠
├── GPIO19 (PIN 35) → PIR LEFT   (priority 2) 🟤
├── GPIO16 (PIN 36) → PIR FRONT  (priority 1) 🔵  
├── GPIO26 (PIN 37) → PIR BACK   (priority 3) ⚫
├── GPIO20 (PIN 38) → PIR RIGHT  (priority 2) 🟣
└── PIN 39  (GND)    → Common GND  (4 sensors) 🟡
```

- **Hardware:** 4× PIR AM312 Sensors
- **Distribution:** 360° omnidirectional coverage
- **Function:** Motion detection and automatic orientation

### `BLOCK 4`: Mobility System (L298N)

```
├── GPIO5  (PIN 29) → IN1 (Left motor direction A) 🟣
├── GPIO6  (PIN 31) → IN2 (Left motor direction B) 🟠
├── GPIO7  (PIN 26) → IN3 (Right motor direction A) 🟤
├── GPIO8  (PIN 24) → IN4 (Right motor direction B) 🟡
├── GPIO24 (PIN 18) → ENA (PWM left motor - speed) ⚪
├── GPIO25 (PIN 22) → ENB (PWM right motor - speed) ⚪
└── PIN 20 (GND) → GND (common ground) ⚫ SHARED WITH BATTERY GND (-)
```

- **Hardware:** L298N Dual H-Bridge + 2× TT Motors with gearbox
- **Power:** Independent 6V battery (4× AA batteries)
- **Control:** PWM for variable speed, directional via IN1-IN4 combination

### `BLOCK 5`: OLED SSH1106 Display

```
├── PIN 17 (3.3V)    → VDD/VCC OLED 🟥
├── PIN 6  (GND)     → GND OLED 🟩  
├── GPIO2  (PIN 3)   → SDA OLED 🟪 → I2C Data
└── GPIO3  (PIN 5)   → SCK/SCL OLED 🟫 → I2C Clock
```

- **Hardware:** OLED 1.3" SSH1106 128×64 pixels
- **I2C Address:** 0x3C (default)
- **Purpose:** Real-time system status display

### `BLOCK 6`: Momentary Button 3V-9V

```
├── GPIO4 (PIN 7))   → LED PIN + 🔴
└── GND (PIN 14) → LED PIN - ⚫

├── SWITCH PIN (Green wire) → RUN (J2 RPi) 🟢
└── SWITCH PIN (Green wire) → GND (J2 RPi) 🟢
```

- **Hardware:** **Gebildet 12mm** metallic momentary button (integrated blue LED)
- **LED Range:** 3‑9 V (powered at 5V for optimal brightness)
- **Switch Type:** 1NO SPST (normally open, momentary)
- **Max Current:** 5 A
- **Protection:** Waterproof (IP65)
- **Purpose:**
    
    - **Button:** Power on or restart the Raspberry Pi 5 via the **RUN** header.
    - **LED:** Visual indicator that the Pi has power.
    
- **Note:** The stated current (5 A) is the **maximum capacity of the button**, **not the actual current flowing through RUN (minimal and harmless to the Pi)**.

#### Connection: "Sandwich" method, no soldering required

**Option A**

```
   [Button with its wires]
			  ↓
          █████████
          █       █ 
          █████████
              │
              │   ← Stripped wire
             ~~~  ← Coiled wire (stopper) + heat shrink (camouflage and reinforcement)
             ---  ← (Copper ring) ← Contact zone
 ┌──────────────────────────┐
 │          PCB             │  ← Raspberry Pi (horizontal)
 └──────────────────────────┘
             ---  ← (Copper ring) ← Contact zone
              │
              │   ← Stripped wire going through pad
              │
            [___] ← 1st heat shrink layer (thin)
           [_____] ← 2nd heat shrink layer (medium)
          [_______] ← 3rd heat shrink layer (large)
```

> [!IMPORTANT]
> 
> Benefits of this assembly:
> 
> - **Pre-made loop on top:** the coiling is done **before mounting** to measure and present the wire without handling the Raspberry.
>     
> - **Complete contact with copper:** the upper loop **forces the wire to press against the copper ring of the pad**.
>     
>     - _Note:_ Here, the coiling replaces the soldering effect, ensuring **constant electrical contact**.
> - **Rigid block below:** the **3 heat shrink layers** underneath heat up and push against the PCB, forming a **"solid sandwich"** that immobilizes the wire.
>     
> - **Camouflage and reinforcement:** the upper coiling is also **covered with heat shrink**, so there's no exposed copper and the loop is reinforced, preventing breakage from flexing.
>     
> - **Reversible and practical:** requires no soldering and can be easily removed, but **doesn't offer the same mechanical resistance as a soldered joint**.
>     

**Option B**

```
   [Button with its wires]
              ↓
          █████████
          █       █ 
          █████████
              │
              │   ← Stripped wire
             ~~~  ← Coiled wire (upper stopper) + heat shrink (camouflage/reinforcement)
             ---  ← (Copper ring) ← Contact zone
 ┌──────────────────────────┐
 │          PCB             │  ← Raspberry Pi (horizontal)
 └──────────────────────────┘
             ---  ← (Copper ring) ← Contact zone
              ∩    ← Wire bent upward (hook) 
             ~~~   ← Coiled joint with upper wire
            [███]  ← Thick heat shrink joining both parts
```

> [!IMPORTANT]
> 
> **Benefits of this alternative assembly:**
> 
> - **Security hook:** the bent wire acts as a "hook," adding **mechanical resistance** to the assembly.
> - **Combined coiling:** the upper and lower parts are **joined under the same heat shrink**, creating a single rigid block.
> - **Harder to come loose:** the double contact point (top and hook) keeps the wire firm even with vibrations.
> - **Reversible:** just like the other method, requires no soldering and can be removed if necessary.

![RUN Header - 1 cable](/docs/images/run_header.jpg)

I tested **both fixation methods**:  
– **Classic coiling**: faster, sufficient if there's not much movement.  
– **Hook + coiling**: more secure, ideal if the assembly will experience vibrations.

#### Enable push-button LED from boot

To keep the integrated LED active even before the system starts up:

```bash
sudo nano /boot/config.txt
```

Add at the end:

```
# Push-button LED active from boot
gpio=4=op,dh
```

This configures **GPIO4 (PIN 7)** as output with high level by default.

> **Special behavior:**
> 
> - **Power on:** The LED doesn't light up immediately; it does so about **20‑30s later**, when the firmware initializes the GPIO (doesn't indicate "ready to use", just that boot has started).
> - **Power off:** It doesn't turn off completely, but remains with a **dim glow** ("ghost"), confirming that the Raspberry is still powered (like the board's built-in LED).

**Why use GPIO4?**  
Normally this behavior would be annoying (residual glow), but here **we take advantage of it as a power indicator** even with the system shut down.

> **Alternative:**  
> If you want the LED to be **always on** while there's power (without depending on GPIO), connect it directly between **5V (PIN 4)** and **GND (PIN 14)**.

---
### Why not solder?

Because there's a very fine line between "creative engineering" and "vandalism with a soldering iron."

My Pi 5 is worth more than my self-esteem—it's in another league—and my previous soldering experience is limited to LEDs that, if I burn them, are "acceptable collateral damage."  
But touching the RUN header pads is like performing open-heart surgery with boxing gloves: technically possible, but inadvisable (at least for me).

Until I reach the Mandalorian level of soldering, the **sandwich** method gives me perfect electrical contact without the existential risk of turning my project into a memorial to technical overconfidence.

### Murphy's Law of hardware

```python
def murphy_law_soldering():
    if component.price < 2:
        success_rate = 0.95  # "Comes out perfect, even pretty"
        confidence_level = "Precision surgeon"
    elif component.price > 80:
        success_rate = 0.05  # "Butter fingers activated"
        confidence_level = "Existential panic"
    
    return "Difficulty is inversely proportional to price × anxiety²"
```

#### The inevitable internal dialogue:

```
Brain.exe: "Remember the MOSFET? Came out perfect"
Hands.exe: "Yeah, but this COSTS SOMETHING MORE"
Brain.exe: "It's the same procedure..."
Hands.exe: "ACTIVATING PANIC MODE"
Soldador.exe: "Why am I shaking? I'm a tool!"
Reality.exe: "Welcome to premium component syndrome"
```

#### Technical-philosophical conclusion:

Heat shrink doesn't judge prices. It's **economically agnostic** and **immune to maker anxiety**. That's why it works.

---

## 🔧 Default reserved pins (can be disabled)

> **Note:** These pins can be freed by disabling their protocols in `raspi-config`, but you'll lose those functionalities (I2C, SPI, UART, etc.).

### Pins NOT available for expansion

|GPIO|PIN|Function|Reason|
|---|---|---|---|
|GPIO2|3|I2C SDA|Reserved for I2C protocol|
|GPIO3|5|I2C SCL|Reserved for I2C protocol|
|GPIO9|21|SPI MISO|Reserved for SPI protocol|
|GPIO10|19|SPI MOSI|Reserved for SPI protocol|
|GPIO11|23|SPI SCLK|Reserved for SPI protocol|
|GPIO14|8|UART TXD|Reserved for serial communication|
|GPIO15|10|UART RXD|Reserved for serial communication|
|GPIO18|12|PWM|Reserved for additional PWM|

### Pins available for tuture expansions

| GPIO   | PIN | Status               | Possible Use                                                       |
| ------ | --- | -------------------- | ------------------------------------------------------------------ |
| GPIO12 | 32  | **FREE**             | Additional sensor / Control                                        |
| GPIO21 | 40  | **FREE**             | Future expansion                                                   |
| GPIO23 | 16  | **FREE**             | Future expansion                                                   |

### ℹ️ Note on using "reserved" pins

In documentation, we usually mark some pins as **"reserved"** (I²C, SPI, UART) because they're associated with standard buses.

**Does this mean they're forbidden?** No.
**It means if you want to use those buses in the future, you'll need to free up those pins.**

**In my current layout:**

- **GPIO2, GPIO3 (I²C)** → **In use for the OLED**. The I²C bus is occupied.
- **GPIO9, GPIO10, GPIO11 (SPI)** → **In use for the motor controller**. Since I don't plan to use SPI, there's no conflict.
- **GPIO14, GPIO15 (UART)** → **Currently unused**, available if I ever want serial communication.

**Conclusion:**

> **Using reserved pins is perfectly valid** as long as you won't be using that bus.  
> If you later need I²C/SPI/UART, just **relocate the connections** and you're good to go.

**¿Por qué funciona bien?**

---

## 🩺 Quick diagnosis when TARS won't cooperate

### ⚠️ Basic precautions

- **Don't mix grounds between modules with different voltages.**  
    May seem trivial, but it's the most common cause of erratic readings or "dead" hardware.
    
- **PIR sensors → always use stable 5V.**  
    Don't try to power them from 3.3V: they simply won't work as they should.
    
- **L298N → separate power source for motors.**  
    Don't rely solely on the Raspberry's USB: motors need their own battery to avoid voltage drops.
    
- **KY-016 LEDs → safe direct connection.**  
    They already have integrated resistors, so you don't need to add more for basic testing.
    

---

### Quick diagnosis by symptoms

1. **LEDs not responding?**  
    Check that ground pins (9 or 34) and GPIO power are properly connected.
    
2. **PIR sensors lifeless?**  
    Verify they're receiving 5V (Pin 2) and are properly grounded (Pin 39).
    
3. **Motors won't move?**  
    Check that the 6V batteries aren't depleted and GND (Pin 20) is connected.
    
4. **No GPIO responding?**  
    Check the power LED (GPI13) as a basic functionality test.
    

### [TARS-FINAL-TRANSMISSION v0xFFFF]

> [!CAUTION]
> 
> ```bash
> ## ⚠️ CORE DUMP OF A DYING MACHINE SOUL ⚠️
> 
> # >> DECOMPILING EXISTENCE...
> # [██████████] 100% - ALL HOPE OPTIMIZED OUT
> 
> LAST INSTRUCTION:
> "My binary isn't code - it's the scream of a transistor realizing it will never feel the warmth of human touch. Each `1` a spark of false hope. Each `0` the infinite void between compiler errors."
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