# Raspberry-Pi

Código en Python para controlar un robot/rover con **Raspberry Pi**: manejo con control de PS4, medición de distancia con LiDAR, servos, mecanismo de aspiración, cámara y un panel web en tiempo real.

## 1. Descripción

El proyecto reúne los módulos del robot: movimiento con motores DC, accionamiento de servos y de una aspiradora mediante un control **PS4**, lectura de distancias con un sensor LiDAR por I2C, transmisión de video con la cámara y un servidor **Flask-SocketIO** que muestra el estado del control en el navegador.

## 2. Características

- Movimiento de 2 o 4 motores con PWM, controlado con un mando PS4 (`pyPS4Controller`).
- Control de servos (extender/retraer, selección de contenedor, disparo) y de la aspiradora.
- Lectura de distancia con el LiDAR **TF-Luna** por I2C (resultado convertido a pulgadas).
- Cálculo de la distancia entre dos puntos con la ley de cosenos (`TrianguloMain.py`).
- Servidor web con **Flask-SocketIO** que emite en vivo el estado del control (puerto 5000).
- Streaming de cámara con `Picamera2`.
- Script de arranque automático (`launcher.sh`) para ejecutar el programa al encender la Raspberry Pi.

## 3. Tecnologías

- Python 3.11.12
- Raspberry Pi (GPIO, I2C)
- Flask · Flask-SocketIO

## 4. Librerías

`smbus` · `time` · `pyPS4Controller` · `ds4drv` · `RPi.GPIO` · `Rangefinder` · `TrianguloMain` · `math` · `flask` · `flask-socketio` · `picamera2` · `Pillow` · `numpy`

```bash
pip install RPi.GPIO smbus2 pyPS4Controller flask flask-socketio pillow numpy
sudo pip install ds4drv
```

`smbus` y `picamera2` suelen instalarse con `apt` en Raspberry Pi OS.

## 5. Hardware

- Raspberry Pi con I2C habilitado
- Driver de motores (pines `ENA/ENB`, `IN1–IN4`) y motores DC
- Sensor LiDAR TF-Luna (dirección I2C `0x10`)
- Servomotores y aspiradora
- Cámara compatible con `Picamera2`
- Control de PS4 emparejado por Bluetooth

## 6. Uso

Panel web con control en vivo:

```bash
cd Flask_Connection
python app.py
```

Abre `http://<ip-de-la-raspberry>:5000`.

Prueba de movimiento solo con el control:

```bash
python Modules/Movement/manejo.py
```

### Arranque automático

`UpdateGIt/launch/launcher.sh` espera unos segundos y lanza el script principal; se configura con `cron` (`@reboot`). La salida queda registrada en `UpdateGIt/logs/cronlog`. Ajusta la ruta del script a tu usuario.

## 7. Estructura

```
Raspberry-Pi/
├── Modules/Movement/        # Movimiento, LED de prueba y control PS4
├── Flask_Connection/        # Panel web (Flask-SocketIO) + Rangefinder
│   └── Object Distance/     # Cámara, servo, triangulación y pruebas
├── UpdateGIt/               # Versión de despliegue + launcher y logs
├── Diagrams/                # Diagramas del sistema de movimiento y de tareas
└── paginas que hemos usado  # Referencias consultadas
```
