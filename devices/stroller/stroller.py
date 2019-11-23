#!/usr/bin/env python
# -*- coding: utf8 -*-
#
#    Copyright 2014,2018 Mario Gomez <mario.gomez@teubi.co>
#
#    This file is part of MFRC522-Python
#    MFRC522-Python is a simple Python implementation for
#    the MFRC522 NFC Card Reader for the Raspberry Pi.
#
#    MFRC522-Python is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    MFRC522-Python is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with MFRC522-Python.  If not, see <http://www.gnu.org/licenses/>.
#

import RPi.GPIO as GPIO
import MFRC522
import signal
import time



import json
import sys

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

host = "azjctapxbp7sc-ats.iot.ap-northeast-2.amazonaws.com"

rootCAPath = "./stroller_pi/RootCA.crt"
certificatePath = "./stroller_pi/c288f6c0db-certificate.pem.crt"
privateKeyPath = "./stroller_pi/c288f6c0db-private.pem.key"
port = 8883
clientId = "stroller_pi"
handfree_topic = "stroller/handfree"

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




continue_reading = True

# each rfid scan duration is 0.5 sec.
scan_time = 0.5

# each rfid scan duration's intrval is 5 sec.
scan_interval = 5

# if rfid is not scanned, state 0. else rfid is scanning key card rfid, state 1.
hand_free = 0

# Capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
    global continue_reading
    #print "Ctrl+C captured, ending read."
    continue_reading = False

# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

# parent's rfid card's uid
card_uid = [151,58,21,98]

def read_card():
    global continue_reading
    
    count =0
    
    max_time_end = time.time() + (scan_time)
    # This loop keeps checking for chips. If one is near it will get the UID and authenticate
    while continue_reading:
    
        # Scan for cards    
        (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

        # Get the UID of the card
        (status,uid) = MIFAREReader.MFRC522_Anticoll()

        # If we have the UID, continue
        if status == MIFAREReader.MI_OK:

            # Print UID
            #print "Card read UID: %s,%s,%s,%s" % (uid[0], uid[1], uid[2], uid[3])
            for i in range(3):
                if uid[i] == card_uid[i]:
                    count = count+1
           
        if time.time() > max_time_end:
            break
    return count

while continue_reading:
    card_present_time = read_card()
    if card_present_time >0:
        if hand_free == 0:
            #send msg parent is behind the stroller
            print("parent is here now")
            hand_free = 1
            message = {}
            message['message'] = "stroller/handfree"
            # not hand free so send 0
            message['sequence'] = 0
            messageJson = json.dumps(message)
            
            message = myAWSIoTMQTTClient.publish(handfree_topic,messageJson,1)
            #print(message, 0)
    
        card_present_time =0
    
    else:
        if hand_free == 1:
            #send msg parent is leave the stroller.
            print("parent is gone")
            hand_free =0
            message = {}
            message['message'] = "stroller/handfree"
            # hand free so send 1
            message['sequence'] = 1
            messageJson = json.dumps(message)

            message = myAWSIoTMQTTClient.publish(handfree_topic,messageJson,1)
            #print(message, 1)
    

    time.sleep(scan_interval)

GPIO.cleanup()
