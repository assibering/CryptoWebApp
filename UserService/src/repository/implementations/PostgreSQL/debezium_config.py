from src.db.settings import get_settings

async def generate_config_dict(settings):
    return {
        "name": "users-outbox-connector",
        "config": {
            "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
            "tasks.max": "1",
            "database.hostname": settings.DB_HOST,
            "database.port": settings.DB_PORT,
            "database.user": settings.DB_USER,
            "database.password": settings.DB_PASSWORD,
            "database.dbname": settings.DB_NAME,
            "database.server.name": "userservice",
            "schema.include.list": "auth",
            "table.include.list": "auth.users_outbox",
            "plugin.name": "pgoutput",
            "publication.name": "dbz_publication_user",
            "tombstones.on.delete": "false",
            "topic.prefix": "userservice",
            "slot.name": "debezium_user",

            "transforms": "outbox",
            "transforms.outbox.type": "io.debezium.transforms.outbox.EventRouter",
            "transforms.outbox.route.by.field": "aggregatetype",
            "transforms.outbox.route.topic.replacement": "userservice.${routedByValue}",

            "transforms.outbox.field.event.id": "id",
            "transforms.outbox.field.event.key": "aggregateid",
            "transforms.outbox.field.event.type": "eventtype",
            "transforms.outbox.field.event.payload": "payload",
            "transforms.outbox.field.event.timestamp": "created_at",
            "transforms.outbox.field.event.timestamp.type": "io.debezium.time.Timestamp",

            "transforms.outbox.expand.json.payload": "true",
            "transforms.outbox.table.fields.additional.placement": "eventtype:envelope:type"
        }
    }

# CONSUMER CONSUMES:
# ConsumerRecord(
#     topic='userservice.user',
#     partition=0,
#     offset=0,
#     timestamp=1746240679362,
#     timestamp_type=0,
#     key=b'{"schema":{"type":"string","optional":false},"payload":"dummy@email.com"}',
#     value={
#         'schema': {
#             'type': 'struct',
#             'fields': [
#                 {'type': 'string', 'optional': False, 'name': 'io.debezium.data.Json', 'version': 1, 'field': 'payload'},
#                 {'type': 'string', 'optional': False, 'field': 'type'}
#             ],
#             'optional': False,
#             'name': 'userservice.auth.users_outbox.user.Value'
#         },
#         'payload': {
#             'payload': '{"email": "dummy@email.com", "is_active": null}',
#             'type': 'user_created_success'
#         }
#     },
#     checksum=None,
#     serialized_key_size=73,
#     serialized_value_size=360,
#     headers=(('id', b'1f027c97-d169-63a8-9cbf-56b86948d5eb'),)
# )
