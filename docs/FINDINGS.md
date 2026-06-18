# Integration of a MQTT Client in a Flask App (Python)

## 1. Dependencies for connecting to a MQTT broker

### MQTT-Paho

The MQTT-Paho library is used to connect to a MQTT broker, and it is a Python library that implements the MQTT protocol.
To install the MQTT-Paho library, you can use pip:

```bash
pip install paho-mqtt
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