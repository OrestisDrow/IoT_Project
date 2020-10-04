import json
class UserRegistration:
    def __init__(self, usrId,  thingId, interests ):
        self.usrId = usrId
        self.thingId = thingId
        self.interests = interests

    def __str__(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=2)
