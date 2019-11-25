import time
import json
import sys
import RPi.GPIO as gpio

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

host = "azjctapxbp7sc-ats.iot.us-east-2.amazonaws.com"
rootCAPath = "/home/pi/certification/RootCA.crt"
certificatePath = "/home/pi/certification/a75d9d3b12-certificate.pem.crt"
privateKeyPath = "/home/pi/certification/a75d9d3b12-private.pem.key" 
port = 8883
clientId = "IoT_System_Client"
topic = "IoT_System_Email_Alarm"

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

sensor = 21
gpio.setmode(gpio.BCM)
gpio.setup(sensor, gpio.OUT)
def customCallback(client, userdata, message):
	print("Received a new message: ")
	print(message.payload)
	print("from topic: ")
	print(message.topic)
	print("--------------\n\n")
	if message.payload == '1':
		gpio.output(sensor,True)
	else:
		gpio.output(sensor, False)
     
	
	
myAWSIoTMQTTClient.subscribe(topic, 1, customCallback)

while True:
	sleep(1)


    


