# -*- coding: utf-8 -*-
"""
@author: Chao Zhou

A simple driver for controlling multiple MiniCircuits RC-8SPDT-A18 switch matrices as one big matrix using QCoDes,
transferred from the one written by Xi Cao and Pinlei Lu.


"""

import logging
from typing import Union, List
from qcodes import Instrument
import logging
from Hatlab_QCoDes_Drivers.MiniCircuits_SwitchMatrix import MiniCircuits_SwitchMatrix

from urllib.request import urlopen

class MiniCircuits_SwitchMatrix_Multi(Instrument):
    def __init__(self, name:str, name_list:List[str], address_list:List[str], mode_dict:dict={}, reset=False, **kwargs):
        """
        :param name: name of all the switches as one instrument
        :param name_list: list of individual names of each switch matrix
        :param address_list: list of address
        :param mode_dict: dictionary that contains the preset modes
        :param reset:
        :param kwargs:
        """
        super().__init__(name, **kwargs)
        logging.info(__name__ + ' : Initializing MiniCircuits RC-8SPDT-A18')
        self._address_list = address_list
        self._mode_dict = mode_dict
        self.switch_dict: {str: MiniCircuits_SwitchMatrix} = {}
        for i, swt_name in enumerate(name_list):
            swt_ = MiniCircuits_SwitchMatrix(swt_name, address_list[i])
            setattr(self, swt_name, swt_)
            self.switch_dict[swt_name] = swt_

        self.add_parameter('portvalue_dict',
                           label='portvalue_dict',
                           get_cmd=self.do_get_portvalue_dict,
                           set_cmd=self.do_set_portvalue_dict)

        self.add_parameter('mode',
                           label='mode',
                           get_cmd=self.do_get_mode,
                           set_cmd=self.do_set_mode)
        if reset:
            self.reset()

    def do_get_portvalue_dict(self):
        port_value_dict = {}
        for swt_name, swt_ in self.switch_dict.items():
            port_value_dict[swt_name] = swt_.portvalue()
        return port_value_dict

    def do_set_portvalue_dict(self, port_value_dict:dict):
        for swt_name, port_value in port_value_dict:
            self.switch_dict[swt_name].set_switch("P", port_value)


    def do_get_mode(self):
        current_states = self.portvalue_dict()
        matched_modes = []
        for mode_name, mode in self._mode_dict.items():
            mode_match = True
            for i, (swt_name, portvalue_) in enumerate(current_states.items()):
                for j, s in enumerate(mode[i]):
                    if (s in ["0", "1"]) and (s != portvalue_[j]):
                        mode_match = False
                        break
            if mode_match:
                matched_modes.append(mode_name)
        return matched_modes


    def do_set_mode(self, mode_name):
        current_states = self.portvalue_dict()
        if mode_name in self._mode_dict:
            for i, (swt_name, swt_) in enumerate(self.switch_dict.items()):
                swt_.set_switch("P", self._create_new_mode_string(current_states[swt_name], self._mode_dict[mode_name][i]))
        else:
         print( 'Confucius say there is no such mode. Nothing has been changed.')


    def _create_new_mode_string(self, current_state, new_state):
        if len(current_state)  != len(new_state):
            raise ValueError("current_state and new_state must be the same length.")
        output = ""
        for i in range(len(new_state)):
            if (new_state[i] not in ["0", "1"]):
                output += current_state[i]
            else:
                output += new_state[i]
        return output

    def get_mode_options(self):
        return self._mode_dict

    def reset(self):
        for swt_ in self.switch_dict.values():
            swt_.reset()

if __name__ == "__main__":
    modes = {'2_IN': ['xxxxxxxx', 'xxxx00xx', 'xxxxxxxx'],
             '3_IN': ['xxxxxxxx', 'xxxx01xx', 'xxxxxxxx'],
             '12_IN': ['xxxxxxxx', 'xxxx1xx0', 'xxxxxxxx'],
             '18_IN': ['xxxxxxxx', 'xxxx1xx1', 'xxxxxxxx'],
             'A_Out': ['xxxxxxxx', '00xxxxxx', 'xxxxxxxx'],
             'B_Out': ['xxxxxxxx', '01xxxxxx', 'xxxxxxxx'],
             'H_Out': ['xxxxxxxx', '1x1xxxxx', 'xxxxxxxx'],
             'E_Out': ['xxxxxxxx', '1x0xxxxx', 'xxxxxxxx'],
             'VNAInOut': ['xxxxxxxx', 'xxx0xx0x', 'xxxxxxxx'],
             'PXIInOut': ['xxx1xxxx', 'xxx1xx1x', 'xxxxxxxx'],
             'Cav1In': ['01xxxxxx', 'xxxxxxxx', 'xxxxxxxx'],
             'Cav4In': ['11xxxxxx', 'xxxxxxxx', 'xxxxxxxx'],
             'Cav6In': ['x00xxxxx', 'xxxxxxxx', 'xxxxxxxx'],
             'SAQuCaIn': ['x010xxxx', 'xxxxxxxx', 'xxxxxxxx']
             }
    SWT = MiniCircuits_SwitchMatrix_Multi('SWT',name_list=["SWT1", "SWT2", "SWT3"],
                address_list=['http://169.254.254.251', 'http://169.254.254.249', 'http://169.254.254.252'],
                mode_dict= modes)
        
        
        
        
        
        
        
        
        
        
        