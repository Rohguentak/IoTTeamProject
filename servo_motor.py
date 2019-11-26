import time
import RPi.GPIO as GPIO

GPIO.setwarnings(False)

pin = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(pin, GPIO.OUT) # gpio for motor
p = GPIO.PWM(pin,50)
p.start(0)

def servo_motor(data):
	if data ==1:
	    print(2)
	    p.ChangeDutyCycle(7.5) ## close canopy or break
            time.sleep(0.5)
        elif data == 0:
	    print(1)
            p.ChangeDutyCycle(12.5)
            time.sleep(0.5)

servo_motor(0)




GPIO.cleanup()
