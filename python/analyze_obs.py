import re
from datetime import datetime
from collections import defaultdict

cypher_pattern = re.compile(
    r"MATCH \(n \{id: '(?P<id>[^']+)'\}\) SET n\.temperature = (?P<temperature>\d+), "
    r"n\.timestamp = '(?P<timestamp>[^']+)', n\.location = '(?P<location>[^']+)';"
)


def load_latest_per_id_from_cypher(cypher_path, last_n):
    with open(cypher_path, "r") as f:
        lines = f.readlines()

    recent_lines = lines[-last_n:]
    latest_by_id = {}

    for line in recent_lines:
        match = cypher_pattern.match(line.strip())
        if not match:
            continue

        item = match.groupdict()
        item_id = item["id"]
        ts_str = item["timestamp"]

        try:
            timestamp = datetime.fromisoformat(ts_str)
        except ValueError:
            continue

        if item_id not in latest_by_id or timestamp > latest_by_id[item_id][0]:
            latest_by_id[item_id] = (timestamp, line.strip())

    return [entry[1] for entry in latest_by_id.values()]


if __name__ == "__main__":
    path_to_cypher = "test.cypher"
    N = 250

    result = load_latest_per_id_from_cypher(path_to_cypher, N)

    with open("filtrati.cypher", "w") as out_file:
        out_file.write("\n".join(result) + "\n")

    print(f"{len(result)} righe salvate in filtrati.cypher")
