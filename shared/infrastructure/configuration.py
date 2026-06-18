from dataclasses import dataclass


@dataclass
class MQTTConfig:
    HOST = "broker.local"
    PORT = 1883
    USERNAME = "backend"
    PASSWORD = "secret"
    CLIENT_ID = "flask_backend"
    SUBSCRIPTIONS = [
        "stores/+/telemetry/weight",
        "stores/+/telemetry/temperature",
        "stores/+/telemetry/humidity"
    ]