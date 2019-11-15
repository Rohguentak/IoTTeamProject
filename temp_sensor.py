import Adafruit_DHT
import time


sensor = Adafruit_DHT.DHT11
pin = 2
try:
    while True :
        print('hi')
        h, t = Adafruit_DHT.read_retry(sensor, pin)
        if h is not None and t is not None :
            print("Temperature = {0:0.1f}*C Humidity = {1:0.1f}%".format(t, h))

        else :
            print('Read error')
        time.sleep(1)
except keyboardInterrupt:
    print("terminated by keyboard")

    
	

