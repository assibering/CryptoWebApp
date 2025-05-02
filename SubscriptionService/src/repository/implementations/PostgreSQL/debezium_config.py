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
            "publication.name": "dbz_publication_subscription",
            "tombstones.on.delete": "false",
            'topic.prefix': 'subscriptionservice',
            "slot.name": "debezium_subscription",

            "transforms": "outbox",
            "transforms.outbox.type": "io.debezium.transforms.outbox.EventRouter",
            "transforms.outbox.route.by.field": "aggregatetype",
            "transforms.outbox.route.topic.replacement": "subscriptionservice.${routedByValue}",

            "transforms.outbox.field.event.id": "id",
            "transforms.outbox.field.event.key": "aggregateid",
            "transforms.outbox.field.event.type": "eventtype",
            "transforms.outbox.field.event.payload": "payload",
            "transforms.outbox.field.event.timestamp": "created_at",
            "transforms.outbox.field.event.timestamp.type": "io.debezium.time.Timestamp",

            "transforms.outbox.expand.json.payload": "true",
            "transforms.outbox.fields.additional.placement": "eventtype:envelope:type"
        }
    }