from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/scrape_weather', methods=['POST'])
def scrape_weather():
    """API endpoint to scrape and combine weather data from provided URLs."""
    data = request.get_json()
    if not data or 'urls' not in data:
        return jsonify({"error": "Invalid input JSON. 'urls' key is required."}), 400

    urls = data['urls']
    combined_content = []

    for url in urls:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code != 200:
                # Skip URLs that don't return a 200 status code
                continue

            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract relevant text content
            body_tags = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            content = ' '.join(tag.get_text(strip=True) for tag in body_tags)

            combined_content.append(content)
        except requests.RequestException:
            # Skip URLs that raise an exception
            continue

    # Combine all content into a single string
    full_content = ' '.join(combined_content)

    return jsonify({"content": full_content})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
