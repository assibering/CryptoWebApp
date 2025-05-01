from src.db.settings import get_settings

async def generate_config_dict(settings):
    return {
        "name": "subscriptions-outbox-connector",
        "config": {
            "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
            "tasks.max": "1",
            "database.hostname": settings.DB_HOST,
            "database.port": settings.DB_PORT,
            "database.user": settings.DB_USER,
            "database.password": settings.DB_PASSWORD,
            "database.dbname": settings.DB_NAME,
            "database.server.name": "subscriptionservice",
            "schema.include.list": "auth",
            "table.include.list": "auth.subscriptions_outbox",
            "plugin.name": "pgoutput",
            "publication.name": "dbz_publication",
            "tombstones.on.delete": "false",

            "transforms": "outbox",
            "transforms.outbox.type": "io.debezium.transforms.outbox.EventRouter",
            "transforms.outbox.route.by.field": "aggregatetype",
            "transforms.outbox.route.topic.replacement": "${routedByValue}",

            "transforms.outbox.table.field.event.id": "id",
            "transforms.outbox.table.field.event.key": "aggregateid",
            "transforms.outbox.table.field.event.type": "type",
            "transforms.outbox.table.field.event.payload": "payload",
            "transforms.outbox.table.field.event.timestamp": "created_at",
            "transforms.outbox.expand.json.payload": "true"
        }
    }