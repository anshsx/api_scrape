from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/scrape_weather', methods=['POST'])
def scrape_weather():
    """API endpoint to scrape weather data from provided URLs."""
    data = request.get_json()
    if not data or 'urls' not in data:
        return jsonify({"error": "Invalid input JSON. 'urls' key is required."}), 400

    urls = data['urls']
    scraped_results = []

    for url in urls:
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract relevant text content
            body_tags = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            content = ' '.join(tag.get_text(strip=True) for tag in body_tags)

            scraped_results.append({
                "link": url,
                "content": content
            })
        except requests.RequestException as e:
            print(f"Failed to scrape {url}: {e}")
            continue

    return jsonify({"results": scraped_results})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
