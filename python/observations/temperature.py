import datetime
import random
import json
import uuid
import numpy as np
import os

from utils import helper
from extrapolate import Scale

sensor_buffers = {}
master_buffer = []
sensor_files = {}


def parseLocation(location):
    if isinstance(location, dict):
        return f"POINT({location['x']} {location['y']} {location['z']})"
    elif isinstance(location, list):
        points = [f"{coord['x']} {coord['y']} {coord['z']}" for coord in location]
        return f"LINESTRING({', '.join(points)})"
    else:
        raise ValueError("Unsupported location format: {}".format(type(location)))


def createTemperatureObservations(dt, end, step, dataDir, size):

    with open(dataDir + "sensor.json") as data_file:
        data = json.load(data_file)

    sensors = []

    for sensor in data:
        if sensor["type_"]["id"] == "Thermometer":
            sensors.append(sensor)
    num = len(sensors)

    with open(dataDir + "infrastructure.json") as data_file:
        geometries = json.load(data_file)

    fpObj = open("data/temperatureData.json", "w")

    print("Creating Random Temperature Observations")

    count = 0

    flush_interval = 50000  # o 10000 per test
    count = 0

    def flush_buffers():
        global master_buffer, sensor_buffers, sensor_files
        if master_buffer:
            fpObj.write("\n".join(json.dumps(o) for o in master_buffer) + "\n")
            master_buffer = []
        for path, obs in sensor_buffers.items():
            if obs:
                if path not in sensor_files:
                    os.makedirs(os.path.dirname(path), exist_ok=True)
                    sensor_files[path] = open(path, "a")
                sensor_files[path].write("\n".join(json.dumps(o) for o in obs) + "\n")
                sensor_buffers[path] = []

    while dt < end:

        for i in np.random.choice(num, num, replace=False):
            pickedSensor = helper.deleteSensorAttributes(sensors[i])
            sensorId = sensors[i]["id"]
            sensorTSPath = f"benchmark/datasets/{size}/timeseries/{sensorId}.json"
            os.makedirs(os.path.dirname(sensorTSPath), exist_ok=True)
            geom_id = random.choice(sensors[i]["coverage"])["id"]
            id = str(uuid.uuid4())
            obs = {
                "id": id,
                "timestamp": dt.strftime("%Y-%m-%dT%H:%M:%S")
                + f".{dt.microsecond // 1000:03d}",
                "sensor": {"id": pickedSensor["id"]},
                "geometry": {
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
                "payload": {"temperature": random.randint(1, 100)},
                "type": "Temperature",
            }
            obs["location"] = parseLocation(obs["geometry"])
            obs.pop("geometry", None)
            master_buffer.append(obs)

            if sensorTSPath in sensor_buffers:
                sensor_buffers[sensorTSPath].append(obs)
            else:
                sensor_buffers[sensorTSPath] = [obs]

            if count % flush_interval == 0:
                flush_buffers()
                print(f"{count} Random Temperature Observations")
            count += 1
        dt += step

    # Final flush
    flush_buffers()
    for f in sensor_files.values():
        f.close()
    # fpObj.close()


def createIntelligentTempObs(
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

    seedFile = open("data/seedTemperature.json", "w")
    for observation in observations:
        if observation["sensor"]["type_"]["id"] == "Thermometer":
            seedFile.write(json.dumps(observation) + "\n")
    seedFile.close()

    seedFile = "data/seedTemperature.json"
    outputFile = "data/temperatureData.json"
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
        "temperature",
        speedScaleNoise,
        timeScaleNoise,
        deviceScaleNoise,
        int,
    )

    scale.speedScale()
    scale.deviceScale()
    scale.timeScale()
