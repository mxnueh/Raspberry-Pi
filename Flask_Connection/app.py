from flask import Flask, render_template
from flask_socketio import SocketIO
import time
import threading
from Rangefinder import getLidarData

app = Flask(__name__)
socketio = SocketIO(app)

TiempoTranscurrido = 0
contador_ejecutandose = False
SenalesControl = False
LidarSensor = False
lidar = None 

@app.route('/')
def index():
    mensaje = 'Contador en tiempo real'
    return render_template('index.html', mensaje=mensaje)


def contador():
    global TiempoTranscurrido
    HoraInicio = time.perf_counter()
    while True:
        TiempoTranscurrido = time.perf_counter()-HoraInicio
        Hours = int(TiempoTranscurrido // 3600)
        minutes = int(TiempoTranscurrido // 60)
        seconds = int(TiempoTranscurrido % 60)
        milliseconds = int((TiempoTranscurrido % 1) * 1000)
        socketio.emit('update_number', {
                      'number': f"{Hours:02}:{minutes:02}:{seconds:02}:{milliseconds:03}"})
        time.sleep(0.01)  # Update every 10ms

def lidar_tf_luna():
    global LidarSensor #Hilo

    while True: 
        address = 0x10 
        getLidarDataCmd = [0x5A,0x05,0x00,0x01,0x60] 
        
        lidar = getLidarData(address, getLidarDataCmd)
        socketio.emit('update_lidar', {'LidarSensor': getLidarData})
        
        time.sleep(0.01)  # Update every 10ms


@socketio.on('connect')
def handle_connect():
    global contador_ejecutandose
    global LidarSensor
    
    socketio.emit('update_number', {'number': TiempoTranscurrido})
    socketio.emit('update_lidar', {'LidarSensor': lidar})

    if not contador_ejecutandose:
        contador_ejecutandose = True
        hilo = threading.Thread(target=contador, daemon=True)
        hilo.start()

    if not LidarSensor:
        LidarSensor = True
        hilo = threading.Thread(target=lidar_tf_luna, daemon=True)
        hilo.start()

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
