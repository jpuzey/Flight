import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import serial
import re
import csv
import seaborn as sns
import warnings
import sys
import os
from datetime import datetime
import glob
import time
import io

def is_mac():
    mac = True if sys.platform == "darwin" else False
    return(mac)
    
if not is_mac():
    import msvcrt
    import winsound
    
#%matplotlib inline
print(sys.version)
print(sys.executable)

# define directories
baseDir = os.getcwd()

# data for storing datafile
dataDir = '/Users/jpuzey/Dropbox/Research/Monarch_Flight/MonarchPesticides/data/'
if not os.path.isdir(dataDir):
    os.mkdir(dataDir)

figDir = '/Users/jpuzey/Dropbox/Research/Monarch_Flight/MonarchPesticides/data/'
if not os.path.isdir(figDir):
    os.mkdir(figDir)

def serial_ports():
    """ Lists serial port names
        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


# list serial ports
ports=serial_ports() # this arduino is on COM6
print(ports)

# connect to arduino
PORT1 = ports[1]

connected1 = False
if "ser1" in globals():
    ser1.close()
    
ser1 = serial.Serial(PORT1, 115200, timeout=1.0) # stop if no data comes in 1 second
while not connected1:
    serin1 = ser1.read()
    connected1 = True
    print("connected to arduino on " + PORT1)
serin1 = ser1.readline()
print(serin1.decode("utf-8")) # should say "setup complete"

ctr = 0
maxTime = 1 # minutes

if not is_mac():
    while msvcrt.kbhit():
        msvcrt.getch()
        print('clearing characters ...')
        
# turn off data collection if it's already started
ser1.write("c".encode("utf-8")) # sending something that's not "r" tell arduino to stop recordin

# read all data in the incoming buffer to clear it
# note that this might take a second or two 
ser1.readlines() 

# sending an "r" tells the arduino so start sending data
ser1.write("r".encode("utf-8"))
while True:
    if not is_mac():
        if msvcrt.kbhit(): # if q, or escape is pressed, then break the loop
            k = msvcrt.getch()
            if(k == b'q') | (k == b'\x1b') | (k == b'\x0b') :
                print("keyboard break")
                winsound.MessageBeep()
                break
            

    if ctr == 0:
        
        minuteCounter = 0
       
        # tell arduino to write data to serial
        # discard first read line, in case it's the wrong length
        ser1.readline()
        
        txt = ser1.readline().decode("utf-8")
        txt2 = (txt).rstrip().split(",") 
        colNames = ["A" + str(ii) for ii in range(len(txt2) -1)]
        colNames.append("ardno_usec_snce_lst_read")
        colNames.append("python_datetime")
        
        # make file  and write header
        fileStart = datetime.now()
        fname = (fileStart.strftime('%Y-%m-%d %H:%M:%S.%f'))
        fname = re.sub(r'[^\w\s]','_',fname)
        fname = re.sub(" ", "__", fname)[0:] + ".csv"

        with open(os.path.join(dataDir, fname), 'a+', newline='') as myfile:
            wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
            wr.writerows([colNames])
            
            
    
    
    # read data
    txt = ser1.readline().decode("utf-8")
    line_to_write =  (txt + "," + datetime.now().
                  strftime('%Y-%m-%d %H:%M:%S.%f')).rstrip().split(",")  

    # check data before writing
    if (len(line_to_write) != len(colNames)):
        print("data length is different from length of columns, dropping a reading")
        print(line_to_write)
        print(colNames)
        print(ctr)
        continue
        
    elif (np.max(list(map(int, line_to_write[:-3]))) > 1023):
        print("data range incorrect, dropping a reading")
        continue
    
    else:
        with open(os.path.join(dataDir, fname), 'a+', newline='') as myfile:
            wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
            wr.writerows([line_to_write])

    # print time
    readTime = datetime.now()
    c = readTime - fileStart
    if c.total_seconds()//60 == minuteCounter:
        print("Time elapsed (minutes):", minuteCounter)
        minuteCounter += 5 # print every 5 minutes
    
    if divmod(c.days * 86400 + c.seconds, 60)[0] >= maxTime:
        break   
    
    # update ctr
    ctr += 1

# stop data collection
ser1.write("c".encode("utf-8"))

print('done')

