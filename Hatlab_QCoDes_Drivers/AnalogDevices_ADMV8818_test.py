# Copyright (c) 2019 Analog Devices, Inc.  All Rights Reserved. This software is proprietary to Analog Devices, Inc. and its licensors.

# These code snippets are provided ‘as is’ with no warranties, guarantees of suitability, or acceptance of any  liability, for their use.

import clr
import sys
import os
import time

# Connect to ACE using the remote control client
sys.path.append(r'C:\Program Files (x86)\Analog Devices\ACE\Client')
clr.AddReference('AnalogDevices.Csa.Remoting.Clients')
import AnalogDevices.Csa.Remoting.Clients as adrc
clientManager = adrc.ClientManager.Create()
client = clientManager.CreateRequestClient('localhost:2357')

# # Load the AD9208 plug-in
client.AddHardwarePlugin('ADMV8818 Board')
#
# # Navigate to initialization wizard and set to one converter

# client.AddAttachedHardware(("ADMV8818Board"))
client.set_ContextPath(r'\System\Subsystem_1\ADMV8818 Board\ADMV8818')
client.NavigateToPath('Root::System.Subsystem_1.ADMV8818 Board.ADMV8818')

for i in range(5):
    client.SetIntParameter(f"SW_IN_WR{i}", f"{i}", "-1")
    client.SetIntParameter(f"SW_OUT_WR{i}", f"{i}", "-1")


client.SetBoolParameter("SW_IN_SET_WR0", "False", "-1")
client.SetBoolParameter("SW_IN_SET_WR1", "True", "-1")
client.SetBoolParameter("SW_OUT_SET_WR0", "False", "-1")
client.SetBoolParameter("SW_OUT_SET_WR1", "True", "-1")
client.SetByteParameter("LPF_WR1", "10", "-1")

# client.ReadRegister("0x0")
# time.sleep(2)
client.ApplySettings()
#


# client.Reset()





client.set_ContextPath(r'\System\Subsystem_1\SDP-S')


