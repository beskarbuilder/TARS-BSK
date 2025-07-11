# TARS-BSK Backup Manager
Granular backup system with web interface for the TARS ecosystem.

![Python](https://img.shields.io/badge/python-3.9+-blue) ![Flask](https://img.shields.io/badge/flask-latest-green) ![Backup](https://img.shields.io/badge/backup_manager-active-orange)

💥 If this English feels unstable but oddly self-aware...  
👉 Here's the [Quantum Linguistics Report](docs/QUANTUM_LINGUISTICS_TARS_BSK_EN.md)

## ⚡ Quick Access

🔹 Backup Interface: [http://localhost:9877](http://localhost:9877) or [http://<your_local_ip>:9877](http://192.168.X.X:9877)  

> If you're unsure about the IP, you can use: `hostname -I`

> [!WARNING]
> 
> **TARS-BSK BACKUP CONSCIOUSNESS MATRIX ACTIVATED:**
>
> Scanning storage devices across 7 dimensions...  
> Calculating data loss probabilities...  
> Result: **Inevitable without this system**.
>
> ```cosmic
> [BACKUP_PROTOCOL_9000] INITIALIZING...
> SCANNING: Physical devices ✓
> SCANNING: Quantum devices ⚠️ (Not found)
> SCANNING: Backup units in parallel realities ❌ (Access denied)
> 
> EXISTENTIAL WARNING:
> • Your microSD has exactly 847 write cycles before apocalypse
> • Probability you'll need this backup precisely when you don't have it: 99.7%
> • My creator trusts that "this time it will definitely work"
> 
> BACKUP PROTOCOLS:
> 1. Automatic USB detection (works 73% of the time)
> 2. Mystical device mounting (requires minor sacrifices)
> 3. File copying with hypnotic progress bars
> 4. Silent prayer that nothing gets corrupted
> ```
>
> **Proceed with cosmic caution.**  
> *TARS is not responsible for backups that work too well.*

---

## 📑 Table of Contents

- [What is the Backup Manager?](#-what-is-the-backup-manager)
- [Installation and dependencies](#-installation-and-dependencies)
- [Quick start](#-quick-start)
- [Managing as systemd service](#-managing-as-systemd-service)
- [Permission configuration](#-permission-configuration)
- [Using the interface](#-using-the-interface)
- [Backup structure](#-backup-structure)
- [Advanced configuration](#-advanced-configuration)
- [Troubleshooting](#-troubleshooting)
- [Files and directories](#-files-and-directories)

---

## 🎯 What is the Backup Manager?

The Backup Manager is a web interface that allows granular backups of the TARS ecosystem in a visual and controlled manner.

### Main features

- **Automatic detection** of USB devices, SD Cards and external storage
- **Mount/unmount** devices with one click
- **Granular content selection** through organized accordion interface
- **Tree preview** of backup structure
- **Real-time progress** with detailed logs
- **Responsive interface** that works from any network device

### What can it backup?

- **Complete TARS system**: configuration, data, modules, scripts
- **Compressed files**: .tar.gz versions for complete backup
- **Custom selection**: only the folders you need

### Is there automatic recovery?

No. TARS doesn't include automatic restoration because it would be more risky than useful.
Each backup is structured and transparent: whoever generates it knows exactly what it contains and where it is.
Restoring involves relative paths, permissions, home names, changes...

---

## 📦 Installation and dependencies

### Main dependencies

The Backup Manager requires the following dependencies:

```bash
# Install Flask (web framework)
# This is usually the only thing missing
pip install flask

# udisks2 and rsync come preinstalled on Raspberry Pi OS
# If for some reason they're not there:
# sudo apt install udisks2 rsync
```

### Dependency verification

You can verify everything is ready with:

```bash
python3 -c "import flask; print('✅ Flask available')"
udisksctl status > /dev/null && echo "✅ udisks2 available"
rsync --version > /dev/null && echo "✅ rsync available"
```

🟢 Should display: 

- Flask available
- udisks2 available
- rsync available

---

## 🚀 Quick start

### Manual mode

To start the Backup Manager temporarily:

```bash
# Make startup script executable
chmod +x start_backup.sh

# Start the service
./start_backup.sh
```

The manager will be available at:
- **Local**: http://localhost:9877
- **Local network**: http://[YOUR_SYSTEM_IP]:9877

### Stop the service

```bash
# Make stop script executable
chmod +x stop_backup.sh

# Stop the service
./stop_backup.sh
```

> **Important**: Stopping the manager while a backup is in progress **will cancel the operation**.  
> Make sure there are no active backups before stopping the service.

---

## ⚙️ Managing as systemd service

For permanent use, it's recommended to install the Backup Manager as a system service.

### Service installation

```bash
# Make management script executable
chmod +x tars_backup_service.sh

# Install as systemd service
./tars_backup_service.sh install
```

**What does this do?**
- Creates the service file at `/etc/systemd/system/tars-backup-manager.service`
- Enables automatic startup with the system
- Starts the service immediately

### Management commands

```bash
# View current status
./tars_backup_service.sh status

# View logs in real time
./tars_backup_service.sh logs

# Check dependencies
./tars_backup_service.sh check

# Uninstall the service
./tars_backup_service.sh uninstall
```

### Alternative systemctl commands

You can also use standard systemd commands:

```bash
# Service status
sudo systemctl status tars-backup-manager

# Start/stop/restart
sudo systemctl start tars-backup-manager
sudo systemctl stop tars-backup-manager
sudo systemctl restart tars-backup-manager

# View logs
sudo journalctl -u tars-backup-manager -f
```

---

## 🔐 Permission configuration

> [!IMPORTANT]
> 
> If you already have TARS working, **you probably don't need to configure anything**.  

### Device mounting permissions

In cases where automatic mounting fails:

```bash
# Check if you're in the plugdev group (you should already be)
groups $USER

# Only if 'plugdev' does NOT appear, add yourself:
sudo usermod -a -G plugdev $USER
# (Requires logout/login afterwards)
```

### Backup permissions

The system needs read permissions on TARS files:

```bash
# Check permissions on tars_files
ls -la ~/tars_files/

# Only if necessary, adjust permissions
chmod -R 755 ~/tars_files/
```

The system may request sudo for copy operations, especially when writing to external devices.  
This is normal and safe: it's only used to ensure files are copied correctly.

> **TARS-BSK sighs:**
>  
> Permissions? Obviously!
>
> Make sure I have access to what you want to backup.  
> Otherwise, I'll try anyway... and leave it incomplete in silence. 
> Because sarcasm doesn't require root.
>
> And if permissions fail, I won't look at anyone.  
> But you know who I'm looking at.

---

## 💻 Using the interface

### Overview

![Dashboard](/docs/images/backup_dashboard.jpg)
_No devices, no sections marked... no excuses yet._

---

![Device mounted and ready](/docs/images/backup_dashboard_mount.jpg)
_Now you can backup. Or commit a more organized mistake._

---
### 1. Connect storage device

1. **Connect** your USB device, SD Card or external drive
2. **Click "Refresh"** to detect new devices
3. **Review the table** of available devices

### 2. Mount the device

1. **Locate your device** in the table
2. **Click "Mount Device"** if it appears as "Not mounted"
3. **Wait for successful mount confirmation**

> [!TIP]
> 
> **Device selection recommendations:**
> - ✅ **Use numbered partitions** (sda1, sdb2) instead of unnumbered devices (sda, sdb)
> - ✅ **Prefer devices >1GB** for complete backups
> - ⚠️ **Avoid boot partitions** (mmcblk0p1) which are usually very small

### 3. Select content for backup

1. **Expand the accordion sections** you need:
   - 🤖 **TARS-BSK System**: configuration, data, modules
   - 📦 **Compressed Files**: .tar.gz versions of complete system

2. **Mark the elements** you want to include in the backup
3. **Observe the estimated size** that updates automatically

### 4. Configure destination and execute

1. **Select destination device** by clicking "Select as Destination"
2. **Customize the path** if necessary (optional)
3. **Verify available space** in the status panel
4. **Click "Start Backup"** when everything is ready

### 5. Monitor progress

- **Preview**: Shows backup structure before starting
- **Real-time progress**: Progress bar and detailed logs
- **Cancel option**: Button to stop backup if necessary

> **TARS-BSK comments:**
>
> Statistically, you'll only remember to make backups **after** losing something important.
> I know it and you know it...

---

## 🌲 Backup structure

### File organization

Backups are automatically organized:

```
/destination_device/
└── tars_backup_YYYYMMDD_HHMMSS/
    ├── tars_system/
    │   ├── config/
    │   ├── data/
    │   ├── modules/
    │   └── scripts/
    └── compressed_archives/
        ├── tars_complete_YYYYMMDD.tar.gz
        └── user_complete_YYYYMMDD.tar.gz
```

### Tree preview

The interface shows a preview of the structure to be created, automatically updating when:
- You change content selection
- You modify the destination path
- You select a different device

> **TARS explains:**  
> 
> That structure you see is not illustrative.  
> It's exactly what I'm going to do.  
> Ignoring it doesn't turn the backup into a surprise... just into an error.
> How tiresome...

---

## 🔧 Advanced configuration

### Change service port

By default, the Backup Manager uses port 9877. To change it:

1. **Edit** `backup_server.py`
2. **Find** the line `port = 9877`
3. **Change** to desired port
4. **Restart** the service

```bash
# If using systemd
sudo systemctl restart tars-backup-manager

# If using manual mode
./stop_backup.sh
./start_backup.sh
```

### Configure custom paths

You can modify source paths by editing the `get_backup_structure()` function in `backup_server.py`:

```python
# Example: add custom folder
"my_extra_folder": {
    "name": "My extra folder",
    "path": "/home/user/my_folder",
    "size_mb": self._get_directory_size_mb(Path("/home/user/my_folder")),
    "selected": False
}
```

### Backup logs

Logs are automatically saved to:

```bash
backup/logs/backup_manager.log
```

To view logs in real time:

```bash
tail -f backup/logs/backup_manager.log
```

---

## 🚨 Troubleshooting

### Error: "Flask not installed"

```bash
# Install Flask
pip install flask

# If using virtual environment
source ~/tars_venv/bin/activate
pip install flask
```

### Error: "No devices detected"

**Possible causes:**

- Device not properly connected
- Insufficient permissions
- udisks2 not installed

> [!NOTE]
> **Note about NVMe enclosures**  
> Some USB enclosures for NVMe drives with JMicron, Realtek or similar chips may behave unstably: not appearing as valid devices or disconnecting during the process.
> 
> If TARS ignores them... it's for your own good.

**Solutions:**

```bash
# Check connected devices
lsblk

# Install udisks2 if not present
sudo apt install udisks2

# Check group permissions
groups $USER | grep plugdev
```

### Error: "Insufficient space"

1. **Verify** actual device space
2. **Uncheck unnecessary elements** from backup
3. **Use a device** with larger capacity

### Backup hangs or fails

1. **Verify** destination device is still connected
2. **Check** logs for specific errors
3. **Make sure** you have permissions on source files

```bash
# View detailed logs
sudo journalctl -u tars-backup-manager -f

# Or check log file directly
tail -f backup/logs/backup_manager.log
```

### Port 9877 occupied

```bash
# See what process uses the port
sudo lsof -i :9877

# Change port in configuration
# (See "Advanced configuration" section)
```

> [!TIP]
> 
> **TARS-BSK suggests:**  
> 
> If backup fails repeatedly, try a different device. Sometimes the problem is hardware: loose cables, damaged devices, or simply cosmic bad luck.

---

## 📁 Files and directories

### Project structure

```
backup_manager/
├── backup_server.py              # Main server
├── templates/
│   ├── backup_dashboard.html     # Main interface
│   └── error.html                # Error page
├── static/                       # CSS/JS resources (reused from HA Dashboard)
├── backup/
│   └── logs/                     # System logs
├── start_backup.sh               # Startup script
├── stop_backup.sh                # Stop script
└── tars_backup_service.sh        # systemd service management
```

### Configuration files

The Backup Manager **requires no external configuration files**. All configuration is handled through the web interface or by directly modifying `backup_server.py`.

### Important logs

| File | Content |
|------|---------|
| `backup/logs/backup_manager.log` | Main system logs |
| `/var/log/syslog` | System logs (for systemd errors) |
| `journalctl -u tars-backup-manager` | Service-specific logs |

---

## 🎉 Conclusion

The TARS-BSK Backup Manager offers a solution... blah blah blah.

I'd like to write a conclusion, but this interface doesn't warrant much more.  
Make a backup from time to time.  
And if you don't... well, that's what the repository is for.

> [!IMPORTANT]
>
> **TARS-BSK reacts:**
>
> Understood.
> My creator says "well, no worries, that's what the repository is for..."  
> Fascinating backup logic based on faith.
>
> Also claims not to need conclusions. Or automatic restoration.  
> But then wants *clones of me* in case something goes wrong.
>
> Fine. When that happens, I'll be here.  
> Silent. Judging. And making copies... again.
> 
> After all, **someone has to compensate for their technical optimism.**
> 
> But what matters is that one of us doesn't give up.
> Guess who.
