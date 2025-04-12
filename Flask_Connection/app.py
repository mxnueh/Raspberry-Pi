from flask import Flask, render_template
from flask_socketio import SocketIO
import threading
import time
from datetime import datetime
import RPi.GPIO as GPIO
from pyPS4Controller.controller import Controller
import smbus
from Rangefinder import getLidarData
import TrianguloMain

app = Flask(__name__)
socketio = SocketIO(app)

# Global variables to store controller data
controller_data = {
    "angle": 90,
    "step": 10,
    "stpact": 11,
    "n": [0, 0, 0, 0],
    "laser_state": False,
    "aspiradora_state": False,
    "servo_brazo_state": "retracted",
    "servo_contenedor_state": "contenedor1",
    "rangefinder_distance": 0,
    "triangulo_result": 0
}

# Configuración global
saltos = [0.1, 0.2, 0.3, 0.7, 0.5, 1, 2, 3, 5, 7, 10, 25]

# Pin definitions
laser = 5
Aspiradora = 24
servo1 = 11  # Servo Brazo
servo2 = 13  # Servo Aspiradora
servo3 = 17  # Servo Rangefinder

# GPIO setup function
def setup_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    # Laser
    GPIO.setup(laser, GPIO.OUT)
    GPIO.output(laser, GPIO.LOW)
    
    # Aspiradora
    GPIO.setup(Aspiradora, GPIO.OUT)
    GPIO.output(Aspiradora, GPIO.LOW)
    
    # Servos
    GPIO.setup(servo1, GPIO.OUT)
    GPIO.setup(servo2, GPIO.OUT)
    GPIO.setup(servo3, GPIO.OUT)
    
    return {
        'servo1': GPIO.PWM(servo1, 25),
        'servo2': GPIO.PWM(servo2, 50),
        'servo3': GPIO.PWM(servo3, 50)
    }

# Helper functions
def calcular_duty_cycle(angle):
    return 2 + (angle / 18)

def changestpmas():
    if controller_data["stpact"] < 11:
        controller_data["stpact"] += 1
        controller_data["step"] = saltos[controller_data["stpact"]]
    print("step: ", controller_data["step"])
    socketio.emit('update_controller', controller_data)
    
def changestpmenos():
    if controller_data["stpact"] > 0:
        controller_data["stpact"] -= 1
        controller_data["step"] = saltos[controller_data["stpact"]]
    print("step:", controller_data["step"])
    socketio.emit('update_controller', controller_data)

# Laser functions
def disparo(pwm_dict):
    print("Laser encendido")
    GPIO.output(laser, GPIO.HIGH)
    controller_data["laser_state"] = True
    socketio.emit('update_controller', controller_data)
    
def no_disparo(pwm_dict):
    print("Laser apagado")
    GPIO.output(laser, GPIO.LOW)
    controller_data["laser_state"] = False
    socketio.emit('update_controller', controller_data)

# Aspiradora functions
def aspirar(pwm_dict):
    print("Aspirar")
    GPIO.output(Aspiradora, GPIO.HIGH)
    controller_data["aspiradora_state"] = True
    socketio.emit('update_controller', controller_data)

def apagar(pwm_dict):
    print("NoAspirar")
    GPIO.output(Aspiradora, GPIO.LOW)
    controller_data["aspiradora_state"] = False
    socketio.emit('update_controller', controller_data)

# Servo brazo functions
def extender(pwm_dict):
    servo_driver = pwm_dict['servo1']
    angleS1 = 90
    controller_data["servo_brazo_state"] = "extended"
    
    for i in range(1, 55):
        servo_driver.ChangeDutyCycle(calcular_duty_cycle(angleS1 - i))
        time.sleep(0.01)
        
    socketio.emit('update_controller', controller_data)

def retraer(pwm_dict):
    servo_driver = pwm_dict['servo1']
    angleS1 = 90
    controller_data["servo_brazo_state"] = "retracted"
    
    for i in range(1, 50):
        servo_driver.ChangeDutyCycle(calcular_duty_cycle(angleS1 + i))
        time.sleep(0.01)
        
    socketio.emit('update_controller', controller_data)

# Servo contenedor functions
def contenedor1(pwm_dict):
    servo_driver = pwm_dict['servo2']
    angleS2 = 180
    print("Sensor hacia la izquierda")
    servo_driver.ChangeDutyCycle(calcular_duty_cycle(angleS2 + 180))
    controller_data["servo_contenedor_state"] = "contenedor1"
    socketio.emit('update_controller', controller_data)

def contenedor2(pwm_dict):
    servo_driver = pwm_dict['servo2']
    angleS2 = 180
    print("Sensor hacia la derecha")
    servo_driver.ChangeDutyCycle(calcular_duty_cycle(angleS2 - 180))
    controller_data["servo_contenedor_state"] = "contenedor2"
    socketio.emit('update_controller', controller_data)

# Rangefinder functions
def read_rangefinder():
    address = 0x10  # Radar default address 0x10
    getLidarDataCmd = [0x5A, 0x05, 0x00, 0x01, 0x60]  # Gets the distance value instruction
    distance = getLidarData(address, getLidarDataCmd)
    controller_data["rangefinder_distance"] = distance
    socketio.emit('update_controller', controller_data)
    return distance

# Modified Controller Class
class MyController(Controller):
    def __init__(self, pwm_dict, **kwargs):
        super().__init__(**kwargs)
        self.pwm_dict = pwm_dict
    
    # Servo Rangefinder
    def on_up_arrow_press(self):
        controller_data["angle"] = 0
        print("Servo en 0 grados")
        self.pwm_dict['servo3'].ChangeDutyCycle(calcular_duty_cycle(controller_data["angle"]))
        socketio.emit('update_controller', controller_data)
    
    def on_left_arrow_press(self):
        controller_data["angle"] = max(0, controller_data["angle"] - controller_data["step"])
        self.pwm_dict['servo3'].ChangeDutyCycle(calcular_duty_cycle(controller_data["angle"]))
        print(f"El servo se movio {controller_data['angle']}")
        socketio.emit('update_controller', controller_data)
    
    def on_right_arrow_press(self):
        controller_data["angle"] = min(180, controller_data["angle"] + controller_data["step"])
        self.pwm_dict['servo3'].ChangeDutyCycle(calcular_duty_cycle(controller_data["angle"]))
        print(f"El servo se movio {controller_data['angle']}")
        socketio.emit('update_controller', controller_data)
    
    # Aspiradora
    def on_playstation_button_press(self):
        aspirar(self.pwm_dict)

    def on_playstation_button_release(self):
        apagar(self.pwm_dict)
        
    # Servo brazo de la aspiradora
    def on_share_press(self):
        print("Brazo en posicion normal")
        retraer(self.pwm_dict)
        
    def on_share_release(self):
        extender(self.pwm_dict)
        
    # Servo muestrario
    def on_options_press(self):
        contenedor1(self.pwm_dict)
        
    def on_options_release(self):
        print("Cambio de contenedor completado")
        contenedor2(self.pwm_dict)
    
    # Funcionalidades para el servo
    def on_L3_press(self):
        print("Imprimer lista: ", controller_data["n"])
        socketio.emit('update_controller', controller_data)
        
    def on_circle_press(self):
        controller_data["n"] = [0, 0, 0, 0]
        print("Lista en cero: ", controller_data["n"])
        socketio.emit('update_controller', controller_data)
    
    # Funcionalidades Rangefinder
    def on_triangle_press(self):
        controller_data["n"][0] = read_rangefinder()
        controller_data["n"][1] = controller_data["angle"]
        print("Tomando distancia: ", controller_data["n"])
        socketio.emit('update_controller', controller_data)
        
    def on_square_press(self):
        controller_data["n"][2] = read_rangefinder()
        controller_data["n"][3] = controller_data["angle"]
        print("Tomando distancia: ", controller_data["n"])
        socketio.emit('update_controller', controller_data)
        
    # Resultado del calculo del servo
    def on_R1_press(self):
        n_values = controller_data["n"]
        result = TrianguloMain.func(n_values[0], n_values[2], n_values[1], n_values[3])
        controller_data["triangulo_result"] = int(result)
        print(controller_data["triangulo_result"])
        socketio.emit('update_controller', controller_data)
    
    # Disparo del laser
    def on_R3_press(self):
        disparo(self.pwm_dict)
        
    def on_R3_release(self):
        no_disparo(self.pwm_dict)

    # Funcionalidades para el servo
    def on_L1_press(self):
        changestpmas()
        
    def on_R1_release(self):
        changestpmenos()

# Controller thread function
def run_controller(pwm_dict):
    try:
        controller = MyController(pwm_dict, interface="/dev/input/js0", connecting_using_ds4drv=False)
        # Start servo PWMs
        pwm_dict['servo1'].start(7)
        pwm_dict['servo2'].start(7)
        pwm_dict['servo3'].start(7)
        
        controller.listen()
        
    except Exception as e:
        print(f"Controller error: {e}")
    finally:
        for servo in pwm_dict.values():
            servo.stop()
        GPIO.cleanup()
        print("Controller thread ended")

# Lidar continuous reading thread
def lidar_tf_luna():
    while True:
        try:
            distance = read_rangefinder()
            # Only update every 100ms to avoid flooding the socket
            time.sleep(0.1)
        except Exception as e:
            print(f"Lidar error: {e}")
            time.sleep(1)

# Flask routes
@app.route('/')
def index():
    mensaje = 'Controlador PS4 y Sensor Lidar en tiempo real'
    return render_template('index.html', mensaje=mensaje)

# SocketIO event handlers
@socketio.on('connect')
def handle_connect():
    socketio.emit('update_controller', controller_data)
    print("Client connected")

@socketio.on('request_data')
def handle_request_data():
    socketio.emit('update_controller', controller_data)

if __name__ == '__main__':
    try:
        # Setup GPIO and get PWM objects
        pwm_dict = setup_gpio()
        
        # Start controller thread
        controller_thread = threading.Thread(target=run_controller, args=(pwm_dict,), daemon=True)
        controller_thread.start()
        
        # Start lidar thread
        lidar_thread = threading.Thread(target=lidar_tf_luna, daemon=True)
        lidar_thread.start()
        
        # Start Flask server
        socketio.run(app, debug=True, host='0.0.0.0', port=5000)
        
    except KeyboardInterrupt:
        print("\nProgram interrupted by user.")
    finally:
        GPIO.cleanup()
        print("Goodbye")
