import time
import datetime
import paho.mqtt.client as mqtt
import random
from Report import Report
from sense_hat import SenseHat
import json
import pickle
from Actuations import LightsActuation
from ThingRegistration import ThingRegistration


global currState
currState = "0"

#GetSensorValues from sensorhat
def GetSensorValues(report):
    sense = SenseHat()
    report.timestamp = str(datetime.datetime.now())
    report.temperature = sense.get_temperature()
    report.humidity = sense.get_humidity()
    report.pressure = sense.get_pressure()
    report.thingId = "1"
    
    
#Mqtt callback functions
def on_log(client, userdata, level, buf):
    print("log:" + buf)
    
def on_connect(client, userdata, flags, rc):
    if rc==0:
        print("connection established")
    else:
        print("could not establish connection:", rc)
        
def on_disconnect(client, userdata, flags, rc=0):
    print("Disconnected with result code: " + str(rc))
    
def on_message(client, userdata, msg):
    actuation = pickle.loads(msg.payload)
    #Checking if the actuation is targeted for this device
    global currState
    if actuation.isOn != currState and actuation.targetId == "1":
        currState = actuation.isOn
        if str(actuation.isOn) == "1":
            sense.set_pixels(actuationScreen)
            print("LIGHTS ON BABY")
        else:
            sense.clear()
            print("lights off..")

#SenseHat Displays
global X, I, O, actuationScreen, sense
sense = SenseHat()
X =  [255, 0, 0]
I = [0, 255, 0]
O = [0, 0, 255]
actuationScreen = [
I, O, O, X, X, O, O, I,
I, O, X, O, O, X, O, I,
I, O, O, O, O, X, O, I,
I, O, O, O, X, O, O, I,
I, O, O, X, O, O, O, I,
I, O, O, X, O, O, O, I,
I, O, O, O, O, O, O, I,
I, O, O, X, O, O, O, I
]

broker_addr = "iot.eclipse.org"
client = mqtt.Client("IoTClient")
#bindings
client.on_connect = on_connect
client.on_disconnect = on_disconnect
#client.on_log = on_log
client.on_message = on_message

#establishing server connection
print("connecting to broker...",broker_addr)
client.connect(broker_addr)
time.sleep(1)
print("connected!")

#Registration to discord bot client
print("making registration to the bot client...")
reg = ThingRegistration("1",["Temperature", "Humidity", "Pressure"])
payload = pickle.dumps(reg)
client.publish("discord/thingRegistration", payload, 0)
time.sleep(1)
print("registration done!")

#IoT thing routine start
report = Report(str(datetime.datetime.now()) ,10,10,10,"1")
GetSensorValues(report)
client.loop_start()
client.subscribe("discord/actuations")
time.sleep(1)

#client.subscribe("discord/inpt")
print("reporting every 10 sec")
while 1:
    payload = pickle.dumps(report)
    client.publish("discord/inpt", payload, 0, True)
    GetSensorValues(report)
    time.sleep(10)
client.disconnect()
client.loop_stop()

