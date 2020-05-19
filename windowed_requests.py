import faust
from datetime import timedelta
from models import APIRequest

APP_NAME = "windowed_requests"
KAFKA_BROKER = "kafka://localhost:9092"
KAFKA_TOPIC_PARTITIONS = 1
KAFKA_TOPIC_NAME = "windowed_requests"
WINDOW_DURATION_MINUTES = 1
TABLE_DATA_EXPIRATION_MINUTES = 5
DEBUG_LOGGING_ENABLED = True


# Define Faust App
app = faust.App(APP_NAME, broker=KAFKA_BROKER, topic_partitions=KAFKA_TOPIC_PARTITIONS)


# Define Kafka topic with message schema
windowed_requests_topic = app.topic(KAFKA_TOPIC_NAME, value_type=APIRequest)


# Define aggregation table
windowed_requests_by_user = app.Table(
    "windowed_requests_by_user", default=int
).tumbling(
    timedelta(minutes=WINDOW_DURATION_MINUTES),
    expires=timedelta(minutes=TABLE_DATA_EXPIRATION_MINUTES),
    key_index=True,
)


def log(message):
    if DEBUG_LOGGING_ENABLED:
        print(message)


# Increment incoming request counts based on user_id
@app.agent(windowed_requests_topic)
async def aggregate_api_requests(api_requests):
    async for api_request in api_requests:
        user_id = api_request.user_id

        if user_id:
            windowed_requests_by_user[user_id] += 1
            log("API request from user: " + user_id)


# Expose metrics API for current time window
@app.page("/metrics/users/{user_id}")
@app.table_route(table=windowed_requests_by_user, match_info="user_id")
async def get_request_count_by_user(web, request, user_id):
    num_requests = windowed_requests_by_user[user_id].now()
    log(
        "Requests by user {} in last {} minute(s): {}".format(
            user_id, str(WINDOW_DURATION_MINUTES), num_requests
        )
    )

    return web.json(
        dict(window_duration=WINDOW_DURATION_MINUTES, total_requests=num_requests)
    )
