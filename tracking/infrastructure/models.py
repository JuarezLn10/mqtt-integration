from peewee import Model, AutoField, CharField, FloatField, DateTimeField

from shared.infrastructure.database import db


class WeightRecordModel(Model):
    """
    ORM model for weight records.

    Attributes:
        weight_record_id (AutoField): Unique identifier for the weight record.
        device_id (CharField): Unique identifier for the device.
        value (FloatField): The weight value recorded.
        created_at (DateTimeField): Timestamp when the record was created.
    """

    weight_record_id = AutoField()
    device_id = CharField()
    value = FloatField()
    created_at = DateTimeField()

    class Meta:
        """ Metadata for the WeightRecordModel class. """

        database = db
        table_name = "weight_records"