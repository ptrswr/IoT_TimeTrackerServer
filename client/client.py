import paho.mqtt.client as mqtt
import json

terminal_id = '123456789'


def main():
    client = mqtt.Client(terminal_id)
    client.connect('test.mosquitto.org', 1883, 60)

    while True:
        input_data = input('Zbliż kartę > ')
        if len(input_data) == 0:
            continue
        else:
            client.publish('terminal/card', json.dumps({'card_id': input_data, 'terminal_id': terminal_id}))


if __name__ == '__main__':
    main()