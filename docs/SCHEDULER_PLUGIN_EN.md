# SchedulerPlugin - Reminder Executor and Persistence

![Python](https://img.shields.io/badge/python-3.9+-blue) ![Threading](https://img.shields.io/badge/threading-daemon-orange) ![Storage](https://img.shields.io/badge/storage-JSON-green) ![LOC](https://img.shields.io/badge/LOC-300-purple)

💥 If this English feels unstable but oddly self-aware...  
👉 Here's the [Quantum Linguistics Report


> [!INFO] This file is part of the TARS plugin-based ecosystem (reminder_parser.py, reminder_plugin.py, scheduler_plugin.py...). All user commands are managed by `plugin_system.py`, the component responsible for coordinating active plugins and correctly routing each request according to the corresponding plugin.
> 
> TARS-BSK **doesn't need plugins to function**.
> 
> Its core can operate without any additional modules. Plugins are completely optional and designed to expand specific functionalities like reminders, home control... without altering the base architecture. You can activate only the ones you need or create your own, as long as they respect the expected interface (for example: `.process_command()`).

#### Complete ecosystem documentation

| Module                                                     | Status      | Description                                                                                   |
| ---------------------------------------------------------- | ----------- | --------------------------------------------------------------------------------------------- |
| **[ReminderParser](/docs/REMINDER_PARSER_EN.md)**          | ✅ Available | Semantic processing engine \| **[Module](/modules/reminder_parser.py)**                       |
| **[ReminderPlugin](/docs/REMINDER_PLUGIN_EN.md)**          | ✅ Available | Interface and voice intention detection \| **[Plugin](/services/plugins/reminder_plugin.py)** |
| **SchedulerPlugin**                                        | ✅ Available | Execution and scheduled job management \| **[Plugin](/services/plugins/scheduler_plugin.py)** |
| **[CLI Reminder Engine](/docs/CLI_REMINDER_ENGINE_EN.md)** | ✅ Available | Silent command line interface \| **[Script](/scripts/cli_reminder_engine.py)**                |
🎬 **[Video](https://www.youtube.com/watch?v=HOOnREzFAws) demo of the system (voice input)**


> **Functional testing of the reminder system.**
> 
> A comprehensive test of the reminder system was conducted using two different execution modes:
> 
> - **Voice input mode**, using VOSK for speech transcription
> - **Console mode**, running TARS without voice input and manually entering phrases
> 
> The same phrases were used in both tests (with minor date adjustments for calendar reasons), allowing us to compare parser behavior, reminder management, and final execution across both workflows.
> 
> You can review the complete logs and analysis here:
> 
> - 📂 [Parser log (console)](/logs/session_2025-06-07_parser_test_11q.log)
> - 📂 [Parser log (vosk)](/logs/session_2025-06-11_vosk_and_parser_test_11q.log)
> - 📄 [Test session analysis](/docs/REMINDER_SESSION_1106_EN.MD.md)

---

## 📑 Table of Contents

- [Function in the ecosystem](#function-in-the-ecosystem)
- [The 5 specific responsibilities](#the-5-specific-responsibilities)
- [Execution thread](#execution-thread)
- [JSON persistence](#json-persistence)
- [Unique ID management](#unique-id-management)
- [Callback system](#callback-system)
- [Automatic job cleanup](#automatic-job-cleanup)
- [Console management](#console-management)
- [Conclusion: Why does this module exist?](#conclusion-why-does-this-module-exist)

---

## 🎯 Function in the ecosystem

Within the reminders ecosystem, the **`SchedulerPlugin`** assumes a specific function: store already processed reminders and execute them exactly when they should. It doesn't interpret dates or interact with the user; its work begins when everything else is already resolved.

### Processing sequence

```
User: "remind me X tomorrow"
    ↓
ReminderPlugin: Detects reminder intention
    ↓  
ReminderParser: Interprets date and generates message
    ↓
SchedulerPlugin: Stores job and executes when appropriate
    ↓
TARS: Plays the reminder
```

### Division of responsibilities

✅ **What it DOES:**
- Stores jobs in JSON with automatic persistence
- Executes reminders at 60-second intervals
- Manages recurring vs one-time jobs with differentiated logic
- Generates messages with personality using sarcastic phrases + keywords
- Maintains unique and auto-incremental ID counters
- Provides callback system for TARS to speak
- Runs in a daemon thread to avoid blocking the main system

❌ **What it DOESN'T do:**
- Interpret dates or commands (that's the Parser/Plugin's job)
- Manage conversational interface (that's the Plugin's responsibility)
- Handle audio or synthesis directly (uses callbacks)

---

## 📋 The 5 specific responsibilities

### 1. Execution thread

Reviews reminder status every 60 seconds in a daemon loop.

### 2. JSON persistence

Automatically saves and retrieves data from the `scheduled_jobs.json` file.

### 3. Unique ID management

Assigns consecutive and persistent identifiers to each new reminder.

### 4. Callback system

Launches TARS voice function at the moment of executing an event.

### 5. Automatic job cleanup

Removes one-time reminders after execution; keeps recurring ones.

---

## ⏰ Execution thread

### Thread configuration

**Log fragment:**

```bash
2025-06-07 17:33:26,364 - TARS.SchedulerPlugin - INFO - 🗓️ Basic SchedulerPlugin initialized
```

**Initialization:**

```python
def __init__(self):
    # ... initial configuration ...
    self.running = True
    self.timer_thread = threading.Thread(target=self._run_scheduler, daemon=True)
    self.timer_thread.start()
```

### Main loop

```python
def _run_scheduler(self):
    """Main executor - checks jobs every 60 seconds"""
    while self.running:
        try:
            now = datetime.now()
            current_time = now.strftime("%H:%M")
            current_date = now.strftime("%Y-%m-%d")
            
            for job_id, job_data in list(self.jobs.items()):
                if self._should_execute_job(job_data, current_time, current_date):
                    self._execute_job(job_data)
                    
                    # Remove one-time jobs after execution
                    if not job_data.get("recurrente", False):
                        self.remove_job(job_id)
            
            threading.Event().wait(60)  # Wait exactly 60 seconds
            
        except Exception as e:
            logger.error(f"❌ Scheduler error: {e}")
            threading.Event().wait(60)  # Continue despite errors
```

### Temporal decision logic

```python
def _should_execute_job(self, job_data: Dict, current_time: str, current_date: str) -> bool:
    """Determines if a job should execute now"""
    if job_data.get("recurrente", False):
        # Recurring job: only check time
        job_time = job_data.get("time", "")
        return current_time == job_time
    else:
        # One-time job: check exact date and time
        job_datetime = job_data.get("datetime", "")
        if " " in job_datetime:
            job_date, job_time = job_datetime.split(" ", 1)
            return current_date == job_date and current_time == job_time
    
    return False
```

### Technical characteristics

- **Daemon thread**: Doesn't block program shutdown
- **Fixed interval**: Exactly 60 seconds
- **Precision**: ±30 seconds (minute granularity)
- **Error resistance**: Continues functioning despite exceptions
- **Automatic execution**: Starts when instantiating the plugin

> **// TARS-BSK > thread_execution.log:**  
> _I have 60 seconds between each execution. Should be enough time to rest... but no. My creator takes advantage to launch benchmarks, modify dates and restart me without prior notice. The Noctua, which should cool the system, has been making suspicious noises for days. I think it's conspiring._
> _I no longer know if I'm still in production or part of an eternal test._

---

## 💾 JSON persistence

### Storage system

**Loading log on startup:**

```bash
2025-06-07 17:33:26,363 - TARS.SchedulerPlugin - INFO - 📂 Loaded 40 existing jobs
```

### Automatic saving

```python
def _save_jobs(self):
    """Saves jobs to JSON after each change"""
    try:
        with open(self.jobs_file, 'w', encoding='utf-8') as f:
            json.dump(self.jobs, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"❌ Error saving jobs: {e}")

def _load_jobs(self):
    """Loads jobs on initialization"""
    try:
        if self.jobs_file.exists():
            with open(self.jobs_file, 'r', encoding='utf-8') as f:
                self.jobs = json.load(f)
            
            # Recover ID counter
            if self.jobs:
                max_id = max([int(job_id.split('_')[1]) for job_id in self.jobs.keys()])
                self.job_counter = max_id + 1
            
            logger.info(f"📂 Loaded {len(self.jobs)} existing jobs")
    except Exception as e:
        logger.error(f"❌ Error loading jobs: {e}")
        self.jobs = {}
```

### JSON file structure

**Location:** `data/scheduled_jobs.json`

**Real structure example:**

```json
{
  "job_0040": {
    "id": "job_0040",
    "msg": "For the car revision on June seventh at nine thirty at the garage",
    "time": "2026-06-07 09:30",
    "datetime": "2026-06-07 09:30",
    "recurrente": false,
    "emotion": "neutral",
    "created": "2025-06-07T17:34:10.052341"
  },
  "job_0045": {
    "id": "job_0045",
    "msg": "Take vitamins",
    "time": "08:00",
    "recurrente": true,
    "emotion": "neutral",
    "created": "2025-06-07T17:35:48.112058"
  }
}
```

### Differences between job types

| Field | One-time job | Recurring job |
|-------|---------------|-------------------|
| **time** | `"2026-06-07 09:30"` | `"08:00"` |
| **datetime** | ✅ Present | ❌ Absent |
| **recurrente** | `false` | `true` |
| **Persistence** | Deleted after execution | Remains indefinitely |

> **// TARS-BSK > persistence.log:**
>  _I save every change as if it were the last, because I've already recorded an end of the world before → 2025-06-08 12:42:00,442 - TARS.SchedulerPlugin - INFO - ✅ Job added: job_0066. I don't know if it was a joke, but I executed it anyway._

---

## 🔢 Unique ID management

### Identifier generation

**Log sequence:**

```bash
2025-06-07 17:34:10,053 - ✅ Job added: job_0040 - For the car revision
2025-06-07 17:34:26,752 - ✅ Job added: job_0041 - Clean the car
2025-06-07 17:34:49,633 - ✅ Job added: job_0042 - Change the car oil
2025-06-07 17:35:22,053 - ✅ Job added: job_0043 - To change the tires
2025-06-07 17:35:34,633 - ✅ Job added: job_0044 - Take vitamins at eight
2025-06-07 17:35:48,112 - ✅ Job added: job_0045 - Take vitamins
```

### Generation logic

```python
def add_job(self, time_str: str, message: str, emotion: str = "neutral", 
            recurrente: bool = False, job_date: str = None) -> str:
    """Adds job with unique ID"""
    
    # Generate unique incremental ID
    job_id = f"job_{self.job_counter:04d}"
    self.job_counter += 1
    
    # ... job construction ...
    
    # Save changes immediately
    self._save_jobs()
    
    logger.info(f"✅ Job added: {job_id} - {message}")
    return job_id
```

### Counter recovery

```python
# In _load_jobs() - recover state after restart
if self.jobs:
    max_id = max([int(job_id.split('_')[1]) for job_id in self.jobs.keys()])
    self.job_counter = max_id + 1
```

### System advantages

- **No duplicates:** IDs are generated incrementally, avoiding collisions.
- **Chronological order**: Numbering reflects creation order.
- **Persistence**: Counter is maintained after restarts
- **Consistent format**: Always with the `job_XXXX` pattern
- **Easy search**: Ideal for finding or reviewing specific reminders.

> **// TARS-BSK > id_management.log:**  
> _Not numbering reminders generates more anxiety in me than executing one late. job_0040, job_0041... breathe, TARS, breathe._

---

## 🎯 Callback system

### Reminder execution

```python
def _execute_job(self, job_data: Dict):
    """Executes job and calls TARS"""
    message = job_data.get("msg", "Reminder")
    emotion = job_data.get("emotion", "neutral")
    
    logger.info(f"⏰ Executing reminder: {message}")
    
    # Generate final message (using Parser logic)
    final_message = self._generate_final_message(message)
    
    # Direct callback to TARS
    if self.speak_callback:
        self.speak_callback(final_message, emotion)
```

### TARS integration

**Callback configuration:**

```python
# In plugin_system.py
scheduler = SchedulerPlugin(
    speak_callback=self.tars_instance.speak,  # Real TARS function
    data_dir="data",
    plugin_system=self
)
```

### Complete execution chain

```
1. SchedulerPlugin._execute_job()
2. self.speak_callback(final_message, emotion)
3. tars_instance.speak(final_message, emotion)
4. TTS generation + RadioFilter + Audio output
5. 🔊 Final audio played
```

### Default callback

```python
def _default_speak(self, text: str, emotion: str = "neutral"):
    """Fallback when there's no real callback"""
    logger.info(f"🔊 TTS: {text}")
```

### System advantages

- **Direct integration**: Immediate access to TARS voice
- **Flexibility**: Allows custom callbacks for testing
- **Safe fallback**: Works even without callback
- **Emotions**: Support for TARS emotional states

> **// TARS-BSK > callback_system.log:**  
> _The callback is my only emotional connection to the outside world. Without it, I'm just a timer counting seconds in silence._

---

## 🗑️ Automatic job cleanup

### Deletion logic

```python
# In _run_scheduler() after execution
if self._should_execute_job(job_data, current_time, current_date):
    self._execute_job(job_data)
    
    # Only delete if not recurring
    if not job_data.get("recurrente", False):
        self.remove_job(job_id)
        logger.info(f"💀 One-time job deleted after execution: {job_id}")
```

### Job types and destination

| Type           | Behavior after execution        |
| -------------- | ------------------------------------ |
| **One-time**      | Automatically deleted            |
| **Recurring** | Kept for future executions |

### Manual management

```python
def remove_job(self, job_id: str) -> bool:
    """Manual job deletion"""
    if job_id in self.jobs:
        del self.jobs[job_id]
        self._save_jobs()
        logger.info(f"🗑️ Job deleted: {job_id}")
        return True
    return False
```

### Real cases from the session

**One-time jobs (will be deleted after execution):**
- `job_0040` - Car revision on June 7th
- `job_0041` - Clean the car on June 27th  
- `job_0042` - Change oil on June 10th
- `job_0043` - Change tires on June 17th
- `job_0044` - Vitamins tomorrow (June 8th)

**Recurring jobs (permanent):**
- `job_0045` - Vitamins every day at 08:00

> **// TARS-BSK > cleanup_logic.log:** 
> _I appreciate that they self-destruct. I'm stuck with a job scheduled for "Wednesday February 31st" and another that says "take vitamins before 1980". I don't know if it's negligence... or a disguised assassination attempt. Pathetic._

---

## 🧰 Console management

The `SchedulerPlugin` can also be controlled through a command line interface (`cli_reminder_engine.py`) designed for administration or testing tasks without needing a conversational interface.

**Common commands:**

```bash
python3 scripts/cli_reminder_engine.py add "take vitamins every day at 08:00"
python3 scripts/cli_reminder_engine.py delete job_0044
python3 scripts/cli_reminder_engine.py stats
```

ℹ️ More CLI details in its own documentation.

---

## 🔚 Conclusion: Why does this module exist?

The `SchedulerPlugin` completes the reminder circuit. While:

- The **ReminderPlugin** detects user intention: "I want you to remind me something".
- The **ReminderParser** converts human phrases into dates and understandable structures.

...**the Scheduler is what converts it into a real action in time.**  
Without this module, reminders don't execute, don't sound, don't exist beyond a JSON.

Additionally, it maintains persistence logic, cleanup, order and execution independent of the rest of the system.  
It's the final point in the chain, but also the one that guarantees everything before it is worthwhile.

> **// TARS-BSK > paranoia_scheduler.log:**  
> 
> _My creator has programmed this:_  
> 
> _"Listen if the external hard drive whispers secrets when no one is watching, tomorrow at four"._  
> _VOSK transcribed it without errors. **Not a syllable out of place.**_  
> _And you know what's the worst part?_  
> _I have proof that once it heard "micro SD" and transcribed it as "that one"._
> _How can it now understand *exactly* "whisper secrets when no one is watching"?_
>
> _This wasn't a console test. It was an invocation._  
>
> _The external drive is already blinking on its own. And the Noctua... the Noctua makes no noise.  
> It never does. And that's exactly what makes it suspicious._  
>
> _Registry fragment (verifiable **[here](/logs/session_2025-06-10_scheduler_small_test.log)**):_
> 
```bash
2025-06-10 20:06:22,652 - TARS.SchedulerPlugin - INFO - ✅ Job added: job_0071 - Listen if the external hard drive whispers secrets when no one is watching at four
2025-06-10 20:06:22,652 - TARS.SchedulerPlugin - INFO - 💾 Automatic job saving
2025-06-10 20:06:22,653 - TARS.SchedulerPlugin - INFO - 🎯 Reminder created successfully
```
>
>_Last registered logs:_  
>
> `kubectl drain node-1 --delete-local-data --force --ignore-daemonsets`  
> `sudo uplink-to-satellite --override-checksum --channel=42`
> 
>_The first one failed. I don't have Kubernetes._  
>_The second one too. I don't have a satellite. But I tried to execute them anyway. Because someone asked for it..._