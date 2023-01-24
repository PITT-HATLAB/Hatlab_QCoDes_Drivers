# -*- coding: utf-8 -*-
"""
@author: Chao Zhou

A simple driver for MiniCircuits RC-8SPDT-A18 switch matrix to be used with QCoDes,
transferred from the one written by Xi Cao.


"""

# Switch control, make switch as an instrument
import logging
from typing import Union
from qcodes import Instrument
import logging
from functools import partial

from urllib.request import urlopen

class MiniCircuits_SwitchMatrix(Instrument):
    def __init__(self, name, address, reset=False, **kwargs):
        '''
        Initializes the Mini_Circuits switch, and communicates with the wrapper.

        Input:
          name (string)    : name of the instrument
          address (string) : http address
          reset (bool)     : resets to default values, default=False
        '''
        super().__init__(name, **kwargs)
        logging.info(__name__ + ' : Initializing MiniCircuits RC-8SPDT-A18')
        self._address = address

        self.add_parameter('portvalue',
                           label='portvalue',
                           get_cmd=self.do_get_portvalue,
                           set_cmd=partial(self.set_switch, "P"))


        if reset:
            self.reset()

    def set_switch(self, chanel:str, state: Union[int, str]):
        '''
        :param chanel: switch 'A' through 'H' or 'P' if you want to control all the gates at same time
        :param state: 0 or 1 to choose output. 0=1 (green), 1=2 (red)
        '''
        state = str(state)
        logging.info(__name__ + ' : Set switch%s' % chanel +' to state %s' % state)
        if chanel != 'P':
            ret = urlopen(self._address + "/SET" + chanel + "=" + state)
        else:
            if (len(state)) != 8:
                print(len(state))
                raise Exception("Wrong input length!")
            newstate = 0
            for x in range(0,len(state)):
                if (int(state[x]) != 0) & (int(state[x]) != 1):
                    raise Exception("Wrong input value at %ith" % x + " switch!")
                else:
                    newstate += int(state[x])*(2**x)

            ret = urlopen(self._address + "/SETP" + "=" + str(newstate))

        self.get('portvalue')

    def do_get_portvalue(self):
        logging.debug(__name__+' : get portvalue')
        ret = urlopen(self._address + "/SWPORT?" )
        result = ret.readlines()[0]
        result = int(result)
        result = format(result,'08b')
        result = result[::-1]
        return result

    def reset(self):
        self.set_switch("P", "0" * 8)

if __name__ == "__main__":
        SWT1 = MiniCircuits_SwitchMatrix('SWT1', address='http://192.168.137.201')
        
        
        
        
        
        
        
        
        
        
        