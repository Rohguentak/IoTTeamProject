import sys
import spidev
import time 
import RPi.GPIO as gpio
sensor = 2
gpio.setmode(gpio.BCM)
gpio.setup(sensor, gpio.OUT)

spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz = 1000000

sampletime = 280
delaytime = 40
offtime = 9680
def analog_read(channel):
	r = spi.xfer2([1,(8+channel) <<4,0])
	adc_out = ((r[1]&3) << 8) + r[2]
	return adc_out
	
def dust_seonsor():
	reading = analog_read(0)
	data =reading
	return data	
	
while True:	
	gpio.output(sensor, False)
	time.sleep(sampletime/1000000.0)
        dust = dust_seonsor()
        time.sleep(delaytime/1000000.0)
	gpio.output(sensor, True)
        time.sleep(offtime/1000000.0)
	volt = dust * 5.0/1023
	dust_density = volt * 0.17 - 0.1
	print('dust = %d		voltage = %f    dust_density = %f' % (dust, volt,dust_density))
	time.sleep(1)
	

