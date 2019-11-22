import random
import time
import json
import spidev
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient



Client_ID = "Publisher"
Thing_Name = "anklet_pi"
Host_Name = "azjctapxbp7sc-ats.iot.ap-northeast-2.amazonaws.com"#End Point
Root_CA = "/home/pi/workspace/MQTT/anklet_pi/RootCA.crt"
Private_Key = "/home/pi/workspace/MQTT/anklet_pi/bc1b2abd97-private.pem.key"
Cert_File = "/home/pi/workspace/MQTT/anklet_pi/bc1b2abd97-certificate.pem.crt"

Client = AWSIoTMQTTShadowClient(Client_ID)
Client.configureEndpoint(Host_Name, 8883)
Client.configureCredentials(Root_CA, Private_Key, Cert_File)
Client.configureConnectDisconnectTimeout(10)
Client.configureMQTTOperationTimeout(5)
Client.connect()


def Callback_func(payload, responseStatus, token):
	print()
	print('UPDATE: $aws/things/' + Thing_Name + '/shadow/update/#')
	print("payload = " + payload)
	print("responseStatus = " + responseStatus)
	print("token = " + token)

Handler = Client.createShadowHandlerWithName(Thing_Name, True)

while True:
	illuminance = 1
	msg = {"state": {"desired": {"illuminance": illuminance}}}
	
	Handler.shadowUpdate(json.dumps(msg), Callback_func, 5)#Publish
	
	time.sleep(3)
