Upgrading Signalcore firmware

IMPORTANT: If your firmware has major revision 2.X then use the latest 2.X binary. If it is 3.X then use the latest 3.X binary. Unless explicitly instructed to do otherwise, using the wrong major revision will cause the device to cease operating correctly. 

The SC5506A/B, SC5313A, and the SC5413A core modules has in field Device Firmware Upgrade (DFU) capability. The following lists step by step instructions to upgrading the firmware on SignalCore devices.


1) Power up the device and plug into into the computer used to perform the upgrade. One device at a time.
2) There is a programming button accessible through a pin-hole on the left side of the devices - viewing from the front of the device. There is also a device reset button accessible through a pin hole in front of the device next to the USB connector. Using pins or wires, depress these 2 buttons, and while holding down the programming pin, release the reset button first, and then release the programming button. NOTE: IT IS IMPORTANT NOT TO APPLY TOO MUCH PRESSURE TO THE BUTTONS BECAUSE THEY COULD GET DAMAGED. SLIGHT PRESSURE IS ALL THAT IS REQUIRED TO DEPRESS THEM.
3)  The action of 2) should put the device into programming mode, and the computer will now indicate that a new USB device is found if the driver for the new found device is not installed. If it a device driver has been installed, the ATMEL USB Device should show up in the Windows device manager. If the computer does not indicate that a new device is found, you can check the device manager in Windows to confirm that. Repeat step 2 careful until you see a new device found.
4) If no driver for the ATMEL USB device has been installed, an installation dialog will ask for a driver. Point the dialog to the Win/dfu-prog-usb-1.2.2 directory which contains the atmel_usb_dfu.inf file. This INF file will instruct the computer to install the correct driver for the SignalCore device in programming mode. The device manager should show at a ATMEL USB device.
5) On the console screen (Type "CMD" on the START/RUN menu), cd to the Win directory and  type  "flashprogrammer.cmd SC5XXXA.hex", and this should start the process of upgrading the firmware. Note flashprogrammer.cmd is just a batch file to dfu-programmer.
6) On success, the device manager will show the SignalCore device again.

LINUX
There are 2 packages required:
	i)	libusb-1.0
	ii) dfu-programmer
	
1) Power up the device and plug into into the computer used to perform the upgrade.One device at a time.
2) There is a programming button accessible through a pin-hole on the left side of the devices - viewing from the front of the device. There is also a device reset button accessible through a pin hole in front of the device next to the USB connector. Using pins or wires, depress these 2 buttons, and while holding down the programming pin, release the reset button first, and then release the programming button. NOTE: IT IS IMPORTANT NOT TO APPLY TOO MUCH PRESSURE TO THE BUTTONS BECAUSE THEY COULD GET DAMAGED. SLIGHT PRESSURE IS ALL THAT IS REQUIRED TO DEPRESS IT.
3) type "usb-devices or lsusb" to make sure the ATMEL device is found.
4) In the Linux directory, type " ./flashprogrammer.sh SC5XXX.hex" to upgrade the firmware. Note, flashprogrammer.sh is a shell for dfu-programmer




