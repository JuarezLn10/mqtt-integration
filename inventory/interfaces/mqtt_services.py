import logging

from flask import json




def validate_payload(payload):
    required_fields = [
        "timestamp",
        "value",
        "unit"
    ]

    for field in required_fields:
        if field not in payload:
            raise ValueError(f"Required field is missing: {field}")

    if not isinstance(payload["value"], (int, float)):
        raise ValueError("The value must be a number")


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
        publish_telemetry_response(device_id, telemetry_type, response)

    except Exception as ex:
        logging.exception(
            "Error while processing MQTT message: %s",
            ex
        )


def publish_telemetry_response(device_id, telemetry_type, response):
    from shared.infrastructure.clients import mqtt_service

    response_topic = f"store/{device_id}/response/{telemetry_type}"

    mqtt_service.publish(response_topic, json.dumps(response), qos=1)

    logging.info(
        "Response send to topic %s",
        response_topic
    )


def process_weight(device_id, payload):
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


def process_temperature(device_id, payload):
    value = payload["value"]

    logging.info(
        "Temperature received for device=%s with value=%s",
        device_id,
        value
    )

    publish_telemetry_response()

    return {
        "status": "ok",
        "received": value,
        "unit": payload["unit"]
    }


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


