import time
import json
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
import spidev
import time

spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz = 1350000


port = 8883

'''
Thing_Name = "raspberrypi5"
Host_Name = "azjctapxbp7sc-ats.iot.us-east-2.amazonaws.com"
Root_CA = "/home/pi/AWS/RootCA.crt"
Cert_File = "/home/pi/AWS/f58824458b-certificate.pem.crt"
Private_Key = "/home/pi/AWS/f58824458b-private.pem.key"
Client_ID = "IoT_System_Client2"
topic = 'IoT_System_Email_Alarm'

'''
topic = 'IoT_System_Email_Alarm'
Thing_Name = "anklet_pi"


Host_Name = "azjctapxbp7sc-ats.iot.ap-northeast-2.amazonaws.com"
Root_CA = "/home/pi/workspace/MQTT/anklet_pi/RootCA.crt"
Cert_File = "/home/pi/workspace/MQTT/anklet_pi/bc1b2abd97-certificate.pem.crt"
Private_Key = "/home/pi/workspace/MQTT/anklet_pi/bc1b2abd97-private.pem.key"
Client_ID = "anklet"




Client = AWSIoTMQTTShadowClient(Client_ID)
Client.configureEndpoint(Host_Name, port)
Client.configureCredentials(Root_CA, Private_Key, Cert_File)
Client.configureConnectDisconnectTimeout(10)
Client.configureMQTTOperationTimeout(5)
Client.connect()

Device = Client.createShadowHandlerWithName(Thing_Name, True)

def Callback_func(payload, responseStatus, token):
    print()
    print('UPDATE: $aws/things/' + Thing_Name + '/shadow/update/#')
    print("payload = " + payload)
    print("responseStatus = " + responseStatus)
    print("token = " + token)


i=2
j=7
while True:
    
    msg = {"state": {"desired": {"illuminance": i}}}


    Device.shadowUpdate(json.dumps(msg), Callback_func, 5)

    time.sleep(3)
    i=(i+15)%100 + 100
    j=(j+7)%100




