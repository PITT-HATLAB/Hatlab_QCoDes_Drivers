@echo off
REM  Firmware Update
REM
REM
 
set flashchip=at32uc3a3256s
set filename=%1

echo This will update the firmware with file %filename%


echo Erasing flash
dfu-programmer %flashchip% erase
if errorlevel == 1 exit /b
echo "Downloading firmware ...."
dfu-programmer %flashchip% flash %1 --suppress-bootloader-mem
if errorlevel == 1 exit /b
echo "Firmware downloaded"
echo "Resetting the device"
dfu-programmer at32uc3a3256s reset
if errorlevel == 1 exit /b
echo "DONE!"
pause


