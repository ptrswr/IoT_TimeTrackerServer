import paho.mqtt.client as mqtt
import json
import time
from server.content import log_card,add_new_user
from server.server_config import db, topic


def disconnect(client):
    client.loop_stop()


def on_disconnect(client, userdata, rc=0):
    disconnect(client)


def on_message(client_, user_data, message):
    data = json.loads(message.payload)
    if not data["terminal_id"] or not data["card_id"]:
        return

    log_card(data["card_id"], data["terminal"])


def on_connect(client_, user_data, flags, rc):
    client_.subscribe(topic)


def main():
    client = mqtt.Client('server')
    client.connect('test.mosquitto.org', 1883, 60)
    client.on_message = on_message
    client.on_connect = on_connect
    client.loop_forever()

    while not client.is_connected:
        time.sleep(1)

        # expect a cli command
    add_new_user(123, "pedro ramirez")
    disconnect(client)


if __name__ == '__main__':
    main()
