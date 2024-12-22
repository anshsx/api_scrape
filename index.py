from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import requests
import concurrent.futures

app = Flask(__name__)

def scrape_content(url):
    """Function to scrape content from the given URL."""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            return {"title": soup.title.string if soup.title else "No Title Found"}
        else:
            return {"error": f"HTTP Error: {response.status_code}"}
    except requests.RequestException as e:
        return {"error": str(e)}

@app.route('/scrape_weather', methods=['POST'])
def scrape_weather():
    """API endpoint to scrape content."""
    data = request.get_json()
    url = data.get("urls")

    if not url:
        return jsonify({"error": "URL is required"}), 400

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(scrape_content, url)
        try:
            result = future.result(timeout=6)  # Timeout in seconds
        except concurrent.futures.TimeoutError:
            return jsonify({"error": "Scraping timed out"}), 504

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
