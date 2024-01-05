# -*- coding: utf-8 -*-
"""
@author: Chao Zhou

A simple driver for Keysight N5183B to be used with QCoDes, transferred from the one written by Erick Brindock.

The function is not complete yet.
"""
import logging
from typing import Any, Dict, Optional

from qcodes import VisaInstrument
from qcodes.utils.validators import Numbers, Enum



class Keysight_N5183B(VisaInstrument):
    OFF = 0
    ON = 1
    def __init__(self, name, address, reset=False, **kwargs):
        super().__init__(name, address, terminator='\n', **kwargs)
        logging.info(__name__+ ' : Initializing Keysight N5183B')
        self._address = address
        # Query the instrument to see what frequency range was purchased
        freq_dict = {'501': 1e9, '503': 3e9, '505': 6e9, '520': 20e9}
        max_freq = freq_dict[self.ask('*OPT?')[:3]]
        if '1EA' in self.ask_from_client('*OPT?'):
            max_pwr = 30
        else:
            max_pwr = 19
        self.connect_message()

        self.add_parameter('power',
                           label='Power',
                           get_cmd='SOUR:POW?',
                           get_parser=float,
                           set_cmd='SOUR:POW {:.2f}',
                           set_parser=float,
                           unit='dBm',
                           vals=Numbers(min_value=-20, max_value=max_pwr))


        self.add_parameter('frequency',
                           label='Frequency',
                           get_cmd='SOUR:FREQ?',
                           get_parser=float,
                           set_cmd='SOUR:FREQ {:.2f}',
                           set_parser=float,
                           unit='Hz',
                           vals=Numbers(min_value=9e3, max_value=max_freq))

        self.add_parameter('phase_offset',
                           label='Phase Offset',
                           get_cmd='SOUR:PHAS?',
                           get_parser=float,
                           set_cmd='SOUR:PHAS {:.2f}',
                           set_parser=float,
                           unit='rad'
                           )

        self.add_parameter('output_status',
                           get_cmd='OUTP:STAT?',
                           get_parser=int,
                           set_cmd='OUTP:STAT {}',
                           set_parser=int)

        self.add_parameter('reference_source',
                           get_cmd='ROSC:SOUR?',
                           set_cmd='ROSC:SOUR {}',
                           val_mapping={1: "EXT", 0: "INT"})


        self.add_parameter('alc_auto',
                           get_cmd='POW:ATT:AUTO?',
                           get_parser=int,
                           set_cmd='POW:ATT:AUTO {}',
                           set_parser=int,
                           val_mapping={'on': 1, 'off': 0})

        self.add_parameter('phase_adjust',
                           get_cmd='PHAS:ADJ?',
                           get_parser=float,
                           set_cmd='PHAS:ADJ? {}',
                           set_parser=float,
                           unit="deg",
                           vals=Numbers(min_value=-180, max_value=179))

        self.add_parameter('frequency_start',
                           get_cmd='FREQ:STAR?',
                           get_parser=float,
                           set_cmd='FREQ:STAR {:.2f}',
                           set_parser=float,
                           unit="Hz",
                           vals=Numbers(min_value=9e3, max_value=max_freq))

        self.add_parameter('frequency_stop',
                           get_cmd='FREQ:STOP?',
                           get_parser=float,
                           set_cmd='FREQ:STOP {:.2f}',
                           set_parser=float,
                           unit="Hz",
                           vals=Numbers(min_value=9e3, max_value=max_freq))

        self.add_parameter('power_start',
                           get_cmd='POW:STAR?',
                           get_parser=float,
                           set_cmd='POW:STAR {:.2f} dBm',
                           set_parser=float,
                           unit="dBm",
                           vals=Numbers(min_value=-20, max_value=30))

        self.add_parameter('power_stop',
                           get_cmd='POW:STOP?',
                           get_parser=float,
                           set_cmd='POW:STOP {:.2f}',
                           set_parser=float,
                           unit="dBm",
                           vals=Numbers(min_value=-20, max_value=30))

        self.add_parameter('sweep_points',
                           get_cmd='SWE:POIN?',
                           get_parser=int,
                           set_cmd='SWE:POIN {}',
                           set_parser=int,
                           unit="pts",
                           vals=Numbers(min_value=2, max_value=65535))

        self.add_parameter('dwell_time',
                           get_cmd='SWE:DWEL?',
                           get_parser=float,
                           set_cmd='SWE:DWEL {}',
                           set_parser=float,
                           unit="sec",
                           vals=Numbers(min_value=100e-6, max_value=100))

        self.add_parameter('trigger_wait_time',
                           get_cmd='TRIG:TIM?',
                           get_parser=float,
                           set_cmd='TRIG:TIM {}',
                           set_parser=float,
                           unit="sec",
                           vals=Numbers(min_value=0, max_value=100))

        self.add_parameter('frequency_mode',
                           get_cmd='FREQ:MODE?',
                           get_parser=str,
                           set_cmd='FREQ:MODE {}',
                           set_parser=str,
                           vals=Enum('CW', 'FIX', 'LIST'))

        self.add_parameter('power_mode',
                           get_cmd='POW:MODE?',
                           get_parser=str,
                           set_cmd='POW:MODE {}',
                           set_parser=str,
                           vals=Enum('CW', 'FIX', 'LIST'))

        self.add_parameter('mod_status',
                           get_cmd='OUTP:MOD?',
                           get_parser=int,
                           set_cmd='OUTP:MOD {}',
                           set_parser=int)

    def get_idn(self) -> Dict[str, Optional[str]]:
        IDN_str = self.ask_raw('*IDN?')
        vendor, model, serial, firmware = map(str.strip, IDN_str.split(','))
        IDN: Dict[str, Optional[str]] = {
            'vendor': vendor, 'model': model,
            'serial': serial, 'firmware': firmware}
        return IDN

    def startSweep(self):
        self.write_raw('LIST:MODE AUTO')

    def stopSweep(self):
        self.write_raw('LIST:MODE MAN')

    def ask_from_client(self, cmd):
        return self.ask(cmd)

    def write_from_client(self, cmd):
        return self.write(cmd)



if __name__ == "__main__":
    test = Keysight_N5183B("test", 'TCPIP0::169.254.15.148::inst0::INSTR')
    test.power_start(-10)
    test.power_stop(0)
    test.power_mode("FIX")
    test.stopSweep()
