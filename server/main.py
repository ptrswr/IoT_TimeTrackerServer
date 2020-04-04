import json
import os
import sys
import time
import paho.mqtt.client as mqtt
from content import log_card,display_menu
from server_config import topic


file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)



def disconnect(client):
    client.loop_stop()


def on_disconnect(client, userdata, rc=0):
    disconnect(client)


def on_message(client_, user_data, message):
    print("otrzymałem wiadomosc\n")
    data = json.loads(message.payload)
    if not data["terminal_id"] or not data["card_id"]:
        return

    log_card(data["card_id"], data["terminal_id"])


def on_connect(client_, user_data, flags, rc):
    client_.subscribe(topic)


def main():
    client = mqtt.Client('server')
    client.connect('test.mosquitto.org', 1883, 60)
    client.on_message = on_message
    client.on_connect = on_connect
    client.loop_start()

    while not client.is_connected:
        time.sleep(1)

    display_menu()

    disconnect(client)


if __name__ == '__main__':
    main()
