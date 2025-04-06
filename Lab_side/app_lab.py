import RPi.GPIO as GPIO
import time

# Configuración de GPIO
GPIO.setmode(GPIO.BCM)  # Usar numeración BCM
GPIO.setwarnings(False)  # Desactivar advertencias

# Define el pin GPIO al que está conectado el servomotor
servo_pin = 18

# Configurar el pin como salida
GPIO.setup(servo_pin, GPIO.OUT)

# Crear un objeto PWM a 50Hz (estándar para servomotores)
servo = GPIO.PWM(servo_pin, 50)

# Iniciar PWM con ciclo de trabajo en 0
servo.start(0)

def set_angle(angle):
    """
    Convierte un ángulo (0-180) a un ciclo de trabajo (2-12)
    y mueve el servo a esa posición
    """
    if angle < 0:
        angle = 0
    elif angle > 180:
        angle = 180
        
    # Cálculo del ciclo de trabajo
    # La mayoría de los servos operan entre 2% (0°) y 12% (180°)
    duty_cycle = angle / 18.0 + 2
    
    servo.ChangeDutyCycle(duty_cycle)
    time.sleep(0.3)  # Dar tiempo al servo para alcanzar la posición

try:
    while True:
        # Ejemplo de movimiento: alternar entre diferentes posiciones
        angle = int(input("Introduce un ángulo entre 0 y 180: "))
        set_angle(angle)
        
except KeyboardInterrupt:
    print("\nPrograma interrumpido por el usuario")
    
finally:
    # Limpiar recursos
    servo.stop()
    GPIO.cleanup()
    print("Programa finalizado")