import io
import logging
import socketserver
from threading import Condition
from http import server
from picamera2 import Picamera2
from PIL import Image
import numpy as np
import time

PAGE = """
<html>
<head>
<title>Raspberry Pi - Surveillance Camera</title>
<style>
    * {
        padding: 0;
        margin: 0
    }
</style>
</head>
<body>
<p>Valor actual: <span id="miVariable">0</span></p>
    <button onclick="actualizarValor()">Actualizar</button>

    <script>
        let contador = 0;

    function actualizarValor() {
    
        document.getElementById("miVariable").innerText = contador;
    }

    // Hacer que la variable se actualice autoticamente cada segundo
    setInterval(actualizarValor, 1000);
    </script>
<center><h1 color="red">Raspberry Pi - Surveillance Camera</h1></center>
<center><img src="stream.mjpg" width="640" height="480"></center>
</body>
</html>
"""

class StreamingOutput:
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def update_frame(self, frame):
        with self.condition:
            self.frame = frame
            self.condition.notify_all()

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning('Removed streaming client %s: %s', self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={'size': (640, 480), 'format': 'YUYV'}))
picam2.start()
output = StreamingOutput()

def capture_frames():
    while True:
        image = picam2.capture_array("main")
        image = Image.fromarray(image)
        with io.BytesIO() as output_io:
            image.convert('RGB').save(output_io, format='JPEG')  # Convertir YUYV a RGB y luego a JPEG
            output.update_frame(output_io.getvalue())
        time.sleep(0.1)  # Capturar aproximadamente 10 FPS

import threading
threading.Thread(target=capture_frames, daemon=True).start()

try:
    address = ('', 8000)
    server = StreamingServer(address, StreamingHandler)
    server.serve_forever()
finally:
    picam2.stop()