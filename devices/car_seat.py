import time
import json
import sys
##import RPi.GPIO as gpio

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

host = "azjctapxbp7sc-ats.iot.ap-northeast-2.amazonaws.com"
rootCAPath = "./RootCA.crt"
certificatePath = "./3cfe6893cf-certificate.pem.crt"
privateKeyPath = "./3cfe6893cf-private.pem.key" 
port = 8883
clientId = "client2"
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

##sensor = 21
##gpio.setmode(gpio.BCM)
#3gpio.setup(sensor, gpio.OUT)
def customCallback(client, userdata, message):
	print("Received a new message: ")
	print(message.payload)
	print("--------------\n\n")
	##if message.payload == '1':
	##	gpio.output(sensor,True)
	##else:
	##	gpio.output(sensor, False)
     
	
	
myAWSIoTMQTTClient.subscribe(topic, 1, customCallback)

while True:
	time.sleep(1)
