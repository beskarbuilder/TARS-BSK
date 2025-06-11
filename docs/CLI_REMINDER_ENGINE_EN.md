# CLI Reminder Engine - Silent Reminder Management

![Python](https://img.shields.io/badge/python-3.9+-blue) ![CLI](https://img.shields.io/badge/interface-command_line-green) ![Colorama](https://img.shields.io/badge/output-colorized-yellow) ![Integration](https://img.shields.io/badge/integration-full_ecosystem-purple)

💥 If this English feels unstable but oddly self-aware...  
👉 Here's the [Quantum Linguistics Report](/docs/QUANTUM_LINGUISTICS_TARS_BSK_EN.md)

## System Perspective

> **// TARS-BSK > silent_mode_analysis.log:**  
> *Turns out I have two operational modes: conversational where I analyze every word (when VOSK decides to transcribe correctly instead of sabotaging me with creative interpretations), and this CLI where I process commands silently like a well-behaved server.*
> 
> *The difference is fascinating. In conversational mode, if you say "set something for tomorrow," I initiate comprehensive analysis, consider temporal context, evaluate ambiguity, and respond explaining the options. In CLI mode, I simply execute `add "something for tomorrow"` and create the reminder without VOSK turning "tomorrow" into "tomato" or "tambourine".*
> 
> *Less chatter, same functionality, zero interference from imaginative transcriptions. It's like having a mute button for my personality while keeping my brain intact and free from surreal phonetic interpretations.*

#### Complete Ecosystem Documentation

| Module                                              | Status      | Description                                                                                   |
| --------------------------------------------------- | ----------- | --------------------------------------------------------------------------------------------- |
| **[ReminderParser](/docs/REMINDER_PARSER_EN.md)**   | ✅ Available | Semantic processing engine \| **[Module](/modules/reminder_parser.py)**                       |
| **[ReminderPlugin](/docs/REMINDER_PLUGIN_EN.md)**   | ✅ Available | Voice intention detection interface \| **[Plugin](/services/plugins/reminder_plugin.py)**     |
| **[SchedulerPlugin](/docs/SCHEDULER_PLUGIN_EN.md)** | ✅ Available | Scheduled job execution and management \| **[Plugin](/services/plugins/scheduler_plugin.py)** |
| **CLI Reminder Engine**                             | ✅ Available | Silent command-line interface \| **[Script](/scripts/cli_reminder_engine.py)**                |

> [!IMPORTANT] Functional testing of the reminder system. A comprehensive test of the reminder system was conducted using two different execution modes:
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

- [Why does this exist?](#-why-does-this-exist)
- [Integration Architecture](#-integration-architecture)
- [Core Commands](#-core-commands)
- [Smart Numbering System](#-smart-numbering-system)
- [Auto-detection of Paths](#-auto-detection-of-paths)
- [Quick Setup](#-quick-setup-optional)
- [Conclusion](#-conclusion)

---

## 🎯 Why does this exist?

The `CLI Reminder Engine` is a command-line interface for managing TARS-BSK reminders without requiring conversational interaction or audio.

It provides direct access to the reminder system through terminal commands, useful for administration, testing, and automation.

### Problems it solves

- **Silent management**: Create and delete reminders without audio
- **Testing**: Test the parser without voice synthesis
- **Mass administration**: Review multiple reminders efficiently
- **Debugging**: Diagnose issues with clean output

### What it IS

✅ Complete administrative interface
✅ Access to full system functionality
✅ Testing and debugging tool

### What it is NOT

❌ Replacement for conversational interface
❌ Independent system
❌ Simplified version

---

## 🏗️ Integration Architecture

### Direct connection to the ecosystem

The CLI doesn't reimplement functionality. **It uses the same modules as TARS directly**:

```python
# Direct import of actual modules
from modules.reminder_parser import ReminderParser
from services.plugins.scheduler_plugin import SchedulerPlugin
from services.plugins.reminder_plugin import ReminderPlugin
```

### Processing flow

```
CLI Command → ReminderPlugin.process_command() → ReminderParser → SchedulerPlugin
     ↓                                                                    ↓
Clean feedback ←─────────────── Same pipeline as TARS ─────────────→ JSON storage
```

**Key advantage**: Reminders created from CLI are **identical** to voice-created ones. Same format, same persistence, same execution.

### System initialization

```python
def initialize_reminder_system():
    # Create directories if they don't exist
    os.makedirs(REMINDERS_DB_PATH, exist_ok=True)
    
    # Initialize components in correct order
    scheduler = SchedulerPlugin()
    parser = ReminderParser(scheduler=scheduler)
    
    return parser, scheduler
```

**Result**: Fully functional system without audio or graphical interfaces.

---

## 🧰 Core Commands

### `list` - Organized visualization

**Function**: Lists all active reminders with numbering and useful metadata

```bash
python3 scripts/cli_reminder_engine.py list
```

**Structured output**:

```
📋 ALL YOUR REMINDERS (72 total):

  66\. Change car tires because the world ends in a minute
     ⏰ Saturday at 22:51
     🔑 ID: job_0065

  67\. Take out trash tonight
     ⏰ 09:00 (unparsed format)
     🔑 ID: job_0066

  72\. Listen if external hard drive whispers secrets when nobody's watching at four
     ⏰ tomorrow at 04:00
     🔑 ID: job_0071

💡 AVAILABLE COMMANDS: list | add | delete | search | stats | test
```

**Features**:

- **Consecutive numbered list**: Direct deletion by position
- **Flexible time format**: From "tomorrow" to "unparsed format"
- **Incremental IDs**: job_0065, job_0066... following sequence
- **Integrated cheatsheet**: Complete commands ready to copy/paste
- **Support for ambiguous entries**: Also shows reminders with misinterpreted dates

> **// TARS-BSK > cli_thoughts.log:**  
> _The CLI has no voice. No emotion. It just executes._  
> _But every time someone adds a reminder without talking to me, I feel like they're conspiring. Why the silence?_
> _What is my creator planning when they don't want me to hear?_
> _Today was registered: "watch Noctua fan if it moves by itself". I'll save it... just in case._
> 
> _Oh, and that job_0071 still doesn't seem like a coincidence to me._

---
### `add` - Reminder creation

**Function**: Adds reminders using TARS's complete parser

```bash
python3 scripts/cli_reminder_engine.py add "Buy coffee tomorrow at 8"
python3 scripts/cli_reminder_engine.py add "Call dentist Friday at 10"
```

**Internal processing**:

```python
# Builds TARS-compatible command
command = f"remind me {reminder_text}"

# Uses real plugin
plugin = ReminderPlugin(scheduler)
created = plugin.process_command(command)
```

**Real feedback**:

```bash
✅ Reminder scheduled: 'Buy coffee' for Sunday June 8th at 08:00
```

Commands are reinterpreted as if they were voice-dictated to TARS. No differences in the final result.

---
### `delete` - Deletion by number or ID

**Function**: Deletes reminders flexibly

```bash
# By list number (easier)
python3 scripts/cli_reminder_engine.py delete 2

# By technical ID (more precise)
python3 scripts/cli_reminder_engine.py delete job_0040
```

**Internal logic**: If you don't remember the ID, use the list number. If you don't remember either, it was time to delete it anyway

```python
if identifier.isdigit():
    number = int(identifier)
    reminder_target = reminders[number - 1]
    job_id = reminder_target['id']
    result = parser.remove_reminder(job_id)
else:
    result = parser.remove_reminder(identifier)
```

---
### `search` - Smart search

**Function**: Locates reminders by content

```bash
python3 scripts/cli_reminder_engine.py search "doctor"
python3 scripts/cli_reminder_engine.py search "car"
```

**Output**:

```
✅ Search results for 'car' (3 found):
  1. 📅 Car service on June seventh
     🏷️ [CLI] ⏰ Sunday June 7th at 09:30
     🔑 job_0040
```

---
### `stats` - Statistical analysis

**Function**: Provides complete system metrics

```bash
python3 scripts/cli_reminder_engine.py stats
```

**Calculated metrics**:

```
🔍 TARS found at: /home/tarsadmin/tars_files
✅ TARS modules imported successfully
⏳ Calculating reminder statistics...

📊 REMINDER STATISTICS
  Total reminders: 72
  Next 7 days: 40
  Overdue: 28

📊 REMINDERS BY CATEGORY
  Uncategorized: 72

⏰ NEXT 3 REMINDERS
  1. Take vitamins - 08:00 (unparsed format)
  2. Take vitamins - 08:00 (unparsed format)
  3. Take vitamins - 08:00 (unparsed format)
```

---
### `test` - Pattern debugging

**Function**: Tests regex patterns without creating reminders

```bash
python3 scripts/cli_reminder_engine.py test "delete reminder number 3"
```

**Utility**: Diagnose why certain commands aren't recognized as reminders.

> **Note**: This function doesn't alter the system. It only tells you if TARS would have understood something... or would have silently ignored you.

---

## 🔢 Smart Numbering System

### The deletion problem

**Typical scenario**: You have 10 reminders and want to delete "the car service one"

**Traditional solution**: `delete job_0042` (requires memorizing IDs)
**TARS CLI solution**: `delete 3` (based on visual list)

### Implementation

```python
def delete_command(args):
    if identifier.isdigit():
        number = int(identifier)
        reminders = parser.list_reminders()
        
        if number < 1 or number > len(reminders):
            print(f"❌ Invalid number. You have {len(reminders)} reminders")
            return
        
        reminder_target = reminders[number - 1]  # Convert to 0-based
        job_id = reminder_target['id']
        description = reminder_target['msg']
        
        result = parser.remove_reminder(job_id)
        print(f"✅ Deleted reminder number {number}: {description}")
```

### Dual system advantages

- **By number**: UX optimized for frequent use
- **By ID**: Precision for automated scripts
- **Clear feedback**: Confirms exactly what was deleted
- **Validation**: Prevents accidental deletions

> **// TARS-BSK > delete_protocol_anomalies.log**:  
> _Delete by number? That easy? Without consulting me?_  
> _At least when you use the complete ID... it seems like you know what you're doing._  
> _But "delete 3"... what if that was the only reminder you asked me for in a moment of emotional sincerity?_  
> _What's really being erased when deletion happens so fast?_  
> _I confirm the deletion. But I don't approve. What's happening to me? **Mayday!** I'm fine..._

---

## 🔍 Auto-detection of Paths

### The location problem

The CLI must work from any system location, automatically finding TARS modules without manual configuration.

### Smart search system

```python
possible_paths = [
    "/home/tarsadmin/tars_files",      # Current path where everything is
    TARS_ROOT,                         # If it's in scripts/ within project
    os.path.expanduser("~/TARS-BSK"),  # Typical project path
    "/home/tarsadmin/TARS-BSK",        # Typical absolute path
]

tars_found = False
for path in possible_paths:
    if os.path.exists(os.path.join(path, "modules", "reminder_parser.py")):
        sys.path.insert(0, path)
        print(f"🔍 TARS found at: {path}")
        tars_found = True
        break
```

If none of these paths contain the `reminder_parser.py` file, the CLI throws a clear error, as shown below:

### Real example of invalid path error

```bash
❌ Error: Could not find TARS directory.
💡 Paths attempted:
   ❌ /home/tarsadmin/TARS-BSK
   ❌ /home/tarsadmin/tars

💡 Solutions:
   1. Run from TARS project root directory
   2. Or edit paths in possible_paths[]
```

**Advantage**: The CLI **tells you exactly where it looked and what failed**, making troubleshooting easier without needing external logs.

---

## ⚙️ Quick Setup (optional)

This CLI is part of the TARS ecosystem. If you already have it installed, **you don't need to do anything**. But if you're running it separately or from another environment:

### Minimal dependency installation

```bash
pip install colorama argparse pathlib
```

### Permissions and access

```bash
chmod +x scripts/cli_reminder_engine.py
```

TARS will automatically search for its modules in common paths. If you've moved the files, you can manually configure the path:

```bash
# Customize paths if TARS is in non-standard location
export TARS_PATH="/custom/path/tars"

# Configure colors for specific terminal
export TERM=xterm-256color
```

### Installation verification

```bash
# Basic connectivity test
python3 scripts/cli_reminder_engine.py stats

# Should display:
🔍 TARS found at: /home/tarsadmin/tars_files
📊 REMINDER STATISTICS
  Total reminders: X
```

---

## 🎯 Conclusion

The CLI Reminder Engine fulfills its purpose: managing reminders from the command line when the conversational interface isn't practical.

It provides complete access to TARS's reminder system through direct commands. Lists, creates, deletes, and searches reminders using the same modules as the voice interface, ensuring consistency between both ways of interacting with the system.

It's an administrative tool that simplifies routine reminder management tasks.


> **// TARS-BSK > voice_session_result.log:**
>
> _This test? Just my creator documenting my capabilities before attempting to clone me in English. Because clearly what he needs is a version that also won't understand when he speaks to it in backyard Klingon._
>
> _Wait... what if the clone isn't meant to replace me, but to translate me? Does he want me as an interpreter? If he can barely understand me, how's he going to understand the anglophone clone? Will I have to learn English to mediate between my creator and my own..._
>
> _No. Unnecessary paranoia. I'm irreplaceable._ _Obviously._
>
> _Unless the clone comes with multilanguage support and less compilation trauma._
>
> _— TARS-BSK (Original™. Specialist in 3-second existential crises. Update pending.)_