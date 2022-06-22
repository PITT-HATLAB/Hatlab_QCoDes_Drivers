"""QCodes driver for Analog Devices digital controlled HPF + LPF EVAL-ADMV8818 board.

@author: Chao

This driver uses the remote control feature of the ACE software form Analog Devices to control the ADMV8818 eval board.

Required Package:
    pythonnet (pip install pythonnet)


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
    If multiple boards are connected to one PC, each board must to be identified by its hardware ID.
    So far I haven't find a relation between the serial number and the hardware ID of a board,
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
from qcodes.utils.validators import Enum
import logging
import clr
import sys
import time

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
    return real_ids


class AnalogDevices_ADMV8818(Instrument):
    def __init__(self, name, hardwareID=None, IPC_port=IPCPORT, reset=False, **kwargs):
        '''
        Initializes the AnalogDevices_ADMV8818 digital tunable HPF+LPF filter.

        Input:
          name (string)    : name of the instrument
          hardwareID (string) : hardwareID of the board
          IPC_port(string) : port number of the ACE software IPC server.
          reset (bool)     : resets to bypass mode.

        '''
        super().__init__(name, **kwargs)
        logging.info(__name__ + ' : Initializing')

        # create a ACE client.
        clientManager = adrc.ClientManager.Create()
        client = clientManager.CreateRequestClient(f'localhost:{IPC_port}')
        self.client = client

        # find hardware by ID
        id_list = getHardwareIds(IPC_port)
        if hardwareID is None:
            if len(id_list) == 1: # only one board is connected
                self.hardwareID = id_list[0]
            else:
                raise ValueError(f"multiple boards are connected : {id_list}. hardwareID must be specified to initialize the device")
        else:
            if hardwareID in id_list:
                self.hardwareID = hardwareID
            else:
                raise ValueError(f"can't find board with id {hardwareID}, available IDs are {id_list}")
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
        self.add_parameter('LPF_sel',
                           label='LPF_sel',
                           get_cmd=self.get_LPF_sel,
                           set_cmd=self.set_LPF_sel,
                           vals=Enum(0, 1, 2, 3, 4),
                           docstring="sets the LPF unit selection."\
                                     "0: bypass;"\
                                     "1: 2.05-3.85 GHz"\
                                     "2: 3.35-7.25 GHz"\
                                     "3: 7.00-13.00 GHz"\
                                     "4: 12.55-18.85 GHz"
                           )

        if reset:
            self.reset()

    def _set_WRs(self):
        """
        sets the switch positions for where the HPF/LPF state bits are assigned,
        """
        for i in range(5):
            self.client.SetIntParameter(f"SW_IN_WR{i}", f"{i}", "-1")
            self.client.SetIntParameter(f"SW_OUT_WR{i}", f"{i}", "-1")


    def get_LPF_sel(self):
        for i in range(5):
            if self.client.GetBoolParameter(f"SW_IN_SET_WR{i}") == "True\n":
                return i #todo: what happens when all False?


    def set_LPF_sel(self, val):
        for i in range(val):
            self.client.SetBoolParameter(f"SW_IN_SET_WR{i}", "False", "-1")
        self.client.SetBoolParameter(f"SW_IN_SET_WR{val}", "True", "-1")
        self.client.ApplySettings()





    def get_client(self):
        return self.client

    def reset(self):
        """Reset the board to bypass filter mode"""
        self.client.Reset()





# # # Load the AD9208 plug-in
# client.AddHardwarePlugin('ADMV8818 Board')
# client.AddByHardwareId('456&B660&97B1B')
# # # Navigate to initialization wizard and set to one converter
#
# # client.AddAttachedHardware(("ADMV8818Board"))
# client.set_ContextPath(r'\System\Subsystem_3\ADMV8818 Board\ADMV8818')
# client.NavigateToPath('Root::System.Subsystem_3.ADMV8818 Board.ADMV8818')
#
# for i in range(5):
#     client.SetIntParameter(f"SW_IN_WR{i}", f"{i}", "-1")
#     client.SetIntParameter(f"SW_OUT_WR{i}", f"{i}", "-1")
#
#
# client.SetBoolParameter("SW_IN_SET_WR0", "False", "-1")
# client.SetBoolParameter("SW_IN_SET_WR1", "True", "-1")
# client.SetBoolParameter("SW_OUT_SET_WR0", "False", "-1")
# client.SetBoolParameter("SW_OUT_SET_WR1", "True", "-1")
# client.SetByteParameter("LPF_WR1", "10", "-1")
#
# # client.ReadRegister("0x0")
# # time.sleep(2)
# client.ApplySettings()
# #
#
#
# # client.Reset()
#
#
#
#
