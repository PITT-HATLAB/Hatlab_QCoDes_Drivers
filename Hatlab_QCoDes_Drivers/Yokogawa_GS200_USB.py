# -*- coding: utf-8 -*-
"""
A driver to control the Yokogawa GS200 through USB port using QCoDes
Modified based on the TCPIP driver written by Eric

@author: Chao 
"""

import ctypes as ct
import logging
import time
from typing import Any, Dict, Optional

from qcodes import Instrument
from qcodes.utils.validators import Numbers, Enum
from Hatlab_QCoDes_Drivers import DLLPATH

MIN_CURR = -200E-3
MAX_CURR = 200E-3
RATE = 0.1e-3 #A/s




class Yokogawa_GS200_USB(Instrument):
    def __init__(self, name, serial_number = '91UA31819', dll = None,
			source_type = 'current', rate = RATE, minimum = MIN_CURR, maximum = MAX_CURR, reset = False, **kwargs):
        super().__init__(name, **kwargs)
        """
        Initializes the Yokogawa GS200
            Input:
                name (string)    : name of the instrument
                address (string) : TCP/IP address
                reset (bool)     : resets to default values, default=False
        """
        if dll is not None:
            self._dll = ct.CDLL(dll)
        else:
            self._dll = ct.CDLL(DLLPATH + '\\YOKO_USB\\tmctl64.dll')  # access dll file
        
        self._serial_number = ct.c_char_p(bytes(serial_number,'utf-8')) 

								
        self._rate = rate
        self._minimum = minimum
        self._maximum = maximum

        self.activate_device_control()
        self.do_set_source("CURR")
        self.do_set_voltage_limit(lim = 1)
        self.usb_write(':SOUR:RANG 100E-3')								
									

        self.add_parameter('output_status',
                           label='output_status',
                           get_cmd=self.do_get_output,
                           get_parser=int,
                           set_cmd=self.do_set_output,
                           vals=Numbers(min_value=0, max_value=1))

        self.add_parameter('source_type',
                           label='output as current or voltage source',
                           get_cmd=self.do_get_source,
                           set_cmd=self.do_set_source,
                           vals=Enum('CURR', 'VOLT'))

        self.add_parameter('output_range',
                           label='output_range',
                           get_cmd=self.do_get_output_range,
                           get_parser=float,
                           set_cmd=self.do_set_output_range,
                           unit="A",
                           vals=Numbers(min_value=1e-3, max_value=0.2))

        self.add_parameter('output_level',
                           label='output_level',
                           get_cmd=self.do_get_output_level,
                           get_parser=float,
                           set_cmd=self.change_current,
                           unit="A",
                           vals=Numbers(min_value=-0.1, max_value=0.1))

        self.add_parameter('output_protection',
                           label='output_level',
                           get_cmd=self.do_get_output_protection,
                           get_parser=float,
                           set_cmd=self.do_set_output_protection,
                           unit="A",
                           vals=Numbers(min_value=-0.1, max_value=0.1))

        self.add_parameter('voltage_limit',
                           label='voltage limit',
                           get_cmd=self.do_get_voltage_limit,
                           get_parser=float,
                           set_cmd=self.do_set_voltage_limit,
                           unit="V",
                           vals=Numbers(min_value=1, max_value=30))
        if reset:
            self.reset()

## Tool Functions ############################################################
    def activate_device_control(self):
        wire = ct.c_int(7) #USB wire
        self.ID = ct.c_int() 
        err = self._dll.TmcInitialize(wire, self._serial_number, ct.byref(self.ID))
        if err: 
            raise NameError(f'YOKO Connection Error:{err}')
												
    def close_device(self):
        err = self._dll.TmcFinish(self.ID)
        if err: 
            raise NameError('YOKO Connection Error')

    def usb_write(self, msg, reactivate=False):
        if reactivate:
            self.activate_device_control()
        err = self._dll.TmcSend( self.ID, ct.c_char_p(bytes(msg,'utf-8')) )
        if err: 
            raise NameError('YOKO Parameter Write Error')
        if reactivate:
            self.close_device()												
    
    def usb_ask (self, msg, reactivate=False):
        if reactivate:
            self.activate_device_control()
        err_s = self._dll.TmcSend( self.ID,  ct.c_char_p(bytes(msg,'utf-8')))
        blen = ct.c_int(1000)
        buff = ct.create_string_buffer(blen.value)
        rlen = ct.c_int() 
        err_r = self._dll.TmcReceive( self.ID, buff, blen, ct.byref(rlen) )
        if err_s or err_r :
            raise NameError('YOKO Parameter Read Error')									
        if reactivate:
            self.close_device()		

        return buff.value



##  Parameters  ##############################################################
    def do_set_source(self, source="CURR"):
        '''
        Sets the output source, current or voltage
        '''
        if source == "CURR":
            self.usb_write(':SOUR:FUNC CURR')
        elif source == "VOLT":
            self.usb_write(':SOUR:FUNC VOLT')
        else:
            raise NameError("Invalid source format. Use 'CURR' or 'VOLT' ")

    def do_get_source(self):
        '''
        Gets the output source, current or voltage
        '''
        print(self.usb_ask(':SOUR:FUNC?'))

    def do_set_voltage_limit(self, lim = 1):
        '''
        Sets the output voltage limit 
        '''
        self._log('Seting the voltage limit')
        self.usb_write(':SOUR:PROT:VOLT %s' %lim)	
								
    def do_get_voltage_limit(self):
        '''
        Gets the output voltage limit 
        '''
        self._log('Geting the voltage limit')
        return self.usb_ask(':SOUR:PROT:VOLT?')	
            
    def do_get_output(self):
        '''
        Reads the output state
            Output:
                state (int) : 0=OFF, 1=ON
        '''
        self._log('Reading the output state')
        return self.usb_ask(':OUTP:STAT?')

        
    def do_set_output(self, enable = 1):
        '''
        Sets the state of the output
            Output:
                enable (int) : 0=OFF, 1=ON
        '''
        self._log('Setting the output to %s' %enable)
        self.usb_write(':OUTP:STAT %s' %enable)

    
    def do_get_output_range(self):
        '''
        Reads the range of the output
            Output:
               range (string) : source range in A
        '''
        self._log('Reading the output range')
        return self.usb_ask(':sour:rang?')
        
    def do_set_output_range(self, _range):
        '''
        Sets the range of the output
            Input:
                range (string | <float>) : the range of the source, acceptable 
                values are:  max | min | up | down | <level> in A    
        '''
        possible_strings = ['max', 'min', 'up', 'down']
        _range = self._check_input_validity(_range, possible_strings, 
                                  self._minimum, self._maximum)
        self._log('Setting the output range to %s' %_range)
        self.usb_write(':sour:rang %s' %_range)
    
    def do_get_output_level(self):
        '''
        Reads the source level in terms of the range being used
            Output:
                level (string) : max | min | <level>
        '''
        self._log('Reading the source level')
        return self.usb_ask(':sour:lev?')
    def do_set_output_level(self, level):
        '''
        Sets the source level in terms of the range being used
            Input:
                level (string | <float>) : level produced max | min | <level>
        '''
        possible_strings = ['max', 'min']
        level = self._check_input_validity(level, possible_strings)
        self._log('Setting the source level to %s' %level)
        self.usb_write(':sour:lev %s' %level)
    def do_get_output_level_auto(self):
        '''
        Reads the source level in terms of the most appropriate range.
            Output:
                range (float) : in Amperes
        '''
        self._log('Reading the source level auto range')
        return self.usb_ask(':sour:lev:auto?')
        
    def do_set_output_level_auto(self, level):
        '''
        Sets the source level range to the smallest value which includes the 
        specified level
            Input:
                level (float) : in Amperes
        '''
        possible_strings = ['max', 'min']
        level = self._check_input_validity(level, possible_strings, self._minimum,
                                           self._maximum)
        self._log('Setting the output level auto range to %s' %level)
        self.usb_write(':sour:lev:auto %s' %level)
        
    def do_get_output_protection(self):
        '''
        Reads the current limiter level
            Output:
                limit (string) : current limit level max | min | <level>
        '''
        self._log('Reading the current limit level')
        return self.usb_ask(':sour:prot:curr?')
    def do_set_output_protection(self, limit):
        '''
        Sets the current limit level
            Input:
                limit (string) : max | min | <level>
        '''
        self._check_input_validity(limit, ['min','max'], self._minimum, 
                                   self._maximum)
        self._log('Setting the current limit to %s' % limit)
        self.usb_write(':sour:prot:curr %s' % limit)
##  Functions  ###############################################################
    def Initialize(self, filename):
        '''
        Saves the system's setup data
            Input:
                filename (string) : name of file to save to
        '''
        self._log('Saving system data to %s' % filename)
        self.usb_write(':syst:set:save %s' %filename)								
        
    def save_setup(self, filename):
        '''
        Saves the system's setup data
            Input:
                filename (string) : name of file to save to
        '''
        self._log('Saving system data to %s' % filename)
        self.usb_write(':syst:set:save %s' %filename)
        
    def load_setup(self, filename):
        '''
        Restores the system's setup
            Input:
                filename (string) : name of the file to be restored
        '''
        self._log('Restoring system state from file %s' % filename)
        self.usb_write(':syst:set:load %s' % filename)
    def send_instruction(self, command):
        '''
        Sends a generic instrucion to the unit
            Input:
                command (string) : see User's Manual for specific commands and 
                their behavior
        '''
        self.usb_write(command)
        
    def retrieve_data(self, command):
        '''
        Reads data from the unit
            Input:
                command (string) : see User's Manual for specifc commands and 
                the values returned
            Output:
               value (varied) : see User's Manual for specific commands and 
               the values returned
        '''
        return self.usb_ask(command)
        
    def reset(self):
        '''
        Resets the unit do default settings, and sets the output to current
        '''
        self._log('Resetting the instrument')
        self.usb_write('*RST;:sour:func curr')
    
    def get_all(self):
#        data = self.retrieve_data(':OUTP:STAT?;:sour:func?;:rang?;:lev?;:lev:auto?;:prot:curr?').split(',')
#        self.set_output(data[0])
#        self.set_output_function(data[1])
#        self.set_output_range(data[2])
#        self.set_output_level(data[3])
#        self.set_output_level_auto(data[4])
#        self.set_output_protection(data[5])
        self.get_output()
        self.get_output_function()
        self.get_output_range()
        self.get_output_level()
        self.get_output_level_auto()
        self.get_output_protection()
        
    def create_csv(self, stepval = 1e-3, minval=.001, maxval=.2):
        '''
        creates a list of currents formatted to be transferred to the Yokogawa 
        unit 
            Input:
                step (float) : the interval between current levels (note:
                negative values will count down from maxval to minval)
                minval (float) : the minimum value for the current to start at
                maxval (float) : the maximum value for the current to reach
            Output:
                csv_values (list) : 
                [(string)of the form "<level>,<range>,<source type>\n..." ,
                (int) the number of lines in the string]  
        '''
        string = ''
        source_type = 'I'
        iteration = 0
        currents = []
        if stepval>0:
            value = minval
            while value < maxval:
                string += '{},{},{}\n'.format(value, self.set_range(value), 
                                                source_type)
                currents.append(value)
                value += stepval
                iteration +=1
            string += '{},{},{}\n'.format(maxval, 
                                    self.set_range(maxval), source_type)
            currents.append(value)
            iteration +=1
        else:
            value = maxval
            while value > minval:
                string += '{},{},{}\n'.format(value, self.set_range(value), 
                                                source_type)
                currents.append(value)                                
                value += stepval
                iteration += 1
            string += '{},{},{}\n'.format(minval, 
                                    self.set_range(minval), source_type)
            currents.append(value)
            iteration +=1
        return [string, iteration]
        
    def set_range(self,_input, _set = True, reactivate=False):
        '''
        Gets an appropriate range for the current level 
            Input:
                _input (float) : the current level in Amperes
                _set (boolean) : if true, sets the range and returns the new range
                                 only returns the new range value if False
            Output:
                range (float) : the smallest range containing the input
        '''
        if abs(_input) < 1e-3:
            source_range = 10e-3
        elif abs(_input) < 10e-3:
            source_range = 10e-3
        elif abs(_input) < 100e-3:
            source_range = 100e-3
        else:
            source_range = 200e-3
        if _set:
            self.usb_write("source:range {}".format(source_range), reactivate)
        return source_range 
        
    def set_ramp_intervals(self, step = .001, rate = RATE):
        '''
        Sets the time it takes to ramp from one step to the next
            Input:
                step (float) : the difference between current levels in Ampere
                rate (float) : the rate of current change in Ampere/second
        '''
        slope_time = abs(step/rate)
        self.usb_write(':prog:slope {}'.format(slope_time))
        return slope_time
    def create_program(self, filename = 'fluxsweep.csv', 
                       step = 1e-3, min_current = MIN_CURR, max_current = MAX_CURR):
        '''
        Creates and loads a program in the Yokogawa unit to sweep current
            Input:
                filename (string) : name file will be saved as
                step (float) : the difference between each output level
                min_current (float) : the lowest current used
                max_current (float) : the highest current used
            Output:
                steps (int) : the total number of steps in the program
        '''
        csv_string = self.create_csv(stepval = step, minval = min_current,
                                     maxval = max_current)
        self.usb_write(':prog:def "{name}","{data}";:prog:load "{name}"'
                                    .format(name = filename, data=csv_string[0]))
        return csv_string[1]
        
    def get_slope_interval(self):
        return self.usb_ask(':prog:slope?')
        
    def set_slope_interval(self, rate):
        self.usb_write('prog:slope %s' % rate)

     
    def change_current(self, new_current, rate = None, min_current = MIN_CURR,
                       max_current = MAX_CURR):
        '''
        Changes the current to a new value using a steady ramp to get from the
        old value to the new value.
            Input:
                new_current (float) : the value the current will be set to 
                (in A)
                rate (float) : the rate of change of the current (in A/sec)
                min_current (float) : set a minimum value the current can be 
                set to (note: this does not change the limit for subsequent 
                calls)
                max_current (float) : set a maximum value the current can be 
                set to (note: this does not change the limit for subsequent 
                calls)
        '''

        org_current = float(self.usb_ask('sour:lev?', reactivate=False))

        step_size = new_current - org_current    
        if rate is None:
            rate = self._rate
        else:
            self._rate=rate
        if min_current < self._minimum:
            logging.warning('Requested lower limit too low. Limit set to %f A'
                            %self._minimum)
            min_current = self._minimum
        if min_current > self._maximum:
            logging.warning('Requested lower limit too high.')
            return False
        if max_current > self._maximum:
            logging.warning('Requested upper limit too high. Limit set to %f A'
                            %self._maximum)
            max_current = self._maximum
        if max_current < self._minimum:
            logging.warning('Requested upper limit too low.')
            return False
        if new_current > max_current:
            logging.warning('Current value too high. Set to %f' %max_current)
            new_current = max_current
        if new_current < min_current:
            logging.warning('Current value too low. Set to %f' %min_current)
            new_current = min_current
        if step_size == 0:
            logging.info('Trying to set to same current')
            return False
        
        _range = float(self.usb_ask("source:range?", reactivate=False))
        next_range = self.set_range(new_current, _set = False)            
        if _range <= next_range:
            _range = self.set_range(new_current)
        self.usb_write(':prog:def "{name}","{data}";:prog:load "{name}"'
                                    .format(name = 'change_current.csv', 
                                            data = '{},{},I'.format(new_current,
                                                                    _range)), reactivate=False)
        time.sleep(0.1)
        slope_time = abs(step_size/rate)
        self.usb_write(':prog:slope {}'.format(slope_time), reactivate=False)        
        interval = slope_time
        print (interval)
        if interval < .1:
            interval = .1
            
        time.sleep(0.1)
        self.usb_write(':prog:int %s;:prog:rep 0;:prog:step' %interval, reactivate=False)

        return float(interval)

    def step_current(self):
        '''
        Advances the Yokogawa program by one step
        '''
        self.usb_write(':prog:step')
##  Helpers  #################################################################
        
    
        
        
    def _log(self, string):
        '''
        Displays the string in the log as info
            Input:
                string (str) : message to be added to log
        '''
        logging.info(__name__ + ' : ' + string)
        
    def _check_input_validity(self, testval, strings, minval = None, maxval = None):
        '''
        Tests whether the testval is a valid input. It will convert the 
        testval to a float then test against minval and maxval. If testval is 
        too low or high, it will return minval or maxval respectively. If 
        testval cannot be converted to a float, it will be tested against 
        strings.
            Input:
                testval (float|string) : value to be tested
                strings (iterable) : values to be compared against if testval
                is not numerical
                minval (float) : lower bound for a numerical testval
                maxval (float) : upper bound for a numerical testval
        '''
        try:
            testval = float(testval)
            print (testval)
            if (minval is not None) and testval < minval:
                logging.warning('{} is out of bounds. Setting to {}'
                                .fromat(testval, minval))
                testval = minval
            if maxval is not None and testval > maxval:
                logging.warning('{} is out of bounds. Setting to {}'
                                .fromat(testval, maxval))
                testval = maxval
            print (testval)
        except:
            if testval.lower() not in strings:
                raise ValueError('%s is not a valid input' %testval)
        return testval# -*- coding: utf-8 -*-

    def close(self):
        self.close_device()

if __name__ == "__main__":
    yoko = Yokogawa_GS200_USB("yoko", '91UA31819')
