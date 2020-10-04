import json

class LightsActuation:

    def __init__(self, isOn, timestamp, targetId):
        self.isOn = isOn
        self.timestamp = timestamp
        self.targetId = targetId

    def __str__(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=2)

    def ToggleOn(self):
        self.isOn = "1"

    def ToggleOff(self):
        self.isOn = "0"

