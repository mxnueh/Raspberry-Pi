import RPi.GPIO as GPIO
from pyPS4Controller.controller import Controller
import time
from datetime import datetime

ENA1 = 18  # Pin PWM para Motor A
ENA2 = 13  # Pin PWM para Motor A buscar otro
IN1 = 17  # Direccn Motor A
IN2 = 7

ENB1 = 19  # Pin P      WM para Motor B
ENB2 = 12  # Pin P      WM para Motor B buscar otro
IN3 = 8  # Direccin Motor B
IN4 = 25


# Configuracion GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(IN3, GPIO.OUT)
GPIO.setup(IN4, GPIO.OUT)
GPIO.setup(ENA, GPIO.OUT)
GPIO.setup(ENB, GPIO.OUT)

# Configuracion PWM
pwm_A = GPIO.PWM(ENA1, 100)  # Frecuencia 100 Hz
pwm_B = GPIO.PWM(ENB1, 100)
pwm_A2 = GPIO.PWM(ENA2, 100)  # Frecuencia 100 Hz
pwm_B2 = GPIO.PWM(ENB2, 100)

pwm_A.start(50)  # Velocidad inicial al 50%
pwm_B.start(50)

pwm_A2.start(50)  # Velocidad inicial al 50%
pwm_B2.start(50)


# Velocidad inicial
speed = 50

def set_speed(value):
    global speed
    speed = max(0, min(100, value))
    pwm_A.ChangeDutyCycle(speed)
    pwm_B.ChangeDutyCycle(speed)
    pwm_A2.ChangeDutyCycle(speed)
    pwm_B2.ChangeDutyCycle(speed)
    print(f"Velocidad ajustada a {speed}%")
    
    
def forward():
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    print("Moviendo hacia adelante")


def backward():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)
    print("Moviendo hacia atras")


def left():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    print("Girando a la izquierda")


def right():
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)
    print("Girando a la derecha")


def stop():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)
    print("Motores detenidos")
    
class MyController(Controller):
    def __init__(self, **kwargs):\
        super().__init__(**kwargs)

    def on_x_press(self):
        forward()

    def on_x_release(self):
        stop()

    def on_triangle_press(self):
        backward()

    def on_triangle_release(self):
        stop()

    def on_circle_press(self):
        right()

    def on_circle_release(self):
        stop()

    def on_square_press(self):
        left()

    def on_square_release(self):
        stop()
        
    
    def on_R1_press(self):
        if (speed < 80):
            set_speed(speed + 10)
        else:
            print("limite de 70")

    def on_L1_press(self):
        set_speed(speed - 10)


try:
    controller = MyController(
        interface="/dev/input/js0", connecting_using_ds4drv=False)
    controller.listen()

except KeyboardInterrupt:
    print("\nPrograma interrumpido por el usuario.")
