from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    "com.udacity.datastreaming.sfcrimes",
    bootstrap_servers=["localhost:9092"],
    auto_offset_reset="earliest",
    group_id="consumer-group-1")

for message in consumer:
    print(message.value)