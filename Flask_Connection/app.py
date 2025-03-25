from flask import Flask, render_template
from flask_socketio import SocketIO
import time
import threading

app = Flask(__name__)
socketio = SocketIO(app)

TiempoTranscurrido = 0
contador_ejecutandose = False


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


@socketio.on('connect')
def handle_connect():
    global contador_ejecutandose
    socketio.emit('update_number', {'number': TiempoTranscurrido})

    if not contador_ejecutandose:
        contador_ejecutandose = True
        hilo = threading.Thread(target=contador, daemon=True)
        hilo.start()


if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
=======
from flask import Flask, render_template
from flask_socketio import SocketIO
import time
import threading  # Para manejar el hilo

app = Flask(__name__)
socketio = SocketIO(app)

contador_actual = 0
contador_ejecutandose = False  # Bandera para evitar múltiples hilos

@app.route('/')
def index():
    mensaje = 'Contador en tiempo real'
    return render_template('index.html', mensaje=mensaje)

def contador():
    global contador_actual
    while True:
        contador_actual += 1
        socketio.emit('update_number', {'number': contador_actual})
        time.sleep(1)  # Espera 1 segundo

@socketio.on('connect')
def handle_connect():
    global contador_ejecutandose
    socketio.emit('update_number', {'number': contador_actual})  # Envía el valor actual al conectarse

    # Verificar si ya está corriendo el hilo del contador
    if not contador_ejecutandose:
        contador_ejecutandose = True
        hilo = threading.Thread(target=contador, daemon=True)  # Se asegura de que el hilo termine con la app
        hilo.start()

if __name__ == '__main__':
    socketio.run(app, debug=True)
>>>>>>> 6a0210f (Cambiando el nombre de la carpeta de New folder a Flask Connection)
