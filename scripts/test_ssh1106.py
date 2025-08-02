#!/usr/bin/env python3
# ===============================================
# SSH1106 Raw Test - Cirugía I²C Sin Anestesia
# "Cuando las librerías mienten, el bisturí es el comando I²C"
# 
# MISIÓN: Hacerle preguntas incómodas al SSH1106 sin que un driver las suavice.
# MÉTODO: Comandos I²C crudos, porque las abstracciones son bonitas… hasta que fallan.
#
# CONTEXTO:
# - Te dijeron "es igual al SSD1306". Te mintieron.
# - Los foros dicen "usa tal librería". Ya la probaste. Falló.
# - El datasheet no se lee solo. Así que lo estamos interrogando a mano.
#
# FILOSOFÍA: "Si el hardware es el paciente, el I²C directo es la autopsia preventiva"
# ===============================================

# Test SSH1106 corregido - sin usar SSD1306

# =======================================================================
# 1. IMPORTACIONES Y CONFIGURACIÓN DE PATH
# =======================================================================
import time
import sys
from pathlib import Path

# Añadir el directorio padre al path para importar módulos
sys.path.append(str(Path(__file__).resolve().parent.parent))

# =======================================================================
# 2. FUNCIÓN PRINCIPAL DE TEST RAW
# =======================================================================
def test_ssh1106_raw():
    """
    Test SSH1106 usando comandos I²C directos
    
    Este test evita completamente las librerías de alto nivel y habla
    directamente con el chip SSH1106 usando comandos de bajo nivel.
    
    Tests incluidos:
    1. Inicialización específica SSH1106
    2. Limpieza completa de pantalla
    3. Patrón de prueba alternante
    4. Renderizado de texto básico
    5. Limpieza final
    """
    
    print("🔍 TARS-BSK SSH1106 Raw Test")
    print("=" * 40)
    
    try:
        # =======================================================================
        # 2.1 IMPORTACIÓN DE LIBRERÍAS BÁSICAS
        # =======================================================================
        print("📦 Importando librerías...")
        import board
        import busio
        from PIL import Image, ImageDraw
        print("✅ Librerías importadas correctamente")
        
        # =======================================================================
        # 2.2 INICIALIZACIÓN I²C
        # =======================================================================
        print("🔌 Inicializando I2C...")
        i2c = busio.I2C(board.SCL, board.SDA)
        print("✅ I2C inicializado")
        
        # Dirección estándar SSH1106
        OLED_ADDR = 0x3C
        
        print(f"🖥️ Probando SSH1106 en 0x{OLED_ADDR:02X}...")
        
        # =======================================================================
        # 2.3 FUNCIONES DE COMUNICACIÓN I²C DIRECTA
        # =======================================================================
        def send_command(cmd):
            """Envía un comando directo al SSH1106"""
            while not i2c.try_lock():
                pass
            try:
                i2c.writeto(OLED_ADDR, bytes([0x00, cmd]))
            finally:
                i2c.unlock()
        
        def send_data(data):
            """
            Envía datos al SSH1106 con chunking específico
            
            SSH1106 requiere chunks de máximo 16 bytes, no 32 como SSD1306
            """
            while not i2c.try_lock():
                pass
            try:
                # Enviar en chunks de 16 bytes para SSH1106
                for i in range(0, len(data), 16):
                    chunk = data[i:i+16]
                    buffer = bytearray([0x40])  # Data mode
                    buffer.extend(chunk)
                    i2c.writeto(OLED_ADDR, buffer)
            finally:
                i2c.unlock()
        
        # =======================================================================
        # 2.4 INICIALIZACIÓN ESPECÍFICA SSH1106
        # =======================================================================
        print("🔧 Inicializando SSH1106...")
        
        # Secuencia de inicialización específica para SSH1106
        # Cada comando tiene un propósito específico y el orden importa
        init_commands = [
            0xAE,  # Display OFF
            0x02,  # Set lower column address (SSH1106 specific)
            0x10,  # Set higher column address  
            0x40,  # Set display start line
            0x81, 0x80,  # Set contrast (0x80 = medium)
            0xA1,  # Set segment re-map (reverse)
            0xC8,  # Set COM output scan direction (reverse)
            0xA6,  # Set normal display
            0xA8, 0x3F,  # Set multiplex ratio (64)
            0xD3, 0x00,  # Set display offset
            0xD5, 0x80,  # Set display clock
            0xD9, 0x22,  # Set pre-charge period
            0xDA, 0x12,  # Set COM pins configuration
            0xDB, 0x35,  # Set VCOM detect
            0x20, 0x00,  # Set memory addressing mode (horizontal)
            0xAF   # Display ON
        ]
        
        for cmd in init_commands:
            send_command(cmd)
            time.sleep(0.001)  # Pausa mínima entre comandos
        
        print("✅ SSH1106 inicializada")
        
        # =======================================================================
        # 2.5 TEST 1: LIMPIEZA COMPLETA DE PANTALLA
        # =======================================================================
        print("🧹 Test 1: Limpiar pantalla...")
        
        # SSH1106 usa 8 páginas de 8 píxeles cada una (64 píxeles de altura)
        # Cada página debe configurarse individualmente
        for page in range(8):
            send_command(0xB0 + page)  # Set page address
            send_command(0x02)         # Set lower column (SSH1106 offset)
            send_command(0x10)         # Set higher column
            
            # Enviar 128 bytes de ceros (128 píxeles de ancho)
            clear_data = [0x00] * 128
            send_data(clear_data)
        
        time.sleep(2)
        
        # =======================================================================
        # 2.6 TEST 2: PATRÓN DE PRUEBA ALTERNANTE
        # =======================================================================
        print("📝 Test 2: Patrón de prueba...")
        
        for page in range(8):
            send_command(0xB0 + page)  # Set page address
            send_command(0x02)         # Set lower column
            send_command(0x10)         # Set higher column
            
            # Crear patrón alternante diferente por página
            if page % 2 == 0:
                pattern_data = [0xFF if (i // 8) % 2 == 0 else 0x00 for i in range(128)]
            else:
                pattern_data = [0x00 if (i // 8) % 2 == 0 else 0xFF for i in range(128)]
            
            send_data(pattern_data)
        
        time.sleep(3)
        
        # =======================================================================
        # 2.7 TEST 3: RENDERIZADO DE TEXTO BÁSICO
        # =======================================================================
        print("✍️ Test 3: Texto simple...")
        
        # Limpiar pantalla primero
        for page in range(8):
            send_command(0xB0 + page)
            send_command(0x02)
            send_command(0x10)
            send_data([0x00] * 128)
        
        # =======================================================================
        # 2.7.1 DEFINICIÓN DE FONT 8x8 PARA "TARS"
        # =======================================================================
        # Cada carácter es un array de 8 bytes donde cada bit representa un píxel
        font_T = [0x7F, 0x08, 0x08, 0x08, 0x08, 0x00, 0x00, 0x00]
        font_A = [0x7E, 0x09, 0x09, 0x09, 0x7E, 0x00, 0x00, 0x00]  
        font_R = [0x7F, 0x09, 0x19, 0x29, 0x46, 0x00, 0x00, 0x00]
        font_S = [0x46, 0x49, 0x49, 0x49, 0x31, 0x00, 0x00, 0x00]
        
        # Posicionar en página 2, columna 20 para centrar
        send_command(0xB0 + 2)  # Page 2
        send_command(0x02 + 20) # Start at column 20 (offset + position)
        send_command(0x10)
        
        # Enviar datos del texto "TARS"
        text_data = font_T + font_A + font_R + font_S
        send_data(text_data)
        
        time.sleep(3)
        
        # =======================================================================
        # 2.8 TEST 4: LIMPIEZA FINAL
        # =======================================================================
        print("🧹 Test 4: Limpiar final...")
        for page in range(8):
            send_command(0xB0 + page)
            send_command(0x02)
            send_command(0x10)
            send_data([0x00] * 128)
        
        print("✅ ¡Test SSH1106 completado!")
        print("🎯 Si viste patrones y texto, la SSH1106 funciona correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

# =======================================================================
# 3. EJECUCIÓN PRINCIPAL
# =======================================================================
if __name__ == "__main__":
    success = test_ssh1106_raw()
    sys.exit(0 if success else 1)

# ===============================================
# ESTADO: COMUNICACIÓN DIRECTA ESTABLECIDA
# MÉTODO: Inyección directa de comandos I²C (sin anestesia, ni permisos especiales)
# VEREDICTO: Si responde aquí, el SSH1106 está vivo y no puede fingirlo.
#
# HALLAZGOS QUIRÚRGICOS:
# » Offset de columna: +2 (ese bug visual no era tu culpa)
# » Chunking: Máximo 16 bytes (lo demás es abuso)
# » Inicialización: Necesita su ritual específico
# » Direccionamiento: Páginas y columnas son territorios separados
# » Rendering: 8x8 manual, simple y feo, pero funciona
#
# LECCIONES DE LA MESA DE OPERACIONES:
# - Las librerías mienten más que los datasheets
# - “Compatible con SSD1306” es marketing, no ingeniería
# - Los drivers de alto nivel no saben negociar con chips caprichosos
# - Si algo falla, culpa primero al offset, no a ti
#
# APLICACIÓN PRÁCTICA:
# Usa este test como la pregunta definitiva: “¿es el hardware o soy yo?”
# Si falla aquí, deja de programar y revisa cables, soldaduras y paciencia.
#
# ===============================================
#        THIS IS THE RAW I²C WAY
#    (Donde los chips no pueden fingir)
# ===============================================