import time
import json
import sys
import spidev
import os

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

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

def save_log_at_file(lat, lon ):
    Y_m_d = time.strftime('%Y-%m-%d',time.localtime(time.time()))

    H_m_s = time.strftime('%x',time.localtime(time.time()))
    H_m_s = H_m_s.replace('/',':')

    time_slot = Y_m_d + "T" + H_m_s + ".000Z"

    file = "./log_data/" + Y_m_d + ".log"

    if os.path.exists(file):
        fp = open(file,'a')
        data = "{\"time_slot\":"+ "\"" + time_slot + "\""
        data = data + "," + "\"event_geo\":"+ "{\"lat\":" + lat
        data = data + "," + "\"lon\":"+ lon + "}}"
        fp.write(data)
        fp.close()
    else :
        fp = open(file,'w')
        data = "{\"time_slot\":"+ "\"" + time_slot + "\""
        data = data + "," + "\"event_geo\":"+ "{\"lat\":" + lat
        data = data + "," + "\"lon\":"+ lon + "}}"
        fp.write(data)
        fp.close()
 


def Callback_for_gps_data(client, userdata, message):
    global temp_to_set
    temp = json.loads(message.payload)# terminal/temp_set_on data is baby's temperature.
    lat = temp["lat"]
    lon = temp["lon"]
    save_log_at_file(lat,lon)
    print(lat)
    print(lon)



myAWSIoTMQTTClient.subscribe(gps_data_topic, 1, Callback_for_gps_data)
#




while True:
    time.sleep(3)




