import logging

from flask import json
from paho.mqtt import client as mqtt_client

from shared.infrastructure.configuration import MQTTConfig


class MQTTClient:
    def __init__(self, config: MQTTConfig):
        self.config = config
        self.connected = False
        self.client = mqtt_client.Client(
            client_id=config.CLIENT_ID,
            callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2
        )
        self.client.username_pw_set(
            config.USERNAME,
            config.PASSWORD,
        )
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def connect(self):
        if self.connected:
            return

        self.client.connect(
            self.config.HOST,
            self.config.PORT,
            keepalive=60
        )

        self.client.loop_start()
        self.connected = True
        logging.info(
            "Connected to MQTT at %s:%s",
            self.config.HOST,
            self.config.PORT
        )

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()

        self.connected = False

    def on_connect(
            self,
            client,
            userdata,
            flags,
            rc,
            properties=None
    ):
        if rc != 0:
            logging.error(
                "MQTT Error. RC=%s",
                rc
            )
            return

        logging.info(
            "Connected to MQTT Broker"
        )

        for topic in self.config.SUBSCRIPTIONS:
            client.subscribe(
                topic,
                qos=1
            )
            logging.info(
                "Subscribed to %s",
                topic
            )

    def on_message(
            self,
            client,
            userdata,
            msg
    ):
        try:
            topic_parts = msg.topic.split("/")
            device_id = topic_parts[1]
            telemetry_type = topic_parts[3]
            payload = json.loads(
                msg.payload.decode()
            )
            self.validate_payload(
                payload
            )

            handlers = {
                "weight": self.process_weight,
                "temperature": self.process_temperature,
                "humidity": self.process_humidity
            }

            handler = handlers.get(
                telemetry_type
            )

            if handler is None:
                logging.warning(
                    "Telemetry type unknown: %s",
                    telemetry_type
                )

                return

            response = handler(
                device_id,
                payload
            )

            self.publish_response(
                device_id,
                telemetry_type,
                response
            )

        except Exception as ex:

            logging.exception(
                "Error while processing MQTT message: %s",
                ex
            )

    def validate_payload(
            self,
            payload
    ):

        required_fields = [
            "timestamp",
            "value",
            "unit"
        ]

        for field in required_fields:

            if field not in payload:
                raise ValueError(
                    f"Required field is missing: {field}"
                )

        if not isinstance(
                payload["value"],
                (int, float)
        ):
            raise ValueError(
                "The value must be a number"
            )


    def process_weight(
            self,
            device_id,
            payload
    ):

        value = payload["value"]

        logging.info(
            "Weight received for device=%s with value=%s",
            device_id,
            value
        )

        return {
            "status": "ok",
            "received": value,
            "unit": payload["unit"]
        }

    def process_temperature(
            self,
            device_id,
            payload
    ):

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

    def process_humidity(
            self,
            device_id,
            payload
    ):

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

    def publish_response(
            self,
            device_id,
            telemetry_type,
            response
    ):

        response_topic = (
            f"store/{device_id}/response/"
            f"{telemetry_type}"
        )

        self.client.publish(
            response_topic,
            json.dumps(response),
            qos=1
        )

        logging.info(
            "Response send to topic %s",
            response_topic
        )

    def publish(
            self,
            topic,
            payload,
            qos=1
    ):

        self.client.publish(
            topic,
            json.dumps(payload),
            qos=qos
        )

mqtt_service = MQTTClient(MQTTConfig())

def init_mqtt_client():
    mqtt_service.connect()