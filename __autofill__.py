import RPi.GPIO as GPIO

valve = 14 #GPIO BCM pin for relay
status = False # Default valve status 

GPIO.setmode(GPIO.BCM)
GPIO.setup(valve,GPIO.OUT)
GPIO.output(valve,status)

STATE = {False:'CLOSED',True:'OPEN'}

while True:
    print('\nThe VALVE is %s'%STATE[status])
    print('Return "0" to close the valve or "1" to open it.')
    new_status = input('Would you like to toggle the valve? : ')
    if new_status == '0':
        status = False
    elif new_status == '1':
        status = True
    else:
        print('Command not recognized, valve closing')
        status = False
    GPIO.output(valve,status)
