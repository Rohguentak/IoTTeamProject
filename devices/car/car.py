import time
import json
import sys
import spidev

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

host = "azjctapxbp7sc-ats.iot.ap-northeast-2.amazonaws.com"

rootCAPath = "./RootCA.crt"
certificatePath = "./5bf4c37523-certificate.pem.crt"
privateKeyPath = "./5bf4c37523-private.pem.key"
port = 8883
clientId = "car_pi"
parent_topic = "car/parent"

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



parent_is_in_car = 1
fsr_sensor = 0

fsr_sensor_adc_channel = 1

spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz = 1000000


def analog_read(channel):
    r = spi.xfer2([1,(8+channel) <<4,0])
    adc_out = ((r[1]&3<<8)+r[2])
    return adc_out

def parent_is_in_car():
    temp = analog_read(fsr_sensor_adc_channel)
    print(temp)
    if (temp > 25) :
        return 1
    else :
        return 0


def send_parent_is_in_car():
    global parent_is_in_car
    if (parent_is_in_car() == 1): # currently parent is in car
        if(parent_is_in_car == 0):
            #send parent is came.
            parent_is_in_car = 1
            message = {}
            message['message'] = "car/parent"
            message['sequence'] = parent_is_in_car
            messageJson = json.dumps(message)

            message = myAWSIoTMQTTClient.publish(parent_topic,messageJson,1)
            print("parent is in car")
    
    elif (parent_is_in_car() == 0): # currently parent is not in car
        if(parent_is_in_car == 1): 
            #send parent is gone.
            parent_is_in_car = 0
            message = {}
            message['message'] = "car/parent"
            message['sequence'] = parent_is_in_car
            messageJson = json.dumps(message)

            message = myAWSIoTMQTTClient.publish(parent_topic,messageJson,1)
            print("parent is not in car")




while True:
    
    send_parent_is_in_car()
    time.sleep(3)




