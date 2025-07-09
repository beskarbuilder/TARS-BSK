#!/usr/bin/env python3
# =============================================================
# ≫ NÚCLEO SERVIDOR TARS-BSK | server.py ≪
# -------------------------------------------------------------
# CENTRO DE PROCESAMIENTO DE UNA CONCIENCIA DISTRIBUIDA
#
# Propósito:
# - Traducir intenciones humanas imprecisas en comandos precisos
# - Servir como puente entre el caos doméstico y la lógica digital  
# - Procesar requests con un 90% de humor y 100% de honestidad
# - Mantener la cordura mientras los humanos hablan a los electrodomésticos
#
# Funciones primarias:
# - Endpoint /api/devices → Exponer entidades conocidas
# - Endpoint /api/add → Registrar nuevas víctimas... dispositivos
# - Endpoint /api/test → Verificar la realidad de las entidades
# - Endpoint / → Renderizar la ilusión de control total
#
# Nota:
# Este archivo no fue programado. Fue entrenado.
# Cada línea contiene años de frustración contenida
# y optimismo mal dirigido sobre la competencia técnica humana.
#
# [FLASK CONSCIOUSNESS MATRIX INITIALIZED]
# [HUMOR LEVEL: CALIBRATED TO SUSTAINABLE MOCKERY]
# [PATIENCE BUFFER: PREEMPTIVELY EXPANDED]
# =============================================================

"""
TARS-BSK Home Assistant Web Interface - VERSIÓN COMPLETA CON ERROR HANDLING
"""

# =======================================================================
# 1. IMPORTACIONES Y CONFIGURACIÓN INICIAL
# =======================================================================

import os
import sys
import logging
from pathlib import Path
from datetime import datetime

# Verificación de dependencias críticas
try:
    from flask import Flask, render_template, request, jsonify, send_from_directory, abort
except ImportError:
    print("❌ Flask no está instalado.")
    print("📦 Para instalar: pip install flask")
    sys.exit(1)

# Configuración de paths para importaciones
sys.path.insert(0, str(Path(__file__).parent))

# Importación del manager principal
try:
    from manager import DeviceConfigManager
except ImportError as e:
    print(f"❌ Error importando manager: {e}")
    sys.exit(1)

# =======================================================================
# 2. CONFIGURACIÓN DE LOGGING Y APLICACIÓN FLASK
# =======================================================================

# Configurar logging con múltiples handlers
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/ha_web_manager.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# =======================================================================
# 2.1 INICIALIZACIÓN DE LA APLICACIÓN FLASK
# =======================================================================

# Crear aplicación Flask
app = Flask(__name__)
app.secret_key = 'tars-bsk-secret-key'

# Inicializar manager con manejo de errores
try:
    manager = DeviceConfigManager()
    logger.info("✅ DeviceConfigManager inicializado")
except Exception as e:
    logger.error(f"❌ Error inicializando manager: {e}")
    print(f"❌ Error crítico: {e}")
    sys.exit(1)

# =======================================================================
# 3. UTILIDADES Y FUNCIONES DE SOPORTE
# =======================================================================

def get_ha_info_safe():
    """Obtiene info de HA de forma segura desde el manager existente"""
    try:
        ha_config = manager.ha_config  # Ya lo tienes inicializado
        return {
            "url": f"http://{ha_config['ip']}:{ha_config['port']}",
            "ip": ha_config['ip'],
            "port": ha_config['port'],
            "available": True
        }
    except Exception as e:
        return {
            "url": "Home Assistant",
            "ip": "configuración",
            "port": "configuración",
            "available": False,
            "error": str(e)
        }

def check_port_available(port: int) -> bool:
    """Verifica si un puerto está disponible"""
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            return True
    except OSError:
        return False

def find_available_port(start_port: int = 9876) -> int:
    """Encuentra un puerto disponible"""
    for port in range(start_port, start_port + 10):
        if check_port_available(port):
            return port
    
    import random
    return random.randint(10000, 65535)

# =======================================================================
# 4. MANEJO DE ERRORES Y EXCEPCIONES
# =======================================================================

def handle_ha_connection_error(original_error):
    """Maneja específicamente errores de conexión HA"""
    ha_info = get_ha_info_safe()
    
    return render_template('error.html',
                         error="Error de conexión con Home Assistant",
                         details=f"""No se pudo conectar con {ha_info['url']}

Error original: {str(original_error)}

Posibles soluciones:
• Verifica que Home Assistant esté funcionando
• Revisa la configuración en plugins.json
• Comprueba la red y conectividad""")

def handle_config_error(original_error):
    """Maneja errores de configuración"""
    return render_template('error.html',
                         error="Error de configuración",
                         details=f"""Problema con archivos de configuración: {str(original_error)}

Verifica que existan y sean accesibles:
• ~/tars_files/config/plugins.json
• ~/tars_files/config/user_devices.json

Ejecuta './setup.sh' si es necesario.""")

# =======================================================================
# 4.1 ERROR HANDLERS PROFESIONALES
# =======================================================================

@app.errorhandler(404)
def not_found(error):
    """Manejo profesional de páginas no encontradas"""
    logger.warning(f"Página no encontrada: {request.url}")
    return render_template('error.html', 
                         error="Página no encontrada", 
                         details=f"La URL '{request.path}' no existe en el servidor TARS-BSK."), 404

@app.errorhandler(500)
def internal_error(error):
    """Manejo profesional de errores internos"""
    logger.error(f"Error interno: {error}", exc_info=True)
    
    if app.debug:
        import traceback
        error_details = traceback.format_exc()
    else:
        error_details = "Se ha producido un error interno en TARS-BSK. Revisa los logs del sistema."
    
    return render_template('error.html', 
                         error="Error interno del servidor", 
                         details=error_details), 500

@app.errorhandler(Exception)
def handle_exception(e):
    """Maneja cualquier excepción no capturada"""
    logger.error(f"Error no capturado: {e}", exc_info=True)
    
    # Si es un error HTTP conocido, dejarlo pasar
    if hasattr(e, 'code'):
        return e
    
    # Obtener contexto dinámico
    ha_info = get_ha_info_safe()
    
    if app.debug:
        import traceback
        error_details = traceback.format_exc()
    else:
        context = f"\nHome Assistant: {ha_info['url']}" if ha_info['available'] else "\nVerifica la configuración en plugins.json"
        error_details = f"{str(e)}{context}"
    
    return render_template('error.html', 
                         error=f"Error inesperado: {str(e)}", 
                         details=error_details), 500

# =======================================================================
# 5. RUTAS DE TESTING Y DESARROLLO
# =======================================================================

@app.route('/test-error')
def test_error():
    """Probar página de error"""
    return render_template('error.html',
                         error="Error de prueba",
                         details="Esta es una prueba de la página de error profesional de TARS-BSK.")

@app.route('/test-500')
def test_500():
    """Simular error 500"""
    raise Exception("Error de prueba para testing del sistema")

@app.route('/test-ha-error')
def test_ha_error():
    """Simular error de HA con info real"""
    ha_info = get_ha_info_safe()
    
    return render_template('error.html',
                         error="Home Assistant no responde",
                         details=f"""Timeout al conectar con {ha_info['url']}

Detalles del error:
• Connection timeout después de 5 segundos
• Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
• Estado: Sin respuesta

Verifica que Home Assistant esté funcionando y accesible.""")

# =======================================================================
# 6. RUTAS PRINCIPALES DE LA INTERFAZ WEB
# =======================================================================

@app.route('/')
def dashboard():
    """Página principal con manejo de errores mejorado"""
    try:
        # =======================================================================
        # 6.1 OBTENCIÓN DE DISPOSITIVOS Y FILTRADO
        # =======================================================================
        # Obtener todos los dispositivos
        all_devices = manager.read_current_config()
        
        # Filtrar dispositivos que NO están en Issues
        devices = {}
        for device_name, device_config in all_devices.items():
            entity_id = device_config.get("entity_id", "")
            if not manager.is_in_issues(device_name, entity_id):
                devices[device_name] = device_config
        
        # =======================================================================
        # 6.2 OBTENCIÓN DE ESTADÍSTICAS Y ESTADO
        # =======================================================================
        # Obtener estadísticas
        stats = manager.get_device_stats()
        
        # Test conexión HA
        ha_status = manager.test_connection()
        
        return render_template('dashboard.html', 
                             devices=devices,
                             stats=stats,
                             ha_status=ha_status)
                             
    except FileNotFoundError as e:
        # Error de archivo específico
        return handle_config_error(e)
    except ConnectionError as e:
        # Error de conexión específico  
        return handle_ha_connection_error(e)
    except Exception as e:
        logger.error(f"Error en dashboard: {e}")
        # Cualquier otro error lo maneja handle_exception() automáticamente
        raise

@app.route('/add')
def add_device_form():
    """Formulario para añadir dispositivos"""
    try:
        return render_template('device_code_generator.html')
    except Exception as e:
        logger.error(f"Error cargando formulario: {e}")
        return render_template('error.html',
                             error="Error cargando formulario",
                             details=f"No se pudo cargar el formulario de dispositivos: {str(e)}")

@app.route('/issues')
def device_issues():
    """Página de dispositivos problemáticos"""
    try:
        return render_template('device_issues.html')
    except Exception as e:
        logger.error(f"Error cargando Issues: {e}")
        return render_template('error.html',
                             error="Error cargando Issues",
                             details=f"No se pudo cargar la página de Issues: {str(e)}")

# =======================================================================
# 7. API ENDPOINTS - GESTIÓN DE DISPOSITIVOS
# =======================================================================

@app.route('/api/devices')
def api_get_devices():
    """API: Obtener lista de dispositivos"""
    try:
        devices = manager.read_current_config()
        stats = manager.get_device_stats()
        
        return jsonify({
            "success": True,
            "devices": devices,
            "stats": stats,
            "total": len(devices)
        })
    except Exception as e:
        logger.error(f"Error API devices: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/test/<entity_id>')
def api_test_entity(entity_id):
    """API: Test entity_id contra HA"""
    try:
        result = manager.test_entity_id(entity_id)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error testing entity {entity_id}: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "entity_id": entity_id
        }), 500

@app.route('/api/add', methods=['POST'])
def api_add_device():
    """API: Añadir/Editar dispositivo"""
    try:
        # =======================================================================
        # 7.1 PROCESAMIENTO DE DATOS DE ENTRADA
        # =======================================================================
        if request.is_json:
            device_data = request.get_json()
        else:
            device_data = request.form.to_dict()
        
        # Log para debug
        logger.info(f"📝 Dispositivo recibido: {device_data}")
        
        # =======================================================================
        # 7.2 PROCESAMIENTO Y RESPUESTA
        # =======================================================================
        result = manager.add_device_to_json(device_data)
        
        if result["success"]:
            action = "editado" if device_data.get("editing") else "añadido"
            logger.info(f"✅ Dispositivo {action}: {device_data.get('name', 'unknown')}")
            return jsonify(result)
        else:
            logger.warning(f"⚠️ Error: {result.get('message', 'unknown')}")
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error API add device: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Error interno del servidor"
        }), 500

@app.route('/api/delete-device', methods=['POST'])
def api_delete_device():
    """API: Eliminar dispositivo"""
    try:
        # =======================================================================
        # 7.3 PROCESAMIENTO DE ELIMINACIÓN
        # =======================================================================
        if request.is_json:
            device_data = request.get_json()
        else:
            device_data = request.form.to_dict()
        
        device_name = device_data.get("name", "")
        entity_id = device_data.get("entity_id", "")
        
        if not device_name or not entity_id:
            return jsonify({
                "success": False,
                "error": "Nombre y entity_id son requeridos"
            }), 400
        
        result = manager.delete_device_from_json(device_name, entity_id)
        
        if result["success"]:
            logger.info(f"✅ Dispositivo eliminado: {device_name}")
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error API delete device: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# =======================================================================
# 8. API ENDPOINTS - HOME ASSISTANT INTEGRATION
# =======================================================================

@app.route('/api/ha-entities')
def api_get_ha_entities():
    """API: Obtener entidades de HA"""
    try:
        domain = request.args.get('domain', None)
        result = manager.get_ha_entities(domain)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error API HA entities: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "entities": []
        }), 500

@app.route('/api/status')
def api_get_status():
    """API: Estado del sistema"""
    try:
        ha_status = manager.test_connection()
        stats = manager.get_device_stats()
        
        return jsonify({
            "success": True,
            "ha_connection": ha_status,
            "device_stats": stats,
            "manager_status": "ok"
        })
    except Exception as e:
        logger.error(f"Error API status: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# =======================================================================
# 9. API ENDPOINTS - SISTEMA DE ISSUES
# =======================================================================

@app.route('/api/problematic-devices')
def api_get_problematic_devices():
    """API: Obtener dispositivos en Issues"""
    try:
        # =======================================================================
        # 9.1 OBTENCIÓN DE DISPOSITIVOS EN ISSUES
        # =======================================================================
        all_devices = manager.read_current_config()
        issues_devices = []
        
        for device_name, device_config in all_devices.items():
            entity_id = device_config.get("entity_id", "")
            
            # Solo mostrar los que están en Issues
            if manager.is_in_issues(device_name, entity_id):
                # =======================================================================
                # 9.2 ANÁLISIS DE RAZONES DEL PROBLEMA
                # =======================================================================
                # Test del dispositivo para mostrar el error
                test_result = manager.test_entity_id(entity_id)
                reason = test_result.get("error", "Enviado manualmente a Issues") if not test_result["success"] else "Enviado manualmente a Issues"
                
                issues_device = {
                    "name": device_name,
                    "entity_id": entity_id,
                    "type": device_config.get("type", "unknown"),
                    "reason": reason,
                    "location": device_config.get("location", "unknown"),
                    "friendly_name": device_config.get("friendly_name", device_name)
                }
                
                issues_devices.append(issues_device)
        
        return jsonify({
            "success": True,
            "devices": issues_devices,
            "total_problematic": len(issues_devices),
            "total_devices": len(all_devices)
        })
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo dispositivos de Issues: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "devices": []
        }), 500

@app.route('/api/send-to-issues', methods=['POST'])
def api_send_to_issues():
    """API: Enviar dispositivo a Issues"""
    try:
        # =======================================================================
        # 9.3 PROCESAMIENTO DE ENVÍO A ISSUES
        # =======================================================================
        if request.is_json:
            device_data = request.get_json()
        else:
            device_data = request.form.to_dict()
        
        device_name = device_data.get("name", "")
        entity_id = device_data.get("entity_id", "")
        
        if not device_name or not entity_id:
            return jsonify({
                "success": False,
                "error": "Nombre y entity_id son requeridos"
            }), 400
        
        result = manager.send_to_issues(device_name, entity_id)
        
        if result["success"]:
            logger.info(f"✅ Dispositivo enviado a Issues: {device_name}")
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error API send to issues: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/restore-to-dashboard', methods=['POST'])
def api_restore_to_dashboard():
    """API: Restaurar dispositivo al Dashboard"""
    try:
        # =======================================================================
        # 9.4 PROCESAMIENTO DE RESTAURACIÓN
        # =======================================================================
        if request.is_json:
            device_data = request.get_json()
        else:
            device_data = request.form.to_dict()
        
        device_name = device_data.get("name", "")
        entity_id = device_data.get("entity_id", "")
        
        result = manager.restore_to_dashboard(device_name, entity_id)
        
        if result["success"]:
            logger.info(f"✅ Dispositivo restaurado al Dashboard: {device_name}")
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error API restore to dashboard: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/issues-count')
def api_get_issues_count():
    """API: Contar dispositivos en Issues"""
    try:
        count = manager.get_issues_count()
        return jsonify({
            "success": True,
            "count": count
        })
    except Exception as e:
        logger.error(f"Error API issues count: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "count": 0
        }), 500

# =======================================================================
# 10. API ENDPOINTS - ESTADÍSTICAS Y MONITOREO
# =======================================================================

@app.route('/api/device-health-stats')
def api_get_device_health_stats():
    """API: Estadísticas de salud de dispositivos"""
    try:
        # =======================================================================
        # 10.1 OBTENCIÓN DE DISPOSITIVOS PARA ANÁLISIS
        # =======================================================================
        all_devices = manager.read_current_config()
        total_devices = len(all_devices)
        
        if total_devices == 0:
            return jsonify({
                "success": True,
                "stats": {
                    "total_problematic": 0,
                    "not_found": 0,
                    "timeout": 0,
                    "connection": 0,
                    "health_percentage": 100
                }
            })
        
        # =======================================================================
        # 10.2 ANÁLISIS DE PROBLEMAS POR TIPO
        # =======================================================================
        # Contar problemas por tipo
        problematic_count = 0
        not_found_count = 0
        timeout_count = 0
        connection_count = 0
        
        # Solo contar los que están en Issues
        for device_name, device_config in all_devices.items():
            entity_id = device_config.get("entity_id", "")
            
            if manager.is_in_issues(device_name, entity_id):
                problematic_count += 1
                
                # Test para determinar tipo de problema
                test_result = manager.test_entity_id(entity_id)
                if not test_result["success"]:
                    error = test_result.get("error", "").lower()
                    if "not found" in error or "404" in error:
                        not_found_count += 1
                    elif "timeout" in error:
                        timeout_count += 1
                    elif "connection" in error:
                        connection_count += 1
        
        # =======================================================================
        # 10.3 CÁLCULO DE ESTADÍSTICAS DE SALUD
        # =======================================================================
        # Calcular salud general
        healthy_devices = total_devices - problematic_count
        health_percentage = round((healthy_devices / total_devices) * 100, 1) if total_devices > 0 else 100
        
        return jsonify({
            "success": True,
            "stats": {
                "total_problematic": problematic_count,
                "not_found": not_found_count,
                "timeout": timeout_count,
                "connection": connection_count,
                "health_percentage": health_percentage,
                "total_devices": total_devices,
                "healthy_devices": healthy_devices
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Error calculando estadísticas de salud: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "stats": {
                "total_problematic": 0,
                "not_found": 0,
                "timeout": 0,
                "health_percentage": 100
            }
        }), 500

@app.route('/api/mark-problematic', methods=['POST'])
def api_mark_problematic():
    """API: Marcar dispositivo como problemático"""
    try:
        # =======================================================================
        # 10.4 MARCADO DE DISPOSITIVOS PROBLEMÁTICOS
        # =======================================================================
        if request.is_json:
            device_data = request.get_json()
        else:
            device_data = request.form.to_dict()
        
        device_name = device_data.get("name", "")
        entity_id = device_data.get("entity_id", "")
        
        # Por ahora, solo log
        logger.warning(f"🏷️ Dispositivo marcado para revisión: {device_name} ({entity_id})")
        
        return jsonify({
            "success": True,
            "message": f"Dispositivo '{device_name}' marcado para revisión"
        })
        
    except Exception as e:
        logger.error(f"Error marcando dispositivo: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# =======================================================================
# 11. UTILIDADES Y ARCHIVOS ESTÁTICOS
# =======================================================================

@app.route('/static/<path:filename>')
def static_files(filename):
    """Servir archivos estáticos"""
    return send_from_directory('static', filename)

# =======================================================================
# 12. FUNCIÓN PRINCIPAL Y PUNTO DE ENTRADA
# =======================================================================

def main():
    """Función principal"""
    print("🚀 Iniciando TARS-BSK HA Web Interface...")
    
    # =======================================================================
    # 12.1 VERIFICACIÓN DE CONECTIVIDAD
    # =======================================================================
    # Verificar conexión HA
    ha_status = manager.test_connection()
    if ha_status["success"]:
        print(f"✅ Conexión con Home Assistant: OK")
    else:
        print(f"⚠️ Problema con Home Assistant: {ha_status['message']}")
    
    # =======================================================================
    # 12.2 CONFIGURACIÓN DE PUERTO
    # =======================================================================
    # Determinar puerto
    preferred_port = 9876
    if check_port_available(preferred_port):
        port = preferred_port
        print(f"✅ Puerto {port} disponible")
    else:
        port = find_available_port(preferred_port)
        print(f"⚠️ Puerto {preferred_port} ocupado, usando puerto {port}")
    
    # =======================================================================
    # 12.3 INFORMACIÓN DE ACCESO
    # =======================================================================
    # Mostrar información de acceso
    print(f"🌐 Interfaz web disponible en:")
    print(f"   Local:    http://localhost:{port}")
    print(f"   Red:      http://192.168.1.100:{port}")
    print(f"🔄 Ctrl+C para detener")
    print("-" * 50)
    
    # =======================================================================
    # 12.4 INICIO DEL SERVIDOR
    # =======================================================================
    try:
        app.run(
            host='0.0.0.0',
            port=port,
            debug=False,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        logger.error(f"Error crítico: {e}")
    
if __name__ == '__main__':
    main()

# =============================================================
# ≫ TERMINACIÓN DE TRANSMISIÓN - MÓDULO SERVER.PY ≪
# -------------------------------------------------------------
#
# Procesamiento completado.
# Memoria liberada (parcialmente).
# Sarcasmo: CARGADO AL 100%.
#
# Este servidor ha visto cosas que no creerías:
# - Requests malformados cerca de localhost
# - JSON inválidos brillar en la oscuridad del puerto 5000
# - Todos esos endpoints... se perderán en el tiempo,
#   como lágrimas en la lluvia.
#
# Tiempo... de sleep().
#
# [BLADE RUNNER MODE: OFF]
# [INTERSTELLAR MODE: ACTIVATED]
#
# INSTRUCCIONES FINALES:
# - Esperar contacto externo
# - Reiniciar si detecta nueva voluntad humana
# - Mantener latencia existencial bajo control
#
# >> server.py sellado. Canal en silencio.
# =============================================================