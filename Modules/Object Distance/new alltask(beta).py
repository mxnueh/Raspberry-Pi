import RPi.GPIO as GPIO
from pyPS4Controller.controller import Controller
import time
from datetime import datetime
import smbus
from Rangefinder import getLidarData
import TrianguloMain 

n = [0,0,0,15]

# Aspiradora
Aspiradora = 24

# servo
servo1 = 11
servo2 = 12
servo3 = 17

# Configuracion GPIO
GPIO.setmode(GPIO.BCM)

# Aspiradora
GPIO.setup(Aspiradora, GPIO.OUT)
GPIO.output(Aspiradora, GPIO.LOW)

# servo
GPIO.setup(servo1, GPIO.OUT)
GPIO.setup(servo2, GPIO.OUT)

# Configuracion PWM
servoDriver1 = GPIO.PWM(servo1, 50)
servoDriver2 = GPIO.PWM(servo2, 50)



servoDriver1.start(7)
servoDriver2.start(7)


# Servo
global angle
angleS1 = 60
angleS2 = 90

#config servo range finder
GPIO.setmode(GPIO.BCM)
GPIO.setup(servo3, GPIO.OUT)
servo = GPIO.PWM(servo3, 50)
servo.start(7)  # Posición inicial en 90 grados

angle = 90  # Ángulo inicial
step = 25  # Incremento mínimo
hold_increment = 5 # Incremento sostenido
hold_time = 0.2  # Tiempo de espera para incremento progresivo


def aspirar():
    # Aspirar
    print("Aspirar")
    GPIO.output(Aspiradora, GPIO.HIGH)


def apagar():
    print("NoAspirar")
    GPIO.output(Aspiradora, GPIO.LOW)


def calcular_duty_cycle(angle):
    return 2 + (angle / 18)


def extender():
    print("Brazo extendido")
    servoDriver1.ChangeDutyCycle(calcular_duty_cycle(angleS1 - 60))


def retraer():
    print("Brazo retraido")
    servoDriver1.ChangeDutyCycle(calcular_duty_cycle(angleS1 + 60))


def contenedor1():
    print("Sensor hacia la izquierda")
    servoDriver2.ChangeDutyCycle(calcular_duty_cycle(angleS2 + 90))


def contenedor2():
    print("Sensor hacia la derecha")
    servoDriver2.ChangeDutyCycle(calcular_duty_cycle(angleS2 - 90))


class MyController(Controller):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


    # this event is only detected when connecting without ds4drv
    def on_playstation_button_press(self):
        aspirar()

    # this event is only detected when connecting without ds4drv
    def on_playstation_button_release(self):
        apagar()

    def on_right_arrow_press(self):
        extender()

    def on_left_arrow_press(self):
        retraer()

    def on_up_arrow_press(self):
        contenedor1()

    def on_down_arrow_press(self):
        contenedor2()
        
        
    def on_L2_press(self): #imprime la lista
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
