import paho.mqtt.client as mqtt
from server.server_config import topic

def on_message(client_, user_data, message):
    print('Message recived', str(message.payload.decode('utf-8')))

def on_connect(client_, user_data, flags, rc):
    client_.subscribe(topic)

def main():
    client = mqtt.Client('server')
    client.connect('test.mosquitto.org', 1883, 60)
    client.on_message = on_message
    client.on_connect = on_connect
    client.loop_forever()


if __name__ == '__main__':
    main()
