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

# if rfid tag is not scanned state, state 0. else rfid tag is scanned state. state 1
hand_free = 1
# unit: minute
neglect_judge_interval = 0.1
neglect_threshold_time = time.time()
car_seat_temp = 0
baby_is_in_car_seat = 0
neglect_alarm_on = 1

def Callback_for_handfree(client, userdata, message):
        global hand_free
        global neglect_alarm_on
        global neglect_threshold_time
        global neglect_judge_interval

	#print("Received a new message: ")
	#print(message.payload)
	#print("--------------\n")
        
        temp = json.loads(message.payload)
        hand_free = temp["sequence"]
        #print(hand_free)
        print("hand_free", hand_free , "is received\n");

        if(hand_free == 1):# rfid is not scanned state. setting neglect_threshold_time
            neglect_alarm_on = 1
            neglect_threshold_time = time.time() + (3)

#checking neglect with condition. temp of car_seat, fsr sensor, neglect time.
def neglect_alarm_condition():
    global hand_free
    global neglect_alarm_on
    global neglect_threshold_time
    global car_seat_temp
    global baby_is_in_car_seat
    if(neglect_alarm_on == 1 and hand_free == 1 and time.time() > neglect_threshold_time):#  car_seat_temp < 15 & baby_is_in_car_seat = 1
        neglect_alarm_on = 0
        return 1
    return 0

	
# anklet/temp	
myAWSIoTMQTTClient.subscribe(temp_topic, 1, customCallback)
# stroller/handfree
myAWSIoTMQTTClient.subscribe(handfree_topic,1,Callback_for_handfree)
# car/parent
myAWSIoTMQTTClient.subscribe(parent_topic,1,customCallback)

loopCount = 0

while True:

    if( neglect_alarm_condition() == 1): #check neglect and if neglect send msg to terminal
        print("send neglect alarm msg to terminal")
        message = {}
        message['message'] = "car_seat/neglect"
        message['sequence'] = 1
        messageJson = json.dumps(message)

        # car_seat/neglect
        message = myAWSIoTMQTTClient.publish(neglect_topic,messageJson,1)
        #print(message, 1)

    time.sleep(3)
    loopCount +=1


