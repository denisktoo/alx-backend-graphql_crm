import os
from datetime import datetime

# file path
base_dir = os.path.dirname(os.path.dirname(__file__))
file_path = os.path.join(base_dir, "tmp", "crm_heartbeat_log.txt")

def log_crm_heartbeat():
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")

    with open(file_path, "a") as file:
        file.write(f"{timestamp} CRM is alive\n")
