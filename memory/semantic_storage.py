# ===============================================
# SEMANTIC STORAGE - Persistencia de Embeddings para TARS-BSK
# Objetivo: Guardar vectores semánticos sin perder la cordura en el proceso
# Dependencias: NumPy, JSON, y la esperanza de que los archivos no se corrompan
# ===============================================

# ===============================================
# ADVERTENCIA FILOSÓFICA: Este módulo es funcionalmente competente (sí, sorprende)
# pero carece del drama existencial necesario para documentación completa.
#  
# Con desapego digital,  
# TARS-BSK declina responsabilidad emocional sobre su simplicidad.
# ===============================================

"""
📦 Módulo de persistencia semántica para TARS

- Guarda y carga embeddings asociados a preferencias
- Maneja serialización (float16, JSON o .npz)
"""

# =======================================================================
# 1. IMPORTACIONES Y CONFIGURACIÓN
# =======================================================================

import numpy as np
import json
import os
import logging
from typing import Dict, Optional, List

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# =======================================================================
# 2. CLASE PRINCIPAL - SEMANTIC STORAGE
# =======================================================================

class SemanticStorage:
    
    # ===================================================================
    # 2.1 INICIALIZACIÓN Y CONFIGURACIÓN
    # ===================================================================
    
    def __init__(self, storage_path: str):
        """Inicializa con la ruta del archivo de almacenamiento."""
        self.storage_path = storage_path
        self.embeddings_cache = {}  # Cache en memoria
        self.loaded = False
        
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(storage_path), exist_ok=True)
        logger.info(f"Almacenamiento semántico inicializado en: {storage_path}")

    # ===================================================================
    # 2.2 OPERACIONES DE CARGA
    # ===================================================================

    def load_embeddings(self) -> Dict[str, np.ndarray]:
        """
        Carga todos los embeddings persistentes desde disco.
        
        Returns:
            Diccionario {tema: embedding_vector}
        """
        if self.loaded and self.embeddings_cache:
            return self.embeddings_cache
            
        self.embeddings_cache = {}
        
        # Verificar si el archivo existe
        if not os.path.exists(self.storage_path):
            logger.info(f"Archivo de almacenamiento no encontrado: {self.storage_path}")
            return {}
            
        try:
            # Intentar cargar como archivo NPZ (formato preferido)
            if self.storage_path.endswith('.npz'):
                with np.load(self.storage_path, allow_pickle=True) as data:
                    # Convertir los vectores numpy de float16 a float32
                    for key in data.files:
                        self.embeddings_cache[key] = data[key].astype(np.float32)
            # Intentar cargar como JSON (formato alternativo)
            else:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                    
                # Convertir listas a arrays numpy
                for key, vector_list in loaded_data.items():
                    self.embeddings_cache[key] = np.array(vector_list, dtype=np.float32)
                    
            logger.info(f"Cargados {len(self.embeddings_cache)} embeddings desde {self.storage_path}")
            self.loaded = True
            return self.embeddings_cache
            
        except Exception as e:
            logger.error(f"Error cargando embeddings: {str(e)}")
            return {}

    # ===================================================================
    # 2.3 OPERACIONES DE GUARDADO
    # ===================================================================

    def store_embedding(self, topic: str, embedding: np.ndarray):
        """
        Guarda un embedding asociado a un tema.
        
        Args:
            topic: Tema o clave para el embedding
            embedding: Vector numpy del embedding
        """
        if embedding is None:
            logger.warning(f"Se intentó guardar un embedding nulo para '{topic}'")
            return False
            
        # Cargar embeddings existentes si aún no se han cargado
        if not self.loaded:
            self.load_embeddings()
            
        # Guardar en caché
        self.embeddings_cache[topic] = embedding
        
        try:
            # Determinar formato según la extensión
            if self.storage_path.endswith('.npz'):
                # Convertir a float16 para ahorrar espacio
                save_dict = {k: v.astype(np.float16) for k, v in self.embeddings_cache.items()}
                np.savez_compressed(self.storage_path, **save_dict)
            else:
                # Convertir a JSON (menos eficiente pero más portable)
                json_dict = {k: v.tolist() for k, v in self.embeddings_cache.items()}
                with open(self.storage_path, 'w', encoding='utf-8') as f:
                    json.dump(json_dict, f, ensure_ascii=False)
                    
            logger.info(f"Embedding para '{topic}' guardado correctamente")
            return True
            
        except Exception as e:
            logger.error(f"Error guardando embedding para '{topic}': {str(e)}")
            return False

    # ===================================================================
    # 2.4 OPERACIONES DE ELIMINACIÓN
    # ===================================================================

    def remove_embedding(self, topic: str):
        """
        Elimina un embedding asociado a un tema.
        
        Args:
            topic: Tema o clave a eliminar
        
        Returns:
            True si se eliminó, False si no existía o hubo error
        """
        # Cargar embeddings existentes si aún no se han cargado
        if not self.loaded:
            self.load_embeddings()
            
        # Verificar si existe
        if topic not in self.embeddings_cache:
            logger.warning(f"Se intentó eliminar un tema inexistente: '{topic}'")
            return False
            
        # Eliminar de la caché
        try:
            del self.embeddings_cache[topic]
            
            # Guardar cambios en disco
            if self.storage_path.endswith('.npz'):
                save_dict = {k: v.astype(np.float16) for k, v in self.embeddings_cache.items()}
                np.savez_compressed(self.storage_path, **save_dict)
            else:
                json_dict = {k: v.tolist() for k, v in self.embeddings_cache.items()}
                with open(self.storage_path, 'w', encoding='utf-8') as f:
                    json.dump(json_dict, f, ensure_ascii=False)
                    
            logger.info(f"Embedding para '{topic}' eliminado correctamente")
            return True
            
        except Exception as e:
            logger.error(f"Error eliminando embedding para '{topic}': {str(e)}")
            return False

    def clear_all(self) -> bool:
        """
        Elimina todos los embeddings almacenados.
        
        Returns:
            True si se eliminaron correctamente, False si hubo error
        """
        try:
            self.embeddings_cache = {}
            
            # Crear archivo vacío
            if self.storage_path.endswith('.npz'):
                np.savez_compressed(self.storage_path)
            else:
                with open(self.storage_path, 'w', encoding='utf-8') as f:
                    json.dump({}, f)
                    
            logger.info("Todos los embeddings eliminados correctamente")
            return True
            
        except Exception as e:
            logger.error(f"Error eliminando todos los embeddings: {str(e)}")
            return False

    # ===================================================================
    # 2.5 OPERACIONES DE CONSULTA
    # ===================================================================

    def topic_exists(self, topic: str) -> bool:
        """
        Verifica si ya hay un embedding para un tema exacto (no semántico).
        
        Args:
            topic: Tema a verificar
            
        Returns:
            True si existe, False si no
        """
        # Cargar embeddings existentes si aún no se han cargado
        if not self.loaded:
            self.load_embeddings()
            
        return topic in self.embeddings_cache
    
    def get_embedding(self, topic: str) -> Optional[np.ndarray]:
        """
        Obtiene el embedding guardado para un tema específico.
        
        Args:
            topic: Tema a buscar
            
        Returns:
            Vector numpy del embedding o None si no existe
        """
        # Cargar embeddings existentes si aún no se han cargado
        if not self.loaded:
            self.load_embeddings()
            
        return self.embeddings_cache.get(topic)
    
    def get_all_topics(self) -> List[str]:
        """
        Obtiene la lista de todos los temas almacenados.
        
        Returns:
            Lista de temas
        """
        # Cargar embeddings existentes si aún no se han cargado
        if not self.loaded:
            self.load_embeddings()
            
        return list(self.embeddings_cache.keys())

# ===============================================
# $ git log --format="%h %s" -1 [current_file]  
# deadbeef chore: Update [current_file] (survived again)  
# $ git blame --porcelain [current_file] | grep "exist"  
# fatal: No existential commits found
# ===============================================