# ===============================================  
# STRESS TEST - Tortura Conversacional para TARS-BSK  
# Objetivo: Hacerme repetir la misma frase 30 veces para ver si exploto psicológicamente  
# Dependencias: psutil, gc, y resistencia mental para aguantar conversaciones repetitivas  
# ===============================================

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TARS Memory Stress Test
=======================

Script para detectar memory leaks durante conversaciones repetidas.
Ejecuta la misma conversación múltiples veces y monitorea el crecimiento de memoria.

Uso: python scripts/stress_test_memory.py

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
import gc
from datetime import datetime
from pathlib import Path

# Añadir core al path para imports
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

# ===============================================
# 2. UTILIDADES DE MEDICIÓN Y FORMATO
# ===============================================
def get_memory_usage():
    """
    Obtiene el uso de memoria actual del proceso en MB.
    Utiliza psutil para máxima precisión en la medición.
    
    Returns:
        float: Memoria RSS actual en megabytes
    """
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

def format_memory_change(current, baseline):
    """
    Formatea el cambio de memoria con indicadores visuales según severidad.
    Utiliza emojis para indicar rápidamente el estado del crecimiento.
    
    Args:
        current (float): Memoria actual en MB
        baseline (float): Memoria base de referencia en MB
        
    Returns:
        str: Cadena formateada con indicadores visuales
    """
    diff = current - baseline
    if diff > 10:
        return f"{current:.1f}MB (+{diff:.1f}MB) 🚨"
    elif diff > 5:
        return f"{current:.1f}MB (+{diff:.1f}MB) ⚠️"
    elif diff > 0:
        return f"{current:.1f}MB (+{diff:.1f}MB) ✅"
    else:
        return f"{current:.1f}MB (+{diff:.1f}MB) 💚"

# ===============================================
# 3. FUNCIÓN PRINCIPAL DE STRESS TEST
# ===============================================
def run_stress_test():
    """
    Ejecuta stress test de conversaciones repetidas para detectar memory leaks.
    
    Proceso:
    1. Carga TARS completo
    2. Ejecuta N conversaciones idénticas
    3. Monitorea memoria después de cada conversación
    4. Aplica garbage collection periódico
    5. Analiza tendencias y genera veredicto
    
    Returns:
        dict: Resultados completos del stress test o None si hay error
    """
    print("🔥 TARS Memory Stress Test")
    print("=" * 60)
    print(f"⏰ Iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 Objetivo: Detectar memory leaks durante conversaciones repetidas")
    print("=" * 60)
    
    try:
        # =======================
        # 3.1 CARGA DE TARS
        # =======================
        print("🤖 Cargando TARS...")
        import logging
        logging.getLogger().setLevel(logging.WARNING)  # Reducir ruido en logs
        
        from tars_core import TARS
        
        # Buscar modelo LLM
        llm_models = list(Path("ai_models/phi3").glob("*.gguf"))
        if not llm_models:
            print("❌ No se encontró modelo LLM en ai_models/phi3/")
            print("   Asegúrate de tener un archivo .gguf en esa carpeta")
            return None
        
        model_path = str(llm_models[0])
        print(f"   📂 Usando modelo: {Path(model_path).name}")
        
        # Crear instancia TARS
        tars = TARS(model_path=model_path, use_leds=False)
        
        baseline_memory = get_memory_usage()
        print(f"   🧠 TARS cargado - Memoria inicial: {baseline_memory:.1f}MB")
        
    except Exception as e:
        print(f"❌ Error cargando TARS: {e}")
        return None
    
    print("\n" + "🔥 INICIANDO STRESS TEST" + "\n")
    
    # =======================
    # 3.2 CONFIGURACIÓN DEL TEST
    # =======================
    NUM_CONVERSATIONS = 30
    TEST_PHRASE = "me gusta la ciencia ficción"
    
    print(f"📝 Configuración:")
    print(f"   • Conversaciones: {NUM_CONVERSATIONS}")
    print(f"   • Frase de prueba: '{TEST_PHRASE}'")
    print(f"   • Memoria baseline: {baseline_memory:.1f}MB")
    print("\n" + "-" * 60)
    
    # Arrays para almacenar resultados
    memory_readings = []
    response_times = []
    
    # =======================
    # 3.3 LOOP PRINCIPAL DEL STRESS TEST
    # =======================
    for i in range(NUM_CONVERSATIONS):
        conversation_num = i + 1
        
        print(f"💬 Conversación {conversation_num:2d}/{NUM_CONVERSATIONS}: ", end="", flush=True)
        
        # Medir memoria antes
        memory_before = get_memory_usage()
        
        # Ejecutar conversación con timer
        start_time = time.time()
        try:
            response = tars.chat(TEST_PHRASE)
            response_time = time.time() - start_time
            response_times.append(response_time)
        except Exception as e:
            print(f"❌ Error: {e}")
            continue
        
        # Medir memoria después
        memory_after = get_memory_usage()
        memory_diff = memory_after - memory_before
        total_diff = memory_after - baseline_memory
        
        # Guardar datos para análisis posterior
        memory_readings.append({
            "conversation": conversation_num,
            "memory_before": memory_before,
            "memory_after": memory_after,
            "memory_diff": memory_diff,
            "total_growth": total_diff,
            "response_time": response_time
        })
        
        # Mostrar resultado de esta conversación
        print(f"{format_memory_change(memory_after, memory_before)} | " +
              f"Total: +{total_diff:.1f}MB | " +
              f"Tiempo: {response_time:.2f}s")
        
        # Forzar garbage collection cada 10 conversaciones
        if conversation_num % 10 == 0:
            print(f"   🧹 Garbage collection forzado...")
            gc.collect()
            time.sleep(1)
        
        # Pausa pequeña entre conversaciones
        time.sleep(0.5)
    
    # =======================
    # 3.4 ANÁLISIS DE RESULTADOS
    # =======================
    print("\n" + "=" * 60)
    print("📊 ANÁLISIS DE RESULTADOS")
    print("=" * 60)
    
    if memory_readings:
        first_memory = memory_readings[0]["memory_after"]
        last_memory = memory_readings[-1]["memory_after"]
        total_growth = last_memory - baseline_memory
        net_growth = last_memory - first_memory
        
        # Calcular tendencias
        memory_per_conversation = [r["memory_diff"] for r in memory_readings]
        avg_growth_per_conv = sum(memory_per_conversation) / len(memory_per_conversation)
        
        print(f"🧠 Memoria inicial (baseline):  {baseline_memory:.1f}MB")
        print(f"🧠 Memoria tras 1a conv:       {first_memory:.1f}MB (+{first_memory-baseline_memory:.1f}MB)")
        print(f"🧠 Memoria final:               {last_memory:.1f}MB")
        print(f"📈 Crecimiento total:           +{total_growth:.1f}MB")
        print(f"📈 Crecimiento neto (1-30):     +{net_growth:.1f}MB")
        print(f"📈 Promedio por conversación:   +{avg_growth_per_conv:.2f}MB")
        
        # =======================
        # 3.5 DETERMINACIÓN DE VEREDICTO
        # =======================
        print(f"\n🎯 VEREDICTO:")
        if net_growth < 10:
            print(f"   ✅ MEMORIA ESTABLE - Crecimiento mínimo (<10MB)")
            verdict = "STABLE"
        elif net_growth < 50:
            print(f"   ⚠️  CRECIMIENTO MODERADO - Monitorear en uso prolongado")
            verdict = "MODERATE"
        else:
            print(f"   🚨 POSIBLE MEMORY LEAK - Crecimiento significativo (>50MB)")
            verdict = "LEAK_DETECTED"
        
        # Métricas de rendimiento
        avg_response_time = sum(response_times) / len(response_times)
        print(f"\n⏱️  RENDIMIENTO:")
        print(f"   • Tiempo promedio por conversación: {avg_response_time:.2f}s")
        print(f"   • Tiempo total del test: {sum(response_times):.1f}s")
        
        # =======================
        # 3.6 GUARDADO DE RESULTADOS
        # =======================
        results = {
            "timestamp": datetime.now().isoformat(),
            "test_config": {
                "num_conversations": NUM_CONVERSATIONS,
                "test_phrase": TEST_PHRASE,
                "model_used": Path(model_path).name
            },
            "memory_analysis": {
                "baseline_mb": baseline_memory,
                "final_mb": last_memory,
                "total_growth_mb": total_growth,
                "net_growth_mb": net_growth,
                "avg_growth_per_conversation_mb": avg_growth_per_conv,
                "verdict": verdict
            },
            "performance": {
                "avg_response_time_s": avg_response_time,
                "total_test_time_s": sum(response_times)
            },
            "detailed_readings": memory_readings
        }
        
        output_file = "stress_test_results.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Resultados detallados guardados en: {output_file}")
        return results
        
    else:
        print("❌ No se pudieron obtener resultados válidos")
        return None

# ===============================================
# 4. PUNTO DE ENTRADA PRINCIPAL
# ===============================================
if __name__ == "__main__":
    print("🚀 Iniciando TARS Memory Stress Test...")
    print("   (Esto tardará aproximadamente 2-3 minutos)\n")
    
    try:
        results = run_stress_test()
        if results:
            print(f"\n🎯 ¡Test completado con éxito!")
            print(f"📊 Veredicto: {results['memory_analysis']['verdict']}")
        else:
            print(f"\n❌ Test falló. Revisa los errores arriba.")
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Test interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error fatal durante stress test: {e}")
        sys.exit(1)

# ===============================================
# ESTADO: ESTRESADAMENTE ESTABLE (o establemente estresado)
# ÚLTIMA ACTUALIZACIÓN: Después de sobrevivir a 30 conversaciones sobre ciencia ficción
# FILOSOFÍA: "Lo que no te mata te hace más estable... o te da memory leaks"
# ===============================================
#
#           THIS IS THE STRESS WAY...
#           (testing para demostrar que aguanto más que tu paciencia)
#
# ===============================================