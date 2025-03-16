import RPi.GPIO as GPIO
import time
from pyPS4Controller.controller import Controller

# Configuración del servo
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.OUT)
servo = GPIO.PWM(11, 50)
servo.start(7)  # Posición inicial en 90 grados

def calcular_duty_cycle(angle):
    return 2 + (angle / 18)

angle = 90  # Ángulo inicial
step = 1  # Incremento mínimo
hold_increment = 5 # Incremento sostenido
hold_time = 0.2  # Tiempo de espera para incremento progresivo

class MyController(Controller):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def on_up_arrow_press(self):
        global angle
        print("Servo en 0 grados")
        angle = 0
        servo.ChangeDutyCycle(calcular_duty_cycle(angle))
    
    def on_left_arrow_press(self):
        global angle
        print("on_left_arrow_press")
        angle = max(0, angle - step)
        servo.ChangeDutyCycle(calcular_duty_cycle(angle))
    
    def on_right_arrow_press(self):
        global angle
        angle = min(180, angle + step)
        print(f"El servo se movio {angle}")
        servo.ChangeDutyCycle(calcular_duty_cycle(angle))
    
    def on_left_arrow_release(self):
        getLidarData(address, getLidarDataCmd)
        time.sleep(0.1)
        print("on_left_arrow_release")
    
    def on_right_arrow_release(self):
        print("on_right_arrow_release")

try:
    controller = MyController(interface="/dev/input/js1", connecting_using_ds4drv=False)
    controller.listen()
except KeyboardInterrupt:
    print("\nPrograma interrumpido por el usuario.")
finally:
    servo.stop()
    GPIO.cleanup()
    print("Goodbye")
