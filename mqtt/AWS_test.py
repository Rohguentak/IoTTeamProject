import time
import random
import json
import spidev
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient

spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz = 1350000

Client_ID = "IoT_System_Client"
Thing_Name = "raspberrypi6"                   
Host_Name = "azjctapxbp7sc-ats.iot.us-east-2.amazonaws.com"       
Root_CA = "/home/pi/certification/RootCA.crt"             
Private_Key = "/home/pi/certification/a75d9d3b12-private.pem.key"             
Cert_File = "/home/pi/certification/a75d9d3b12-certificate.pem.crt"   

Client = AWSIoTMQTTShadowClient(Client_ID)
Client.configureEndpoint(Host_Name, 8883)
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
def analog_read(channel):
    r = spi.xfer2([1,(8+channel) <<4,0])
    adc_out = ((r[1]&3<<8)+r[2])
    return adc_out

reading = analog_read(0)
time.sleep(5)
illuminance = reading
msg = {"state": {"reported": {"illuminance": illuminance}}}
    
Device.shadowUpdate(json.dumps(msg), Callback_func, 5)
    
time.sleep(10)
