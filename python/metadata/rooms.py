import random
import json
import uuid


def createRooms(numRooms, src, dest):

    with open(src + "infrastructure.json") as data_file:
        rooms = json.load(data_file)
        rooms = [{**item, "type_": {"id": item["type_"]["id"]}} for item in rooms]

    for geometry in rooms:
        for point in geometry["geometry"]:
            point.pop("id", None)

    print("Creating Rooms")

    newRooms = []

    if numRooms - len(rooms) <= 0:
        for room in rooms:
            room["type"] = "Infrastructure"

    for i in range(numRooms - len(rooms)):
        id = str(uuid.uuid4())
        copiedRoom = rooms[random.randint(0, len(rooms) - 1)]
        room = {
            "id": id.replace("-", "_"),
            "name": "simRoom{}".format(i),
            "floor": copiedRoom["floor"],
            "geometry": copiedRoom["geometry"],
            "dfsf": "Infrastructure",
            "type_": {"id": copiedRoom["type_"]["id"]},
        }
        newRooms.append(room)

    newRooms.extend(rooms)

    with open(dest + "infrastructure.json", "w") as writer:
        json.dump(newRooms, writer, indent=4)
