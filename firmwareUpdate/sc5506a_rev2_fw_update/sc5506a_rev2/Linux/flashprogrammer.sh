#  Firmware Update
#
#
 
flashchip=at32uc3a3256s
filename=$1

echo "This will update the firmware with $filename"

echo "Erasing flash ...."
sudo dfu-programmer $flashchip erase
if [ $? -eq 1 ]
then 
	echo "Flash not erase"
	exit 1
fi
echo "Downloading firmware ...."
sudo dfu-programmer $flashchip flash $filename --suppress-bootloader-mem
if [ $? -eq 1 ]
then 
	echo "Flash not erase"
	exit 1
else
	echo "Firmware downloaded"
fi

echo "Resetting the device ...."

sudo dfu-programmer $flashchip reset

echo "DONE!"


