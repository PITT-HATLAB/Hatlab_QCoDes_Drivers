# -*- coding: utf-8 -*-
"""
@author: Chao Zhou

A driver for Keithley 6220/6221 current source. More functions can be added.

The function is not complete yet.
"""
import logging
from typing import Any, Dict, Optional, Union, List

import numpy as np

from qcodes import VisaInstrument
from qcodes.utils.validators import Numbers, Enum



class Keithley_622x(VisaInstrument):
    def __init__(self, name, ipAddress, **kwargs):
        """
        :param name: Name of the device that will be used for calling
        :param ipAddress: IP address of the device, in format of "'TCPIP::169.254.253.232"
        """
        super().__init__(name, ipAddress, terminator='\n', **kwargs)
        logging.info(__name__+ ' : Initializing Keithley_622x')
        self._address = ipAddress + "::1932::" #todo:
        self.write("SOUR:SWE:SPAC LIST")
        # Query the instrument to see what frequency range was purchased
        self.connect_message()

        self.add_parameter('current',
                           label='current',
                           get_cmd='SOUR:CURR?',
                           get_parser=float,
                           set_cmd='SOUR:CURR {:.13f}',
                           set_parser=float,
                           unit='A',
                           vals=Numbers(min_value=-50e-3, max_value=50e-3)) # for protection

        self.add_parameter('output_level', # same as current
                           label='current',
                           get_cmd='SOUR:CURR?',
                           get_parser=float,
                           set_cmd='SOUR:CURR {:.13f}',
                           set_parser=float,
                           unit='A',
                           vals=Numbers(min_value=-30e-3, max_value=30e-3))

        self.add_parameter('output_status',
                           label='output_status',
                           get_cmd='OUTP:STAT?',
                           get_parser=int,
                           set_cmd='OUTP:STAT {}',
                           set_parser=int)

        self.add_parameter('output_range',
                           label='output_range',
                           get_cmd='SOUR:CURR:RANG?',
                           get_parser=float,
                           set_cmd='SOUR:CURR:RANG {:.13f}',
                           unit="A",
                           vals=Numbers(min_value=-105e-3, max_value=105e-3))

        self.add_parameter('voltage_limit',
                           label='voltage limit',
                           get_cmd='SOUR:CURR:COMP?',
                           get_parser=float,
                           set_cmd='SOUR:CURR:COMP{:.1}',
                           unit="V",
                           vals=Numbers(min_value=0.1, max_value=105))



    def get_idn(self) -> Dict[str, Optional[str]]:
        IDN_str = self.ask_raw('*IDN?')
        vendor, model, serial, firmware = map(str.strip, IDN_str.split(','))
        IDN: Dict[str, Optional[str]] = {
            'vendor': vendor, 'model': model,
            'serial': serial, 'firmware': firmware}
        return IDN

    def sweep_current(self, currentList:Union[List,np.ndarray], delays: Union[List, float]):
        self.write("SOUR:SWE:ABOR") #todo: try?

        if type (delays) in [list, np.ndarray]:
            if len(delays) != len(currentList):
                raise IndexError(f"delays has a length of {len(delays)}, which is shorter than the length of currentList {len{currentList}")
        else:
            delays = np.zeros_like(currentList) + delays

        currentListStr = f"{[float(i) for i in currentList]}"[1:-1]
        delayListStr = f"{[float(t) for t in delays]}"[1:-1]

        self.write("SOUR:LIST:CURR " + currentListStr)
        self.write("SOUR:LIST:DEL " + delayListStr)
        self.write("SOUR:SWE:ARM")
        self.write("INIT:IMM")
        return np.sum(delays)

    def change_current(self, new_current, rate=None):
        """Changes the current to a new value using a steady ramp to get from the
        old value to the new value.
        :param new_current: target current in A
        :param rate: ramp slope of the current in A/sec
        """
        init_curr = self.current()
        steps = (new_current-init_curr)/rate * 10 # assume current change 10 times per second
        currentList = np.linspace(init_curr, new_current, steps)
        return self.sweep_current(currentList, 0.1)




if __name__ == "__main__":
    curr = Keithley_622x("curr", 'TCPIP::169.254.253.232::inst0::INSTR')