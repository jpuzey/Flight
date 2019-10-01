import sys
import pandas as pd
import numpy as np
import random
import matplotlib.pyplot as plt
from matplotlib import *
import warnings
import scipy
from scipy.signal import find_peaks
from scipy.misc import electrocardiogram
#from scipy.interpolate import interp1d
from datetime import datetime
from datetime import timedelta
warnings.filterwarnings('ignore')

datafile = sys.argv[1]

##what is the minimum height of a 'peak'
PeakHeight=300

##how far do two peaks need to be to be called distinct peaks
distancebtwpeaks=20

##Open the data file
df=pd.read_csv(datafile,sep=',', delimiter=None, header='infer', engine='python')

##
df['datetime']= pd.to_datetime(df['python_datetime'])

##create empty numeric 'peak' column 
df['peak']=np.nan
df['peak']= pd.to_numeric(df['peak'])

for a in ['A0','A1','A2','A3','A4','A5']:
    #P=[]
    ##find peaks -- set peak height and distance between peaks
    P, _ = find_peaks(df[a], height=PeakHeight, distance=distancebtwpeaks)
    for b in P:
        #print(b)
        name=a+'peak'
        df.at[b,name]=1000

##calculate time difference between two peaks
##ignore the time to first peak
delta=[]
count=0
time=[]
for a in P:
    if count == 0:
        firstpeak=df['datetime'][a]
    else:
        nextpeak=df['datetime'][a]
        time.append(str(nextpeak))
        C=nextpeak-firstpeak
        delta.append(str(C))
        firstpeak=nextpeak  
    count = count + 1


###clean up the time, just get the seconds between rotations. This assumes the butterfly
###won't take more than 60 seconds to complete a rotation. Not paying attention to
###the minute entry
seconds=[]
for b in delta:
    D=b.split(':')
    seconds.append(float(D[2]))

##create dataframe from two lists. The 'Time' column is when the data was taken
##the 'Seconds' column is the time between two peaks
F = pd.DataFrame(list(zip(time, seconds)), columns =['Time', 'Seconds']) 
F['Time']= pd.to_datetime(F['Time'])

##Calculate the frequency of rotations (1/s)
F['freq']=1/F['Seconds']
##calculate moving window average of frequency
F['W5']=F['freq'].rolling(window=10).mean()



###Generate plots
#fig, axs = plt.subplots(2, 1)

#fig, ax = plt.subplots(1,2, figsize = [20,12])
fig, ax = plt.subplots(2,2)
ax[0,0].plot(df['datetime'],df['A0'],marker='o', markerfacecolor='blue', markersize=5, color='skyblue',linestyle="-")
ax[0,0].plot(df['datetime'],df['A0peak'],marker='X', markerfacecolor='red', markersize=5, color='red')
plt.xlabel('Time')
ax[0,0].set_ylabel('A0 signal')

ax[0,1].plot(F['Time'],F['freq'],marker='o', markerfacecolor='blue', markersize=5, color='skyblue',linestyle="")
ax[0,1].set_ylim(0,5)
ax[0,1].set_ylabel('Frequency (1/s)')
ax[0,1].plot(F['Time'],F['W5'],marker='o', markerfacecolor='red', markersize=5, color='skyblue',linestyle="--")




ax[1,0].plot(df['datetime'],df['A1'],marker='o', markerfacecolor='blue', markersize=5, color='skyblue',linestyle="-")
ax[1,0].plot(df['datetime'],df['A1peak'],marker='X', markerfacecolor='red', markersize=5, color='red')
plt.xlabel('Time')
ax[1,1].set_ylabel('A1 signal')

#ax[2].plot(df['datetime'],df['A2'],marker='o', markerfacecolor='blue', markersize=5, color='skyblue',linestyle="-")
#ax[2].plot(df['datetime'],df['A2peak'],marker='X', markerfacecolor='red', markersize=5, color='red')
#plt.xlabel('Time')
#ax[2].set_ylabel('A1 signal')

#ax[3].plot(df['datetime'],df['A3'],marker='o', markerfacecolor='blue', markersize=5, color='skyblue',linestyle="-")
#ax[3].plot(df['datetime'],df['A3peak'],marker='X', markerfacecolor='red', markersize=5, color='red')
#plt.xlabel('Time')
#ax[3].set_ylabel('A1 signal')

#ax[4].plot(df['datetime'],df['A4'],marker='o', markerfacecolor='blue', markersize=5, color='skyblue',linestyle="-")
#ax[4].plot(df['datetime'],df['A4peak'],marker='X', markerfacecolor='red', markersize=5, color='red')
#plt.xlabel('Time')
#ax[4].set_ylabel('A1 signal')

#ax[5].plot(df['datetime'],df['A5'],marker='o', markerfacecolor='blue', markersize=5, color='skyblue',linestyle="-")
#ax[5].plot(df['datetime'],df['A5peak'],marker='X', markerfacecolor='red', markersize=5, color='red')
#plt.xlabel('Time')
#ax[5].set_ylabel('A1 signal')

##total number of rotations
Rotations=len(P)
TotalTime=str(df['datetime'][len(df)-1] - df['datetime'][0])
TT=TotalTime.split(':')
Minutes = float(TT[1]) + (float(TT[2])/60)
RPM=round(Rotations/Minutes, 3)
props = dict(boxstyle='square', facecolor='white', alpha=0.7)
text= 'Total Number of Rotations = ' + str(Rotations) + '\n' + 'RPM = ' + str(RPM) 
#ax[0].text(0.01, 0.95, text, transform=ax[0].transAxes, fontsize=14,
#        verticalalignment='top', bbox=props)

name="./Figures/"+'Temp'+'.png'
plt.savefig(name)

