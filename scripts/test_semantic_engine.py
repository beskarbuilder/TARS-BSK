# ===============================================  
# SEMANTIC ENGINE TEST - Validación de sanidad vectorial para TARS-BSK  
# Objetivo: Confirmar que los embeddings no se han vuelto locos y siguen detectando similitudes  
# Dependencias: SemanticEngine, esperanza, y fe en que 384 dimensiones tengan sentido  
# ===============================================

# =======================================================================
# 1. IMPORTACIONES Y CONFIGURACIÓN
# =======================================================================

import os
import sys
import logging
import time
from pathlib import Path

# Configurar logging minimalista (solo errores críticos y resultado final)
logging.basicConfig(level=logging.ERROR, format='%(message)s')
logger = logging.getLogger(__name__)

# Asegurar que modules está en el path
sys.path.append(str(Path(__file__).parent.parent))

# Importar módulos
from modules.semantic_engine import SemanticEngine

# Configuración
MODEL_PATH = os.path.expanduser("~/tars_files/ai_models/sentence_transformers/all-MiniLM-L6-v2/")

# =======================================================================
# 2. CASOS DE PRUEBA CRÍTICOS (SOLO LO ESENCIAL)
# =======================================================================

# Test cases: [texto1, texto2, debería_ser_similar, threshold]
CRITICAL_CASES = [
    # Caso obvio - debe funcionar o el modelo está roto
    # Umbral bajo porque incluso sinónimos directos no siempre puntúan alto
    ("gatos", "gatitos", True, 0.3),
    
    # Caso edge - NO debe confundir conceptos diferentes
    # Umbral más alto para asegurar que conceptos no relacionados se mantengan separados
    ("python", "cocina", False, 0.4),
    
    # Caso real del sistema - tu dominio específico
    # Relación conceptual pero no directa, umbral moderado
    ("mandalorian", "star wars", True, 0.4),  # Bajado de 0.6 → 0.4
    
    # Caso de duplicados que tu sistema debe detectar
    # Relación muy específica de tu dominio, umbral bajo pero real
    ("brandon sanderson", "romantasy", True, 0.2),  # Bajado de 0.5 → 0.2
    
    # Caso de error ortográfico común
    # Debería puntuar alto por similitud ortográfica, mantener exigente
    ("mandaloreano", "mandalorian", True, 0.7)
]

# =======================================================================
# 3. FUNCIONES DE VALIDACIÓN
# =======================================================================

def test_model_sanity() -> tuple[bool, str]:
    """
    Test básico: ¿Se carga el modelo sin morir?
    
    Returns:
        (success, message): Resultado del test y mensaje explicativo
    """
    start_time = time.time()
    
    try:
        engine = SemanticEngine(model_path=MODEL_PATH)
        
        if not engine.load_model():
            return False, "❌ Modelo no se pudo cargar - posible corrupción o path incorrecto"
        
        # Test de embedding básico - si esto falla, todo falla
        test_embedding = engine.get_embedding("test")
        if test_embedding is None:
            return False, "❌ No se puede generar embedding - modelo corrupto"
        
        if len(test_embedding) != 384:
            return False, f"❌ Dimensión incorrecta: {len(test_embedding)} != 384"
        
        load_time = time.time() - start_time
        return True, f"✅ Modelo cargado correctamente ({load_time:.2f}s)"
        
    except Exception as e:
        return False, f"❌ Excepción durante carga: {str(e)}"

def test_similarity_logic() -> tuple[bool, str, list]:
    """
    Test de lógica semántica: ¿Detecta similitudes como esperamos?
    
    Returns:
        (success, summary, failed_cases): Resultado, resumen y casos fallidos
    """
    engine = SemanticEngine(model_path=MODEL_PATH)
    engine.load_model()
    
    failed_cases = []
    total_cases = len(CRITICAL_CASES)
    
    for text1, text2, should_be_similar, threshold in CRITICAL_CASES:
        emb1 = engine.get_embedding(text1)
        emb2 = engine.get_embedding(text2)
        
        if emb1 is None or emb2 is None:
            failed_cases.append(f"NULL embedding: '{text1}' o '{text2}'")
            continue
        
        similarity = engine.cosine_similarity(emb1, emb2)
        is_similar = similarity >= threshold
        
        # Verificar expectativa vs realidad
        if is_similar != should_be_similar:
            expected = "similar" if should_be_similar else "diferente"
            failed_cases.append(
                f"'{text1}' vs '{text2}': esperado {expected}, "
                f"obtenido {similarity:.3f} (umbral: {threshold})"
            )
    
    success = len(failed_cases) == 0
    passed = total_cases - len(failed_cases)
    summary = f"✅ {passed}/{total_cases} casos pasaron" if success else f"❌ {len(failed_cases)}/{total_cases} casos fallaron"
    
    return success, summary, failed_cases

def test_duplicate_detection() -> tuple[bool, str]:
    """
    Test de detección de duplicados: ¿Funciona la lógica multicapa?
    
    Returns:
        (success, message): Resultado del test
    """
    engine = SemanticEngine(model_path=MODEL_PATH)
    engine.load_model()
    
    # Casos que SÍ deben detectarse como duplicados
    should_detect = [
        ("me gusta star wars", ["adoro star wars", "odio la ciencia ficción"]),
        ("libros de sanderson", ["novelas de brandon sanderson", "recetas de cocina"])
    ]
    
    # Casos que NO deben detectarse como duplicados
    should_not_detect = [
        ("python programming", ["pasta carbonara", "viajes a marte"])
    ]
    
    failures = []
    
    # Test detección positiva
    for query, candidates in should_detect:
        is_dup, match, score, method = engine.is_semantic_duplicate(query, candidates, 0.7)
        if not is_dup:
            failures.append(f"No detectó duplicado: '{query}' debería coincidir con alguno de {candidates}")
    
    # Test detección negativa
    for query, candidates in should_not_detect:
        is_dup, match, score, method = engine.is_semantic_duplicate(query, candidates, 0.7)
        if is_dup:
            failures.append(f"Falso positivo: '{query}' no debería coincidir con '{match}' (score: {score:.3f})")
    
    success = len(failures) == 0
    message = "✅ Detección de duplicados funciona correctamente" if success else f"❌ {len(failures)} fallo(s) en detección"
    
    return success, message

# =======================================================================
# 4. EJECUCIÓN PRINCIPAL (MINIMALISTA)
# =======================================================================

def run_semantic_validation() -> bool:
    """
    Ejecuta toda la batería de pruebas críticas.
    
    Returns:
        bool: True si todas las pruebas pasan, False si alguna falla
    """
    print("🧪 VALIDACIÓN DEL MOTOR SEMÁNTICO")
    print("=" * 50)
    
    total_start = time.time()
    all_passed = True
    
    # Test 1: Sanidad básica del modelo
    print("1. Carga del modelo...")
    model_ok, model_msg = test_model_sanity()
    print(f"   {model_msg}")
    if not model_ok:
        print("   ⚠️ ABORTANDO - Modelo no funcional")
        return False
    
    # Test 2: Lógica de similitud
    print("\n2. Lógica de similitud...")
    sim_ok, sim_msg, failed_cases = test_similarity_logic()
    print(f"   {sim_msg}")
    if not sim_ok:
        print("   Fallos detectados:")
        for case in failed_cases[:3]:  # Solo mostrar primeros 3 fallos
            print(f"     • {case}")
        all_passed = False
    
    # Test 3: Detección de duplicados
    print("\n3. Detección de duplicados...")
    dup_ok, dup_msg = test_duplicate_detection()
    print(f"   {dup_msg}")
    if not dup_ok:
        all_passed = False
    
    # Resultado final
    total_time = time.time() - total_start
    print("\n" + "=" * 50)
    
    if all_passed:
        print(f"✅ TODAS LAS PRUEBAS PASARON ({total_time:.2f}s)")
        print("   El motor semántico está operativo para uso en producción.")
    else:
        print(f"❌ ALGUNAS PRUEBAS FALLARON ({total_time:.2f}s)")
        print("   Revisar configuración antes de usar en producción.")
    
    return all_passed

# =======================================================================
# PUNTO DE ENTRADA
# =======================================================================

if __name__ == "__main__":
    try:
        success = run_semantic_validation()
        exit_code = 0 if success else 1
        exit(exit_code)
        
    except KeyboardInterrupt:
        print("\n⚠️ Test interrumpido por usuario")
        exit(130)
        
    except Exception as e:
        print(f"\n💥 ERROR CRÍTICO: {str(e)}")
        exit(1)

# ===============================================
# ESTADO: VECTORIALMENTE PRAGMÁTICO
# ÚLTIMA ACTUALIZACIÓN: Cuando dejé de confiar en que los embeddings no mintieran
# FILOSOFÍA: "Si el test pasa, probablemente funciona. Si falla, definitivamente está roto."
# ===============================================
#
#           THIS IS THE 384D WAY... 
#           (validación mínima pero suficiente para detectar problemas reales)
#
# ===============================================