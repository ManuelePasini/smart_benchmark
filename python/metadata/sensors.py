import random
import json
import uuid


def parseSensor(sensor):
    sensor["coverage"] = [{"id": coverage["id"]} for coverage in sensor["coverage"]]
    sensor["type_"] = {"id": sensor["type_"]["id"]}
    sensor["owner"] = {"id": sensor["owner"]["id"]}
    sensor["infrastructure"] = {"id": sensor["infrastructure"]["id"]}
    sensor["type"] = "Sensor"
    return sensor


def createSensors(numWifi, numWemo, numTemperature, src, dest):

    with open(src + "sensor.json") as data_file:
        sensors = json.load(data_file)
    for sensor in sensors:
        sensor["type"] = "Sensor"

    with open(src + "user.json") as data_file:
        users_json = json.load(data_file)
        users = [{"id": user["id"]} for user in users_json]

    with open(src + "infrastructure.json") as data_file:
        rooms_json = json.load(data_file)
        rooms = [{"id": room["id"]} for room in rooms_json]

    wifiSensors = []
    wemoSensors = []
    temperatureSensors = []

    print("Creating Sensors")

    for sensor in sensors:

        if sensor["type_"]["id"] == "WiFiAP":
            wifiSensors.append(parseSensor(sensor))
        if sensor["type_"]["id"] == "Thermometer":
            temperatureSensors.append(parseSensor(sensor))
        if sensor["type_"]["id"] == "WeMo":
            wemoSensors.append(parseSensor(sensor))

    for i in range(numWifi - len(wifiSensors)):
        id = str(uuid.uuid4())
        copiedSensor = wifiSensors[random.randint(0, len(wifiSensors) - 1)]
        copiedRoom = rooms[random.randint(0, len(rooms) - 1)]
        sensor = {
            "id": id.replace("-", "_"),
            "name": "simSensor{}".format(i),
            "coverage": [
                {"id": coverage["id"]} for coverage in copiedSensor["coverage"]
            ],
            "sensorConfig": copiedSensor["sensorConfig"],
            "type_": {"id": copiedSensor["type_"]["id"]},
            "owner": {"id": copiedSensor["owner"]["id"]},
            "infrastructure": copiedRoom,
            "type": "Sensor",
        }
        sensors.append(sensor)

    for i in range(numWemo - len(wemoSensors)):
        id = str(uuid.uuid4())
        copiedSensor = wemoSensors[random.randint(0, len(wemoSensors) - 1)]
        owner = users[random.randint(0, len(users) - 1)]
        copiedRoom = rooms[random.randint(0, len(rooms) - 1)]
        sensor = {
            "id": id.replace("-", "_"),
            "name": "simSensor{}".format(i),
            "coverage": [
                {"id": coverage["id"]} for coverage in copiedSensor["coverage"]
            ],
            "sensorConfig": copiedSensor["sensorConfig"],
            "type_": {"id": copiedSensor["type_"]["id"]},
            "owner": {"id": owner["id"]},
            "infrastructure": copiedRoom,
            "type": "Sensor",
        }
        sensors.append(sensor)

    for i in range(numTemperature - len(temperatureSensors)):
        id = str(uuid.uuid4())
        copiedSensor = temperatureSensors[
            random.randint(0, len(temperatureSensors) - 1)
        ]
        owner = users[random.randint(0, len(users) - 1)]
        copiedRoom = rooms[random.randint(0, len(rooms) - 1)]
        sensor = {
            "id": id.replace("-", "_"),
            "name": "simSensor{}".format(i),
            "coverage": [
                {"id": coverage["id"]} for coverage in copiedSensor["coverage"]
            ],
            "sensorConfig": copiedSensor["sensorConfig"],
            "type_": {"id": copiedSensor["type_"]["id"]},
            "owner": {"id": owner["id"]},
            "infrastructure": copiedRoom,
            "type": "Sensor",
        }
        sensors.append(sensor)

    with open(dest + "sensor.json", "w") as writer:
        json.dump(sensors, writer, indent=4)


def createIntelligentSensors(numWemo, numTemperature, src, dest):

    with open(src + "sensor.json") as data_file:
        sensors = json.load(data_file)

    with open(src + "user.json") as data_file:
        users = json.load(data_file)

    wemoSensors = []
    temperatureSensors = []

    print("Creating Sensors")

    for sensor in sensors:
        if sensor["type_"]["id"] == "Thermometer":
            temperatureSensors.append(sensor)
        if sensor["type_"]["id"] == "WeMo":
            wemoSensors.append(sensor)

    for wemo in wemoSensors:
        for i in range(numWemo / len(wemoSensors)):
            id = str(uuid.uuid4())
            copiedSensor = wemo
            owner = users[random.randint(0, len(users) - 1)]
            sensor = {
                "id": id.replace("-", "_"),
                "name": "simSensor_{}_{}".format(copiedSensor["id"], i),
                "coverage": [
                    {"id": coverage["id"]} for coverage in copiedSensor["coverage"]
                ],
                "sensorConfig": copiedSensor["sensorConfig"],
                "type_": {"id": copiedSensor["type_"]["id"]},
                "owner": {"id": owner["id"]},
                "infrastructure": {"id": copiedSensor["infrastructure"]["id"]},
            }
            sensors.append(sensor)

    for tempSensor in temperatureSensors:
        for i in range(numTemperature / len(temperatureSensors)):
            id = str(uuid.uuid4())
            copiedSensor = tempSensor
            owner = users[random.randint(0, len(users) - 1)]
            sensor = {
                "id": id.replace("-", "_"),
                "name": "simSensor_{}_{}".format(copiedSensor["id"], i),
                "coverage": [
                    {"id": coverage["id"]} for coverage in copiedSensor["coverage"]
                ],
                "sensorConfig": copiedSensor["sensorConfig"],
                "type_": {"id": copiedSensor["type_"]["id"]},
                "owner": {"id": owner["id"]},
                "infrastructure": {"id": copiedSensor["infrastructure"]["id"]},
            }
            sensors.append(sensor)

    with open(dest + "sensor.json", "w") as writer:
        json.dump(sensors, writer, indent=4)
