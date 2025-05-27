#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ===============================================  
# TARS CLI - Interfaz de línea de comandos para TARS-BSK  
# Objetivo: Modificar preferencias sin activar todo el circo neuronal
# Dependencias: SQLite3, colorama, argparse, y suficiente oscuridad en el alma como para preferir una CLI
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

# Configurar colorama para que funcione en Windows
colorama.init()

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Rutas principales - Ajustadas para acceder a la base de datos SQLite
DB_PATH = os.path.expanduser("~/tars_files/memory/memory_db/tars_memory.db")
TAXONOMY_PATH = os.path.expanduser("~/tars_files/data/taxonomy/categories.json")

# =======================================================================
# 2. FUNCIONES DE UTILIDAD Y CARGA DE DATOS
# =======================================================================

def cargar_taxonomia():
    """Carga la taxonomía desde el archivo JSON"""
    try:
        if os.path.exists(TAXONOMY_PATH):
            with open(TAXONOMY_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("taxonomy", {})
        else:
            print(f"{Fore.YELLOW}⚠️ Archivo de taxonomía no encontrado: {TAXONOMY_PATH}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}❌ Error cargando taxonomía: {str(e)}{Style.RESET_ALL}")
    
    return {}

def obtener_preferencias_desde_db(usuario="usuario", categoria=None, limite=50):
    """
    Obtiene preferencias directamente desde la base de datos SQLite
    
    Args:
        usuario: Nombre del usuario (por defecto "usuario")
        categoria: Categoría específica para filtrar (opcional)
        limite: Número máximo de resultados
    
    Returns:
        Lista de preferencias como diccionarios
    """
    if not os.path.exists(DB_PATH):
        print(f"{Fore.RED}❌ Base de datos no encontrada: {DB_PATH}{Style.RESET_ALL}")
        return []
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Para obtener resultados como diccionarios
        cursor = conn.cursor()
        
        # Construir consulta SQL
        query = "SELECT * FROM preferences"
        params = []
        
        if categoria:
            query += " WHERE category = ?"
            params.append(categoria)
        
        query += " ORDER BY importance DESC, timestamp DESC LIMIT ?"
        params.append(limite)
        
        cursor.execute(query, params)
        results = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return results
    except Exception as e:
        print(f"{Fore.RED}❌ Error al leer desde la base de datos: {str(e)}{Style.RESET_ALL}")
        return []

# =======================================================================
# 3. COMANDOS DEL CLI - OPERACIONES DE CONSULTA
# =======================================================================

def comando_list(args):
    """Lista todas las preferencias guardadas en la base de datos SQLite"""
    print(f"{Fore.BLUE}⏳ Obteniendo tus preferencias desde la base de datos...{Style.RESET_ALL}")
    
    # =======================================================================
    # 3.1 OBTENCIÓN Y VALIDACIÓN DE DATOS
    # =======================================================================
    
    # Obtener datos de la base de datos
    preferencias = obtener_preferencias_desde_db()
    
    if not preferencias:
        print(f"{Fore.YELLOW}⚠️ No se encontraron preferencias en la base de datos{Style.RESET_ALL}")
        return
    
    # Cargar taxonomía para mostrar categorías completas
    taxonomia = cargar_taxonomia()
    
    # =======================================================================
    # 3.2 CLASIFICACIÓN Y PRESENTACIÓN DE DATOS
    # =======================================================================
    
    # Separar por sentimiento positivo/negativo
    gustos = [p for p in preferencias if p.get("sentiment", 0) > 0]
    disgustos = [p for p in preferencias if p.get("sentiment", 0) < 0]
    
    print(f"\n{Fore.GREEN}👍 GUSTOS ({len(gustos)}){Style.RESET_ALL}")
    if gustos:
        for i, gusto in enumerate(gustos, 1):
            tema = gusto.get("topic", "desconocido")
            categoria = gusto.get("category", "desconocida")
            sentimiento = gusto.get("sentiment", 0)
            importancia = gusto.get("importance", 0)
            
            # Si la categoría está en la taxonomía, mostrar información adicional
            cat_info = f" [{categoria}]"
                
            print(f"  {i}. {tema}{cat_info} (sent: {sentimiento:.2f}, imp: {importancia:.2f})")
    else:
        print("  No hay gustos registrados")
    
    print(f"\n{Fore.RED}👎 DISGUSTOS ({len(disgustos)}){Style.RESET_ALL}")
    if disgustos:
        for i, disgusto in enumerate(disgustos, 1):
            tema = disgusto.get("topic", "desconocido")
            categoria = disgusto.get("category", "desconocida")
            sentimiento = disgusto.get("sentiment", 0)
            importancia = disgusto.get("importance", 0)
            
            # Si la categoría está en la taxonomía, mostrar información adicional
            cat_info = f" [{categoria}]"
                
            print(f"  {i}. {tema}{cat_info} (sent: {sentimiento:.2f}, imp: {importancia:.2f})")
    else:
        print("  No hay disgustos registrados")

def comando_search(args):
    """Busca preferencias por palabra clave"""
    if not args.texto:
        print(f"{Fore.RED}❌ Debes especificar un texto para buscar{Style.RESET_ALL}")
        return
    
    if not os.path.exists(DB_PATH):
        print(f"{Fore.RED}❌ Base de datos no encontrada: {DB_PATH}{Style.RESET_ALL}")
        return
    
    try:
        # =======================================================================
        # 3.3 BÚSQUEDA CON LIKE EN SQLITE
        # =======================================================================
        
        # Conectar a la base de datos
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Realizar búsqueda con LIKE
        cursor.execute(
            "SELECT * FROM preferences WHERE topic LIKE ? ORDER BY importance DESC", 
            (f"%{args.texto}%",)
        )
        
        resultados = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        if not resultados:
            print(f"{Fore.YELLOW}⚠️ No se encontraron preferencias que contengan '{args.texto}'{Style.RESET_ALL}")
            return
        
        print(f"{Fore.GREEN}✅ Resultados de búsqueda para '{args.texto}' ({len(resultados)} encontrados):{Style.RESET_ALL}")
        
        for i, pref in enumerate(resultados, 1):
            tema = pref.get("topic", "desconocido")
            categoria = pref.get("category", "desconocida")
            sentimiento = pref.get("sentiment", 0)
            
            emoji = "👍" if sentimiento > 0 else "👎"
            print(f"  {i}. {emoji} {tema} [{categoria}] (sentimiento: {sentimiento:.2f})")
        
    except Exception as e:
        print(f"{Fore.RED}❌ Error al buscar preferencias: {str(e)}{Style.RESET_ALL}")

def comando_categorias(args):
    """Muestra las categorías disponibles en la taxonomía"""
    taxonomia = cargar_taxonomia()
    
    if not taxonomia:
        print(f"{Fore.YELLOW}⚠️ No se pudo cargar la taxonomía.{Style.RESET_ALL}")
        return
    
    print(f"{Fore.BLUE}📋 Categorías disponibles en la taxonomía:{Style.RESET_ALL}")
    
    # =======================================================================
    # 3.4 PRESENTACIÓN DE TAXONOMÍA COMPLETA
    # =======================================================================
    
    for categoria, datos in taxonomia.items():
        # Obtener número de palabras clave principales
        n_keywords = len(datos.get("keywords", []))
        
        # Obtener subcategorías
        subcategorias = datos.get("subcategories", {})
        n_subcats = len(subcategorias)
        
        print(f"\n{Fore.GREEN}▶ {categoria.upper()} ({n_keywords} keywords, {n_subcats} subcategorías){Style.RESET_ALL}")
        
        # Mostrar algunas keywords de ejemplo (máximo 5)
        if n_keywords > 0:
            keywords = datos.get("keywords", [])[:5]
            print(f"  Keywords: {', '.join(keywords)}" + (f" (y {n_keywords-5} más...)" if n_keywords > 5 else ""))
        
        # Mostrar subcategorías
        if subcategorias:
            print("  Subcategorías:")
            for subcat, subkeywords in subcategorias.items():
                n_subkw = len(subkeywords)
                print(f"   - {subcat} ({n_subkw} keywords)")

def comando_stats(args):
    """Muestra estadísticas de las preferencias almacenadas"""
    if not os.path.exists(DB_PATH):
        print(f"{Fore.RED}❌ Base de datos no encontrada: {DB_PATH}{Style.RESET_ALL}")
        return
    
    try:
        # =======================================================================
        # 3.5 RECOPILACIÓN DE ESTADÍSTICAS GENERALES
        # =======================================================================
        
        # Conectar a la base de datos
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Estadísticas generales
        cursor.execute("SELECT COUNT(*) FROM preferences")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM preferences WHERE sentiment > 0")
        total_gustos = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM preferences WHERE sentiment < 0")
        total_disgustos = cursor.fetchone()[0]
        
        print(f"\n{Fore.BLUE}📊 ESTADÍSTICAS DE PREFERENCIAS{Style.RESET_ALL}")
        print(f"  Total de preferencias: {total}")
        print(f"  Gustos: {total_gustos}")
        print(f"  Disgustos: {total_disgustos}")
        
        # =======================================================================
        # 3.6 ESTADÍSTICAS POR CATEGORÍA
        # =======================================================================
        
        # Estadísticas por categoría
        cursor.execute(
            "SELECT category, COUNT(*) as count FROM preferences GROUP BY category ORDER BY count DESC"
        )
        cats = cursor.fetchall()
        
        if cats:
            print(f"\n{Fore.BLUE}📊 PREFERENCIAS POR CATEGORÍA{Style.RESET_ALL}")
            for cat, count in cats:
                print(f"  {cat}: {count}")
        
        # =======================================================================
        # 3.7 TOP PREFERENCIAS MÁS IMPORTANTES
        # =======================================================================
        
        # Preferencias con mayor importancia
        cursor.execute(
            "SELECT topic, category, sentiment, importance FROM preferences ORDER BY importance DESC LIMIT 5"
        )
        top_prefs = cursor.fetchall()
        
        if top_prefs:
            print(f"\n{Fore.BLUE}🌟 TOP 5 PREFERENCIAS MÁS IMPORTANTES{Style.RESET_ALL}")
            for tema, cat, sent, imp in top_prefs:
                emoji = "👍" if sent > 0 else "👎"
                print(f"  {emoji} {tema} [{cat}] (importancia: {imp:.2f})")
        
        conn.close()
        
    except Exception as e:
        print(f"{Fore.RED}❌ Error al obtener estadísticas: {str(e)}{Style.RESET_ALL}")

# =======================================================================
# 4. COMANDOS DEL CLI - OPERACIONES DE MODIFICACIÓN
# =======================================================================

def comando_add(args):
    """Añade una nueva preferencia a la base de datos"""
    if not args.texto:
        print(f"{Fore.RED}❌ Debes especificar un texto para añadir como preferencia{Style.RESET_ALL}")
        return
    
    if not os.path.exists(DB_PATH):
        print(f"{Fore.RED}❌ Base de datos no encontrada: {DB_PATH}{Style.RESET_ALL}")
        return
    
    # =======================================================================
    # 4.1 PREPARACIÓN DE PARÁMETROS
    # =======================================================================
    
    # Determinar tipo, categoría y valores
    tipo = "gusto" if not args.disgusto else "disgusto"
    sentimiento = 0.9 if tipo == "gusto" else -0.9
    importancia = args.importancia if args.importancia is not None else 0.8
    tema = args.texto.lower().strip()
    categoria = args.categoria if args.categoria else "general"
    
    try:
        # =======================================================================
        # 4.2 VERIFICACIÓN DE PREFERENCIA EXISTENTE
        # =======================================================================
        
        # Conectar a la base de datos
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar si ya existe
        cursor.execute(
            "SELECT id, sentiment, importance FROM preferences WHERE LOWER(topic) = ?", 
            (tema,)
        )
        existente = cursor.fetchone()
        
        if existente:
            # =======================================================================
            # 4.3 ACTUALIZACIÓN CON PROMEDIO PONDERADO
            # =======================================================================
            
            # Actualizar preferencia existente
            id_pref, sent_ant, imp_ant = existente
            nuevo_sent = (sentimiento * 0.7) + (sent_ant * 0.3)  # Promedio ponderado
            nueva_imp = max(imp_ant, importancia)
            
            cursor.execute(
                "UPDATE preferences SET sentiment = ?, importance = ?, category = ?, timestamp = CURRENT_TIMESTAMP WHERE id = ?",
                (nuevo_sent, nueva_imp, categoria, id_pref)
            )
            
            print(f"{Fore.GREEN}✅ Preferencia actualizada: '{tema}' (sentimiento: {nuevo_sent:.2f}, importancia: {nueva_imp:.2f}){Style.RESET_ALL}")
        else:
            # =======================================================================
            # 4.4 INSERCIÓN DE NUEVA PREFERENCIA
            # =======================================================================
            
            # Insertar nueva preferencia
            cursor.execute(
                "INSERT INTO preferences (category, topic, sentiment, importance, source) VALUES (?, ?, ?, ?, ?)",
                (categoria, tema, sentimiento, importancia, "CLI")
            )
            
            print(f"{Fore.GREEN}✅ Nueva preferencia añadida: '{tema}' (sentimiento: {sentimiento:.2f}, importancia: {importancia:.2f}){Style.RESET_ALL}")
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        print(f"{Fore.RED}❌ Error al añadir preferencia: {str(e)}{Style.RESET_ALL}")

def comando_delete(args):
    """Elimina una preferencia de la base de datos"""
    if not args.texto:
        print(f"{Fore.RED}❌ Debes especificar un texto para eliminar{Style.RESET_ALL}")
        return
    
    if not os.path.exists(DB_PATH):
        print(f"{Fore.RED}❌ Base de datos no encontrada: {DB_PATH}{Style.RESET_ALL}")
        return
    
    try:
        # =======================================================================
        # 4.5 VERIFICACIÓN Y ELIMINACIÓN SEGURA
        # =======================================================================
        
        # Conectar a la base de datos
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar si existe
        cursor.execute(
            "SELECT id, topic FROM preferences WHERE LOWER(topic) = ?", 
            (args.texto.lower(),)
        )
        existente = cursor.fetchone()
        
        if not existente:
            print(f"{Fore.YELLOW}⚠️ No se encontró ninguna preferencia con el tema '{args.texto}'{Style.RESET_ALL}")
            conn.close()
            return
        
        id_pref, tema = existente
        
        # Eliminar preferencia
        cursor.execute("DELETE FROM preferences WHERE id = ?", (id_pref,))
        conn.commit()
        
        print(f"{Fore.GREEN}✅ Preferencia eliminada: '{tema}'{Style.RESET_ALL}")
        conn.close()
        
    except Exception as e:
        print(f"{Fore.RED}❌ Error al eliminar preferencia: {str(e)}{Style.RESET_ALL}")

# =======================================================================
# 5. CONFIGURACIÓN DE ARGUMENTOS Y PARSER PRINCIPAL
# =======================================================================

def main():
    """Función principal del CLI"""
    parser = argparse.ArgumentParser(description='TARS CLI - Interfaz de línea de comandos para TARS')
    subparsers = parser.add_subparsers(dest='comando', help='Comandos disponibles')
    
    # =======================================================================
    # 5.1 DEFINICIÓN DE SUBCOMANDOS
    # =======================================================================
    
    # Comando list
    list_parser = subparsers.add_parser('list', help='Listar todas las preferencias de la base de datos')
    
    # Comando add
    add_parser = subparsers.add_parser('add', help='Añadir una nueva preferencia a la base de datos')
    add_parser.add_argument('texto', help='Texto de la preferencia a añadir')
    add_parser.add_argument('-d', '--disgusto', action='store_true', help='Añadir como disgusto en lugar de gusto')
    add_parser.add_argument('-c', '--categoria', help='Categoría a asignar')
    add_parser.add_argument('-i', '--importancia', type=float, help='Importancia (0.0 a 1.0)')
    
    # Comando search
    search_parser = subparsers.add_parser('search', help='Buscar preferencias por palabra clave')
    search_parser.add_argument('texto', help='Texto a buscar')
    
    # Comando delete
    delete_parser = subparsers.add_parser('delete', help='Eliminar una preferencia')
    delete_parser.add_argument('texto', help='Tema de la preferencia a eliminar')
    
    # Comando categorias
    cat_parser = subparsers.add_parser('categorias', help='Mostrar las categorías disponibles en la taxonomía')
    
    # Comando stats
    stats_parser = subparsers.add_parser('stats', help='Mostrar estadísticas de las preferencias')
    
    args = parser.parse_args()
    
    # =======================================================================
    # 5.2 DISTRIBUCIÓN DE COMANDOS
    # =======================================================================
    
    # Si no se especifica comando, mostrar ayuda
    if not args.comando:
        parser.print_help()
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
    elif args.comando == 'categorias':
        comando_categorias(args)
    elif args.comando == 'stats':
        comando_stats(args)

# =======================================================================
# 6. EJECUCIÓN PRINCIPAL Y MANEJO DE EXCEPCIONES
# =======================================================================

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⚠️ Operación cancelada por el usuario{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}")

# ===============================================
# ESTADO: FUNCIONALMENTE SARCÁSTICO (pero útil)
# ÚLTIMA ACTUALIZACIÓN: Después de una conversación incómoda con el parser
# FILOSOFÍA: "Algunas cosas es mejor escribirlas que decirlas. Esto es una de ellas."
# ===============================================
#
#           THIS IS THE CLI WAY... 
#           (porque hay cosas que ni yo quiero recordar en voz alta)
#
# ===============================================