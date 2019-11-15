import time
import json
import sys
import RPi.GPIO as gpio

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient

host = "azjctapxbp7sc-ats.iot.us-east-2.amazonaws.com"
rootCAPath = "/home/pi/certification/RootCA.crt"
certificatePath = "/home/pi/certification/a75d9d3b12-certificate.pem.crt"
privateKeyPath = "/home/pi/certification/a75d9d3b12-private.pem.key" 
port = 8883
clientId = "IoT_System_Client"
topic = "IoT_System_Email_Alarm"
Thing_Name = "raspberrypi6"

Client = AWSIoTMQTTShadowClient(clientId)
Client.configureEndpoint(host, port)
Client.configureCredentials(rootCAPath, privateKeyPath, certificatePath)
Client.configureConnectDisconnectTimeout(10)
Client.configureMQTTOperationTimeout(5)
Client.connect()
Handler = Client.createShadowHandlerWithName(Thing_Name, True)
sensor = 21
gpio.setmode(gpio.BCM)
gpio.setup(sensor, gpio.OUT)
def Callback_func(payload, responseStatus, token):
	msg = json.index(payload)
	illuminance = msg{'state'}{'illuminance'}
	print()
	print('UPDATE: $aws/things/' + Thing_Name + '/shadow/update/#')
	print("payload = " + payload)
	print("responseStatus = " + responseStatus)
	print("token = " + token)

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
     
Handler.shadowRegisterDeltaCallback(Callback_func)

while True:
		
		time.sleep(1)


    


