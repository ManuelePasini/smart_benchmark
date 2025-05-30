import datetime
import random
import json
import uuid
import numpy as np

from utils import helper
from extrapolate import Scale


def createWemoObservations(dt, end, step, dataDir):

    with open(dataDir + "sensor.json") as data_file:
        data = json.load(data_file)

    sensors = []

    for sensor in data:
        if sensor["type_"]["id"] == "WeMo":
            sensors.append(sensor)
    num = len(sensors)

    with open(dataDir + "infrastructure.json") as data_file:
        geometries = json.load(data_file)

    fpObj = open("data/wemoData.json", "w")

    print("Creating Random Wemo Observations")

    count = 0
    while dt < end:

        for i in np.random.choice(num, num, replace=False):
            pickedSensor = helper.deleteSensorAttributes(sensors[i])
            id = str(uuid.uuid4())
            geom_id = random.choice(sensors[i]["coverage"])["id"]
            obs = {
                "id": id,
                "timestamp": dt.strftime("%Y-%m-%d %H:%M:%S"),
                "sensor": {"id": pickedSensor["id"]},
                "location": {
                    k: v
                    for k, v in random.choice(
                        [
                            geometry
                            for geometry in geometries
                            if geometry["id"] == geom_id
                        ][0]["geometry"]
                    ).items()
                    if k != "id"
                },
                "payload": {
                    "currentMilliWatts": random.randint(1, 100),
                    "onTodaySeconds": random.randint(1, 3600),
                },
            }
            fpObj.write(json.dumps(obs) + "\n")

            if count % 200000 == 0:
                print("{} Random Wemo Observations".format(count))
            count += 1

        dt += step

    fpObj.close()


def createIntelligentWemoObs(
    origDays,
    extendDays,
    origSpeed,
    extendSpeed,
    origSensor,
    extendSensor,
    speedScaleNoise,
    timeScaleNoise,
    deviceScaleNoise,
    dataDir,
):

    with open(dataDir + "observation.json") as data_file:
        observations = json.load(data_file)

    seedFile = open("data/seedWemo.json", "w")
    for observation in observations:
        if observation["sensor"]["type_"]["id"] == "WeMo":
            seedFile.write(json.dumps(observation) + "\n")
    seedFile.close()

    seedFile = "data/seedWemo.json"
    outputFile = "data/wemoData.json"
    scale = Scale(
        dataDir,
        seedFile,
        outputFile,
        origDays,
        extendDays,
        origSpeed,
        extendSpeed,
        origSensor,
        extendSensor,
        ["currentMilliWatts", "onTodaySeconds"],
        speedScaleNoise,
        timeScaleNoise,
        deviceScaleNoise,
        int,
    )

    scale.speedScale()
    scale.deviceScale()
    scale.timeScale()
