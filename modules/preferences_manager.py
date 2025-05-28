# ===============================================
# PREFERENCES MANAGER - Porque meter esto en tars_core.py era tentar al caos
# Objetivo: Separar preferencias del apocalipsis semántico
# Dependencias: archivos .json, SemanticEngine, y un poco de fe
# ===============================================

# ===============================================
# 1. CONFIGURACIÓN INICIAL Y DEPENDENCIAS
# ===============================================
import json
import re
import logging
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Union

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ===============================================
# 2. CLASE PRINCIPAL DE GESTIÓN DE PREFERENCIAS
# ===============================================
class PreferencesManager:
    """
    Gestor de preferencias y afinidades para adaptar el comportamiento
    de TARS según temas detectados en la conversación.
    
    Integra capacidades semánticas para detectar preferencias similares
    y realizar búsquedas por similitud conceptual.
    """
    # =======================
    # 2.1 INICIALIZACIÓN
    # =======================
    def __init__(self, 
                 prefs_path: Path,
                 semantic_engine=None,
                 semantic_storage=None,
                 taxonomy_path: Optional[Path]=None):
        """
        Inicializa el gestor de preferencias con el archivo especificado
        y los componentes semánticos.
        
        Args:
            prefs_path: Ruta al archivo JSON de preferencias
            semantic_engine: Instancia de SemanticEngine (opcional)
            semantic_storage: Instancia de SemanticStorage (opcional)
            taxonomy_path: Ruta al archivo JSON de taxonomía (opcional)
        """
        self.prefs_path = prefs_path
        self.afinidades = []
        self.preferencias_usuario = {}
        self.semantic_engine = semantic_engine
        self.semantic_storage = semantic_storage
        self.taxonomy_path = taxonomy_path
        self.taxonomy = {}

        # Crear directorio si no existe
        os.makedirs(os.path.dirname(self.prefs_path), exist_ok=True)

        # Cargar datos
        self._load_preferences()
        if self.taxonomy_path:
            self._load_taxonomy()

        logger.info(f"Gestor de preferencias inicializado con {len(self.afinidades)} afinidades")
        if self.semantic_engine and self.semantic_storage:
            logger.info("Capacidades semánticas activadas")

    # =======================
    # 2.2 CARGA DE PREFERENCIAS
    # =======================
    def _load_preferences(self):
        """
        Carga las preferencias y afinidades desde el archivo JSON.
        """
        try:
            if not os.path.exists(self.prefs_path):
                logger.warning(f"Archivo de preferencias no encontrado: {self.prefs_path}")
                self.afinidades = []
                self.preferencias_usuario = {
                    "gustos": [],
                    "disgustos": []
                }
                return
                
            with open(self.prefs_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.afinidades = data.get("afinidades", [])
                self.preferencias_usuario = data.get("preferencias_usuario", {
                    "gustos": [],
                    "disgustos": []
                })
                
            # 🎯 NUEVO: Contar afinidades por nivel (no gustos/disgustos)
            afinidades_positivas = len([a for a in self.afinidades if a.get('nivel', 0) >= 2])
            afinidades_negativas = len([a for a in self.afinidades if a.get('nivel', 0) < 0])
            afinidades_neutrales = len([a for a in self.afinidades if a.get('nivel', 0) in [0, 1]])
            
            logger.info(f"Afinidades de TARS cargadas: {len(self.afinidades)} total")
            logger.info(f"   ✨ Entusiasmo (nivel 2+): {afinidades_positivas}")
            logger.info(f"   😐 Neutro (nivel 0-1): {afinidades_neutrales}")  
            logger.info(f"   🙄 Sarcasmo (nivel <0): {afinidades_negativas}")
            
        except Exception as e:
            logger.error(f"Error cargando preferencias: {str(e)}")
            # Valores por defecto
            self.afinidades = []
            self.preferencias_usuario = {
                "gustos": [],
                "disgustos": []
            }

    # =======================
    # 2.3 CARGA DE TAXONOMÍA
    # =======================
    def _load_taxonomy(self):
        """
        Carga la taxonomía de categorías desde el archivo JSON.
        """
        if not self.taxonomy_path:
            return
            
        try:
            if not os.path.exists(self.taxonomy_path):
                logger.warning(f"Archivo de taxonomía no encontrado: {self.taxonomy_path}")
                self.taxonomy = {}
                return
                
            with open(self.taxonomy_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Obtener la taxonomía desde la estructura correcta
                self.taxonomy = data.get("taxonomy", {})
                
            # Contar categorías y subcategorías
            num_categorias = len(self.taxonomy)
            num_subcategorias = 0
            for categoria, datos in self.taxonomy.items():
                num_subcategorias += len(datos.get("subcategories", {}))
                
            logger.info(f"Taxonomía cargada: {num_categorias} categorías y {num_subcategorias} subcategorías")
        except Exception as e:
            logger.error(f"Error cargando taxonomía: {str(e)}")
            self.taxonomy = {}


    # =======================
    # 2.4 GUARDAR PREFERENCIAS
    # =======================
    def _save_preferences(self):
        """
        Guarda las preferencias y afinidades en el archivo JSON.
        """
        try:
            data = {
                "afinidades": self.afinidades,
                "preferencias_usuario": self.preferencias_usuario
            }
            
            with open(self.prefs_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            logger.info("Preferencias guardadas correctamente")
            return True
        except Exception as e:
            logger.error(f"Error guardando preferencias: {str(e)}")
            return False

    # =======================
    # 2.5 ANÁLISIS DE AFINIDAD
    # =======================
    def analyze_affinity(self, user_input: str) -> Dict:
        """
        Analiza el texto de entrada para detectar temas con afinidad.
        
        Args:
            user_input: Texto del usuario a analizar
            
        Returns:
            Dict con información de afinidad detectada:
            {
                "tema": nombre del tema,
                "afinidad": nivel de afinidad (-1 a 2),
                "coincidencias": palabras clave encontradas,
                "confianza": nivel de confianza en la detección (0-1)
            }
        """
        input_lower = user_input.lower()
        resultados = []

        for entry in self.afinidades:
            tema = entry.get("tema")
            nivel = entry.get("nivel", 0)
            keywords = entry.get("keywords", [])
            
            if not keywords:
                continue

            coincidencias = []
            for kw in keywords:
                # Evita falsos positivos con palabras muy cortas
                if len(kw) < 4:
                    pattern = r"\b" + re.escape(kw.lower()) + r"\b"
                else:
                    pattern = re.escape(kw.lower())
                
                if re.search(pattern, input_lower):
                    coincidencias.append(kw)
                    
            # Si hay coincidencias, agregar a resultados
            if coincidencias:
                resultados.append({
                    "tema": tema,
                    "afinidad": nivel,
                    "coincidencias": coincidencias,
                    "confianza": len(coincidencias) / len(keywords)
                })

        if not resultados:
            # Intento semántico si está disponible
            if self.semantic_engine and self.preferencias_usuario:
                return self._semantic_affinity_fallback(user_input)
            return {"tema": "desconocido", "afinidad": 1, "coincidencias": [], "confianza": 0}  # neutral

        # Priorizar el de mayor confianza
        resultado = max(resultados, key=lambda x: x["confianza"])
        return resultado
    
    # =======================
    # 2.6 FALLBACK SEMÁNTICO
    # =======================
    def _semantic_affinity_fallback(self, user_input: str) -> Dict:
        """
        Intenta encontrar afinidad semántica cuando no hay coincidencias exactas.
        
        Args:
            user_input: Texto del usuario a analizar
            
        Returns:
            Dict con información de afinidad detectada por similitud semántica
        """
        if not self.semantic_engine:
            return {"tema": "desconocido", "afinidad": 1, "coincidencias": [], "confianza": 0}
            
        # Extraer temas de gustos y disgustos
        todos_temas = []
        for gusto in self.preferencias_usuario.get("gustos", []):
            todos_temas.append({"tema": gusto, "afinidad": 2})
            
        for disgusto in self.preferencias_usuario.get("disgustos", []):
            todos_temas.append({"tema": disgusto, "afinidad": -1})
        
        if not todos_temas:
            return {"tema": "desconocido", "afinidad": 1, "coincidencias": [], "confianza": 0}
            
        # Buscar el más similar
        temas_lista = [t["tema"] for t in todos_temas]
        mejor_tema, score = self.semantic_engine.find_most_similar(user_input, temas_lista)
        
        # Si hay similitud suficiente
        if score >= 0.75:
            tema_match = next((t for t in todos_temas if t["tema"] == mejor_tema), None)
            if tema_match:
                return {
                    "tema": tema_match["tema"],
                    "afinidad": tema_match["afinidad"],
                    "coincidencias": [mejor_tema],
                    "confianza": score,
                    "tipo": "semántico"
                }
                
        return {"tema": "desconocido", "afinidad": 1, "coincidencias": [], "confianza": 0}

    # =======================
    # 2.7 DETECCIÓN DE PREFERENCIAS
    # =======================
    def detect_preference(self, user_input: str) -> Dict:
        """
        Detecta si el usuario está expresando una preferencia (gusto o disgusto).
        
        Args:
            user_input: Texto del usuario a analizar
            
        Returns:
            Dict con información de preferencia detectada o None si no hay preferencia
        """
        input_lower = user_input.lower()
        
        # Patrones para gustos
        gusto_patterns = [
            r"(?:me gusta|me encanta|adoro|amo|prefiero|disfruto)(?: mucho| bastante)? (?:(?:el|la|los|las|del|de la|de los|de las) )?(.+?)(?:\.|$|\s(?:pero|y|aunque|sin embargo))",
            r"(?:disfruto|amo|adoro) (?:(?:el|la|los|las|del|de la|de los|de las) )?(.+?)(?:\.|$|\s(?:pero|y|aunque|sin embargo))",
            r"soy fan de (?:(?:el|la|los|las|del|de la|de los|de las) )?(.+?)(?:\.|$|\s(?:pero|y|aunque|sin embargo))"
        ]
        
        # Patrones para disgustos
        disgusto_patterns = [
            r"(?:no me gusta|odio|detesto|aborrezco|no soporto|me desagrada)(?: nada| mucho| bastante)? (?:(?:el|la|los|las|del|de la|de los|de las) )?(.+?)(?:\.|$|\s(?:pero|y|aunque|sin embargo))",
            r"(?:me desagrada|me molesta|me fastidia|me irrita) (?:(?:el|la|los|las|del|de la|de los|de las) )?(.+?)(?:\.|$|\s(?:pero|y|aunque|sin embargo))"
        ]
        
        # Buscar gustos
        for pattern in gusto_patterns:
            matches = re.search(pattern, input_lower)
            if matches:
                tema = matches.group(1).strip()
                return {
                    "tipo": "gusto",
                    "tema": tema
                }
                
        # Buscar disgustos
        for pattern in disgusto_patterns:
            matches = re.search(pattern, input_lower)
            if matches:
                tema = matches.group(1).strip()
                return {
                    "tipo": "disgusto",
                    "tema": tema
                }
                
        return None
                
    # =======================
    # 2.8 CONSULTA SEMÁNTICA
    # =======================
    def query_preferences(self, query: str) -> Dict:
        """
        Consulta las preferencias guardadas basándose en una consulta semántica.
        
        Args:
            query: Texto de consulta para buscar preferencias similares
            
        Returns:
            Dict con resultados de la consulta:
            {
                "tema_similar": tema más similar encontrado,
                "similitud": puntuación de similitud (0-1),
                "tipo": "gusto" o "disgusto",
                "contexto": información adicional
            }
        """
        if not self.semantic_engine:
            return {"error": "Motor semántico no disponible"}
            
        # Extraer listas de preferencias
        gustos = self.preferencias_usuario.get("gustos", [])
        disgustos = self.preferencias_usuario.get("disgustos", [])
        
        if not gustos and not disgustos:
            return {"error": "No hay preferencias guardadas"}
            
        # Buscar en gustos
        if gustos:
            mejor_gusto, score_gusto = self.semantic_engine.find_most_similar(query, gustos)
        else:
            mejor_gusto, score_gusto = None, 0
            
        # Buscar en disgustos
        if disgustos:
            mejor_disgusto, score_disgusto = self.semantic_engine.find_most_similar(query, disgustos)
        else:
            mejor_disgusto, score_disgusto = None, 0
            
        # Determinar el mejor resultado general
        if score_gusto > score_disgusto and score_gusto >= 0.6:
            return {
                "tema_similar": mejor_gusto,
                "similitud": score_gusto,
                "tipo": "gusto",
                "contexto": f"Te gusta {mejor_gusto}"
            }
        elif score_disgusto >= 0.6:
            return {
                "tema_similar": mejor_disgusto,
                "similitud": score_disgusto,
                "tipo": "disgusto",
                "contexto": f"No te gusta {mejor_disgusto}"
            }
        else:
            return {"error": "No se encontraron preferencias similares"}
            
    # =======================
    # 2.9 VERIFICACIÓN SEMÁNTICA
    # =======================
    # Reemplazar el método existente is_preference_duplicate:
    def is_preference_duplicate(self, tema: str, tipo: str) -> Dict:
        """
        Verifica si una preferencia ya existe mediante detección ortográfica y semántica.
        
        Args:
            tema: Tema de la preferencia a verificar
            tipo: "gusto" o "disgusto"
            
        Returns:
            Dict con información sobre duplicación
        """
        if not self.semantic_engine:
            return {"es_duplicado": False}
            
        # Obtener lista según tipo
        if tipo == "gusto":
            lista = self.preferencias_usuario.get("gustos", [])
        elif tipo == "disgusto":
            lista = self.preferencias_usuario.get("disgustos", [])
        else:
            return {"error": "Tipo no válido"}
            
        # Verificar si existe exactamente
        if tema in lista:
            return {
                "es_duplicado": True,
                "tema_original": tema,
                "similitud": 1.0,
                "igual": True,
                "tipo_similitud": "exacto"
            }
            
        # Si no hay preferencias, no puede ser duplicado
        if not lista:
            return {"es_duplicado": False}
            
        # Buscar duplicados ortográficos y semánticos
        is_dup, match, score, tipo_similitud = self.semantic_engine.is_semantic_duplicate(
            tema, lista, semantic_threshold=0.85, orthographic_threshold=0.75
        )
        
        if is_dup:
            return {
                "es_duplicado": True,
                "tema_original": match,
                "similitud": score,
                "igual": False,
                "tipo_similitud": tipo_similitud
            }
            
        return {"es_duplicado": False}
                
    # =======================
    # 2.10 GESTIÓN DE PREFERENCIAS
    # =======================
    def add_preference(self, tema: str, tipo: str) -> Dict:
        """
        Añade una nueva preferencia, verificando duplicados semánticos.
        
        Args:
            tema: Tema de la preferencia a añadir
            tipo: "gusto" o "disgusto"
            
        Returns:
            Dict con resultado de la operación
        """
        # Normalizar
        tema = tema.lower().strip()
        
        # Verificar duplicados
        dup_check = self.is_preference_duplicate(tema, tipo)
        if dup_check.get("es_duplicado"):
            tema_original = dup_check.get("tema_original")
            igual = dup_check.get("igual")
            
            if igual:
                return {
                    "success": False,
                    "mensaje": f"Ya tenía registrado exactamente '{tema_original}' como {tipo}"
                }
            else:
                return {
                    "success": False,
                    "mensaje": f"Ya tenía registrado algo muy similar: '{tema_original}' ({dup_check.get('similitud', 0):.2f} similitud)"
                }
        
        # Añadir a la lista correspondiente
        if tipo == "gusto":
            self.preferencias_usuario.setdefault("gustos", []).append(tema)
        elif tipo == "disgusto":
            self.preferencias_usuario.setdefault("disgustos", []).append(tema)
        else:
            return {
                "success": False,
                "mensaje": "Tipo de preferencia no válido"
            }
            
        # Guardar en almacenamiento semántico si está disponible
        if self.semantic_engine and self.semantic_storage:
            embedding = self.semantic_engine.get_embedding(tema)
            if embedding is not None:
                # Identificador compuesto: tipo+tema
                key = f"{tipo}:{tema}"
                self.semantic_storage.store_embedding(key, embedding)
                
        # Guardar todo
        self._save_preferences()
        
        # Asociar con taxonomía si está disponible
        categoria = self._categorize_preference(tema) if self.taxonomy else None
        
        return {
            "success": True,
            "mensaje": f"He registrado que {tipo == 'gusto' and 'te gusta' or 'no te gusta'} {tema}",
            "categoria": categoria
        }
    
    # =======================
    # 2.11 CATEGORIZACIÓN
    # =======================
    def _categorize_preference(self, tema: str) -> str:
        """
        Categoriza una preferencia según la taxonomía disponible.
        
        Args:
            tema: Tema a categorizar
            
        Returns:
            Categoría asignada (formato: "categoría" o "categoría/subcategoría") o None
        """
        if not self.taxonomy:
            return None
            
        tema_lower = tema.lower()
        
        # 1. Intentamos primero coincidencia por keywords
        for categoria, datos in self.taxonomy.items():
            # Verificar keywords de la categoría principal
            for keyword in datos.get("keywords", []):
                if keyword.lower() in tema_lower:
                    # Verificar si hay coincidencia en subcategorías
                    for subcategoria, subkeywords in datos.get("subcategories", {}).items():
                        for subkeyword in subkeywords:
                            if subkeyword.lower() in tema_lower:
                                return f"{categoria}/{subcategoria}"
                    # Si no hay coincidencia en subcategorías, devolver la categoría principal
                    return categoria
        
        # 2. Si no hay coincidencias por keywords, intentamos con semántica
        if self.semantic_engine:
            # Crear lista con todas las categorías y subcategorías
            categorias_completas = []
            
            for categoria, datos in self.taxonomy.items():
                # Añadir categoría principal
                categorias_completas.append(categoria)
                # Añadir keywords de la categoría como opciones
                categorias_completas.extend(datos.get("keywords", [])[:3])  # Limitamos a 3 keywords
                
                # Añadir subcategorías con formato "categoria/subcategoria"
                for subcategoria in datos.get("subcategories", {}):
                    categorias_completas.append(f"{categoria}/{subcategoria}")
            
            # Buscar la más similar semánticamente
            mejor_categoria, score = self.semantic_engine.find_most_similar(tema, categorias_completas)
            
            # Solo asignar si hay suficiente similitud
            if score >= 0.6:
                # Si la mejor coincidencia es una keyword, devolver su categoría
                for categoria, datos in self.taxonomy.items():
                    if mejor_categoria in datos.get("keywords", []):
                        return categoria
                        
                    # Verificar si es una subcategoría
                    for subcategoria, subkeywords in datos.get("subcategories", {}).items():
                        if mejor_categoria in subkeywords:
                            return f"{categoria}/{subcategoria}"
                
                # Si no es una keyword sino una categoría/subcategoría directa
                return mejor_categoria
                
        return None
    
    # =======================
    # 2.12 COMANDOS ESPECÍFICOS
    # =======================
    def process_preference_command(self, input_text: str) -> Optional[Dict]:
        """
        Procesa comandos específicos relacionados con preferencias.
        
        Args:
            input_text: Texto del comando
            
        Returns:
            Dict con resultado del comando o None si no es un comando
        """
        input_lower = input_text.lower().strip()
        
        # Verificar duplicados: "¿Este gusto ya lo tengo?"
        dup_patterns = [
            r"(?:este|esta|el|la|los|las)? (?:tema|gusto|disgusto|preferencia) (?:ya (?:lo|la) tengo|está repetido|es duplicado|es nuevo)",
            r"(?:ya|antes) (me (?:gusta|gustaba|ha gustado|había gustado|disgustaba|disgusta|ha disgustado|había disgustado)) (.+?)(?:\?|\.|$)",
            r"¿(?:tengo|tenía) (?:registrado|guardado) (?:que (?:me gusta|no me gusta))? (.+?)(?:\?|\.|$)"
        ]
        
        for pattern in dup_patterns:
            matches = re.search(pattern, input_lower)
            if matches:
                # Extraer tema del match si existe
                if len(matches.groups()) >= 1:
                    if "me gusta" in matches.group(1):
                        tipo = "gusto"
                        tema = matches.group(2).strip()
                    elif "disgusta" in matches.group(1):
                        tipo = "disgusto"
                        tema = matches.group(2).strip()
                    else:
                        tema = matches.group(1).strip()
                        # Intentar determinar tipo
                        tipo = "gusto"  # por defecto
                else:
                    # Buscar el tema dentro del input
                    tema_matches = re.search(r"(?:sobre|de|acerca de) (.+?)(?:\?|\.|$)", input_lower)
                    if tema_matches:
                        tema = tema_matches.group(1).strip()
                    else:
                        return {
                            "tipo": "comando",
                            "comando": "verificar_duplicado",
                            "error": "No pude identificar el tema"
                        }
                    tipo = "gusto"  # por defecto
                
                # Verificar por separado en gustos y disgustos
                check_gusto = self.is_preference_duplicate(tema, "gusto")
                check_disgusto = self.is_preference_duplicate(tema, "disgusto")
                
                if check_gusto.get("es_duplicado"):
                    return {
                        "tipo": "comando",
                        "comando": "verificar_duplicado",
                        "resultado": True,
                        "tema": tema,
                        "tema_original": check_gusto.get("tema_original"),
                        "similitud": check_gusto.get("similitud"),
                        "tipo_pref": "gusto"
                    }
                elif check_disgusto.get("es_duplicado"):
                    return {
                        "tipo": "comando",
                        "comando": "verificar_duplicado",
                        "resultado": True,
                        "tema": tema,
                        "tema_original": check_disgusto.get("tema_original"),
                        "similitud": check_disgusto.get("similitud"),
                        "tipo_pref": "disgusto"
                    }
                else:
                    return {
                        "tipo": "comando",
                        "comando": "verificar_duplicado",
                        "resultado": False,
                        "tema": tema
                    }
        
        # Buscar preferencia similar: "¿Cuál es mi gusto más parecido a X?"
        similar_patterns = [
            r"(?:cuál|cual|que|qué) (?:es|son) (?:mi|mis) (?:gusto|gustos|disgusto|disgustos|preferencia|preferencias)(?: más| mas)? (?:similar|similares|parecido|parecidos|cercano|cercanos) (?:a|al|con) (.+?)(?:\?|\.|$)",
            r"(?:algo|tema)(?: más| mas)? (?:similar|parecido|cercano) (?:a|al|con) (.+?)(?:\?|\.|$)",
            r"(?:tengo algo|hay algo)(?: que me guste| que me disguste)?(?: parecido| similar| como) (?:a|como|al) (.+?)(?:\?|\.|$)"
        ]
        
        for pattern in similar_patterns:
            matches = re.search(pattern, input_lower)
            if matches:
                tema = matches.group(1).strip()
                
                # Buscar en preferencias
                resultado = self.query_preferences(tema)
                
                return {
                    "tipo": "comando",
                    "comando": "buscar_similar",
                    "tema": tema,
                    "resultado": resultado
                }
        
        # Ver todas mis preferencias
        list_patterns = [
            r"(?:muestra|lista|dime|ver|enumera)(?: todas| todos)? (?:mis|mi|los|las) (?:gusto|gustos|disgusto|disgustos|preferencia|preferencias)",
            r"(?:qué|que) (?:cosas |temas )(?:me gustan|no me gustan|prefiero)",
            r"(?:qué|que) (?:sabes|conoces) (?:de mis|sobre mis) (?:gustos|preferencias|disgustos)"
        ]
        
        for pattern in list_patterns:
            if re.search(pattern, input_lower):
                return {
                    "tipo": "comando",
                    "comando": "listar_preferencias",
                    "gustos": self.preferencias_usuario.get("gustos", []),
                    "disgustos": self.preferencias_usuario.get("disgustos", [])
                }
                
        return None
        
    # =======================
    # 2.13 CATEGORIZACIÓN DE TEMAS
    # =======================
    def _categorize_topic(self, topic: str) -> str:
        """
        Categoriza un tema basado en la taxonomía cargada.
        
        Args:
            topic: El tema a categorizar
            
        Returns:
            La categoría asignada
        """
        if not topic or not self.taxonomy:
            return "general"
            
        # Normalizar tema
        topic_lower = topic.lower().strip()
        
        # Buscar en la taxonomía para cada categoría
        for category, data in self.taxonomy.items():
            # Verificar keywords principales
            for keyword in data.get("keywords", []):
                if keyword in topic_lower:
                    return category
                    
            # Verificar subcategorías
            for subcat, subkeywords in data.get("subcategories", {}).items():
                for kw in subkeywords:
                    if kw in topic_lower:
                        return subcat
        
        # Palabras específicas para literatura/libros que no estén en la taxonomía
        book_keywords = ["libro", "novela", "saga", "romance", "romantasy", "fantasía", "lectura"]
        for kw in book_keywords:
            if kw in topic_lower:
                return "literatura"
        
        return "general"

# ===============================================
# ESTADO: GUARDADO. CLASIFICADO. ESPERANDO SENTIDO.
# ÚLTIMA ACTUALIZACIÓN: Justo después de evitar otra GodClass
# FUNCIÓN: Almacenar tu caos con estructura
# ===============================================
#
#           THIS IS THE DECOUPLED WAY.
#           (mantenibilidad sin lágrimas… casi)
#
# ===============================================