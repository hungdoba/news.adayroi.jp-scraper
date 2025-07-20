import os
import json
from datetime import datetime


def log_id(log_file, log_id=None):
    timestamp = datetime.now().isoformat()
    entry = {"timestamp": timestamp, "id": log_id}
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry) + '\n')
    return log_id


def get_all_ids(log_file):
    if not os.path.exists(log_file):
        return []
    ids = []
    with open(log_file, 'r', encoding='utf-8') as f:
        for line in f:
            entry = json.loads(line)
            ids.append(entry['id'])
    return ids


if __name__ == "__main__":
    log_file = "log.txt"
    log_id(log_file, "test_id_1")
    log_id(log_file, "test_id_2")
    log_id(log_file, "test_id_3")
    all_ids = get_all_ids(log_file)
    print("All IDs:", all_ids)
