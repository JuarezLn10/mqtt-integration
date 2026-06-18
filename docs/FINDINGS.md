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
- For example, the topic `stores/weight` is a topic that contains the weight of supplies in the store.
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
        self.connected = False
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

    def connect(self):
        if self.connected:
            return

        self.client.connect(self.host, self.port)
        self.client.loop_start()
        self.connected = True
        logging.info(
            "Connected to MQTT at %s:%s",
            self.host,
            self.port
        )

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


def on_disconnect(client, userdata, flags, rc, properties=None):
    logging.info("Disconnected from MQTT Broker with RC=%s", rc)
```

- At last, create a singleton class to manage the MQTT client instance.
- The singleton class ensures that only one instance of the MQTT client is created and used throughout the application.
- Then, define a global method to initialize and shut down the MQTT client to be used from the app file.

```python
import logging

class MQTTClient:
    pass

# A singleton instance of the MQTTClient
mqtt_service = MQTTClient()


def init_mqtt_client():
    """ Initializes the MQTT client. """
    mqtt_service.connect()
    logging.info("MQTT Client Initialized")


def shutdown_mqtt_client():
    """ Shuts down the MQTT client. """
    mqtt_service.client.disconnect()
    mqtt_service.client.loop_stop()
    mqtt_service.connected = False
    logging.info("MQTT Client Shutdown")
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
import signal
import threading

from flask import Flask

from shared.infrastructure.clients import init_mqtt_client, shutdown_mqtt_client
from shared.infrastructure.database import init_db

# Create the Flask application.
app = Flask(__name__)

# Configure logging.
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
)

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
    app.logger.info(f"Received signal {signum}, shutting down server...")
    shutdown_app()

first_request = True

@app.before_request
def setup():
    global first_request

    if first_request:
        first_request = False
        init_mqtt_client()
        app.logger.info("MQTT Client Initialized")
        init_db()
        app.logger.info("Database Initialized")

# Register the shutdown function to be called when the program exits.
atexit.register(shutdown_app)

# Register the signal handler for SIGINT and SIGTERM.
signal.signal(signal.SIGINT, signal_handler)  # Closing process in the terminal
signal.signal(signal.SIGTERM, signal_handler)  # Closing process in Docker


if __name__ == '__main__':
    """ Runs the application. """
    app.logger.info(app.url_map)
    app.run(host = "0.0.0.0", port = 5000, debug = True)

```

## 5. Create a Virtual Machine with the MQTT Broker

- For this task, we'll create an Alpine Linux virtual machine and install Docker in it.
- Then, execute `cd /etc/apk` to verify the repositories of the Alpine Linux packages.
- After that, execute `apk add docker` or `sudo apk add docker` to install Docker in the Alpine Linux virtual machine and execute `service docker start` to start the Docker service.
- Then, install the Mosquitto broker with `apk add mosquitto` or `sudo apk add mosquitto`.
- Then, create some folders in the home directory of the user with `mkdir ~/mqtt/data ~/mqtt/log ~/mqtt/config` to create the folders for the MQTT broker.
- Now, execute `docker run -d -p 1883:1883 -p 9001:9001 -v ~/mqtt/data:/mqtt/data -v ~/mqtt/log/mosquitto.log:/mqtt/log/mosquitto.log -v ~/mqtt/config/mosquitto.conf:/mqtt/config/mosquitto.conf -v ~/mqtt/config/password_file.txt:/mqtt/config/password_file.txt --name mqtt-broker eclipse-mosquitto` to run the MQTT broker in the Docker container.

## 6. Configure the MQTT Broker

- To set passwords, use the mosquitto_passwd command. If you don't have it installed, use `apk add mosquitto-clients` to install the Mosquitto clients in the Alpine Linux virtual machine.
- You can set users and passwords for the broker in the password_file.txt file with `mosquitto_passwd -c ~/mqtt/password_file.txt your_username` and then set a password for that user.
- Then, restart the service broker with `sudo systemctl restart mosquitto` or `docker restart mqtt-broker` if you are using Docker.
- If you get an error of writing of the files, use this command so the broker has writing access `sudo chown -R 1883:1883 ~/mqtt/log` and then restart the container `docker restart mqtt-broker`.
- To see if that worked, analyze the logs with `docker logs mqtt-broker`.

## 7. Create message handlers and response handlers

- As you remember, we defined a method to react when a message is left in the MQTT Broker, this one:

```python
import logging

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
```

- Now, we can define the message handlers and response handlers for the MQTT broker for different topics.
- For this example, we'll define the message and response handlers for the telemetry topics.
- When using Domain-Driven Design (DDD), an interface is needed to define the message and response handlers and to orchestrate the domain logic.
- For this case, there is a MQTT interface that implements the message and response handlers. In other cases, we normally use REST interfaces for endpoints.

```python
import logging

from flask import json

from tracking.application.services import WeightRecordApplicationService

# We must implement business logic first to be orchestrated by the mqtt interface
weight_record_service = WeightRecordApplicationService()


# Define a method to validate the payload of the telemetry message.
def validate_payload(payload):
    """
    Validate the payload of the telemetry message.

    :param payload: The payload of the telemetry message.
    :raise ValueError: If the payload is invalid.
    """

    # The payload must contain the following fields: value
    required_fields = [
        "value",
    ]

    for field in required_fields:
        if field not in payload:
            raise ValueError(f"Required field is missing: {field}")

    if not isinstance(payload["value"], (int, float)):
        raise ValueError("The value must be a number")
    
    
# Define a method with logic of what you want to do with the response.
# For example, a response in a topic of responses in the same broker.
def publish_telemetry_response(device_id, telemetry_type, response):
    
    # We define this here to avoid circular imports
    from shared.infrastructure.clients import mqtt_service

    try:
        response_topic = f"store/{device_id}/response/{telemetry_type}"

        mqtt_service.publish(response_topic, json.dumps(response), qos=1)

        logging.info(
            "Response send to topic %s",
            response_topic
        )
    except Exception as ex:
        raise ValueError(f"Error while publishing response: {ex}")
    

# Define a method to process each type of telemetry
# One for the weight
def process_weight(device_id, payload):
    value = float(payload["value"])
    created_at = str(payload["created_at"])

    logging.info(
        "Weight received for device=%s with value=%s",
        device_id,
        value
    )

    record = weight_record_service.create_weight_record(
        device_id=device_id,
        value=value,
        created_at=created_at
    )

    response = {
        "status": "ok",
        "id": record.weight_record_id,
        "device_id": record.device_id,
        "weight": record.value,
        "created_at": record.created_at.isoformat()
    }

    # Publishes the response to the response topic
    publish_telemetry_response(device_id, "weight", response)


# Another one for temperature
def process_temperature(device_id, payload):
    value = payload["value"]

    logging.info(
        "Temperature received for device=%s with value=%s",
        device_id,
        value
    )

    return {
        "status": "ok",
        "received": value,
        "unit": payload["unit"]
    }


# And another for humidity
def process_humidity(device_id, payload):
    value = payload["value"]

    logging.info(
        "Humidity received for device=%s with value=%s",
        device_id,
        value
    )

    return {
        "status": "ok",
        "received": value,
        "unit": payload["unit"]
    }


# Now we define the main method to process the telemetry messages that will be registered in the MQTT broker Configuration
# You can create various of these methods for different topics and contexts.
def on_telemetry_message(msg, topic_parts):
    try:
        device_id = topic_parts[1]
        telemetry_type = topic_parts[3]

        payload = json.loads(msg.payload.decode("utf-8"))
        validate_payload(payload)

        handlers = {
            "weight": process_weight,
            "temperature": process_temperature,
            "humidity": process_humidity,
        }

        handler = handlers.get(telemetry_type)

        if handler is None:
            logging.warning(
                "Telemetry type unknown: %s",
                telemetry_type
            )
            return

        response = handler(device_id, payload)

    except Exception as ex:
        logging.exception(
            "Error while processing MQTT message: %s",
            ex
        )
```

## 8. Access the MQTT Broker

Now, we access and test the flow of sending messages through the MQTT broker and how the Flask API persists it in an SQLite Database.

### Accessing the MQTT Broker

- You can see the users created for the broker with `sudo cat ~/mosquitto/config/password_file.txt`.
- Use `docker exec -it -u 1883 mqtt-broker sh` to enter the container.
- Or, you can use `mosquitto_sub -h localhost -p 1883 -t '#' -v` to see all the topics that are available in the MQTT broker.

### Testing the MQTT Broker

- Then, use `mosquitto_sub -h localhost -p 1883 -u your_username -P your_password -t "stores/+/telemetry/#" -v` to subscribe to the topics of the MQTT broker and see the messages that are published in those topics.
- To send a message to the MQTT broker, use `mosquitto_pub -h localhost -p 1883 -u your_username -P your_password -t "stores/1234567890/telemetry/temperature" -m '{"value": 25.0, "created_at": ""2026-08-14 06:19:12}'` to publish a message to the MQTT broker in the topic "stores/1234567890/telemetry/temperature."

### Sending Messages to the MQTT Broker

Here, you can see the messages that are sent to the MQTT broker.

<div align="center">
    <img src="https://i.imgur.com/zaHJjY6.png" alt="Sending messages to the broker" width="800">
</div>

Now, you can see the messages that are received by the MQTT Broker in the subscribed topic.

<div align="center">
    <img src="https://i.imgur.com/RteBwxR.png" alt="Subscribing and seeing entry messages in the broker" width="800">
</div>

Finally, after the Flask API processes the message, the payload is persisted in the SQLite database.

<div align="center">
    <img src="https://i.imgur.com/UtHeM0i.png" alt="Testing payload persisted in an SQLite database" width="800">
</div>