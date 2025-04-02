from fastapi import FastAPI
import redis
import json
import threading

app = FastAPI()
r = redis.Redis.from_url("redis://localhost:6379")

def handle_features(msg):
    if msg['type'] != 'message':
        return
    features = json.loads(msg['data'].decode())
    rsi = features["rsi"]
    signal = None
    if rsi < 30:
        signal = "BUY"
    elif rsi > 70:
        signal = "SELL"
    if signal:
        r.publish("trade_signal", json.dumps({"signal": signal, "price": features["price"]}))

@app.on_event("startup")
def subscribe():
    pubsub = r.pubsub()
    pubsub.subscribe("features")
    thread = threading.Thread(target=lambda: [handle_features(msg) for msg in pubsub.listen()])
    thread.start()
