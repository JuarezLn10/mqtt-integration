from peewee import SqliteDatabase

# Shared SQLite database instance for the edge service
db = SqliteDatabase("edge_service.db")


def init_db() -> None:
    """
    Initializes the database, connects to it, and creates tables if they don't exist.

    Also, it imports ORM models from contexts through deferred imports to avoid circular dependencies.
    """
    should_close = db.is_closed()
    if should_close:
        db.connect()

    from tracking.infrastructure.repositories import WeightRecordModel

    db.create_tables([
        WeightRecordModel
    ], safe=True)

    if should_close and not db.is_closed():
        db.close()