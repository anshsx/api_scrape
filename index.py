from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

app = Flask(__name__)

def scrape_url(url):
    """Scrapes content from a single URL."""
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

@app.route('/api/scrape', methods=['POST'])
def scrape_weather():
    """API endpoint to scrape and combine weather data from provided URLs with a 9-second timeout."""
    data = request.get_json()
    if not data or 'urls' not in data:
        return jsonify({"error": "Invalid input JSON. 'urls' key is required."}), 400

    urls = data['urls']
    combined_content = []
    start_time = time.time()

    with ThreadPoolExecutor() as executor:
        # Submit scraping tasks to the executor
        futures = {executor.submit(scrape_url, url): url for url in urls}

        for future in as_completed(futures):
            # Stop processing if 9 seconds have passed
            if time.time() - start_time > 9:
                break
            content = future.result()
            if content:
                combined_content.append(content)

    # Combine all content into a single string
    full_content = ' '.join(combined_content)

    return jsonify({"content": full_content})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
