import RPi.GPIO as GPIO
from pyPS4Controller.controller import Controller
import time
from datetime import datetime
import smbus
from Rangefinder import getLidarData
import TrianguloMain 

n = [0,0,0,0] 


saltos= [0.1,0.2,0.3,0.7,0.5,1,2,3,5,7,10,25]

#Pin Laser
laser = 5


# Aspiradora
Aspiradora = 24

# servo
servo1 = 11
servo2 = 12
servo3 = 17

# Configuracion GPIO
GPIO.setmode(GPIO.BCM)

#laser
GPIO.setup(laser, GPIO.OUT)
GPIO.output(laser, GPIO.LOW)

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

stpact = 11
angle = 90  # Ángulo inicial
step = saltos[stpact] # Incremento mínimo


#cambio de step
def changestpmas():
    if(stpact <11):
        stpact += 1
    step = [stpact]
    print(step)
def changestpmenos():
    if(stpact > 0):
        stpact -= 1
    step[stpact]
    print(step)

hold_time = 0.2  # Tiempo de espera para incremento progresivo


#Laser
def disparo():
    print("Laser encendido")
    GPIO.output(laser, GPIO.HIGH)
    
def no_disparo():
    print("Laser apagado")
    GPIO.output(laser, GPIO.LOW)

#Aspiradora
def aspirar():
    # Aspirar
    print("Aspirar")
    GPIO.output(Aspiradora, GPIO.HIGH)


def apagar():
    print("NoAspirar")
    GPIO.output(Aspiradora, GPIO.LOW)


def calcular_duty_cycle(angle):
    return 2 + (angle / 18)

# Brazo de aspiradora
def extender():
    print("Brazo extendido")
    servoDriver1.ChangeDutyCycle(calcular_duty_cycle(angleS1 - 60))


def retraer():
    print("Brazo retraido")
    servoDriver1.ChangeDutyCycle(calcular_duty_cycle(angleS1 + 60))

#Contenedores de la aspiradora
def contenedor1():
    print("Sensor hacia la izquierda")
    servoDriver2.ChangeDutyCycle(calcular_duty_cycle(angleS2 + 90))


def contenedor2():
    print("Sensor hacia la derecha")
    servoDriver2.ChangeDutyCycle(calcular_duty_cycle(angleS2 - 90))


class MyController(Controller):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    #Servo Rangefinder
    def on_up_arrow_press(self):
        global angle
        print("Servo en 0 grados")
        angle = 0
        servo.ChangeDutyCycle(calcular_duty_cycle(angle))
    
    def on_left_arrow_press(self):
        global angle
        print(f"El servo se movio {angle}")
        angle = max(0, angle - step)
        servo.ChangeDutyCycle(calcular_duty_cycle(angle))
    
    def on_right_arrow_press(self):
        global angle
        angle = min(180, angle + step)
        servo.ChangeDutyCycle(calcular_duty_cycle(angle))
        print(f"El servo se movio {angle}")
        
    def on_x_press(self):
        global angle
        angle -= 25
        servo.ChangeDutyCycle(calcular_duty_cycle(angle))
        print(f"El servo se ha movido {angle}")
    
    #Aspirardora
    def on_playstation_button_press(self):
        aspirar()

    def on_playstation_button_release(self):
        apagar()
        
    #Servo brazo de la aspiradora
    def on_share_press(self):
        print("Brazo en posicion normal")
        extender()
        
    def on_share_release(self):
        print("Proceso de servo completo")
        retraer()
        
    #Servo muestrario
    def on_options_press(self):
        contenedor1()
        
    def on_options_release(self):
        print("Cambio de contenedor completado")
        contenedor2()
    
    #Funcionalidades para el servo
    def on_L1_press(self):
        changestpmas

    def on_R1_press(self):
        changestpmenos

    
    def on_L3_press(self): #imprime la lista
        global angle
        print("Imprimer lista: ",n)
        angle = max(0, angle - step)
        servo.ChangeDutyCycle(calcular_duty_cycle(angle))
        
    def on_circle_press(self): #borra la lista completa
        global angle
        n[0],n[1],n[2],n[3]=0,0,0,0
        print("Lista en cero: ",n)
        angle = max(0, angle - step)
        servo.ChangeDutyCycle(calcular_duty_cycle(angle))
    
    #Funcionalidades Rangefinder
    def on_triangle_press(self):
        address = 0x10 # Radar default address 0x10
        getLidarDataCmd = [0x5A,0x05,0x00,0x01,0x60] # Gets the distance value instruction	
        
        n[0] = getLidarData(address, getLidarDataCmd)
        n[2] = getLidarData(address, getLidarDataCmd) #aqui va el angulo inicial delk se
        print("Tomando distancia: ", n)
		
    def on_square_press(self):
        address = 0x10 # Radar default address 0x10
        getLidarDataCmd = [0x5A,0x05,0x00,0x01,0x60] # Gets the distance value instruction	
     
        n[1] = getLidarData(address, getLidarDataCmd)
        n[3] = getLidarData(address, getLidarDataCmd) #aqui v a el angulo del servo
        print("Tomando distancia: ", n)
     #Resultado del calculo del servo
    def on_R1_press(self):
        num = TrianguloMain.func(n[0],n[2],n[1],n[3])
        print(int(num))
    
    #Disparo del laser
    def on_R3_press(self):
        disparo()
        
    def on_R3_release(self):
        no_disparo()

    

try:
    controller = MyController(interface="/dev/input/js0", connecting_using_ds4drv=False)
    controller.listen()
    GPIO.cleanup()

except KeyboardInterrupt:
    print("\nPrograma interrumpido por el usuario.")
    GPIO.cleanup()

finally:
    servo.stop()
    GPIO.cleanup()
    print("Goodbye")
