#!/usr/bin/env python

import json
import logging
import time
import random
import asyncio

from hacbi.canbus import send_msg, open_can, close_can
from hacbi.msgs import *
import hacbi.mqtt as mqtt

options_file = '/data/options.json'

option_names = [
    'interface',
    'device',
    'mqtt_port',
    'mqtt_user',
    "mqtt_password",
    "mqtt_broker",
    'verbose_log',
    'log_interval',
    'sample_period',
    'expire_values_after',
    'bat_modules',
    'charge_volts',
    'absorption_volts',
    'min_voltage',
    'rebulk_offset',
    'charge_current',
    'discharge_current',
    'root_topic',
    'force_charge_1_topic',
    'force_charge_2_topic',
    'discharge_topic',
    'charge_topic',
    'identifier'
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
verbose = config['verbose_log']
log_interval = config['log_interval']
if verbose:
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
root_topic = config['root_topic']
force_charge_1_topic = config['force_charge_1_topic']
force_charge_2_topic = config['force_charge_2_topic']
charge_topic = config['charge_topic']
discharge_topic = config['discharge_topic']
charge_current_topic = config['charge_current_topic']
topic_list = []
topic_list.append(voltage_topic)
topic_list.append(current_topic)
topic_list.append(soc_topic)
topic_list.append(power_topic)
topic_list.append(f"{root_topic}/switch/{force_charge_1_topic}")
topic_list.append(f"{root_topic}/switch/{force_charge_2_topic}")
topic_list.append(f"{root_topic}/switch/{charge_topic}")
topic_list.append(f"{root_topic}/switch/{discharge_topic}")
topic_list.append(f"{root_topic}/number/{charge_current_topic}")

# Create the mqtt client interface
client_id = f'python-mqtt-{random.randint(0, 1000)}'
client = mqtt.Client(client_id, config['mqtt_broker'], config['mqtt_port'], config['mqtt_user'], config['mqtt_password'], topic_list)

charge_volts = config['charge_volts']
absorb_volts = config['absorption_volts']
min_volts = config['min_voltage']
rebulk_offset = config['rebulk_offset']
charge_current = config['charge_current']
discharge_current = config['discharge_current']
sample_period = config['sample_period']
root_topic = config['root_topic']
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

# Add the force charge/discharge switch topics
identifier = config['identifier']
client.add_switch(root_topic, force_charge_1_topic, "Force Charge 1", identifier)
client.add_switch(root_topic, force_charge_2_topic, "Force Charge 2", identifier)
client.add_switch(root_topic, charge_topic, "Charge", identifier, default=True)
client.add_switch(root_topic, discharge_topic, "Discharge", identifier, default=True)
client.add_number(root_topic, charge_current_topic, "Charge Current", identifier, "A", 0, charge_current, default=charge_current)

async def process_messages():
    counter = 0

    while await client.task_wait(sample_period):

        # Retrieve the battery information from the MQTT topics
        force_charge_1 = client.get_sensor_binary(f"{root_topic}/switch/{force_charge_1_topic}")
        force_charge_2 = client.get_sensor_binary(f"{root_topic}/switch/{force_charge_2_topic}")
        charge = client.get_sensor_binary(f"{root_topic}/switch/{charge_topic}")
        discharge = client.get_sensor_binary(f"{root_topic}/switch/{discharge_topic}")
        cur_charge_current = client.get_sensor_number(f"{root_topic}/number/{charge_current_topic}")
        voltage = client.get_sensor_number(voltage_topic)
        current = client.get_sensor_number(current_topic)
        soc = client.get_sensor_number(soc_topic)
        power = client.get_sensor_number(power_topic)
        cur_log_level = logging.DEBUG
        if counter == log_interval:
            cur_log_level = logging.INFO
            counter = 0
        else:
            counter += 1
        if voltage == 0 or current == 0 or soc == 0:
            ready = False
            ready_msg = "NOT ready"
        else:
            ready = True
            ready_msg = "READY"
        logging.log(cur_log_level, f"Current battery values ({ready_msg}): {voltage}V, {current}A, {power}W, {soc}%, charge={charge}, discharge={discharge}, force_charge_1={force_charge_1}, force_charge_2={force_charge_2}")
        if not ready:
            continue
        msg = create_limits_msg(charge_volts, min_volts, cur_charge_current, discharge_current)
        send_msg(bus, msg)
        await asyncio.sleep(wait_time)

        msg = create_soc_msg(soc, soh)
        send_msg(bus, msg)
        await asyncio.sleep(wait_time)

        msg = create_state_msg(voltage, current, temperature)
        send_msg(bus, msg)
        await asyncio.sleep(wait_time)

        msg = create_charge_msg(force_charge_1, force_charge_2, charge, discharge)
        send_msg(bus, msg)
        await asyncio.sleep(wait_time)

        msg = create_cell_stats_msg(max_cell_temp, min_cell_temp, max_cell_voltage, min_cell_voltage)
        send_msg(bus, msg)
        await asyncio.sleep(wait_time)

        msg = create_cell_stats_id_msg(max_temp_cell, min_temp_cell, max_voltage_cell, min_voltage_cell)
        send_msg(bus, msg)
        await asyncio.sleep(wait_time)

        msg = create_inverter_type_msg()
        send_msg(bus, msg)
        await asyncio.sleep(wait_time)

# Create the message processing task
client.add_task(process_messages())

# Run until asked to stop
client.connect_and_run()

# Close the can bus connection
close_can(bus)
