import time
import json
import sys

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

def send_parent_is_in_car(temp):
    global parent_is_in_car
    if (temp == 1): # fsr_sensor
        if(parent_is_in_car == 0):
            #send parent is came.
            parent_is_in_car = 1
            message = {}
            message['message'] = "car/parent"
            message['sequence'] = parent_is_in_car
            messageJson = json.dumps(message)

            message = myAWSIoTMQTTClient.publish(parent_topic,messageJson,1)
            print("parent is in car")
    
    elif (temp == 0): # fsr_sensor
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
    
    temp = input()
    send_parent_is_in_car(temp)
    time.sleep(3)




