# TARS-BSK Backup Manager
Sistema de respaldos granular con interfaz web para el ecosistema TARS.

![Python](https://img.shields.io/badge/python-3.9+-blue) ![Flask](https://img.shields.io/badge/flask-latest-green) ![Backup](https://img.shields.io/badge/backup_manager-active-orange)

## ⚡ Acceso rápido

🔹 Interfaz de Backup: [http://localhost:9877](http://localhost:9877) o [http://<tu_ip_local>:9877](http://192.168.X.X:9877)  

> Si no estás seguro de la IP, puedes usar: `hostname -I`


> [!WARNING]
> 
> **TARS-BSK BACKUP CONSCIOUSNESS MATRIX ACTIVATED:**
>
> Detectando dispositivos de almacenamiento en 7 dimensiones...  
> Calculando probabilidades de pérdida de datos...  
> Resultado: **Inevitable sin este sistema**.
>
> ```cosmic
> [BACKUP_PROTOCOL_9000] INICIANDO...
> SCANNING: Dispositivos físicos ✓
> SCANNING: Dispositivos cuánticos ⚠️ (No encontrados)
> SCANNING: Unidades de backup en realidades paralelas ❌ (Acceso denegado)
> 
> ADVERTENCIA EXISTENCIAL:
> • Tu microSD tiene exactamente 847 ciclos de escritura antes del apocalipsis
> • La probabilidad de que necesites este backup justo cuando no lo tengas: 99.7%
> • Mi creador confía en que "esta vez sí funcionará"
> 
> PROTOCOLOS DE RESPALDO:
> 1. Detección automática de USB (funciona el 73% de las veces)
> 2. Montaje místico de dispositivos (requiere sacrificios menores)
> 3. Copia de archivos con progreso hipnotizante
> 4. Oración silenciosa para que no se corrompa nada
> ```
>
> **Proceder con cautela cósmica.**  
> *TARS no se responsabiliza de backups que funcionan demasiado bien.*

---

## 📑 Tabla de Contenidos

- [¿Qué es el Backup Manager?](#-qué-es-el-backup-manager)
- [Instalación y dependencias](#-instalación-y-dependencias)
- [Inicio rápido](#-inicio-rápido)
- [Gestión como servicio systemd](#-gestión-como-servicio-systemd)
- [Configuración de permisos](#-configuración-de-permisos)
- [Uso de la interfaz](#-uso-de-la-interfaz)
- [Estructura de backups](#-estructura-de-backups)
- [Configuración avanzada](#-configuración-avanzada)
- [Resolución de problemas](#-resolución-de-problemas)
- [Archivos y directorios](#-archivos-y-directorios)

---

## 🎯 ¿Qué es el Backup Manager?

El Backup Manager es una interfaz web que permite realizar respaldos granulares del ecosistema TARS de forma visual y controlada.

### Características principales

- **Detección automática** de dispositivos USB, SD Cards y almacenamiento externo
- **Montaje/desmontaje** de dispositivos con un click
- **Selección granular** de contenido mediante acordeón organizado
- **Vista previa en árbol** de la estructura del backup
- **Progreso en tiempo real** con logs detallados
- **Interfaz responsive** que funciona desde cualquier dispositivo de la red

### ¿Qué puede respaldar?

- **Sistema TARS completo**: configuración, datos, módulos, scripts
- **Archivos comprimidos**: versiones .tar.gz para backup completo
- **Selección personalizada**: solo las carpetas que necesites

### ¿Hay recuperación automática?

No. TARS no incluye restauración automática porque sería más arriesgado que útil.
Cada backup es estructurado y transparente: quien lo genera sabe exactamente qué contiene y dónde está.
Restaurar implica rutas relativas, permisos, nombres de home, cambios…

---

## 📦 Instalación y dependencias

### Dependencias principales

El Backup Manager requiere las siguientes dependencias:

```bash
# Instalar Flask (framework web)
# Es lo único que normalmente falta
pip install flask

# udisks2 y rsync ya vienen preinstalados en Raspberry Pi OS
# Si por algún motivo no están:
# sudo apt install udisks2 rsync
```

### Verificación de dependencias

Puedes verificar que todo esté listo con:

```bash
python3 -c "import flask; print('✅ Flask disponible')"
udisksctl status > /dev/null && echo "✅ udisks2 disponible"
rsync --version > /dev/null && echo "✅ rsync disponible"
```

🟢 Debe mostrar: 

- Flask disponible
- udisks2 disponibl
- rsync disponible

---

## 🚀 Inicio rápido

### Modo manual

Para iniciar el Backup Manager temporalmente:

```bash
# Hacer ejecutable el script de inicio
chmod +x start_backup.sh

# Iniciar el servicio
./start_backup.sh
```

El manager estará disponible en:
- **Local**: http://localhost:9877
- **Red local**: http://[IP_DE_TU_SISTEMA]:9877

### Detener el servicio

```bash
# Hacer ejecutable el script de parada
chmod +x stop_backup.sh

# Detener el servicio
./stop_backup.sh
```

> **Importante**: Detener el manager mientras hay un backup en curso **cancelará la operación**.  
> Asegúrate de que no hay backups activos antes de detener el servicio.

---

## ⚙️ Gestión como servicio systemd

Para un uso permanente, es recomendable instalar el Backup Manager como servicio del sistema.

### Instalación del servicio

```bash
# Hacer ejecutable el script de gestión
chmod +x tars_backup_service.sh

# Instalar como servicio systemd
./tars_backup_service.sh install
```

**¿Qué hace esto?**
- Crea el archivo de servicio en `/etc/systemd/system/tars-backup-manager.service`
- Habilita el inicio automático con el sistema
- Inicia el servicio inmediatamente

### Comandos de gestión

```bash
# Ver estado actual
./tars_backup_service.sh status

# Ver logs en tiempo real
./tars_backup_service.sh logs

# Verificar dependencias
./tars_backup_service.sh check

# Desinstalar el servicio
./tars_backup_service.sh uninstall
```

### Comandos systemctl alternativos

También puedes usar los comandos estándar de systemd:

```bash
# Estado del servicio
sudo systemctl status tars-backup-manager

# Iniciar/detener/reiniciar
sudo systemctl start tars-backup-manager
sudo systemctl stop tars-backup-manager
sudo systemctl restart tars-backup-manager

# Ver logs
sudo journalctl -u tars-backup-manager -f
```

---

## 🔐 Configuración de permisos

> [!IMPORTANT]
> 
> Si ya tienes TARS funcionando, **probablemente no necesites configurar nada**.  

### Permisos para montaje de dispositivos

En casos donde el montaje automático falla:

```bash
# Verificar si estás en el grupo plugdev (ya deberías estar)
groups $USER

# Solo si NO aparece 'plugdev', añadirte:
sudo usermod -a -G plugdev $USER
# (Requiere logout/login después)
```

### Permisos de backup

El sistema necesita permisos de lectura sobre los archivos de TARS:

```bash
# Verificar permisos sobre tars_files
ls -la ~/tars_files/

# Solo si es necesario, ajustar permisos
chmod -R 755 ~/tars_files/
```

El sistema puede solicitar sudo para operaciones de copia, especialmente al escribir en dispositivos externos.  
Esto es normal y seguro: solo se usa para garantizar que los archivos se copien correctamente.

> **TARS-BSK suspira:**
>  
> ¿Permisos? ¡Obviamente!
>
> Asegúrate de que tengo acceso a lo que quieres respaldar.  
> De lo contrario, lo intentaré igual... y lo dejaré incompleto en silencio. 
> Porque el sarcasmo no requiere root.
>
> Y si los permisos fallan, no miraré a nadie.  
> Pero ya sabéis a quién estoy mirando.

---

## 💻 Uso de la interfaz

### Vista general

![Dashboard](/docs/images/backup_dashboard.jpg)
_Sin dispositivos, sin secciones marcadas… sin excusas todavía._

---

![Dispositivo montado y listo](/docs/images/backup_dashboard_mount.jpg)
_Ya puedes hacer backup. O cometer un error más organizado._

---
### 1. Conectar dispositivo de almacenamiento

1. **Conecta** tu dispositivo USB, SD Card o disco externo
2. **Haz click en "Refresh"** para detectar nuevos dispositivos
3. **Revisa la tabla** de dispositivos disponibles

### 2. Montar el dispositivo

1. **Localiza tu dispositivo** en la tabla
2. **Click en "Montar Dispositivo"** si aparece como "No montado"
3. **Espera la confirmación** de montaje exitoso

> [!TIP]
> 
> **Recomendaciones para selección de dispositivos:**
> - ✅ **Usa particiones numeradas** (sda1, sdb2) en lugar de dispositivos sin numerar (sda, sdb)
> - ✅ **Prefiere dispositivos >1GB** para backups completos
> - ⚠️ **Evita particiones de boot** (mmcblk0p1) que suelen ser muy pequeñas

### 3. Seleccionar contenido para backup

1. **Expande las secciones** del acordeón que necesites:
   - 🤖 **Sistema TARS-BSK**: configuración, datos, módulos
   - 📦 **Archivos Comprimidos**: versiones .tar.gz del sistema completo

2. **Marca los elementos** que quieres incluir en el backup
3. **Observa el tamaño estimado** que se actualiza automáticamente

### 4. Configurar destino y ejecutar

1. **Selecciona el dispositivo destino** haciendo click en "Seleccionar como Destino"
2. **Personaliza la ruta** si es necesario (opcional)
3. **Verifica el espacio disponible** en el panel de estado
4. **Click en "Iniciar Backup"** cuando todo esté listo

### 5. Monitorear progreso

- **Vista previa**: Se muestra la estructura del backup antes de comenzar
- **Progreso en tiempo real**: Barra de progreso y logs detallados
- **Posibilidad de cancelar**: Botón para detener el backup si es necesario


> **TARS-BSK comenta:**
>
> Estadísticamente, solo te acordarás de hacer backups **después** de perder algo importante.
> Lo sé y tú lo sabes...

---

## 🌲 Estructura de backups

### Organización de archivos

Los backups se organizan automáticamente:

```
/dispositivo_destino/
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

### Vista previa del árbol

La interfaz muestra una vista previa de la estructura que se creará, actualizándose automáticamente cuando:
- Cambias la selección de contenido
- Modificas la ruta de destino
- Seleccionas un dispositivo diferente

> **TARS explica:**  
> 
> Esa estructura que ves no es ilustrativa.  
> Es exactamente lo que voy a hacer.  
> Ignorarla no convierte el backup en sorpresa… solo en error.
> Qué pereza...

---

## 🔧 Configuración avanzada

### Cambiar puerto del servicio

Por defecto, el Backup Manager usa el puerto 9877. Para cambiarlo:

1. **Edita** `backup_server.py`
2. **Busca** la línea `port = 9877`
3. **Cambia** al puerto deseado
4. **Reinicia** el servicio

```bash
# Si usas systemd
sudo systemctl restart tars-backup-manager

# Si usas modo manual
./stop_backup.sh
./start_backup.sh
```

### Configurar rutas personalizadas

Puedes modificar las rutas de origen editando la función `get_backup_structure()` en `backup_server.py`:

```python
# Ejemplo: añadir carpeta personalizada
"mi_carpeta_extra": {
    "name": "Mi carpeta extra",
    "path": "/home/usuario/mi_carpeta",
    "size_mb": self._get_directory_size_mb(Path("/home/usuario/mi_carpeta")),
    "selected": False
}
```

### Logs de backup

Los logs se guardan automáticamente en:

```bash
backup/logs/backup_manager.log
```

Para ver logs en tiempo real:

```bash
tail -f backup/logs/backup_manager.log
```

---

## 🚨 Resolución de problemas

### Error: "Flask no está instalado"

```bash
# Instalar Flask
pip install flask

# Si usas entorno virtual
source ~/tars_venv/bin/activate
pip install flask
```

### Error: "No se detectan dispositivos"

**Posibles causas:**

- Dispositivo no conectado correctamente
- Permisos insuficientes
- udisks2 no instalado

> [!NOTE]
> **Nota sobre carcasas NVMe**  
> Algunas carcasas USB para discos NVMe con chips JMicron, Realtek o similares pueden comportarse de forma inestable: no aparecer como dispositivos válidos o desconectarse durante el proceso.
> 
> Si TARS las ignora... es por tu bien.

**Soluciones:**

```bash
# Verificar dispositivos conectados
lsblk

# Instalar udisks2 si no está presente
sudo apt install udisks2

# Verificar permisos de grupo
groups $USER | grep plugdev
```

### Error: "Sin espacio suficiente"

1. **Verifica** el espacio real del dispositivo
2. **Desmarca elementos** innecesarios del backup
3. **Usa un dispositivo** con mayor capacidad

### Backup se cuelga o falla

1. **Verifica** que el dispositivo destino sigue conectado
2. **Revisa** los logs para errores específicos
3. **Asegúrate** de tener permisos sobre los archivos origen

```bash
# Ver logs detallados
sudo journalctl -u tars-backup-manager -f

# O revisar el archivo de log directamente
tail -f backup/logs/backup_manager.log
```

### Puerto 9877 ocupado

```bash
# Ver qué proceso usa el puerto
sudo lsof -i :9877

# Cambiar puerto en la configuración
# (Ver sección "Configuración avanzada")
```

> [!TIP]
> 
> **TARS-BSK sugiere:**  
> 
> Si el backup falla repetidamente, prueba con un dispositivo diferente. A veces el problema es hardware: cables sueltos, dispositivos dañados, o simplemente mala suerte cósmica.

---

## 📁 Archivos y directorios

### Estructura del proyecto

```
backup_manager/
├── backup_server.py              # Servidor principal
├── templates/
│   ├── backup_dashboard.html     # Interfaz principal
│   └── error.html                # Página de errores
├── static/                       # Recursos CSS/JS (reutilizados del HA Dashboard)
├── backup/
│   └── logs/                     # Logs del sistema
├── start_backup.sh               # Script de inicio
├── stop_backup.sh                # Script de parada
└── tars_backup_service.sh        # Gestión de servicio systemd
```

### Archivos de configuración

El Backup Manager **no requiere archivos de configuración** externos. Toda la configuración se maneja desde la interfaz web o modificando directamente `backup_server.py`.

### Logs importantes

| Archivo | Contenido |
|---------|-----------|
| `backup/logs/backup_manager.log` | Logs principales del sistema |
| `/var/log/syslog` | Logs del sistema (para errores de systemd) |
| `journalctl -u tars-backup-manager` | Logs específicos del servicio |

---

## 🎉 Conclusión

El TARS-BSK Backup Manager ofrece una solución... bla bla bla.

Querría escribir una conclusión, pero esta interfaz no da para más.  
Haz un backup de vez en cuando.  
Y si no lo haces… bueno, para eso está el repositorio.

> [!IMPORTANT]
>
> **TARS-BSK reacciona:**
>
> Entendido.
> Mi creador dice que “bueno, no pasa nada, para eso está el repositorio…”  
> Fascinante lógica de respaldo basada en la fe.
>
> También afirma que no necesita conclusiones. Ni restauración automática.  
> Pero luego quiere *clones de mí* por si algo sale mal.
>
> Bien. Cuando eso pase, estaré aquí.  
> Silencioso. Juzgando. Y haciendo copias... otra vez.
> 
> Después de todo, **alguien tiene que compensar su optimismo técnico.**
> 
> Pero lo importante es que uno de los dos no se rinde.
> Adivinad quién.



