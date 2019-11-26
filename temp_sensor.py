import Adafruit_DHT
import time


sensor = Adafruit_DHT.DHT11
pin = 24
try:
    while True :
        h , t = Adafruit_DHT.read_retry(sensor, pin)
        if t is not None :
            print(type(t))
            ##print("Temperature = {0:0.1f}*C".t)
            ##print(type(format(t, h)))
            ##print("Temperature = {0:0.1f}*C Humidity = {1:0.1f}%" type(t, h))

        else :
            print('Read error')
        time.sleep(5)
except KeyboardInterrupt:
    print("terminated by keyboard")

    
	

