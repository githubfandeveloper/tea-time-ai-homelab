from flask import Flask, Response, jsonify
from prometheus_client import (
    Counter, Histogram, Gauge,
    generate_latest, CONTENT_TYPE_LATEST
)
import random
import time
import logging

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s: %(message)s'
)
logger = logging.getLogger("teatime-sample-app")

REQUEST_COUNT = Counter(
    'http_requests_total', 'Total HTTP requests',
    ['method', 'endpoint', 'status']
)
REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds', 'Request latency',
    ['endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
)
APP_HEALTH = Gauge('app_health_status', 'Health: 1=ok, 0=broken')

FAILURE_MODE = False
APP_HEALTH.set(1)


@app.route('/')
def home():
    start = time.time()
    if FAILURE_MODE and random.random() < 0.7:
        duration = time.time() - start
        REQUEST_COUNT.labels('GET', '/', '500').inc()
        REQUEST_LATENCY.labels('/').observe(duration)
        logger.error("REQUEST FAILED: 500 - app in failure mode")
        return jsonify({"error": "Internal Server Error"}), 500

    time.sleep(random.uniform(0.01, 0.1))
    duration = time.time() - start
    REQUEST_COUNT.labels('GET', '/', '200').inc()
    REQUEST_LATENCY.labels('/').observe(duration)
    logger.info("REQUEST OK: 200 - duration=%.3fs", duration)
    return jsonify({"status": "ok"}), 200


@app.route('/health')
def health():
    if FAILURE_MODE:
        return jsonify({"status": "unhealthy"}), 503
    return jsonify({"status": "healthy"}), 200


@app.route('/break')
def break_app():
    global FAILURE_MODE
    FAILURE_MODE = True
    APP_HEALTH.set(0)
    logger.critical("APP BROKEN - Failure mode ACTIVATED")
    return jsonify({
        "status": "broken",
        "message": "70 percent of requests will now return 500"
    }), 200


@app.route('/fix')
def fix_app():
    global FAILURE_MODE
    FAILURE_MODE = False
    APP_HEALTH.set(1)
    logger.info("APP FIXED - Failure mode DEACTIVATED")
    return jsonify({"status": "fixed"}), 200


@app.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


if __name__ == '__main__':
    logger.info("Tea Time Sample App starting on port 5000...")
    app.run(host='0.0.0.0', port=5000)