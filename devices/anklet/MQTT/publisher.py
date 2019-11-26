import time
import json
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import spidev
from threading import Thread


spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz = 1350000

BPM = 0
TEMP = 0
exit = 1
def analog_read(channel):
    r = spi.xfer2([1,(8+channel) << 4,0])
    adc_out = ((r[1]&3)<<8) + r[2]
    return adc_out



def pulse():
    global BPM
    global exit
    rate = [0] * 10         # array to hold last 10 IBI values
    sampleCounter = 0       # used to determine pulse timing
    lastBeatTime = 0        # used to find IBI
    P = 512                 # used to find peak in pulse wave, seeded
    T = 512                 # used to find trough in pulse wave, seeded
    thresh = 400            # used to find instant moment of heart beat, seeded
    amp = 100               # used to hold amplitude of pulse waveform, seeded
    firstBeat = True        # used to seed rate array so we startup with reasonable BPM
    secondBeat = False      # used to seed rate array so we startup with reasonable BPM


    IBI = 600               # int that holds the time interval between beats! Must be seeded
    Pulse = False           # "True" when User's live heartbeat is detected. "False" when not a "live beat
    lastTime = int(time.time()*1000)
    try:
      while exit == 1:
        for k in range(1,20):
            Signal = analog_read(0)
            currentTime = int(time.time()*1000)
            
            sampleCounter += currentTime - lastTime
            lastTime = currentTime
            
            N = sampleCounter - lastBeatTime

            # find the peak and trough of the pulse wave
            if Signal < thresh and N > (IBI/5.0)*3:     # avoid dichrotic noise by waiting 3/5 of last IBI
                if Signal < T:                          # T is the trough
                    T = Signal                          # keep track of lowest point in pulse wave 

            if Signal > thresh and Signal > P:
                P = Signal

            # signal surges up in value every time there is a pulse
            if N > 250:                                 # avoid high frequency noise
                if Signal > thresh and Pulse == False and N > (IBI/5.0)*3:       
                    Pulse = True                        # set the Pulse flag when we think there is a pulse
                    IBI = sampleCounter - lastBeatTime  # measure time between beats in mS
                    lastBeatTime = sampleCounter        # keep track of time for next pulse

                    if secondBeat:                      # if this is the second beat, if secondBeat == TRUE
                        secondBeat = False;             # clear secondBeat flag
                        for i in range(len(rate)):      # seed the running total to get a realisitic BPM at startup
                          rate[i] = IBI

                    if firstBeat:                       # if it's the first time we found a beat, if firstBeat == TRUE
                        firstBeat = False;              # clear firstBeat flag
                        secondBeat = True;              # set the second beat flag
                        continue

                    # keep a running total of the last 10 IBI values  
                    rate[:-1] = rate[1:]                # shift data in the rate array
                    rate[-1] = IBI                      # add the latest IBI to the rate array
                    runningTotal = sum(rate)            # add upp oldest IBI values

                    runningTotal /= len(rate)           # average the IBI values 
                    BPM= 60000/runningTotal       # how many beats can fit into a minute? that's BPM!

            if Signal < thresh and Pulse == True:       # when the values are going down, the beat is over
                Pulse = False                           # reset the Pulse flag so we can do it again
                amp = P - T                             # get amplitude of the pulse wave
                thresh = amp/2 + T                      # set thresh at 50% of the amplitude
                P = thresh                              # reset these for next time
                T = thresh

            if N > 2500:                                # if 2.5 seconds go by without a beat
                thresh = 512                            # set thresh default
                P = 512                                 # set P default
                T = 512                                 # set T default
                lastBeatTime = sampleCounter            # bring the lastBeatTime up to date        
                firstBeat = True                        # set these to avoid noise
                secondBeat = False                      # when we get the heartbeat back
                BPM= 0

            time.sleep(0.05)
            '''
            print(Signal)
            
            if   Signal > 760 : print('-----------------')
            elif Signal > 700 : print('---------------')
            elif Signal > 600 : print('-------------')
            elif Signal > 500 : print('-----------')
            elif Signal > 450 : print('---------')
            elif Signal > 400 : print('-------')
            
            else :              print('-')
            '''
    except KeyboardInterrupt:
        print("terminated by keyboard------pulse")
            
# pulse part




import Adafruit_DHT

def temp():
    sensor = Adafruit_DHT.DHT11
    pin = 24
    global TEMP
    global exit
    try:
        while exit==1 :
            h, t = Adafruit_DHT.read_retry(sensor, pin)
            
            if h is not None and t is not None :
                print("Temperature = {0:0.1f}%".format(t))
                TEMP = t
        
            else :
                print('Read error')
            time.sleep(5)
    except KeyboardInterrupt:
        print("terminated by keyboard-------temp")

#temp part

































port = 8883

host = "azjctapxbp7sc-ats.iot.ap-northeast-2.amazonaws.com"
rootCAPath = "./anklet_pi/RootCA.crt"
certificatePath = "./anklet_pi/bc1b2abd97-certificate.pem.crt"
privateKeyPath = "./anklet_pi/bc1b2abd97-private.pem.key"
clientId = "anklet_pi"
topic_temp = "anklet/temp"
topic_pulse = "anklet/pulse"



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



def Callback_func(payload, responseStatus, token):
    print()
    print('UPDATE: $aws/things/' + Thing_Name + '/shadow/update/#')
    print("payload = " + payload)
    print("responseStatus = " + responseStatus)
    print("token = " + token)


loopCount=0

t1 = Thread(target = pulse)
t1.start()
t2 = Thread(target = temp)
t2.start()

try:
    while True:
    
        message_temp = {}
        message_temp['message'] = topic_temp
        message_temp['sequence'] = TEMP
        messageJson_temp = json.dumps(message_temp)

        message_pulse = {}
        message_pulse['message'] = topic_pulse
        message_pulse['sequence'] = BPM
        messageJson_pulse = json.dumps(message_pulse)
        
        
        message = myAWSIoTMQTTClient.publish(topic_temp,messageJson_temp,1)
        print(message, BPM)
        message = myAWSIoTMQTTClient.publish(topic_pulse,messageJson_pulse,1)
        print(message, TEMP)
    
        for k in range(3):
            print(str(TEMP) + "*****" + str(BPM))
            time.sleep(1)
        
        loopCount +=1
except KeyboardInterrupt:
    print("keyboard interrupt")
    exit = 0
    t1.join()
    print("t1 joined")
    
    t2.join()
    print("t2 joined")
    
    print("terminated by keyboard")



