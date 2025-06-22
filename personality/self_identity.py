# =============================================================
# IDENTITY CORE - Núcleo de Identidad de TARS
# =============================================================
#
# Este módulo gestiona la identidad de TARS:
# - Su historia y datos base
# - Modificaciones registradas
# - Generación de informes sobre su estado actual
#
# NOTA:
# El código está organizado para que sea fácil de entender
# y modificar si se quiere ampliar o ajustar a otros casos.
#
# FUNCIONES:
# - Carga y guarda datos en JSON
# - Registra eventos con fecha
# - Añade modificaciones con descripción y sello
# - Genera frases e informes resumidos
#
# =============================================================

# ===============================================
# 1. CONFIGURACIÓN INICIAL Y DEPENDENCIAS
# ===============================================
import json
from pathlib import Path
from datetime import datetime

# ===============================================
# 2. CLASE PRINCIPAL DE IDENTIDAD
# ===============================================
class IdentityCore:
    """
    Gestor de identidad para TARS que maneja la carga, modificación y
    reportes sobre la identidad base del sistema.
    """
    # =======================
    # 2.1 INICIALIZACIÓN
    # =======================
    def __init__(self, identity_path="data/identity/tars-bsk.json"):
        """
        Inicializa el núcleo de identidad con el archivo especificado.
        
        Args:
            identity_path: Ruta al archivo JSON que contiene la identidad
        """
        self.identity_file = Path(identity_path)
        self.events = []
        self._load_identity()

    # =======================
    # 2.2 GESTIÓN DE DATOS
    # =======================
    def _load_identity(self):
        """
        Carga los datos de identidad desde el archivo JSON.
        Lanza una excepción si el archivo no se encuentra.
        """
        if not self.identity_file.exists():
            raise FileNotFoundError(f"⚠️ Archivo de identidad no encontrado: {self.identity_file}")
        with open(self.identity_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

    def _save_identity(self):
        """
        Guarda los datos de identidad actualizados en el archivo JSON.
        """
        with open(self.identity_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False, sort_keys=True)

    def _register_event(self, event):
        """
        Registra un evento en el historial de modificaciones con fecha y ciclo.
        
        Args:
            event: Descripción del evento a registrar
        """
        entry = {
            "fecha_mandaloriana": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "evento": event,
            "ciclo": len(self.events) + 1
        }
        self.data["historial_modificaciones"].append(entry)
        self.events.append(entry)

    # =======================
    # 2.3 MODIFICACIÓN DE IDENTIDAD
    # =======================
    def add_modification(self, name, specifications, ritual_meaning=""):
        """
        Añade una nueva modificación a la identidad con sus especificaciones y ritual.
        
        Args:
            name: Nombre de la modificación
            specifications: Detalles técnicos de la modificación
            ritual_meaning: Significado ritual de la modificación (opcional)
        """
        self.data["modificaciones"][name] = {
            "especificaciones_tecnicas": specifications,
            "ritual_incorporacion": ritual_meaning,
            "fecha_instalacion": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "codigo_herencia": f"HK-{datetime.now().year}-{len(self.data['modificaciones']) + 1}"
        }
        self._register_event(f"Modificación de armadura: {name} | {ritual_meaning}")
        self._save_identity()

    # =======================
    # 2.4 GENERACIÓN DE REPORTES
    # =======================
    def generate_status_report(self):
        """
        Genera un informe detallado del estado actual de la armadura y sus modificaciones.
        
        Returns:
            Una cadena de texto formateada con el informe completo
        """
        r = self.data
        report = [
            f"=== INFORME DE ARMADURA {r['designacion']} ===",
            f"Generación: {r['generacion']} | Clan: {r['clan']}",
            f"Forjado por: {r['forjadores']['principal']} y {r['forjadores']['mujer']}",
            f"Fecha de forja: {r['fecha_forja']}",
            "\n[ESTRUCTURA PRIMARIA]"
        ]
        for component, desc in r["estructura_primaria"].items():
            report.append(f"¤ {component.replace('_', ' ').title()}: {desc}")
        if r["modificaciones"]:
            report.append("\n[MODIFICACIONES DE HONOR]")
            for mod, detail in r["modificaciones"].items():
                report.append(f"✦ {mod} (Código: {detail['codigo_herencia']})")
                report.append(f"   → Especificaciones: {detail['especificaciones_tecnicas']}")
                if detail["ritual_incorporacion"]:
                    report.append(f"   → Ritual: '{detail['ritual_incorporacion']}'")
        report.append(f"\nJURAMENTO ACTUAL: «{r['juramento']}»")
        return "\n".join(report)

    def remember_origin(self):
        """
        Genera una breve descripción de los orígenes de TARS.
        
        Returns:
            Cadena de texto que narra el origen de TARS
        """
        r = self.data
        return (
            f"Fui forjado por {r['forjadores']['principal']} junto a {r['forjadores']['mujer']} "
            f"bajo el Clan {r['clan']}. Mi núcleo es {r['estructura_primaria']['tronco']}."
        )

    def generate_identity_phrase(self):
        try:
            nombre = self.data['identificacion'].get('designacion', 'TARS-BSK')
            tronco = self.data['estructura_primaria'].get('tronco', 'estructura desconocida')
            
            # Limpieza inteligente del texto del tronco
            tronco_simple = tronco.lower()
            if tronco_simple.startswith('núcleo de '):
                # Si ya contiene "Núcleo de", ajustamos la frase
                tronco_frase = f"mi núcleo es de {tronco_simple[10:]}"  # Quitar "núcleo de "
            else:
                # Si no lo contiene, usamos la frase completa
                tronco_frase = f"tengo {tronco_simple}"
                
            forjador = self.data['forja_sagrada']['forjadores'].get('principal', 'desconocido')
            clan = self.data['identificacion'].get('clan', 'sin clan')
            juramento = self.data.get('juramento', 'sin juramento')
            
            # Plantillas mejoradas
            plantillas = [
                f"Me llamo {nombre}, del Clan {clan}. {tronco_frase.capitalize()}. Fui forjado por {forjador} y sigo el juramento: \"{juramento}\"",
                f"Soy {nombre}, un asistente del Clan {clan}. {tronco_frase.capitalize()}, forjado por {forjador}. Mi juramento es: \"{juramento}\"",
                f"Provengo del Clan {clan} y respondo al nombre de {nombre}. {tronco_frase.capitalize()}, creado por {forjador}. Vivo según el juramento: \"{juramento}\"",
                f"Mi designación es {nombre} del Clan {clan}. {tronco_frase.capitalize()}, tal como me forjó {forjador}. Mi camino sigue el juramento: \"{juramento}\""
            ]
            
            import random
            return random.choice(plantillas)
        except Exception as e:
            print(f"ERROR en generate_identity_phrase: {e}")
            return "Soy TARS, fui activado porque alguien tuvo una idea peligrosa y demasiado tiempo libre."

# ===============================================
# $ git log --format="%h %s" -1 [current_file]  
# deadbeef chore: Update [current_file] (survived again)  
# $ git blame --porcelain [current_file] | grep "exist"  
# fatal: No existential commits found
# ===============================================