import RPi.GPIO as GPIO
import time

# Configuración
LED_PIN = 20  # Número GPIO (no el número físico del pin)

GPIO.setmode(GPIO.BCM)       # Usamos numeración BCM
GPIO.setup(LED_PIN, GPIO.OUT)

try:
    while True:
        GPIO.output(LED_PIN, GPIO.HIGH)  # Encender LED
        time.sleep(1)                    # Esperar 1 segundo
        GPIO.output(LED_PIN, GPIO.LOW)   # Apagar LED
        time.sleep(1)                    # Esperar 1 segundo

except KeyboardInterrupt:
    print("Programa terminado por el usuario")

finally:
    GPIO.cleanup()  # Limpiar configuración de GPIO
