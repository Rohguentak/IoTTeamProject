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
# sub topics
car_seat_neglect_topic = "car_seat/neglect"
topic_pulse = "anklet/pulse"
anklet_temp_topic = "anklet/temp"

# pub topics
temp_request_topic = "terminal/temp_request" # for request baby's temperature to anklet
temp_set_on_topic = "terminal/temp_set_on"

# inital value
TEMP = -200

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
	#if message.payload == '1':
	##	gpio.output(sensor,True)
	##else:
	##	gpio.output(sensor, False)
     
def customCallback_dummy(client, userdata, message):
        print("Received a new message: ")
	print(message.payload)
	print("--------------\n\n")
	
def Callback_anklet_temp(client, userdata, message):
        global TEMP
        temp = json.loads(message.payload)
        anklet_temp = temp["sequence"]
        print("temp : ")
        print(anklet_temp)
        print("\n")
        TEMP = anklet_temp

def send_temp_set_request():
        global TEMP
        message_temp_request = {}
        message_temp_request['message'] = temp_request_topic
        message_temp_request['sequence'] = 1
        messageJson_temp_request = json.dumps(message_temp_request)
        
        
        message = myAWSIoTMQTTClient.publish(temp_request_topic,messageJson_temp_request,1)
       	while True: 
        	if( TEMP != -200):
            		message_temp_set_on = {}
            		message_temp_set_on['message'] = temp_set_on_topic
            		message_temp_set_on['sequence'] = TEMP
            		messageJson_temp_set_on = json.dumps(message_temp_set_on)
        
            		message = myAWSIoTMQTTClient.publish(temp_set_on,messageJson_temp_set_on,1)
            		print("sent to carseat temp : ")
            		print(message.palyoad)
            		TEMP = -200
			break
            


myAWSIoTMQTTClient.subscribe(car_seat_neglect_topic, 1, customCallback)
myAWSIoTMQTTClient.subscribe(topic_pulse, 1, customCallback_dummy)
myAWSIoTMQTTClient.subscribe(anklet_temp_topic, 1, Callback_anklet_temp)

# do temp set request
send_temp_set_request()

while True:
        	time.sleep(1)
