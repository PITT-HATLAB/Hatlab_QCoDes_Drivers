import time
from itertools import product
import  os
import h5py
import matplotlib.pyplot as plt
from Hatlab_QCoDes_Drivers.Hat_ENA5071C import Hat_ENA5071C
from Hatlab_QCoDes_Drivers.AnalogDevices_ADMV8818 import AnalogDevices_ADMV8818


filter_ID = '456&B660&97B5E'
VNA_IP = "TCPIP0::192.168.137.63::INSTR"

device_ID = filter_ID.split("&")[-1] # only the last 4 digits are unique to device. 456 is vendor ID, B660 is product ID

dataPath = rf"L:\Data\00_Calibrations\RT Equipment calibrations\ADMV8818_Filters\{device_ID}\\"

def dataFileName(HPF_setting, LPF_setting):
    return  f"HPF{HPF_setting[0]}_{HPF_setting[1]}_LPF{LPF_setting[0]}_{LPF_setting[1]}"

def setVNA(VNA):
    VNA.power(-10)
    VNA.fstart(300e3)
    VNA.fstop(20e9)
    VNA.VNA.trform("MLOG")

def saveData(filePath, fileName, fData, magData, overWrite=0):
    try:
        os.mkdir(filePath)
    except:
        pass

    if overWrite:
        f = h5py.File(filePath + fileName, "w")
    else:
        f = h5py.File(filePath + fileName, "w-")

    f.create_dataset("freq", data=fData)
    f.create_dataset("mag", data=magData)
    f.close()

def readData(filePath, HPF_setting, LPF_setting):
    fileName = dataFileName(HPF_setting, LPF_setting)
    f = h5py.File(filePath + fileName, "r")
    freq = f["freq"][()]
    mag = f["mag"][()]
    return  freq, mag

def plotData(freq, mag):
    plt.figure()
    plt.plot(freq, mag)
    plt.xlabel("freq (GHz)")
    plt.ylabel("logMag (dBm)")


def measureFilterData(filter, VNA):
    plt.figure()
    for i, (iH, rH, iL, rL) in enumerate(product(range(5), range(16), range(5), range(16))):
        fileName = dataFileName([iH, rH], [iL, rL])
        filter.set_HPF_setting([iH, rH], apply=False)
        filter.set_LPF_setting([iL, rL], apply=True)

        time.sleep(VNA.sweep_time()*2)

        freqData = VNA.getfdata()
        magData = VNA.gettrace()[0]

        plt.plot(freqData, magData)
        plt.pause(0.1)

        saveData(dataPath, fileName, freqData, magData, overWrite=1)


if __name__ == "__main__":
    # filter = AnalogDevices_ADMV8818("filter", filter_ID)
    # VNA = Hat_ENA5071C("VNA", VNA_IP)
    # measureFilterData(filter, VNA)



    freq, mag = readData(dataPath, [0,15], [2,1]) # [HPF switch,HPF Register] , [LPF switch,LPF Register]
    plotData(freq/1e9, mag)




