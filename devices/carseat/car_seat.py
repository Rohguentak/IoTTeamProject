import time
import json
import sys
import spidev
import Adafruit_DHT
import RPi.GPIO as gpio
import signal
import random
import os
import threading
from gps import *

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from threading import Thread

host = "azjctapxbp7sc-ats.iot.ap-northeast-2.amazonaws.com"
rootCAPath = "./RootCA.crt"
certificatePath = "./3cfe6893cf-certificate.pem.crt"
privateKeyPath = "./3cfe6893cf-private.pem.key" 
port = 8883
clientId = "car_seat_pi"

myAWSIoTMQTTClient = None
myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId)
myAWSIoTMQTTClient.configureEndpoint(host, port)
myAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)
myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)
myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec
myAWSIoTMQTTClient.connect()

sensor = Adafruit_DHT.DHT11
temp_pin = 24 
dust_gpio = 2
pad_gpio = 17
pin_servo = 18 
vibe_pin = 3

gpio.setmode(gpio.BCM)
gpio.setup(dust_gpio, gpio.OUT)
gpio.setup(pad_gpio,gpio.OUT)
gpio.setup(pin_servo, gpio.OUT)
gpio.setup(vibe_pin, gpio.IN)

servo = gpio.PWM(pin_servo,50)
servo.start(0)

##sleeptime for dust_sensor
sampletime = 280
delaytime = 40
offtime = 9680

spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz = 1000000

# subscribe topics
gps_topic = "gps/log_data"
temp_topic = "anklet/temp"
handfree_topic = "stroller/handfree"
temp_set_on_topic = "terminal/temp_set_on"

# pub topics 
neglect_topic = "car_seat/neglect"
request_topic = "realtime/temp_request"
# if rfid tag is not scanned state, state 0. else rfid tag is scanned state. state 1
# unit: second
hand_free = 0 #0
neglect_judge_interval = 3
neglect_threshold_time = time.time()
car_seat_temp = 0
baby_is_in_car_seat = 0
neglect_alarm_on = 0 #0
temp_of_baby = 0
dust_near_baby = 0
temp_to_set = 0
exit = 1
dust = 0
shock_condition = 1
lat_random = 0 # for test #lat_for_test = 37.1234567
lon_random = 0 #for teest #lon_for_test = 127.1234567
lat = 0#0
lon = 0#0

def analog_read(channel):
    r = spi.xfer2([1,(8+channel) <<4,0])
    adc_out = ((r[1]&3<<8)+r[2])
    return adc_out
    
def car_seat_temper():
    global car_seat_temp 
    global exit
    while exit == 1 :
        h , t = Adafruit_DHT.read_retry(sensor, temp_pin)
        if t is not None :
             car_seat_temp = t
             print(car_seat_temp)

def dust_sensor():
    global dust_near_baby
    global dust
    gpio.output(dust_gpio, False)
    time.sleep(sampletime/1000000.0)
    dust = analog_read(1)
    time.sleep(delaytime/1000000.0)
    gpio.output(dust_gpio, True)
    time.sleep(offtime/1000000.0)
    if(dust > 60) :
        dust_near_baby = 1
        print("                     dust density is too high to baby!!!")
    else :
        dust_near_baby = 0
    print("dust : ",dust)
    
#checking neglect with condition. temp of car_seat, fsr sensor, neglect time.
def baby_is_in_seat():
    global baby_is_in_car_seat
    temp = analog_read(0)
    if (temp > 25) :
        baby_is_in_car_seat = 1
        print("-----------------------")
        print("baby is in carseat")
    else :
        baby_is_in_car_seat = 0
        print("-----------------------")
        print("carseat is empty")

def move_servo(data):
    if data ==1:
        servo.ChangeDutyCycle(7.5) ## close canopy or break
        time.sleep(0.5)
    elif data == 0:
        servo.ChangeDutyCycle(12.5)
        time.sleep(0.5)
    
def control_pad(data):
    if(data == 1) :
        print("pad on")
        gpio.output(pad_gpio,True)
    else :
        print("pad off")
        gpio.output(pad_gpio,False)
        
def vibe_sensor():
    global shock_condition
    global exit
    while exit == 1:
        shock_condition = gpio.input(vibe_pin)
        if shock_condition == 0 :
            lat_random = "37.28" + str(random.randrange(0627,6091))#str(random.randrange(3042,4126))
            lon_random = "127.04" + str(random.randrange(2160,8971))#str(random.randrange(2336,5694))
            print("                     vibe is sensing")
            print("                     send gps data : " + lat_random + "," + lon_random)
            #print("                     send gps data : " + str(lat) + "," + str(lon))
            message = {}
            message['message'] = "gps data"
            message['lat'] = lat_random #str(lat)
            message['lon'] = lon_random #str(lon)
            messageJson = json.dumps(message)
            message = myAWSIoTMQTTClient.publish(gps_topic,messageJson,1)
        time.sleep(1)   
	
def stroller_neglect_alarm_condition():
    global neglect_alarm_on
    baby_is_in_seat()
    dust_sensor()
    if(neglect_alarm_on == 1):
        if(hand_free == 1):
            if(baby_is_in_car_seat == 1):
                if(time.time() > neglect_threshold_time or dust_near_baby == 1 or shock_condition == 0) :
                    neglect_alarm_on = 0
                    return 1
    return 0
        
def Callback_for_tempcontrol(client, userdata, message):
    global temp_of_baby
    temp = json.loads(message.payload)
    temp_of_baby = temp["sequence"]
    print("                     temp_of_baby", temp_of_baby , "is received\n")

def Callback_for_handfree(client, userdata, message):
    global hand_free
    global neglect_alarm_on
    global neglect_threshold_time
    temp = json.loads(message.payload)
    hand_free = temp["sequence"]
    print("                     hand_free", hand_free , "is received\n")
    if(hand_free == 1):# rfid is not scanned state. setting neglect_threshold_time. should set time based on temp.
        neglect_alarm_on = 1
        neglect_threshold_time = time.time() + (neglect_judge_interval)
        
def Callback_for_temp_set_on(client, userdata, message):
    global temp_to_set
    temp = json.loads(message.payload)# terminal/temp_set_on data is baby's temperature.
    temp_to_set = temp["sequence"]
    print("pad must be ready to", temp_to_set)

# anklet/temp	
myAWSIoTMQTTClient.subscribe(temp_topic, 1, Callback_for_tempcontrol)
# stroller/handfree
myAWSIoTMQTTClient.subscribe(handfree_topic,1,Callback_for_handfree)
# terminal/temp_set_on
myAWSIoTMQTTClient.subscribe(temp_set_on_topic,1,Callback_for_temp_set_on)

loopCount = 0
move_servo(0) ##set canopy to initial setting
t1 = Thread(target = car_seat_temper) ## car_seat_temp thread
t1.start()
t2 = Thread(target = vibe_sensor)
t2.start()
send = 1

gpsd = None 
#os.system('clear') #clear the terminal (optional)

class GpsPoller(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    global gpsd #bring it in scope
    gpsd = gps(mode=WATCH_ENABLE) #starting the stream of info
    self.current_value = None
    self.running = True #setting the thread running to true
 
  def run(self):
    global gpsd
    while gpsp.running:
      gpsd.next()
      
gpsp = GpsPoller() # create the thread
        
def end_read(signal,frame):
    gpio.cleanup()
    global exit
    print("keyboard interrupt")
    gpsp.running = False
    print("gpsp.runnig", str(gpsp.running) , str(exit))
    exit = 0
    t1.join()
    t2.join()
    gpsp.join()
    print("t1 joined")
    print("t2 joined")
    print("terminated by keyboard")
    
signal.signal(signal.SIGINT, end_read)
gpsp.start()
while exit:
    print '----------------------------------------'
    print 'latitude    ' , gpsd.fix.latitude
    print 'longitude   ' , gpsd.fix.longitude
    lat = round(gpsd.fix.latitude,6)
    lon = round(gpsd.fix.longitude,6)
        
    if( stroller_neglect_alarm_condition() == 1): #check neglect and if neglect send msg to terminal
        print("                     __WARNINGS__send stroller neglect alarm msg to terminal")
        message = {}
        message['message'] = "baby is neglected!!! "
        message['dust density(0~200)'] = dust
        message['car_seat_temp'] = car_seat_temp
        #message['stroller is shocked[0:TRUE,1:FALSE]'] = shock_condition
        messageJson = json.dumps(message)
        message = myAWSIoTMQTTClient.publish(neglect_topic,messageJson,1)
        
    if (baby_is_in_car_seat == 1 and send == 1) :
        send = 0
        print("                     __REQUEST_SIGNAL__is sent to realtime temp control")
        message = {}
        message['sequence'] = 1
        messageJson = json.dumps(message)
        message = myAWSIoTMQTTClient.publish(request_topic,messageJson,1)
    if (baby_is_in_car_seat == 0 and send == 0) : 
        send = 1
        print("                     __STOP__SIGNAL_is sent to realtime temp control")
        message = {}
        message['sequence'] = 0
        messageJson = json.dumps(message)
        message = myAWSIoTMQTTClient.publish(request_topic,messageJson,1)
            
    if(dust_near_baby == 1 and baby_is_in_car_seat == 1) :
        move_servo(1)
        
    print("carseat temperature is "+str(car_seat_temp))
    print("baby's temperature is "+str(temp_of_baby))
    if(temp_to_set > 0 or 20 > abs(car_seat_temp - temp_of_baby) > 3 and temp_of_baby != 0):
        print("pad must be ready")
        control_pad(1)
        
    if(abs(temp_to_set-car_seat_temp) < 3 or abs(car_seat_temp - temp_of_baby) < 3) :
        temp_to_set = 0
        print("pad is hot enough")
        control_pad(0)
        
    time.sleep(3)
    loopCount +=1

