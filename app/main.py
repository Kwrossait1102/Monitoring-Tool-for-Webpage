from fastapi import FastAPI
import requests, time

app = FastAPI()

TARGET_URL = "https://www.sap.com/germany/index.html"

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
