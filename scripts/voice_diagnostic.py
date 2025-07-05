#!/usr/bin/env python3
# ===============================================
# VOICE ID DIAGNOSTIC TOOL
# Sistema de Diagnóstico Avanzado para Voice ID
# ===============================================
# 
# DESCRIPCIÓN:
# Herramienta de diagnóstico completa para analizar el funcionamiento
# del sistema de identificación vocal TARS. Proporciona análisis detallado
# de embeddings, similitudes y recomendaciones de optimización.
# 
# FUNCIONALIDADES PRINCIPALES:
# - Análisis técnico de archivos de audio y embeddings
# - Comparación de similitudes con múltiples métricas
# - Diagnóstico automático del estado del sistema
# - Recomendaciones de umbrales y configuraciones
# - Interpretación de resultados con estado visual
# 
# MÉTRICAS UTILIZADAS:
# - Similitud coseno (principal)
# - Distancia L2 euclidiana
# - Norma de embeddings
# - Estadísticas descriptivas completas
# 
# ===============================================

# ===============================================
# 1. IMPORTACIONES Y DEPENDENCIAS
# ===============================================
import os
import sys
import json
import numpy as np
import argparse
from pathlib import Path
from datetime import datetime
from resemblyzer import VoiceEncoder, preprocess_wav
from sklearn.metrics.pairwise import cosine_similarity
import soundfile as sf

# ===============================================
# 2. CLASE PRINCIPAL DE DIAGNÓSTICO
# ===============================================

class VoiceDiagnostic:
    """
    Sistema de diagnóstico avanzado para Voice ID.
    
    Proporciona análisis completo del funcionamiento del sistema de
    identificación vocal, incluyendo análisis de embeddings, comparaciones
    de similitud y recomendaciones de optimización automáticas.
    
    Attributes:
        encoder (VoiceEncoder): Encoder de Resemblyzer para análisis
        db_path (str): Ruta a la base de datos de embeddings
        results (dict): Almacén de resultados de análisis
    """
    
    def __init__(self):
        """
        Inicializa el sistema de diagnóstico.
        
        Configura las rutas por defecto y prepara el contenedor
        de resultados para análisis posteriores.
        """
        self.encoder = None
        self.db_path = "data/identity/voice_embeddings.json"
        self.results = {}

    # ===============================================
    # 3. SISTEMA DE CARGA Y INICIALIZACIÓN
    # ===============================================
        
    def load_encoder(self):
        """
        Carga y prepara el VoiceEncoder de Resemblyzer.
        
        Returns:
            bool: True si se carga correctamente, False en caso de error
            
        El encoder es fundamental para el análisis de embeddings.
        Si falla la carga, todo el sistema de diagnóstico se ve comprometido.
        """
        print("🧠 Cargando VoiceEncoder...")
        try:
            self.encoder = VoiceEncoder()
            print("✅ VoiceEncoder cargado correctamente")
            return True
        except Exception as e:
            print(f"❌ Error cargando VoiceEncoder: {e}")
            return False
    
    def load_database(self):
        """
        Carga la base de datos de embeddings de usuarios registrados.
        
        Returns:
            dict|None: Datos de la base de datos o None si hay error
            
        La base de datos contiene los embeddings de referencia de cada
        usuario registrado. Sin esta, no se pueden hacer comparaciones.
        """
        if not os.path.exists(self.db_path):
            print(f"❌ Base de datos no encontrada: {self.db_path}")
            return None
            
        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                db = json.load(f)
            print(f"✅ Base de datos cargada: {len(db.get('users', {}))} usuarios")
            return db
        except Exception as e:
            print(f"❌ Error cargando base de datos: {e}")
            return None

    # ===============================================
    # 4. MOTOR DE ANÁLISIS DE AUDIO
    # ===============================================
    
    def analyze_audio_file(self, file_path, name="Audio"):
        """
        Realiza análisis completo de un archivo de audio.
        
        Args:
            file_path (str): Ruta al archivo de audio
            name (str): Nombre descriptivo para el análisis
            
        Returns:
            dict|None: Análisis completo o None si hay error
            
        PROCESO DE ANÁLISIS:
        1. Carga metadatos del archivo (duración, frecuencia, etc.)
        2. Lee audio raw para estadísticas básicas
        3. Procesa con Resemblyzer (normalización, filtros)
        4. Genera embedding usando VoiceEncoder
        5. Calcula estadísticas descriptivas completas
        
        El análisis proporciona tanto datos técnicos del archivo
        como características del embedding generado.
        """
        if not os.path.exists(file_path):
            print(f"❌ Archivo no encontrado: {file_path}")
            return None
            
        try:
            # Información básica del archivo
            info = sf.info(file_path)
            raw_audio, _ = sf.read(file_path)
            
            # Procesamiento con Resemblyzer
            sys.path.append('core')
            from voice_utils import VoicePreprocessor
            preprocessor = VoicePreprocessor()
            audio = preprocessor.load_audio(file_path)
            processed_audio = preprocessor.normalize_volume(audio, target_dbfs=-20.0)
            embedding = self.encoder.embed_utterance(processed_audio)
            
            # Construcción del análisis completo
            analysis = {
                "file": file_path,
                "name": name,
                "duration": info.duration,
                "samplerate": info.samplerate,
                "channels": info.channels,
                "raw_rms": np.sqrt(np.mean(raw_audio**2)),
                "processed_rms": np.sqrt(np.mean(processed_audio**2)),
                "raw_samples": len(raw_audio),
                "processed_samples": len(processed_audio),
                "embedding": embedding,
                "embedding_norm": np.linalg.norm(embedding),
                "embedding_stats": {
                    "min": float(embedding.min()),
                    "max": float(embedding.max()),
                    "mean": float(embedding.mean()),
                    "std": float(embedding.std())
                }
            }
            
            return analysis
            
        except Exception as e:
            print(f"❌ Error analizando {file_path}: {e}")
            return None

    # ===============================================
    # 5. SISTEMA DE COMPARACIÓN DE EMBEDDINGS
    # ===============================================
    
    def compare_embeddings(self, embed1, embed2, name1="Audio 1", name2="Audio 2"):
        """
        Compara dos embeddings usando múltiples métricas matemáticas.
        
        Args:
            embed1 (np.ndarray): Primer embedding
            embed2 (np.ndarray): Segundo embedding
            name1 (str): Nombre del primer audio
            name2 (str): Nombre del segundo audio
            
        Returns:
            dict|None: Métricas de comparación o None si hay error
            
        MÉTRICAS CALCULADAS:
        - Similitud coseno: Métrica principal (0-1, 1=idénticos)
        - Similitud manual: Verificación del cálculo coseno
        - Distancia L2: Distancia euclidiana en espacio embedding
        - Estadísticas de diferencia: Análisis elemento por elemento
        
        La similitud coseno es la métrica más robusta para embeddings
        de voz ya que es invariante a la magnitud del vector.
        """
        try:
            # Similitud coseno usando sklearn (optimizada)
            cosine_sim = cosine_similarity(
                embed1.reshape(1, -1), 
                embed2.reshape(1, -1)
            )[0][0]
            
            # Similitud coseno manual (verificación)
            manual_sim = np.dot(embed1, embed2) / (
                np.linalg.norm(embed1) * np.linalg.norm(embed2)
            )
            
            # Distancia euclidiana L2
            l2_distance = np.linalg.norm(embed1 - embed2)
            
            # Análisis elemento por elemento
            diff = embed1 - embed2
            
            comparison = {
                "cosine_similarity": float(cosine_sim),
                "manual_similarity": float(manual_sim),
                "l2_distance": float(l2_distance),
                "difference_stats": {
                    "mean": float(diff.mean()),
                    "std": float(diff.std()),
                    "min": float(diff.min()),
                    "max": float(diff.max())
                }
            }
            
            return comparison
            
        except Exception as e:
            print(f"❌ Error comparando embeddings: {e}")
            return None
    
    def interpret_similarity(self, similarity):
        """
        Interpreta valores de similitud con clasificación visual.
        
        Args:
            similarity (float): Valor de similitud coseno (0-1)
            
        Returns:
            str: Interpretación con emoji de estado y descripción
            
        UMBRALES DE INTERPRETACIÓN:
        - 0.95+: Excelente (misma persona, muy alta confianza)
        - 0.85+: Muy buena (misma persona, alta confianza)
        - 0.75+: Buena (probablemente misma persona)
        - 0.65+: Moderada (posiblemente misma persona)
        - 0.50+: Baja (probablemente diferente persona)
        - <0.50: Muy baja (definitivamente diferente persona)
        
        """
        if similarity >= 0.95:
            return "🟢 EXCELENTE - Misma persona (muy alta confianza)"
        elif similarity >= 0.85:
            return "🟢 MUY BUENA - Misma persona (alta confianza)"
        elif similarity >= 0.75:
            return "🟡 BUENA - Probablemente misma persona"
        elif similarity >= 0.65:
            return "🟡 MODERADA - Posiblemente misma persona"
        elif similarity >= 0.50:
            return "🟠 BAJA - Probablemente diferente persona"
        else:
            return "🔴 MUY BAJA - Definitivamente diferente persona"

    # ===============================================
    # 6. SISTEMA DE PRESENTACIÓN DE RESULTADOS
    # ===============================================
    
    def print_audio_analysis(self, analysis):
        """
        Presenta análisis detallado de audio en formato estructurado.
        
        Args:
            analysis (dict): Datos del análisis de audio
            
        Muestra información técnica completa incluyendo:
        - Metadatos del archivo (duración, frecuencia, canales)
        - Estadísticas de señal (RMS antes/después procesamiento)
        - Características del embedding (norma, estadísticas)
        - Comparación entre audio original y procesado
        """
        if not analysis:
            return
            
        print(f"\n📊 ANÁLISIS DE {analysis['name'].upper()}")
        print("=" * 60)
        print(f"📁 Archivo: {analysis['file']}")
        print(f"⏱️ Duración: {analysis['duration']:.2f}s")
        print(f"🔊 Frecuencia: {analysis['samplerate']} Hz")
        print(f"📈 Canales: {analysis['channels']}")
        print(f"🎵 RMS Original: {analysis['raw_rms']:.6f}")
        print(f"🎵 RMS Procesado: {analysis['processed_rms']:.6f}")
        print(f"📊 Samples Original: {analysis['raw_samples']:,}")
        print(f"📊 Samples Procesado: {analysis['processed_samples']:,}")
        print(f"🧠 Embedding Norm: {analysis['embedding_norm']:.6f}")
        print(f"📈 Embedding Stats:")
        stats = analysis['embedding_stats']
        print(f"   - Min: {stats['min']:.6f}")
        print(f"   - Max: {stats['max']:.6f}")
        print(f"   - Mean: {stats['mean']:.6f}")
        print(f"   - Std: {stats['std']:.6f}")
    
    def print_comparison(self, comparison, name1, name2):
        """
        Presenta comparación detallada entre dos embeddings.
        
        Args:
            comparison (dict): Datos de la comparación
            name1 (str): Nombre del primer audio
            name2 (str): Nombre del segundo audio
            
        Incluye interpretación automática del resultado y
        todas las métricas calculadas para análisis técnico.
        """
        if not comparison:
            return
            
        sim = comparison['cosine_similarity']
        interpretation = self.interpret_similarity(sim)
        
        print(f"\n🔍 COMPARACIÓN: {name1} vs {name2}")
        print("=" * 60)
        print(f"🎯 Similitud Coseno: {sim:.6f}")
        print(f"🎯 Similitud Manual: {comparison['manual_similarity']:.6f}")
        print(f"📏 Distancia L2: {comparison['l2_distance']:.6f}")
        print(f"📊 Interpretación: {interpretation}")
        
        print(f"\n📈 Estadísticas de Diferencias:")
        diff_stats = comparison['difference_stats']
        print(f"   - Media: {diff_stats['mean']:.6f}")
        print(f"   - Desv. Estándar: {diff_stats['std']:.6f}")
        print(f"   - Mínimo: {diff_stats['min']:.6f}")
        print(f"   - Máximo: {diff_stats['max']:.6f}")

    # ===============================================
    # 7. SISTEMA DE DIAGNÓSTICO AUTOMÁTICO
    # ===============================================
    
    def test_current_setup(self, simple=False):
        """
        Ejecuta diagnóstico completo del estado actual del sistema.
        
        Args:
            simple (bool): Si usar formato simplificado
            
        PROCESO DE DIAGNÓSTICO:
        1. Carga y valida el VoiceEncoder
        2. Carga y valida la base de datos
        3. Identifica usuarios disponibles
        4. Ejecuta análisis automático si hay un solo usuario
        5. Proporciona guía de uso si hay múltiples usuarios
        
        En sistemas con un solo usuario, ejecuta análisis completo
        automáticamente. Con múltiples usuarios, requiere especificación.
        """
        print("\n🔬 DIAGNÓSTICO COMPLETO DEL SISTEMA")
        print("=" * 80)
        
        # Validación del encoder
        if not self.load_encoder():
            return
        
        # Validación de la base de datos
        db = self.load_database()
        if not db:
            return
        
        # Análisis de usuarios disponibles
        users = db.get('users', {})
        if len(users) > 1:
            print(f"\n👥 Usuarios registrados: {', '.join(users.keys())}")
            print("💡 Usa --user NOMBRE para análisis específico")
            return
        
        # Análisis automático para usuario único
        if len(users) == 1:
            username = list(users.keys())[0]
            print(f"\n🎯 Analizando usuario: {username}")
            self.test_specific_user(username, simple)
    
    def test_specific_user(self, username, simple=False):
        """
        Ejecuta análisis específico y detallado para un usuario.
        
        Args:
            username (str): Nombre del usuario a analizar
            simple (bool): Si usar formato simplificado
            
        ANÁLISIS REALIZADO:
        1. Validación de existencia del usuario
        2. Análisis de archivos de audio relevantes
        3. Comparación entre archivos disponibles
        4. Comparación con embedding almacenado en BD
        5. Generación de recomendaciones específicas
        
        Los archivos analizados incluyen:
        - Último wakeword capturado
        - Archivo de registro del usuario
        - Cualquier otro archivo temporal relevante
        """
        db = self.load_database()
        if not db:
            return
            
        # Validación del usuario
        users = db.get('users', {})
        if username not in users:
            print(f"❌ Usuario '{username}' no encontrado")
            print(f"Usuarios disponibles: {', '.join(users.keys())}")
            return
        
        # Definición de archivos a analizar
        files_to_test = {
            "Último Wakeword": "temp/last_wakeword.wav",
            f"Registro {username}": f"temp/voice_registration_{username}.wav"
        }
        
        # Análisis de archivos disponibles
        analyses = {}
        for name, path in files_to_test.items():
            if os.path.exists(path):
                analysis = self.analyze_audio_file(path, name)
                if analysis:
                    analyses[name] = analysis
                    if not simple:
                        self.print_audio_analysis(analysis)
        
        # Comparaciones cruzadas entre archivos
        if len(analyses) >= 2 and not simple:
            print(f"\n🔍 REALIZANDO COMPARACIONES")
            print("=" * 80)
            
            audio_names = list(analyses.keys())
            for i in range(len(audio_names)):
                for j in range(i + 1, len(audio_names)):
                    name1, name2 = audio_names[i], audio_names[j]
                    embed1 = analyses[name1]['embedding']
                    embed2 = analyses[name2]['embedding']
                    
                    comparison = self.compare_embeddings(embed1, embed2, name1, name2)
                    self.print_comparison(comparison, name1, name2)
        
        # Análisis del embedding almacenado en base de datos
        if not simple:
            print(f"\n💾 ANÁLISIS DE BASE DE DATOS")
            print("=" * 80)
        
        user_data = users[username]
        if isinstance(user_data, dict) and 'embedding' in user_data:
            stored_embedding = np.array(user_data['embedding'])
            
            if not simple:
                print(f"\n👤 Usuario: {username}")
                print(f"   - Embedding Norm: {np.linalg.norm(stored_embedding):.6f}")
                print(f"   - Min/Max: {stored_embedding.min():.6f} / {stored_embedding.max():.6f}")
                print(f"   - Valores no-cero: {np.count_nonzero(stored_embedding)}/256")
            
            # Comparación BD vs archivos actuales
            for name, analysis in analyses.items():
                comparison = self.compare_embeddings(
                    stored_embedding, analysis['embedding'], 
                    f"BD-{username}", name
                )
                if comparison:
                    sim = comparison['cosine_similarity']
                    interpretation = self.interpret_similarity(sim)
                    if simple:
                        print(f"   {name}: {sim:.3f}")
                    else:
                        print(f"   vs {name}: {sim:.6f} - {interpretation}")
        
        # Generación de recomendaciones
        self.print_recommendations(analyses, db)

    # ===============================================
    # 8. SISTEMA DE RECOMENDACIONES INTELIGENTES
    # ===============================================
    
    def print_recommendations(self, analyses, db):
        """
        Genera recomendaciones específicas basadas en el análisis.
        
        Args:
            analyses (dict): Análisis de archivos realizados
            db (dict): Base de datos de usuarios
            
        RECOMENDACIONES GENERADAS:
        1. Estado actual del sistema (funcionamiento/problemas)
        2. Ajustes de umbral recomendados
        3. Necesidad de re-registro
        4. Problemas de configuración detectados
        5. Parámetros técnicos optimizados
        
        Las recomendaciones son específicas para el usuario analizado
        y consideran las similitudes reales medidas vs. umbrales actuales.
        """
        print(f"\n🎯 DIAGNÓSTICO DEL SISTEMA")
        print("=" * 80)
        
        # Análisis para usuario principal (BeskarBuilder como ejemplo)
        users = db.get('users', {})
        if 'BeskarBuilder' in users and 'Último Wakeword' in analyses and 'Registro BeskarBuilder' in analyses:
            
            wakeword = analyses['Último Wakeword']
            registro = analyses['Registro BeskarBuilder']
            stored_embedding = np.array(users['BeskarBuilder']['embedding'])
            
            # Cálculo de similitudes críticas
            bd_vs_registro = self.compare_embeddings(stored_embedding, registro['embedding'])
            bd_vs_wakeword = self.compare_embeddings(stored_embedding, wakeword['embedding'])
            
            if bd_vs_registro and bd_vs_wakeword:
                sim_bd_registro = bd_vs_registro['cosine_similarity']
                sim_bd_wakeword = bd_vs_wakeword['cosine_similarity']
                
                print("📊 Similitudes clave:")
                print(f"   BD ↔ Registro:  {sim_bd_registro:.3f}")
                print(f"   BD ↔ Wakeword:  {sim_bd_wakeword:.3f}")
                print(f"   Umbral actual:  0.800")
                
                # Evaluación del estado del sistema
                print(f"\n⚙️ Estado del sistema:")
                
                registro_status = "✅ Válido" if sim_bd_registro >= 0.71 else "❌ Inválido"
                wakeword_status = "✅ Válido" if sim_bd_wakeword >= 0.71 else "❌ Degradado"
                
                print(f"   Registro:  {registro_status} ({sim_bd_registro:.3f})")
                print(f"   Wakeword:  {wakeword_status} ({sim_bd_wakeword:.3f})")
                
                # Análisis predictivo de funcionamiento
                print(f"\n🔍 Análisis:")
                
                if sim_bd_registro >= 0.80:
                    print("   • El sistema debería reconocerte perfectamente")
                elif sim_bd_registro >= 0.70:
                    print("   • Funcionamiento correcto con umbral ajustado")
                    recommended_threshold = round(max(0.65, sim_bd_wakeword - 0.02), 2)
                    print(f"   • Umbral recomendado: {recommended_threshold}")
                else:
                    print("   • Requiere re-registro completo")
                
                if sim_bd_wakeword < 0.65:
                    print("   • Wakeword presenta problemas de captura")
                    
                # Soluciones específicas y accionables
                print(f"\n🛠️ Acciones recomendadas:")
                
                if sim_bd_registro >= 0.70 and sim_bd_wakeword < 0.70:
                    recommended_threshold = round(max(0.65, sim_bd_registro - 0.05), 2)
                    print(f"   1. Ajustar umbral a {recommended_threshold} en voice_id.py")
                    print(f"   2. Verificar configuración de SpeechListener")
                    
                elif sim_bd_registro < 0.70:
                    print(f"   1. Re-registrar usuario con audio de mayor calidad")
                    print(f"   2. Verificar configuración del micrófono")
                    
                else:
                    print(f"   • Sistema operativo - sin cambios necesarios")
        
        # Configuración técnica recomendada
        print(f"\n⚙️ Configuración técnica:")
        
        # Cálculo específico de umbral óptimo
        if 'BeskarBuilder' in users and 'Último Wakeword' in analyses:
            stored_embedding = np.array(users['BeskarBuilder']['embedding'])
            wakeword = analyses['Último Wakeword']
            bd_vs_wakeword = self.compare_embeddings(stored_embedding, wakeword['embedding'])
            
            if bd_vs_wakeword:
                sim = bd_vs_wakeword['cosine_similarity']
                if 0.60 <= sim < 0.80:
                    recommended_threshold = round(max(0.65, sim - 0.03), 2)
                    print(f"   • voice_id.py → base_threshold = {recommended_threshold}")
                    print(f"   • Archivo: core/voice_id.py")
                    print(f"   • Función: _calculate_dynamic_threshold()")
        
        print(f"   • Parámetros estándar: umbral=0.70-0.75, min_duration=1.5s")
        
        # Resumen ejecutivo con estado visual
        if 'BeskarBuilder' in users and bd_vs_registro:
            sim = bd_vs_registro['cosine_similarity']
            if sim >= 0.80:
                status = "🟢 ÓPTIMO"
            elif sim >= 0.70:
                status = "🟡 FUNCIONAL"
            else:
                status = "🔴 REQUIERE ATENCIÓN"
                
            print(f"\n📋 Resumen: {status} (similitud: {sim:.3f})")

# ===============================================
# 9. FUNCIÓN PRINCIPAL Y MANEJO DE CLI
# ===============================================

def main():
    """
    Función principal con manejo completo de argumentos CLI.
    
    Proporciona interfaz de línea de comandos para todas las
    funcionalidades del sistema de diagnóstico.
    
    COMANDOS DISPONIBLES:
    --test: Diagnóstico completo automático
    --user USERNAME: Análisis específico de usuario
    --list: Lista usuarios registrados
    --compare FILE1 FILE2: Compara dos archivos de audio
    --analyze FILE: Analiza archivo específico
    --simple: Modo simplificado (menos detalles)
    
    Sin argumentos, ejecuta diagnóstico completo por defecto.
    """
    parser = argparse.ArgumentParser(description="Diagnóstico de Voice ID")
    parser.add_argument("--test", action="store_true", help="Ejecutar test completo")
    parser.add_argument("--user", metavar='USERNAME', help="Analizar usuario específico")
    parser.add_argument("--list", action="store_true", help="Listar todos los usuarios")
    parser.add_argument("--compare", nargs=2, metavar=('FILE1', 'FILE2'), 
                       help="Comparar dos archivos de audio")
    parser.add_argument("--analyze", metavar='FILE', help="Analizar un archivo específico")
    parser.add_argument("--simple", action="store_true", help="Modo simplificado (menos detalles)")
    
    args = parser.parse_args()
    
    diagnostic = VoiceDiagnostic()
    
    if args.list:
        # === LISTADO DE USUARIOS ===
        db = diagnostic.load_database()
        if db:
            users = db.get('users', {})
            print(f"\n👥 USUARIOS REGISTRADOS ({len(users)}):")
            print("=" * 40)
            for username, user_data in users.items():
                if isinstance(user_data, dict) and 'stats' in user_data:
                    stats = user_data['stats']
                    samples = stats.get('total_samples', 1)
                    last_update = stats.get('last_update', 'Desconocido')[:10]
                    print(f"   • {username} ({samples} muestras, {last_update})")
                else:
                    print(f"   • {username} (datos incompletos)")
    
    elif args.user:
        # === ANÁLISIS DE USUARIO ESPECÍFICO ===
        username = args.user
        if diagnostic.load_encoder():
            diagnostic.test_specific_user(username, simple=args.simple)
    
    elif args.test or len(sys.argv) == 1:
        # === DIAGNÓSTICO COMPLETO ===
        diagnostic.test_current_setup(simple=args.simple)
        
    elif args.compare:
        # === COMPARACIÓN DE DOS ARCHIVOS ===
        file1, file2 = args.compare
        if diagnostic.load_encoder():
            analysis1 = diagnostic.analyze_audio_file(file1, f"Archivo 1")
            analysis2 = diagnostic.analyze_audio_file(file2, f"Archivo 2")
            
            if analysis1 and analysis2:
                if not args.simple:
                    diagnostic.print_audio_analysis(analysis1)
                    diagnostic.print_audio_analysis(analysis2)
                
                comparison = diagnostic.compare_embeddings(
                    analysis1['embedding'], analysis2['embedding'],
                    file1, file2
                )
                diagnostic.print_comparison(comparison, file1, file2)
    
    elif args.analyze:
        # === ANÁLISIS DE ARCHIVO INDIVIDUAL ===
        if diagnostic.load_encoder():
            analysis = diagnostic.analyze_audio_file(args.analyze, "Archivo")
            if analysis:
                diagnostic.print_audio_analysis(analysis)

# ===============================================
# 10. PUNTO DE ENTRADA DEL PROGRAMA
# ===============================================

if __name__ == "__main__":
    main()

# ===============================================
# ESTADO: ANÁLISIS FINALIZADO (pero emocionalmente roto)
# ÚLTIMA ACTUALIZACIÓN: Justo antes de declarar “esta muestra está mal”
# FILOSOFÍA: "La voz no miente. Pero puede herir espectrogramas sensibles."
# ===============================================
#
#           THIS IS THE SONIC AUTOPSY ROOM WAY...
#           (tus frecuencias bajas no pasarán desapercibidas)
#
# ===============================================