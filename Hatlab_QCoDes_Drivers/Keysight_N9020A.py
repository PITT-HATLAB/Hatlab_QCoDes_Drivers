# -*- coding: utf-8 -*-
"""
@author: Chao Zhou

A simple driver for Keysight_N9020A to be used with QCoDes, transferred from the one written by Erick Brindock.

"""

import logging
import warnings
import time

import numpy as np

from qcodes import VisaInstrument
from qcodes.utils.validators import Numbers, Enum

# list for accepted values for functions
TRACE_MODES = ['ON', 'VIEW', 'BLANK', 'BACKGROUND']
TRACE_TYPES = ['writ', 'write', 'aver', 'average', 'maxh', 'maxhold',
               'minh', 'minhold']
TRACE_DETECTORS = ['aver', 'average', 'neg', 'negative', 'norm', 'normal',
                   'pos', 'positive', 'samp', 'sample', 'qpe', 'qpeak',
                   'eav', 'eaverage', 'rav', 'raverage']


class Keysight_N9020A(VisaInstrument):
    def __init__(self, name, address, reset=False, **kwargs):
        """
        Initializes the Keysight MXA N9020A
            Input:
                name (string)    : name of the instrument
                address (string) : TCP/IP address
                reset (bool)     : resets to default values, default=False
        """
        super().__init__(name, address, terminator='\n', **kwargs)
        logging.info(__name__ + ' : Initializing Keysight N5183B')

        self._address = address

        self.add_parameter('frequency_center',
                           label='frequency_center',
                           get_cmd='FREQ:CENT?',
                           get_parser=float,
                           set_cmd='FREQ:CENT {}',
                           unit='Hz',
                           vals=Numbers(min_value=10, max_value=26.5e9))

        self.add_parameter('frequency_start',
                           label='frequency_start',
                           get_cmd='FREQ:STAR?',
                           get_parser=float,
                           set_cmd='FREQ:STAR {}',
                           unit='Hz',
                           vals=Numbers(min_value=10, max_value=26.5e9))

        self.add_parameter('frequency_stop',
                           label='frequency_stop',
                           get_cmd='FREQ:STOP?',
                           get_parser=float,
                           set_cmd='FREQ:STOP {}',
                           unit='Hz',
                           vals=Numbers(min_value=10, max_value=26.5e9))

        self.add_parameter('frequency_span',
                           label='frequency_span',
                           get_cmd='FREQ:SPAN?',
                           get_parser=float,
                           set_cmd='FREQ:SPAN {}',
                           unit='Hz',
                           vals=Numbers(min_value=10, max_value=26.5e9))

        self.add_parameter('bandwidth_res',
                           docstring="Note:Only certain discrete resolution bandwidths are available. "
                                     "The available bandwidths are dependent on the Filter Type or the EMC "
                                     "Standard. If an unavailable bandwidth is entered with the numeric "
                                     "keypad, the closest available bandwidth is selected.",
                           label='bandwidth_res',
                           get_cmd='BAND?',
                           get_parser=float,
                           set_cmd='BAND {}',
                           unit='Hz')

        self.add_parameter('bandwidth_res_auto',
                           label='bandwidth_res_auto',
                           get_cmd='BAND:AUTO?',
                           get_parser=int,
                           set_cmd='BAND:AUTO {}',
                           vals=Enum(0, 1))

        self.add_parameter('bandwidth_video',
                           label='bandwidth_video',
                           get_cmd='BAND:VID?',
                           get_parser=float,
                           set_cmd='BAND:VID {}',
                           unit='Hz',
                           vals=Numbers(min_value=1, max_value=50000000))

        self.add_parameter('bandwidth_video_auto',
                           label='bandwidth_video_auto',
                           get_cmd='BAND:VID:AUTO?',
                           get_parser=int,
                           set_cmd='BAND:VID:AUTO {}',
                           vals=Enum(0, 1))

        self.add_parameter('trigger_source',
                           label='trigger_source',
                           get_cmd='TRIG:SOUR?',
                           set_cmd='TRIG:SOUR {}',
                           vals=Enum('ext1', 'external1', 'ext2', 'external2', 'imm', 'immediate'))

        self.add_parameter('sweep_time',
                           label='sweep_time',
                           get_cmd='SWE:TIME?',
                           get_parser=float,
                           set_cmd='SWE:TIME {}',
                           unit='s',
                           vals=Numbers(min_value=1e-6, max_value=6000))

        self.add_parameter('max_count',
                           label='max_count',
                           get_cmd='AVER:COUN?',
                           get_parser=int,
                           set_cmd='AVER:COUN {}',
                           vals=Numbers(min_value=1, max_value=99999))

        self.add_parameter('sweep_time_auto',
                           label='sweep_time_auto',
                           get_cmd='SWE:TIME:AUTO?',
                           get_parser=int,
                           set_cmd='SWE:TIME:AUTO {}',
                           vals=Enum(0, 1))

        self.add_parameter('sweep_time_auto_rules',
                           label='sweep_time_auto_rules',
                           get_cmd='SWE:TIME:AUTO:RUL?',
                           set_cmd='SWE:TIME:AUTO:RUL {}',
                           vals=Enum('norm', 'normal', 'accuracy', 'acc', 'sres', 'sresponse'))

        self.add_parameter('continous_measurement',
                           label='continous_measurement',
                           get_cmd='INIT:CONT?',
                           set_cmd='INIT:CONT {}',
                           vals=Enum(0, 1))

        self.add_parameter('mode',
                           label='mode',
                           get_cmd=':INSTRUMENT?',
                           set_cmd=':INSTRUMENT {}')

        self.add_parameter('num_points',
                           label='num_points',
                           get_cmd=':SWE:POIN?',
                           set_cmd=':SWE:POIN {}')

        if reset:
            self.reset()

    def set_max_count(self, maxval):
        '''
        Sets the hold value
            Input: 
                maxval (int) : the number of averages taken (note: Only stops 
                if in Single measurement mode. See XNA-manual pg. 617 for more 
                information on continous mode averaging behavior)
        '''
        warnings.warn("This function is deprecated, is is recommended to call max_count(maxval) directly",
                      DeprecationWarning)
        logging.info(__name__ + ' Setting the max hol count to %s' % maxval)
        self.visa_handle.write('AVER:COUN %s' % maxval)

    def get_data(self, count=0, channel=1, mute=False):
        '''
        Reads the data from the current sweep (NEEDS TESTED)
            Input:
                count (int) : sets max hold value between 1 and 10,000
                0 uses the value stored in the instrument
                channel (int):
            Output:
                data (numpy 2dArray) : [x, y] values
        '''
        data = None
        if count is not 0:
            if count > 10000:
                count = 10000
                logging.warning(__name__ +
                                ' Count too high. set to max value 10000')
            self.visa_handle.write('AVER:COUN %s' % count)
        if channel < 1 or channel > 6:
            raise ValueError('channel must be between 1 and 6')
        else:
            pass
        while data is None:
            try:
                data = self.visa_handle.query('CALC:DATA%s?' % channel)
            except Exception as e:
                print('Running test.')
                logging.info(__name__ + str(type(e)) +
                             ' raised. Count not done')
            else:
                if not mute:
                    print('Count complete')
                logging.info(__name__ + ' Reading the trace data')
                data = data.lstrip('[').rstrip(']').split(',')
                data = [float(value) for value in data]
                np_array = np.reshape(data, (-1, 2))
                return np_array

    def average(self):
        self.visa_handle.write('AVER:CLE')

    def get_ydata(self, count=0, channel=1, mute=False):
        '''
        Reads the data from the current sweep (NEEDS TESTED)
            Input:
                channel (int):
            Output:
                data (numpy 2dArray) : [x, y] values
        '''
        data = None
        if channel < 1 or channel > 6:
            raise ValueError('channel must be between 1 and 6')
        data = self.visa_handle.query('TRAC? TRACE1')
        data = data.lstrip('[').rstrip(']').split(',')
        data = [float(value) for value in data]
        np_array = np.reshape(data)
        return np_array

    def get_previous_data(self, channel=1):
        '''
        Reads the data already acquired without starting a new test
        '''
        return self.visa_handle.query('CALC:DATA%s?' % channel)

    def get_average(self):
        '''
        Reads the average of the current sweep
            Output: 
                average (float) :the average
        '''
        logging.info(__name__ + ' Reading the average value')
        return self.visa_handle.query('CALC:DATA:COMP? MEAN')

    def trace_type(self, trace_type, channel=1):
        '''
        Sets the type of the trace on the specified channel
            Input:
                trace_type (string) : 
                    ['writ', 'write', 'aver', 'average', 'maxh', 'maxhold', 
                     'minh', 'minhold']
                channel (int) : channel 1-6
        '''
        self.is_valid_channel(channel)
        trace_type = trace_type.lower()
        if trace_type not in TRACE_TYPES:
            raise ValueError('%s is not a valid trace type' % trace_type)
        logging.info(__name__ +
                     ' setting trace type to {} on channel {}'.format(trace_type,
                                                                      channel))
        self.visa_handle.write('TRAC{}:TYPE {}'.format(channel,
                                                       trace_type))

    def trace_detector(self, detector, channel=1):
        '''
        Sets the detector for the trace on the specified channel
            Input:
                detector (string) : 
                    ['aver', 'average', 'neg', 'negative', 'norm', 'normal', 
                    'pos', 'positive', 'samp', 'sample', 'qpe', 'qpeak', 'eav',
                    'eaverage', 'rav', 'raverage']
                channel (int) : channel 1-6
        '''
        self.is_valid_channel(channel)
        if detector not in TRACE_DETECTORS:
            raise ValueError('%s is not a valid detector type' % detector)
        logging.info(__name__ +
                     ' setting the detector to {} for channel {}'.format(detector,
                                                                         channel))
        self.visa_handle.write('DET:TRAC{} {}'.format(channel, detector))

    def get_trace_1(self):
        '''
        Reads the style of trace 1
            Output:
                values (list) : [Display, Update, Type, Detector] ON = 1 OFF =2
        '''
        logging.info(__name__ + ' Reading state of trace 1')
        return ['Disp: ' + self.visa_handle.query('TRAC1:DISP?'),
                'Upd: ' + self.visa_handle.query('TRAC1:UPD?'),
                'Type: ' + self.visa_handle.query('TRAC1:TYPE?'),
                'Det: ' + self.visa_handle.query('DET:TRAC1?')]

    def get_trace_2(self):
        '''
        Reads the style of trace 2
            Output:
                values (list) : [Display, Update, Type, Detector] ON = 1 OFF =2
        '''
        logging.info(__name__ + ' Reading state of trace 2')
        return ['Disp: ' + self.visa_handle.query('TRAC2:DISP?'),
                'Upd: ' + self.visa_handle.query('TRAC2:UPD?'),
                'Type: ' + self.visa_handle.query('TRAC2:TYPE?'),
                'Det: ' + self.visa_handle.query('DET:TRAC2?')]

    def get_trace_3(self):
        '''
        Reads the style of trace 3
            Output:
                values (list) : [Display, Update, Type, Detector] ON = 1 OFF =2
        '''
        logging.info(__name__ + ' Reading state of trace 3')
        return ['Disp: ' + self.visa_handle.query('TRAC3:DISP?'),
                'Upd: ' + self.visa_handle.query('TRAC3:UPD?'),
                'Type: ' + self.visa_handle.query('TRAC3:TYPE?'),
                'Det: ' + self.visa_handle.query('DET:TRAC3?')]

    def get_trace_4(self):
        '''
        Reads the style of trace 4
            Output:
                values (list) : [Display, Update, Type, Detector] ON = 1 OFF =2
        '''
        logging.info(__name__ + ' Reading state of trace 4')
        return ['Disp: ' + self.visa_handle.query('TRAC4:DISP?'),
                'Upd: ' + self.visa_handle.query('TRAC4:UPD?'),
                'Type: ' + self.visa_handle.query('TRAC4:TYPE?'),
                'Det: ' + self.visa_handle.query('DET:TRAC4?')]

    def get_trace_5(self):
        '''
        Reads the style of trace 5
            Output:
                values (list) : [Display, Update, Type, Detector] ON = 1 OFF =2
        '''
        logging.info(__name__ + ' Reading state of trace 5')
        return ['Disp: ' + self.visa_handle.query('TRAC5:DISP?'),
                'Upd: ' + self.visa_handle.query('TRAC5:UPD?'),
                'Type: ' + self.visa_handle.query('TRAC5:TYPE?'),
                'Det: ' + self.visa_handle.query('DET:TRAC5?')]

    def get_trace_6(self):
        '''
        Reads the style of trace 6
            Output:
                values (list) : [Display, Update, Type, Detector] ON = 1 OFF =2
        '''
        logging.info(__name__ + ' Reading state of trace 6')
        return ['Disp: ' + self.visa_handle.query('TRAC6:DISP?'),
                'Upd: ' + self.visa_handle.query('TRAC6:UPD?'),
                'Type: ' + self.visa_handle.query('TRAC6:TYPE?'),
                'Det: ' + self.visa_handle.query('DET:TRAC6?')]

    def get_frequency_center(self):
        '''
        Reads the frequency center
            Output:
                frequency_center (float) : center frequency in Hz
        '''
        warnings.warn("This function is deprecated, is is recommended to call frequency_center() directly",
                      DeprecationWarning)
        logging.info(__name__ + ' : Getting frequency center')
        return self.visa_handle.query('FREQ:CENT?')

    def set_frequency_center(self, frequency):
        """
        Sets the center frequency of the graticle. The span is held constant,
        while the start and stop are changed.
            Input:
                frequency (float) : location of the center frequency in Hz
        """
        warnings.warn("This function is deprecated, is is recommended to call frequency_center(frequency) directly",
                      DeprecationWarning)
        logging.info(__name__ + ' : Setting frequency to %f' % frequency)
        return self.visa_handle.write('FREQ:CENT %f' % frequency)

    def get_frequency_start(self):
        """
        Reads the starting (left side) frequency of the graticle
            Output:
                frequency (float) : value of starting frequency in Hz
        """
        warnings.warn("This function is deprecated, is is recommended to call frequency_start() directly",
                      DeprecationWarning)
        logging.info(__name__ + ' : Reading start frequency')
        return self.visa_handle.query('FREQ:STAR?')

    def set_frequency_start(self, frequency):
        '''
        Sets the starting (left side) frequency of the graticle. The stop 
        frequency is held constant, while the center frequency and span will 
        change
            Input:
                frequency (float) : value of the starting frequency in Hz
        '''
        warnings.warn("This function is deprecated, is is recommended to call frequency_start(frequency) directly",
                      DeprecationWarning)
        logging.info(__name__ + ' : Setting start frequency to %f' % frequency)
        self.visa_handle.write('FREQ:STAR %f' % frequency)

    def get_frequency_stop(self):
        '''
        Reads the stop (right side) frequency of the graticle
            Output:
                frequency (float) : value ofstop frequency in Hz
        '''
        warnings.warn("This function is deprecated, is is recommended to call frequency_stop() directly",
                      DeprecationWarning)
        logging.info(__name__ + ' : Reading stop frequency')
        return self.visa_handle.query('FREQ:STOP?')

    def set_frequency_stop(self, frequency):
        '''
        Sets the stop (right side) frequency of the graticle. The start 
        frequency is held constant, while the center and span are changed.
            Input:
                frequency (float) : value fo stop frequency in Hz
        '''
        warnings.warn("This function is deprecated, is is recommended to call frequency_stop(frequency) directly",
                      DeprecationWarning)
        logging.info(__name__ + ' : Setting stop frequency to %f' % frequency)
        self.visa_handle.write('FREQ:STOP %f' % frequency)

    def get_frequency_span(self):
        '''
        Reads the span of the frequency sweep
            Output:
                frequency (float) : span of the sweep in Hz
        '''
        warnings.warn("This function is deprecated, is is recommended to call frequency_span() directly",
                      DeprecationWarning)
        logging.info(__name__ + ' : Reading the frequency span')
        return self.visa_handle.query('FREQ:SPAN?')

    def set_frequency_span(self, span):
        '''
        Sets the span of the frequency sweep. The center is held constant,
        while the start and stop are changed.
            Input:
                range (float) : 
        '''
        warnings.warn("This function is deprecated, is is recommended to call frequency_span(span) directly",
                      DeprecationWarning)
        logging.info(__name__ + ' : Setting the frequency span %f' % span)
        self.visa_handle.write('FREQ:SPAN %f' % span)

    def get_bandwidth_res(self):
        '''
        Reads the bandwidth resolution
            Output: 
                bandwidth (float) : resolution of bandwidth in Hz
        '''
        warnings.warn("This function is deprecated, is is recommended to call bandwidth_res() directly",
                      DeprecationWarning)
        logging.info(__name__ + ' : Reading the bandwitdth resolution')
        return self.visa_handle.query('BAND?')

    def set_bandwidth_res(self, resolution):
        '''
        Sets the resolution of the bandwidth
        Note:Only certain discrete resolution bandwidths are available. 
        The available bandwidths are dependent on the Filter Type or the EMC 
        Standard. If an unavailable bandwidth is entered with the numeric 
        keypad, the closest available bandwidth is selected.
            Input:
                resolution (float) : resolution of bandwidth in Hz
        '''
        warnings.warn("This function is deprecated, is is recommended to call bandwidth_res(resolution) directly",
                      DeprecationWarning)
        logging.info(__name__ +
                     ' : Setting bandwidth resolution to %f' % resolution)
        self.visa_handle.write('BAND %f' % resolution)

    def get_bandwidth_res_auto(self):
        '''
        Reads the state of bandwidth coupling
            Output:
                state (int) : 0 = OFF, 1 = ON
        '''
        warnings.warn("This function is deprecated, is is recommended to call bandwidth_res_auto() directly",
                      DeprecationWarning)
        logging.info(__name__ + ' : Reading the state bandwidth coupling')
        return self.visa_handle.query('BAND:AUTO?')

    def set_bandwidth_res_auto(self, enable):
        '''
        Sets the state of bandwidth coupling
            Input:
                state (int) : 0 = OFF, 1 = ON
        '''
        warnings.warn("This function is deprecated, is is recommended to call bandwidth_res_auto(enable) directly",
                      DeprecationWarning)
        logging.info(__name__ +
                     ' : Setting the bandwidth coupling to %s' % enable)
        self.visa_handle.write('BAND:AUTO %s' % enable)

    def get_bandwidth_video(self):
        '''
        Reads the post-detection filter frequency
            Output:
                frequency (float) : video bandwidth in Hz
        '''
        warnings.warn("This function is deprecated, is is recommended to call bandwidth_video() directly",
                      DeprecationWarning)
        logging.info(__name__ + ' : Reading the video bandwidth')
        return self.visa_handle.query('BAND:VID?')

    def set_bandwidth_video(self, frequency):
        '''
        Sets the video bandwidth frequency
            Input:
                frequency (float) : video band width in Hz (from 1 Hz to 8MHz)
                (set to 50 MHz for wide open video filter)
        '''
        warnings.warn("This function is deprecated, is is recommended to call bandwidth_video(frequency) directly",
                      DeprecationWarning)
        if frequency > 8000000 and frequency < 50000000:
            frequency = 8000000
        logging.info(__name__ +
                     ' : Setting the video bandwidth to %f' % frequency)
        self.visa_handle.write('BAND:VID %f' % frequency)

    def get_bandwidth_video_auto(self):
        '''
        Reads the state of the video bandwith coupling
            Output:
                state (int) : 0 = OFF, 1= ON
        '''
        warnings.warn("This function is deprecated, is is recommended to call bandwidth_video_auto() directly",
                      DeprecationWarning)
        logging.info(__name__ + ' : Reading the state of the video bandwidth')
        return self.visa_handle.query('BAND:VID:AUTO?')

    def set_bandwidth_video_auto(self, enable):
        '''
        Sets the video bandwidth coupling to auto
            Input:
                enable (int) : 0=OFF, 1=ON
        '''
        warnings.warn("This function is deprecated, is is recommended to call bandwidth_video_auto(enable) directly",
                      DeprecationWarning)
        logging.info(__name__ + ' : Setting the VBW coupling to %s' % enable)
        self.visa_handle.write('BAND:VID:AUTO %s' % enable)

    def get_trigger_source(self):
        '''
        Reads the source of the trigger
            Output:
                source (string) : source of triggering
        '''
        warnings.warn("This function is deprecated, is is recommended to call trigger_source() directly",
                      DeprecationWarning)
        logging.info(__name__ + ' : Reading the triggering source')
        return self.visa_handle.query('TRIG:SOUR?')

    def set_trigger_source(self, source):
        '''
        Sets the source of the trigger
            Input:
                source (string) : the source to be used as the trigger
        '''
        warnings.warn("This function is deprecated, is is recommended to call trigger_source(source) directly",
                      DeprecationWarning)
        logging.info(__name__ +
                     ' : Setting the source of the trigger to %s' % source)
        self.visa_handle.write('TRIG:SOUR %s' % source)

    def trace_on(self, channel=1):
        '''
        Sets the trace mode to ON (ie Display on, Update on)
            Input:
                channel (int) : channel to alter [1-6]
        '''
        logging.info(__name__ + ' Setting channel %s to on' % channel)
        self.visa_handle.write('TRAC%s:UPD 1' % channel)
        self.visa_handle.write('TRAC%s:DISP 1' % channel)

    def trace_view(self, channel=1):
        '''
        Sets the trace mode to VIEW (ie Display on, Update off)
            Input:
                channel (int) : channel to alter [1-6]
        '''
        logging.info(__name__ + ' Setting channel %s to view' % channel)
        self.visa_handle.write('TRAC%s:UPD 0' % channel)
        self.visa_handle.write('TRAC%s:DISP 1' % channel)

    def trace_blank(self, channel=1):
        '''
        Sets the trace mode to BLANK (ie Display off, Update off)
            Input:
                channel (int) : channel to alter [1-6]
        '''
        logging.info(__name__ + ' Setting channel %s to blank' % channel)
        self.visa_handle.write('TRAC%s:UPD 0' % channel)
        self.visa_handle.write('TRAC%s:DISP 0' % channel)

    def trace_background(self, channel=1):
        '''
        Sets the trace mode to BACKGROUND (ie Display off, Update on)
            Input:
                channel (int) : channel to alter [1-6]
        '''
        logging.info(__name__ + ' Setting channel %s to background' % channel)
        self.visa_handle.write('TRAC%s:UPD 1' % channel)
        self.visa_handle.write('TRAC%s:DISP 0' % channel)

    def clear_trace(self, *trace_channel):
        '''
        Clears the specified trace without effecting state of function or 
        variable
            Input:
                trace_channel (int) : 1|2|3|4|5|6 channel to be cleared
        '''
        logging.info(__name__ + ' Clearing the trace')
        for i in trace_channel:
            self.visa_handle.write('TRAC:CLE TRACE%s' % i)

    def get_sweep_time(self):
        '''
        Reads the sweep time of the current frequency span
            Output:
                time (float) : in seconds
        '''
        warnings.warn("This function is deprecated, is is recommended to call sweep_time() directly",
                      DeprecationWarning)
        logging.info(__name__ + ' Reading sweep time')
        return self.visa_handle.query('SWE:TIME?')

    def set_sweep_time(self, time):
        '''
        Sets the sweep time of the current frequency span
            Input:
                time (float): in seconds
        '''
        warnings.warn("This function is deprecated, is is recommended to call sweep_time(time) directly",
                      DeprecationWarning)
        logging.info(__name__ + ' Setting sweep time to %s' % time)
        self.visa_handle.write('SWE:TIME %s' % time)

    def get_sweep_time_auto(self):
        '''
        Reads the status the sweep time auto mode
            Output:
                auto enabled (int) : OFF = 0, ON = 1
        '''
        warnings.warn("This function is deprecated, is is recommended to call sweep_time_auto() directly",
                      DeprecationWarning)
        logging.info(__name__ + ' Reading sweep time auto state')
        return self.visa_handle.query('SWE:TIME:AUTO?')

    def set_sweep_time_auto(self, enable):
        '''
        Sets the sweep time auto mode
            Input: 
                enable (int) : OFF = 0, ON = 1
        '''
        warnings.warn("This function is deprecated, is is recommended to call sweep_time_auto(enable) directly",
                      DeprecationWarning)
        logging.info(__name__ + ' Setting the sweep time auto mode %s' % enable)
        self.visa_handle.write('SWE:TIME:AUTO %s' % enable)

    def get_sweep_time_auto_rules(self):
        '''
        Reads the rules for the auto sweep function
            Output:
                rule (string)
        '''
        warnings.warn("This function is deprecated, is is recommended to call sweep_time_auto_rules() directly",
                      DeprecationWarning)
        logging.info(__name__ + ' Reading the sweep auto rules')
        return self.visa_handle.query('SWE:TIME:AUTO:RUL?')

    def set_sweep_time_auto_rules(self, rule):
        '''
        Sets the rule for the sweep auto time
            Input (string):
                rule (string):
                    ['norm', 'normal', 'accuracy', 'acc', 'sres', 'sresponse']
        '''
        warnings.warn("This function is deprecated, is is recommended to call sweep_time_auto_rules(rule) directly",
                      DeprecationWarning)
        logging.info(__name__ + ' Setting the sweep time auto rule to %s'
                     % rule)
        self.visa_handle('SWE:TIME:AUTO:RUL %s' % rule)

    # Xi: add the following two set/get parameter method on 2017-07-16 for AWG calibration   
    def get_mode(self):
        '''
        Read the current mode of the instrument        
        
        '''
        warnings.warn("This function is deprecated, is is recommended to call mode() directly",
                      DeprecationWarning)
        logging.debug(__name__ + ' : get mode')
        return str(self.visa_handle.query(':INSTRUMENT?'))

    def set_mode(self, modename):
        '''
        Set the mode of the instrument
        '''
        warnings.warn("This function is deprecated, is is recommended to call mode(modename) directly",
                      DeprecationWarning)
        logging.debug(__name__ + ' : set mode to %s' % modename)
        self.visa_handle.write(':INSTRUMENT %s' % modename)


    def reset(self):
        '''
        Resets the device to default state
        '''
        logging.info(__name__ + ' : resetting the device')
        self.visa_handle.write('*RST')

    def send_command(self, command):
        '''
        Sends a command to the instrument
            Input:
                command (string) : command to be sent (see manual for commands)
        '''
        self.visa_handle.write(command)

    def retrieve_data(self, query):
        '''
        Reads data from the instrument
            Input:
                query (string) : command to be sent (see manual for commands)
            Output:
                varies depending on command sent
        '''
        return self.visa_handle.query(query)

    def is_valid_channel(self, channel):
        min_chan_val = 1
        max_chan_val = 6
        if channel < min_chan_val or channel > max_chan_val:
            raise ValueError('channel must be between {} and {}'.format(min_chan_val, max_chan_val))
        else:
            return channel

    def marker_Y_value(self, markernum=1):
        '''
        Get the Y value for the No. markernum marker
        '''
        logging.info(__name__ + ' : get Y value of %i marker' % markernum)
        mode = self.get_mode()
        if mode == 'BASIC':
            return float(self.visa_handle.query(':CALCULATE:SPECTRUM:MARKER%i:Y? ' % markernum))
        elif mode == 'SA':
            return float(self.visa_handle.query(':CALCULATE:MARKER%i:Y? ' % markernum))

    def marker_X_value(self, markernum=1):
        '''
        Get the Y value for the No. markernum marker
        '''
        logging.info(__name__ + ' : get X value of %i marker' % markernum)
        mode = self.get_mode()
        if mode == 'BASIC':
            return float(self.visa_handle.query(':CALCULATE:SPECTRUM:MARKER%i:X? ' % markernum))
        elif mode == 'SA':
            return float(self.visa_handle.query(':CALCULATE:MARKER%i:X? ' % markernum))

    def new_peak(self, markernum=1):
        '''
        Set the chosen marker on a peak
        '''
        logging.info(__name__ + ' : set the %i marker on a peak' % markernum)
        mode = self.get_mode()
        if mode == 'BASIC':
            self.visa_handle.write(':CALCULATE:SPECTRUM:MARKER%i:MAXIMUM' % markernum)
        elif mode == 'SA':
            self.visa_handle.write(':CALCULATE:MARKER%i:MAXIMUM' % markernum)

    def next_peak(self, markernum=1):
        '''
        Set the chosen marker to the next peak
        '''
        logging.info(__name__ + ' : set the %i marker to the next peak' % markernum)
        mode = self.get_mode()
        if mode == 'BASIC':
            self.visa_handle.write(':CALCULATE:SPECTRUM:MARKER%i:MAXIMUM:NEXT' % markernum)
        elif mode == 'SA':
            self.visa_handle.write(':CALCULATE:MARKER%i:MAXIMUM:NEXT' % markernum)

    def next_peak_right(self, markernum=1):
        '''
        Set the chosen marker to the next peak right
        '''
        logging.info(__name__ + ' : set the %i marker to the next peak right' % markernum)
        mode = self.get_mode()
        if mode == 'BASIC':
            self.visa_handle.write(':CALCULATE:SPECTRUM:MARKER%i:MAXIMUM:RIGHT' % markernum)
        elif mode == 'SA':
            self.visa_handle.write(':CALCULATE:MARKER%i:MAXIMUM:RIGHT' % markernum)

    def next_peak_left(self, markernum=1):
        '''
        Set the chosen marker to the next peak
        '''
        logging.info(__name__ + ' : set the %i marker to the next peak left' % markernum)
        mode = self.get_mode()
        if mode == 'BASIC':
            self.visa_handle.write(':CALCULATE:SPECTRUM:MARKER%i:MAXIMUM:LEFT' % markernum)
        elif mode == 'SA':
            self.visa_handle.write(':CALCULATE:MARKER%i:MAXIMUM:LEFT' % markernum)

    def marker_off(self, markernum=1):
        '''
        Turn off the chosen marker
        '''
        logging.info(__name__ + ' : turn off the %i marker' % markernum)
        mode = self.get_mode()
        if mode == 'BASIC':
            self.visa_handle.write(':CALCULATE:SPECTRUM:MARKER%i:MODE OFF' % markernum)
        elif mode == 'SA':
            self.visa_handle.write(':CALCULATE:MARKER%i:MODE OFF' % markernum)

    def marker_to_center(self, markernum=1):
        '''
        Set the marker frequency to be the center frequency
        '''
        logging.info(__name__ + ' : turn off the %i marker' % markernum)
        mode = self.get_mode()
        if mode == 'BASIC':
            self.visa_handle.write(':CALCULATE:SPECTRUM:MARKER%i:CENTER' % markernum)
        elif mode == 'SA':
            self.visa_handle.write(':CALCULATE:MARKER%i:CENTER' % markernum)

if __name__ == "__main__":
    MXA = Keysight_N9020A("MXA", address='TCPIP0::192.168.137.101::INSTR')