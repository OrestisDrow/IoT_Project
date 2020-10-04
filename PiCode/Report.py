import json
import random

class Report:

    def __init__(self, timestamp, temperature, humidity, pressure, thingId):
        self.timestamp = timestamp
        self.temperature= temperature
        self.humidity = humidity
        self.pressure = pressure
        self.thingId = thingId

    def __str__(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=2)

    def GetDetails(self):
        return 'timestamp: {} \ntemperature: {} \nhumidity: {} \npressure: {}'.format(self.timestamp,
                                                                                      self.temperature,
                                                                                      self.humidity,
                                                                                      self.pressure)
    def UpdateValue(self, field, newValue):
        if field.upper() == 'TIMESTAMP':
            self.timestamp = newValue
        if field.upper() == 'TEMPERATURE':
            self.temperature = newValue
        if field.upper() == 'HUMIDITY':
            self.humidity = newValue
        if field.upper() == 'PRESSURE':
            self.pressure = newValue

    def GenerateRandomValues(self):
        self.timestamp = str(datetime.datetime.now())
        self.temperature = random.randrange(10,40,1)
        self.humidity = random.randrange(10,20,1)
        self.pressure = random.randrange(10,20,1)
        