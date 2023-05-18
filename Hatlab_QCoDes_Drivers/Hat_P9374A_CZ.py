# -*- coding: utf-8 -*-
"""
Created on Tue Dec  8 16:31:55 2020

@author: Ryan Kaufman

purpose: add additional functionality to PNA driver without adding bulk to base driver
"""
from Hatlab_QCoDes_Drivers.Hat_P9374A import Hat_P9374A
import numpy as np
import time

try:
    import easygui
    EASYGUI = True
except ImportError:
    EASYGUI = False

class Hat_P9374A_CZ(Hat_P9374A):
    
    def __init__(self,name: str, address: str = None, **kwargs):
        if address == None:
            raise Exception('TCPIP Address needed')
        super().__init__(name, address, **kwargs)

    
    def gettrace(self):
        data = super().gettrace()
        data[1, :] = data[1, :] / np.pi * 180
        return data

if __name__=="__main__":
    pVNA = Hat_P9374A("pVNA", address = "TCPIP0::hatlab-msmt3::hislip0::INSTR", timeout = 3)
