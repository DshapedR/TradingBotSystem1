from fastapi import FastAPI
import redis
import json
import threading
import hmac
import hashlib
import time
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
r = redis.Redis.from_url("redis://localhost:6379")

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

BASE_URL = "https://testnet.binance.vision"

headers = {
    "X-MBX-APIKEY": API_KEY
}

def sign_params(params, secret):
    query_string = "&".join([f"{key}={params[key]}" for key in sorted(params)])
    return hmac.new(secret.encode(), query_string.encode(), hashlib.sha256).hexdigest()

def execute_order(symbol, side, quantity):
    endpoint = f"{BASE_URL}/api/v3/order"
    timestamp = int(time.time() * 1000)
    params = {
        "symbol": symbol,
        "side": side,
        "type": "MARKET",
        "quantity": quantity,
        "timestamp": timestamp
    }
    params["signature"] = sign_params(params, API_SECRET)
    response = requests.post(endpoint, headers=headers, params=params)
    print(response.json())

def handle_signal(msg):
    if msg['type'] != 'message':
        return
    signal = json.loads(msg['data'].decode())
    print(f"Executing {signal['signal']} at price {signal['price']}")
    execute_order("BTCUSDT", signal["signal"], 0.001)

@app.on_event("startup")
def subscribe():
    pubsub = r.pubsub()
    pubsub.subscribe("trade_signal")
    thread = threading.Thread(target=lambda: [handle_signal(msg) for msg in pubsub.listen()])
    thread.start()
