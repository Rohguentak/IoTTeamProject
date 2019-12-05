import time
import RPi.GPIO as gpio
vibe_pin = 2
gpio.setmode(gpio.BCM)
gpio.setup(vibe_pin, gpio.IN) # gpio for vibe

def vibe_sensor():
	a = gpio.input(vibe_pin)
        print(a)
	if a == 0 :
		print("vibe is sensing")
	else :
		print("nothing")
		
		
while True :
	vibe_sensor()
        time.sleep(0.5)
    

