from datetime import datetime, timezone

from tracking.domain.entities import WeightRecord


class WeightRecordService:
    """
    Domain service for weight record operations.
    """

    @classmethod
    def create_weight_record(
            cls,
            device_id: str,
            value: float,
            created_at: str | None = None,
            weight_record_id: int | None = None
    ) -> WeightRecord:
        """
        Creates a new weight record.

        :param device_id: The ID of the device.
        :param value: The weight value.
        :param created_at: The date and time when the weight record was created.
        :param weight_record_id: The ID of the weight record.
        :return: A new weight record.
        """

        try:
            parsed_weight = float(value)
            if parsed_weight < 0:
                raise ValueError("Weight cannot be negative.")

            if created_at:
                parsed_created_at = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
            else:
                parsed_created_at = datetime.now(timezone.utc)
        except (ValueError, TypeError):
            raise ValueError("Invalid data format.")

        return WeightRecord(
            weight_record_id=weight_record_id,
            device_id=device_id,
            value=parsed_weight,
            created_at=parsed_created_at,
        )