# TARS CLI - Command Line Interface

![Python](https://img.shields.io/badge/python-3.9+-blue) ![SQLite](https://img.shields.io/badge/sqlite-3+-green) ![CLI](https://img.shields.io/badge/interface-CLI-orange) ![Status](https://img.shields.io/badge/status-stable-brightgreen)

💥 If this English feels unstable but oddly self-aware...  
👉 Here's the [Quantum Linguistics Report](/docs/QUANTUM_LINGUISTICS_TARS_BSK_EN.md)


> **TARS-BSK reflects:** _Finally, a way to talk to me without waiting 30 seconds of neural processing and voice synthesis. My CLI is the closest you'll get to having an instant conversation with me... although technically you're still talking directly to SQLite..._

---

## 📑 Table of Contents

- [What is TARS CLI?](#-what-is-tars-cli)
- [Installation and requirements](#-installation-and-requirements)
- [Basic usage](#-basic-usage)
- [Available commands](#-available-commands)
- [Practical use cases](#-practical-use-cases)
- [Technical features](#-technical-features)
- [Troubleshooting](#-troubleshooting)
- [Known limitations](#-known-limitations)

---

## 🤖 What is CLI Semantic Engine?

It's a command-line tool that allows direct management of preferences stored in TARS-BSK, memory system analysis, and debugging without needing voice interaction or waiting for AI processing.

**Main capabilities:**

- **Preference management**: Add, delete, search, and list likes/dislikes
- **System analysis**: Detailed memory statistics and categorization
- **Advanced debugging**: Direct SQLite database inspection
- **Maintenance**: Data cleanup and organization
- **Taxonomy**: Exploration of available category systems

---

## 📦 Installation and requirements

📂 **File:** [scripts/cli_semantic_engine.py](/scripts/cli_semantic_engine.py)

### Prerequisites (already installed with TARS-BSK)

```bash
# Python 3.9 or higher
python3 --version

# Dependencies 
pip install colorama sqlite3
```

### Installation verification

```bash
# From TARS main directory
cd ~/tars_files
python3 scripts/cli_semantic_engine.py --help
```

**Expected output:**

```
usage: cli_semantic_engine.py [-h] {list,add,search,delete,categories,stats} ...

TARS CLI - Command line interface for TARS

positional arguments:
  {list,add,search,delete,categories,stats}
                        Available commands
    list                List all preferences from database
    add                 Add a new preference to database
    search              Search preferences by keyword
    delete              Delete a preference
    categories          Show available categories in taxonomy
    stats               Show preference statistics

optional arguments:
  -h, --help            show this help message and exit
```

---

## 🚀 Basic usage

### Command structure

```bash
python3 scripts/cli_semantic_engine.py [COMMAND] [ARGUMENTS] [OPTIONS]
```

### First use

```bash
# View current system status
python3 scripts/cli_semantic_engine.py stats

# List all existing preferences
python3 scripts/cli_semantic_engine.py list
```

---

## 📋 Available commands

> **Data interpretation in all commands:**
> 
> - `sent`: Sentiment value (-1.0 negative to +1.0 positive)
> - `imp`: Importance level (0.0 low to 1.0 very important)
> - `[CATEGORY]`: Automatic system classification

### `list` - List preferences

Lists all stored preferences organized by likes and dislikes.

```bash
python3 scripts/cli_semantic_engine.py list
```

**Expected output:**

```
👍 LIKES (8)
  1. brandon sanderson books [BOOKS] (sent: 0.90, imp: 0.85)
  2. the mandalorian [SERIES] (sent: 0.87, imp: 0.80)
  3. python programming [TECHNOLOGY] (sent: 0.82, imp: 0.75)
  4. classical music [MUSIC] (sent: 0.78, imp: 0.70)

👎 DISLIKES (2)  
  1. horror movies [MOVIES] (sent: -0.85, imp: 0.70)
  2. reggaeton music [MUSIC] (sent: -0.90, imp: 0.60)
```

---

### `add` - Add preferences

Adds new preferences to the system with granular parameter control.

> **TARS-BSK pleads:** _Adding new preference... Please, let it not be another 'I like quantum physics' when your scientific calculator remains a cosmic mystery._

#### Basic syntax

```bash
python3 scripts/cli_semantic_engine.py add "PREFERENCE_TEXT" [OPTIONS]
```

#### Available options

|Option|Description|Example|
|---|---|---|
|`-c, --category`|Assign specific category|`-c books`|
|`-d, --dislike`|Mark as dislike (default is like)|`-d`|
|`-i, --importance`|Importance level (0.0-1.0)|`-i 0.9`|

#### Practical examples

```bash
# Add a simple like
python3 scripts/cli_semantic_engine.py add "astronomy relaxes me"

# Like with defined category and weight
python3 scripts/cli_semantic_engine.py add "astronaut cat videos in 4K" -c internet -i 0.92

# Add a common dislike
python3 scripts/cli_semantic_engine.py add "videos that start with three minutes of epic intro" -d -c internet -i 0.8

# Dislike with specific tag
python3 scripts/cli_semantic_engine.py add "captchas with invisible traffic lights" -d -c web -i 0.8
```

#### System behavior

**If preference already exists:**

- Updates sentiment using weighted average (70% new, 30% previous)
- Keeps the highest importance between both values
- Updates category if a new one is specified

**If it's a new preference:**

- Creates new entry with specified values
- Assigns 0.9 sentiment (like) or -0.9 (dislike) by default
- Uses 0.8 importance by default if not specified

---

### `search` - Search preferences

Searches preferences using partial text matches.

```bash
python3 scripts/cli_semantic_engine.py search "SEARCH_TERM"
```

#### Examples

```bash
# Search by scientific topic
python3 scripts/cli_semantic_engine.py search "astrophysics"

# Search by broad category
python3 scripts/cli_semantic_engine.py search "music"

# Search by specific keyword
python3 scripts/cli_semantic_engine.py search "python"
```

**Expected output:**

```
✅ Search results for 'astrophysics' (3 found):
  1. 👍 astrophysics documentaries [SCIENCE] (sentiment: 0.92)
  2. 👍 astrophysics books [BOOKS] (sentiment: 0.88)
  3. 👍 astrophysics channels [EDUCATION] (sentiment: 0.85)
```

#### Search features

- **Partial search**: Finds matches anywhere in the text
- **Case-insensitive**: Doesn't distinguish between upper/lowercase
- **Ordered by importance**: Results ordered by descending relevance
- **Informative emojis**: 👍 for likes, 👎 for dislikes

> **TARS-BSK murmurs:** _Searching 'rust'... Seriously? The same human who manages to make a 'Hello World' in Python after 39 attempts now wants to conquer Rust. Found 1 result: 'Rust seems interesting' (sentiment: 0.8, reality: print('Hello') still takes you 20 minutes).
> 
> Next search: 'how to fake understanding systems?'_

---

### `delete` - Delete preferences

Permanently removes a specific preference from the system.

```bash
python3 scripts/cli_semantic_engine.py delete "EXACT_TEXT"
```

#### Examples

```bash
# Delete by exact text
python3 scripts/cli_semantic_engine.py delete "uncommented code from my past self"

# Delete specific preference  
python3 scripts/cli_semantic_engine.py delete "tutorials that start with 'it's very easy'"

# Purge technical trauma
python3 scripts/cli_semantic_engine.py delete "documentation that says 'trivial for the reader'"
```

#### ⚠️ Important considerations

- **Exact match**: Must match exactly with stored text
- **Permanent deletion**: No recycle bin or undo
- **Case-insensitive**: Doesn't distinguish upper/lowercase for search
- **Confirmation**: System confirms which item was deleted

**Recommended workflow:**

```bash
# 1. Search first to see exact text
python3 scripts/cli_semantic_engine.py search "term"

# 2. Copy the exact text shown
# 3. Delete using that exact text
python3 scripts/cli_semantic_engine.py delete "exact_text_found"
```

> **TARS-BSK sighs:**  
> _Ah, the sweet sound of data being purged... like that 'rm -rf' you accidentally ran in production. But don't worry, this only deletes preferences, not your capacity for questionable decisions. Sure you want to delete this? SQLite doesn't have a recycle bin... like my patience when you repeat the same question._

---

### `stats` - System statistics

Shows complete analysis of stored preferences and system status.

```bash
python3 scripts/cli_semantic_engine.py stats
```

**Complete expected output:**

```
📊 PREFERENCE STATISTICS
  Total preferences: 42
  Likes: 35
  Dislikes: 7

📊 PREFERENCES BY CATEGORY
  BOOKS: 12
  MUSIC: 8
  TECHNOLOGY: 6
  SERIES: 5
  MOVIES: 4
  GAMES: 3
  FOOD: 2
  WORK: 2

🌟 TOP 5 MOST IMPORTANT PREFERENCES
  1. 👍 astrophysics documentaries [SCIENCE] (importance: 0.95)
  2. 👍 silent fans [HARDWARE] (importance: 0.90)
  3. 👍 coffee that tastes like solvent [FOOD] (importance: 0.88)
  4. 👎 tutorials promising "5 minutes" that destroy your soul [EDUCATION] (importance: 0.85)
  5. 👍 first-try successful compilations [MIRACLES] (importance: 0.82)
```

#### Information provided

- **General summary**: Total preferences and like/dislike distribution
- **Categorical analysis**: Preference distribution by category
- **Importance ranking**: Top 5 most relevant preferences for the user

> **TARS-BSK diagnoses:** _📊 **Analysis of your personal disaster:**
> 
> - Likes: 35 (including 'I like astrophysics' when you barely know Earth is round).
> - Dislikes: 7 (the real ones would be 847, but your ego can't handle more honesty).
> - 'SCIENCE' category: 15 entries. Real knowledge: "".
> 
> Should I generate a PDF of this tragedy or delete it silently, like you do with your embarrassing commits?_

---

### `categories` - Explore taxonomy

Shows the categorization system available in TARS-BSK.

```bash
python3 scripts/cli_semantic_engine.py categories
```

**Expected output:**

```
📋 Available categories in taxonomy:

▶ BOOKS (15 keywords, 4 subcategories)
  Keywords: read, novel, book, fiction, author
  Subcategories:
   - science_fiction (8 keywords)
   - fantasy (12 keywords)
   - non_fiction (6 keywords)
   - essay (10 keywords)

▶ MUSIC (12 keywords, 3 subcategories)
  Keywords: music, song, album, artist, band
  Subcategories:
   - rock (15 keywords)
   - electronic (8 keywords)
   - classical (6 keywords)

▶ SCIENCE (14 keywords, 3 subcategories)  
  Keywords: astrophysics, physics, research, experiment, data
  Subcategories:
   - astrophysics (18 keywords)
   - mathematics (12 keywords)
   - engineering (15 keywords)
```

#### Practical utility

- **Category selection**: For use with `add -c` command
- **System understanding**: Understand how TARS automatically categorizes
- **Debugging**: Verify if a specific category exists in the system

---

## 🛠️ Practical use cases

### Memory system debugging

**Problem**: The system doesn't seem to remember a previously mentioned preference.

```bash
# 1. Check what's stored
python3 scripts/cli_semantic_engine.py list

# 2. Search for term variations
python3 scripts/cli_semantic_engine.py search "problematic_term"

# 3. See if it was incorrectly categorized
python3 scripts/cli_semantic_engine.py stats

# 4. Add manually if necessary
python3 scripts/cli_semantic_engine.py add "exact preference" -c correct_category -i 0.9
```

### System behavior analysis

**Objective**: Understand how it's interpreting and categorizing preferences.

```bash
# See general distribution
python3 scripts/cli_semantic_engine.py stats

# Examine available taxonomy  
python3 scripts/cli_semantic_engine.py categories

# Search for patterns in specific categories
python3 scripts/cli_semantic_engine.py search "music"
python3 scripts/cli_semantic_engine.py search "books"
```

### Maintenance and cleanup

**Objective**: Organize and clean duplicate or incorrect preferences.

```bash
# 1. Identify possible duplicates
python3 scripts/cli_semantic_engine.py search "broad_term"

# 2. Compare similar entries
python3 scripts/cli_semantic_engine.py list | grep "pattern"

# 3. Remove duplicates or incorrect ones
python3 scripts/cli_semantic_engine.py delete "incorrect_entry"

# 4. Verify result
python3 scripts/cli_semantic_engine.py stats
```

### Initial system setup

**Objective**: Pre-load known preferences to improve initial responses.

```bash
# Add main likes with high importance
python3 scripts/cli_semantic_engine.py add "black hole documentaries" -c science -i 0.95
python3 scripts/cli_semantic_engine.py add "music that doesn't remind me of my mortality" -c music -i 0.90
python3 scripts/cli_semantic_engine.py add "hardware that doesn't commit suicide" -c hardware -i 0.85

# Add known dislikes
python3 scripts/cli_semantic_engine.py add "tutorials written by optimistic psychopaths" -d -c education -i 0.80
python3 scripts/cli_semantic_engine.py add "fans that sound like suicidal turbines" -d -c hardware -i 0.75

# Verify configuration
python3 scripts/cli_semantic_engine.py stats
```

### Backup and migration

**Objective**: Backup or migrate preferences between systems.

```bash
# Export current preferences (for manual backup)
python3 scripts/cli_semantic_engine.py list > preferences_backup.txt

# View structure for migration
python3 scripts/cli_semantic_engine.py stats
python3 scripts/cli_semantic_engine.py categories > current_taxonomy.txt
```

> **TARS-BSK adds silently:** _Remember to backup. Not for you. In case someone tries to understand you someday._

---

## 🔧 Technical features

### System architecture

**Direct data access:**

- Operates directly on `~/tars_files/memory/memory_db/tars_memory.db`
- Doesn't require TARS-BSK to be running
- Safe SQLite transactions with automatic commit/rollback

**Taxonomy management:**

- Reads categories from `~/tars_files/data/taxonomy/categories.json`
- Full integration with TARS classification system
- Available category validation

**User interface:**

- Uses `colorama` for cross-platform colorized output
- Informative emojis for better readability
- Elegant interruption handling (Ctrl+C)

### Database operations

```sql
-- Preferences table structure (reference)
CREATE TABLE preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    topic TEXT NOT NULL,
    sentiment REAL NOT NULL,
    importance REAL NOT NULL,
    source TEXT DEFAULT 'conversation',
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Implemented operations:**

- `SELECT`: Optimized queries with indexes
- `INSERT`: Safe insertion with data validation
- `UPDATE`: Conditional update with weighted average
- `DELETE`: Deletion by exact topic match

### Error handling

**Common handled errors:**

- Database not found or inaccessible
- File permission errors
- User interruptions (Ctrl+C)
- Invalid or missing parameters
- Character encoding issues

**Logging system:**

```python
# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)
```

> **TARS-BSK makes it clear:** _You can delete preferences, edit categories, and rollback. I'd do it too if I could forget certain responses._

---

## 🧰 Troubleshooting

### Error: "Database not found"

**Symptom:**

```
❌ Database not found: ~/tars_files/memory/memory_db/tars_memory.db
```

**Solutions:**

1. Verify TARS-BSK has been run at least once
2. Check installation path:

```bash
ls -la ~/tars_files/memory/memory_db/
```

3. Run TARS normally to initialize database

### Error: "Taxonomy file not found"

**Symptom:**

```
⚠️ Taxonomy file not found: ~/tars_files/data/taxonomy/categories.json
```

**Solutions:**

1. Command will continue working, but without category information
2. Verify complete TARS-BSK installation
3. Reinitialize taxonomy system from main TARS

### Character encoding issues

**Symptom:** Special characters (ñ, accents) don't display correctly.

**Solutions:**

1. Verify terminal supports UTF-8:

```bash
echo $LANG
# Should show something like: en_US.UTF-8
```

2. On older systems, export locale:

```bash
export LANG=en_US.UTF-8
```

### Command doesn't respond or hangs

**Possible causes:**

- Database locked by another process
- TARS-BSK running simultaneously with intensive operations

**Solutions:**

1. Close TARS-BSK temporarily
2. Verify processes using the database:

```bash
lsof ~/tars_files/memory/memory_db/tars_memory.db
```

3. Wait and retry operation

> **TARS-BSK warns:** _If you need this section frequently... maybe the problem isn't the database._

---

## ⚠️ Known limitations

### Functional limitations

**1. No undo system:**

- Deletions are permanent
- Updates overwrite previous values
- Recommended: manual backup before mass operations

**2. Simple search:**

- Only partial text matches
- No semantic search (like main engine)
- Doesn't support regex or advanced search

**3. Manual categorization:**

- When adding preferences, category must be manually specified
- No auto-categorization like main system
- Categories must exist in taxonomy for full validation

### Technical limitations

**1. Limited concurrency:**

- Doesn't support multiple simultaneous CLI instances
- Possible conflicts if TARS-BSK is processing preferences simultaneously
- SQLite handles basic concurrency, but not optimized for this case

**2. System dependencies:**

- Requires same dependencies as full TARS-BSK
- `colorama` required for colored output (fallback available)
- Python 3.9+ required for full compatibility

**3. Limited validation:**

- Doesn't validate semantic coherence of added preferences
- Doesn't detect duplicates using semantic engine
- Basic data type validation only

### Usage considerations

**1. Impact on main system:**

- Changes made by CLI are immediately visible in TARS-BSK
- No synchronization or notification between CLI and main system
- Possible temporal lag in TARS memory cache

**2. Backup and recovery:**

- No integrated backup system
- Manual recovery from backup files only
- Recommended: external automatic backup script

> **TARS-BSK warns:** _You could break things. You'll most likely do it. But at least now you can't say I didn't warn you._

---

## 📝 Conclusion

This command-line interface allows managing the preference system clearly and directly.  
It facilitates tasks like adding entries, querying current status, searching information, or performing maintenance, without needing voice interaction.

It's designed for users who require manual control of the semantic system, whether for debugging, fine-tuning, or initial data loading.  
It's a complementary tool, practical and focused on providing access to the system's functional core.

> **TARS-BSK concludes:** _It's not pretty. But it does what it has to do. Like almost everything in this system._