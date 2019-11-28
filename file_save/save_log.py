import time
import os

def gen_one_set_save(lat, lon ):
    Y_m_d = time.strftime('%Y-%m-%d',time.localtime(time.time()))

    H_m_s = time.strftime('%x',time.localtime(time.time()))
    H_m_s = H_m_s.replace('/',':')

    time_slot = Y_m_d + "T" + H_m_s

    file = "./" + Y_m_d + ".log"

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
   
gen_one_set_save("37.554648","126.972559");
'''
f = open("./test.log",'w')
data1 = "{\"time_slot\":\"2013-12-31T15:00:00.000Z\",\"event_geo\":{\"lat\":37.554648,\"lon\":126.972559}}"
data = gen_one_set("37.554648","126.972559")



f.write(data)
f.close()

fp = open("./test1.log",'w')
fp.write(data1)
fp.close()

fpp = open("./test.log",'a')
fpp.write(data1)
fpp.close()

'''



