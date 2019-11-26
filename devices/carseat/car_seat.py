import time
import json
import sys
import spidev
import Adafruit_DHT
import RPi.GPIO as gpio

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

host = "azjctapxbp7sc-ats.iot.ap-northeast-2.amazonaws.com"
rootCAPath = "./RootCA.crt"
certificatePath = "./3cfe6893cf-certificate.pem.crt"
privateKeyPath = "./3cfe6893cf-private.pem.key" 
port = 8883
clientId = "car_seat_pi"

sensor = Adafruit_DHT.DHT11
pin = 24 ## temp_sensor
dust_gpio = 2
gpio.setmode(gpio.BCM)
gpio.setup(dust_gpio, gpio.OUT)

sampletime = 280
delaytime = 40
offtime = 9680

spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz = 1000000

# sub topics
temp_topic = "anklet/temp"
handfree_topic = "stroller/handfree"
parent_topic = "car/parent"
temp_set_on_topic = "terminal/temp_set_on"

# pub topics 
neglect_topic = "car_seat/neglect"
#auto_

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

# if rfid tag is not scanned state, state 0. else rfid tag is scanned state. state 1
hand_free = 0
# unit: second
neglect_judge_interval = 3
neglect_threshold_time = time.time()
car_seat_temp = 0
baby_is_in_car_seat = 0
neglect_alarm_on = 1
parent_is_in_car = 1
temp_of_baby = 0
dust_near_baby = 0

def analog_read(channel):
    r = spi.xfer2([1,(8+channel) <<4,0])
    adc_out = ((r[1]&3<<8)+r[2])
    return adc_out
    
def car_seat_temper():
    global car_seat_temp 
    while True :
        h , t = Adafruit_DHT.read_retry(sensor, pin)
        if t is not None :
             car_seat_temp = t

def dust_sensor():
    global dust_near_baby
    gpio.output(dust_gpio, False)
    time.sleep(sampletime/1000000.0)
    dust = analog_read(1)
    time.sleep(delaytime/1000000.0)
    gpio.output(dust_gpio, True)
    time.sleep(offtime/1000000.0)
    if(dust > 60) :
        dust_near_baby = 1
    else :
        dust_near_baby = 0
    volt = dust * 5.0/1023
    dust_density = volt * 0.17 - 0.1
    print('dust = %d		voltage = %f    dust_density = %f' % (dust, volt,dust_density))
	
	
        
#checking neglect with condition. temp of car_seat, fsr sensor, neglect time.
def baby_is_in_seat():
    global baby_is_in_car_seat
    temp = analog_read(0)
    print(temp)
    if (temp > 25) :
        baby_is_in_car_seat = 1
    else :
        baby_is_in_car_seat = 0

def Callback_for_tempcontrol(client, userdata, message):
    global temp_of_baby
    temp = json.loads(message.payload)
    temp_of_baby = temp["sequence"]
    print("temp_of_baby", temp_of_baby , "is received\n")

def Callback_for_handfree(client, userdata, message):
    global hand_free
    global neglect_alarm_on
    global neglect_threshold_time
    temp = json.loads(message.payload)
    hand_free = temp["sequence"]
    print("hand_free", hand_free , "is received\n")
    if(hand_free == 1):# rfid is not scanned state. setting neglect_threshold_time. should set time based on temp.
        neglect_alarm_on = 1
        neglect_threshold_time = time.time() + (neglect_judge_interval)

def Callback_for_parent(client, userdata, message):
    global parent_is_in_car
    global neglect_alarm_on
    global neglect_threshold_time
    temp = json.loads(message.payload)
    parent_is_in_car = temp["sequence"]
    print("parent_is_in_car", parent_is_in_car , "is received\n")
    if(parent_is_in_car == 0): # should set time based on temp.
        neglect_alarm_on = 1
        neglect_threshold_time = time.time() + (neglect_judge_interval)
def Callback_for_temp_set_on(client, userdata, message):
    temp = json.loads(message.payload)
    # terminal/temp_set_on data is baby's temperature.
    temperature = temp["sequence"]
    print("temperature", temperature , "is received\n")
    
def stroller_neglect_alarm_condition():
    global neglect_alarm_on
    baby_is_in_seat()
    dust_sensor()
    if(neglect_alarm_on == 1 and hand_free == 1 or time.time() > neglect_threshold_time and baby_is_in_car_seat == 1 or dust_near_baby == 1):# baby_is_in_car_seat = 1
        neglect_alarm_on = 0
        return 1
    return 0
    
def car_neglect_alarm_condition():
    global neglect_alarm_on
    baby_is_in_seat()
    dust_sensor()
    if(neglect_alarm_on == 1 and parent_is_in_car == 0 or time.time() > neglect_threshold_time and baby_is_in_car_seat == 1 or dust_near_baby == 1):# baby_is_in_car_seat = 1
        neglect_alarm_on = 0
        return 1
    return 0

##def control_pad():
        
	
# anklet/temp	
myAWSIoTMQTTClient.subscribe(temp_topic, 1, Callback_for_tempcontrol)
# stroller/handfree
myAWSIoTMQTTClient.subscribe(handfree_topic,1,Callback_for_handfree)
# car/parent
myAWSIoTMQTTClient.subscribe(parent_topic,1,Callback_for_parent)
# terminal/temp_set_on
myAWSIoTMQTTClient.subscribe(temp_set_on_topic,1,Callback_for_temp_set_on)

loopCount = 0

while True:
    #dust_sensor()
    #if(dust_near_baby == 1) :
    #    print("baby is danger")
    #else :
    #    print("air is fresh")
    #baby_is_in_seat()
    #if(baby_is_in_car_seat == 1) :
    #    print("baby is in car seat")
    #else :
    #    print("no baby")
            
    if( car_neglect_alarm_condition() == 1):
        print("send car neglect alarm msg to terminal")
        message = {}
        message['message'] = "car_seat/neglect"
        message['sequence'] = 1
        messageJson = json.dumps(message)

        # car_seat/neglect
        message = myAWSIoTMQTTClient.publish(neglect_topic,messageJson,1)
        #print(message, 1)


    if( stroller_neglect_alarm_condition() == 1): #check neglect and if neglect send msg to terminal
        print("send stroller neglect alarm msg to terminal")
        message = {}
        message['message'] = "car_seat/neglect"
        message['sequence'] = 1
        messageJson = json.dumps(message)

        # car_seat/neglect
        message = myAWSIoTMQTTClient.publish(neglect_topic,messageJson,1)
        #print(message, 1)
    car_seat_temper()
    if(abs(car_seat_temp - temp_of_baby) > 3) : ##live temp controller
        print("pad must be controlled")
        ##control_pad()
        
    time.sleep(3)
    loopCount +=1


