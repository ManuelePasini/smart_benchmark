import datetime
import random
import json
import uuid
import numpy as np
import os
from utils import helper


def createPresence(dt, end, step, dataDir, size):

    with open(dataDir + "virtualSensor.json") as data_file:
        vs = json.load(data_file)
    for v in vs:
        if v["type_"]["id"] == "WiFiToPresence":
            pickedSensor = v
            break
        v["type_"] = {"id": v["type_"]["id"]}
        v["semanticObservationType"] = {"id": v["semanticObservationType"]["id"]}
        v["type"] = "VirtualSensor"

    with open(dataDir + "sensor.json") as data_file:
        data = json.load(data_file)
    sensors = []
    for sensor in data:
        if sensor["type_"]["id"] == "WiFiAP":
            sensors.append(sensor)
        sensor["type_"] = ({"id": sensor["type_"]["id"]},)
        sensor["owner"] = ({"id": sensor["owner"]["id"]},)
        sensor["type"] = "Sensor"

    with open(dataDir + "infrastructure.json") as data_file:
        rooms = json.load(data_file)
        rooms = [room for room in rooms if "_" not in room["id"]]

    with open(dataDir + "user.json") as data_file:
        users = json.load(data_file)

    numRooms = len(rooms)
    numUsers = len(users)

    fpObj = open("data/presenceData.json", "w")

    print("Creating Random Presence Data " + str(numUsers))

    type_ = pickedSensor["type_"]["semanticObservationType"]
    type_ = helper.deleteSOTypeAttributes(type_)
    pickedSensor = helper.deleteVirtualSensorAttributes(pickedSensor)
    count = 0
    buffer = {}
    sensorId = pickedSensor["id"]
    sensorTSPath = f"benchmark/datasets/{size}/timeseries/{sensorId}.json"
    os.makedirs(os.path.dirname(sensorTSPath), exist_ok=True)
    while dt < end:
        c = np.random.choice(numUsers, int(numUsers / 8), replace=False)
        for j in np.random.choice(numUsers, int(numUsers / 8), replace=False):
            id = str(uuid.uuid4())

            sobs = {
                "id": id,
                "timestamp": dt.strftime("%Y-%m-%d %H:%M:%S"),
                "virtualSensor": {"id": pickedSensor["id"]},
                "type_": {"id": type_["id"]},
                "semanticEntity": {"id": users[j]["id"]},
                "payload": {
                    "location": int(rooms[random.randint(0, numRooms - 1)]["id"])
                },
                "type": "Presence",
            }
            fpObj.write(json.dumps(sobs) + "\n")
            if sensorTSPath in buffer:
                buffer[sensorTSPath].append(sobs)
            else:
                buffer[sensorTSPath] = [sobs]

            if count % 200000 == 0:
                for sensorPath, observations in buffer.items():
                    with open(sensorPath, "a") as sensorFile:
                        sensorFile.write(
                            "\n".join(json.dumps(o) for o in observations) + "\n"
                        )
                    buffer[sensorPath] = []
                print("{} Random Presence Observations".format(count))

            count += 1
        dt += step
    for sensorPath, observations in buffer.items():
        with open(sensorPath, "a") as sensorFile:
            sensorFile.write("\n".join(json.dumps(o) for o in observations) + "\n")
        buffer[sensorPath] = []
    fpObj.close()
