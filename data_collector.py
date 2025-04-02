from fastapi import FastAPI
import redis
import json
import requests

app = FastAPI()
r = redis.Redis.from_url("redis://localhost:6379")

@app.get("/collect")
def collect_data():
    url = f"https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=5m&limit=1"
    response = requests.get(url)
    if response.status_code == 200:
        kline = response.json()[0]
        data = {
            "price": float(kline[4]),
            "timestamp": kline[6]
        }
        r.publish("raw_data", json.dumps(data))
        return {"status": "data published", "data": data}
    return {"status": "error", "code": response.status_code}
