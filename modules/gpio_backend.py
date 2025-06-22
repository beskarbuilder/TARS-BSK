# ===============================================
# ADVERTENCIA FILOSÓFICA: Este módulo es funcionalmente competente (sí, sorprende)
# pero carece del drama existencial necesario para documentación completa.
#  
# Con desapego digital,  
# TARS-BSK declina responsabilidad emocional sobre su simplicidad.
# ===============================================

# GPIO BACKEND - Inicializa y gestiona salidas GPIO para LEDs y hardware TARS

# ===============================================
# 1. CONFIGURACIÓN INICIAL Y DEPENDENCIAS
# ===============================================
# gpio_backend.py
from gpiozero import Device

# ===============================================
# 2. CONFIGURACIÓN DEL BACKEND LGPIO
# ===============================================
try:
    # Intentar configurar LGPIO como backend preferido
    from gpiozero.pins.lgpio import LGPIOFactory
    Device.pin_factory = LGPIOFactory()
    print("✅ Backend GPIO configurado: lgpio")
except Exception as e:
    # Terminar el programa si LGPIO no está disponible
    # para evitar usar backends menos fiables automáticamente
    print(f"❌ Error al configurar LGPIO: {e}")
    raise SystemExit("❌ LGPIO no disponible. Aborta para evitar uso de backends no deseados.")

# ===============================================
# $ git log --format="%h %s" -1 [current_file]  
# deadbeef chore: Update [current_file] (survived again)  
# $ git blame --porcelain [current_file] | grep "exist"  
# fatal: No existential commits found
# ===============================================
    