import time
import json
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

loopCount = 0
while True:
	message = {}
	message['message'] = 'hello world'
	print(message)
	message['sequence'] = loopCount
	print(message)
	messageJson = json.dumps(message)
	
	myAWSIoTMQTTClient.publish(topic, messageJson, 1)
	print('Published topic %s: %s\n' % (topic, messageJson))
	loopCount += 1
	time.sleep(1)
