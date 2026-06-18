from tracking.domain.entities import WeightRecord
from tracking.infrastructure.models import WeightRecordModel


class WeightRecordRepository:
    """
    Repository for weight record operations.

    This persists weight records to the database.
    """

    @staticmethod
    def save(weight_record: WeightRecord) -> WeightRecord:
        """
        Persist weight record to the database.

        :param weight_record: The weight record to persist.
        :return: A new weight record with the generated ID.
        """

        record = WeightRecordModel.create(
            device_id=weight_record.device_id,
            value=weight_record.value,
            created_at=weight_record.created_at
        )

        return WeightRecord(
            weight_record_id=record.weight_record_id,
            device_id=record.device_id,
            value=record.value,
            created_at=record.created_at
        )