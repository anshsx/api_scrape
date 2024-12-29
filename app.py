# app.py
from flask import Flask, request, jsonify
import requests
from index import scrape  # Import the scrape function from index.py

app = Flask(__name__)

# In-memory store for API keys and credits (In a real-world case, you would use a database)
api_keys = {
    "sample-api-key-123": {"credits": 10},  # API Key: credits
    "sample-api-key-456": {"credits": 5}
}

# Helper function to check API key and credits
def check_api_key_and_credits(api_key):
    if api_key not in api_keys:
        return False, "Invalid API key"
    
    credits = api_keys[api_key]["credits"]
    if credits <= 0:
        return False, "Credit limit exceeded, please buy more credits"
    
    return True, credits

@app.route('/scrape', methods=['POST'])
def scrape_api():
    # Get data from the request
    data = request.get_json()

    # Check if required parameters are in the request
    if not data or 'query' not in data or 'ratio' not in data or 'api_key' not in data:
        return jsonify({"error": "Missing required parameters: 'query', 'ratio', or 'api_key'."}), 400
    
    api_key = data['api_key']
    query = data['query']
    ratio = data['ratio'].lower()

    # Validate API key and credits
    is_valid, message = check_api_key_and_credits(api_key)
    if not is_valid:
        return jsonify({"error": message}), 403

    # Call the scrape function from index.py if the API key is valid
    try:
        results = scrape(query, ratio)
        if results:
            # Decrease credits if the request is successful
            api_keys[api_key]["credits"] -= 1
            return jsonify(results)
        else:
            return jsonify({"error": "No results found"}), 500

    except Exception as e:
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500

# Run the Flask app if this file is run directly
if __name__ == "__main__":
    app.run(debug=True)
