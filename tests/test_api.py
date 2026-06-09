"""
PyTest Unit Tests for Sentiment API
Run against BASE_URL = "http://<ip>:5000"
All 4 function names are required EXACTLY as written.
"""

import os
import pytest
import requests

# Get base URL from environment variable, default to localhost:5000
BASE_URL = os.environ.get("BASE_URL", "http://localhost:5000")


def test_health_endpoint():
    """GET /health -> HTTP 200; 'status':'healthy' and key 'model_version' present"""
    response = requests.get(f"{BASE_URL}/health", timeout=10)

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    data = response.json()
    assert data.get("status") == "healthy", f"Expected status=healthy, got: {data}"
    assert "model_version" in data, f"Key 'model_version' missing from response: {data}"


def test_predict_returns_label_and_confidence():
    """POST /predict -> HTTP 200; label in [POSITIVE,NEGATIVE]; 0<=confidence<=1; 'model_version' present"""
    payload = {"text": "This is a wonderful product I really love it"}
    response = requests.post(
        f"{BASE_URL}/predict",
        json=payload,
        timeout=30
    )

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    data = response.json()
    assert data.get("label") in ["POSITIVE", "NEGATIVE"], \
        f"Label must be POSITIVE or NEGATIVE, got: {data.get('label')}"

    confidence = data.get("confidence")
    assert confidence is not None, "Response missing 'confidence' field"
    assert 0 <= float(confidence) <= 1, f"Confidence must be between 0 and 1, got: {confidence}"

    assert "model_version" in data, f"Key 'model_version' missing from response: {data}"


def test_predict_negative_text():
    """POST /predict with negative text -> HTTP 200"""
    payload = {"text": "This is terrible, I hate it, worst product ever"}
    response = requests.post(
        f"{BASE_URL}/predict",
        json=payload,
        timeout=30
    )

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"


def test_health_returns_model_version_unstable():
    """GET /health -> model_version == 'unstable-v1' exactly"""
    response = requests.get(f"{BASE_URL}/health", timeout=10)

    assert response.status_code == 200

    data = response.json()
    model_version = data.get("model_version")
    assert model_version == "unstable-v1", \
        f"Expected model_version='unstable-v1', got: '{model_version}'"
