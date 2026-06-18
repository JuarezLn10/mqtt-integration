import logging
import os

from dotenv import load_dotenv
from flask import json
from paho.mqtt import client as mqtt_client

from inventory.interfaces.mqtt_services import on_telemetry_message

# Load environment variables from .env file
load_dotenv()

# Define the MQTT subscriptions
SUBSCRIPTIONS = [
    "stores/+/telemetry/weight",
    "stores/+/telemetry/temperature",
    "stores/+/telemetry/humidity",
    "stores/+/health"
]


def on_message(client, userdata, msg):
    """
    Method to handle incoming MQTT messages.
    In this, depending on the device topic, the message is processed accordingly to its correspondent context.

    :param client: The MQTT client
    :param userdata: The user data
    :param msg: The MQTT message received, containing the topic and the payload
    """

    try:
        topic_parts = msg.topic.split("/")
        device_topic = topic_parts[2]

        match device_topic:
            case "telemetry":
                on_telemetry_message(msg, topic_parts)
            case "health":
                pass

    except Exception as ex:
        logging.exception(
            "Error while processing MQTT message: %s",
            ex
        )


def on_connect(client, userdata, flags, rc, properties=None):
    """
    Function that triggers when the client connects to the broker.

    :param client: The MQTT client.
    :param userdata: The user data.
    :param flags: The connection flags.
    :param rc: The return code.
    :param properties: The properties.
    """

    if rc != 0:
        logging.error(
            "MQTT Error. RC=%s",
            rc
        )
        return

    logging.info("Connected to MQTT Broker")

    for topic in SUBSCRIPTIONS:
        client.subscribe(topic, qos=1)
        logging.info(
            "Subscribed to %s",
            topic
        )


def on_disconnect(client, userdata, flags, rc):
    """
    Function that triggers when the client disconnects from the broker.

    :param client: The MQTT client.
    :param userdata: The user data.
    :param flags: The disconnection flags.
    :param rc: The return code.
    """

    logging.info("Disconnected from MQTT Broker with RC=%s", rc)


class MQTTClient:
    """
    Class to handle the MQTT client.

    Attributes:
        host (str): The MQTT broker host.
        port (int): The MQTT broker port.
        connected (bool): Flag indicating whether the client is connected.
        client (mqtt_client.Client): The MQTT client instance.
    """

    def __init__(self):
        """
        Initializes the MQTTClient with the given configuration.
        """

        self.host = os.getenv('MQTT_HOST')
        self.port = int(os.getenv('MQTT_PORT'))
        self.connected = False
        self.client = mqtt_client.Client(
            client_id=os.getenv('MQTT_CLIENT_ID'),
            callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2,
        )

        self.configure()

    def configure(self):
        """
        Configures the MQTT client with the necessary callbacks and authentication.
        """

        self.client.username_pw_set(os.getenv('MQTT_USERNAME'), os.getenv('MQTT_PASSWORD'))
        self.client.on_connect = on_connect
        self.client.on_message = on_message
        self.client.on_disconnect = on_disconnect
        self.client.disconnect = self.disconnect

    def connect(self):
        """
        Connects to the MQTT broker and starts the loop to listen for messages.
        This also subscribes to the specified topics in the configuration.
        """

        if self.connected:
            return

        self.client.connect(self.host, self.port, keepalive=60)
        self.client.loop_start()
        self.connected = True
        logging.info(
            "Connected to MQTT at %s:%s",
            self.host,
            self.port
        )

    def disconnect(self):
        """
        Disconnects from the MQTT broker and stops the loop.
        """

        if self.connected:
            self.client.loop_stop()
            self.client.disconnect()

        self.connected = False

    def publish(self, topic, payload, qos=1):
        """
        Function to publish a message to a specified topic.

        :param topic: The topic to publish the message to.
        :param payload: The message to be published.
        :param qos: The quality of service level.
        """

        self.client.publish(topic, json.dumps(payload), qos=qos)


# A singleton instance of the MQTTClient
mqtt_service = MQTTClient()


def init_mqtt_client():
    """ Initializes the MQTT client. """
    mqtt_service.connect()


def shutdown_mqtt_client():
    """ Shuts down the MQTT client. """
    mqtt_service.disconnect()
