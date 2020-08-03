import os
import time
import numpy as np
import datetime as dt

import RPi.GPIO as GPIO
import __buffer__ as buff

import logging
from logging.handlers import RotatingFileHandler
import traceback

DATA = buff.autovalve()[0]
LOG = buff.autovalve()[1]
buffName = buff.autovalve()[2]

analysis = {}
analysis['overFill'] = buff.autovalve()[3]
analysis['ident'] = buff.autovalve()[4]

avgTime = buff.autovalve()[5]

buffr = os.path.join(DATA,buffName)

valve = 14 #GPIO BCM pin for relay
status = False # Default valve status 

fillTime = 10*60 # min*s
scanTime = 1
ts = [0,0]

closeVolt = 10.0
closedVolt = 9.0
openVolt = -1E-4

waiting = True
filling = False
closing = False

GPIO.setmode(GPIO.BCM)
GPIO.setup(valve,GPIO.OUT)
GPIO.output(valve,status)

STATE = {False:'CLOSED',True:'OPEN'}

# What is the buffer log filename?
autoLog = 'autoLog_%s.txt'%dt.datetime.utcnow().timestamp()
log = os.path.join(LOG,autoLog)
# Make Log File
logger = logging.getLogger("Rotating Log")
logger.setLevel(logging.ERROR)
handler = RotatingFileHandler(log, maxBytes=10000, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def toggleWait():
    time.sleep(0.5)

def toggleValve():
    GPIO.output(valve,False);toggleWait()
    GPIO.output(valve,True);toggleWait()
    GPIO.output(valve,False);toggleWait()
    GPIO.output(valve,True);toggleWait()
    GPIO.output(valve,False)

def alarm():
    return 0

if __name__ == '__main__':
    try:
        while True:
            ts[0] = dt.datetime.utcnow().timestamp()
            try:
                data = np.genfromtxt(buffr,comments='#',delimiter=';',skip_header=1,skip_footer=1,names=True)
            except:
                time.sleep(1)
                continue
            if waiting:
                openCount = 0
                for strname in analysis['ident']:
                    if data['%s'%strname][-1] < openVolt:
                        openCount += 1
                if openCount == 3:
                    GPIO.output(valve,True)
                    startFill = dt.datetime.utcnow().timestamp()
                    waiting = False
                    filling = True
                if data['%s'%analysis['overFill']][-1] > closeVolt:
                    toggleValve()
                    waiting = False
                    closing = True
            if filling:
                closeCount = 0
                if data['%s'%analysis['overFill']][-1] > closeVolt:
                    toggleValve()
                    endFill = dt.datetime.utcnow().timestamp()
                    filling = False
                    closing = True
                if (dt.datetime.utcnow().timestamp()-startFill) > fillTime:
                    toggleValve()
                    endFill = dt.datetime.utcnow().timestamp()
                    filling = False
                    closing = True
            if closing:
                if dt.datetime.utcnow().timestamp()-endFill > avgTime:
                    toggleValve()
                    closeCount += 1
                    endFill = dt.datetime.utcnow().timestamp()
                if closeCount == 3:
                    alarm()
                if data['%s'%analysis['overFill']][-1] < closedVolt:
                    closing = False
                    waiting = True
            ts[1] = dt.datetime.utcnow().timestamp()
            procTime = ts[1]-ts[0]
            if (scanTime-procTime) > 0:
                waitTime = scanTime-procTime
                time.sleep(waitTime)
    except Exception as e:
        logger.error(str(e))
        logger.error(traceback.format_exc())