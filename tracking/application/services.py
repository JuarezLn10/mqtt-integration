from tracking.domain.entities import WeightRecord
from tracking.domain.services import WeightRecordService
from tracking.infrastructure.repositories import WeightRecordRepository


class WeightRecordApplicationService:
    """
    Application Service for the weight record domain.

    Attributes:
        weight_record_repository (WeightRecordRepository): The repository for weight records.
        weight_record_service (WeightRecordService): The service for weight record operations.
    """

    def __init__(self):
        """ Initializes the application service. """
        self.weight_record_repository = WeightRecordRepository()
        self.weight_record_service = WeightRecordService()

    def create_weight_record(
            self,
            device_id: str,
            value: float,
            created_at: str | None = None,
    ) -> WeightRecord:
        """
        Creates a new weight record.

        :param device_id: The ID of the device.
        :param value: The weight value.
        :param created_at: The date and time when the weight record was created.
        :return: A new weight record.
        """

        record = self.weight_record_service.create_weight_record(
            device_id=device_id,
            value=value,
            created_at=created_at
        )

        return self.weight_record_repository.save(record)