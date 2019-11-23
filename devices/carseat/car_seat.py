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
clientId = "car_seat_pi"
temp_topic = "anklet/temp"

handfree_topic = "stroller/handfree"

neglect_topic = "car_seat/neglect"

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
     
	
# anklet/temp	
myAWSIoTMQTTClient.subscribe(temp_topic, 1, customCallback)
# stroller/handfree
myAWSIoTMQTTClient.subscribe(handfree_topic,1,customCallback)
# car/parent
myAWSIoTMQTTClient.subscribe(parent_topic,1,customCallback)

loopCount = 0

while True:

    message = {}
    message['message'] = "car_seat/neglect"
    message['sequence'] = loopCount
    messageJson = json.dumps(message)

    # car_seat/neglect
    message = myAWSIoTMQTTClient.publish(neglect_topic,messageJson,1)
    print(message, loopCount)
    
    time.sleep(3)
    loopCount +=1


