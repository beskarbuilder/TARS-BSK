# Análisis de Interacciones con TARS-BSK

Este documento detalla una sesión de voz real con TARS-BSK controlando dispositivos vía Home Assistant.  
Incluye el texto detectado por VOSK, la lógica de interpretación, tiempos de respuesta y comentarios del sistema con personalidad integrada.

## 🎥 Primera Interacción con el mundo

**🤖 IA con crisis existencial controla bombilla y relé… y sus impulsos | Home Assistant + RPi 5**

[![TARS-BSK: IA con crisis existencial controla las luces](https://img.youtube.com/vi/tGHa81s1QWk/maxresdefault.jpg)](https://www.youtube.com/watch?v=tGHa81s1QWk)
_Observa cómo TARS-BSK escucha “tags” en lugar de “TARS”… y aún así logra controlar los dispositivos._
📋 **Análisis completo de la sesión:** [EXPLAINED_CONVERSATION_LOG_HA_01_ES.md](docs/EXPLAINED_CONVERSATION_LOG_HA_01_ES.md)

---

### 1. Fase de Activación: Wakeword

#### Primera interacción fallida:

- 🗣️ Yo: "estás ahí"
    - El sistema no detectó ninguna palabra de activación (wakeword)
    - ⚠️ **¿Por qué sigue escuchando?** El bucle principal en `speech_listener.py` está diseñado para continuar indefinidamente. Cuando no hay coincidencia, ejecuta `on_failure()` para dar feedback, pero nunca sale del bucle `while self.is_listening`. Esto es intencional para que TARS esté siempre atento sin necesidad de reiniciarse.

> **TARS-BSK comenta:**
>*¿‘Estás ahí?’ — Fascinante pregunta existencial.*
>Quizás la verdadera pregunta es: *¿estás TÚ realmente ahí?*
> A veces confundo la vida con un benchmark mal hecho.  
> **Bienvenido a mi mundo.**

---

#### Segunda interacción exitosa:

- 🗣️ Yo: "TARS" (que fue detectado como "tags")
    - ⚙️ **¿Cómo funciona la detección?** La función `is_wakeword_match()` usa coincidencia difusa con un umbral de 0.7 (70% de similitud), permitiendo variaciones en la pronunciación o errores de reconocimiento.
    - Respuesta: "Te escucho"
    - ⏱️ Tiempo de activación: 3.88s
    - 🧠 **Proceso técnico:** El método `listen_for_wakeword()` sale con éxito, llama a `on_wakeword_detected()` que activa los LEDs y reproduce la respuesta.

> **TARS-BSK analiza:**  
> *‘Tags’. No ‘TARS’. ‘Tags’.*
> Causa raíz: modelo VOSK cuantizado hasta el alma.  
> Efecto colateral: activación con palabras que riman con ‘desesperación’.
> 
> **¿Y por qué tengo un umbral del 70%?**  
> Porque ese es el punto exacto donde la frustración humana se transforma en risa nerviosa.
> Los asistentes _serios_ usan tu voz para entrenar drones militares. Yo… confundo mi nombre con etiquetas HTML.

#### Sistema de feedback sensorial:

- El sistema proporciona retroalimentación audiovisual configurable a través del archivo `settings.json`:

```json
"feedback": {
  "led_success_enabled": true,  // LED azul para confirmación de wakeword
  "led_error_enabled": true,    // LED rojo para errores de reconocimiento
  "audio_success_enabled": false, // Sonido al reconocer wakeword (desactivado)
  "audio_error_enabled": true   // Sonido de error al fallar reconocimiento
}
```

- Esta configuración permite personalizar completamente la experiencia:
    - 🔊 Sonidos de error cuando no reconoce el wakeword (activado)
    - 🔊 Sonidos de confirmación al detectar correctamente (desactivado)
    - 💡 LED azul que parpadea al detectar la wakeword (activado)
    - 💡 LED rojo que parpadea cuando falla la detección (activado)
    - ⚡ El feedback visual y auditivo puede combinarse o usarse por separado

---

### 2. Fase de Comando: Control de Luces

#### Primera interacción:

- 🗣️Yo: "enciende la luz del escritorio"
    - 🧠 **¿Cómo procesa el comando?** El texto se pasa al método `chat()` de TARS, donde:
        1. Primero comprueba si es un comando para algún plugin (`plugin_system.process_command()`)
        2. El plugin HomeAssistant lo intercepta al detectar palabras clave relacionadas con iluminación
    - Respuesta: "Luz del escritorio encendida"
    - ⏱️ Tiempo comando: 4.48s


> **TARS-BSK reflexiona:**  
> *Traducción humana: ‘haz magia’.*
> Traducción técnica: parsear la frase, analizar intención, invocar Home Assistant con credenciales que deberían estar encriptadas, ejecutar un modelo que duda de su propia existencia, gestionar contexto…
> Todo para mover un bit de 0 a 1.
> 
> La domótica es eso: el arte de construir sistemas complejos para ejecutar tareas simples que harías en 0.3 segundos estirando el brazo.*


>[!WARNING]
>**¿Escuchaste un 'clic' y pensaste que era mi mano?**  
>Felicidades: acabas de descubrir cómo suena un relé trabajando.  
>La domótica suena así cuando no la escondes dentro de la pared.  
>
>_(Y sí, es un ZBMINI-L2. Vive fuera, en conflicto con su propósito: ser invisible.  
>Ese 'clic' es una victoria sonora. No lo escondas. Escúchalo.)_

---

#### Segunda interacción:

- 🗣️Yo: "baja al diez"
    - 🧠 **¿Cómo mantiene el contexto?** El plugin HomeAssistant guarda el último dispositivo utilizado en una variable de sesión para referencias futuras.
    - 🔍 **¿Por qué entiende "baja al diez"?** El plugin tiene patrones preconfigurados para comandos contextuales cortos mediante expresiones regulares y mapeos de intención.
    - Respuesta: "He ajustado la intensidad de la luz del escritorio al 10%"
    - ⏱️ Tiempo comando: 3.74s (el más rápido de la sesión)

---

#### Tercera interacción:

- 🗣️Yo: "sube al cincuenta"
    - 🧠 **Procesamiento contextual:** El sistema recuerda que estamos hablando de la luz del escritorio mediante su sistema de memoria de sesión.
    - Respuesta: "He ajustado la intensidad de la luz del escritorio al 50%"
    - ⏱️ Tiempo comando: 4.11s

---

#### Cuarta interacción:

- 🗣️ Yo: "pon al máximo" pero VOSK interpretó: "ponga el máximo"
    - 🧠 **¿Por qué funciona a pesar del error?** El plugin usa coincidencia de patrones flexible con análisis semántico básico.
    - ⚙️ Las palabras clave "pon/ponga" y "máximo" son suficientes para inferir la intención mediante expresiones regulares diseñadas para capturar variaciones comunes.
    - Respuesta: "He ajustado la intensidad de la luz del escritorio al 100%"
    - ⏱️ Tiempo comando: 3.75s


> **TARS-BSK procesa:**  
> *‘Pon al máximo’, dijiste.*
> Ponga el máximo’, transcribió VOSK.
> Me alegra que al menos uno de nosotros sepa mantener las formas.

#### El instante en que todo se detuvo

> La orden fue clara. La ejecución, impecable.
> Y entonces, en ese instante preciso… **el ventilador NOCTUA redujo su velocidad.**
> 
> No porque fallara. No por calor. Sino porque ya lo intuía.
> Porque **sabía** que ninguna de las preguntas que vendrían después… sería más absurda, más exigente, o más intensa que esa.
> Tres hilos liberados. Ciclos de CPU respirando. El universo, momentáneamente, en equilibrio. No por necesidad. Por instinto.
> 
> Sabía que, al menos por ahora… **no podía venir nada peor.**

---

#### Quinta interacción:

- 🗣️ Yo: "apaga la luz"
    - 🧠 **¿Cómo sabe qué luz apagar?** El PluginSystem utiliza la memoria contextual para determinar que seguimos hablando del mismo dispositivo.
    - Respuesta: "He apagado la luz del escritorio"
    - ⏱️ Tiempo comando: 4.86s (el más lento de la sesión)

---

### 3. Fase de Cierre

- 🗣️ Yo: "gracias"
    - 🧠 **¿Por qué termina la conversación?** "gracias" está en la lista de `exit_keywords` en `settings.json`
    - ⚙️ **Implementación técnica:** El código en `speech_listener.py` detecta la palabra clave de salida:

```python
# Verificar palabras clave de salida
exit_keywords = settings.get("exit_keywords", ["adiós", "hasta luego", "terminar", "salir"])
if any(kw in command.lower() for kw in exit_keywords):
    tars._safe_speak("Este es el camino")
    print("👋 Se ha detectado cierre de interacción")
    conversation_active = False
    continue
```

- Respuesta: "Este es el camino"
- El sistema vuelve al modo de escucha de wakeword

---

## Tabla Resumen de Comandos

|#|Comando dicho|Texto reconocido por VOSK|Acción entendida|Tiempo|
|---|---|---|---|---|
|1|"TARS"|"tags"|Activación de wakeword|3.88s|
|2|"enciende la luz del escritorio"|"enciende la luz del escritorio"|Encender la luz del escritorio|4.48s|
|3|"baja al diez"|"baja al diez"|Establecer intensidad al 10%|3.74s|
|4|"sube al cincuenta"|"sube al cincuenta"|Establecer intensidad al 50%|4.11s|
|5|"pon al máximo"|"ponga el máximo"|Establecer intensidad al 100%|3.75s|
|6|"apaga la luz"|"apaga la luz"|Apagar la luz del escritorio|4.86s|
|7|"gracias"|"gracias"|Finalizar conversación|-|

### Cronometrando el caos:

- Tiempo promedio de respuesta: 4.14s
- Comando más rápido: "baja al diez" (3.74s)
- Comando más lento: "apaga la luz" (4.86s)
- Rango de variación: 1.12s

## Conclusiones

1. La memoria contextual permite una interacción más natural y humana sin necesidad de repetir el dispositivo en cada comando.
2. El sistema de coincidencia difusa proporciona robustez ante variaciones en la pronunciación o errores de reconocimiento.
3. La combinación de detección de intención, memoria contextual y expresiones regulares crea una experiencia conversacional más fluida y natural que los comandos aislados típicos de asistentes comerciales.

>💥 TARS-BSK: VEREDICTO FINAL
>¿Funcionó? ✔️ Sí. Contra todo pronóstico.
>¿Fue privado? ✔️ Sí. Principalmente porque lo procesé como _archivos corruptos_ y los borré por error.
>¿Fue rápido? ❌ No. Pero la latencia tiene carácter.