# IoT-Project
This is a personal project which i developed in 2018. A more extensive explanation of the project and the use case it was trying to address exists in the presentation.pdf file (in Greek).

## Brief Explanation in English
This project's use case is something like: I am not at home and i want to be able to do the things below: 
- Have remote access to multiple sensor readings and sensor types in my home (e.g. temperature, humidity etc).
- Can perform some kind of actuation remotely, such as lighting up the sense hat pixel screen by simply sending a message from my phone.
- Have an automation: In this specific project, I implemented and automation service that if the temp sensor gets a high temp reading that indicates fire, then i will be 
  notified through message by the discord bot on my phone.
  
More info:
- PiCode is supposed to run on a raspberry pi with a sense hat extension. The required libraries have to be installed.
- BotCode can be run wherever (even in Pi) but i am treating pi as a low-resource limited-capability sensor that is able only for limited and specific actions, so I developed it on my laptop.

What does RPi do?:
- Uses the MQTT protocol and a public broker for external communication with the discord bot (registration, sensor reading publish etc).
- Registers itself through an established registration process unto the bot as an IoT thing. The concept was that multiple things would register unto the bot but of course i only had 1 Rpi so only 1 thing.
- Reports sensor values to the MQTT broker regularly so that the discord bot can use them if needed.  
- Listens to the MQTT topic for actuations and when the correct message is sent it performs the !lights_on/off actuation on the sense hat.

What does the bot do?:
- Controls the discord bot fully.
- Communicates with other discord users who have registered unto the bot. The user can interact with the bot using specific commands like !register, !report etc.
- Communicates with the IoT things through MQTT broker. Keeps registrations.
- Runs the fire notification Service if a user is intrested
- Sends the actuation message that would trigger the actual !lights_on/off actuation. 
