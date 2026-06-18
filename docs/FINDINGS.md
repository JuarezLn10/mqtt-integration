# Integration of a MQTT Client in a Flask App (Python)

## 1. Dependencies for connecting to a MQTT broker

### MQTT-Paho

The MQTT-Paho library is used to connect to a MQTT broker, and it is a Python library that implements the MQTT protocol.
To install the MQTT-Paho library, you can use pip:

```bash
pip install paho-mqtt
```

### Python-dotenv

The Python-dotenv library is used to load environment variables from an .env file.
To install the Python-dotenv library.

```bash
pip install python-dotenv
```

## 2. Some topics about MQTT

### Topics

- A topic is a string that contains a name for a message or a set of messages.
- To name one topic, a slash is used to separate the names about the different levels of the topic.
- For example, the topic `stores//weight` is a topic that contains the weight of supplies in the store.
- Another example is the topic `stores/supplies/temperature` that contains the temperature of supplies in the store.
- Also, it can be defined with use of ids like `stores/1234567890/telemetry/temperature`.
- And define a topic for responses like `stores/1234567890/telemetry/response/temperature`.
- A wildcard character `#` is used to match any number of characters in a topic.
- For example, the topic `stores/supplies/#` matches any topic that starts with `stores/supplies`.

## 3. Configure the MQTT client

To configure the MQTT client, you need to create a client object and set the configuration options.
For this, an environment file could be used for security reasons.

- First, define the environment variables. The username and password are set for authentication with the MQTT broker, and the client id is used to identify the client to the broker:

```bash
MQTT_HOST=host
MQTT_PORT=4567
MQTT_USERNAME=username
MQTT_PASSWORD=password
MQTT_CLIENT_ID=client_id
```

- Then, create a client object and set the configuration options:

```python
import os
import logging

from dotenv import load_dotenv
from paho.mqtt import client as mqtt_client

# Load environment variables from .env file
load_dotenv()

class MQTTClient:
    def __init__(self):
        self.host = os.getenv('MQTT_HOST')
        self.port = int(os.getenv('MQTT_PORT'))
        self.connected = False # Flag to track connection status
        self.client = mqtt_client.Client(
            client_id=os.getenv('MQTT_CLIENT_ID'),
            callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2,
        )
```

- Additionally, connection functions can be defined to handle the connection to the MQTT broker.
- The "connect" function is used to establish a connection to the MQTT broker.
- The "disconnect" function is used to disconnect from the MQTT broker.
- The "publish" function is used to publish messages to the MQTT broker.

```python
import os
import logging

from dotenv import load_dotenv
from paho.mqtt import client as mqtt_client
from flask import json


def on_connect():
    pass


def on_message():
    pass


def on_disconnect():
    pass


class MQTTClient:
    def __init__(self):
        self.host = os.getenv('MQTT_HOST')
        self.port = int(os.getenv('MQTT_PORT'))
        self.connected = False # Flag to track connection status
        self.client = mqtt_client.Client(
            client_id=os.getenv('MQTT_CLIENT_ID'),
            callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2,
        )
        
        self.configure()
        
    def configure(self):
        self.client.username_pw_set(os.getenv('MQTT_USERNAME'), os.getenv('MQTT_PASSWORD'))
        self.client.on_connect = on_connect
        self.client.on_message = on_message
        self.client.on_disconnect = on_disconnect
        self.client.disconnect = self.disconnect

    def connect(self):
        if self.connected:
            return

        self.client.connect(self.host, self.port, keepalive=60)
        self.client.loop_start()
        self.connected = True

    def disconnect(self):
        if self.connected:
            self.client.loop_stop()
            self.client.disconnect()

        self.connected = False

    def publish(self, topic, payload, qos=1):
        self.client.publish(topic, json.dumps(payload), qos=qos)
```

- Then, defines the "on" methods for the MQTT client.
- The "on_message" method is used to handle incoming messages from the MQTT broker.
- The "on_connect" method is used to trigger an action when the MQTT client successfully connects to the broker.
- The "on_disconnect" method is used to trigger an action when the MQTT client disconnects from the broker.

```python
import logging

# Define the MQTT subscriptions
SUBSCRIPTIONS = [
    "stores/+/telemetry/weight",
    "stores/+/telemetry/temperature",
    "stores/+/telemetry/humidity",
    "stores/+/health"
]


def on_message(client, userdata, msg):
    try:
        topic_parts = msg.topic.split("/")
        device_topic = topic_parts[2]

        match device_topic:
            case "telemetry":
                pass
            case "health":
                pass

    except Exception as ex:
        logging.exception(
            "Error while processing MQTT message: %s",
            ex
        )


def on_connect(client, userdata, flags, rc, properties=None):
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
    logging.info("Disconnected from MQTT Broker with RC=%s", rc)
```

- At last, create a singleton class to manage the MQTT client instance.
- The singleton class ensures that only one instance of the MQTT client is created and used throughout the application.
- Then, define a global method to initialize and shut down the MQTT client to be used from the app file.

```python
class MQTTClient:
    pass

# A singleton instance of the MQTTClient
mqtt_service = MQTTClient()


def init_mqtt_client():
    """ Initializes the MQTT client. """
    mqtt_service.connect()


def shutdown_mqtt_client():
    """ Shuts down the MQTT client. """
    mqtt_service.disconnect()
```

## 4. Configure the Flask app

- Create a Flask app with the Flask framework.
- Then, define a shutdown function to be called when the program exits.
- Register the shutdown function to be called when the program exits.
- Register the signal handler for SIGINT and SIGTERM for using the app in the terminal and Docker.
- Finally, in the "if" statement, validate that the connection to the MQTT broker is only established once.

```python
import atexit
import logging
import os
import signal
import threading

from flask import Flask

from shared.infrastructure.clients import init_mqtt_client, shutdown_mqtt_client

# Create the Flask application.
app = Flask(__name__)

# Lock to ensure that shutdown is only called once.
_shutdown_lock = threading.Lock()
_shutdown_done = False


def shutdown_app():
    global _shutdown_done

    with _shutdown_lock:
        if _shutdown_done:
            return

        _shutdown_done = True

        try:
            shutdown_mqtt_client()
        except Exception as e:
            logging.exception(f"Error during shutdown: {e}")


def signal_handler(signum, frame):
    logging.info(f"Received signal {signum}, shutting down server...")
    shutdown_app()


# Register the shutdown function to be called when the program exits.
atexit.register(shutdown_app)

# Register the signal handler for SIGINT and SIGTERM.
signal.signal(signal.SIGINT, signal_handler)  # Closing process in the terminal
signal.signal(signal.SIGTERM, signal_handler)  # Closing process in Docker


if __name__ == '__main__':
    if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        init_mqtt_client()
    logging.info(app.url_map)
    app.run(debug=True)
```