# -*- coding: utf-8 -*-
"""
Created on Tue Dec  8 16:31:55 2020

@author: Ryan Kaufman

purpose: add additional functionality to PNA driver without adding bulk to base driver
"""
import matplotlib.pyplot as plt
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
    # pVNA = Hat_P9374A("pVNA", address = "TCPIP0::hatlab-msmt3::hislip0::INSTR", timeout = 3)
    pVNA = Hat_P9374A("pVNA", address = "TCPIP0::DESKTOP-F8SGIH5::hislip0::INSTR", timeout = 3)

    from matplotlib import pyplot as plt

    plt.close("all")
    pVNA.num_points(int(1241*2.2))
    trace = pVNA.gettrace()
    plt.figure()
    plt.plot(trace[0])
    plt.plot(trace[1])

    # fdata =  pVNA.getfdata()
    # plt.figure()
    # plt.plot(fdata, trace[0])
    # plt.plot(fdata, trace[1])

    # low level debugging....
    # pVNA.visa_handle.write(':CALC1:DATA? FDATA')
    # rd_raw_ = pVNA.visa_handle._read_raw()
    # rd_raw = bytes(rd_raw_)
    # rd = rd_raw.decode("latin1")
    # data = np.zeros(len(rd.split(',')))+1000
    # for i, dd in enumerate(np.array(rd.split(','))):
    #     try:
    #         data[i] = dd.astype(float)
    #     except Exception as e:
    #         print("!!!!!!!!!!!!!", i, dd, e)
    # plt.figure()
    # plt.plot(data.reshape(2, -1)[0])
    # plt.plot(data.reshape(2, -1)[1])
    # print(pVNA.visa_handle.chunk_size)

