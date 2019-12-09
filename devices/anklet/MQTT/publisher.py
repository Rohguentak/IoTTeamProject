

from pulsesensor import Pulsesensor

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import spidev
from threading import Thread
import RPi.GPIO as gpio
import random
import sys
import time
import json
import signal


spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz = 1350000

BPM = 0
TEMP = 0
exit = True
request = 0
realtime = 0

def analog_read(channel):
    r = spi.xfer2([1,(8+channel) << 4,0])
    adc_out = ((r[1]&3)<<8) + r[2]
    return adc_out


def end_read(signal,frame):
    global exit
    print("keyboard interrupt")
    
    exit = False
    t1.join()
    print("t1 joined")
    
    t2.join()
    print("t2 joined")
    
    print("terminated by keyboard")
    
signal.signal(signal.SIGINT, end_read)


def pulse():
    global BPM
    global exit
    
    p = Pulsesensor()
    p.startAsyncBPM()

    while exit:
        BPM = p.BPM
        if BPM > 0:
            print("BPM: %d" % BPM)
        else:
            print("No Heartbeat found")
        time.sleep(1)
    p.stopAsyncBPM()
    print("pulse finished")
    
# pulse part




import Adafruit_DHT
gpio.setmode(gpio.BCM)

def temp():
    sensor = Adafruit_DHT.DHT11
    pin = 24
    global TEMP
    global exit
    while exit:
        h, t = Adafruit_DHT.read_retry(sensor, pin)
            
        if h is not None and t is not None :
            print("Temperature = {0:0.1f}%".format(t))
            TEMP = t
        
        else :
            print('Read error')
        time.sleep(5)
    
    print("Temp finished")


#temp part

































port = 8883

host = "azjctapxbp7sc-ats.iot.ap-northeast-2.amazonaws.com"
rootCAPath = "./anklet_pi/RootCA.crt"
certificatePath = "./anklet_pi/bc1b2abd97-certificate.pem.crt"
privateKeyPath = "./anklet_pi/bc1b2abd97-private.pem.key"
clientId = "anklet_pi"

# pub topics
topic_temp = "anklet/temp"
topic_temp_for_terminal = "anklet/temp_for_terminal"
topic_pulse = "anklet/pulse"

# sub topics
temp_request_topic = "terminal/temp_request"
realtime_request_topic = "realtime/temp_request"


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



def Callback_func(payload, responseStatus, token):
    print()
    print('UPDATE: $aws/things/' + Thing_Name + '/shadow/update/#')
    print("payload = " + payload)
    print("responseStatus = " + responseStatus)
    print("token = " + token)

def Callback_temp_request(client, userdata, message):
    global request
    '''
    message_temp = {}
    randNUM = int(random.random()*7)+ 30
    message_temp['message'] = topic_temp
    message_temp['sequence'] = TEMP + randNUM
    messageJson_temp = json.dumps(message_temp)
    '''
    
    request = 1
    
def Callback_realtime_request(client, userdata, message):
    global realtime
    temp = json.loads(message.payload)
    realtime = temp["sequence"]
    print(realtime)

offset = 0

t1 = Thread(target = pulse)
t1.start()
t2 = Thread(target = temp)
t2.start()

myAWSIoTMQTTClient.subscribe(temp_request_topic,1,Callback_temp_request)
myAWSIoTMQTTClient.subscribe(realtime_request_topic,1,Callback_realtime_request)


while exit:
    message_temp = {}
    message_temp['message'] = topic_temp
    message_temp['sequence'] = TEMP
    messageJson_temp = json.dumps(message_temp)

    message_pulse = {}
    message_pulse['message'] = topic_pulse
    message_pulse['sequence'] = int(BPM/3)
    messageJson_pulse = json.dumps(message_pulse)
     
     
    if realtime == 1:
        message = myAWSIoTMQTTClient.publish(topic_temp,messageJson_temp,1)
        print(message, BPM/3)
        message = myAWSIoTMQTTClient.publish(topic_pulse,messageJson_pulse,1)
        print(message, TEMP+offset)
            
    if request == 1:
        message = myAWSIoTMQTTClient.publish(topic_temp_for_terminal,messageJson_temp,1)
        request = 0
        print("TEMP is sended to terminal for temp_set_on")
        print(message, TEMP+offset)
     
    for k in range(3):
        print(str(TEMP+offset) + "*****" + str(int(BPM/3)))
        time.sleep(1)
        offset = (offset+0.1)%0.2


