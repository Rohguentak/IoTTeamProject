import time
import json
import sys
import spidev
import os
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

import random
import signal

host = "azjctapxbp7sc-ats.iot.ap-northeast-2.amazonaws.com"

rootCAPath = "./RootCA.crt"
certificatePath = "./5bf4c37523-certificate.pem.crt"
privateKeyPath = "./5bf4c37523-private.pem.key"
port = 8883
clientId = "car_pi"

parent_topic = "car/parent"

# sub topic
gps_data_topic = "gps/log_data"



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

from collections import OrderedDict

stop = 0

def signal_handler(sig,frame):
	global stop
   	stop = 1

signal.signal(signal.SIGINT, signal_handler)

def load(filepath):
	with open(filepath) as json_file:
    		temp = json.load(json_file)
		return temp

def save_log_at_file(lat, lon ):
    Y_m_d = time.strftime('%Y-%m-%d',time.localtime(time.time()))

    H_m_s = time.strftime('%X',time.localtime(time.time()))
    H_m_s = H_m_s.replace('/',':')

    time_slot = Y_m_d + "T" + H_m_s + ".000Z"
    print(time.time())
    print(time_slot)
    file = "./log_data/" + Y_m_d + "T" + H_m_s + ".log"

    data = OrderedDict()
    if os.path.exists(file):
        fp = open(file,'a')
	data["time_slot"] = str(time_slot)
	data["event_geo"] = {'lat':lat,'lon':lon}
        fp.write(json.dumps(data))
	fp.write("\n")
	return fp
    else :
        fp = open(file,'w')
	data["time_slot"] = str(time_slot)
        data["event_geo"] = {'lat':lat,'lon':lon}
        fp.write(json.dumps(data))
	fp.write("\n")
     	return fp



def Callback_for_gps_data(client, userdata, message):
    global temp_to_set
    temp = json.loads(message.payload)# terminal/temp_set_on data is baby's temperature.
    lat = temp["lat"]
    lon = temp["lon"]
    fp = save_log_at_file(str(lat),str(lon))
    fp.close()
    print(lat)
    print(lon)



myAWSIoTMQTTClient.subscribe(gps_data_topic, 1, Callback_for_gps_data)
#

i=0

while (stop == 0):
    	#lat_random = round(random.random(),6) + 37
    	#lon_random = round(random.random(),6) + 121
    	#fp = save_log_at_file(lat_random, lon_random)
	#fp.close()
    	#print(lat_random, lon_random)
	print(str(i)+"\n")
	i = i+1
    	time.sleep(3)
	





