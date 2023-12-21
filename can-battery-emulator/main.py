#!/usr/bin/env python

import json
import logging
import time
import random

from hacbi.canbus import send_msg, open_can
from hacbi.msgs import *
from hacbi.mqtt import *

options_file = '/data/options.json'
option_names = [
    'interface',
    'device',
    'mqtt_port',
    'mqtt_user',
    "mqtt_password",
    "mqtt_broker",
    'verbose_log',
    'sample_period',
    'publish_period',
    'watchdog',
    'expire_values_after',
    'bat_modules',
    'charge_volts',
    'absorption_volts',
    'min_voltage',
    'rebulk_offset',
    'charge_current',
    'discharge_current',
    ]

def die(value=-1):
    exit(value)

def verify_options(option_names, config):
    for option_name in option_names:
        if not option_name in config:
            print("Missing option:", option_name)
            print(config)
            print(option_names)
            die()


# Read the configuration file
try:
    config_file = open(options_file, mode="r")
    config = json.load(config_file)
except:
    print("Error opening/reading the options file:", OPTIONS_FILE)
    die()

# Verify that we have all the options we expect
verify_options(option_names, config)

# Initizlie the logging interface
if config['verbose_log']:
    logging.basicConfig(level=logging.DEBUG, format='%(process)d-%(levelname)s-%(message)s')
else:
    logging.basicConfig(level=logging.INFO, format='%(process)d-%(levelname)s-%(message)s')

# Open the canbus
bus = open_can(config['interface'], config['device'])
if bus is None:
    die(-1)

# Create the topic list
voltage_topic = config['voltage_topic']
current_topic = config['current_topic']
soc_topic = config['soc_topic']
power_topic = config['power_topic']
topic_list = []
topic_list.append(voltage_topic)
topic_list.append(current_topic)
topic_list.append(soc_topic)
topic_list.append(power_topic)
    
# Create the mqtt client interface
client_id = f'python-mqtt-{random.randint(0, 1000)}'
client = connect_mqtt(client_id, config['mqtt_broker'], config['mqtt_port'],
                      config['mqtt_user'], config['mqtt_password'], topic_list)

charge_volts = config['charge_volts']
absorb_volts = config['absorption_volts']
min_volts = config['min_voltage']
rebulk_offset = config['rebulk_offset']
charge_current = config['charge_current']
discharge_current = config['discharge_current']
sample_period = config['sample_period']
charge = False
discharge = False

# Dummy values for now
max_cell_temp = 30
min_cell_temp = 30
max_cell_voltage = 3.34
min_cell_voltage = 3.34
max_temp_cell = 1
min_temp_cell = 2
max_voltage_cell = 1
min_voltage_cell = 2
wait_time = 0.02
soh = 90
temperature = 30

while True:
    time.sleep(sample_period)

    client.loop()

    # Retrieve the battery information from the MQTT topics
    voltage = get_sensor_float(voltage_topic)
    current = get_sensor_float(current_topic)
    soc = get_sensor_float(soc_topic)
    power = get_sensor_float(power_topic)
    logging.info(f"Current battery values: {voltage}V, {current}A, {power}W, {soc}%")
    if voltage == 0 or current == 0 or soc == 0:
        logging.info(f"Waiting for battery stats")
        continue

    msg = create_limits_msg(charge_volts, min_volts, charge_current, discharge_current)
    send_msg(bus, msg)
    time.sleep(wait_time)

    msg = create_soc_msg(soc, soh)
    send_msg(bus, msg)
    time.sleep(wait_time)

    msg = create_state_msg(voltage, current, temperature)
    send_msg(bus, msg)
    time.sleep(wait_time)

    msg = create_charge_msg(charge, discharge)
    #send_msg(bus, msg)
    time.sleep(wait_time)

    msg = create_cell_stats_msg(max_cell_temp, min_cell_temp, max_cell_voltage, min_cell_voltage)
    send_msg(bus, msg)
    time.sleep(wait_time)
    
    msg = create_cell_stats_id_msg(max_temp_cell, min_temp_cell, max_voltage_cell, min_voltage_cell)
    send_msg(bus, msg)
    time.sleep(wait_time)

    msg = create_inverter_type_msg()
    send_msg(bus, msg)
    time.sleep(wait_time)


# from ha_mqtt_discoverable import Settings
# from ha_mqtt_discoverable.sensors import BinarySensor, BinarySensorInfo

# # Configure the required parameters for the MQTT broker
# mqtt_settings = Settings.MQTT(host="nas.local", username="hass", password="jvc2sun")

# # Information about the sensor
# sensor_info = BinarySensorInfo(name="MySensor", device_class="motion")

# settings = Settings(mqtt=mqtt_settings, entity=sensor_info)

# # Instantiate the sensor
# mysensor = BinarySensor(settings)

# # Change the state of the sensor, publishing an MQTT message that gets picked up by HA
# mysensor.on()
# mysensor.off()

# # You can also set custom attributes on the sensor via a Python dict
# mysensor.set_attributes({"my attribute": "awesome"})

# from ha_mqtt_discoverable import Settings, DeviceInfo
# from ha_mqtt_discoverable.sensors import BinarySensor, BinarySensorInfo

# # Configure the required parameters for the MQTT broker
# mqtt_settings = Settings.MQTT(host="nas.local", username="hass", password="jvc2sun")




# # Define the device. At least one of `identifiers` or `connections` must be supplied
# device_info = DeviceInfo(name="My device", identifiers="device_id")

# # Associate the sensor with the device via the `device` parameter
# # `unique_id` must also be set, otherwise Home Assistant will not display the device in the UI
# motion_sensor_info = BinarySensorInfo(name="My motion sensor", device_class="motion", unique_id="my_motion_sensor", device=device_info)

# motion_settings = Settings(mqtt=mqtt_settings, entity=motion_sensor_info)

# # Instantiate the sensor
# motion_sensor = BinarySensor(motion_settings)

# # Change the state of the sensor, publishing an MQTT message that gets picked up by HA
# motion_sensor.on()

# # An additional sensor can be added to the same device, by re-using the DeviceInfo instance previously defined
# door_sensor_info = BinarySensorInfo(name="My door sensor", device_class="door", unique_id="my_door_sensor", device=device_info)
# door_settings = Settings(mqtt=mqtt_settings, entity=door_sensor_info)

# # Instantiate the sensor
# door_sensor = BinarySensor(settings)

# # Change the state of the sensor, publishing an MQTT message that gets picked up by HA
# door_sensor.on()

# # The two sensors should be visible inside Home Assistant under the device `My device`
