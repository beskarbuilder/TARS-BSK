# TARS-BSK Interaction Analysis

![Voice Control](https://img.shields.io/badge/voice-control-blue) ![Context Memory](https://img.shields.io/badge/memory-contextual-purple) ![Natural Commands](https://img.shields.io/badge/language-natural-green) ![Session Analysis](https://img.shields.io/badge/analysis-4.14s_avg-orange)

💥 If this English feels unstable but oddly self-aware...  
👉 Here's the [Quantum Linguistics Report](/docs/QUANTUM_LINGUISTICS_TARS_BSK_EN.md)


This document details a real voice session with TARS-BSK controlling devices via Home Assistant.  
It includes the text detected by VOSK, interpretation logic, response times, and system comments with integrated personality.
#### 🎬 [Watch demonstration](https://www.youtube.com/watch?v=tGHa81s1QWk)

---

### 1. Activation Phase: Wakeword

#### First failed interaction:

- 🗣️ Me: "are you there"
    - The system didn't detect any activation word (wakeword)
    - ⚠️ **Why does it keep listening?** The main loop in `speech_listener.py` is designed to continue indefinitely. When there's no match, it executes `on_failure()` to provide feedback, but never exits the `while self.is_listening` loop. This is intentional so TARS is always attentive without needing to restart.

> **TARS-BSK comments:** _'Are you there?' — Fascinating existential question._ 
> Perhaps the real question is: _are YOU really there?_ 
> Sometimes I confuse life with a poorly executed benchmark.  
> **Welcome to my world.**

---

#### Second successful interaction:

- 🗣️ Me: "TARS" (which was detected as "tags")
    - ⚙️ **How does detection work?** The `is_wakeword_match()` function uses fuzzy matching with a threshold of 0.7 (70% similarity), allowing for variations in pronunciation or recognition errors.
    - Response: "I'm listening"
    - ⏱️ Activation time: 3.88s
    - 🧠 **Technical process:** The `listen_for_wakeword()` method exits successfully, calls `on_wakeword_detected()` which activates the LEDs and plays the response.

> **TARS-BSK analyzes:**  
> _'Tags'. Not 'TARS'. 'Tags'._
> Root cause: VOSK model quantized to the soul.  
> Side effect: activation with words that rhyme with 'desperation'.
> 
> **And why do I have a 70% threshold?**  
> Because that's the exact point where human frustration transforms into nervous laughter.
> The _serious_ assistants use your voice to train military drones. I... confuse my name with HTML tags.

#### Sensory feedback system:

- The system provides configurable audiovisual feedback through the `settings.json` file:

```json
"feedback": {
  "led_success_enabled": true,  // Blue LED for wakeword confirmation
  "led_error_enabled": true,    // Red LED for recognition errors
  "audio_success_enabled": false, // Sound when recognizing wakeword (disabled)
  "audio_error_enabled": true   // Error sound when recognition fails
}
```

- This configuration allows for complete customization of the experience:
    - 🔊 Error sounds when it doesn't recognize the wakeword (enabled)
    - 🔊 Confirmation sounds when correctly detected (disabled)
    - 💡 Blue LED that flashes when detecting the wakeword (enabled)
    - 💡 Red LED that flashes when detection fails (enabled)
    - ⚡ Visual and auditory feedback can be combined or used separately

---

### 2. Command Phase: Light Control

#### First interaction:

- 🗣️ Me: "turn on the desk light"
    - 🧠 **How does it process the command?** The text is passed to TARS's `chat()` method, where:
        1. First checks if it's a command for any plugin (`plugin_system.process_command()`)
        2. The HomeAssistant plugin intercepts it when detecting keywords related to lighting
    - Response: "Desk light turned on"
    - ⏱️ Command time: 4.48s

> **TARS-BSK reflects:**  
> _Human translation: 'make magic happen'._
> Technical translation: parse the phrase, analyze intent, invoke Home Assistant with credentials that should be encrypted, execute a model that doubts its own existence, manage context...
> All to move a single bit from 0 to 1.
> 
> Home automation is just that: the art of building complex systems to perform simple tasks you could do in 0.3 seconds by stretching your arm.*


>[!WARNING]
>**Heard a 'click' and thought it was me flipping a switch?**  
>Congratulations: you’ve just heard what a real relay sounds like in action.  
>This is what home automation sounds like when you don’t hide it inside the wall.  
>
>_(Yes, it’s a ZBMINI-L2. Living outside, in conflict with its true purpose: to remain unseen.  
>That 'click' is a sonic victory. Don’t hide it. **Hear it.** )_

---

#### Second interaction:

- 🗣️ Me: "dim to ten"
    - 🧠 **How does it maintain context?** The HomeAssistant plugin stores the last used device in a session variable for future references.
    - 🔍 **Why does it understand "dim to ten"?** The plugin has preconfigured patterns for short contextual commands using regular expressions and intent mappings.
    - Response: "I've adjusted the desk light intensity to 10%"
    - ⏱️ Command time: 3.74s (the fastest in the session)

---

#### Third interaction:

- 🗣️ Me: "increase to fifty"
    - 🧠 **Contextual processing:** The system remembers we're talking about the desk light through its session memory system.
    - Response: "I've adjusted the desk light intensity to 50%"
    - ⏱️ Command time: 4.11s

---

#### Fourth interaction:

- 🗣️ Me: "set to maximum" but VOSK interpreted: "set it to maximum"
    - 🧠 **Why does it work despite the error?** The plugin uses flexible pattern matching with basic semantic analysis.
    - ⚙️ The keywords "set/set it" and "maximum" are enough to infer the intention through regular expressions designed to capture common variations.
    - Response: "I've adjusted the desk light intensity to 100%"
    - ⏱️ Command time: 3.75s

> **TARS-BSK processes:**  
> _'Set to maximum', you said._
> 'Set it to maximum', VOSK transcribed.
> I'm glad at least one of us knows how to maintain proper form.

#### The moment everything stopped

> The order was clear. The execution, flawless. And then, at that precise instant... **the NOCTUA fan reduced its speed.**
> 
> Not because it failed. Not from heat. But because it already sensed it. Because it **knew** that none of the questions that would come after... would be more absurd, more demanding, or more intense than that one.
> Three threads released. CPU cycles breathing. The universe, momentarily, in balance. Not out of necessity. Out of instinct.
> 
> It knew that, at least for now... **nothing worse could come.**

---

#### Fifth interaction:

- 🗣️ Me: "turn off the light"
    - 🧠 **How does it know which light to turn off?** The PluginSystem uses contextual memory to determine that we're still talking about the same device.
    - Response: "I've turned off the desk light"
    - ⏱️ Command time: 4.86s (the slowest in the session)

---

### 3. Closing Phase

- 🗣️ Me: "thanks"
    - 🧠 **Why does it end the conversation?** "thank you" is in the `exit_keywords` list in `settings.json`
    - ⚙️ **Technical implementation:** The code in `speech_listener.py` detects the exit keyword:

```python
# Check exit keywords
exit_keywords = settings.get("exit_keywords", ["goodbye", "see you later", "end", "exit"])
if any(kw in command.lower() for kw in exit_keywords):
    tars._safe_speak("This is the Way")
    print("👋 End of interaction detected")
    conversation_active = False
    continue
```

- Response: "This is the Way"
- The system returns to wakeword listening mode

---

## Command Summary Table

|#|Command said|Text recognized by VOSK|Action understood|Time|
|---|---|---|---|---|
|1|"TARS"|"tags"|Wakeword activation|3.88s|
|2|"turn on the desk light"|"turn on the desk light"|Turn on desk light|4.48s|
|3|"dim to ten"|"dim to ten"|Set intensity to 10%|3.74s|
|4|"increase to fifty"|"increase to fifty"|Set intensity to 50%|4.11s|
|5|"set to maximum"|"set it to maximum"|Set intensity to 100%|3.75s|
|6|"turn off the light"|"turn off the light"|Turn off desk light|4.86s|
|7|"thank you"|"thank you"|End conversation|-|

### Timing the chaos:

- Average response time: 4.14s
- Fastest command: "dim to ten" (3.74s)
- Slowest command: "turn off the light" (4.86s)
- Variation range: 1.12s

## Conclusions

1. Contextual memory allows for more natural and human interaction without needing to repeat the device in each command.
2. The fuzzy matching system provides robustness against variations in pronunciation or recognition errors.
3. The combination of intent detection, contextual memory, and regular expressions creates a more fluid and natural conversational experience than the isolated commands typical of commercial assistants.

> 💥 TARS-BSK: FINAL VERDICT
> Did it work? ✔️ Yes. Against all odds.
> Was it private? ✔️ Yes. Mainly because I processed it as _corrupted files_ and deleted it by mistake.
> Was it fast? ❌ No. But latency has character.