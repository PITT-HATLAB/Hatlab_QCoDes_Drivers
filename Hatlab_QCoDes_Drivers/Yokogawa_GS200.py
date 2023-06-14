# -*- coding: utf-8 -*-
"""
Created on Wed Jun 24 15:39:29 2020
@author: Ryan Kaufman
'change_current' functions is modified by Chao to avoid timeout issue when using the instrument from a client.
"""


#The Qcodes driver does pretty much everything I need it to, 
#the problem is that it's not formatted like we used to have it
#So this driver will subclass the qcodes driver 
#(at: https://github.com/QCoDeS/Qcodes/blob/master/qcodes/instrument_drivers/yokogawa/GS200.py)
#and just add a few things that we used before
import time
import logging
from qcodes.instrument_drivers.yokogawa.GS200 import GS200
import numpy as np
from functools import partial
from typing import Optional, Union, Any

RAMPRATE = 0.1e-3 #A/s

class YOKO(GS200): 
    
    def __init__(self,name: str, address: str = None, terminator: str = "\n", initCurrentSource=True, **kwargs):
        if address == None:
            raise Exception('TCPIP Address needed')
        super().__init__(name, address, terminator = terminator, **kwargs)
        #the driver assumes you just turned on the YOKO, and it's in voltage mode. This is almost never the case
        #for us so this sequence changes that assumption to currents instead of voltages
        self._cached_mode = "CURR"
        self.output_level.source = self.current # the whole parameter, not just one value
        self.max_abs_current = 10e-3

        if initCurrentSource:
            try:
                self.source_mode("CURR")
                self.voltage_limit(1)
            except Exception as e:
                logging.warning(e)
        else:
            try:
                self._cached_range_value = self.current_range()
            except Exception as e:
                logging.warning("YOKO set to non-current mode")


    def change_current(self, new_current, rate = None):
        '''
        Changes the current to a new value using a steady ramp to get from the old value to the new value.
        The ramping is done internaly in YOKO, instead of sending multiple set commends from python with time intervals.
        Input:
            new_current (float) : the value the current will be set to
            (in A)
            rate (float) : the rate of change of the current (in A/sec)
        '''
        if np.abs(new_current) > np.abs(self.max_abs_current): 
            raise Exception(f'The requested current {new_current*1000} mA is above the maximum value of {self.max_abs_current*1000} mA\n \ 
            If you need to change this, you can change the class attribute "max_abs_current" by setting "yoko.max_abs_current = new_max_value"')
        min_current = -1 * self.current_range()
        max_current = self.current_range()
        org_current = self.current()
        
        step_size = new_current - org_current
        if rate is None:
            rate = RAMPRATE

        if new_current > max_current:
            logging.warning('Current value too high. Set to %f' % max_current)
            new_current = max_current
        if new_current < min_current:
            logging.warning('Current value too low. Set to %f' % min_current)
            new_current = min_current
        if step_size == 0:
            logging.info('Trying to set to same current')
            return False

        _range = float(self.ask("source:range?"))
        self.write(':prog:def "{name}","{data}";:prog:load "{name}"'.format(name='change_current.csv',
                               data='{},{},I'.format(new_current, _range)))
        time.sleep(0.1)
        slope_time = abs(step_size / rate)
        self.write(':prog:slope {}'.format(slope_time))
        interval = slope_time
        print(interval)
        if interval < .1:
            interval = .1

        time.sleep(0.1)
        self.write(':prog:int %s;:prog:rep 0;:prog:step' % interval)

        return float(interval)


    def bump(self, bump):
        old = self.current()
        new = old + bump
        self.change_current(new)



