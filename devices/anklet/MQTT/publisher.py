import time
import json

from pulsesensor import Pulsesensor
import time

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import spidev
from threading import Thread


spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz = 1350000

BPM = 0
TEMP = 0
exit = 1
def analog_read(channel):
    r = spi.xfer2([1,(8+channel) << 4,0])
    adc_out = ((r[1]&3)<<8) + r[2]
    return adc_out



def pulse():
    global BPM
    global exit
    
    p = Pulsesensor()
    p.startAsyncBPM()

    while exit == 1:
        BPM = p.BPM
        if BPM > 0:
            print("BPM: %d" % BPM)
        else:
            print("No Heartbeat found")
        time.sleep(1)
# pulse part




import Adafruit_DHT

def temp():
    sensor = Adafruit_DHT.DHT11
    pin = 24
    global TEMP
    global exit
    try:
        while exit==1 :
            h, t = Adafruit_DHT.read_retry(sensor, pin)
            
            if h is not None and t is not None :
                print("Temperature = {0:0.1f}%".format(t))
                TEMP = t
        
            else :
                print('Read error')
            time.sleep(5)
    except KeyboardInterrupt:
        print("terminated by keyboard-------temp")

#temp part

































port = 8883

host = "azjctapxbp7sc-ats.iot.ap-northeast-2.amazonaws.com"
rootCAPath = "./anklet_pi/RootCA.crt"
certificatePath = "./anklet_pi/bc1b2abd97-certificate.pem.crt"
privateKeyPath = "./anklet_pi/bc1b2abd97-private.pem.key"
clientId = "anklet_pi"

# pub topics
topic_temp = "anklet/temp"
topic_pulse = "anklet/pulse"

# sub topics
temp_request_topic = "terminal/temp_request"


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
    message_temp = {}
    message_temp['message'] = topic_temp
    message_temp['sequence'] = 35
    messageJson_temp = json.dumps(message_temp)

    message = myAWSIoTMQTTClient.publish(topic_temp,messageJson_temp,1)
    print("TEMP is sended to terminal for temp_set_on")
    print(message, TEMP)
    


loopCount=0

t1 = Thread(target = pulse)
t1.start()
t2 = Thread(target = temp)
t2.start()

myAWSIoTMQTTClient.subscribe(temp_request_topic,1,Callback_temp_request)



try:
    while True:
    
        message_temp = {}
        message_temp['message'] = topic_temp
        message_temp['sequence'] = TEMP
        messageJson_temp = json.dumps(message_temp)

        message_pulse = {}
        message_pulse['message'] = topic_pulse
        message_pulse['sequence'] = BPM
        messageJson_pulse = json.dumps(message_pulse)
        
        
        #message = myAWSIoTMQTTClient.publish(topic_temp,messageJson_temp,1)
        #print(message, BPM)
        #message = myAWSIoTMQTTClient.publish(topic_pulse,messageJson_pulse,1)
        #print(message, TEMP)
    
        for k in range(3):
            print(str(TEMP) + "*****" + str(BPM))
            time.sleep(1)
        
        loopCount +=1
except KeyboardInterrupt:
    print("keyboard interrupt")
    exit = 0
    t1.join()
    print("t1 joined")
    
    t2.join()
    print("t2 joined")
    
    print("terminated by keyboard")



