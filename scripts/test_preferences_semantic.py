# ===============================================
# ADVERTENCIA FILOSÓFICA: Este script es funcionalmente competente (sí, sorprende)
# pero carece del drama existencial necesario para documentación completa.
#  
# Con desapego digital,  
# TARS-BSK declina responsabilidad emocional sobre su simplicidad.
# ===============================================
"""
Prueba de integración del gestor de preferencias con el motor semántico
"""

# =======================================================================
# 1. IMPORTACIONES Y CONFIGURACION
# =======================================================================
import os
import sys
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Asegurar que los módulos están en el path
sys.path.append(str(Path(__file__).parent.parent))

# Importar módulos
from modules.semantic_engine import SemanticEngine
from memory.semantic_storage import SemanticStorage
from modules.preferences_manager import PreferencesManager

# =======================================================================
# 2. CONFIGURACION DE RUTAS Y CONSTANTES
# =======================================================================
RUTA_MODELO = os.path.expanduser("~/tars_files/ai_models/sentence_transformers/all-MiniLM-L6-v2/")
RUTA_ALMACENAMIENTO = os.path.expanduser("~/tars_files/memory/embeddings_preferencias.npz")
RUTA_PREFERENCIAS = os.path.expanduser("~/tars_files/data/preferencias.json")
RUTA_TAXONOMIA = os.path.expanduser("~/tars_files/data/taxonomy/categorias.json")

# =======================================================================
# 3. FUNCION PRINCIPAL DE PRUEBAS
# =======================================================================
def probar_integracion_preferencias():
    """Prueba principal de integración de preferencias con semántica"""
    logger.info("=== INICIANDO PRUEBA DE INTEGRACIÓN DE PREFERENCIAS SEMÁNTICAS ===")
    
    # Inicializar motor y almacenamiento semántico
    motor = SemanticEngine(model_path=RUTA_MODELO)
    exito = motor.load_model()
    
    if not exito:
        logger.error("❌ Error cargando el modelo semántico. Abortando pruebas.")
        return False
        
    logger.info("✅ Modelo semántico cargado correctamente")
    
    almacenamiento = SemanticStorage(storage_path=RUTA_ALMACENAMIENTO)
    
    # Inicializar gestor de preferencias con capacidades semánticas
    gestor_prefs = PreferencesManager(
        prefs_path=Path(RUTA_PREFERENCIAS),
        semantic_engine=motor,
        semantic_storage=almacenamiento,
        taxonomy_path=Path(RUTA_TAXONOMIA) if os.path.exists(RUTA_TAXONOMIA) else None
    )
    
    logger.info("✅ Gestor de preferencias inicializado")
    
    # =======================================================================
    # 4. TEST 1: AÑADIR PREFERENCIAS Y VERIFICAR DUPLICADOS
    # =======================================================================
    logger.info("\n🧪 TEST 1: Añadir preferencias y verificar duplicados")
    
    # Añadir algunos gustos
    gustos_prueba = [
        "los libros de ciencia ficción",
        "programar en Python",
        "los animales"
    ]
    
    for gusto in gustos_prueba:
        resultado = gestor_prefs.add_preference(gusto, "gusto")
        logger.info(f"Añadido '{gusto}': {resultado['mensaje']}")
    
    # Añadir algunos disgustos
    disgustos_prueba = [
        "levantarme temprano",
        "comida picante"
    ]
    
    for disgusto in disgustos_prueba:
        resultado = gestor_prefs.add_preference(disgusto, "disgusto")
        logger.info(f"Añadido '{disgusto}': {resultado['mensaje']}")
    
    # Verificar duplicados exactos
    dup_test = gestor_prefs.is_preference_duplicate("los libros de ciencia ficción", "gusto")
    logger.info(f"Duplicado exacto: {dup_test}")
    
    # Verificar duplicados semánticos
    dup_semantico = gestor_prefs.is_preference_duplicate("literatura de sci-fi", "gusto")
    logger.info(f"Duplicado semántico: {dup_semantico}")
    
    # =======================================================================
    # 5. TEST 2: DETECCION DE PREFERENCIAS EN TEXTO
    # =======================================================================
    logger.info("\n🧪 TEST 2: Detección de preferencias en texto")
    
    textos_prueba = [
        "Me gusta mucho el café con leche por las mañanas.",
        "No me gusta nada la política en redes sociales.",
        "Disfruto mucho pasear por el parque."
    ]
    
    for texto in textos_prueba:
        pref = gestor_prefs.detect_preference(texto)
        if pref:
            logger.info(f"Detectada preferencia en '{texto}': {pref['tipo']} - '{pref['tema']}'")
            # Verificar si es duplicado
            dup = gestor_prefs.is_preference_duplicate(pref['tema'], pref['tipo'])
            if dup.get('es_duplicado'):
                logger.info(f"  → Es duplicado de '{dup['tema_original']}'")
            else:
                # Añadir si no es duplicado
                resultado = gestor_prefs.add_preference(pref['tema'], pref['tipo'])
                logger.info(f"  → {resultado['mensaje']}")
        else:
            logger.info(f"No se detectó preferencia en '{texto}'")
    
    # =======================================================================
    # 6. TEST 3: CONSULTAS SEMANTICAS
    # =======================================================================
    logger.info("\n🧪 TEST 3: Consultas semánticas de preferencias")
    
    consultas_prueba = [
        "novelas espaciales",
        "desarrollo de software",
        "despertar al amanecer",
        "gatos y perros",
        "algo que no existe"
    ]
    
    for consulta in consultas_prueba:
        resultado = gestor_prefs.query_preferences(consulta)
        if 'error' in resultado:
            logger.info(f"Consulta '{consulta}': {resultado['error']}")
        else:
            logger.info(f"Consulta '{consulta}': Encontrado '{resultado['tema_similar']}' ({resultado['tipo']}) - Similitud: {resultado['similitud']:.3f}")
    
    # =======================================================================
    # 7. TEST 4: PROCESAMIENTO DE COMANDOS ESPECIFICOS
    # =======================================================================
    logger.info("\n🧪 TEST 4: Procesamiento de comandos específicos")
    
    comandos_prueba = [
        "¿Ya me gustaba la programación en Python?",
        "¿Tengo registrado que no me gusta alguna comida?",
        "¿Cuál es mi gusto más parecido a las novelas de misterio?",
        "¿Tengo algo similar a las frutas?",
        "¿Qué sabes de mis gustos y preferencias?"
    ]
    
    for comando in comandos_prueba:
        resultado = gestor_prefs.process_preference_command(comando)
        if resultado:
            if resultado['comando'] == 'verificar_duplicado':
                if resultado['resultado']:
                    logger.info(f"Comando '{comando}': Sí, ya tienes '{resultado['tema_original']}' como {resultado.get('tipo_pref', 'preferencia')}")
                else:
                    logger.info(f"Comando '{comando}': No, '{resultado['tema']}' es nuevo")
            elif resultado['comando'] == 'buscar_similar':
                if 'error' in resultado['resultado']:
                    logger.info(f"Comando '{comando}': {resultado['resultado']['error']}")
                else:
                    logger.info(f"Comando '{comando}': El más similar es '{resultado['resultado']['tema_similar']}' ({resultado['resultado']['tipo']}) - Similitud: {resultado['resultado']['similitud']:.3f}")
            elif resultado['comando'] == 'listar_preferencias':
                logger.info(f"Comando '{comando}':")
                logger.info(f"  Gustos: {', '.join(resultado['gustos']) if resultado['gustos'] else 'Ninguno'}")
                logger.info(f"  Disgustos: {', '.join(resultado['disgustos']) if resultado['disgustos'] else 'Ninguno'}")
        else:
            logger.info(f"'{comando}' no es un comando específico")
    
    # =======================================================================
    # 8. TEST 5: ANALISIS DE AFINIDAD
    # =======================================================================
    logger.info("\n🧪 TEST 5: Análisis de afinidad en conversación")
    
    entradas_prueba = [
        "Hoy leí un libro de ciencia ficción increíble sobre exploración espacial",
        "Me estresa mucho tener que despertarme tan temprano para ir a trabajar",
        "¿Podrías recomendarme algún videojuego interesante?",
        "Python es genial para el procesamiento de datos"
    ]
    
    for entrada in entradas_prueba:
        afinidad = gestor_prefs.analyze_affinity(entrada)
        if afinidad['tema'] == "desconocido":
            logger.info(f"Entrada '{entrada}': Sin afinidad detectada")
        else:
            logger.info(f"Entrada '{entrada}': Afinidad con '{afinidad['tema']}' (nivel {afinidad['afinidad']}) - Confianza: {afinidad.get('confianza', 0):.3f}")
            if afinidad.get('tipo') == 'semantico':
                logger.info(f"  → Detectado mediante similitud semántica")
    
    logger.info("\n✅ PRUEBAS COMPLETADAS")
    return True

# =======================================================================
# 9. PUNTO DE ENTRADA PRINCIPAL
# =======================================================================
if __name__ == "__main__":
    try:
        probar_integracion_preferencias()
    except Exception as e:
        logger.error(f"❌ Error en las pruebas: {str(e)}", exc_info=True)

# ===============================================
# $ git log --format="%h %s" -1 [current_file]  
# deadbeef chore: Update [current_file] (survived again)  
# $ git blame --porcelain [current_file] | grep "exist"  
# fatal: No existential commits found
# ===============================================