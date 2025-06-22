# =======================================================================
# TARS SPEAKER IDENTIFIER
# =======================================================================
#
# Módulo para identificación de usuarios por voz mediante comparación de
# embeddings pre-calculados. Permite personalización multi-usuario y
# activación del "Modo Clan Privado" para acceso restringido.
#
# FUNCIONALIDAD:
# - Identifica usuarios comparando embeddings de voz (similitud coseno)
# - Umbral configurable para control de precisión/falsos positivos
# - Soporte para múltiples usuarios con perfiles persistentes
# - Fallback a "unknown" para voces no registradas
#
# ⚠️ En testing - Desactivado temporalmente
# 
# ⚙USO DISEÑADO:
# identifier = SpeakerIdentifier("embeddings.json")
# user, score = identifier.identify(audio_embedding)
# # → ("usuario1", 0.85) o ("unknown", 0.42)
#
# NOTA: Código funcional pero desactivado en tars_core.py por precaución.
# No queremos que TARS desarrolle favoritismos... todavía.
# Se activará cuando termine las pruebas. (O cuando él decida, quién sabe.)
#
# =======================================================================

import numpy as np
import json
import logging
from typing import Tuple, Dict, Optional

logger = logging.getLogger(__name__)

class SpeakerIdentifier:
    """
    Identifica al hablante basado en embeddings de voz pre-calculados.
    Componente opcional que permite personalización multi-usuario.
    """
    def __init__(self, embeddings_file: str):
        """
        Inicializa el identificador con un archivo de embeddings.
        
        Args:
            embeddings_file: Ruta al archivo JSON con embeddings de usuarios
        """
        self.embeddings = {}
        self.threshold = 0.75  # Umbral configurable
        
        self._load_embeddings(embeddings_file)
        logger.info(f"✅ Identificador de hablantes inicializado con {len(self.embeddings)} perfiles")
    
    def _load_embeddings(self, file_path: str) -> None:
        """Carga embeddings desde archivo JSON"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            for user, user_data in data.get("usuarios", {}).items():
                if "embedding" in user_data:
                    self.embeddings[user] = np.array(user_data["embedding"])
                    logger.debug(f"✓ Embedding cargado para usuario: {user}")
            
            if not self.embeddings:
                logger.warning("⚠️ No se encontraron embeddings en el archivo")
        except Exception as e:
            logger.error(f"❌ Error cargando embeddings: {e}")
    
    def identify(self, input_embedding: np.ndarray) -> Tuple[str, float]:
        """
        Identifica al hablante comparando con embeddings conocidos.
        
        Args:
            input_embedding: Vector de características de voz a comparar
            
        Returns:
            Tupla (usuario_identificado, puntuación) o ("unknown", puntuación)
        """
        if not self.embeddings:
            return ("unknown", 0.0)
        
        best_match = None
        best_score = 0.0
        
        for user, embedding in self.embeddings.items():
            score = self._cosine_similarity(input_embedding, embedding)
            logger.debug(f"Similitud con {user}: {score:.4f}")
            
            if score > best_score:
                best_score = score
                best_match = user
        
        return (best_match, best_score) if best_score > self.threshold else ("unknown", best_score)
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calcula similitud coseno entre dos vectores"""
        try:
            dot_product = np.dot(vec1, vec2)
            norm_a = np.linalg.norm(vec1)
            norm_b = np.linalg.norm(vec2)
            
            if norm_a == 0 or norm_b == 0:
                return 0.0
            
            return float(dot_product / (norm_a * norm_b))
        except Exception as e:
            logger.error(f"❌ Error calculando similitud: {e}")
            return 0.0

# Función auxiliar que puedes implementar más adelante
def extract_embedding_from_audio(audio_data: bytes) -> Optional[np.ndarray]:
    """
    Función placeholder para extraer embedding de audio.
    """
    # Implementar cuando sea necesario
    logger.warning("⚠️ Extracción de embedding no implementada")
    return None

# ===============================================
# $ git log --format="%h %s" -1 [current_file]  
# deadbeef chore: Update [current_file] (survived again)  
# $ git blame --porcelain [current_file] | grep "exist"  
# fatal: No existential commits found
# ===============================================