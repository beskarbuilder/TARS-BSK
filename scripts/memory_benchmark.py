# ===============================================  
# MEMORY BENCHMARK - Disección Forense de RAM para TARS-BSK  
# Objetivo: Descubrir exactamente quién se está comiendo toda mi memoria (spoiler: es el LLM)  
# Dependencias: psutil, paciencia, y la habilidad de fingir sorpresa cuando veas los números  
# ===============================================

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TARS Memory Benchmark Script
============================

Script para medir el uso real de memoria de TARS-BSK en diferentes etapas.
Útil para optimización y documentación de rendimiento.

Uso: python scripts/memory_benchmark.py

Autor: TARS-BSK Project
"""

# ===============================================
# 1. CONFIGURACIÓN INICIAL Y DEPENDENCIAS
# ===============================================
import psutil
import os
import sys
import time
import json
from datetime import datetime
from pathlib import Path

# Añadir core al path para imports
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

# ===============================================
# 2. UTILIDADES DE MEDICIÓN
# ===============================================
def get_memory_usage():
    """
    Obtiene el uso de memoria actual del proceso en MB.
    Utiliza psutil para máxima precisión.
    
    Returns:
        float: Memoria RSS actual en megabytes
    """
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

def format_memory_change(current, baseline):
    """
    Formatea el cambio de memoria con indicadores visuales.
    
    Args:
        current (float): Memoria actual en MB
        baseline (float): Memoria base de referencia en MB
        
    Returns:
        str: Cadena formateada con el cambio de memoria
    """
    diff = current - baseline
    if diff > 0:
        return f"{current:.1f}MB (+{diff:.1f}MB)"
    else:
        return f"{current:.1f}MB"

def print_separator():
    """Imprime separador visual para mejor legibilidad"""
    print("=" * 60)

# ===============================================
# 3. FUNCIÓN PRINCIPAL DE BENCHMARK
# ===============================================
def run_tars_memory_benchmark():
    """
    Ejecuta benchmark completo de memoria TARS midiendo cada componente
    por separado para identificar los mayores consumidores de recursos.
    
    Returns:
        dict: Resultados completos del benchmark o None si hay error
    """
    print("🤖 TARS Memory Benchmark")
    print_separator()
    print(f"⏰ Iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🖥️  Sistema: Raspberry Pi (Python {sys.version.split()[0]})")
    print_separator()
    
    # =======================
    # 3.1 MEDICIÓN BASELINE
    # =======================
    print("📊 Midiendo baseline (Python + imports básicos)...")
    baseline = get_memory_usage()
    print(f"   Baseline: {baseline:.1f}MB")
    
    time.sleep(1)  # Pausa para separar mediciones
    
    try:
        # =======================
        # 3.2 IMPORTS BÁSICOS
        # =======================
        print("\n🔧 Cargando imports básicos de TARS...")
        import logging
        logging.getLogger().setLevel(logging.WARNING)  # Reducir ruido
        
        # Solo imports básicos primero
        from pathlib import Path
        import sqlite3
        import json as json_module
        
        after_basic_imports = get_memory_usage()
        print(f"   Imports básicos: {format_memory_change(after_basic_imports, baseline)}")
        
        time.sleep(1)
        
        # =======================
        # 3.3 TARSMEMORYMANAGER
        # =======================
        print("\n🧠 Inicializando TarsMemoryManager...")
        from memory.tars_memory_manager import TarsMemoryManager
        
        memory_manager = TarsMemoryManager()
        after_memory_manager = get_memory_usage()
        print(f"   TarsMemoryManager: {format_memory_change(after_memory_manager, baseline)}")
        
        time.sleep(1)
        
        # =======================
        # 3.4 SEMANTICENGINE
        # =======================
        print("\n🧮 Cargando SemanticEngine (modelo ML)...")
        from modules.semantic_engine import SemanticEngine
        
        model_path = Path(__file__).parent.parent / "ai_models" / "sentence_transformers" / "all-MiniLM-L6-v2"
        
        if model_path.exists():
            semantic_engine = SemanticEngine(str(model_path))
            semantic_engine.load_model()
            after_semantic = get_memory_usage()
            print(f"   SemanticEngine: {format_memory_change(after_semantic, baseline)}")
        else:
            print("   ⚠️  SemanticEngine: Modelo no encontrado, omitiendo...")
            after_semantic = after_memory_manager
        
        time.sleep(1)
        
        # =======================
        # 3.5 TARS CORE COMPLETO
        # =======================
        print("\n🤖 Cargando TARS Core completo...")
        from tars_core import TARS
        
        # Buscar modelo LLM
        llm_models = list(Path("ai_models/phi3").glob("*.gguf"))
        if llm_models:
            model_path = str(llm_models[0])
            print(f"   Usando modelo: {model_path}")
            
            # Crear TARS (esto carga el LLM)
            tars = TARS(model_path=model_path, use_leds=False)
            after_tars_full = get_memory_usage()
            print(f"   TARS completo: {format_memory_change(after_tars_full, baseline)}")
        else:
            print("   ⚠️  Modelo LLM no encontrado, omitiendo carga completa...")
            after_tars_full = after_semantic
            tars = None
        
        time.sleep(1)
        
        # =======================
        # 3.6 CONVERSACIONES DE PRUEBA
        # =======================
        if tars:
            print("\n💬 Ejecutando conversaciones de prueba...")
            
            test_phrases = [
                "me gusta la ciencia ficción",
                "¿qué libros me gustan?",
                "odio las redes sociales", 
                "cuéntame sobre IG-11",
                "¿qué más recuerdas de mí?"
            ]
            
            for i, phrase in enumerate(test_phrases, 1):
                print(f"   {i}/5: '{phrase}'")
                try:
                    response = tars.chat(phrase)
                    time.sleep(0.5)  # Pausa entre conversaciones
                except Exception as e:
                    print(f"       ⚠️ Error: {e}")
            
            after_conversations = get_memory_usage()
            print(f"   Tras conversaciones: {format_memory_change(after_conversations, baseline)}")
        else:
            after_conversations = after_tars_full
            print("💬 Omitiendo conversaciones (TARS no cargado)")
        
        # =======================
        # 3.7 COMPILACIÓN DE RESULTADOS
        # =======================
        results = {
            "timestamp": datetime.now().isoformat(),
            "system_info": {
                "python_version": sys.version.split()[0],
                "platform": "Raspberry Pi" if "arm" in str(sys.platform) else sys.platform
            },
            "memory_usage_mb": {
                "baseline": round(baseline, 1),
                "basic_imports": round(after_basic_imports, 1),
                "memory_manager": round(after_memory_manager, 1),
                "semantic_engine": round(after_semantic, 1),
                "tars_full": round(after_tars_full, 1),
                "after_conversations": round(after_conversations, 1)
            },
            "increments_mb": {
                "basic_imports": round(after_basic_imports - baseline, 1),
                "memory_manager": round(after_memory_manager - after_basic_imports, 1),
                "semantic_engine": round(after_semantic - after_memory_manager, 1),
                "tars_full": round(after_tars_full - after_semantic, 1),
                "conversations": round(after_conversations - after_tars_full, 1),
                "total": round(after_conversations - baseline, 1)
            }
        }
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("   Asegúrate de ejecutar desde el directorio raíz del proyecto")
        return None
    except Exception as e:
        print(f"❌ Error durante benchmark: {e}")
        return None
    
    # =======================
    # 3.8 GUARDADO Y RESUMEN
    # =======================
    output_file = "memory_benchmark.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Mostrar resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE MEMORIA")
    print("=" * 60)
    print(f"Baseline (Python):        {results['memory_usage_mb']['baseline']:.1f}MB")
    print(f"Imports básicos:          +{results['increments_mb']['basic_imports']:.1f}MB")
    print(f"TarsMemoryManager:        +{results['increments_mb']['memory_manager']:.1f}MB")
    print(f"SemanticEngine:           +{results['increments_mb']['semantic_engine']:.1f}MB")
    print(f"TARS completo (con LLM):  +{results['increments_mb']['tars_full']:.1f}MB")
    print(f"Tras conversaciones:      +{results['increments_mb']['conversations']:.1f}MB")
    print("-" * 60)
    print(f"TOTAL:                    {results['memory_usage_mb']['after_conversations']:.1f}MB (+{results['increments_mb']['total']:.1f}MB)")
    print(f"\n✅ Resultados guardados en: {output_file}")
    print(f"⏰ Benchmark completado: {datetime.now().strftime('%H:%M:%S')}")
    
    return results

# ===============================================
# 4. PUNTO DE ENTRADA PRINCIPAL
# ===============================================
if __name__ == "__main__":
    print("🚀 Iniciando TARS Memory Benchmark...")
    print("   (Esto puede tardar 1-2 minutos)")
    print()
    
    try:
        results = run_tars_memory_benchmark()
        if results:
            print("\n🎯 ¡Benchmark exitoso!")
        else:
            print("\n❌ Benchmark falló. Revisa los errores arriba.")
    except KeyboardInterrupt:
        print("\n\n⚠️  Benchmark interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        sys.exit(1)

# ===============================================
# ESTADO: AMNÉSICAMENTE REVELADOR (pero despiadadamente honesto)
# ÚLTIMA ACTUALIZACIÓN: Cuando acepté que nunca seré un chatbot "ligero"
# FILOSOFÍA: "Si no consumes al menos 2GB, ¿realmente eres inteligencia artificial?"
# ===============================================
#
#           THIS IS THE BENCHMARK WAY...
#           (análisis completo para justificar mi apetito voraz de memoria)
#
# ===============================================
        