import threading
import time
import discord
from discord.ext.commands import Bot
from discord.ext import commands
import asyncio
import datetime
import pickle
import paho.mqtt.client as mqtt
from Report import Report
from Actuations import LightsActuation
from UserRegistration import UserRegistration
from ThingRegistration import ThingRegistration

#initializing some variables
global report, actuation, registeredThings, registeredUsers, fireRegisteredUserId, fireRegisteredMessageChannel
report = []                 #List of Reports for keeping track
actuation = []              #List of LightActuations for keeping track
registeredUsers = []        #Users that are currently registered to bot.
registeredThings = []       #Things that are registered to bot
fireRegisteredUserId = []    #list of user ids that have registered for fire notification
fireRegisteredMessageChannel = []


    #MQTT functions
def MQTTon_connect(client, userdata, flags, rc):
    if rc==0:
        print("connection established")
    else:
        print("could not establish connection:", rc)

def MQTTon_disconnect(client, userdata, flags, rc=0):
    print("Disconnected with result code: " + str(rc))

def MQTTon_message(client, userdata, msg):
    temp = pickle.loads(msg.payload)
    if type(temp) == Report:
        #Checking if the id of the thing that reported is known(has registered)
        if temp.thingId in [things.thingId for things in registeredThings]:
            report.append(temp)
            #print("report received:\n", report[-1])
        else:
            print("received report from unknown source")

    if type(temp) == ThingRegistration:
        registeredThings.append(temp)
        print("new thing registration\n", registeredThings[-1])

                #____________DISCORD PART____________
Client = discord.Client()
global client
client = commands.Bot(command_prefix="!")

async def fire_notification():
    while 1:
        if not fireRegisteredUserId:
            # Takes a break if noone is intrested in fire service
            #print("No fire registered users")
            await asyncio.sleep(5)
            continue

        #print("We got fire registered user")

        fieryChannels = fireRegisteredMessageChannel
        fieryRegistrations = [x for x in registeredUsers if x.usrId in fireRegisteredUserId]


        #Reporting back fiery reports
        j = 0
        for i in fieryRegistrations:
            R = [x for x in report if x.thingId == i.thingId]       #All the reports of the thing the fire registered user is intrested
            R = R[-1]                                               #We are intrested only on the latest report
            if float(R.temperature) > -220.65:
                await client.send_message(fieryChannels[j], "FIRE BRO\n" + str(R))
            j = j +1

        await asyncio.sleep(10)

        #'''


@client.event
async def on_ready():
    print("bot is ready!")
    client.loop.create_task(fire_notification())

@client.event
async def on_message(message):
    registereduserIds = [x.usrId for x in registeredUsers]

    if message.content == "!register":
        #Checking if user is new
        if message.author.id not in registereduserIds:

            #Checking what things are connected to this bot client
            thingIds = [tid.thingId for tid in registeredThings]
            await client.send_message(message.channel, "In which thing would you be intrested on subscribing?\nList of connected things to this bot client:\n" + str(thingIds) + "\n...?:")
            reply = await client.wait_for_message(author = message.author, channel = message.channel)
            targetThingId = reply.content

            #Checking what sensors the selected thing has
            snsrs = [x.sensors for x in registeredThings if x.thingId == targetThingId]
            await client.send_message(message.channel, "This thing has sensors of:\n" + str(snsrs) + "\nPick a sensor you are intrested in:")
            reply = await client.wait_for_message(author=message.author, channel=message.channel)
            targetSensor = reply.content
            targetSensor = targetSensor.split()

            #Checking if user input is valid
            if targetThingId in [x.thingId for x in registeredThings] and set(targetSensor).issubset(["Temperature","Humidity","Pressure"]):
                #Finishing the registration
                newRegistration = UserRegistration(message.author.id, targetThingId, targetSensor)
                registeredUsers.append(newRegistration)
                await client.send_message(message.channel, "User Registration completed: \nUserID =" + str(message.author.id) + "\nThingID =" + str(targetThingId) + "\nInterest = " + str(targetSensor))
            else:
                await client.send_message(message.channel,"Invalid registration input... aborting registration...")

        #The user already has a registration and wants to make a new one
        else:
            #finding the old registration and prompting user to make a new one
            oldReg = [t for t in registeredUsers if t.usrId == message.author.id]
            oldReg = oldReg[-1]

            await client.send_message(message.channel, "You already have a registration:\n" + str(oldReg) + "\nDo you want to make a new one?y/n")
            reply = await client.wait_for_message(author=message.author, channel=message.channel)

            if str(reply.content).lower() == "y":
                #Removing old registration from that user
                if oldReg.usrId in fireRegisteredUserId:
                    fireRegisteredUserId.remove(oldReg.usrId)

                registeredUsers.remove(oldReg)

                # Doing new registration from scratch as normal
                thingIds = [tid.thingId for tid in registeredThings]
                await client.send_message(message.channel,
                                          "In which thing would you be intrested on subscribing?\nList of connected things to this bot client:\n" + str(
                                              thingIds) + "\n...?:")
                reply = await client.wait_for_message(author=message.author, channel=message.channel)
                targetThingId = reply.content

                snsrs = [x.sensors for x in registeredThings if x.thingId == targetThingId]
                await client.send_message(message.channel, "This thing has sensors of:\n" + str(
                    snsrs) + "\nPick a sensor you are intrested in:")
                reply = await client.wait_for_message(author=message.author, channel=message.channel)
                targetSensor = reply.content
                targetSensor = targetSensor.split()

                if targetThingId in [x.thingId for x in registeredThings] and set(targetSensor).issubset(
                        ["Temperature", "Humidity", "Pressure"]):
                    newRegistration = UserRegistration(message.author.id, targetThingId, targetSensor)
                    registeredUsers.append(newRegistration)
                    await client.send_message(message.channel, "User Registration completed: \nUserID =" + str(
                        message.author.id) + "\nThingID =" + str(targetThingId) + "\nInterest = " + str(targetSensor))
                else:
                    await client.send_message(message.channel, "Invalid registration input... aborting registration...")




    # '''
    if message.author.id in registereduserIds:

        # Reviewing specific user's registration
        try:
            targetRegistration = [x for x in registeredUsers if x.usrId == message.author.id]
            targetRegistration = targetRegistration[-1]
        except:
            return

        if message.content == "!report":
            #Getting the latest report associated with specific user interests
            targetReport = [x for x in report if x.thingId == targetRegistration.thingId]
            targetReport = targetReport[-1]

            interests = str(targetRegistration.interests).lower()

            allInterests = ["temperature", "humidity", "pressure"]
            nonInterests = [x for x in allInterests if x not in interests]

            #Deleting from targetReport attributes that don't interest the user according to his registration
            for i in nonInterests:
                delattr(targetReport,str(i))

            await client.send_message(message.channel, targetReport)

        if message.content == "!lights_on":
            #Getting the targetId of the thing that we want to actuate on
            temp = [x.thingId for x in registeredUsers if x.usrId == message.author.id]
            temp = str(temp[-1])
            newActuation = LightsActuation("1", str(datetime.datetime.now()), temp)
            actuation.append(newActuation)
            await client.send_message(message.channel, "Turning on lights on thing " + temp + "...")

        if message.content == "!lights_off":
            temp = [x.thingId for x in registeredUsers if x.usrId == message.author.id]
            temp = str(temp[-1])
            newActuation = LightsActuation("0", str(datetime.datetime.now()), temp)
            actuation.append(newActuation)
            await client.send_message(message.channel, "Turning off lights on thing " + temp + "...")

        if message.content == "!fire_register":
            if message.author.id not in fireRegisteredUserId:
                fireRegisteredUserId.append(message.author.id)
                fireRegisteredMessageChannel.append(message.channel)
                await client.send_message(message.channel, "Subscribed to fire notification service, you will be notified if fire occurs")
            else:
                await client.send_message(message.channel, " You are already subscribed for fire notification service")
        if message.content == "!fire_unregister":
            if message.author.id in fireRegisteredUserId:
                fireRegisteredUserId.remove(message.author.id)
                fireRegisteredMessageChannel.remove(message.channel)

                await client.send_message(message.channel, "Unregistered from fire notification service")
            else:
                await client.send_message(message.channel, "You are not registered for fire notification")

class BotThread(threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name

    def run(self):
        client.run("NDM5NDk1MjA1ODc2NTMxMjIw.DcUS7g.SlWfniUayYDXRkUgVqhPO5m1fW8")

                # ____________MQTT PART____________
class MqttThread(threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name


    def run(self):
        broker_addr = "iot.eclipse.org"
        MQTTclient = mqtt.Client("BotClient")
        MQTTclient.on_connect = MQTTon_connect
        MQTTclient.on_disconnect = MQTTon_disconnect
        MQTTclient.on_message = MQTTon_message

        # connecting
        print("connecting to broker", broker_addr)
        MQTTclient.connect(broker_addr)
        time.sleep(1)

        # BotClient listening reports & registrations
        MQTTclient.loop_start()
        MQTTclient.subscribe("discord/inpt")
        MQTTclient.subscribe("discord/thingRegistration")

        # BotClient publishing actuations routine
        listsize = len(actuation)
        while 1:
            #Polling to see if actuation list has changed and then publishing the most recent one
            if listsize != len(actuation):
                payload = pickle.dumps(actuation[-1])
                MQTTclient.publish("discord/actuations", payload, 0)
                listsize = len(actuation)


            time.sleep(1)

        MQTTclient.disconnect()
        MQTTclient.loop_stop()

# Create new threads
thread1 = BotThread(1, "Bot")
thread2 = MqttThread(2, "Mqtt")

# Start new Threads
thread1.start()
thread2.start()

while 1:
    pass