#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ===============================================  
# TARS CLI MULTIUSUARIO - Versión NOCTUA corregida  
# Objetivo: Modificar preferencias por usuario sin activar todo el circo neuronal
# Dependencias: SQLite3, colorama, argparse, y suficiente oscuridad en el alma como para preferir una CLI
# CORRECCIÓN: argparse funcional + preservar datos existentes
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

def obtener_preferencias_desde_db(usuario="global", categoria=None, limite=50):
    """
    Obtiene preferencias filtradas por usuario específico desde la base de datos SQLite
    
    Args:
        usuario: Nombre del usuario (default "global" para compatibilidad)
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
        
        # FILTRAR POR USUARIO ESPECÍFICO
        query = "SELECT * FROM preferences WHERE user = ?"
        params = [usuario]
        
        if categoria:
            query += " AND category = ?"
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

def obtener_usuarios_disponibles():
    """
    Obtiene lista de usuarios que tienen preferencias almacenadas
    
    Returns:
        Lista de tuplas (usuario, count) ordenadas por número de preferencias
    """
    if not os.path.exists(DB_PATH):
        print(f"{Fore.RED}❌ Base de datos no encontrada: {DB_PATH}{Style.RESET_ALL}")
        return []
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT user, COUNT(*) as count FROM preferences GROUP BY user ORDER BY count DESC")
        usuarios = cursor.fetchall()
        conn.close()
        
        return usuarios
    except Exception as e:
        print(f"{Fore.RED}❌ Error al obtener usuarios: {str(e)}{Style.RESET_ALL}")
        return []

# =======================================================================
# 3. COMANDOS DEL CLI - OPERACIONES DE CONSULTA
# =======================================================================

def comando_list(args):
    """Lista preferencias: usuario específico o todos los usuarios con --all"""
    # 🆕 DETECTAR SI ES --all O USUARIO ESPECÍFICO
    if getattr(args, 'all', False):
        # MODO --all: MOSTRAR TODOS LOS USUARIOS
        print(f"{Fore.BLUE}⏳ Obteniendo preferencias de TODOS los usuarios...{Style.RESET_ALL}")
        
        usuarios = obtener_usuarios_disponibles()
        if not usuarios:
            print(f"{Fore.YELLOW}⚠️ No hay usuarios con preferencias registradas{Style.RESET_ALL}")
            return
        
        total_gustos = 0
        total_disgustos = 0
        
        for usuario, count in usuarios:
            print(f"\n{'='*60}")
            print(f"{Fore.CYAN}👤 USUARIO: {usuario.upper()} ({count} preferencias){Style.RESET_ALL}")
            print('='*60)
            
            # Obtener preferencias de este usuario
            preferencias = obtener_preferencias_desde_db(usuario=usuario)
            gustos = [p for p in preferencias if p.get("sentiment", 0) > 0]
            disgustos = [p for p in preferencias if p.get("sentiment", 0) < 0]
            
            total_gustos += len(gustos)
            total_disgustos += len(disgustos)
            
            # Mostrar gustos
            print(f"\n{Fore.GREEN}👍 GUSTOS ({len(gustos)}){Style.RESET_ALL}")
            if gustos:
                for i, gusto in enumerate(gustos, 1):
                    tema = gusto.get("topic", "desconocido")
                    categoria = gusto.get("category", "desconocida")
                    sentimiento = gusto.get("sentiment", 0)
                    importancia = gusto.get("importance", 0)
                    print(f"  {i}. {tema} [{categoria}] (sent: {sentimiento:.2f}, imp: {importancia:.2f})")
            else:
                print("  Sin gustos registrados")
            
            # Mostrar disgustos
            print(f"\n{Fore.RED}👎 DISGUSTOS ({len(disgustos)}){Style.RESET_ALL}")
            if disgustos:
                for i, disgusto in enumerate(disgustos, 1):
                    tema = disgusto.get("topic", "desconocido")
                    categoria = disgusto.get("category", "desconocida")
                    sentimiento = disgusto.get("sentiment", 0)
                    importancia = disgusto.get("importance", 0)
                    print(f"  {i}. {tema} [{categoria}] (sent: {sentimiento:.2f}, imp: {importancia:.2f})")
            else:
                print("  Sin disgustos registrados")
        
        # 🆕 RESUMEN FINAL
        print(f"\n{'='*60}")
        print(f"{Fore.BLUE}📊 RESUMEN GLOBAL:{Style.RESET_ALL}")
        print(f"  👤 Usuarios totales: {len(usuarios)}")
        print(f"  👍 Gustos totales: {total_gustos}")
        print(f"  👎 Disgustos totales: {total_disgustos}")
        print(f"  📝 Preferencias totales: {total_gustos + total_disgustos}")
        print('='*60)
        
    else:
        # MODO NORMAL: USUARIO ESPECÍFICO
        usuario = getattr(args, 'user', 'global')
        print(f"{Fore.BLUE}⏳ Obteniendo preferencias de '{usuario}' desde la base de datos...{Style.RESET_ALL}")
        
        # Obtener datos de la base de datos para el usuario específico
        preferencias = obtener_preferencias_desde_db(usuario=usuario)
        
        if not preferencias:
            print(f"{Fore.YELLOW}⚠️ '{usuario}' no tiene preferencias registradas{Style.RESET_ALL}")
            
            # Sugerencia inteligente si no es global
            if usuario != "global":
                print(f"{Fore.CYAN}💡 Prueba: python3 {sys.argv[0]} list --user global{Style.RESET_ALL}")
            
            # Sugerencia para ver todos
            print(f"{Fore.CYAN}🌐 Ver todos: python3 {sys.argv[0]} list --all{Style.RESET_ALL}")
            
            # Mostrar usuarios disponibles como ayuda
            usuarios_disp = obtener_usuarios_disponibles()
            if usuarios_disp:
                print(f"{Fore.CYAN}👥 Usuarios con preferencias: {', '.join([u[0] for u in usuarios_disp[:5]])}{Style.RESET_ALL}")
            return
        
        # Cargar taxonomía para mostrar categorías completas
        taxonomia = cargar_taxonomia()
        
        # Separar por sentimiento positivo/negativo
        gustos = [p for p in preferencias if p.get("sentiment", 0) > 0]
        disgustos = [p for p in preferencias if p.get("sentiment", 0) < 0]
        
        print(f"\n{Fore.GREEN}👍 GUSTOS DE '{usuario.upper()}' ({len(gustos)}){Style.RESET_ALL}")
        if gustos:
            for i, gusto in enumerate(gustos, 1):
                tema = gusto.get("topic", "desconocido")
                categoria = gusto.get("category", "desconocida")
                sentimiento = gusto.get("sentiment", 0)
                importancia = gusto.get("importance", 0)
                
                cat_info = f" [{categoria}]"
                print(f"  {i}. {tema}{cat_info} (sent: {sentimiento:.2f}, imp: {importancia:.2f})")
        else:
            print(f"  {usuario} no tiene gustos registrados")
        
        print(f"\n{Fore.RED}👎 DISGUSTOS DE '{usuario.upper()}' ({len(disgustos)}){Style.RESET_ALL}")
        if disgustos:
            for i, disgusto in enumerate(disgustos, 1):
                tema = disgusto.get("topic", "desconocido")
                categoria = disgusto.get("category", "desconocida")
                sentimiento = disgusto.get("sentiment", 0)
                importancia = disgusto.get("importance", 0)
                
                cat_info = f" [{categoria}]"
                print(f"  {i}. {tema}{cat_info} (sent: {sentimiento:.2f}, imp: {importancia:.2f})")
        else:
            print(f"  {usuario} no tiene disgustos registrados")

def comando_search(args):
    """Busca preferencias por palabra clave en usuario específico"""
    usuario = getattr(args, 'user', 'global')
    
    if not args.texto:
        print(f"{Fore.RED}❌ Debes especificar un texto para buscar{Style.RESET_ALL}")
        return
    
    if not os.path.exists(DB_PATH):
        print(f"{Fore.RED}❌ Base de datos no encontrada: {DB_PATH}{Style.RESET_ALL}")
        return
    
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # BUSCAR SOLO EN LAS PREFERENCIAS DEL USUARIO ESPECÍFICO
        cursor.execute(
            "SELECT * FROM preferences WHERE topic LIKE ? AND user = ? ORDER BY importance DESC", 
            (f"%{args.texto}%", usuario)
        )
        
        resultados = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        if not resultados:
            print(f"{Fore.YELLOW}⚠️ '{usuario}' no tiene preferencias que contengan '{args.texto}'{Style.RESET_ALL}")
            
            # Sugerencia para buscar en global si no es global
            if usuario != "global":
                print(f"{Fore.CYAN}💡 Prueba buscar en global: python3 {sys.argv[0]} search '{args.texto}' --user global{Style.RESET_ALL}")
            return
        
        print(f"{Fore.GREEN}✅ Resultados de '{usuario}' con '{args.texto}' ({len(resultados)} encontrados):{Style.RESET_ALL}")
        
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
    """Muestra estadísticas de las preferencias del usuario especificado"""
    usuario = getattr(args, 'user', 'global')
    
    if not os.path.exists(DB_PATH):
        print(f"{Fore.RED}❌ Base de datos no encontrada: {DB_PATH}{Style.RESET_ALL}")
        return
    
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # ESTADÍSTICAS ESPECÍFICAS DEL USUARIO
        cursor.execute("SELECT COUNT(*) FROM preferences WHERE user = ?", (usuario,))
        total = cursor.fetchone()[0]
        
        if total == 0:
            print(f"{Fore.YELLOW}⚠️ '{usuario}' no tiene preferencias registradas{Style.RESET_ALL}")
            conn.close()
            return
        
        cursor.execute("SELECT COUNT(*) FROM preferences WHERE sentiment > 0 AND user = ?", (usuario,))
        total_gustos = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM preferences WHERE sentiment < 0 AND user = ?", (usuario,))
        total_disgustos = cursor.fetchone()[0]
        
        print(f"\n{Fore.BLUE}📊 ESTADÍSTICAS DE '{usuario.upper()}'{Style.RESET_ALL}")
        print(f"  Total de preferencias: {total}")
        print(f"  Gustos: {total_gustos}")
        print(f"  Disgustos: {total_disgustos}")
        
        # Estadísticas por categoría para este usuario
        cursor.execute(
            "SELECT category, COUNT(*) as count FROM preferences WHERE user = ? GROUP BY category ORDER BY count DESC",
            (usuario,)
        )
        cats = cursor.fetchall()
        
        if cats:
            print(f"\n{Fore.BLUE}📊 PREFERENCIAS POR CATEGORÍA DE '{usuario.upper()}'{Style.RESET_ALL}")
            for cat, count in cats:
                print(f"  {cat}: {count}")
        
        # Preferencias con mayor importancia para este usuario
        cursor.execute(
            "SELECT topic, category, sentiment, importance FROM preferences WHERE user = ? ORDER BY importance DESC LIMIT 5",
            (usuario,)
        )
        top_prefs = cursor.fetchall()
        
        if top_prefs:
            print(f"\n{Fore.BLUE}🌟 TOP 5 PREFERENCIAS MÁS IMPORTANTES DE '{usuario.upper()}'{Style.RESET_ALL}")
            for tema, cat, sent, imp in top_prefs:
                emoji = "👍" if sent > 0 else "👎"
                print(f"  {emoji} {tema} [{cat}] (importancia: {imp:.2f})")
        
        conn.close()
        
    except Exception as e:
        print(f"{Fore.RED}❌ Error al obtener estadísticas: {str(e)}{Style.RESET_ALL}")

def comando_usuarios(args):
    """Lista todos los usuarios que tienen preferencias registradas"""
    usuarios = obtener_usuarios_disponibles()
    
    if not usuarios:
        print(f"{Fore.YELLOW}⚠️ No hay usuarios con preferencias registradas{Style.RESET_ALL}")
        return
    
    print(f"{Fore.BLUE}👥 USUARIOS CON PREFERENCIAS:{Style.RESET_ALL}")
    for usuario, count in usuarios:
        # Destacar usuario global si existe
        if usuario == "global":
            print(f"  {Fore.CYAN}{usuario}{Style.RESET_ALL}: {count} preferencias {Fore.CYAN}(compartidas){Style.RESET_ALL}")
        else:
            print(f"  {usuario}: {count} preferencias")
    
    print(f"\n{Fore.CYAN}💡 Usa: python3 {sys.argv[0]} list --user <nombre_usuario>{Style.RESET_ALL}")

# =======================================================================
# 4. COMANDOS DEL CLI - OPERACIONES DE MODIFICACIÓN
# =======================================================================

def comando_add(args):
    """Añade una nueva preferencia al usuario especificado"""
    usuario = getattr(args, 'user', 'global')
    
    if not args.texto:
        print(f"{Fore.RED}❌ Debes especificar un texto para añadir como preferencia{Style.RESET_ALL}")
        return
    
    if not os.path.exists(DB_PATH):
        print(f"{Fore.RED}❌ Base de datos no encontrada: {DB_PATH}{Style.RESET_ALL}")
        return
    
    # Determinar tipo, categoría y valores
    tipo = "gusto" if not args.disgusto else "disgusto"
    sentimiento = 0.9 if tipo == "gusto" else -0.9
    importancia = args.importancia if args.importancia is not None else 0.8
    tema = args.texto.lower().strip()
    categoria = args.categoria if args.categoria else "general"
    
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # VERIFICAR SI EXISTE PARA ESTE USUARIO ESPECÍFICO
        cursor.execute(
            "SELECT id, sentiment, importance FROM preferences WHERE LOWER(topic) = ? AND user = ?", 
            (tema, usuario)
        )
        existente = cursor.fetchone()
        
        if existente:
            # Actualizar preferencia existente para este usuario
            id_pref, sent_ant, imp_ant = existente
            nuevo_sent = (sentimiento * 0.7) + (sent_ant * 0.3)  # Promedio ponderado
            nueva_imp = max(imp_ant, importancia)
            
            cursor.execute(
                "UPDATE preferences SET sentiment = ?, importance = ?, category = ?, timestamp = CURRENT_TIMESTAMP WHERE id = ?",
                (nuevo_sent, nueva_imp, categoria, id_pref)
            )
            
            print(f"{Fore.GREEN}✅ Preferencia actualizada para '{usuario}': '{tema}' (sent: {nuevo_sent:.2f}, imp: {nueva_imp:.2f}){Style.RESET_ALL}")
        else:
            # INSERTAR NUEVA PREFERENCIA CON USUARIO ESPECÍFICO
            cursor.execute(
                "INSERT INTO preferences (user, category, topic, sentiment, importance, source) VALUES (?, ?, ?, ?, ?, ?)",
                (usuario, categoria, tema, sentimiento, importancia, "CLI")
            )
            
            print(f"{Fore.GREEN}✅ Nueva preferencia para '{usuario}': '{tema}' (sent: {sentimiento:.2f}, imp: {importancia:.2f}){Style.RESET_ALL}")
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        print(f"{Fore.RED}❌ Error al añadir preferencia: {str(e)}{Style.RESET_ALL}")

def comando_delete(args):
    """Elimina una preferencia del usuario especificado"""
    usuario = getattr(args, 'user', 'global')
    
    if not args.texto:
        print(f"{Fore.RED}❌ Debes especificar un texto para eliminar{Style.RESET_ALL}")
        return
    
    if not os.path.exists(DB_PATH):
        print(f"{Fore.RED}❌ Base de datos no encontrada: {DB_PATH}{Style.RESET_ALL}")
        return
    
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # VERIFICAR SI EXISTE PARA ESTE USUARIO ESPECÍFICO
        cursor.execute(
            "SELECT id, topic FROM preferences WHERE LOWER(topic) = ? AND user = ?", 
            (args.texto.lower(), usuario)
        )
        existente = cursor.fetchone()
        
        if not existente:
            print(f"{Fore.YELLOW}⚠️ '{usuario}' no tiene una preferencia con el tema '{args.texto}'{Style.RESET_ALL}")
            
            # Sugerencia para verificar en global
            if usuario != "global":
                print(f"{Fore.CYAN}💡 Verifica si existe en global: python3 {sys.argv[0]} search '{args.texto}' --user global{Style.RESET_ALL}")
            
            conn.close()
            return
        
        id_pref, tema = existente
        
        # Eliminar preferencia específica del usuario
        cursor.execute("DELETE FROM preferences WHERE id = ?", (id_pref,))
        conn.commit()
        
        print(f"{Fore.GREEN}✅ Preferencia eliminada de '{usuario}': '{tema}'{Style.RESET_ALL}")
        conn.close()
        
    except Exception as e:
        print(f"{Fore.RED}❌ Error al eliminar preferencia: {str(e)}{Style.RESET_ALL}")

# =======================================================================
# 5. CONFIGURACIÓN DE ARGUMENTOS Y PARSER PRINCIPAL
# =======================================================================

def main():
    """Función principal del CLI con soporte multiusuario FUNCIONAL"""
    parser = argparse.ArgumentParser(description='TARS CLI - Interfaz multiusuario para preferencias')
    subparsers = parser.add_subparsers(dest='comando', help='Comandos disponibles')
    
    # =======================================================================
    # 5.1 FUNCIÓN HELPER PARA AÑADIR --user A SUBPARSERS
    # =======================================================================
    
    def add_user_argument(subparser):
        """Añade el argumento --user a un subparser"""
        subparser.add_argument('--user', '-u', default='global', 
                             help='Usuario para las preferencias (default: global)')
    
    # =======================================================================
    # 5.2 DEFINICIÓN DE SUBCOMANDOS CON --user EN CADA UNO
    # =======================================================================
    
    # Comando list
    list_parser = subparsers.add_parser('list', help='Listar preferencias del usuario especificado o de todos')
    add_user_argument(list_parser)
    # 🆕 AÑADIR OPCIÓN --all
    list_parser.add_argument('--all', '-a', action='store_true', 
                           help='Mostrar preferencias de todos los usuarios')
    
    # Comando add
    add_parser = subparsers.add_parser('add', help='Añadir preferencia al usuario especificado')
    add_parser.add_argument('texto', help='Texto de la preferencia a añadir')
    add_parser.add_argument('-d', '--disgusto', action='store_true', help='Añadir como disgusto en lugar de gusto')
    add_parser.add_argument('-c', '--categoria', help='Categoría a asignar')
    add_parser.add_argument('-i', '--importancia', type=float, help='Importancia (0.0 a 1.0)')
    add_user_argument(add_parser)
    
    # Comando search
    search_parser = subparsers.add_parser('search', help='Buscar preferencias del usuario por palabra clave')
    search_parser.add_argument('texto', help='Texto a buscar')
    add_user_argument(search_parser)
    
    # Comando delete
    delete_parser = subparsers.add_parser('delete', help='Eliminar preferencia del usuario')
    delete_parser.add_argument('texto', help='Tema de la preferencia a eliminar')
    add_user_argument(delete_parser)
    
    # Comando categorias (no necesita --user)
    cat_parser = subparsers.add_parser('categorias', help='Mostrar categorías disponibles en la taxonomía')
    
    # Comando stats
    stats_parser = subparsers.add_parser('stats', help='Mostrar estadísticas del usuario especificado')
    add_user_argument(stats_parser)
    
    # Comando usuarios (no necesita --user)
    usuarios_parser = subparsers.add_parser('usuarios', help='Listar todos los usuarios con preferencias')
    
    args = parser.parse_args()
    
    # =======================================================================
    # 5.3 DISTRIBUCIÓN DE COMANDOS
    # =======================================================================
    
    # Si no se especifica comando, mostrar ayuda
    if not args.comando:
        parser.print_help()
        print(f"\n{Fore.CYAN}💡 Ejemplos de uso:{Style.RESET_ALL}")
        print(f"  python3 {sys.argv[0]} list --user BeskarBuilder")
        print(f"  python3 {sys.argv[0]} list --all")
        print(f"  python3 {sys.argv[0]} add 'me relaja la astronomía' --user BeskarBuilder")
        print(f"  python3 {sys.argv[0]} usuarios")
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
    elif args.comando == 'usuarios':
        comando_usuarios(args)

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
# ESTADO: ARGUMENTOS ARREGLADOS + DATOS PRESERVADOS
# ÚLTIMA ACTUALIZACIÓN: Después de solucionar el lío de argparse de una vez por todas
# FILOSOFÍA: "Los argumentos son como las preferencias: mejor organizados desde el principio"
# CORRECCIÓN: --user funciona en cada subcommand sin conflictos
# ===============================================
#
#           THIS IS THE FUNCTIONAL CLI WAY... 
#           (porque un CLI que no acepta sus propios argumentos es como una IA que no escucha)
#
# ===============================================