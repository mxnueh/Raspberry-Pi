from flask import Flask, render_template
from flask_socketio import SocketIO
import time
import threading 

app = Flask(__name__)
socketio = SocketIO(app)

contador_actual = 0
contador_ejecutandose = False 

@app.route('/')
def index():
    mensaje = 'Contador en tiempo real'
    return render_template('index.html', mensaje=mensaje)

def contador():
    global contador_actual
    while True:
        contador_actual += 1
        socketio.emit('update_number', {'number': contador_actual})
        time.sleep(1) 

@socketio.on('connect')
def handle_connect():
    global contador_ejecutandose
    socketio.emit('update_number', {'number': contador_actual})  

    if not contador_ejecutandose:
        contador_ejecutandose = True
        hilo = threading.Thread(target=contador, daemon=True)  
        hilo.start()

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
