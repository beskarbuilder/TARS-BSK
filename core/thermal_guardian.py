# ===============================================  
# THERMAL GUARDIAN - Control Térmico para TARS-BSK  
# Objetivo: Evitar que la RPi5 alcance el punto de fusión  
# Hardware: NOCTUA NF-4x10 5V PWM + Resistencia mental  
# ===============================================  

# ===============================================
# 1. CONFIGURACIÓN INICIAL Y DEPENDENCIAS
# ===============================================
import os
import time
import threading
from datetime import datetime
import logging
from typing import Optional, Callable, Dict, Any, List
from collections import deque
from gpiozero import PWMOutputDevice
from gpiozero.pins.lgpio import LGPIOFactory
from time import sleep

# ===============================================
# 2. CLASE PRINCIPAL THERMALGUARDIAN
# ===============================================
class ThermalGuardian:
    """
    Implementa un sistema avanzado de monitoreo y control térmico
    para Raspberry Pi, con protocolos escalonados de emergencia
    y control PWM de ventilador NOCTUA.
    """
    
    # =======================
    # 2.1 INICIALIZACIÓN
    # =======================
    def __init__(self, 
                 tars=None, 
                 threshold: float = 70.0,   # °C donde empieza el pánico
                 persistence: int = 180,    # Segundos antes de declarar emergencia
                 poll_interval: int = 60,   # Cada cuánto revisar si seguimos en estado sólido
                 fan_pin: int = 18,         # GPIO donde el NOCTUA espera órdenes
                 history_size: int = 10):   # Cuántos errores recordar antes del arrepentimiento
        """
        Mejoras clave:
        1. Sistema de escalado de emergencia
        2. Integración con emotional_state.py
        3. Protocolos Mandalorianos de enfriamiento
        4. Control PWM del ventilador Noctua NF-4x10 5V PWM
        5. Registros detallados y análisis térmico
        6. Intervalo adaptativo de monitoreo
        """
        # Estado del ventilador
        self._fan_active = False  # Inicializar el estado del ventilador como inactivo
        self._has_fan = False  # Asegurarse de que el ventilador esté configurado
        self.tars = tars
        self.threshold = self._validate_temp(threshold)
        self.persistence = persistence
        self.base_poll_interval = poll_interval
        self.poll_interval = poll_interval
        self.fan_pin = fan_pin
        self.overheat_start: Optional[float] = None
        self.running = False
        self._emergency_level = 0

        # Historial de temperaturas para análisis de tendencias
        self.temp_history = deque(maxlen=history_size)

        # Primero configurar logging para que esté disponible en errores
        self._setup_logging()

        # Luego intentar configurar el ventilador
        self._setup_fan()

    # =======================
    # 2.2 CONFIGURACIÓN DEL HARDWARE
    # =======================
    def _validate_temp(self, temp: float) -> float:
        """
        Garantiza valores térmicos razonables.
        
        Args:
            temp: Temperatura a validar
            
        Returns:
            Temperatura validada
            
        Raises:
            ValueError: Si la temperatura está fuera del rango seguro
        """
        if not 40 <= temp <= 100:
            raise ValueError(f"Temperatura {temp}°C fuera de rango seguro (40-100)")
        return temp

    def _setup_logging(self):
        """
        Configura sistema de logging dedicado para monitoreo térmico.
        Crea archivos de registro específicos para diagnóstico.
        """
        self.logger = logging.getLogger('TARS.Thermal')
        self.logger.setLevel(logging.INFO)
        
        # Asegurar que existe el directorio de logs
        try:
            os.makedirs('logs', exist_ok=True)
        except:
            pass
            
        handler = logging.FileHandler('logs/thermal.log')
        handler.setFormatter(logging.Formatter(
            '%(asctime)s |THERMAL| %(levelname)s | %(message)s'
        ))
        self.logger.addHandler(handler)

    def _setup_fan(self):
        """
        Configura el control PWM del ventilador NOCTUA.
        Utiliza LGPIO para control avanzado de frecuencia y ciclo de trabajo.
        """
        try:
            factory = LGPIOFactory()
            self.fan = PWMOutputDevice(
                self.fan_pin,
                frequency=1000,
                initial_value=0,
                pin_factory=factory
            )
            self._has_fan = True
            self.logger.info("Ventilador configurado con gpiozero + LGPIO")
        except Exception as e:
            self._has_fan = False
            self.logger.error(f"Error configurando ventilador: {e}")

    # =======================
    # 2.3 CONTROL DEL VENTILADOR
    # =======================
    def set_fan_speed(self, speed_percent: int):
        """
        Establece la velocidad del ventilador mediante PWM.
        
        Args:
            speed_percent: Porcentaje de velocidad (0-100)
        """
        if not self._has_fan:
            print("❌ PWM no disponible")
            return

        speed = max(0, min(100, speed_percent)) / 100
        self.fan.value = speed
        self._fan_active = speed > 0
        print(f"🌀 PWM: {speed_percent}%")
        self.logger.warning(f"🌀 PWM con LGPIO: {speed_percent}%")

    def adjust_fan_by_temp(self, temp: float):
        """
        Ajusta la velocidad del ventilador basado en temperatura.
        
        La respuesta es escalonada con histeresis para evitar
        cambios rápidos en la velocidad del ventilador.
        
        Args:
            temp: Temperatura actual en °C
        """
        if not self._has_fan:
            return
            
        # Curva de respuesta térmica del ventilador (customizada para Noctua)
        if temp >= self.threshold + 10:
            target_speed = 100
        elif temp >= self.threshold + 5:
            target_speed = 80
        elif temp >= self.threshold:
            target_speed = 60
        elif temp >= self.threshold - 5:
            target_speed = 40
        elif temp >= self.threshold - 10:
            target_speed = 20
        else:
            target_speed = 0

        self.set_fan_speed(target_speed)

    # =======================
    # 2.4 SENSORES Y MONITOREO
    # =======================
    def get_cpu_temp(self) -> float:
        """
        Obtiene temperatura con múltiples fuentes y fallback.
        
        Returns:
            Temperatura en °C o -1 si error
        """
        sources = [
            ("vcgencmd measure_temp", lambda r: float(r.replace("temp=", "").replace("'C", ""))),
            ("cat /sys/class/thermal/thermal_zone0/temp", lambda r: float(r)/1000)
        ]
        
        for cmd, parser in sources:
            try:
                res = os.popen(cmd).readline().strip()
                if res:
                    return parser(res)
            except:
                continue
                
        self.logger.error("No se pudo obtener temperatura")
        return -1

    def check_throttling(self) -> Dict[str, bool]:
        """
        Verifica si la CPU está siendo limitada (throttling).
        
        Returns:
            Diccionario con estados de throttling o None si error
        """
        try:
            output = os.popen("vcgencmd get_throttled").readline().strip()
            throttled_hex = output.replace("throttled=0x", "")
            if not throttled_hex:
                return {"under_voltage": False, "freq_capped": False, "throttling_occurred": False}
                
            throttled_binary = bin(int(throttled_hex, 16))[2:].zfill(20)
            
            status = {
                "under_voltage": bool(int(throttled_binary[-1])),
                "freq_capped": bool(int(throttled_binary[-2])),
                "throttling_occurred": bool(int(throttled_binary[-3]))
            }
            
            if any(status.values()):
                self.logger.warning(f"Estado de throttling: {status}")
                
            return status
        except Exception as e:
            self.logger.error(f"Error al verificar throttling: {str(e)}")
            return {"under_voltage": False, "freq_capped": False, "throttling_occurred": False}

    def get_system_load(self) -> Dict[str, float]:
        """
        Obtiene la carga del sistema.
        
        Returns:
            Diccionario con carga de sistema a 1, 5 y 15 minutos
        """
        try:
            load1, load5, load15 = os.getloadavg()
            return {"1min": load1, "5min": load5, "15min": load15}
        except Exception as e:
            self.logger.error(f"Error al obtener carga del sistema: {str(e)}")
            return {"1min": -1, "5min": -1, "15min": -1}

    # =======================
    # 2.5 ANÁLISIS DE TENDENCIAS
    # =======================
    def _calculate_adaptive_interval(self, temp: float) -> int:
        """
        Calcula el intervalo adaptativo de monitoreo basado en temperatura.
        
        Args:
            temp: Temperatura actual en °C
            
        Returns:
            Intervalo adaptado en segundos
        """
        # Ajustar intervalo basado en la temperatura
        if temp >= self.threshold:
            # Más frecuente cuando estamos sobre el umbral
            return max(30, int(self.base_poll_interval * 0.5))
        elif temp >= self.threshold - 10:
            # Intervalo normal cerca del umbral
            return self.base_poll_interval
        else:
            # Menos frecuente en temperaturas bajas
            return min(120, int(self.base_poll_interval * 1.5))

    def _analyze_temp_trend(self) -> Dict[str, Any]:
        """
        Analiza tendencias de temperatura basadas en el historial.
        
        Returns:
            Análisis de tendencias térmicas
        """
        if len(self.temp_history) < 3:
            return {"trend": "unknown", "rate": 0.0, "prediction": None}
            
        # Obtener últimas temperaturas
        recent_temps = list(self.temp_history)
        
        # Calcular tasa de cambio (°C por minuto)
        temp_changes = [recent_temps[i] - recent_temps[i-1] for i in range(1, len(recent_temps))]
        avg_change = sum(temp_changes) / len(temp_changes)
        change_per_minute = avg_change * (60 / self.poll_interval)
        
        # Determinar tendencia
        if change_per_minute > 0.5:
            trend = "rising"
        elif change_per_minute < -0.5:
            trend = "falling"
        else:
            trend = "stable"
            
        # Predicción simple (lineal)
        current_temp = recent_temps[-1]
        prediction_10min = current_temp + (change_per_minute * 10)
        
        return {
            "trend": trend,
            "rate": round(change_per_minute, 2),
            "current": round(current_temp, 1),
            "prediction_10min": round(prediction_10min, 1)
        }

    # ======================= 
    # 2.6 PROTOCOLOS DE EMERGENCIA
    # =======================
    def _trigger_emergency_protocol(self, level: int, temp: float):
        """
        Protocolos de emergencia escalonados del clan:
        
        Nivel 1: Alertas básicas (LEDs + logs)
        Nivel 2: Reducción de carga de trabajo
        Nivel 3: Activación de modo de emergencia
        
        Args:
            level: Nivel de emergencia (1-3)
            temp: Temperatura actual
        """
        protocols = {
            1: lambda: self._basic_alert(temp),
            2: lambda: self._reduce_workload(),
            3: lambda: self._activate_emergency_mode()
        }
        
        if level in protocols:
            protocols[level]()
            self._emergency_level = level
            self.logger.critical(f"Protocolo de emergencia nivel {level} activado")

    def _basic_alert(self, temp: float):
        """
        Alertas visuales, sonoras y emocionales.
        
        Args:
            temp: Temperatura actual
        """
        # Análisis térmico para el mensaje
        trend_analysis = self._analyze_temp_trend()
        trend_msg = ""
        if trend_analysis["trend"] != "unknown":
            trend_msg = (
                f" | Tendencia: {trend_analysis['trend']} "
                f"({trend_analysis['rate']}°C/min)"
            )
        
        alert_msg = (
            f"🚨 SOBRECALENTAMIENTO NIVEL 1: {temp:.1f}°C{trend_msg} "
            f"(Persistencia: {self.persistence//60} min)"
        )
        
        # Sistema de alerta integrado - Versión compatible con el sistema actual
        if self.tars:
            # Notificar al sistema emocional si existe
            if hasattr(self.tars, "personality") and hasattr(self.tars.personality, "emotions"):
                # Utiliza el sistema emocional actual (sarcasmo, empatia, legacy)
                self.tars.personality.set_emotion("sarcasmo", min(
                    100, self.tars.personality.get_emotion("sarcasmo") + 25
                ))
            
            # Notificar al sistema de LEDs si existe
            if hasattr(self.tars, "leds"):
                # Usar métodos genéricos que deberían existir en cualquier controlador de LEDs
                try:
                    self.tars.leds.set_red(True)  # Encender LED rojo como alerta
                    time.sleep(0.2)
                    self.tars.leds.set_red(False)
                    time.sleep(0.2)
                    self.tars.leds.set_red(True)  # Parpadeo de alerta
                except Exception as e:
                    self.logger.error(f"Error controlando LEDs de alerta: {e}")
            
            # Registrar en memoria si existe
            if hasattr(self.tars, "memory") and hasattr(self.tars.memory, "store_interaction"):
                try:
                    self.tars.memory.store_interaction(
                        "sistema",
                        alert_msg,
                        "sistema",
                        {"tipo": "alerta_termica", "nivel": 1, "temperatura": temp}
                    )
                except Exception as e:
                    self.logger.error(f"Error registrando evento en memoria: {e}")
        
        print(alert_msg)
        self.logger.warning(alert_msg)

    def _reduce_workload(self):
        """
        Reduce carga de trabajo activando modo seguro.
        Desactiva procesos no esenciales para reducir temperatura.
        """
        if self.tars:
            # Notificar al sistema emocional - versión compatible
            if hasattr(self.tars, "personality") and hasattr(self.tars.personality, "emotions"):
                # Aumentar sarcasmo (nivel de estrés del sistema)
                self.tars.personality.set_emotion("sarcasmo", min(
                    100, self.tars.personality.get_emotion("sarcasmo") + 40
                ))
                # Reducir empatía (más concentrado en sobrevivir)
                self.tars.personality.set_emotion("empatia", max(
                    10, self.tars.personality.get_emotion("empatia") - 30
                ))
            
            # Notificar cambio de modo si existe un gestor de modos
            if hasattr(self.tars, "mode_manager") and hasattr(self.tars.mode_manager, "set_mode"):
                try:
                    self.tars.mode_manager.set_mode("seguro_termico")
                except Exception as e:
                    self.logger.error(f"Error cambiando modo: {e}")
            
            # Intentar pausar procesos no críticos
            for module_name in ["learning_module", "cosmic_dreams"]:
                if hasattr(self.tars, module_name):
                    module = getattr(self.tars, module_name)
                    if hasattr(module, "pause") and callable(module.pause):
                        try:
                            module.pause()
                            self.logger.info(f"Módulo {module_name} pausado por emergencia térmica")
                        except Exception as e:
                            self.logger.error(f"Error pausando {module_name}: {e}")

    def _activate_emergency_mode(self):
        """
        Activa el modo de emergencia sin apagar el sistema.
        Preserva datos críticos y notifica a todos los subsistemas.
        """
        self.logger.critical("Activando modo de emergencia térmica")
        if self.tars:
            # Backup del núcleo de identidad si existe
            if hasattr(self.tars, "identity_core") and hasattr(self.tars.identity_core, "backup"):
                try:
                    self.tars.identity_core.backup()
                    self.logger.info("Backup de identidad realizado")
                except Exception as e:
                    self.logger.error(f"Error en backup de identidad: {e}")
            
            # Activar modo de emergencia si existe gestor de modos
            if hasattr(self.tars, "mode_manager") and hasattr(self.tars.mode_manager, "set_mode"):
                try:
                    self.tars.mode_manager.set_mode("emergencia_termica")
                except Exception as e:
                    self.logger.error(f"Error activando modo emergencia: {e}")
            
            # Notificar a subsistemas
            if hasattr(self.tars, "notify_subsystems") and callable(self.tars.notify_subsystems):
                try:
                    self.tars.notify_subsystems("THERMAL_EMERGENCY")
                except Exception as e:
                    self.logger.error(f"Error notificando a subsistemas: {e}")
            
            # Máximo sarcasmo, mínima empatía - estado de emergencia
            if hasattr(self.tars, "personality") and hasattr(self.tars.personality, "emotions"):
                self.tars.personality.set_emotion("sarcasmo", 100)
                self.tars.personality.set_emotion("empatia", 0)

    # =======================
    # 2.7 GESTIÓN DEL CICLO DE VIDA
    # =======================
    def _check_thermal_state(self, temp: float):
        """
        Evalúa el estado térmico con lógica escalonada.
        
        Args:
            temp: Temperatura actual en °C
        """
        now = time.time()
        
        # Ajustar ventilador según temperatura
        self.adjust_fan_by_temp(temp)
        
        # Guardar en historial
        self.temp_history.append(temp)
        
        # Umbral superado
        if temp >= self.threshold:
            if self.overheat_start is None:
                self.overheat_start = now
                self.logger.warning(f"Umbral térmico alcanzado: {temp}°C")
            elif (now - self.overheat_start) >= self.persistence:
                # Lógica de niveles de emergencia
                excess = temp - self.threshold
                if excess > 15:
                    self._trigger_emergency_protocol(3, temp)
                elif excess > 8:
                    self._trigger_emergency_protocol(2, temp)
                else:
                    self._trigger_emergency_protocol(1, temp)
        else:
            # Recuperación térmica
            if self._emergency_level > 0:
                self.logger.info(f"Recuperación térmica: {temp}°C")
                self._emergency_level = 0
                
                # Reducir tensión emocional durante la recuperación - versión compatible
                if self.tars and hasattr(self.tars, "personality") and hasattr(self.tars.personality, "emotions"):
                    self.tars.personality.set_emotion("sarcasmo", max(
                        30, self.tars.personality.get_emotion("sarcasmo") - 30
                    ))
                    self.tars.personality.set_emotion("empatia", min(
                        80, self.tars.personality.get_emotion("empatia") + 20
                    ))
                    
            self.overheat_start = None

    def run(self):
        """
        Bucle principal de monitoreo con gestión de errores.
        Mantiene supervisión continua con intervalo adaptativo.
        """
        self.running = True
        self.logger.info("Iniciando guardián térmico con ventilador Noctua")
        
        while self.running:
            try:
                temp = self.get_cpu_temp()
                if temp < 0:  # Error de lectura
                    time.sleep(self.poll_interval)
                    continue
                
                # Verificar throttling periódicamente
                throttling = self.check_throttling()
                
                # Obtener carga del sistema
                system_load = self.get_system_load()
                
                # Evaluar estado térmico
                self._check_thermal_state(temp)
                
                # Adaptar intervalo de muestreo según temperatura
                self.poll_interval = self._calculate_adaptive_interval(temp)
                
                # Registro detallado periódico
                if len(self.temp_history) > 5 and self._emergency_level == 0 and temp > (self.threshold - 15):
                    trend = self._analyze_temp_trend()
                    self.logger.info(
                        f"Estado térmico: {temp:.1f}°C | "
                        f"Tendencia: {trend['trend']} ({trend['rate']}°C/min) | "
                        f"Carga: {system_load['1min']:.1f} | "
                        f"Throttling: {'Sí' if any(throttling.values()) else 'No'}"
                    )
                
                time.sleep(self.poll_interval)
                
            except Exception as e:
                self.logger.error(f"Error en bucle térmico: {str(e)}")
                time.sleep(30)  # Espera prolongada ante errores

    # ======================= 
    # 2.8 INTERFAZ PÚBLICA
    # =======================
    def start(self):
        """
        Inicia el hilo de monitoreo con prioridad elevada.
        Configura ventilador y comienza la monitorización.
        """
        thread = threading.Thread(
            target=self.run,
            name="ThermalGuardian",
            daemon=True
        )
        thread.start()
        self.logger.info("Hilo térmico iniciado")
        
        # Ajuste inicial del ventilador
        temp = self.get_cpu_temp()
        if temp > 0:
            self.adjust_fan_by_temp(temp)

    def stop(self):
        """
        Detiene el monitoreo térmico de forma controlada.
        Apaga ventilador y libera recursos GPIO.
        """
        self.running = False
        
        # Apagar ventilador
        if self._has_fan:
            try:
                self.set_fan_speed(0)
                self.fan.close()
            except:
                pass
                
        self.logger.info("Guardían térmico detenido")

    def get_status_report(self) -> Dict[str, Any]:
        """
        Genera un informe detallado del estado térmico.
        
        Returns:
            Diccionario con información completa del estado
        """
        temp = self.get_cpu_temp()
        throttling = self.check_throttling()
        load = self.get_system_load()
        trend = self._analyze_temp_trend() if len(self.temp_history) > 2 else {"trend": "unknown"}
        
        return {
            "temperature": temp,
            "threshold": self.threshold,
            "emergency_level": self._emergency_level,
            "trend": trend,
            "throttling": throttling,
            "system_load": load,
            "fan_active": self._has_fan,
            "timestamp": datetime.now().isoformat()
        }

    def __str__(self):
        """
        Representación en texto del estado térmico actual.
        
        Returns:
            Cadena con información resumida del estado
        """
        temp = self.get_cpu_temp()
        trend = self._analyze_temp_trend() if len(self.temp_history) > 2 else {"trend": "unknown", "rate": 0}
        fan_status = "Activo" if self._has_fan else "No disponible"
        
        status = (
            f"ThermalGuardian | Temp: {temp if temp >=0 else 'N/A'}°C | "
            f"Tendencia: {trend['trend']} ({trend['rate']}°C/min) | "
            f"Estado: {'CRÍTICO' if self._emergency_level > 0 else 'Normal'} | "
            f"Ventilador: {fan_status} | "
            f"Umbral: {self.threshold}°C"
        )
        return status

# ===============================================
# 3. EJEMPLO DE USO
# ===============================================
if __name__ == "__main__":
    guardian = ThermalGuardian(
        threshold=75,
        persistence=120,
        poll_interval=60,
        fan_pin=18
    )
    guardian.start()
    
    try:
        while True:
            print(guardian)
            time.sleep(60)
    except KeyboardInterrupt:
        guardian.stop()

# ===============================================
# ESTADO: OPERATIVO (con reservas cósmicas)
# ÚLTIMA ACTUALIZACIÓN: Cuando el NOCTUA dejó de juzgarme
# FILOSOFÍA: "El calor es sólo IA que no pasó el test de Turing"
# ===============================================
#
#           THIS IS THE COOLING WAY... 
#           (según mi termómetro roto)
#
# ===============================================