import logging
from typing import Any, Dict, Optional, Union, List

import numpy as np

from qcodes import VisaInstrument
from qcodes.utils.validators import Numbers, Enum


class Keithley_622x(VisaInstrument):
    def __init__(self, name, address, **kwargs):
        """
        :param name: Name of the device that will be used for calling
        :param ipAddress: IP address of the device, in format of "'TCPIP::169.254.253.232"
        """
        super().__init__(name, address, terminator='\n', **kwargs)
        logging.info(__name__+ ' : Initializing Keithley_622x')
        self._address = address
        self.write("SOUR:SWE:SPAC LIST")
        # Query the instrument to see what frequency range was purchased
        self.connect_message()



if __name__ == '__main__':
    curr = Keithley_622x("curr", "TCPIP::169.254.47.111::1394::SOCKET")



    # if len(sys.argv) != 3:
    #     print("Usage: ", os.path.basename(sys.argv[0]), "<COM port> <GPIB address>")
    #     sys.exit(1)
    #
    # comport = sys.argv[1];
    # addr = sys.argv[2];
    #
    # ser = serial.Serial()
    #
    # try:
    #     success = True
    #
    #     ser = serial.Serial('\\\\.\\' + sys.argv[1], 9600, timeout=0.5)
    #
    #     cmd = '++mode 1'
    #     print('Sending:', cmd)
    #     ser.write(cmd + '\n')
    #     s = ser.read(256);
    #     if len(s) > 0:
    #         print
    #         s
    #
    #     cmd = '++addr ' + addr
    #     print('Sending:', cmd)
    #     ser.write(cmd + '\n')
    #     s = ser.read(256);
    #     if len(s) > 0:
    #         print
    #         s
    #
    #     cmd = '++auto 1'
    #     print('Sending:', cmd)
    #     ser.write(cmd + '\n')
    #     s = ser.read(256);
    #     if len(s) > 0:
    #         print
    #         s
    #
    #     cmd = 'plot;'
    #     print('Sending:', cmd)
    #     ser.write(cmd + '\n')
    #
    #     f = open("plot.bin", "wb")
    #
    #     while (1):
    #         s = ser.read(1000)
    #         if len(s) > 0:
    #             f.write(s)
    #         else:
    #             break
    #
    #     f.close()
    #
    # except serial.SerialExceptionas as e:
    #     print(e)
    #     f.close()
    #
    # except KeyboardInterrupt as e:
    #     ser.close()
    #     f.close()
    #
