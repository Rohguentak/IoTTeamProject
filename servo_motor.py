import time
import RPi.GPIO as GPIO

GPIO.setwarnings(False)

pin = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(pin, GPIO.OUT) # gpio for motor
p = GPIO.PWM(pin,50)
p.start(0)

def servo_motor(data):
	p.start(0)
	if data ==1:
	    p.ChangeDutyCycle(7.5) ## close canopy or break
            time.sleep(0.5)
	    p.stop()
        elif data == 0:
            p.ChangeDutyCycle(12.5)
            time.sleep(0.5)
            p.stop()
		

servo_motor(0)
servo_motor(1)
servo_motor(0)
servo_motor(1)
servo_motor(0)

GPIO.cleanup()
