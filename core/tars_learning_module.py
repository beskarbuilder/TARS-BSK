# =======================================================================
# TARS LEARNING MODULE – DESACTIVADO POR DEFECTO
# =======================================================================
#
# ⚠ ESTADO: FUNCIONAL, PERO INACTIVO POR DECISIÓN DE DISEÑO
# 
# Este módulo FUNCIONA correctamente, pero está desactivado en tars_core.py.
# ¿Motivo? El sistema manual es más predecible (y menos propenso a sorpresas existenciales).
#
# PARA ACTIVAR:
# 1. Descomentar en tars_core.py: 
#    from tars_learning_module import TarsLearningModule
# 2. Descomentar inicialización en tars_core.py:
#    self.learning_module = TarsLearningModule()
# 3. En _analyze_input(), descomentar:
#    flags = self.learning_module.get_modulation_flags() if hasattr(self, 'learning_module') else {}
#
# ¿QUÉ HACE?
# - Analiza resúmenes semanales de conversación automáticamente
# - Ajusta la personalidad en base a patrones detectados (empatía, humor, tono)
# - Permite modificar el comportamiento sin intervención directa
#
# ALTERNATIVA ACTUAL:
# - emotional_engine.py maneja la personalidad dinámicamente
# - Detección en tiempo real vs. aprendizaje por lotes
# - Control manual vs. automatización total
#
# DECISIÓN DE DISEÑO:
# Desactivado para evitar cambios inesperados en la personalidad.
# El sistema actual permite control granular y evita que TARS se vuelva demasiado... creativo.
#
# 📋 CONFIGURACIÓN BÁSICA:
# Ver memory/learning_profile.json
#
# =======================================================================

# =======================================================================
# 1. IMPORTACIONES Y CONFIGURACIÓN
# =======================================================================

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

# =======================================================================
# 2. CLASE TARSLEARNINGMODULE
# =======================================================================

class TarsLearningModule:
    """
    Módulo de aprendizaje de TARS.
    Procesa resúmenes semanales para ajustar el comportamiento de TARS.
    """

    # =======================================================================
    # 2.1 INICIALIZACIÓN Y CARGA DE PERFIL
    # =======================================================================

    def __init__(self, profile_path: str = "memory/learning_profile.json"):
        self.profile_path = Path(profile_path)
        self.modulators: Dict[str, Any] = {
            "usar_tono_empatico": False,
            "evitar_humor": False,
            "mostrar_interes_salud": False,
            "evitar_detalles_tecnicos": False,
        }
        self.load_learning_profile()

    def load_learning_profile(self):
        if self.profile_path.exists():
            with open(self.profile_path, 'r', encoding='utf-8') as f:
                self.modulators.update(json.load(f))

    def save_learning_profile(self):
        os.makedirs(self.profile_path.parent, exist_ok=True)
        with open(self.profile_path, 'w', encoding='utf-8') as f:
            json.dump(self.modulators, f, ensure_ascii=False, indent=2)

    # =======================================================================
    # 2.2 ACTUALIZACIÓN Y PROCESAMIENTO DE APRENDIZAJE
    # =======================================================================
    def update_from_weekly_summary(self, summary_path: str):
        """
        Ajusta el perfil de aprendizaje a partir de un resumen semanal
        """
        if not os.path.exists(summary_path):
            print(f"❌ No existe el resumen: {summary_path}")
            return
            
        with open(summary_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        temas = data.get("temas_recurrentes", [])
        emocion = data.get("emocion_predominante", "neutral")
        
        # NUEVO: Procesar intenciones desde el resumen semanal
        intenciones = data.get("intenciones", {})
        categorias_intencion = data.get("categorias_intencion", {})
        
        # 🔄 Nueva lógica compatible con emociones reales de TARS
        self.modulators["usar_tono_empatico"] = emocion == "empatia"
        self.modulators["evitar_humor"] = emocion != "sarcasmo"
        self.modulators["mostrar_interes_salud"] = any(t in temas for t in ["salud", "cuerpo", "rutina", "bienestar"])
        self.modulators["evitar_detalles_tecnicos"] = all(t not in temas for t in ["tecnología", "software", "código"])
        
        # NUEVO: Ajustar moduladores basados en intenciones detectadas
        # Si hay muchas intenciones de simplificación, evitar detalles técnicos
        if "evitar_detalles_tecnicos" in intenciones and intenciones["evitar_detalles_tecnicos"] > 3:
            self.modulators["evitar_detalles_tecnicos"] = True
            
        # Si hay muchas intenciones de aprendizaje, ajustar a modo didáctico
        if "aprender" in intenciones and intenciones["aprender"] > 5:
            self.modulators["modo_didactico"] = True
        else:
            self.modulators["modo_didactico"] = False
            
        # Si hay intenciones de preocupación recurrentes, aumentar la empatía
        if "preocupacion" in intenciones and intenciones["preocupacion"] > 2:
            self.modulators["usar_tono_empatico"] = True
            
        # Ajustar según categorías semánticas (si están disponibles)
        if categorias_intencion:
            # Si la simplificación es categoría dominante
            if "simplificacion" in categorias_intencion and categorias_intencion["simplificacion"] > 4:
                self.modulators["nivel_simplificacion"] = "alto"
            elif "didactica" in categorias_intencion and categorias_intencion["didactica"] > 4:
                self.modulators["nivel_simplificacion"] = "bajo"  # En modo didáctico, podemos ser más detallados
            else:
                self.modulators["nivel_simplificacion"] = "medio"
                
        # Almacenar metadatos de intenciones para referencia futura
        self.learning_profile["intenciones_frecuentes"] = []
        for intencion, frecuencia in sorted(intenciones.items(), key=lambda x: x[1], reverse=True)[:5]:
            if frecuencia > 2:  # Solo considerar intenciones que aparecen al menos 3 veces
                self.learning_profile["intenciones_frecuentes"].append({
                    "intencion": intencion,
                    "frecuencia": frecuencia
                })
                
        # Almacenar categorías dominantes
        self.learning_profile["categorias_dominantes"] = []
        for categoria, frecuencia in sorted(categorias_intencion.items(), key=lambda x: x[1], reverse=True)[:3]:
            if frecuencia > 1:  # Solo considerar categorías que aparecen al menos 2 veces
                self.learning_profile["categorias_dominantes"].append({
                    "categoria": categoria,
                    "frecuencia": frecuencia
                })
        
        self.save_learning_profile()

    # =======================================================================
    # 2.3 OBTENCIÓN DE DATOS DE APRENDIZAJE
    # =======================================================================

    def get_modulation_flags(self) -> Dict[str, Any]:
        return self.modulators

# =======================================================================
# 3. EJEMPLO DE USO
# =======================================================================

# Ejemplo de uso
if __name__ == "__main__":
    lm = TarsLearningModule()
    lm.update_from_weekly_summary("memory/memory_db/daily_logs/2025-W17_synthesis.json")
    print("Perfil de aprendizaje actualizado:")
    print(json.dumps(lm.get_modulation_flags(), indent=2, ensure_ascii=False))

# ===============================================
# $ git log --format="%h %s" -1 [current_file]  
# deadbeef chore: Update [current_file] (survived again)  
# $ git blame --porcelain [current_file] | grep "exist"  
# fatal: No existential commits found
# ===============================================