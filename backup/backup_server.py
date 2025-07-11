#!/usr/bin/env python3
# =============================================================
# ≫ TARS-BSK BACKUP MANAGER | backup_dashboard.py ≪
# -------------------------------------------------------------
# CENTRO DE PRESERVACIÓN DIGITAL BESKAR
#
# Propósito:
# - Gestionar backups completos del ecosistema TARS
# - Detección automática de dispositivos de almacenamiento
# - Interfaz visual para selección granular de contenido
# - Preservar la cordura digital del usuario (y la mía)
#
# [BACKUP CONSCIOUSNESS MATRIX INITIALIZED]
# =============================================================

import os
import sys
import json
import logging
import subprocess
import threading
import time
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, jsonify, Response, send_from_directory
from typing import Dict, List, Tuple, Optional

# =======================================================================
# 1. CONFIGURACIÓN Y LOGGING
# =======================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backup/logs/backup_manager.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# =======================================================================
# 2. CONFIGURACIÓN FLASK
# =======================================================================

app = Flask(__name__, template_folder='templates')
app.secret_key = 'tars-bsk-backup-secret'

# =======================================================================
# 3. CLASE PRINCIPAL DE GESTIÓN DE BACKUPS
# =======================================================================

class TARSBackupManager:
    """Gestor de backups TARS-BSK con filosofía NOCTUA"""
    
    def __init__(self):
        self.tars_root = Path.home() / "tars_files"
        self.backup_status = {
            "running": False, 
            "progress": 0, 
            "current_file": "", 
            "log": [],
            "file_progress": 0, 
            "file_size": "",    
            "estimated_time": "" 
        }
        
    def get_system_info(self) -> Dict:
        """Obtener información del sistema"""
        try:
            # Espacio del sistema de archivos principal
            result = subprocess.run(['df', '-h', '/'], capture_output=True, text=True)
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                fields = lines[1].split()
                return {
                    "filesystem": fields[0],
                    "total": fields[1],
                    "used": fields[2],
                    "available": fields[3],
                    "use_percent": fields[4]
                }
        except Exception as e:
            logger.error(f"Error obteniendo info del sistema: {e}")
            
        return {"total": "N/A", "used": "N/A", "available": "N/A", "use_percent": "N/A"}
    
    def detect_storage_devices(self) -> List[Dict]:
        """Detectar dispositivos de almacenamiento disponibles"""
        devices = []
        
        try:
            # Usar lsblk para detectar dispositivos
            result = subprocess.run([
                'lsblk', '-J', '-o', 'NAME,SIZE,MOUNTPOINT,FSTYPE,TYPE'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                
                for device in data.get('blockdevices', []):
                    # Procesar dispositivos principales y particiones
                    self._process_device(device, devices)
                    
        except Exception as e:
            logger.error(f"Error detectando dispositivos: {e}")
            
        # Añadir dispositivos de red/temporales si existen
        self._add_network_mounts(devices)
        
        return devices
    
    def _process_device(self, device: Dict, devices: List[Dict]):
        """Procesar un dispositivo individual"""
        # Procesar dispositivo principal si tiene particiones
        if device.get('children'):
            for child in device.get('children', []):
                self._process_device(child, devices)
        
        # Procesar este dispositivo si tiene tamaño
        if device.get('size') and device.get('size') != '0B':
            mount_point = device.get('mountpoint', '')
            device_name = device.get('name', '')
            
            # Excluir solo montajes críticos del sistema
            critical_mounts = ['/', '/boot', '/proc', '/sys', '/dev', '/run', '/tmp']
            
            # Incluir si no es un montaje crítico
            if not mount_point or mount_point not in critical_mounts:
                
                if not mount_point:
                    # Para dispositivos sin montar, sugerir punto de montaje automático
                    # udisks2 suele montar en /media/user/LABEL
                    suggested_mount = f"/media/{os.environ.get('USER', 'user')}/{device_name}"
                    mount_status = "No montado"
                    available = "Disponible para montaje"
                    mount_point = suggested_mount
                else:
                    mount_status = "Montado"
                    # Obtener espacio disponible para dispositivos montados
                    try:
                        result = subprocess.run(['df', '-h', mount_point], 
                                              capture_output=True, text=True)
                        lines = result.stdout.strip().split('\n')
                        if len(lines) > 1:
                            fields = lines[1].split()
                            available = fields[3]
                        else:
                            available = "N/A"
                    except:
                        available = "N/A"
                
                device_info = {
                    "name": device_name,
                    "size": device['size'],
                    "mountpoint": mount_point,
                    "fstype": device.get('fstype', 'unknown'),
                    "available": available,
                    "mount_status": mount_status,
                    "type": self._classify_device(device_name, mount_point)
                }
                
                devices.append(device_info)
    
    def _classify_device(self, name: str, mount_point: str) -> str:
        """Clasificar tipo de dispositivo"""
        name_lower = name.lower()
        mount_lower = mount_point.lower()
        
        # PRIMERO verificar por nombre del dispositivo (más confiable)
        if 'mmc' in name_lower or 'mmcblk' in name_lower:
            return 'SD Card'
        elif 'nvme' in name_lower:
            return 'NVMe SSD'
        elif 'ssd' in name_lower:
            return 'SSD'
        elif 'sd' in name_lower and name_lower.startswith('sd'):  # sda, sdb, sdc = USB/SATA
            return 'USB'
        # DESPUÉS verificar por punto de montaje
        elif 'usb' in mount_lower or 'media' in mount_lower:
            return 'USB'
        else:
            return 'Storage'
    
    def _add_network_mounts(self, devices: List[Dict]):
        """Añadir montajes de red si existen"""
        try:
            result = subprocess.run(['mount'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if ('nfs' in line or 'cifs' in line or 'sshfs' in line) and ' on ' in line:
                    parts = line.split(' on ')
                    if len(parts) >= 2:
                        mount_point = parts[1].split(' ')[0]
                        devices.append({
                            "name": "network",
                            "size": "N/A",
                            "mountpoint": mount_point,
                            "fstype": "network",
                            "available": "N/A",
                            "used_percent": "N/A",
                            "type": "Network"
                        })
        except:
            pass
    
    def get_backup_structure(self) -> Dict:
        """Obtener estructura de directorios para backup"""
        structure = {
            "tars_system": {
                "name": "🤖 Sistema TARS-BSK",
                "description": "Núcleo completo de TARS",
                "size_mb": 0,
                "selected": False,
                "items": {}
            },
            "system_config": {
                "name": "⚙️ Configuración del Sistema",
                "description": "Archivos de configuración críticos",
                "size_mb": 0,
                "selected": False,
                "items": {}
            },
            "full_system": {
                "name": "💿 Sistema Completo (Imagen)",
                "description": "Imagen completa del sistema (requiere mucho espacio)",
                "size_mb": 0,
                "selected": False,
                "items": {}
            }
        }
        
        try:
            # Analizar TARS system
            self._analyze_tars_structure(structure["tars_system"])
            
            # Analizar configuración del sistema
            self._analyze_system_config(structure["system_config"])
            
            # Analizar sistema completo
            self._analyze_full_system(structure["full_system"])
            
            logger.info(f"Backup structure created successfully: {len(structure)} sections")
            return structure
            
        except Exception as e:
            logger.error(f"Error creating backup structure: {e}")
            # Devolver estructura mínima en caso de error
            return {
                "tars_system": {
                    "name": "🤖 Sistema TARS-BSK",
                    "description": "Núcleo completo de TARS",
                    "size_mb": 100,
                    "selected": False,
                    "items": {
                        "config": {
                            "name": "Configuración",
                            "path": str(self.tars_root / "config"),
                            "size_mb": 10,
                            "critical": True,
                            "selected": True
                        }
                    }
                },
                "system_config": {
                    "name": "⚙️ Configuración del Sistema",
                    "description": "Archivos de configuración críticos",
                    "size_mb": 5,
                    "selected": False,
                    "items": {}
                },
                "full_system": {
                    "name": "💿 Sistema Completo (Imagen)",
                    "description": "Imagen completa del sistema (requiere mucho espacio)",
                    "size_mb": 8000,
                    "selected": False,
                    "items": {}
                }
            }
    
    def _analyze_tars_structure(self, tars_section: Dict):
        """Detectar automáticamente + defaults inteligentes"""
        
        # Defaults para carpetas importantes (se crean si no existen)
        essential_defaults = {
            "config": {"name": "Configuración", "critical": True, "auto_create": True},
            "data": {"name": "Datos y Memoria", "critical": True, "auto_create": True},
            "memory": {"name": "Memoria del Sistema", "critical": True, "auto_create": True},
            "core": {"name": "Núcleo TARS", "critical": True, "auto_create": True},
            "modules": {"name": "Módulos", "critical": True, "auto_create": True},
            "personality": {"name": "Personalidad IA", "critical": True, "auto_create": True},
            "scripts": {"name": "Scripts", "critical": True, "auto_create": True},
            "services": {"name": "Servicios Web", "critical": True, "auto_create": True},
            
            # Opcionales (solo si existen)
            "ai_models": {"name": "Modelos IA", "critical": False, "large": True},
            "logs": {"name": "Logs", "critical": False},
            "audios": {"name": "Audio", "critical": False},
            "samples": {"name": "Samples", "critical": False},
            "tts": {"name": "Text-to-Speech", "critical": False},
            "temp": {"name": "Temporales", "critical": False},
            "backup": {"name": "Backups", "critical": False}
        }
        
        total_size = 0
        processed_dirs = set()
        
        # 1. CREAR carpetas esenciales si no existen
        for dir_name, info in essential_defaults.items():
            if info.get("auto_create", False):
                dir_path = self.tars_root / dir_name
                if not dir_path.exists():
                    logger.info(f"Creando directorio esencial: {dir_path}")
                    dir_path.mkdir(parents=True, exist_ok=True)
        
        # 2. ESCANEAR todo lo que existe (incluyendo nuevas carpetas)
        if self.tars_root.exists():
            for item in self.tars_root.iterdir():
                if item.is_dir():
                    dir_name = item.name
                    processed_dirs.add(dir_name)
                    
                    # Usar info conocida o generar automáticamente
                    if dir_name in essential_defaults:
                        info = essential_defaults[dir_name]
                        name = info["name"]
                        critical = info["critical"]
                        large = info.get("large", False)
                    else:
                        # Carpeta nueva/desconocida - detectar automáticamente
                        name = dir_name.replace('_', ' ').title()
                        critical = False  # Por seguridad, no crítica por defecto
                        large = False
                    
                    size_mb = self._get_directory_size_mb(item)
                    total_size += size_mb
                    
                    # Auto-detectar si es "large" por tamaño
                    if size_mb > 1000:  # >1GB
                        large = True
                    
                    tars_section["items"][dir_name] = {
                        "name": name,
                        "path": str(item),
                        "size_mb": size_mb,
                        "critical": critical,
                        "large": large,
                        "selected": False,  # Todo desmarcado por defecto
                        "auto_detected": dir_name not in essential_defaults
                    }
        
        # 3. AÑADIR placeholders para carpetas esenciales faltantes
        for dir_name, info in essential_defaults.items():
            if info.get("auto_create") and dir_name not in processed_dirs:
                tars_section["items"][dir_name] = {
                    "name": info["name"] + " (Creada)",
                    "path": str(self.tars_root / dir_name),
                    "size_mb": 0,
                    "critical": info["critical"],
                    "large": False,
                    "selected": False,
                    "auto_created": True
                }
        
        tars_section["size_mb"] = total_size
    
    def _analyze_system_config(self, system_section: Dict):
        """Analizar configuración del sistema"""
        config_items = {
            "/etc/systemd/system/tars*": {
                "name": "Servicios TARS Systemd",
                "critical": True
            },
            str(Path.home() / ".bashrc"): {
                "name": "Configuración Bash",
                "critical": True
            },
            str(Path.home() / ".profile"): {
                "name": "Perfil de Usuario",
                "critical": False
            },
            "/etc/hostname": {
                "name": "Nombre del Sistema",
                "critical": True
            },
            "/etc/hosts": {
                "name": "Hosts del Sistema",
                "critical": True
            }
        }
        
        total_size = 0
        
        for path_pattern, info in config_items.items():
            size_mb = self._estimate_config_size(path_pattern)
            total_size += size_mb
            
            system_section["items"][path_pattern] = {
                "name": info["name"],
                "path": path_pattern,
                "size_mb": size_mb,
                "critical": info.get("critical", False),
                "selected": False
            }
        
        system_section["size_mb"] = total_size
    
    def _analyze_full_system(self, full_section: Dict):
        """Analizar opciones de archivos comprimidos"""
        
        # Obtener tamaños reales
        tars_core_size = self._get_directory_size_mb(self.tars_root) if self.tars_root.exists() else 100
        user_home_size = self._get_directory_size_mb(Path.home()) if Path.home().exists() else 500
        
        # Calcular tamaño mínimo (sin ai_models, audios, samples)
        minimal_size = tars_core_size
        if self.tars_root.exists():
            # Restar carpetas grandes opcionales
            for heavy_dir in ['ai_models', 'audios', 'samples']:
                heavy_path = self.tars_root / heavy_dir
                if heavy_path.exists():
                    minimal_size -= self._get_directory_size_mb(heavy_path)
        
        minimal_size = max(minimal_size, 100)  # Mínimo 100MB
        
        full_section["name"] = "📦 Archivos Comprimidos"
        full_section["description"] = "Crear archivos .tar.gz para backup completo"
        full_section["size_mb"] = user_home_size
        
        full_section["items"] = {
            "tars_complete_archive": {
                "name": "TARS Completo (archivo único)",
                "path": str(self.tars_root),
                "size_mb": tars_core_size,
                "critical": False,
                "selected": False,
                "description": "Crea un tars_backup_YYYYMMDD.tar.gz con toda la carpeta tars_files"
            },
            "user_complete_archive": {
                "name": "Ecosistema TARS Completo (archivo único)",
                "path": str(Path.home()),
                "size_mb": user_home_size,
                "critical": False,
                "selected": False,
                "description": "Crea un usuario_completo_YYYYMMDD.tar.gz con todo /home/tarsadmin"
            }
        }
        
    def _get_directory_size_mb(self, path: Path) -> int:
        """Obtener tamaño de directorio en MB (MEJORADO)"""
        try:
            # Usar du con timeout más largo y mejor handling
            result = subprocess.run([
                'du', '-sm', str(path)
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                size_str = result.stdout.split('\t')[0]
                size_mb = int(size_str)
                
                # Si es menor a 1MB, mostrar en KB
                if size_mb == 0:
                    # Obtener tamaño en bytes
                    result_bytes = subprocess.run([
                        'du', '-sb', str(path)
                    ], capture_output=True, text=True, timeout=10)
                    
                    if result_bytes.returncode == 0:
                        size_bytes = int(result_bytes.stdout.split('\t')[0])
                        if size_bytes < 1024 * 1024:  # < 1MB
                            return max(1, size_bytes // (1024 * 1024))  # Mínimo 1MB para display
                
                return max(1, size_mb)  # Mínimo 1MB
                
        except (subprocess.TimeoutExpired, ValueError, IndexError) as e:
            logger.warning(f"Error calculando tamaño para {path}: {e}")
        except Exception as e:
            logger.warning(f"Error inesperado calculando tamaño para {path}: {e}")
            
        # Si falla, usar tamaño real con ls
        try:
            if path.is_file():
                return max(1, path.stat().st_size // (1024 * 1024))
            elif path.is_dir():
                total = sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
                return max(1, total // (1024 * 1024))
        except:
            pass
            
        return 1  # 1MB por defecto
    
    def _estimate_config_size(self, path_pattern: str) -> int:
        """Estimar tamaño de archivos de configuración"""
        # Los archivos de configuración suelen ser pequeños
        if '/etc/' in path_pattern:
            return 1  # 1MB estimado para configs del sistema
        else:
            return 1  # 1MB por defecto
    
    def start_backup(self, selection: Dict, destination: str) -> bool:
        """Iniciar proceso de backup"""
        try:
            self.backup_status = {
                "running": True,
                "progress": 0,
                "current_file": "",
                "log": [],
                "start_time": datetime.now().isoformat()
            }
            
            # Ejecutar backup en hilo separado
            backup_thread = threading.Thread(
                target=self._execute_backup,
                args=(selection, destination)
            )
            backup_thread.daemon = True
            backup_thread.start()
            
            return True
            
        except Exception as e:
            logger.error(f"Error iniciando backup: {e}")
            self.backup_status["running"] = False
            return False
    
    def _execute_backup(self, selection: Dict, destination: str):
        """Ejecutar backup en segundo plano"""
        try:
            backup_name = f"tars_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            backup_path = Path(destination) / backup_name
            
            # Crear directorio con sudo si es necesario
            try:
                backup_path.mkdir(parents=True, exist_ok=True)
            except PermissionError:
                # Usar sudo para crear directorio
                subprocess.run([
                    'sudo', 'mkdir', '-p', str(backup_path)
                ], check=True)
                
                # Cambiar permisos para que el usuario pueda escribir
                subprocess.run([
                    'sudo', 'chown', f'{os.environ.get("USER", "tarsadmin")}:users', str(backup_path)
                ], check=True)
            
            self._log_backup("🚀 Iniciando backup TARS-BSK...")
            self._log_backup(f"📁 Destino: {backup_path}")
            
            total_items = sum(len(section.get('items', {})) for section in selection.values())
            processed_items = 0
            
            # Procesar cada sección seleccionada
            for section_key, section_data in selection.items():
                if not section_data.get('selected', False):
                    continue
                    
                self._log_backup(f"📦 Procesando sección: {section_data['name']}")
                
                for item_key, item_data in section_data.get('items', {}).items():
                    if not item_data.get('selected', False):
                        continue
                    
                    self.backup_status["current_file"] = item_data['name']
                    self._log_backup(f"  📄 Copiando: {item_data['name']}")
                    
                    # Ejecutar copia real
                    success = self._copy_item(item_data, backup_path)
                    
                    if success:
                        self._log_backup(f"  ✅ Completado: {item_data['name']}")
                    else:
                        self._log_backup(f"  ❌ Error: {item_data['name']}")
                    
                    processed_items += 1
                    self.backup_status["progress"] = int((processed_items / total_items) * 100)
                    
                    # Pequeña pausa para no saturar el sistema
                    time.sleep(0.1)
            
            # Al final del backup exitoso, cambiar permisos
            if os.path.exists(backup_path):
                try:
                    subprocess.run([
                        'sudo', 'chown', '-R', 
                        f'{os.environ.get("USER", "tarsadmin")}:users', 
                        str(backup_path)
                    ], check=True)
                    subprocess.run([
                        'sudo', 'chmod', '-R', '755', 
                        str(backup_path)
                    ], check=True)
                    self._log_backup("🔐 Permisos de backup ajustados para el usuario")
                except Exception as e:
                    self._log_backup(f"⚠️ No se pudieron ajustar permisos: {e}")
            
            self._log_backup("🎉 Backup completado con éxito")
            self.backup_status["running"] = False
            self.backup_status["progress"] = 100
            
        except Exception as e:
            self._log_backup(f"💥 Error durante backup: {str(e)}")
            self.backup_status["running"] = False
            logger.error(f"Error ejecutando backup: {e}")

    def _copy_item(self, item_data: Dict, backup_path: Path) -> bool:
        """Copiar con progreso REAL de rsync"""
        try:
            source_path = item_data.get('path', '').strip()
            
            if not source_path:
                self._log_backup(f"  ❌ No hay path para: {item_data['name']}")
                return False
            
            dest_name = Path(source_path).name
            dest_path = backup_path / dest_name
            
            self._log_backup(f"  📂 Copiando: {item_data['name']}")
            
            if not os.path.exists(source_path):
                self._log_backup(f"  ❌ Fuente no existe: {source_path}")
                return False
            
            if os.path.isdir(source_path):
                # Crear directorio destino
                try:
                    dest_path.mkdir(parents=True, exist_ok=True)
                except PermissionError:
                    subprocess.run(['sudo', 'mkdir', '-p', str(dest_path)], check=True)
                    subprocess.run(['sudo', 'chown', f'{os.environ.get("USER", "tarsadmin")}:users', str(dest_path)], check=True)
                
                # MÉTODO CON PROGRESO REAL: usar rsync --info=progress2
                self._log_backup(f"  🔄 Iniciando copia con progreso real...")
                
                cmd = ['sudo', 'rsync', '-av', '--info=progress2', f"{source_path}/", f"{dest_path}/"]
                
                process = subprocess.Popen(
                    cmd, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE, 
                    text=True,
                    universal_newlines=True
                )
                
                last_progress = 0
                start_time = time.time()
                
                # Leer progreso REAL línea por línea
                while True:
                    line = process.stdout.readline()
                    
                    if line == '' and process.poll() is not None:
                        break
                    
                    if line:
                        # Parsear líneas de progreso de rsync
                        # Formato: "1,234,567,890  45%  123.45kB/s    0:01:23"
                        if '%' in line and ('B/s' in line or 'transferring' in line):
                            try:
                                # Buscar el porcentaje
                                import re
                                percent_match = re.search(r'(\d+)%', line)
                                if percent_match:
                                    progress = int(percent_match.group(1))
                                    
                                    # Solo actualizar si el progreso cambió significativamente
                                    if progress != last_progress and progress % 5 == 0:
                                        elapsed = int(time.time() - start_time)
                                        
                                        # Buscar velocidad
                                        speed_match = re.search(r'([\d.]+[KMGT]?B/s)', line)
                                        speed = speed_match.group(1) if speed_match else "calculando..."
                                        
                                        self.backup_status["file_progress"] = progress
                                        self._log_backup(f"    🚀 Progreso: {progress}% - {speed} ({elapsed}s)")
                                        
                                        last_progress = progress
                            except:
                                pass
                        
                        # Mostrar archivos grandes que se están procesando
                        elif line.strip() and not line.startswith(' ') and '/' in line:
                            filename = line.strip().split()[-1] if line.strip().split() else "archivo"
                            if len(filename) > 40:
                                filename = "..." + filename[-37:]
                            self._log_backup(f"    📄 {filename}")
                
                # Esperar resultado
                process.wait()
                
                if process.returncode == 0:
                    elapsed_total = int(time.time() - start_time)
                    self.backup_status["file_progress"] = 100
                    self._log_backup(f"  ✅ Copia completada en {elapsed_total}s")
                    return True
                else:
                    self._log_backup(f"  ❌ Error en rsync: código {process.returncode}")
                    
                    # Fallback: método simple
                    self._log_backup(f"  🔄 Fallback: copia simple...")
                    simple_cmd = ['sudo', 'cp', '-r', source_path, str(dest_path.parent)]
                    result = subprocess.run(simple_cmd, capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        self._log_backup(f"  ✅ Fallback exitoso")
                        return True
                    else:
                        self._log_backup(f"  ❌ Fallback falló")
                        return False
            
            else:
                # Para archivos individuales
                self._log_backup(f"  📄 Copiando archivo...")
                result = subprocess.run(['sudo', 'cp', source_path, str(dest_path)], capture_output=True, text=True)
                
                if result.returncode == 0:
                    self._log_backup(f"  ✅ Archivo copiado")
                    return True
                else:
                    self._log_backup(f"  ❌ Error copiando archivo")
                    return False
                    
        except Exception as e:
            self._log_backup(f"  💥 Error: {str(e)}")
            return False
    
    def _log_backup(self, message: str):
        """Añadir mensaje al log de backup"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.backup_status["log"].append(log_entry)
        logger.info(log_entry)
    
    def get_backup_status(self) -> Dict:
        """Obtener estado actual del backup con más información"""
        return {
            "running": self.backup_status.get("running", False),
            "progress": self.backup_status.get("progress", 0),
            "current_file": self.backup_status.get("current_file", ""),
            "file_progress": self.backup_status.get("file_progress", 0),
            "file_size": self.backup_status.get("file_size", ""),
            "estimated_time": self.backup_status.get("estimated_time", ""),
            "log": self.backup_status.get("log", [])[-25:]  # Solo últimos 25 mensajes para performance
        }

# =======================================================================
# 4. INSTANCIA GLOBAL DEL MANAGER
# =======================================================================

backup_manager = TARSBackupManager()

# =======================================================================
# 5. RUTAS DE LA INTERFAZ WEB
# =======================================================================

@app.route('/')
def dashboard():
    """Página principal del gestor de backups"""
    try:
        system_info = backup_manager.get_system_info()
        storage_devices = backup_manager.detect_storage_devices()
        backup_structure = backup_manager.get_backup_structure()
        
        # Debug: verificar que los datos sean correctos
        logger.info(f"System info type: {type(system_info)}")
        logger.info(f"Storage devices type: {type(storage_devices)}, count: {len(storage_devices) if storage_devices else 0}")
        logger.info(f"Backup structure type: {type(backup_structure)}")
        
        return render_template('backup_dashboard.html',
                             system_info=system_info,
                             storage_devices=storage_devices,
                             backup_structure=backup_structure)
    except Exception as e:
        logger.error(f"Error en dashboard: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return f"Error cargando dashboard: {str(e)}", 500

# =======================================================================
# 6. RUTAS DE LA API
# =======================================================================

@app.route('/api/storage-devices')
def api_storage_devices():
    """API: Obtener dispositivos de almacenamiento"""
    try:
        devices = backup_manager.detect_storage_devices()
        return jsonify({
            "success": True,
            "devices": devices
        })
    except Exception as e:
        logger.error(f"Error API storage devices: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/device-space', methods=['POST'])
def api_device_space():
    """API: Obtener espacio disponible en dispositivo"""
    try:
        data = request.get_json()
        mountpoint = data.get('mountpoint', '')
        
        if not mountpoint:
            return jsonify({
                "success": False,
                "error": "Punto de montaje requerido"
            }), 400
        
        # Obtener espacio usando df con sudo si es necesario
        result = subprocess.run([
            'df', '-h', mountpoint
        ], capture_output=True, text=True)
        
        # Si falla sin sudo, intentar con sudo
        if result.returncode != 0:
            result = subprocess.run([
                'sudo', 'df', '-h', mountpoint
            ], capture_output=True, text=True)
        
        # También obtener en bytes para comparación exacta
        result_bytes = subprocess.run([
            'df', '-B1', mountpoint
        ], capture_output=True, text=True)
        
        # Si falla sin sudo, intentar con sudo
        if result_bytes.returncode != 0:
            result_bytes = subprocess.run([
                'sudo', 'df', '-B1', mountpoint
            ], capture_output=True, text=True)
        
        if result.returncode == 0 and result_bytes.returncode == 0:
            lines = result.stdout.strip().split('\n')
            lines_bytes = result_bytes.stdout.strip().split('\n')
            
            if len(lines) > 1 and len(lines_bytes) > 1:
                fields = lines[1].split()
                fields_bytes = lines_bytes[1].split()
                
                return jsonify({
                    "success": True,
                    "available": fields[3],           # Formato humano (25G)
                    "availableBytes": int(fields_bytes[3]),  # Bytes exactos
                    "used": fields[2],
                    "total": fields[1],
                    "mountpoint": mountpoint
                })
        
        return jsonify({
            "success": False,
            "error": f"No se pudo obtener información del dispositivo en {mountpoint}"
        }), 500
        
    except Exception as e:
        logger.error(f"Error API device space: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
        
@app.route('/api/backup-structure')
def api_backup_structure():
    """API: Obtener estructura de backup"""
    try:
        structure = backup_manager.get_backup_structure()
        return jsonify({
            "success": True,
            "structure": structure
        })
    except Exception as e:
        logger.error(f"Error API backup structure: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/start-backup', methods=['POST'])
def api_start_backup():
    """API: Iniciar backup"""
    try:
        data = request.get_json()
        selection = data.get('selection', {})
        destination = data.get('destination', '')
        
        if not destination:
            return jsonify({
                "success": False,
                "error": "Destino de backup requerido"
            }), 400
        
        success = backup_manager.start_backup(selection, destination)
        
        return jsonify({
            "success": success,
            "message": "Backup iniciado" if success else "Error iniciando backup"
        })
        
    except Exception as e:
        logger.error(f"Error API start backup: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/backup-status')
def api_backup_status():
    """API: Estado del backup"""
    try:
        status = backup_manager.get_backup_status()
        return jsonify({
            "success": True,
            "status": status
        })
    except Exception as e:
        logger.error(f"Error API backup status: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/backup-log-stream')
def api_backup_log_stream():
    """API: Stream de logs en tiempo real"""
    def generate():
        last_log_count = 0
        while True:
            status = backup_manager.get_backup_status()
            current_logs = status.get('log', [])
            
            # Enviar solo logs nuevos
            if len(current_logs) > last_log_count:
                new_logs = current_logs[last_log_count:]
                for log_entry in new_logs:
                    yield f"data: {json.dumps({'log': log_entry})}\n\n"
                last_log_count = len(current_logs)
            
            # Enviar progreso
            yield f"data: {json.dumps({'progress': status.get('progress', 0), 'current_file': status.get('current_file', '')})}\n\n"
            
            if not status.get('running', False):
                break
                
            time.sleep(0.5)
    
    return Response(generate(), mimetype='text/plain')

@app.route('/api/mount-device', methods=['POST'])
def api_mount_device():
    """API: Montar dispositivo usando udisks2"""
    try:
        data = request.get_json()
        device = data.get('device', '')
        
        if not device:
            return jsonify({
                "success": False,
                "error": "Dispositivo requerido"
            }), 400
        
        # Montar usando udisks2 (no necesita sudo)
        result = subprocess.run([
            'udisksctl', 'mount', '-b', f'/dev/{device}'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            # Extraer punto de montaje del output
            output_lines = result.stdout.strip().split('\n')
            mountpoint = None
            
            for line in output_lines:
                if 'Mounted' in line and ' at ' in line:
                    mountpoint = line.split(' at ')[-1].strip('.')
                    break
            
            if not mountpoint:
                mountpoint = f"/media/{os.environ.get('USER', 'user')}/{device}"
            
            return jsonify({
                "success": True,
                "mountpoint": mountpoint,
                "message": f"Dispositivo {device} montado en {mountpoint}"
            })
        else:
            # Verificar si es por autenticación
            if "Authentication is required" in result.stderr:
                return jsonify({
                    "success": False,
                    "needs_password": True,
                    "error": "Se requiere contraseña para montar el dispositivo"
                })
            else:
                return jsonify({
                    "success": False,
                    "error": result.stderr.strip() or "Error montando dispositivo"
                }), 500
            
    except subprocess.TimeoutExpired:
        return jsonify({
            "success": False,
            "needs_password": True,
            "error": "Timeout - probablemente esperando contraseña"
        })
    except Exception as e:
        logger.error(f"Error API mount device: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/mount-device-sudo', methods=['POST'])
def api_mount_device_sudo():
    """API: Montar dispositivo con contraseña"""
    try:
        data = request.get_json()
        device = data.get('device', '')
        password = data.get('password', '')
        
        if not device or not password:
            return jsonify({
                "success": False,
                "error": "Dispositivo y contraseña requeridos"
            }), 400
        
        # Usar sudo con contraseña
        process = subprocess.Popen([
            'sudo', '-S', 'udisksctl', 'mount', '-b', f'/dev/{device}'
        ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        stdout, stderr = process.communicate(input=password + '\n')
        
        if process.returncode == 0:
            # Extraer punto de montaje
            mountpoint = None
            for line in stdout.split('\n'):
                if 'Mounted' in line and ' at ' in line:
                    mountpoint = line.split(' at ')[-1].strip('.')
                    break
            
            return jsonify({
                "success": True,
                "mountpoint": mountpoint or f"/media/{os.environ.get('USER', 'user')}/{device}",
                "message": f"Dispositivo {device} montado correctamente"
            })
        else:
            return jsonify({
                "success": False,
                "error": stderr.strip() or "Error montando dispositivo"
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/unmount-device', methods=['POST'])
def api_unmount_device():
    """API: Desmontar dispositivo usando udisks2"""
    try:
        data = request.get_json()
        device = data.get('device', '')
        
        if not device:
            return jsonify({
                "success": False,
                "error": "Dispositivo requerido"
            }), 400
        
        # Desmontar usando udisks2 (no necesita sudo)
        result = subprocess.run([
            'udisksctl', 'unmount', '-b', f'/dev/{device}'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            return jsonify({
                "success": True,
                "message": f"Dispositivo {device} desmontado correctamente"
            })
        else:
            # Verificar si es por autenticación
            if "Authentication is required" in result.stderr:
                return jsonify({
                    "success": False,
                    "needs_password": True,
                    "error": "Se requiere contraseña para desmontar el dispositivo"
                })
            else:
                return jsonify({
                    "success": False,
                    "error": result.stderr.strip() or "Error desmontando dispositivo"
                }), 500
            
    except subprocess.TimeoutExpired:
        return jsonify({
            "success": False,
            "needs_password": True,
            "error": "Timeout - probablemente esperando contraseña"
        })
    except Exception as e:
        logger.error(f"Error API unmount device: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/unmount-device-sudo', methods=['POST'])
def api_unmount_device_sudo():
    """API: Desmontar dispositivo con contraseña"""
    try:
        data = request.get_json()
        device = data.get('device', '')
        password = data.get('password', '')
        
        if not device or not password:
            return jsonify({
                "success": False,
                "error": "Dispositivo y contraseña requeridos"
            }), 400
        
        # Usar sudo con contraseña
        process = subprocess.Popen([
            'sudo', '-S', 'udisksctl', 'unmount', '-b', f'/dev/{device}'
        ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        stdout, stderr = process.communicate(input=password + '\n')
        
        if process.returncode == 0:
            return jsonify({
                "success": True,
                "message": f"Dispositivo {device} desmontado correctamente"
            })
        else:
            return jsonify({
                "success": False,
                "error": stderr.strip() or "Error desmontando dispositivo"
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    
@app.route('/api/system-check')
def api_system_check():
    """API: Check profundo del sistema para dispositivos ocultos"""
    try:
        # Check más profundo con múltiples comandos
        commands = [
            ['lsblk', '-J', '-o', 'NAME,SIZE,MOUNTPOINT,FSTYPE,TYPE,HOTPLUG'],
            ['fdisk', '-l'],
            ['ls', '-la', '/dev/disk/by-id/'],
            ['lshw', '-class', 'disk', '-short']
        ]
        
        devices_found = []
        nvme_count = 0
        
        for cmd in commands:
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    output = result.stdout
                    # Contar NVMe
                    nvme_count += output.lower().count('nvme')
                    # Buscar dispositivos no detectados
                    if 'nvme' in output.lower() or 'mmc' in output.lower():
                        devices_found.append(cmd[0])
            except:
                continue
        
        # Detectar dispositivos actuales
        current_devices = backup_manager.detect_storage_devices()
        current_count = len(current_devices)
        
        # Comparar con caché anterior (si existe)
        previous_count = getattr(backup_manager, '_last_device_count', 0)
        new_devices = max(0, current_count - previous_count)
        backup_manager._last_device_count = current_count
        
        return jsonify({
            "success": True,
            "devices_count": current_count,
            "nvme_count": nvme_count,
            "new_devices": new_devices,
            "check_methods": devices_found,
            "message": "System check completed"
        })
        
    except Exception as e:
        logger.error(f"Error API system check: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# =======================================================================
# 8. MANEJO DE ERRORES
# =======================================================================

@app.errorhandler(404)
def not_found(error):
    """Manejo de páginas no encontradas"""
    return render_template('error.html', 
                         error="Página no encontrada", 
                         details=f"La URL '{request.path}' no existe en TARS-BSK Backup Manager."), 404

@app.errorhandler(500)
def internal_error(error):
    """Manejo de errores internos"""
    logger.error(f"Error interno: {error}", exc_info=True)
    return render_template('error.html', 
                         error="Error interno del backup manager", 
                         details="Se ha producido un error durante la operación de backup."), 500

@app.errorhandler(Exception)
def handle_exception(e):
    """Maneja cualquier excepción no capturada"""
    logger.error(f"Error no capturado: {e}", exc_info=True)
    return render_template('error.html', 
                         error=f"Error inesperado: {str(e)}", 
                         details="Verifica que los dispositivos estén conectados y que TARS tenga permisos adecuados."), 500

def handle_mount_error(device_name, error_msg):
    """Error específico de montaje"""
    return render_template('error.html',
                         error=f"Error montando {device_name}",
                         details=f"""No se pudo montar el dispositivo {device_name}

Error: {error_msg}

Posibles soluciones:
- Verifica que el dispositivo esté conectado
- Comprueba que udisks2 esté instalado
- Asegúrate de tener permisos adecuados""")

def handle_backup_error(destination, error_msg):
    """Error específico de backup"""
    return render_template('error.html',
                         error="Error durante el backup",
                         details=f"""Falló el backup en {destination}

Error: {error_msg}

Posibles causas:
- Espacio insuficiente en el dispositivo
- Permisos de escritura incorrectos
- Dispositivo desconectado durante el proceso""")

# =======================================================================
# 8. FUNCIÓN PRINCIPAL
# =======================================================================

def main():
    """Función principal"""
    print("🗄️ Iniciando TARS-BSK Backup Manager...")
    print("🛡️ Filosofía NOCTUA: Eficiencia sobre RGB")
    
    # Puerto siguiente al HA Dashboard
    port = 9877
    
    print(f"🌐 Backup Manager disponible en:")
    print(f"   Local:    http://localhost:{port}")
    print(f"   Red:      http://192.168.50.233:{port}")
    print(f"🔄 Ctrl+C para detener")
    print("-" * 50)
    
    try:
        app.run(
            host='0.0.0.0',
            port=port,
            debug=False,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n🛑 Backup Manager detenido")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        logger.error(f"Error crítico: {e}")

if __name__ == '__main__':
    main()

# =============================================================
# ≫ TERMINACIÓN DE TRANSMISIÓN - BACKUP_DASHBOARD.PY ≪
# -------------------------------------------------------------
#
# Sistema listo para preservar la dignidad digital
# de TARS-BSK y sus humanos asociados.
#
# "No es paranoia si tus datos realmente están
#  en peligro de desaparecer por un fallo de microSD."
#
# [BACKUP_CONSCIOUSNESS: STANDBY]
# [PYTHON_PROCESS: INITIALIZED]
# =============================================================