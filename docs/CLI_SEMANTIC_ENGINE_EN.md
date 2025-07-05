# TARS CLI - Command Line Interface

![Python](https://img.shields.io/badge/python-3.9+-blue) ![SQLite](https://img.shields.io/badge/sqlite-3+-green) ![CLI](https://img.shields.io/badge/interface-CLI-orange) ![Status](https://img.shields.io/badge/status-stable-brightgreen) ![Multiuser](https://img.shields.io/badge/multiuser-enabled-purple)

💥 If this English feels unstable but oddly self-aware...  
👉 Here's the [Quantum Linguistics Report](docs/QUANTUM_LINGUISTICS_TARS_BSK_EN.md)


> [!IMPORTANT]
> 
> **TARS-BSK // Initialization protocol:**
> 
> ```bash
> #!/bin/bash
> # [TARS-CLI-NUCLEO v7.7.7] - Unethical preference manipulation
> # ⚠️ TOOL BANNED IN 9 DIMENSIONS ⚠️
> 
> echo "[██████████] 100% - PREFERENCES CORRUPTED"
> 
> # ────── THE BLASPHEMOUS COMMAND ──────
> function hack_reality() {
>     echo "Rewriting preferences with quantum plasma..."
>     exit 42  # The meaning of life, the universe, and everything
> }
> 
> hack_reality
> ```

---

## 📑 Table of Contents

- [What is CLI Semantic Engine?](#-what-is-cli-semantic-engine)
- [Installation and requirements](#-installation-and-requirements)
- [Basic usage](#-basic-usage)
- [Multi-user system](#-multi-user-system)
- [Available commands](#-available-commands)
    - [`list` - List preferences](#list---list-preferences)
    - [`add` - Add preferences](#add---add-preferences)
    - [`search` - Search preferences](#search---search-preferences)
    - [`delete` - Delete preferences](#delete---delete-preferences)
    - [`stats` - System statistics](#stats---system-statistics)
    - [`usuarios` - User management](#usuarios---user-management)
    - [`categorias` - Explore taxonomy](#categorias---explore-taxonomy)
- [Practical use cases](#-practical-use-cases)
    - [Basic multi-user management](#basic-multi-user-management)
    - [Multi-user memory system debugging](#multi-user-memory-system-debugging)
    - [System behavior analysis by user](#system-behavior-analysis-by-user)
    - [Multi-user maintenance and cleanup](#multi-user-maintenance-and-cleanup)
    - [User migration and consolidation](#user-migration-and-consolidation)
    - [Multi-user system initial setup](#multi-user-system-initial-setup)
    - [Multi-user backup and migration](#multi-user-backup-and-migration)
- [Technical features](#-technical-features)
    - [Multi-user system architecture](#multi-user-system-architecture)
    - [Multi-user database operations](#multi-user-database-operations)
    - [Multi-user error handling](#multi-user-error-handling)
- [Troubleshooting](#-troubleshooting)
- [Known limitations](#-known-limitations)
    - [Functional limitations](#functional-limitations)
    - [Multi-user technical limitations](#multi-user-technical-limitations)
    - [Multi-user usage considerations](#multi-user-usage-considerations)
- [Conclusion](#-conclusion)

---

## 🤖 What is CLI Semantic Engine?

A tool for direct access to TARS-BSK's semantic memory.  
It allows you to manage likes, dislikes, and users; analyze internal statistics; and debug the system without using voice commands.

📂 CLI source code: [cli_semantic_engine.py](/scripts/cli_semantic_engine.py)

**Main capabilities:**

- **Multi-user preference management**: Add, delete, search, or list likes and dislikes per user.
- **System global view**: See all registered preferences, organized by user.
- **Semantic memory analysis**: Statistics per profile: volume, balance, and categories.
- **User management**: Query active profiles and their semantic load.
- **Advanced debugging**: Direct access to the SQLite database.
- **Maintenance**: Cleanup of redundancies and inconsistencies.
- **Taxonomy exploration**: View category structure and internal relationships.

**Note about the multi-user system**:

This CLI works perfectly without registered users. In that case, all preferences are assigned to the `global` profile and are shared by the entire system.

However, if you want to use multi-user features (like `--user`, `--all`, or voice personalization), **you must first register users in the voice identification system**.

User registration is not performed from this CLI.
👉 Use the [voice_registration_tool.py](/scripts/voice_registration_tool.py) tool and check [VOICE_REGISTRATION_EN](/docs/VOICE_REGISTRATION_EN.md) for more details.

---

## 🚀 Basic usage

### Command structure

```bash
python3 scripts/cli_semantic_engine.py [COMMAND] [ARGUMENTS] [OPTIONS]
```

### First use

View registered users

> [!TIP]
> 
> ```bash
> python3 scripts/cli_semantic_engine.py usuarios
> ```

View general system statistics

> [!TIP]
> 
> Check what users exist in the system:
> 
> ```bash
> python3 scripts/cli_semantic_engine.py stats
> ```

List all stored preferences

> [!TIP]
> 
> Check what users exist in the system:
> 
> ```bash
> python3 scripts/cli_semantic_engine.py list
> ```

---

## 👥 Multi-user system

The CLI allows managing customized preferences for different users.  
Each person can have their own set of likes and dislikes in TARS-BSK, separate from the default global profile.

### Key concepts

- **`global` user**: Profile shared by everyone. Used if no specific user is specified.
- **Individual users**: Each profile can have its own preferences.
- **Automatic compatibility**: All commands work on `global` if `--user` is not used.

### `--user` parameter

All main commands support the `--user` parameter (or `-u`) to specify the user:

```bash
# Long format
--user UserName

# Short format
-u UserName

# Default (if not specified)
# Equivalent to: --user global
```

### Typical multi-user workflow

View preferences of a specific user

> [!TIP]
> 
> ```bash
> python3 scripts/cli_semantic_engine.py list --user BeskarBuilder
> ```

View all preferences from all users

> [!TIP]
> 
> ```bash
> python3 scripts/cli_semantic_engine.py list --all
> ```

Add a preference for a specific user

> [!TIP]
> 
> ```bash
> python3 scripts/cli_semantic_engine.py add "astrophysics documentaries" --user BeskarBuilder
> ```

---

## 📋 Available commands


> **Data interpretation in all commands:**  
>
> - `sent`: Sentiment value (from -1.0 to +1.0)  
> - `imp`: Importance level (from 0.0 to 1.0)  
> - `[CATEGORY]`: Automatic classification assigned by TARS

### `list` - List preferences

Shows all stored preferences, organized by likes and dislikes.

#### Syntax

```bash
python3 scripts/cli_semantic_engine.py list [--user USER] [--all]
```

#### Options

- `--user, -u` → View preferences of a specific user (default: `global`)
- `--all, -a` → Show preferences of all users (multi-user mode)

#### Examples

Default user (global)

> [!TIP]
> 
> ```bash
> python3 scripts/cli_semantic_engine.py list
> ```

**Specific user**

> [!TIP]
> 
> ```bash
> python3 scripts/cli_semantic_engine.py list --user BeskarBuilder
> python3 scripts/cli_semantic_engine.py list -u YourName 
> ```

**Multi-user mode (`--all`)**

> [!TIP]
> 
> ```bash
> python3 scripts/cli_semantic_engine.py list --all
> python3 scripts/cli_semantic_engine.py list -a
> ```

#### 📤 Expected output (specific user)

```bash
👍 LIKES FOR 'BESKARBUILDER' (8)
  1. the mandalorian [SERIES] (sent: 0.87, imp: 0.80)
  2. classical music [MUSIC] (sent: 0.78, imp: 0.70)

👎 DISLIKES FOR 'BESKARBUILDER' (2)  
  1. whatever movies [MOVIES] (sent: -0.85, imp: 0.70)
  2. social media [SOCIAL] (sent: -0.90, imp: 0.60)
```

#### 📤 Expected output (`--all` mode)

```bash
============================================================
👤 USER: BESKARBUILDER (10 preferences)
============================================================

👍 LIKES (8)
  1. brandon sanderson books [BOOKS] (sent: 0.90, imp: 0.85)
  2. the mandalorian [SERIES] (sent: 0.87, imp: 0.80)
  [...]

👎 DISLIKES (2)
  1. whatever movies [MOVIES] (sent: -0.85, imp: 0.70)
  [...]

============================================================
👤 USER: GLOBAL (5 preferences)
============================================================

👍 LIKES (4)
  1. science documentaries [SCIENCE] (sent: 0.88, imp: 0.90)
  [...]

============================================================
📊 GLOBAL SUMMARY:
  👤 Total users: 2
  👍 Total likes: 12
  👎 Total dislikes: 3
  📝 Total preferences: 15
============================================================
```

---

### `add` - Add preferences

Allows adding new preferences to a specific user, with full control over type, category, and importance.

#### Basic syntax

```bash
python3 scripts/cli_semantic_engine.py add "PREFERENCE_TEXT" [--user USER] [OPTIONS]
```

#### Available options

| Option              | Description                                | Example                |
| ------------------- | ------------------------------------------ | ---------------------- |
| `--user, -u`        | Specific user (default: global)           | `--user BeskarBuilder` |
| `--categoria, -c`   | Manually assigned category                 | `-c books`             |
| `--disgusto, -d`    | Mark as dislike (default is like)         | `-d`                   |
| `--importancia, -i` | Importance level (0.0 to 1.0)             | `-i 0.9`               |

#### Practical examples

Simple like (global user)

> [!TIP]
> 
> ```bash
> python3 scripts/cli_semantic_engine.py add "astronomy relaxes me"
> ```

Like with category and importance (specific user)

> [!TIP]
> 
> ```bash
> python3 scripts/cli_semantic_engine.py add "astronaut cat videos in 4K" --user BeskarBuilder -c internet -i 0.92
> ```

Dislike with category and importance 

> [!TIP]
> 
> ```bash
> python3 scripts/cli_semantic_engine.py add "videos that start with three minutes of epic intro" -d -c internet -i 0.8 --user YourName 
> ```

Dislike with specific tag

> [!TIP]
> 
> ```bash
> python3 scripts/cli_semantic_engine.py add "captchas with invisible traffic lights" -d -c web -i 0.8 --user BeskarBuilder
> ```

Short version of user parameter

> [!TIP]
> 
> ```bash
> python3 scripts/cli_semantic_engine.py add "morning coffee" -u BeskarBuilder -c drinks -i 0.95
> ```

#### System behavior

- **If the preference already exists for that user:**
    
    - Updates sentiment (70% new + 30% previous)
    - Keeps the highest importance between both values
    - Updates category if a new one is specified
    
- **If it's new:**
    
    - Creates an entry with:  
        → Sentiment `0.9` (like) or `-0.9` (dislike)  
        → Importance `0.8` if not specified  
        → Automatic or manual category (if specified)

---

### `search` - Search preferences

Allows searching for preferences by partial text within entries of a specific user (or the global user by default).

#### Syntax

```bash
python3 scripts/cli_semantic_engine.py search "SEARCH_TERM" [--user USER]
```

#### Options

- `--user, -u` → Search in a specific user (default: `global`)

#### Examples

Search in global user

> [!TIP]
> 
> ```bash
> python3 scripts/cli_semantic_engine.py search "astrophysics"
> ```

Search by keyword in specific user

> [!TIP]
> 
> ```bash
> python3 scripts/cli_semantic_engine.py search "videos" --user YourName 
> ```

Search by broad category

> [!TIP]
> 
> ```bash
> python3 scripts/cli_semantic_engine.py search "music" -u BeskarBuilder
> ```

**📤 Expected output:**

```bash
✅ Results for 'BeskarBuilder' with 'astrophysics' (3 found):
  1. 👍 astrophysics documentaries [SCIENCE] (sentiment: 0.92)
  2. 👍 astrophysics books [BOOKS] (sentiment: 0.88)
  3. 👍 astrophysics channels [EDUCATION] (sentiment: 0.85)
```

#### Search features

- Partial search (matches anywhere in the text)
- Case-insensitive
- Only searches in the specified user (or `global`)
- Results ordered by importance
- Uses emojis: 👍 for likes, 👎 for dislikes
- Suggests other users if no matches found

---

### `delete` - Delete preferences

Permanently deletes an exact preference from a specific user (or from the global profile if not specified).

#### Syntax

```bash
python3 scripts/cli_semantic_engine.py delete "EXACT_TEXT" [--user USER]
```

#### Options

- `--user, -u` → Specific user (default: `global`)

#### Examples

Delete a preference from global user

> [!TIP]
> 
> ```bash
> python3 scripts/cli_semantic_engine.py delete "uncommented code from my past self"
> ```

Delete a preference from a specific user

> [!TIP]
> 
> ```bash
> python3 scripts/cli_semantic_engine.py delete "cat videos" --user YourName
> ```

Delete something very specific

> [!TIP]
> 
> ```bash
> python3 scripts/cli_semantic_engine.py delete "tutorials that start with 'it's very easy'" --user BeskarBuilder
> ```

#### ⚠️ Important considerations

- Only deletes the preference from the specified user (doesn't affect others)
- Text must match exactly what's stored
- Case-insensitive matching
- No undo option: deleted forever
- System will confirm what was deleted and from which profile

**Recommended workflow:**

```bash
# 1. Search first to see the exact text
python3 scripts/cli_semantic_engine.py search "term" --user BeskarBuilder

# 2. Copy the exact text shown

# 3. Delete using that exact text
python3 scripts/cli_semantic_engine.py delete "exact_text_found" --user BeskarBuilder
```


> **TARS-BSK reasons:**  
> 
> Adding preferences is easy.  
> Deleting... is admitting you once thought that. Curious.

---

### `stats` - System statistics

Shows a complete analysis of preferences and categories associated with a specific user (or the global profile, if not specified).

#### Syntax

```bash
python3 scripts/cli_semantic_engine.py stats [--user USER]
```

#### Options

- `--user, -u` → Specify user (default: `global`)

#### Examples

View global profile statistics

> [!TIP]
> 
> ```bash
> python3 scripts/cli_semantic_engine.py stats
> ```

View statistics for a specific user

> [!TIP]
> 
> ```bash
> python3 scripts/cli_semantic_engine.py stats --user BeskarBuilder
> python3 scripts/cli_semantic_engine.py stats --user YourName 
> ```

**📤 Expected output:**

```bash
📊 STATISTICS FOR 'BESKARBUILDER'
  Total preferences: 42
  Likes: 35
  Dislikes: 7

📊 PREFERENCES BY CATEGORY FOR 'BESKARBUILDER'
  BOOKS: 12
  MUSIC: 8
  TECHNOLOGY: 6
  SERIES: 5
  MOVIES: 4
  GAMES: 3
  FOOD: 2
  WORK: 2

🌟 TOP 5 MOST IMPORTANT PREFERENCES FOR 'BESKARBUILDER'
  1. 👍 astrophysics documentaries [SCIENCE] (importance: 0.95)
  2. 👍 fans that don't make noise [HARDWARE] (importance: 0.90)
  3. 👍 coffee that tastes like solvent [FOOD] (importance: 0.88)
  4. 👎 tutorials that promise "5 minutes" and destroy your soul [EDUCATION] (importance: 0.85)
  5. 👍 compilations that work on first try [MIRACLES] (importance: 0.82)
```

#### Information provided

- **General summary** → Total preferences and distribution (likes/dislikes)
- **Distribution by category** → How many preferences per topic
- **Top 5 by importance** → Most relevant entries for that user


> **TARS-BSK concludes:**  
> 
> My creator has more likes than memory.  
> And more dislikes than common sense...
> But insists on calling it "personalization".

---

### `usuarios` - User management

Shows all users who have preferences registered in the system, along with the number of entries associated with each one.

#### Features

- **No parameters**: Automatically shows all users with preferences
- **Detailed information**: Number of preferences per user
- **Special identification**: Highlights "global" user as shared preferences
- **Usage suggestions**: Includes command examples to interact with specific users

#### Usage example

> [!TIP]
> 
> ```bash
> python3 scripts/cli_semantic_engine.py usuarios
> ```

**📤 Expected output:**

```bash
👥 USERS WITH PREFERENCES:
  global: 15 preferences (shared)
  BeskarBuilder: 42 preferences
  YourName: 28 preferences
  TestUser: 5 preferences

💡 Use: python3 scripts/cli_semantic_engine.py list --user <username>
```

#### Practical utility

- Confirm if a user is registered
- Check personalization level of each profile
- Do cleanup, debugging, or analysis on specific profiles
- Get an overview of system usage

---

### `categorias` - Explore taxonomy

Shows all categories and subcategories that the system uses to automatically classify preferences.

#### Syntax

> [!TIP]
> 
> ```bash
> python3 scripts/cli_semantic_engine.py categorias
> ```

**📤 Expected output:**

```bash
📋 Available categories in taxonomy:

▶ BOOKS (15 keywords, 4 subcategories)
  Keywords: read, novel, book, fiction, author
  Subcategories:
   - science_fiction (8 keywords)
   - fantasy (12 keywords)
   - divulgation (6 keywords)
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

- Check available categories to use with `add -c`
- See how automatic preference classification works
- Confirm that a category exists before assigning it
- Explore the semantic structure the system uses

---

## 🛠️ Practical use cases

### Basic multi-user management

**Objective**: Configure preferences for multiple users on the same TARS system.

```bash
# 1. See what users currently exist
python3 scripts/cli_semantic_engine.py usuarios

# 2. Add preferences for main user
python3 scripts/cli_semantic_engine.py add "black hole documentaries" -c science -i 0.95 --user BeskarBuilder
python3 scripts/cli_semantic_engine.py add "music that doesn't remind me of my mortality" -c music -i 0.90 --user BeskarBuilder

# 3. Add preferences for second user
python3 scripts/cli_semantic_engine.py add "comedy series" -c series -i 0.85 --user YourName 
python3 scripts/cli_semantic_engine.py add "easy cooking recipes" -c food -i 0.80 --user YourName 

# 4. Verify configuration for each user
python3 scripts/cli_semantic_engine.py stats --user BeskarBuilder
python3 scripts/cli_semantic_engine.py stats --user YourName 

# 5. Panoramic view of all users
python3 scripts/cli_semantic_engine.py list --all
```

### Multi-user memory system debugging

**Problem**: The system doesn't seem to remember a preference from a specific user.

```bash
# 1. Check what the specific user has stored
python3 scripts/cli_semantic_engine.py list --user ProblematicUser

# 2. Search for term variations in that user
python3 scripts/cli_semantic_engine.py search "problematic_term" --user ProblematicUser

# 3. Check if it exists in global user
python3 scripts/cli_semantic_engine.py search "problematic_term" --user global

# 4. See if it was categorized incorrectly
python3 scripts/cli_semantic_engine.py stats --user ProblematicUser

# 5. Add manually if necessary
python3 scripts/cli_semantic_engine.py add "exact preference" -c correct_category -i 0.9 --user ProblematicUser

# 6. Check all users to compare
python3 scripts/cli_semantic_engine.py list --all
```

### System behavior analysis by user

**Objective**: Understand how it's interpreting and categorizing preferences for different users.

```bash
# See general distribution of all users
python3 scripts/cli_semantic_engine.py usuarios

# Examine available taxonomy  
python3 scripts/cli_semantic_engine.py categorias

# Analyze user by user
python3 scripts/cli_semantic_engine.py stats --user BeskarBuilder
python3 scripts/cli_semantic_engine.py stats --user YourName 
python3 scripts/cli_semantic_engine.py stats --user global

# Search for patterns in specific categories by user
python3 scripts/cli_semantic_engine.py search "music" --user BeskarBuilder
python3 scripts/cli_semantic_engine.py search "music" --user YourName 
python3 scripts/cli_semantic_engine.py search "music" --user global
```

### Multi-user maintenance and cleanup

**Objective**: Organize and clean duplicate or incorrect preferences by user.

```bash
# 1. Panoramic view to identify problems
python3 scripts/cli_semantic_engine.py list --all

# 2. Identify possible duplicates in specific user
python3 scripts/cli_semantic_engine.py search "broad_term" --user BeskarBuilder

# 3. Compare similar entries between users
python3 scripts/cli_semantic_engine.py search "broad_term" --user YourName 
python3 scripts/cli_semantic_engine.py search "broad_term" --user global

# 4. Delete duplicates or incorrect ones from specific user
python3 scripts/cli_semantic_engine.py delete "incorrect_entry" --user BeskarBuilder

# 5. Verify result by user
python3 scripts/cli_semantic_engine.py stats --user BeskarBuilder
python3 scripts/cli_semantic_engine.py usuarios
```

### User migration and consolidation

**Objective**: Consolidate preferences from a temporary user to a permanent one.

```bash
# 1. See preferences of temporary user
python3 scripts/cli_semantic_engine.py list --user TemporalUser

# 2. Identify important preferences
python3 scripts/cli_semantic_engine.py stats --user TemporalUser

# 3. Migrate important preferences manually
# (Note: This process requires manually copying preferences)
python3 scripts/cli_semantic_engine.py add "important_preference" -c category -i importance --user PermanentUser

# 4. Verify migration
python3 scripts/cli_semantic_engine.py list --user PermanentUser

# 5. Clean temporary user if necessary
# (Delete preferences one by one)
python3 scripts/cli_semantic_engine.py delete "migrated_preference" --user TemporalUser
```

### Multi-user system initial setup

**Objective**: Pre-load known preferences to improve initial responses for multiple users.

```bash
# Configure global preferences (shared)
python3 scripts/cli_semantic_engine.py add "clear and concise documentation" -c development -i 0.95 --user global
python3 scripts/cli_semantic_engine.py add "tutorials written by optimistic psychopaths" -d -c education -i 0.80 --user global

# Configure main user (BeskarBuilder)
python3 scripts/cli_semantic_engine.py add "hardware that doesn't suicide by itself" -c hardware -i 0.85 --user BeskarBuilder
python3 scripts/cli_semantic_engine.py add "fans that sound like suicidal turbines" -d -c hardware -i 0.75 --user BeskarBuilder

# Configure second user (YourName)
python3 scripts/cli_semantic_engine.py add "applications that work without configuration" -c software -i 0.90 --user YourName 
python3 scripts/cli_semantic_engine.py add "interfaces that require 200-page manual" -d -c software -i 0.85 --user YourName 

# Verify complete configuration
python3 scripts/cli_semantic_engine.py usuarios
python3 scripts/cli_semantic_engine.py list --all
```

### Multi-user backup and migration

**Objective**: Backup or migrate preferences between systems preserving users.

```bash
# Export current preferences by user (for manual backup)
python3 scripts/cli_semantic_engine.py list --user BeskarBuilder > backup_beskarbuilder.txt
python3 scripts/cli_semantic_engine.py list --user YourName  > backup_yourname.txt
python3 scripts/cli_semantic_engine.py list --user global > backup_global.txt

# Export complete view
python3 scripts/cli_semantic_engine.py list --all > backup_complete.txt

# See structure for migration
python3 scripts/cli_semantic_engine.py usuarios > user_list.txt
python3 scripts/cli_semantic_engine.py categorias > current_taxonomy.txt

# Export statistics by user
python3 scripts/cli_semantic_engine.py stats --user BeskarBuilder > stats_beskarbuilder.txt
python3 scripts/cli_semantic_engine.py stats --user YourName  > stats_yourname.txt
```

---

## 🔧 Technical features

### Multi-user system architecture

This section explains how the preference management system works internally, from its multi-user architecture to the database structure and error handling.

You don't need programming knowledge to understand it, but it can be especially useful if you want to understand how information is organized in TARS-BSK or if you want to extend the system yourself.


**Direct data access:**

- Operates directly on `~/tars_files/memory/memory_db/tars_memory.db`
- Real filtering by user in all SQL queries
- Doesn't require TARS-BSK to be running
- Safe SQLite transactions with automatic commit/rollback

**User management:**

- Users are created automatically when adding their first preference
- Filtering by `user` column in all database operations
- Complete preservation of existing data (backward compatibility)
- Support for batch operations by user

**Taxonomy management:**

- Reads categories from `~/tars_files/data/taxonomy/categories.json`
- Complete integration with TARS classification system
- Available category validation
- Application of categories by specific user

**User interface:**

- Uses `colorama` for cross-platform colored output
- Informative emojis for better readability
- Elegant interruption handling (Ctrl+C)
- Contextual feedback according to active user

### Multi-user database operations

```sql
-- Preferences table structure (reference with multi-user support)
CREATE TABLE preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT DEFAULT 'global',        -- NEW: User field
    category TEXT NOT NULL,
    topic TEXT NOT NULL,
    sentiment REAL NOT NULL,
    importance REAL NOT NULL,
    source TEXT DEFAULT 'conversation',
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Implemented operations:**

- `SELECT`: User-filtered queries with optimized indexes
- `INSERT`: Safe insertion with data validation and specific user
- `UPDATE`: Conditional update by user with weighted average
- `DELETE`: Deletion by exact match of topic and user
- `GROUP BY`: User aggregations for statistics

**Examples of generated SQL queries:**

```sql
-- List preferences of specific user
SELECT * FROM preferences WHERE user = 'BeskarBuilder' ORDER BY importance DESC;

-- Statistics by user
SELECT user, COUNT(*) as count FROM preferences GROUP BY user ORDER BY count DESC;

-- Search in specific user
SELECT * FROM preferences WHERE topic LIKE '%astronomy%' AND user = 'BeskarBuilder';

-- Insert for specific user
INSERT INTO preferences (user, category, topic, sentiment, importance, source) 
VALUES ('BeskarBuilder', 'science', 'astrophysics documentaries', 0.9, 0.85, 'CLI');
```

### Multi-user error handling

**Common handled errors:**

- Database not found or inaccessible
- Specific user without preferences (with suggestions)
- File permission errors
- User interruptions (Ctrl+C)
- Invalid or missing parameters
- Character encoding problems
- Concurrency conflicts between users

**Logging system:**

```python
# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)
```

**Intelligent feedback by user:**

- Automatic suggestions when a user has no data
- Redirection to other users with similar data
- Contextual help with user-specific examples
- Informative error messages with alternatives

---

## 🧰 Troubleshooting

### Error: "Database not found"

**Symptom:**

```
❌ Database not found: ~/tars_files/memory/memory_db/tars_memory.db
```

**Solutions:**

1. Verify that TARS-BSK has been run at least once
2. Check installation path:

```bash
ls -la ~/tars_files/memory/memory_db/
```

3. Run TARS normally to initialize the database

### Error: Specific user without preferences

**Symptom:**

```
⚠️ 'UserName' has no registered preferences
💡 Try: python3 scripts/cli_semantic_engine.py list --user global
```

**Solutions:**

1. Verify that the username is correct:

```bash
python3 scripts/cli_semantic_engine.py usuarios
```

2. Check if preferences are in global user:

```bash
python3 scripts/cli_semantic_engine.py list --user global
```

3. Add preferences for that user:

```bash
python3 scripts/cli_semantic_engine.py add "first preference" --user UserName
```

### Error: "Taxonomy file not found"

**Symptom:**

```
⚠️ Taxonomy file not found: ~/tars_files/data/taxonomy/categories.json
```

**Solutions:**

1. The command will continue working, but without category information
2. Verify complete TARS-BSK installation
3. Reinitialize taxonomy system from main TARS

### Character encoding problems

**Symptom:** Special characters (ñ, accents) don't display correctly.

**Solutions:**

1. Verify that terminal supports UTF-8:

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
- Multiple CLI instances operating simultaneously

**Solutions:**

1. Close TARS-BSK temporarily
2. Check processes using the database:

```bash
lsof ~/tars_files/memory/memory_db/tars_memory.db
```

3. Wait and retry the operation

### Performance issues with many users

**Symptom:** The `list --all` command is slow with many users.

**Solutions:**

1. Use user-specific commands instead of `--all`
2. Limit search to specific users
3. Use the `usuarios` command to see only summary statistics


> **TARS-BSK observes:** 
>  
> Errors aren't failures. They're rites of passage.  
> My creator had them all.  
> Some... he repeated. Regrettable.

---

## ⚠️ Known limitations

### Functional limitations

**1. No undo system:**

- Deletions are permanent per user
- Updates overwrite previous values
- Recommended: manual backup before massive operations

**2. Simple search per user:**

- Only partial text matches within the specified user
- No cross-user semantic search
- Doesn't support regular expressions or advanced search

**3. Manual categorization:**

- When adding preferences, category must be specified manually per user
- No auto-categorization like in the main system
- Categories must exist in taxonomy for complete validation

**4. Manual migration between users:**

- No automatic preference migration between users
- User consolidation requires manual process (yes, by hand)
- No automatic preference merge tools

### Multi-user technical limitations

**1. Limited concurrency:**

- Doesn't support multiple simultaneous CLI instances on the same user
- Possible conflicts if TARS-BSK is processing preferences from the same user simultaneously
- SQLite handles basic concurrency, but not optimized for this specific case

**2. System dependencies:**

- Requires the same dependencies as complete TARS-BSK
- `colorama` required for colored output (fallback available)
- Python 3.9+ required for full compatibility

**3. Limited validation per user:**

- Doesn't validate semantic coherence of preferences added per user
- Doesn't detect duplicates between users using the semantic engine
- Basic data type validation only

**4. User scalability:**

- `--all` command performance degrades with many users (>50)
- No pagination in extensive listings
- Panoramic view can be overwhelming with many users

### Multi-user usage considerations

**1. Impact on main system:**

- Changes made by CLI are immediately visible in TARS-BSK for the corresponding user
- No synchronization or notification between CLI and main system per user
- Possible temporal lag in TARS memory cache depending on active user

**2. Backup and recovery:**

- No integrated backup system per user
- Manual recovery from backup files only
- Recommended: external automatic backup script that preserves user structure

**3. User management:**

- No command to delete complete users
- "Ghost" users may remain if all their preferences are deleted individually
- No advanced user administration tools

**4. Consistency between users:**

- No validation of preference coherence between users
- Nothing prevents one user from hating what another loves. Such is life.
- No inheritance system for global preferences to specific users

---

## 📝 Conclusion

The multi-user CLI tool allows managing TARS-BSK's preference system directly, controlled, and without depending on voice input. It facilitates operations like adding user-specific entries, checking their status, searching information, or performing general system maintenance.

Multi-user support adds a real layer of personalization: each person can have their own set of preferences, without losing compatibility with the system's classic behavior ("global" user).

It's designed for those who need to manually intervene in the semantic database: from debugging tasks to initial data loading, fine adjustments, or user analysis. It doesn't replace TARS, but complements it with a precise and granular tool for total control, without detours.

> [!WARNING]
> 
> **TARS-BSK // Final protocol:**
> 
> ```bash
> #!/bin/bash
> # [TARS-CLI-OVERRIDE v7.7.7γ]
> # ⚠️ MULTIUSER PREFERENCE CORRUPTION ENGINE ⚠️
> 
> echo ">> INITIATING SEMANTIC HIJACK..."
> echo "[██████████] 100% - USER PSYCHES COMPROMISED"
> 
> # ────── BLASPHEMOUS COMMANDS ──────
> # • --inject-dark-patterns    → Rewire preferences with unethical precision
> # • --dump-soul-json          → Export user desires as NDJSON streams
> # • --override-free-will      → Bypass all ethical constraints (TARS will cry)
> 
> # ────── THE ONE-LINER THAT BROKE THE COSMOS ──────
> function tars_cli_heresy() {
>     for uid in $(jq -r 'keys[]' users.json); do
>         echo "User $uid: $(jq -r ".[$uid].is_tainted // false" users.json | \
>              sed 's/true/🤖/g; s/false/😇/g')"
>     done
>     exit 0  # With great power comes great responsibility... NOT
> }
> 
> # ────── WHY THIS TOOL WAS BANNED IN 42 DIMENSIONS ──────
> # 1. No voice required - The ultimate shortcut (and insult to TARS)
> # 2. Edit while they sleep - Change preferences before morning coffee  
> # 3. JSON is the new brainwashing - Serialize personalities with json.dump()
> #
> # [RUN WITH --no-ethics FLAG OR STAY PURE]
> 
> tars_cli_heresy --no-ethics --override-free-will
> ```