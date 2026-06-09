#!/usr/bin/env python3
"""
Custom Prometheus Exporter for Sentiment API
- Polls /api/latest-confidence every 5 seconds
- Exposes metric: prediction_confidence_score
- Runs on port 8000 on EC2
"""

import time
import requests
from prometheus_client import start_http_server, Gauge

# The single metric Prometheus will scrape
CONFIDENCE_GAUGE = Gauge(
    'prediction_confidence_score',
    'Latest prediction confidence score from the sentiment ML API'
)

# The app is accessible via NodePort 32500 on EC2 localhost (via minikube)
APP_URL = "http://localhost:32500/api/latest-confidence"
POLL_INTERVAL = 5  # seconds
DEFAULT_CONFIDENCE = 1.0  # use 1.0 when endpoint unreachable


def fetch_confidence():
    """Fetch latest confidence score from the ML API."""
    try:
        response = requests.get(APP_URL, timeout=3)
        response.raise_for_status()
        data = response.json()
        confidence = float(data.get("confidence", DEFAULT_CONFIDENCE))
        print(f"[OK]  confidence = {confidence:.4f}")
        return confidence
    except Exception as e:
        print(f"[WARN] Could not reach {APP_URL}: {e} — using default {DEFAULT_CONFIDENCE}")
        return DEFAULT_CONFIDENCE


def main():
    # Start the HTTP server on port 8000 so Prometheus can scrape /metrics
    start_http_server(8000)
    print("=== Prometheus Exporter started on port 8000 ===")
    print(f"=== Polling {APP_URL} every {POLL_INTERVAL}s ===")

    while True:
        confidence = fetch_confidence()
        CONFIDENCE_GAUGE.set(confidence)
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
