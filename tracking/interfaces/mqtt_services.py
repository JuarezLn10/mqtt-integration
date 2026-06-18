import logging

from flask import json, jsonify

from tracking.application.services import WeightRecordApplicationService

weight_record_service = WeightRecordApplicationService()


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


def publish_telemetry_response(device_id, telemetry_type, response):
    """
    Function that publishes the response to the response topic.

    :param device_id: The device ID.
    :param telemetry_type: The type of telemetry message.
    :param response: The response to be published, which will be converted to JSON before publishing.
    """

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


def process_weight(device_id, payload):
    """
    Process the weight telemetry message.

    :param device_id: The device ID.
    :param payload: The payload of the telemetry message.
    """

    value = payload["value"]
    created_at = payload["created_at"]

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

    response = jsonify({
        "id": record.weight_record_id,
        "device_id": record.device_id,
        "weight": record.value,
        "created_at": record.created_at.isoformat()
    })

    # Publishes the response to the response topic
    publish_telemetry_response(device_id, "weight", response)


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


def on_telemetry_message(msg, topic_parts):
    """
    Validates the type of telemetry message and calls the appropriate handler.

    :param msg: The MQTT message.
    :param topic_parts: The topic parts, divided from the original topic string.
    """

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