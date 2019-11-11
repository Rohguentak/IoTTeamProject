import sys
import Adafruit_DHT

def temp_sensor():
	
	sensor = 'Adafruit_DHT.DHT11' ## using dht11
	pin = ''#put pin num'
	humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
	if humidity is not None and temperature is not None:
		print('temp ={0:0.1f}* Humodity={1:0.1f}%'.format(temperature, humidity))
	else:
		print('fail to get read data')
		sys.exit(1)


