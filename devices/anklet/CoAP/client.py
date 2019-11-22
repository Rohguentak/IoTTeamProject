from coapthon.client.helperclient import HelperClient
import random

host = "192.168.0.121"
port = 5683
path = "advanced/"

n = random.randrange(0,40)

client = HelperClient(server=(host, port))
response = client.put(path, payload=str(n))
print(response.pretty_print())

response = client.get(path)
print(response.pretty_print())

client.stop()