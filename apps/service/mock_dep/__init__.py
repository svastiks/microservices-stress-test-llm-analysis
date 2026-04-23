import os
import random
import time
from flask import Flask
app = Flask(__name__)
LATENCY_MS = int(os.environ.get("LATENCY_MS", "0"))
ERROR_RATE = float(os.environ.get("ERROR_RATE", "0"))

@app.route("/")
def root():
    if LATENCY_MS > 0:
        time.sleep(LATENCY_MS / 1000.0)
    if random.random() < ERROR_RATE:
        return "", 500
    return "ok", 200
