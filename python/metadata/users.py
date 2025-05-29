import random
import json
import uuid


def createUsers(numUsers, src, dest):

    with open(src + "user.json") as data_file:
        users = json.load(data_file)

    with open(src + "group.json") as data_file:
        groups_json = json.load(data_file)
        groups = [{"id": group["id"]} for group in groups_json]

    with open(src + "platform.json") as data_file:
        platforms = json.load(data_file)
        platforms = [
            {**item, "owner": {"id": item["owner"]["id"]}} for item in platforms
        ]
        for platform in platforms:
            platform["type"] = "Platform"

    with open(src + "platformType.json") as data_file:
        platformsTypes_json = json.load(data_file)
        platformsTypes = [
            {"id": platformType["id"]} for platformType in platformsTypes_json
        ]

    numGroups = len(groups)

    print("Creating Users And Platforms")

    for i in range(numUsers - len(users)):
        id = str(uuid.uuid4())
        groupList = [groups[random.randint(0, numGroups - 1)]]
        user = {
            "id": id.replace("-", "_"),
            "googleAuthToken": id,
            "name": "simUser{}".format(i),
            "emailId": "simUser{}@uci.edu".format(i),
            "groups": groupList,
            "type": "User",
        }
        users.append(user)

        id = str(uuid.uuid4())
        platform = {
            "id": id.replace("-", "_"),
            "name": "simPlatform{}".format(i),
            "owner": {"id": user["id"]},
            "type_": platformsTypes[random.randint(1, len(platformsTypes) - 1)],
            "hashedMac": id,
            "type": "Platform",
        }
        platforms.append(platform)

    with open(dest + "user.json", "w") as writer:
        json.dump(users, writer, indent=4)

    with open(dest + "platform.json", "w") as writer:
        json.dump(platforms, writer, indent=4)
