from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import signal

app = Flask(__name__)

# Signal handler for enforcing timeouts
class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException("Execution exceeded time limit")

# Scraping logic
def scrape_url(url):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            return ""
        soup = BeautifulSoup(response.text, 'html.parser')
        body_tags = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        content = ' '.join(tag.get_text(strip=True) for tag in body_tags)
        return content
    except requests.RequestException:
        return ""

@app.route('/scrape_weather', methods=['POST'])
def scrape_weather():
    """Scrape URLs and enforce a strict 8-second timeout."""
    data = request.get_json()
    if not data or 'urls' not in data:
        return jsonify({"error": "Invalid input JSON. 'urls' key is required."}), 400

    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(8)  # Set timeout for the request

    combined_content = []
    try:
        urls = data['urls']
        for url in urls:
            content = scrape_url(url)
            if content:
                combined_content.append(content)
        signal.alarm(0)  # Disable alarm after success
    except TimeoutException:
        return jsonify({"content": "Scraping stopped due to timeout."}), 408

    return jsonify({"content": ' '.join(combined_content)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
