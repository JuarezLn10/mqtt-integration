from datetime import datetime


class WeightRecord:
    """
    Telemetry record of weight.

    Attributes:
        weight_record_id (int): The unique identifier of the weight record.
        device_id (str): The unique identifier of the device.
        value (float): The weight value.
        created_at (datetime): The date and time when the weight record was created.
    """

    def __init__(
            self,
            device_id: str,
            value: float,
            created_at: datetime,
            weight_record_id: int | None = None
    ):
        """
        Initializes a new instance of the WeightRecord class.

        :param device_id: The unique identifier of the device.
        :param value: The weight value.
        :param created_at: The date and time when the weight record was created.
        :param weight_record_id: The unique identifier of the weight record.
        """

        self.weight_record_id = weight_record_id
        self.device_id = device_id
        self.value = value
        self.created_at = created_at