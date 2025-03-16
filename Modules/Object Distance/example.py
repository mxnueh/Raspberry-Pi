import RPi.GPIO as GPIO
import time
import smbus
from pyPS4Controller.controller import Controller
from Rangefinder import getLidarData
import TrianguloMain 

n = [0,0,0,15]

# Configuración del servo
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.OUT)
servo = GPIO.PWM(11, 50)
servo.start(7)  # Posición inicial en 90 grados

def calcular_duty_cycle(angle):
    return 2 + (angle / 18)

angle = 90  # Ángulo inicial
step = 25  # Incremento mínimo
hold_increment = 5 # Incremento sostenido
hold_time = 0.2  # Tiempo de espera para incremento progresivo

class MyController(Controller):
    def __init__(self, **kwargs,):
        super().__init__(**kwargs)
    
    
    def on_left_arrow_press(self): #imprime la lista
        global angle
        print("Imprimer ista: ",n)
        angle = max(0, angle - step)
        servo.ChangeDutyCycle(calcular_duty_cycle(angle))
        
    def on_circle_press(self): #borra la lista completa
        global angle
        n = [0,0,0,0]
        print("Lista en cero: ",n)
        angle = max(0, angle - step)
        servo.ChangeDutyCycle(calcular_duty_cycle(angle))
        
    def on_triangle_press(self):
        address = 0x10 # Radar default address 0x10
        getLidarDataCmd = [0x5A,0x05,0x00,0x01,0x60] # Gets the distance value instruction	
        
        n[0] = getLidarData(address, getLidarDataCmd)
        print("Tomando distancia: ", n)
		
    def on_x_press(self):
        address = 0x10 # Radar default address 0x10
        getLidarDataCmd = [0x5A,0x05,0x00,0x01,0x60] # Gets the distance value instruction	
     
        n[2] = getLidarData(address, getLidarDataCmd)
        print("Tomando distancia: ", n)
        
    def on_L1_press(self):
        num = TrianguloMain.func(n[0],n[2],n[1],n[3])
        print(int(num))


try:
    controller = MyController(interface="/dev/input/js1", connecting_using_ds4drv=False)
    controller.listen()
except KeyboardInterrupt:
    print("\nPrograma interrumpido por el usuario.")
finally:
    servo.stop()
    GPIO.cleanup()
    print("Goodbye")
