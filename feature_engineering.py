from fastapi import FastAPI
import redis
import json
import numpy as np
import threading

app = FastAPI()
r = redis.Redis.from_url("redis://localhost:6379")

def handle_raw_data(msg):
    if msg['type'] != 'message':
        return
    data = json.loads(msg['data'].decode())
    price = float(data["price"])
    rsi = np.random.randint(10, 90)
    features = {"price": price, "rsi": rsi}
    r.publish("features", json.dumps(features))

@app.on_event("startup")
def subscribe():
    pubsub = r.pubsub()
    pubsub.subscribe("raw_data")
    thread = threading.Thread(target=lambda: [handle_raw_data(msg) for msg in pubsub.listen()])
    thread.start()
