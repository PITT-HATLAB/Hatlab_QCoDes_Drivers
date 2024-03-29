import logging
import time
from typing import Union
from qcodes import Instrument
import logging
from functools import partial
from qcodes.utils.validators import Enum, Lists, Ints, Arrays

from urllib.request import urlopen

"""
An example that shows the timeout issue of the server-client method 
"""

class dummy(Instrument):
    def __init__(self, name, address, reset=False, **kwargs):
        '''
        Initializes the Mini_Circuits switch, and communicates with the wrapper.

        Input:
          name (string)    : name of the instrument
          address (string) : http address
          reset (bool)     : resets to default values, default=False
        '''
        super().__init__(name, **kwargs)
        logging.info(__name__ + ' : Initializing')
        self._address = address
        self._test_val = 0
        self.add_parameter('test_val',
                           label='test_val',
                           get_cmd=self.do_get_test_val,
                           set_cmd=self.do_set_test_val,)

        self.add_parameter('list_val',
                           label='list_val',
                           vals=Lists(Ints()),
                           get_cmd=self.do_get_list_val,
                           set_cmd=self.do_set_list_val,)

        if reset:
            self.reset()

    def do_get_test_val(self):
        '''
        :param sw: switch 'A' through 'H' or 'P' if you want to control all the gates at same time
        :param state: 0 or 1 to choose output. 0=1 (green), 1=2 (red)
        '''
        time.sleep(10)
        return self._test_val

    def do_set_test_val(self, val):
        time.sleep(10)
        self._test_val = val

    def do_set_list_val(self, val):
        self._list_val = val

    def do_get_list_val(self):
        return  self._list_val

if __name__=="__main__":
    dd = dummy("dd", "1")
    dd.list_val([1,1,1])
    print(dd.list_val())