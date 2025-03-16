import smbus
import time

bus = smbus.SMBus(1) # Change the I2C bus number based on the actual device

address = 0x10 # Radar default address 0x10
getLidarDataCmd = [0x5A,0x05,0x00,0x01,0x60] # Gets the distance value instruction

def getLidarData(addr, cmd):
    bus.write_i2c_block_data(addr, 0x00, cmd)
    time.sleep(0.01)
    data = bus.read_i2c_block_data(addr, 0x00, 9)
    distance = data[0] | (data[1] << 8)
    strengh = data[2] | (data[3] << 8)
    temperature = (data[4] | (data[5] << 8)) / 100 
    return int(distance)


