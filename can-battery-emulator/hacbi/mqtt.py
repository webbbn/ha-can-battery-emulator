import logging
import sys
import asyncio
import signal

from gmqtt import Client as MQTTClient

# Use uvloop
import uvloop
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

class Client:
    '''Maintains a connection to an MQTT broker to monitor a list of topics'''

    def __init__(self, client_id, broker_host, broker_port, username, password, topic_list, expire_after=20.0):
        '''
        Create the MQTTClient class
        client_id - A unique client identifier string
        broker_host - The hostname/IP address where the MQTT broker is running
        broker_port - The port number of the MQTT broker (typically 1883)
        username - The username used to connect to the MQTT broker
        password - The password used to connect to the MQTT broker
        topic_list - A list of topics to subscribe to
        expire_after - Walues will be removed from the values list if they have not been updated in this amount of time (seconds)
        '''
        self.client_id = client_id
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.username = username
        self.password = password
        self.topic_list = topic_list
        self.expire_after = expire_after
        self.expire_counter = 0
        self.values = {}
        self.tasks = []
        self.loop = asyncio.get_event_loop()

        # Create the MQTT client class
        self.client = MQTTClient(self.client_id)

        # Initialize the callbacks
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.client.on_subscribe = self.on_subscribe

        # Initilize the authorization credentials
        self.client.set_auth_credentials(self.username, self.password)
        
        # STOP can be signaled to initiate a controlled shutdown
        self.stop = asyncio.Event()

        # Create signal handlers to initiate a controlled shutdown
        self.loop.add_signal_handler(signal.SIGINT, self.shutdown)
        self.loop.add_signal_handler(signal.SIGTERM, self.shutdown)

    async def connect(self):
        '''Attempt to connect to the MQTT broker'''

        logging.debug(f"Connecting to MQTT broker {self.broker_host}:{self.broker_port}")
        await self.client.connect(self.broker_host, self.broker_port, keepalive=60)

    def wait_on_connect(self):
        self.loop.run_until_complete(connect())

    def on_connect(self, client, flags, rc, properties):
        logging.info('Connected to MQTT broker.')

        # Subscribe to all the requested topics.
        for topic in self.topic_list:
            self.client.subscribe(topic, qos=0)

    def on_message(self, client, topic, payload, qos, properties):
        logging.debug(f"{topic} {qos} {payload} {properties}")
        if not topic in self.values:
            logging.info(f"Aquired initial value for {topic}: {payload}")
        self.values[topic] = [ payload, self.expire_counter ]

    def on_disconnect(self, client, packet, exc=None):
        logging.debug("Disconnected from MQTT broker.")

    def on_subscribe(self, client, mid, qos, properties):
        logging.info(f"Subscribed: {mid} {qos} {properties}")

    def get_value(self, topic):
        if topic in self.values:
            return self.values[topic][0]
        else:
            return None

    def get_sensor_float(self, topic):
        val = self.get_value(topic)
        if val is None:
            return 0
        else:
            return float(val)

    def shutdown(self, *args):
        self.stop.set()

    def add_task(self, task):
        t = self.loop.create_task(task)
        self.tasks.append(t)
        return t

    async def task_wait(self, timeout):
        '''Waits for the specified timeout and returns True if the task should continue or False if it should stop'''
        
        # Wait until we either get a stop event or our check interval timeout occurs (1 second)
        try:
            await asyncio.wait_for(self.stop.wait(), timeout=timeout)
        except TimeoutError:
            logging.debug("Task timeout expired. Task continuing.")
            return True
        else:
            logging.debug("Task timeout did not expired. Task exiting.")
            return False

    async def expire_task(self):

        while await self.task_wait(1.0):

            # Check each topic value to see if it hasn't changed in the expire_after interval
            for topic, [value, counter] in list(self.values.items()):
                logging.debug(f"Checking expiration: topic={topic} value={value} counter={counter} expire_counter={self.expire_counter} expire_after={self.expire_after}")
                if self.expire_counter > (counter + self.expire_after):
                    # Remove the value on expiration
                    logging.warning(f"Topic: {topic} has expired after no updates for {self.expire_after} seconds")
                    del self.values[topic]

            # Increment the expire counter
            self.expire_counter += 1

    async def run_until_shutdown(self):
        '''Wait for the stop event to signal shutdown'''

        # Run until stop is signaled
        await self.stop.wait()

        # Wait until all tasks have completed
        if len(self.tasks) > 0:
            await asyncio.gather(*self.tasks)

        # Disconnect from the client
        await self.client.disconnect()

    def run(self):
        '''Continue running until shutdown'''
        self.loop.run_until_complete(self.run_until_shutdown())

    def connect_and_run(self):
        '''Attempt to connect to the MQTT server and run until shutdown'''
        
        # Create a task to expire values after the specified time
        expire_task = self.add_task(self.expire_task())

        # Connect to the server
        self.loop.run_until_complete(self.connect())

        # Wait until we get a shutdown event
        self.loop.run_until_complete(self.run_until_shutdown())
