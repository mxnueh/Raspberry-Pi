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
