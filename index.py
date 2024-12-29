from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

app = Flask(__name__)

def get_google_results(query):
    google_url = f"https://www.google.com/search?q={query}&num=10"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    response = requests.get(google_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    results = []
    for g in soup.find_all('div', class_='tF2Cxc'):
        title = g.find('h3').text
        link = g.find('a')['href']
        snippet = g.find('div', class_='IsZvec').text if g.find('div', class_='IsZvec') else 'No snippet'
        favicon_url = get_favicon_url(link)
        results.append({'title': title, 'url': link, 'snippet': snippet, 'favicon': favicon_url})
    
    return results

def get_bing_results(query):
    bing_url = f"https://www.bing.com/search?q={query}&count=10"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    response = requests.get(bing_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    results = []
    for b in soup.find_all('li', class_='b_algo'):
        title = b.find('h2').text
        link = b.find('a')['href']
        snippet = b.find('p').text if b.find('p') else 'No snippet'
        favicon_url = get_favicon_url(link)
        results.append({'title': title, 'url': link, 'snippet': snippet, 'favicon': favicon_url})
    
    return results

def get_favicon_url(url):
    # Extract domain from the URL and construct the favicon URL
    domain = urlparse(url).netloc
    return f"https://{domain}/favicon.ico"

def deduplicate(results):
    # A dictionary to store URLs and their snippets
    unique_results = {}
    
    for result in results:
        domain = urlparse(result['url']).netloc
        path = urlparse(result['url']).path
        url_key = f"{domain}{path}"
        
        if url_key not in unique_results:
            unique_results[url_key] = {'title': result['title'], 'url': result['url'], 'snippets': [result['snippet']], 'favicon': result['favicon']}
        else:
            # Combine snippets if the URL already exists
            unique_results[url_key]['snippets'].append(result['snippet'])
    
    # Now combine snippets and prepare final results
    deduplicated_results = []
    for url_key, value in unique_results.items():
        combined_snippet = " ".join(value['snippets'])
        deduplicated_results.append({
            'title': value['title'],
            'url': value['url'],
            'snippet': combined_snippet,
            'favicon': value['favicon']
        })
    
    return deduplicated_results

@app.route('/scrape', methods=['POST'])
def scrape():
    # Get the JSON data from the POST request
    data = request.get_json()
    
    if not data or 'query' not in data or 'ratio' not in data:
        return jsonify({"error": "Missing 'query' or 'ratio' in the request data."}), 400
    
    query = data['query']
    ratio = data['ratio'].lower()

    if ratio not in ['g', 'b', 'm']:
        return jsonify({"error": "Invalid ratio. Use 'g', 'b', or 'm'."}), 400
    
    results = []
    
    if ratio == 'g' or ratio == 'm':
        google_results = get_google_results(query)
        results.extend(google_results)
    
    if ratio == 'b' or ratio == 'm':
        bing_results = get_bing_results(query)
        results.extend(bing_results)
    
    # Deduplicate if multiple results are fetched
    if ratio == 'm':
        results = deduplicate(results)
    
    # Return the results as a JSON response
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)
