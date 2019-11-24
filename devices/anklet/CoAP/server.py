import time
import json
import getopt
import sys
import spidev
from coapthon.server.coap import CoAP
#from exampleresources import AdvancedResource
from coapthon.resources.resource import Resource
from coapthon import defines
from threading import Thread

spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz = 1350000

BPM = 0
TEMP = 0
def analog_read(channel):
    r = spi.xfer2([1,(8+channel) << 4,0])
    adc_out = ((r[1]&3)<<8) + r[2]
    return adc_out



def pulse():
    global BPM
    rate = [0] * 10         # array to hold last 10 IBI values
    sampleCounter = 0       # used to determine pulse timing
    lastBeatTime = 0        # used to find IBI
    P = 512                 # used to find peak in pulse wave, seeded
    T = 512                 # used to find trough in pulse wave, seeded
    thresh = 525            # used to find instant moment of heart beat, seeded
    amp = 100               # used to hold amplitude of pulse waveform, seeded
    firstBeat = True        # used to seed rate array so we startup with reasonable BPM
    secondBeat = False      # used to seed rate array so we startup with reasonable BPM


    IBI = 600               # int that holds the time interval between beats! Must be seeded
    Pulse = False           # "True" when User's live heartbeat is detected. "False" when not a "live beat
    lastTime = int(time.time()*1000)
    while True:
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




































class AdvancedResource(Resource):
    def __init__(self, name="Advanced"):
        super(AdvancedResource, self).__init__(name)
        self.payload = "Advanced resource"
    '''
    def render_PUT_advanced(self, request, response):
        self.payload = request.payload
        from coapthon.messages.response import Response
        assert(isinstance(response, Response))
        response.payload = "Response changed through PUT"
        
        value = int(request.payload)
        print("put value : " + request.payload)
        if (value>20): gpio.output(sensor, False)
        else: gpio.output(sensor, False)
        
        response.code = defines.Codes.CHANGED.number
        return self, response
    '''
    
    def render_GET_advanced(self, request, response):
        response.payload = "BPM:" + str(BPM) + ", temp:" + str(TEMP)
        response.max_age = 20
        response.code = defines.Codes.CONTENT.number
        return self, response

class CoAPServer(CoAP):
    def __init__(self, host, port, multicast=False):
        CoAP.__init__(self, (host, port), multicast)
        self.add_resource('advanced/', AdvancedResource())
        
        print "CoAP Server start on " + host + ":" + str(port)
   

        
def main():
    ip = "192.168.0.121"
    port = 5683
    
    

    server = CoAPServer(ip, port)
    print (server)
    
    t1 = Thread(target = pulse)
    t1.start()
    
    try:
        server.listen(10)
        
    except KeyboardInterrupt:
        print "Server Shutdown"
        server.close()
            
if __name__ == "__main__" :
    main()
        