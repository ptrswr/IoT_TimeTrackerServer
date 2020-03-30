import os
from tinydb import TinyDB

server_id = "IoT_RFID_server"
topic = "rfid-reader"
ip = "test.mosquitto.org"


def storage_file_location(name):
    return os.path.join(os.path.dirname(__file__), name)


db = TinyDB(storage_file_location("storage.json"))
