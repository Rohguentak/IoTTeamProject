from pulsesensor import Pulsesensor # pulse library

import sys
import Adafruit_DHT
import spidev
import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(12, GPIO.OUT) # gpio for motor
p = GPIO.PWM(12,50)
    
spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz = 1350000

def analog_read(channel):
    r = spi.xfer2([1,(8+channel) <<4,0])
    adc_out = ((r[1]&3) << 8) + r[2]
    return adc_out
def temp_sensor():
    
    sensor = 'Adafruit_DHT.DHT11' ## using dht11
    pin = ''#put pin num'
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    if humidity is not None and temperature is not None:
        print('temp ={0:0.1f}* Humodity={1:0.1f}%'.format(temperature, humidity))
    else:
        print('fail to get read data')
        sys.exit(1)

def pulse_sensor():
    p = Pulsesensor()
    p.startAsyncBPM()

    try:
        while True:
            bpm = p.BPM
            if bpm > 0:
                print("BPM: %d" % bpm)
            else:
                print("No Heartbeat found")
            time.sleep(1)
    except:
        p.stopAsyncBPM()
    return data
    
def dust_seonsor():
    reading = analog_read(1)
    data =reading
    return data
    
def servo_motor(data):
    p.start(0)
    if data ==1:
        p.ChangeDutyCycle(7.5) ## close canopy or break
        p.stop()
        
    
    
    
pulse_sensor()
