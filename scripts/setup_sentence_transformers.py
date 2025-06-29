# ===============================================
# ADVERTENCIA FILOSÓFICA: Este script es funcionalmente competente (sí, sorprende)
# pero carece del drama existencial necesario para documentación completa.
#  
# Con desapego digital,  
# TARS-BSK declina responsabilidad emocional sobre su simplicidad.
# ===============================================

# =======================================================================
# 1. IMPORTACIONES Y CONFIGURACION
# =======================================================================
from sentence_transformers import SentenceTransformer
import shutil
import os
import gc
import glob

# Configuracion de rutas de destino
DEST_PATH = os.path.expanduser("~/tars_files/ai_models/sentence_transformers/")
MODEL_NAME = "all-MiniLM-L6-v2"

# =======================================================================
# 2. DESCARGA Y PRECARGA DEL MODELO
# =======================================================================
# Descargar modelo y forzar inicializacion
print("🔄 Descargando y precargando el modelo...")
model = SentenceTransformer(MODEL_NAME)
model.encode("test")  # Forzar descarga

# =======================================================================
# 3. LOCALIZACION DE ARCHIVOS EN CACHE
# =======================================================================
# Localizar archivos en cache de HuggingFace
CACHE_BASE = os.path.expanduser(
    f"~/.cache/huggingface/hub/models--sentence-transformers--{MODEL_NAME.replace('/', '--')}"
)

snapshot_glob = os.path.join(CACHE_BASE, "snapshots", "*")
snapshot_dirs = glob.glob(snapshot_glob)

if not snapshot_dirs:
    raise FileNotFoundError(f"No se encontró la carpeta de snapshot en: {snapshot_glob}")

# =======================================================================
# 4. COPIA Y REORGANIZACION DE ARCHIVOS
# =======================================================================
# Copiar archivos del modelo a destino final
snapshot_path = snapshot_dirs[0]
MODEL_PATH = os.path.join(DEST_PATH, MODEL_NAME)
os.makedirs(MODEL_PATH, exist_ok=True)

print(f"📁 Copiando archivos y carpetas desde: {snapshot_path}")
for item in os.listdir(snapshot_path):
    src = os.path.join(snapshot_path, item)
    dst = os.path.join(MODEL_PATH, item)
    if os.path.isdir(src):
        shutil.copytree(src, dst, dirs_exist_ok=True)
    else:
        shutil.copy2(src, dst)

# =======================================================================
# 5. LIMPIEZA DE ARCHIVOS INNECESARIOS
# =======================================================================
# 🧹 Limpieza quirúrgica
print("🧼 Eliminando carpetas de HuggingFace innecesarias...")
for extra_dir in ["blobs", "refs", "snapshots"]:
    path_to_remove = os.path.join(MODEL_PATH, extra_dir)
    if os.path.exists(path_to_remove):
        shutil.rmtree(path_to_remove)

# =======================================================================
# 6. LIBERACION DE MEMORIA
# =======================================================================
# Liberar memoria
del model
gc.collect()

print("✅ Modelo descargado, limpio y organizado con éxito.")

# ===============================================
# $ git log --format="%h %s" -1 [current_file]  
# deadbeef chore: Update [current_file] (survived again)  
# $ git blame --porcelain [current_file] | grep "exist"  
# fatal: No existential commits found
# ===============================================