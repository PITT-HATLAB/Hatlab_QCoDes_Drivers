import serial
import time
from datetime import datetime
import os
import ctypes as ct
import logging
from qcodes import Instrument


class Arduino_TempSensor(Instrument):
    def __init__(self, name: str, comPort: str, **kwargs):
        super().__init__(name, **kwargs)

        logging.info(__name__ + f' : Initializing instrument Arduino_TempSensor on port  {comPort}')

        self.add_parameter('temperature',
                           label='temperature',
                           get_cmd=self.get_temperature
                           )

        self.ser = serial.Serial(comPort, baudrate=115200, timeout=5)

        # somehow this is necessary on a windows computer
        # https://stackoverflow.com/questions/2301127/pyserial-app-runs-in-shell-by-not-py-script
        time.sleep(1)
        self.ser.dtr = 0
        time.sleep(1)

        # get the connect sensors from the setup message
        sensors_str = self.read_line()
        print(f"Arduino temperature sensor, port {comPort}", sensors_str)
        self.connected_sensors = sensors_str.replace("connected sensors: ", "") # mask for connected sensors

    def read_line(self):
        line = self.ser.readline()
        try:
            ld = line[:-2].decode("utf-8")
        except Exception as e:
            print(e)
            ld = None
        return ld

    def get_temperature(self):
        # write commend to the arduino for getting temperature
        self.ser.write(b'A')
        time.sleep(0.1)
        '''give the ardu time to think. btw, even though the
        measurements are recorded with delays, the measurements themselves
        represent one instant
        '''
        temp_str = self.read_line()
        temps_ = temp_str.split(",")
        temps = []
        for i, vld in enumerate(self.connected_sensors):
            if vld == "1":
                temps.append(float(temps_[i]))
            else:
                temps.append(None)
        return temps

    def get_temp_dict(self, sensors="1111"):
        temps = self.get_temperature()
        temp_dict={}
        for i, t in enumerate(temps):
            if (sensors[i] == "1") and (t is not None):
                temp_dict[f"{self.name}_{i}_temperature"] = t
        return temp_dict



if __name__ == "__main__":
    temp = Arduino_TempSensor("temp", "COM7")
    temp.temperature()


