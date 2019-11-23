import time
import json
import sys
##import RPi.GPIO as gpio

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

host = "azjctapxbp7sc-ats.iot.ap-northeast-2.amazonaws.com"
rootCAPath = "./RootCA.crt"
certificatePath = "./6ca402f832-certificate.pem.crt"
privateKeyPath = "./6ca402f832-private.pem.key" 
port = 8883
clientId = "terminal_pc"
car_seat_neglect_topic = "car_seat/neglect"

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


def customCallback(client, userdata, message):
	#print("Received a new message: ")
	#print(message.payload)
	#print("--------------\n\n")
        temp = json.loads(message.payload)
        neglect = temp["sequence"]
        if(neglect == 1):
            print("baby is neglected\n")
	##if message.payload == '1':
	##	gpio.output(sensor,True)
	##else:
	##	gpio.output(sensor, False)
     
	
	
myAWSIoTMQTTClient.subscribe(car_seat_neglect_topic, 1, customCallback)

while True:
	time.sleep(1)
