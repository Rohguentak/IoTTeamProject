import getopt
import sys
from coapthon.server.coap import CoAP
#from exampleresources import AdvancedResource
from coapthon.resources.resource import Resource
from coapthon import defines

import sys
import RPi.GPIO as gpio

sensor=21
gpio.setmode(gpio.BCM)
gpio.setup(sensor,gpio.OUT)

value=0
class AdvancedResource(Resource):
    def __init__(self, name="Advanced"):
        super(AdvancedResource, self).__init__(name)
        self.payload = "Advanced resource"

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
    
    def render_GET_advanced(self, request, response):
        response.payload = self.payload
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
    try:
        server.listen(10)
        
    except KeyboardInterrupt:
        print "Server Shutdown"
        server.close()
            
if __name__ == "__main__" :
    main()
        