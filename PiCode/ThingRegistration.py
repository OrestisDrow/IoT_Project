import json
class ThingRegistration:
    def __init__(self, thingId,  sensors ):
        self.thingId = thingId
        self.sensors = sensors
        
    def __str__(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=2)