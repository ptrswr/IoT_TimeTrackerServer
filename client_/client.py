import paho.mqtt.client as mqtt
import json
import time

terminal_id = '123456789'


def main():
    client = mqtt.Client(terminal_id)
    client.connect('test.mosquitto.org', 1883, 60)
    while not client.is_connected:
        time.sleep(1)

    while True:
        input_data = input('Enter card > ')
        if len(input_data) == 0:
            continue
        else:
            client.publish("rfid-reader", json.dumps({'card_id': input_data, 'terminal_id': terminal_id}))


if __name__ == '__main__':
    main()