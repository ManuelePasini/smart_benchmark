import configparser as ConfigParser
import datetime
import shutil
import sys
import os
import json
import ijson
import glob

from metadata import sensors, users, rooms
from observations import observations
from semanticobservation import semanticobservations
from queries import Queries
from utils import dataSeparator

common = [
    "location.json",
    "infrastructureType.json",
    "infrastructure.json",
    "sensorType.json",
    "group.json",
    "platformType.json",
    "virtualSensorType.json",
    "virtualSensor.json",
    "semanticObservationType.json",
    "wifiMap.json",
    "observation.json",
    "semanticObservation.json",
]


def readConfiguration(configFile):
    Config = ConfigParser.ConfigParser()
    Config.read(configFile)

    print("Reading Configuration File")
    configDict = {section: {} for section in Config.sections()}

    for section in Config.sections():
        options = Config.options(section)
        for option in options:
            try:
                configDict[section][option] = Config.get(section, option)
            except Exception as e:
                configDict[section][option] = None

    return configDict


def copyFiles(files, src, dest):
    print(f"Copying Source Files from {src}")

    for file in files:
        print(file)
        shutil.copy2(src + file, dest + file)
    print("Done copying files.")


def createUsers(config):
    users.createUsers(
        int(config["others"]["users"]),
        config["others"]["data-dir"],
        config["others"]["output-dir"],
    )


def createRooms(config):
    rooms.createRooms(
        int(config["others"]["rooms"]),
        config["others"]["data-dir"],
        config["others"]["output-dir"],
    )


def createSensors(config, pattern):
    if pattern == "random":
        sensors.createSensors(
            int(config["sensors"]["wifiap"]),
            int(config["sensors"]["wemo"]),
            int(config["sensors"]["temperature"]),
            config["others"]["data-dir"],
            config["others"]["output-dir"],
        )
    elif pattern == "intelligent":
        sensors.createIntelligentSensors(
            int(config["sensors"]["wemo"]),
            int(config["sensors"]["temperature"]),
            config["others"]["data-dir"],
            config["others"]["output-dir"],
        )


def createObservations(config, pattern, size):
    start = datetime.datetime.strptime(
        config["observation"]["start_timestamp"], "%Y-%m-%d %H:%M:%S"
    )
    end = start + datetime.timedelta(days=int(config["observation"]["days"]))
    step = datetime.timedelta(seconds=int(config["observation"]["step"]))

    if pattern == "random":
        observations.createObservations(
            start,
            end,
            step,
            config["others"]["data-dir"],
            config["others"]["output-dir"],
            size,
        )
    elif pattern == "intelligent":
        observations.createIntelligentObservations(
            start,
            int(config["seed"]["days"]),
            int(config["observation"]["days"]),
            int(config["seed"]["step"]),
            int(config["observation"]["step"]),
            int(config["seed"]["wemo"]),
            int(config["sensors"]["wemo"]),
            int(config["seed"]["temperature"]),
            int(config["sensors"]["temperature"]),
            float(config["seed"]["speed-noise"]),
            float(config["seed"]["time-noise"]),
            float(config["seed"]["sensor-noise"]),
            config["others"]["data-dir"],
            config["others"]["output-dir"],
        )


def createSemanticObservations(config, pattern, size):
    start = datetime.datetime.strptime(
        config["observation"]["start_timestamp"], "%Y-%m-%d %H:%M:%S"
    )
    end = start + datetime.timedelta(days=int(config["observation"]["days"]))
    step = datetime.timedelta(seconds=int(config["observation"]["step"]))

    if pattern == "random":
        semanticobservations.createObservations(
            start,
            end,
            step,
            config["others"]["data-dir"],
            config["others"]["output-dir"],
            size,
        )
    elif pattern == "intelligent":
        semanticobservations.createIntelligentObservations(
            int(config["seed"]["days"]),
            int(config["observation"]["days"]),
            int(config["seed"]["step"]),
            int(config["observation"]["step"]),
            float(config["seed"]["speed-noise"]),
            float(config["seed"]["time-noise"]),
            config["others"]["data-dir"],
            config["others"]["output-dir"],
        )


def createQueries(config):
    q = Queries(
        int(config["query"]["runs"]),
        config["others"]["output-dir"],
        config["query"]["output-dir"],
        config["observation"]["start_timestamp"],
        int(config["observation"]["days"]),
        int(config["query"]["num-locations"]),
        int(config["query"]["num-sensors"]),
        int(config["query"]["time-delta"]),
    )
    q.generateQueries()


def directoryClenaup(config):
    pass


def parseValue(value):
    if isinstance(value, str):
        return f"'{value}'"
    elif isinstance(value, (int, float)):
        return value
    elif isinstance(value, bool):
        return "true" if value else "false"
    else:
        return json.dumps(value)


def createEdge(source_id, label: str, dest_id):
    label = label if label != "sensor" else "temperature"
    # If it's a measurement, the link is not temp -> sensor but sensor -> temp
    return (
        f"""MATCH (u {{id : {parseValue(source_id)} }}), (v {{id : {parseValue(dest_id)} }}) CREATE (u) - [r:has{label.capitalize()}] -> (v);"""
        if label != "temperature"
        else f"""MATCH (u {{id : {parseValue(source_id)} }}), (v {{id : {parseValue(dest_id)} }}) CREATE (v) - [r:has{label.capitalize()}] -> (u);"""
    )


def parseProp(entityId, k, v):
    edges = []

    if isinstance(v, str):
        return f"{k}: '{v}'", edges
    elif isinstance(v, (int, float)):
        return f"{k}: {v}", edges
    elif isinstance(v, bool):
        return f"{k}: {'true' if v else 'false'}", edges
    elif isinstance(v, list):
        # Check if it's a list of edges
        edgesList = all(
            [True if isinstance(item, dict) and "id" in item else False for item in v]
        )
        if edgesList:
            [edges.append(createEdge(entityId, k, item["id"])) for item in v]
            return "", edges
        else:
            if k == "geometry":
                return "", edges
            return f"{k}: {json.dumps(v)}", edges

    elif isinstance(v, dict):
        if "id" in v:
            edges.append(createEdge(entityId, k, v["id"]))
            return "", edges
        else:
            if k == "geometry":
                return "", edges
            elif k == "payload":
                key = list(v.keys())[0]
                value = v[key]
                return f"{key}: {repr(value)}", edges
    else:
        return f"{k}: {json.dumps(v)}", edges


def entityToCypher(entity):
    type = entity["type"]
    id = entity["id"]

    a = [parseProp(id, k, v) for k, v in entity.items() if k != "type"]
    props = ",".join(item[0] for item in a if item[0] != "")
    edges = "\n".join([item2 for item in a if len(item[1]) > 0 for item2 in item[1]])
    cypherQuery = f"CREATE (n:{type} {{ {props} }});"
    return cypherQuery + "\n" + edges if len(edges) > 0 else cypherQuery


def updateMeasurement(entity, id):
    payload = entity["payload"]
    key = list(payload.keys())[0]
    value = payload[key]
    if "location" in entity:
        return f"""MATCH (n {{id: '{id}'}}) SET n.{key} = {repr(value)}, n.timestamp = '{entity['timestamp']}', n.location = '{entity["location"]}';"""
    else:
        return f"""MATCH (n {{id: '{id}'}}) SET n.{key} = {repr(value)}, n.timestamp = '{entity['timestamp']}';"""


def parseToCypher(config):
    print("Parsing to Cypher")

    outputDir = config["others"]["output-dir"]
    tempSensors = int(config["sensors"]["temperature"]) + 6
    files = [
        "group.json",
        "user.json",
        "platformType.json",
        "sensorType.json",
        "platform.json",
        "infrastructureType.json",
        "infrastructure.json",
        "sensor.json",
        "virtualSensorType.json",
        "virtualSensor.json",
        # "semanticObservation.json",
        # "semanticObservationType.json",
        "observation.json",
    ]
    for filename in files:
        if (
            filename.endswith(".json")
            and "location" not in filename
            and "semanticObservation" not in filename
        ):
            print(f"Processing {filename}")
            json_path = os.path.join(outputDir, filename)
            cypher_path = os.path.join(outputDir, filename.replace(".json", ".cypher"))

            tsMap = {}
            # Open input and output files
            with open(json_path, "r") as f_in, open(cypher_path, "w") as f_out:
                count = 0
                # For each entity in the JSON file, convert to Cypher
                try:
                    for entityDict in ijson.items(f_in, "item"):
                        # Special processing for observation.json
                        if (
                            filename == "observation.json"
                            or filename == "semanticObservation.json"
                        ):
                            payload = entityDict["payload"]
                            key = list(payload.keys())[0]
                            # First create the ts
                            if count < tempSensors:
                                count = count + 1
                                cypher_line = entityToCypher(entityDict)
                                if filename == "observation.json":
                                    tsMap[entityDict["sensor"]["id"]] = {
                                        key: entityDict["id"]
                                    }
                                else:
                                    tsMap[entityDict["virtualSensor"]["id"]] = {
                                        key: entityDict["id"]
                                    }
                            else:
                                # Then update them
                                if filename == "observation.json":
                                    id = tsMap[entityDict["sensor"]["id"]][key]
                                else:
                                    id = tsMap[entityDict["virtualSensor"]["id"]][key]
                                cypher_line = updateMeasurement(entityDict, id)
                        else:
                            cypher_line = entityToCypher(entityDict)
                        f_out.write(cypher_line + "\n")
                except Exception as e:
                    print(f"Error processing {filename}: {e}")
                    continue

    # Merge cypher files
    cypherFiles = [f.replace(".json", ".cypher") for f in files]
    if len(cypherFiles) > 0:
        staticCypherPath = os.path.join(outputDir, "small.cypher")
        with open(staticCypherPath, "w") as merged_file:
            for cypher_file in cypherFiles:
                with open(os.path.join(outputDir, cypher_file), "r") as f:
                    row = f.read()
                    if row != "":
                        merged_file.write(row)
    else:
        print("No Cypher files found to merge.")


def removeJsonField(walk_generator, field_to_remove):
    for dirpath, _, filenames in walk_generator:
        for filename in filenames:
            if filename.endswith(".json"):
                print(
                    f"Removing field '{field_to_remove}' from {filename} in {dirpath}"
                )
                filepath = os.path.join(dirpath, filename)
                tmp_path = filepath + ".tmp"

                with open(filepath, "r", encoding="utf-8") as infile, open(
                    tmp_path, "w", encoding="utf-8"
                ) as outfile:
                    outfile.write("[\n")
                    first = True
                    try:
                        for obj in ijson.items(infile, "item"):
                            obj.pop(field_to_remove, None)
                            if not first:
                                outfile.write(",\n")
                            outfile.write(json.dumps(obj, ensure_ascii=False))
                            first = False
                    except Exception:
                        continue
                    outfile.write("\n]")

                os.replace(tmp_path, filepath)


if __name__ == "__main__":

    size = "big"
    configFile = f"/home/python/configs/config_{size}.ini"
    configDict = readConfiguration(configFile)
    pattern = configDict["others"]["pattern"]
    tsDirectory = f"benchmark/datasets/{size}/timeseries/"
    os.makedirs(tsDirectory, exist_ok=True)
    # Clear old TS data
    for file_path in glob.glob(os.path.join(tsDirectory, "*")):
        if os.path.isfile(file_path):
            os.remove(file_path)
    copyFiles(
        common, configDict["others"]["data-dir"], configDict["others"]["output-dir"]
    )

    createUsers(configDict)
    createRooms(configDict)
    createSensors(configDict, pattern)

    createObservations(configDict, pattern, size)
    createSemanticObservations(configDict, pattern, size)

    removeJsonField(os.walk(configDict["others"]["output-dir"]), "geometry")
    parseToCypher(configDict)
    # dataSeparator.separateData(
    #     int(configDict["others"]["insert-test-data"]),
    #     configDict["others"]["output-dir"],
    # )

    # head -n -30000 small.cypher > small2.cypher
