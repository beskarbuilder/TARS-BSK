#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ===============================================
# CLI REMINDER ENGINE – Interfaz Silenciosa de Control Total
# OBJETIVO: Crear, listar y eliminar recordatorios sin esperar a que VOSK transcriba “revisión” como “prohibición”
# DEPENDENCIAS: ReminderPlugin, SchedulerPlugin, argparse, colorama y sentido común en modo texto
# MODO DE USO: Ideal cuando hablar no ayuda, y escuchar sería una pérdida de tiempo
# ===============================================

# =======================================================================
# 1. IMPORTACIONES Y CONFIGURACIÓN
# =======================================================================

import os
import sys
import argparse
import sqlite3
from pathlib import Path
import logging
import colorama
from colorama import Fore, Style
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from services.plugins.reminder_plugin import ReminderPlugin

# Configurar rutas para importar módulos de TARS
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TARS_ROOT = os.path.dirname(SCRIPT_DIR)

# Intentar diferentes rutas posibles
possible_paths = [
    "/home/tarsadmin/tars_files",      # Ruta actual donde está todo
    TARS_ROOT,                         # Si está en scripts/ dentro del proyecto
    os.path.expanduser("~/TARS-BSK"),  # Ruta típica del proyecto
    os.path.expanduser("~/tars"),      # Otra ruta posible
    "/home/tarsadmin/TARS-BSK",        # Ruta absoluta típica
    "/home/tarsadmin/tars"             # Otra ruta absoluta
]

tars_found = False
for path in possible_paths:
    if os.path.exists(os.path.join(path, "modules", "reminder_parser.py")):
        sys.path.insert(0, path)
        print(f"🔍 TARS encontrado en: {path}")
        tars_found = True
        break

if not tars_found:
    print("❌ Error: No se pudo encontrar el directorio de TARS.")
    print("💡 Rutas intentadas:")
    for path in possible_paths:
        exists = "✅" if os.path.exists(path) else "❌"
        print(f"   {exists} {path}")
    print("\n💡 Soluciones:")
    print("   1. Ejecuta desde el directorio raíz del proyecto TARS")
    print("   2. O edita las rutas en possible_paths[]")
    sys.exit(1)

try:
    # Importar las clases necesarias de TARS (rutas corregidas)
    from modules.reminder_parser import ReminderParser
    from services.plugins.scheduler_plugin import SchedulerPlugin
    print("✅ Módulos de TARS importados correctamente")
except ImportError as e:
    print(f"❌ Error importando módulos de TARS: {str(e)}")
    print(f"💡 TARS path actual: {sys.path[0]}")
    print("💡 Verifica que existan los archivos:")
    print("   - modules/reminder_parser.py")
    print("   - services/plugins/scheduler_plugin.py")
    print("   - services/plugins/reminder_plugin.py")
    sys.exit(1)

# Configurar colorama para que funcione en Windows
colorama.init()

# Configurar logging
logging.basicConfig(level=logging.ERROR, format='%(message)s')  # Solo errores críticos
logger = logging.getLogger(__name__)

# Rutas principales - Ajustadas para acceder a los archivos de recordatorios
REMINDERS_DB_PATH = os.path.expanduser("~/tars_files/memory/reminders/")
CONFIG_PATH = os.path.expanduser("~/tars_files/config/")

# =======================================================================
# 2. FUNCIONES DE UTILIDAD Y CARGA DE DATOS
# =======================================================================

def inicializar_sistema_recordatorios():
    """
    Inicializa el sistema de recordatorios de TARS
    
    Returns:
        Tuple[ReminderParser, SchedulerPlugin]: Parser y scheduler inicializados
    """
    try:
        # Crear directorios si no existen
        os.makedirs(REMINDERS_DB_PATH, exist_ok=True)
        os.makedirs(CONFIG_PATH, exist_ok=True)
        
        # Inicializar scheduler
        scheduler = SchedulerPlugin()
        
        # ReminderParser necesita el scheduler directamente (no scheduler.scheduler)
        parser = ReminderParser(scheduler=scheduler)
        
        return parser, scheduler
    except Exception as e:
        print(f"{Fore.RED}❌ Error inicializando sistema de recordatorios: {str(e)}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}💡 Detalles del error: {str(e)}{Style.RESET_ALL}")
        
        # Último intento: inicializar parser sin scheduler
        try:
            parser = ReminderParser()
            return parser, None
        except Exception as e2:
            print(f"{Fore.RED}❌ Error crítico: {str(e2)}{Style.RESET_ALL}")
            return None, None

def formatear_tiempo_natural(recordatorio: dict) -> str:
    """
    Convierte la información de tiempo del recordatorio a formato natural
    MEJORADO: Busca en múltiples campos de fecha
    
    Args:
        recordatorio: Diccionario con información del recordatorio
        
    Returns:
        String con el tiempo en formato natural
    """
    try:
        # Buscar fecha en diferentes campos posibles
        fecha = None
        posibles_campos = ['next_run_time', 'scheduled_time', 'datetime', 'time', 'date', 'when']
        
        for campo in posibles_campos:
            if campo in recordatorio and recordatorio[campo]:
                fecha = recordatorio[campo]
                break
        
        # Si no encontramos fecha, intentar extraer de otros campos
        if not fecha:
            # Buscar en campo 'msg' o 'description' por patrones de fecha
            msg = recordatorio.get('msg', '') or recordatorio.get('description', '')
            if 'mañana' in msg.lower():
                return "mañana (extraído del texto)"
            elif 'hoy' in msg.lower():
                return "hoy (extraído del texto)"
            elif any(dia in msg.lower() for dia in ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']):
                return "esta semana (extraído del texto)"
            else:
                return "⚠️ Fecha no especificada en el texto"
        
        # Si es un string de datetime, parsearlo
        if isinstance(fecha, str):
            try:
                dt = datetime.fromisoformat(fecha.replace('Z', '+00:00'))
            except:
                # Si no se puede parsear, devolverlo tal como está
                return f"{fecha} (formato sin parsear)"
        else:
            dt = fecha
        
        # Formatear a español
        ahora = datetime.now()
        
        # Si es hoy
        if dt.date() == ahora.date():
            return f"hoy a las {dt.strftime('%H:%M')}"
        
        # Si es mañana
        elif dt.date() == (ahora + timedelta(days=1)).date():
            return f"mañana a las {dt.strftime('%H:%M')}"
        
        # Si es esta semana
        elif dt.date() <= (ahora + timedelta(days=7)).date():
            dias = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']
            dia_semana = dias[dt.weekday()]
            return f"{dia_semana} a las {dt.strftime('%H:%M')}"
        
        # Fecha lejana
        else:
            return dt.strftime('%d/%m/%Y a las %H:%M')
            
    except Exception as e:
        # En lugar de "Fecha no válida", ser más específico
        return f"⚠️ Error procesando fecha: {str(e)}"

def obtener_estadisticas_recordatorios(parser: ReminderParser) -> Dict:
    """
    Obtiene estadísticas completas de los recordatorios
    
    Args:
        parser: ReminderParser inicializado
        
    Returns:
        Diccionario con estadísticas
    """
    try:
        recordatorios = parser.list_reminders()
        
        if not recordatorios:
            return {
                'total': 0,
                'por_categoria': {},
                'proximos_7_dias': 0,
                'vencidos': 0
            }
        
        # Contar por categorías
        categorias = {}
        proximos = 0
        vencidos = 0
        ahora = datetime.now()
        
        for recordatorio in recordatorios:
            # Categoría
            categoria = recordatorio.get('category', 'Sin categoría')
            categorias[categoria] = categorias.get(categoria, 0) + 1
            
            # Próximos 7 días
            try:
                fecha_str = recordatorio.get('time', '')
                if fecha_str:
                    if isinstance(fecha_str, str):
                        fecha = datetime.fromisoformat(fecha_str.replace('Z', '+00:00'))
                    else:
                        fecha = fecha_str
                    
                    # Próximos 7 días
                    if fecha.date() <= (ahora + timedelta(days=7)).date():
                        proximos += 1
                    
                    # Vencidos
                    if fecha < ahora:
                        vencidos += 1
            except:
                pass  # Ignorar errores de fecha
        
        return {
            'total': len(recordatorios),
            'por_categoria': categorias,
            'proximos_7_dias': proximos,
            'vencidos': vencidos
        }
        
    except Exception as e:
        print(f"{Fore.RED}❌ Error obteniendo estadísticas: {str(e)}{Style.RESET_ALL}")
        return {'total': 0, 'por_categoria': {}, 'proximos_7_dias': 0, 'vencidos': 0}

# =======================================================================
# 3. COMANDOS DEL CLI - OPERACIONES DE CONSULTA
# =======================================================================

def comando_list(args):
    """Lista todos los recordatorios con numeración para eliminación fácil"""
    print(f"{Fore.BLUE}⏳ Obteniendo tus recordatorios desde el motor de TARS...{Style.RESET_ALL}")
    
    # =======================================================================
    # 3.1 INICIALIZACIÓN Y OBTENCIÓN DE DATOS
    # =======================================================================
    
    parser, scheduler = inicializar_sistema_recordatorios()
    if not parser:
        print(f"{Fore.RED}❌ No se pudo inicializar el sistema de recordatorios{Style.RESET_ALL}")
        return
    
    recordatorios = parser.list_reminders()
    
    if not recordatorios:
        print(f"{Fore.YELLOW}⚠️ No tienes recordatorios programados{Style.RESET_ALL}")
        return
    
    # =======================================================================
    # 3.2 CLASIFICACIÓN Y PRESENTACIÓN CON NUMERACIÓN
    # =======================================================================
    
    # Separar por categorías
    categorias = {}
    for recordatorio in recordatorios:
        cat = recordatorio.get('category', 'Sin categoría')
        if cat not in categorias:
            categorias[cat] = []
        categorias[cat].append(recordatorio)
    
    print(f"\n{Fore.GREEN}📋 TODOS TUS RECORDATORIOS ({len(recordatorios)} total):{Style.RESET_ALL}")
    
    numero_global = 1
    
    for categoria, items in categorias.items():
        print(f"\n{Fore.CYAN}🏷️ {categoria.upper()} ({len(items)}):{Style.RESET_ALL}")
        
        for recordatorio in items:
            descripcion = recordatorio.get('msg', 'Sin descripción')
            job_id = recordatorio.get('id', 'sin_id')
            tiempo = formatear_tiempo_natural(recordatorio)
            
            print(f"  {Fore.WHITE}{numero_global}.{Style.RESET_ALL} {descripcion}")
            print(f"     ⏰ {tiempo}")
            print(f"     🔑 ID: {job_id}")
            
            numero_global += 1
    
    # CHEATSHEET COMPLETO
    print(f"\n{Fore.BLUE}💡 COMANDOS DISPONIBLES:{Style.RESET_ALL}")
    print(f"  {Fore.GREEN}📋 Gestión básica:{Style.RESET_ALL}")
    print(f"    python3 scripts/cli_reminder_engine.py list")
    print(f"    python3 scripts/cli_reminder_engine.py add \"Comprar café mañana 8am\"")
    print(f"    python3 scripts/cli_reminder_engine.py delete 2")
    print(f"    python3 scripts/cli_reminder_engine.py delete job_0005")
    print(f"  {Fore.CYAN}🔍 Búsqueda y análisis:{Style.RESET_ALL}")
    print(f"    python3 scripts/cli_reminder_engine.py search \"médico\"")
    print(f"    python3 scripts/cli_reminder_engine.py stats")
    print(f"  {Fore.YELLOW}🧪 Testing y debug:{Style.RESET_ALL}")
    print(f"    python3 scripts/cli_reminder_engine.py test \"elimina recordatorio número 3\"")

def comando_search(args):
    """Busca recordatorios por palabra clave"""
    if not args.texto:
        print(f"{Fore.RED}❌ Debes especificar un texto para buscar{Style.RESET_ALL}")
        return
    
    # =======================================================================
    # 3.3 BÚSQUEDA EN RECORDATORIOS
    # =======================================================================
    
    parser, scheduler = inicializar_sistema_recordatorios()
    if not parser:
        print(f"{Fore.RED}❌ No se pudo inicializar el sistema de recordatorios{Style.RESET_ALL}")
        return
    
    recordatorios = parser.list_reminders(filter_text=args.texto)
    
    if not recordatorios:
        print(f"{Fore.YELLOW}⚠️ No se encontraron recordatorios que contengan '{args.texto}'{Style.RESET_ALL}")
        return
    
    print(f"{Fore.GREEN}✅ Resultados de búsqueda para '{args.texto}' ({len(recordatorios)} encontrados):{Style.RESET_ALL}")
    
    for i, recordatorio in enumerate(recordatorios, 1):
        descripcion = recordatorio.get('msg', 'Sin descripción')
        categoria = recordatorio.get('category', 'Sin categoría')
        tiempo = formatear_tiempo_natural(recordatorio)
        job_id = recordatorio.get('id', 'sin_id')
        
        print(f"  {i}. 📅 {descripcion}")
        print(f"     🏷️ [{categoria}] ⏰ {tiempo}")
        print(f"     🔑 {job_id}")

def comando_stats(args):
    """Muestra estadísticas completas de los recordatorios"""
    print(f"{Fore.BLUE}⏳ Calculando estadísticas de recordatorios...{Style.RESET_ALL}")
    
    # =======================================================================
    # 3.4 RECOPILACIÓN DE ESTADÍSTICAS GENERALES
    # =======================================================================
    
    parser, scheduler = inicializar_sistema_recordatorios()
    if not parser:
        print(f"{Fore.RED}❌ No se pudo inicializar el sistema de recordatorios{Style.RESET_ALL}")
        return
    
    stats = obtener_estadisticas_recordatorios(parser)
    
    print(f"\n{Fore.BLUE}📊 ESTADÍSTICAS DE RECORDATORIOS{Style.RESET_ALL}")
    print(f"  Total de recordatorios: {stats['total']}")
    print(f"  Próximos 7 días: {stats['proximos_7_dias']}")
    print(f"  Vencidos: {stats['vencidos']}")
    
    # =======================================================================
    # 3.5 ESTADÍSTICAS POR CATEGORÍA
    # =======================================================================
    
    if stats['por_categoria']:
        print(f"\n{Fore.BLUE}📊 RECORDATORIOS POR CATEGORÍA{Style.RESET_ALL}")
        for categoria, count in sorted(stats['por_categoria'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {categoria}: {count}")
    
    # =======================================================================
    # 3.6 PRÓXIMOS RECORDATORIOS
    # =======================================================================
    
    recordatorios = parser.list_reminders()
    if recordatorios:
        # Ordenar por fecha
        try:
            recordatorios_ordenados = sorted(recordatorios, key=lambda x: x.get('time', ''))
            proximos = recordatorios_ordenados[:3]  # Top 3
            
            print(f"\n{Fore.BLUE}⏰ PRÓXIMOS 3 RECORDATORIOS{Style.RESET_ALL}")
            for i, recordatorio in enumerate(proximos, 1):
                descripcion = recordatorio.get('msg', 'Sin descripción')
                tiempo = formatear_tiempo_natural(recordatorio)
                print(f"  {i}. {descripcion} - {tiempo}")
        except:
            pass  # Ignorar errores de ordenación
    
    # Mostrar comandos disponibles
    print(f"\n{Fore.BLUE}💡 GESTIÓN RÁPIDA:{Style.RESET_ALL}")
    print(f"    python3 scripts/cli_reminder_engine.py add \"nuevo recordatorio\"")
    print(f"    python3 scripts/cli_reminder_engine.py delete <número>")
    print(f"    python3 scripts/cli_reminder_engine.py search <texto>")

# =======================================================================
# 4. COMANDOS DEL CLI - OPERACIONES DE MODIFICACIÓN
# =======================================================================

def comando_add(args):
    """Añade un nuevo recordatorio al sistema"""
    if not args.texto:
        print(f"{Fore.RED}❌ Debes especificar un texto para el recordatorio{Style.RESET_ALL}")
        return
    
    # =======================================================================
    # 4.1 INICIALIZACIÓN Y PREPARACIÓN
    # =======================================================================
    
    parser, scheduler = inicializar_sistema_recordatorios()
    if not parser:
        print(f"{Fore.RED}❌ No se pudo inicializar el sistema de recordatorios{Style.RESET_ALL}")
        return
    
    # Preparar texto del recordatorio
    texto_recordatorio = args.texto.strip()
    categoria = args.categoria if args.categoria else "CLI"
    
    try:
        # =======================================================================
        # 4.2 CREACIÓN DEL RECORDATORIO
        # =======================================================================
        
        # Usar el parser para crear el recordatorio
        # 1. Parsear texto
        resultado = parser.parse(texto_recordatorio)

        # 2. Verificar si hay feedback del parser (intención pero sin fecha)
        if resultado:
            if "feedback" in resultado:
                print(f"{Fore.YELLOW}❓ {resultado['feedback']}{Style.RESET_ALL}")
                return
            if not resultado.get("fecha") or not resultado.get("hora"):
                print(f"{Fore.RED}❌ No pude detectar una fecha válida. ¿Puedes ser más específico?{Style.RESET_ALL}")
                return
        else:
            print(f"{Fore.RED}❌ No pude entender el recordatorio. ¿Puedes reformularlo?{Style.RESET_ALL}")
            return

        # 3. Crear recordatorio usando el plugin real y su método process_command
        plugin = ReminderPlugin(scheduler)
        
        # Construir un comando que el plugin pueda entender
        comando = f"recuérdame {texto_recordatorio}"
        
        # Llamar a process_command en lugar de create
        creado = plugin.process_command(comando)

        # 4. Confirmación
        if creado and ("creado" in creado.lower() or "programado" in creado.lower()):
            print(f"{Fore.GREEN}✅ {creado}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}⚠️ No se pudo crear el recordatorio. Respuesta: {creado}{Style.RESET_ALL}")

            
    except Exception as e:
        print(f"{Fore.RED}❌ Error al crear recordatorio: {str(e)}{Style.RESET_ALL}")
        # Imprimir la traza completa para ayudar en depuración
        import traceback
        traceback.print_exc()

def comando_delete(args):
    """Elimina un recordatorio por número o ID"""
    if not args.identificador:
        print(f"{Fore.RED}❌ Debes especificar un número o ID para eliminar{Style.RESET_ALL}")
        return
    
    # =======================================================================
    # 4.3 ELIMINACIÓN POR NÚMERO O ID
    # =======================================================================
    
    parser, scheduler = inicializar_sistema_recordatorios()
    if not parser:
        print(f"{Fore.RED}❌ No se pudo inicializar el sistema de recordatorios{Style.RESET_ALL}")
        return
    
    try:
        identificador = args.identificador.strip()
        
        # Si es un número, eliminar por posición
        if identificador.isdigit():
            numero = int(identificador)
            recordatorios = parser.list_reminders()
            
            if not recordatorios:
                print(f"{Fore.YELLOW}⚠️ No tienes recordatorios para eliminar{Style.RESET_ALL}")
                return
            
            if numero < 1 or numero > len(recordatorios):
                print(f"{Fore.RED}❌ Número inválido. Tienes {len(recordatorios)} recordatorios (del 1 al {len(recordatorios)}){Style.RESET_ALL}")
                return
            
            # Obtener recordatorio por posición (convertir a 0-based)
            recordatorio_target = recordatorios[numero - 1]
            job_id = recordatorio_target['id']
            descripcion = recordatorio_target['msg']
            
            # Eliminar
            resultado = parser.remove_reminder(job_id)
            
            if "eliminado" in resultado.lower():
                print(f"{Fore.GREEN}✅ Eliminado recordatorio número {numero}: {descripcion}{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}⚠️ {resultado}{Style.RESET_ALL}")
        
        else:
            # Eliminar por ID directamente
            resultado = parser.remove_reminder(identificador)
            
            if "eliminado" in resultado.lower():
                print(f"{Fore.GREEN}✅ {resultado}{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}⚠️ {resultado}{Style.RESET_ALL}")
            
    except Exception as e:
        print(f"{Fore.RED}❌ Error al eliminar recordatorio: {str(e)}{Style.RESET_ALL}")

def comando_test(args):
    """Prueba patrones de regex para comandos de recordatorios"""
    if not args.texto:
        print(f"{Fore.RED}❌ Debes especificar un texto para probar{Style.RESET_ALL}")
        return
    
    # =======================================================================
    # 4.4 TESTING DE PATRONES REGEX
    # =======================================================================
    
    parser, scheduler = inicializar_sistema_recordatorios()
    if not parser:
        print(f"{Fore.RED}❌ No se pudo inicializar el sistema de recordatorios{Style.RESET_ALL}")
        return
    
    texto = args.texto.strip()
    
    print(f"{Fore.BLUE}🧪 TESTING DE PATRONES PARA: '{texto}'{Style.RESET_ALL}")
    
    # Obtener patrones del ReminderPlugin
    try:
        # Simular la detección de comando
        from services.plugins.reminder_plugin import ReminderPlugin
        plugin = ReminderPlugin()
        
        # Acceder a los patrones (si están disponibles)
        if hasattr(plugin, 'COMMAND_PATTERNS'):
            patrones = plugin.COMMAND_PATTERNS
            
            print(f"\n{Fore.CYAN}🔍 PROBANDO PATRONES:{Style.RESET_ALL}")
            
            encontrado = False
            for tipo_comando, lista_patrones in patrones.items():
                for patron in lista_patrones:
                    match = re.search(patron, texto, re.IGNORECASE)
                    if match:
                        encontrado = True
                        captura = match.group(1) if match.groups() else ""
                        print(f"  ✅ {Fore.GREEN}{tipo_comando}{Style.RESET_ALL}: '{patron}'")
                        print(f"     Captura: '{captura}'")
                        print()
            
            if not encontrado:
                print(f"  ❌ {Fore.YELLOW}No se encontró ningún patrón que coincida{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}⚠️ No se pudieron acceder a los patrones del plugin{Style.RESET_ALL}")
            
    except Exception as e:
        print(f"{Fore.RED}❌ Error en testing: {str(e)}{Style.RESET_ALL}")

# =======================================================================
# 5. CONFIGURACIÓN DE ARGUMENTOS Y PARSER PRINCIPAL
# =======================================================================

def main():
    """Función principal del CLI"""
    parser = argparse.ArgumentParser(
        description='TARS CLI REMINDER ENGINE - Gestión de recordatorios sin despertar al vecindario',
        epilog='Porque a veces es mejor escribir que hablar. Especialmente a las 3 AM.'
    )
    subparsers = parser.add_subparsers(dest='comando', help='Comandos disponibles')
    
    # =======================================================================
    # 5.1 DEFINICIÓN DE SUBCOMANDOS
    # =======================================================================
    
    # Comando list
    list_parser = subparsers.add_parser('list', help='Listar todos los recordatorios con numeración')
    
    # Comando add
    add_parser = subparsers.add_parser('add', help='Añadir un nuevo recordatorio')
    add_parser.add_argument('texto', help='Texto del recordatorio (incluye fecha/hora)')
    add_parser.add_argument('-c', '--categoria', help='Categoría del recordatorio', default='CLI')
    
    # Comando search
    search_parser = subparsers.add_parser('search', help='Buscar recordatorios por palabra clave')
    search_parser.add_argument('texto', help='Texto a buscar')
    
    # Comando delete
    delete_parser = subparsers.add_parser('delete', help='Eliminar un recordatorio por número o ID')
    delete_parser.add_argument('identificador', help='Número del recordatorio (del comando list) o ID del job')
    
    # Comando stats
    stats_parser = subparsers.add_parser('stats', help='Mostrar estadísticas de recordatorios')
    
    # Comando test
    test_parser = subparsers.add_parser('test', help='Probar patrones de regex para comandos')
    test_parser.add_argument('texto', help='Texto de comando a probar')
    
    args = parser.parse_args()
    
    # =======================================================================
    # 5.2 DISTRIBUCIÓN DE COMANDOS
    # =======================================================================
    
    # Si no se especifica comando, mostrar ayuda ÉPICA
    if not args.comando:
        print(f"\n{Fore.BLUE}🤖 TARS CLI REMINDER ENGINE{Style.RESET_ALL}")
        print(f"{Fore.CYAN}═══════════════════════════════════════════════════════════════{Style.RESET_ALL}")
        print(f"\n{Fore.GREEN}📋 COMANDOS DE GESTIÓN:{Style.RESET_ALL}")
        print(f"  list                    # Lista todos los recordatorios")
        print(f"  add \"texto\"              # Crea nuevo recordatorio")
        print(f"  delete <número>         # Elimina por número de lista")
        print(f"  delete <job_id>         # Elimina por ID directo")
        print(f"\n{Fore.CYAN}🔍 COMANDOS DE BÚSQUEDA:{Style.RESET_ALL}")
        print(f"  search \"palabra\"         # Busca recordatorios")
        print(f"  stats                   # Estadísticas completas")
        print(f"\n{Fore.YELLOW}🧪 COMANDOS DE DEBUG:{Style.RESET_ALL}")
        print(f"  test \"comando\"           # Prueba patrones de regex")
        print(f"\n{Fore.GREEN}📝 EJEMPLOS PRÁCTICOS:{Style.RESET_ALL}")
        print(f"  python3 scripts/cli_reminder_engine.py list")
        print(f"  python3 scripts/cli_reminder_engine.py add \"Llamar dentista mañana 10am\"")
        print(f"  python3 scripts/cli_reminder_engine.py delete 2")
        print(f"  python3 scripts/cli_reminder_engine.py search \"médico\"")
        print(f"  python3 scripts/cli_reminder_engine.py test \"elimina recordatorio 3\"")
        print(f"\n{Fore.BLUE}💡 Tip: Usa números para eliminar fácilmente (del comando list){Style.RESET_ALL}")
        return
    
    # Ejecutar el comando correspondiente
    if args.comando == 'list':
        comando_list(args)
    elif args.comando == 'add':
        comando_add(args)
    elif args.comando == 'search':
        comando_search(args)
    elif args.comando == 'delete':
        comando_delete(args)
    elif args.comando == 'stats':
        comando_stats(args)
    elif args.comando == 'test':
        comando_test(args)

# =======================================================================
# 6. EJECUCIÓN PRINCIPAL Y MANEJO DE EXCEPCIONES
# =======================================================================

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⚠️ Operación cancelada por el usuario. Los recordatorios siguen ahí, tranquilo.{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}❌ Error inesperado: {str(e)}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}💡 Tip: Asegúrate de estar ejecutando desde el directorio correcto de TARS{Style.RESET_ALL}")

# ===============================================
# ESTADO: OPERATIVO Y SOSPECHOSAMENTE SILENCIOSO
# ÚLTIMA ACTUALIZACIÓN: Justo después de ejecutar 6 eliminaciones sin pedir confirmación
# FILOSOFÍA: “Los comandos no se discuten. Se ejecutan.”
# VALIDADO EN: Consolas remotas, crontabs, y momentos en los que la voz no tiene cabida
# ===============================================
#
#     THIS IS THE SILENT WAY
#     (porque algunos recordatorios es mejor crearlos en secreto)
#
# ===============================================
