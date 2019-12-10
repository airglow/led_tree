import serial
import time
import numpy as np
import sys

class LEDController:
    def __init__(self, led_count, port='/dev/ttyUSB0', baudrate=115200, timeout=1):
        self.led_count = led_count
        self.conf = np.zeros((led_count, 3), dtype=np.uint8)
        self.ser = None
        
        try:
            self.ser = serial.Serial(port, baudrate, timeout=timeout)
        except IOError:
            print("Could not open serial port. Was the correct Port selected? Is the "
            "microcontroller connected? \n\nExiting application...")
            sys.exit(-1)

    def __del__(self):
        if self.ser:
            self.ser.close()

    def send(self):
        self.ser.write(b'\xFF'); # start byte
        self.ser.write(self.conf.reshape((3*self.led_count,)))

    def get_conf(self):
        return self.conf

    def all_on(self):
        self.conf = np.full((self.led_count, 3), 254, dtype=np.uint8)
        self.send()

    def all_off(self):
        self.conf = np.zeros((self.led_count, 3), dtype=np.uint8)
        self.send()

    def set_single_led(led_id, value=[254,254,254]):
        self.conf = np.zeros((self.led_count, 3), dtype=np.uint8)
        self.conf[led_id] = value
        self.send()

    def set_config(self, config):
        if self.conf.shape != config.shape:
            print("Wrong shape: {}. Correct shape: {}".format(self.conf.shape, config.shape))
            return
        if config.dtype != np.uint8:
            print("Datatype must be np.uint8.")
            return

        if config.max() >= 255:
            print("Config contains value 255. But 255 is reserved as start byte")
            return

        self.conf = config
        self.send()
