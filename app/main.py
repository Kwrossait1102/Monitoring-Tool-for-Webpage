from fastapi import FastAPI
import requests, time, os

app = FastAPI()

# load URL from enviroment variable
TARGET_URL = os.getenv("TARGET_URL", "https://example.com")

@app.get("/")
def check_availability():
    start = time.time()
    try:
        r = requests.get(TARGET_URL, timeout=5)
        latency = round((time.time() - start) * 1000, 2)
        return {
            "url": TARGET_URL,
            "status_code": r.status_code,
            "available": r.ok,
            "latency_ms": latency
        }
    except Exception as e:
        return {"url": TARGET_URL, "available": False, "error": str(e)}
