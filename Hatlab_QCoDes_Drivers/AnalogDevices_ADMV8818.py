"""QCodes driver for Analog Devices digital controlled HPF + LPF EVAL-ADMV8818 board.

@author: Chao

This driver uses the remote control feature of the ACE software form Analog Devices to control the ADMV8818 eval board.

Required Package:
    pythonnet ("pip install pythonnet" or "conda install -c conda-forge pythonnet")


Setup:
    Before using this driver, the following steps must be done on the local computer:
    1. Download and install the ACE software and the ADMV8818 board support from the product page (https://www.analog.com/en/design-center/evaluation-hardware-and-software/evaluation-boards-kits/eval-admv8818.html#eb-documentation)
        To makes thing easier, use the default installation path.
    2. Enable ACE server.
        In the ACE software, go to Settings -> IPC Server. Check "Server enabled", and then add a port.
        The default port number is 2357, you can change the port number if you need to, just remember to change the IPC_port number in this driver or when you call this driver.
    3. Step 1-2 only needs to be done once on each PC. But everytime before you try to control the board using this driver,
        the ACE software must be started and kept running in the background (as the server).
        (No need to manually add the board in the software though, you should only need to start the software and leave it.)


Identify boards:
    If multiple boards are connected to one PC, each board must be identified by its hardware ID.
    So far I haven't found a relation between the serial number and the hardware ID of a board,
    so the only way to know the ID of a specific board is using the 'getHardwareIds' function.
    Note that the ID we use here is actually the ID of the SDP-S control board.


More device info:
    For more details about the ADMV8818 chip and the eval board, check the user manuals here
    https://www.analog.com/en/products/admv8818.html#product-overview
    and here
    https://www.analog.com/en/design-center/evaluation-hardware-and-software/evaluation-boards-kits/eval-admv8818.html#eb-overview
"""

import logging
from typing import Union
from qcodes import Instrument
from qcodes.utils.validators import Enum, Lists, Ints
import logging
import clr
import sys
import time
from typing import Dict, Optional

IPCPORT = "2357"
sys.path.append(r'C:\Program Files (x86)\Analog Devices\ACE\Client')
clr.AddReference('AnalogDevices.Csa.Remoting.Clients')
import AnalogDevices.Csa.Remoting.Clients as adrc


def getHardwareIds(IPC_port=IPCPORT):
    """
    Get a list of Hardware IDs for the boards that are connected to this PC. To get the ID of a specific board,
    connect only that one board to the PC and run this function.

    :param IPC_port: port number of the ACE software IPC server.
    :return: List of hardware IDs connected.
    """
    clientManager = adrc.ClientManager.Create()
    client = clientManager.CreateRequestClient(f'localhost:{IPC_port}')
    all_ids = client.ListHardwareIds().split("\n")
    real_ids = []
    for id in all_ids:
        if ("Virtual" not in id) and (len(id) > 0):
            real_ids.append(id)
    if len(real_ids) == 0:
        raise RuntimeError("no board detected")
    return real_ids


class AnalogDevices_ADMV8818(Instrument):
    def __init__(self, name, hardwareID=None, IPC_port=IPCPORT, reset=False, **kwargs):
        '''
        Initializes the AnalogDevices_ADMV8818 digital tunable HPF+LPF filter.

        Input:
          name (string)    : name of the instrument
          hardwareID (string) : hardwareID of the board. If only one board is connected to the PC, hardwareID can None.
                                Otherwise, check the doc sting above to see how to identify hardwareID.
          IPC_port(string) : port number of the ACE software IPC server.
          reset (bool)     : resets to bypass mode.

        '''
        super().__init__(name, **kwargs)
        logging.info(__name__ + ' : Initializing')

        # create a ACE client.
        clientManager = adrc.ClientManager.Create()
        client = clientManager.CreateRequestClient(f'localhost:{IPC_port}')
        self.__client = client

        # find hardware by ID
        id_list = getHardwareIds(IPC_port)
        if hardwareID is None:
            if len(id_list) == 1: # only one board is connected
                self.hardwareID = id_list[0]
            else:
                raise ValueError(f"multiple boards are detected: {id_list}. hardwareID must be specified to initialize a specific device")
        else:
            if hardwareID in id_list:
                self.hardwareID = hardwareID
            else:
                raise ValueError(f"can't find board with ID {hardwareID}, available IDs are {id_list}")
        self._address = self.hardwareID

        # Load hardware with ID
        client.AddHardwarePlugin('ADMV8818 Board')
        self.subsystem = client.AddByHardwareId(self.hardwareID)[:-1]

        # Navigate to the board page
        client.set_ContextPath(fr'\System\{self.subsystem}\ADMV8818 Board\ADMV8818')
        client.NavigateToPath(f'Root::System.{self.subsystem}.ADMV8818 Board.ADMV8818')

        # initialize the switch positions
        self._set_WRs()

        # add params
        # self.add_parameter('LPF_switch',
        #                    label='LPF_switch',
        #                    get_cmd=self.get_LPF_switch,
        #                    set_cmd=self.set_LPF_switch,
        #                    vals=Enum(0, 1, 2, 3, 4),
        #                    docstring="controls the switch to a LPF unit."\
        #                              "0: bypass;"\
        #                              "1: 2.05-3.85 GHz"\
        #                              "2: 3.35-7.25 GHz"\
        #                              "3: 7.00-13.00 GHz"\
        #                              "4: 12.55-18.85 GHz"
        #                    )
        #
        # self.add_parameter('HPF_switch',
        #                    label='HPF_switch',
        #                    get_cmd=self.get_HPF_switch,
        #                    set_cmd=self.set_HPF_switch,
        #                    vals=Enum(0, 1, 2, 3, 4),
        #                    docstring="controls the switch to a HPF unit."\
        #                              "0: bypass;"\
        #                              "1: 1.75-3.55 GHz"\
        #                              "2: 3.40-7.25 GHz"\
        #                              "3: 6.60-12.00 GHz"\
        #                              "4: 12.50-19.90 GHz"
        #                    )
        #
        # self.add_parameter('LPF_register',
        #                    label='LPF_register',
        #                    get_cmd=self.get_LPF_register,
        #                    set_cmd=self.set_LPF_register,
        #                    vals=Enum(*range(16)),
        #                    docstring="the value of the 4 bit register that controls the cut-freq of the currently selected LPF unit."
        #                    )
        #
        # self.add_parameter('HPF_register',
        #                    label='HPF_register',
        #                    get_cmd=self.get_HPF_register,
        #                    set_cmd=self.set_HPF_register,
        #                    vals=Enum(*range(16)),
        #                    docstring="the value of the 4 bit register that controls the cut-freq of the currently selected HPF unit."
        #                    )

        self.add_parameter('LPF_setting',
                           label='LPF_setting',
                           get_cmd=self.get_LPF_setting,
                           set_cmd=self.set_LPF_setting,
                           vals=Lists(Ints()),
                           docstring="controls the setting of LPF unit, and its register value."\
                                     "first digit controls the switch to a specific LPF unit:"\
                                     "0: bypass;"\
                                     "1: 2.05-3.85 GHz;"\
                                     "2: 3.35-7.25 GHz;"\
                                     "3: 7.00-13.00 GHz;"\
                                     "4: 12.55-18.85 GHz."\
                                     "Second digit controls the value of the 4-bit register that controls the cut-freq of the selected LPF:"\
                                     "The register value can be 0-15, which uniformly divides the cut-freq of the LPF in its tunable range."
                           )

        self.add_parameter('HPF_setting',
                           label='HPF_setting',
                           get_cmd=self.get_HPF_setting,
                           set_cmd=self.set_HPF_setting,
                           vals=Lists(Ints()),
                           docstring="controls the setting of HPF unit, and its register value."\
                                     "first digit controls the switch to a specific HPF unit:"\
                                     "0: bypass;"\
                                     "1: 1.75-3.55 GHz;"\
                                     "2: 3.40-7.25 GHz;"\
                                     "3: 6.60-12.00 GHz;"\
                                     "4: 12.50-19.90 GHz." \
                                     "Second digit controls the value of the 4-bit register that controls the cut-freq of the selected HPF:" \
                                     "The register value can be 0-15, which uniformly divides the cut-freq of the HPF in its tunable range."
                           )

        if reset:
            self.reset()

    def _set_WRs(self):
        """
        sets the switch positions for where the HPF/LPF state bits are assigned,
        """
        for i in range(5):
            self.__client.SetIntParameter(f"SW_IN_WR{i}", f"{i}", "-1")
            self.__client.SetIntParameter(f"SW_OUT_WR{i}", f"{i}", "-1")

    def _validate_setting(self, val):
        if len(val)!= 2:
            raise ValueError("filter selection variable must be a length 2 list")
        if val[0] not in range(5):
            raise ValueError("first element of filter selection variable selects the filter unit, it must be an integer between 0 to 5")
        if val[1] not in range(16):
            raise ValueError("second element of filter selection variable controls the filter register, it must be an integer between 0 to 15")


    def get_LPF_switch(self):
        self.__client.ReadSettings() # read settings from the board
        for i in range(5):
            if self.__client.GetBoolParameter(f"SW_OUT_SET_WR{i}") == "True\n":
                return i
        return 0

    def set_LPF_switch(self, val, apply=True):
        for i in range(val):
            self.__client.SetBoolParameter(f"SW_OUT_SET_WR{i}", "False", "-1")
        self.__client.SetBoolParameter(f"SW_OUT_SET_WR{val}", "True", "-1")
        if apply:
            self.__client.ApplySettings()
            time.sleep(0.5)

    def get_HPF_switch(self):
        self.__client.ReadSettings() # read settings from the board
        for i in range(5):
            if self.__client.GetBoolParameter(f"SW_IN_SET_WR{i}") == "True\n":
                return i
        return 0


    def set_HPF_switch(self, val, apply=True):
        for i in range(val):
            self.__client.SetBoolParameter(f"SW_IN_SET_WR{i}", "False", "-1")
        self.__client.SetBoolParameter(f"SW_IN_SET_WR{val}", "True", "-1")
        if apply:
            self.__client.ApplySettings()
            time.sleep(0.5)



    def get_LPF_register(self):
        sw = self.get_LPF_switch()
        val = int(self.__client.GetByteParameter(f"LPF_WR{sw}")[:-1])
        return val


    def set_LPF_register(self, val, apply=True):
        sw = self.get_LPF_switch()
        self.__client.SetByteParameter(f"LPF_WR{sw}", f"{val}", "-1")
        if apply:
            self.__client.ApplySettings()
            time.sleep(0.5)

    def get_HPF_register(self):
        sw = self.get_HPF_switch()
        val = int(self.__client.GetByteParameter(f"HPF_WR{sw}")[:-1])
        return val


    def set_HPF_register(self, val, apply=True):
        sw = self.get_HPF_switch()
        self.__client.SetByteParameter(f"HPF_WR{sw}", f"{val}", "-1")
        if apply:
            self.__client.ApplySettings()
            time.sleep(0.5)



    def get_LPF_setting(self):
        self.__client.ReadSettings() # read settings from the board
        sw=0
        for i in range(5):
            if self.__client.GetBoolParameter(f"SW_OUT_SET_WR{i}") == "True\n":
                sw=i
                break
        reg = int(self.__client.GetByteParameter(f"LPF_WR{sw}")[:-1])
        return [sw, reg]


    def set_LPF_setting(self, val, apply=True):
        self._validate_setting(val)
        self.set_LPF_switch(val[0], apply=False)
        self.__client.SetByteParameter(f"LPF_WR{val[0]}", f"{val[1]}", "-1")
        if apply:
            self.__client.ApplySettings()
            time.sleep(0.5)


    def get_HPF_setting(self):
        self.__client.ReadSettings() # read settings from the board
        sw=0
        for i in range(5):
            if self.__client.GetBoolParameter(f"SW_In_SET_WR{i}") == "True\n":
                sw=i
                break
        reg = int(self.__client.GetByteParameter(f"HPF_WR{sw}")[:-1])
        return [sw, reg]


    def set_HPF_setting(self, val, apply=True):
        self._validate_setting(val)
        self.set_HPF_switch(val[0], apply=False)
        self.__client.SetByteParameter(f"HPF_WR{val[0]}", f"{val[1]}", "-1")
        if apply:
            self.__client.ApplySettings()
            time.sleep(0.5)



    def apply_settings(self):
        self.__client.ApplySettings()

    def _get_client(self):
        # not supported for instrument server
        return self.__client

    def reset(self):
        """Reset the board to bypass filter mode"""
        self.__client.Reset()
        self._set_WRs()


    def get_idn(self) -> Dict[str, Optional[str]]:
        IDN: Dict[str, Optional[str]] = {
            'vendor': "Analog Devices",
            'model': "EVAL-ADMV8818",
            'hardwareID': self.hardwareID
            }
        return IDN

if __name__ == "__main__":
    filter = AnalogDevices_ADMV8818("filter", '456&B660&97B5E')
    # filter.set_HPF_setting([0,0])
    filter.set_LPF_setting([2,14])