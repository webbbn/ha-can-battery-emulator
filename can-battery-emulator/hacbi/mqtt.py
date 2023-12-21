import logging
import time

import paho.mqtt.client as mqtt

mqtt_sensors = {}

FIRST_RECONNECT_DELAY = 1
RECONNECT_RATE = 2
MAX_RECONNECT_DELAY = 60

all_topics = []

def subscribe_all(client, topics):
    for topic in topics:
        client.subscribe(topic)

def on_disconnect(client, userdata, rc):
    logging.info("Disconnected with result code: %s", rc)
    reconnect_delay = FIRST_RECONNECT_DELAY
    while True:
        logging.info("Reconnecting in %d seconds...", reconnect_delay)
        time.sleep(reconnect_delay)

        try:
            client.reconnect()
            logging.info("Reconnected successfully!")
            break
        except Exception as err:
            logging.error("%s. Reconnect failed. Retrying...", err)

        reconnect_delay = min(reconnect_delay * RECONNECT_RATE, MAX_RECONNECT_DELAY)

    subscribe_all(client, all_topics)
    
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.debug("Connected to MQTT Broker!")
    else:
        logging.error(f"Failed to connect, return code {rc}")

def connect_mqtt(client_id, broker, port, username, password, topic_list):
    all_topics = topic_list

    connect_delay = FIRST_RECONNECT_DELAY
    while True:
        logging.info("Connecting in %d seconds...", connect_delay)
        time.sleep(connect_delay)
        
        # Set Connecting Client ID
        client = mqtt.Client(client_id)
        client.username_pw_set(username, password)
        client.on_connect = on_connect
        client.on_disconnect = on_disconnect
        try:
            client.connect(broker)
            logging.info("Connected successfully!")
            break
        except Exception as err:
            logging.error(f"{err}. Connect failed. Retrying...")
        connect_delay = min(connect_delay * RECONNECT_RATE, MAX_RECONNECT_DELAY)

    client.on_subscribe = on_subscribe
    client.on_message = on_message
    subscribe_all(client, all_topics)
    return client

def on_subscribe(mqttc, userdata, mid, granted_qos):
    logging.info(f"Subscribed: {userdata} {mid} {granted_qos}")

def on_message(mqttc, userdata, msg):
    logging.info(f"{msg.topic} {msg.qos} {msg.payload}")
    mqtt_sensors[msg.topic] = msg.payload

def get_sensor_float(topic):
    if topic in mqtt_sensors:
        return float(mqtt_sensors[topic])
    else:
        return 0
