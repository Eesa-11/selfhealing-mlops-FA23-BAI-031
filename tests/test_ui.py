"""
Selenium Headless UI Test for Sentiment Analyzer frontend.
Function name must be exactly: test_frontend_sentiment
Tests against the index.html frontend using the 3 fixed element IDs.
"""

import os
import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = os.environ.get("BASE_URL", "http://localhost:5000")


@pytest.fixture
def driver():
    """Set up headless Chrome driver."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1280,720")

    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)
    yield driver
    driver.quit()


def test_frontend_sentiment(driver):
    """
    Load the frontend, enter a test sentence, click Analyze,
    and assert the result contains POSITIVE, NEGATIVE, or Confidence.
    """
    # Navigate to the app frontend
    driver.get(BASE_URL)

    # Wait for the page to load and find the text input (element ID: text-input)
    wait = WebDriverWait(driver, 15)
    text_input = wait.until(
        EC.presence_of_element_located((By.ID, "text-input"))
    )

    # Type a test sentence into the input
    test_sentence = "This product is absolutely amazing and I love it"
    text_input.clear()
    text_input.send_keys(test_sentence)

    # Click the submit button (element ID: submit-btn)
    submit_btn = driver.find_element(By.ID, "submit-btn")
    submit_btn.click()

    # Wait for the result to appear (element ID: result-output)
    result_div = wait.until(
        EC.presence_of_element_located((By.ID, "result-output"))
    )

    # Wait a bit more for the async call to complete
    time.sleep(3)

    result_text = result_div.text.strip()

    # Assert result is non-empty AND contains POSITIVE, NEGATIVE, or Confidence
    assert len(result_text) > 0, "result-output div is empty after clicking Analyze"

    assert any(keyword in result_text for keyword in ["POSITIVE", "NEGATIVE", "Confidence"]), \
        f"Result output does not contain expected keywords. Got: '{result_text}'"

    print(f"[PASS] Frontend result: {result_text}")
