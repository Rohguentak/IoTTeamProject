import sys
import spidev
import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(2, GPIO.OUT) 
	
spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz = 1350000

def analog_read(channel):
	r = spi.xfer2([1,(8+channel) <<4,0])
	adc_out = ((r[1]&3) << 8) + r[2]
	return adc_out
	
def dust_seonsor():
	reading = analog_read(0)
	data =reading
	return data	
	
while True:
	dust = dust_seonsor()
	volt = dust* 3.3 /1024
	print('dust = %d		voltage = %f' % (dust, volt))
	time.sleep(1)
	

