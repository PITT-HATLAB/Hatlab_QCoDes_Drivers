# -*- coding: utf-8 -*-
"""
Created on Thu Oct 28 2021

@author: Chao


Driver for SignalCore SC5413A to be used with QCoDes.
"""
import ctypes as ct
import logging
from typing import Any, Dict, Optional, List

import numpy as np

from qcodes import Instrument
from qcodes.utils.validators import Numbers, Enum, Lists, Ints, MultiType, Bool
from Hatlab_QCoDes_Drivers import DLLPATH


class deviceInfo_t(ct.Structure):
    _fields_ = [("productSerialNumber", ct.c_uint),
                ("rfModuleSerialNumber", ct.c_uint),
                ("firmwareRevision", ct.c_float),
                ("hardwareRevision", ct.c_float),
                ("calDate", ct.c_uint),
                ("manDate", ct.c_uint)
                ]


class deviceStatus_t(ct.Structure):
    _fields_ = [("rfAmpEnable", ct.c_bool),
                ("rfPath", ct.c_bool),
                ("loEnable", ct.c_bool),
                ("deviceAccess", ct.c_bool)
                ]


class RfParams_t(ct.Structure):
    _fields_ = [("frequency", ct.c_ulonglong),
                ("atten0", ct.c_char),
                ("atten1", ct.c_char),
                ("atten2", ct.c_char),
                ("atten3", ct.c_char),
                ("rfFilter", ct.c_char),
                ("loFilter", ct.c_char),
                ("offsetDacI", ct.c_ushort),
                ("offsetDacQ", ct.c_ushort),
                ("linearDacI", ct.c_ushort),
                ("linearDacQ", ct.c_ushort)
                ]

RFPathMap = {"main": 0, "axu": 1}
FilterMap = {400: 0, 500: 1, 650: 2, 1000: 3, 1400: 4, 2000: 5, 2825: 6, 3800: 7, 6000: 8}
FilterMap_inv = {v: k for k, v in FilterMap.items()}

def LinDacMap(linVoltage: float) -> int:
    return int(16383 * linVoltage / 5)

def LinDacMap_inv(linDAC: int) -> float:
    return np.round(linDAC / 16383 * 5, 4)

def OffsetDacMap(offsetVoltage: float) -> int:
    return int(16383 * (offsetVoltage + 0.05) / 0.1)

def OffsetDacMap_inv(offsetDAC: int) -> float:
    return np.round(offsetDAC / 16383 * 0.1 - 0.05, 7)


class SignalCore_SC5413A(Instrument):
    def __init__(self, name: str, serial_number: str, dll=None, debug=False, initialize=False, **kwargs: Any):
        super().__init__(name, **kwargs)
        logging.info(__name__ + f' : Initializing instrument SignalCore modulator {serial_number}')
        if dll is not None:
            self._dll = ct.CDLL(dll)
        else:
            self._dll = ct.CDLL(DLLPATH + '//sc5413a.dll')  # access dll file

        self._serial_number = ct.c_char_p(bytes(serial_number, 'utf-8'))
        if debug:
            print(self._dll)

        self._dll.sc5413a_OpenDevice.restype = ct.c_ulonglong  # the handle number is actually 64-bit unsigned, not int as defualt. fk sigcore

        self.add_parameter('frequency',
                           label='frequency',  # no get command for this value, not provided in dll
                           get_cmd=self.do_get_frequency,
                           get_parser=int,
                           set_cmd=self.do_set_frequency,
                           set_parser=int,
                           docstring="change the output frequency for auto filtering, the manual filter setting will be overwrite",
                           vals=Numbers(min_value=400e6, max_value=6e9))

        self.add_parameter('RF_filter',
                           label='RF_filter',
                           get_cmd=self.do_get_RF_filter,
                           get_parser=int,
                           set_cmd=self.do_set_RF_filter,
                           set_parser=int,
                           docstring="filter on the RF port, the automatic filtering setting based on frequency will be overwrite",
                           vals=Enum(*list(FilterMap.keys())))

        self.add_parameter('LO_filter',
                           label='LO_filter',
                           get_cmd=self.do_get_LO_filter,
                           get_parser=int,
                           set_cmd=self.do_set_LO_filter,
                           set_parser=int,
                           docstring="filter on the LO port, the automatic filtering setting based on frequency will be overwrite",
                           vals=Enum(*list(FilterMap.keys())))

        self.add_parameter('attenuation',
                           label='attenuation',
                           get_cmd=self.do_get_attenuation,
                           get_parser= list,
                           set_cmd=self.do_set_attenuation,
                           set_parser= list,
                           docstring="list of attenuation values for internal attenuators 0-3 ",
                           vals=Lists(Ints(min_value=0, max_value=31)))

        self.add_parameter('DC_offset',
                           label='DC_offset',
                           get_cmd=self.do_get_DC_offset,
                           get_parser= list,
                           set_cmd=self.do_set_DC_offset,
                           set_parser= list,
                           docstring="list of DC offsets for channel I/Q ",
                           vals=Lists(Numbers(min_value=-0.05, max_value=0.05)))

        self.add_parameter('linearity_voltage',
                           label='linearity_voltage',
                           get_cmd=self.do_get_linearity_voltage,
                           get_parser= list,
                           set_cmd=self.do_set_linearity_voltage,
                           set_parser= list,
                           docstring="list of linearity voltages for channel I/Q ",
                           vals=Lists(Numbers(min_value=0, max_value=5)))

        self.add_parameter('amplifier_enable',
                           label='amplifier_enable',
                           get_cmd=self.do_get_rf_amplifier_enable,
                           get_parser= int,
                           set_cmd=self.do_set_rf_amplifier_enable,
                           set_parser= int,
                           docstring="enable amplifier on RF port",
                           vals=MultiType(Bool(), Enum(0,1)))

        self.add_parameter('rf_path',
                           label='rf_path',
                           get_cmd=self.do_get_rf_path,
                           set_cmd=self.do_set_rf_path,
                           docstring="0 for main, 1 for aux",
                           vals=MultiType(Enum("main","aux", 0, 1)))

        self.add_parameter('LO_out',
                           label='LO_out',
                           get_cmd=self.do_get_LO_out,
                           get_parser=int,
                           set_cmd=self.do_set_LO_out,
                           set_parser=int,
                           docstring="0 disables the LO output, 1 Enables it for common LO drive in phase coherent "
                                     "application where more than one demodulator/modulator is used.",
                           vals=MultiType(Bool(), Enum(0,1)))

        self.add_parameter('temperature',
                           label='temperature',
                           get_cmd=self.do_get_temperature)

        self.get_idn()
        if initialize:
            self.attenuation([0,0,0,0])
            self.DC_offset([0, 0])
            self.linearity_voltage([1.2, 1.2])
            self.amplifier_enable(0)
            self.rf_path(0)



    def activate_device_control(self):
        # activate device control, get device handle
        self._handle = ct.c_void_p(self._dll.sc5413a_OpenDevice(self._serial_number, 'utf-8'))
        if self._handle.value < 0:
            raise TypeError("SC5413A connection error, check serial number")

    def close_device(self):
        self._dll.sc5413a_CloseDevice(self._handle)

    def get_idn(self) -> Dict[str, Optional[str]]:
        logging.info(__name__ + " : Getting device info")
        self.activate_device_control()
        device_info = deviceInfo_t(0, 0, 0, 0, 0, 0)
        self._dll.sc5413a_GetDeviceInfo(self._handle, ct.byref(device_info))
        self._device_info = device_info
        self.close_device()

        def date_decode(date_int: int):
            date_str = f"{date_int:032b}"
            yr = f"20{int(date_str[:8], 2)}"
            month = f"{int(date_str[8:16], 2)}"
            day = f"{int(date_str[16:24], 2)}"
            return f"{month}/{day}/{yr}"

        IDN: Dict[str, Optional[str]] = {
            'vendor': "SignalCore",
            'model': "SC5413A",
            'serial_number': hex(device_info.productSerialNumber)[2:],
            'RF_module_serial_number': hex(device_info.rfModuleSerialNumber)[2:],
            'firmware_revision': device_info.firmwareRevision,
            'hardware_revision': device_info.hardwareRevision,
            'manufacture_date': date_decode(device_info.manDate),
            'calibration_date': date_decode(device_info.calDate),
        }
        return IDN

    def get_device_status(self):
        self.activate_device_control()
        status_c = deviceStatus_t(0, 0, 0, 0)
        self._dll.sc5413a_GetDeviceStatus(self._handle, ct.byref(status_c))
        self.close_device()
        status = {"rfAmpEnable": status_c.rfAmpEnable}
        status["loEnable"] = status_c.loEnable
        status["deviceAccess"] = status_c.deviceAccess
        status["rfPath"] = "aux" if status_c.rfPath else "main"
        return status


    def get_RF_parameters(self):
        self.activate_device_control()
        rfParams_c = RfParams_t(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        self._dll.sc5413a_FetchRfParams(self._handle, ct.byref(rfParams_c))
        self.close_device()
        rfParams = {"frequency": rfParams_c.frequency}
        for i in range(4):  # decode attenuation values
            rfParams[f"atten{i}"] = int.from_bytes(rfParams_c.__getattribute__(f"atten{i}"), "big")
        rfParams["rfFilter"] = FilterMap_inv[int.from_bytes(rfParams_c.rfFilter, "big")]  # decode rf filter cutoff value
        rfParams["loFilter"] = FilterMap_inv[int.from_bytes(rfParams_c.loFilter, "big")]  # decode lo filter cutoff value
        rfParams["offsetValueI"] = OffsetDacMap_inv(rfParams_c.offsetDacI) # decode DC offset values
        rfParams["offsetValueQ"] = OffsetDacMap_inv(rfParams_c.offsetDacQ)
        rfParams["linearValueI"] = LinDacMap_inv(rfParams_c.linearDacI) # decode linearity voltage values
        rfParams["linearValueQ"] = LinDacMap_inv(rfParams_c.linearDacQ)
        return rfParams

    def do_set_frequency(self, freq):
        logging.info(__name__ + ' : Setting frequency for filtering to %s' % freq)
        c_freq = ct.c_ulonglong(freq)
        self.activate_device_control()
        completed = self._dll.sc5413a_SetFrequency(self._handle, c_freq)
        self.close_device()
        return completed

    def do_get_frequency(self):
        rfParams = self.get_RF_parameters()
        return rfParams["frequency"]

    def do_set_RF_filter(self, cutoffFreq):
        logging.info(__name__ + f' : Setting RF filter cutoff frequency to {cutoffFreq}')
        c_freq_sel = ct.c_char(FilterMap[cutoffFreq])
        self.activate_device_control()
        completed = self._dll.sc5413a_SetRfFilter(self._handle, c_freq_sel)
        self.close_device()
        return completed

    def do_get_RF_filter(self):
        rfParams = self.get_RF_parameters()
        return rfParams["rfFilter"]

    def do_set_LO_filter(self, cutoffFreq):
        logging.info(__name__ + f' : Setting LO filter cutoff frequency to {cutoffFreq}')
        c_freq_sel = ct.c_char(FilterMap[cutoffFreq])
        self.activate_device_control()
        completed = self._dll.sc5413a_SetLoFilter(self._handle, c_freq_sel)
        self.close_device()
        return completed

    def do_get_LO_filter(self):
        rfParams = self.get_RF_parameters()
        return rfParams["loFilter"]

    def do_set_attenuation(self, attenuations: List[int]):
        if len(attenuations) != 4:
            raise ValueError("list of attenuation values must be length 4")
        logging.info(__name__ + f' : Setting attenuators 0-3 to {attenuations}')
        self.activate_device_control()
        for i, atten in enumerate(attenuations):
            err = self._dll.sc5413a_SetRfAttenuation(self._handle, ct.c_char(i), ct.c_char(atten))
        self.close_device()
        return err

    def do_get_attenuation(self):
        rfParams = self.get_RF_parameters()
        attens = [rfParams[f"atten{i}"] for i in range(4)]
        return attens

    def do_set_DC_offset(self, offsetIQ: List[float]):
        if len(offsetIQ) != 2:
            raise ValueError("list of DC offset values must be length 2 ([I,Q])")
        logging.info(__name__ + f' : Setting DC_offset I,Q to {offsetIQ}')
        self.activate_device_control()
        for i, offset in enumerate(offsetIQ):
            offset_DAC = OffsetDacMap(offset)
            err = self._dll.sc5413a_SetDcOffsetDac(self._handle, ct.c_char(i), ct.c_ushort(offset_DAC))
        self.close_device()
        return err

    def do_get_DC_offset(self):
        rfParams = self.get_RF_parameters()
        offsetIQ = [rfParams["offsetValueI"], rfParams["offsetValueQ"]]
        return offsetIQ

    def do_set_linearity_voltage(self, lvIQ: List[float]):
        if len(lvIQ) != 2:
            raise ValueError("list of linearity voltage values must be length 2 ([I,Q])")
        logging.info(__name__ + f' : Setting linearity voltage I,Q to {lvIQ}')
        self.activate_device_control()
        for i, vol in enumerate(lvIQ):
            lv_DAC = LinDacMap(vol)
            err = self._dll.sc5413a_SetLinearityDac(self._handle, ct.c_char(i), ct.c_ushort(lv_DAC))
        self.close_device()
        return err

    def do_get_linearity_voltage(self):
        rfParams = self.get_RF_parameters()
        offsetIQ = [rfParams["linearValueI"], rfParams["linearValueQ"]]
        return offsetIQ

    def do_set_rf_amplifier_enable(self, enable):
        self.activate_device_control()
        err = self._dll.sc5413a_SetRfAmplifier(self._handle, ct.c_bool(enable))
        self.close_device()
        return err

    def do_get_rf_amplifier_enable(self):
        status = self.get_device_status()
        ampOn = status["rfAmpEnable"]
        return ampOn

    def do_set_rf_path(self, path):
        try:
            path = RFPathMap[path]
        except KeyError:
            pass
        self.activate_device_control()
        err = self._dll.sc5413a_SetRfPath(self._handle, ct.c_bool(path))
        self.close_device()
        return err

    def do_get_rf_path(self):
        status = self.get_device_status()
        path = status["rfPath"]
        return path

    def do_set_LO_out(self, enable):
        self.activate_device_control()
        err = self._dll.sc5413a_SetLoOut(self._handle, ct.c_bool(enable))
        self.close_device()
        return err

    def do_get_LO_out(self):
        status = self.get_device_status()
        loEnable = status["loEnable"]
        return loEnable

    def do_get_temperature(self):
        temp = ct.c_float()
        self.activate_device_control()
        self._dll.sc5413a_GetTemperature(self._handle, ct.byref(temp))
        self.close_device()
        return temp.value

if __name__ == "__main__":
    Mod1 = SignalCore_SC5413A("Mod1", "100022C6")
