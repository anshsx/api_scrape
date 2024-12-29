# index.py
from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

app = Flask(__name__)

# Function to scrape Google search results
def get_google_results(query):
    google_url = f"https://www.google.com/search?q={query}&num=10"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    response = requests.get(google_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    results = []
    
    for g in soup.find_all('div', class_='tF2Cxc'):
        title_tag = g.find('h3')
        link_tag = g.find('a')
        
        if title_tag and link_tag:
            title = title_tag.text
            link = link_tag['href']
            
            snippet_tag = g.find('div', class_='IsZvec')
            snippet = snippet_tag.text if snippet_tag else 'No snippet'

            favicon_url = get_favicon_url(link)
            
            results.append({'title': title, 'url': link, 'snippet': snippet, 'favicon': favicon_url})

    return results

# Function to scrape Bing search results
def get_bing_results(query):
    bing_url = f"https://www.bing.com/search?q={query}&count=10"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    response = requests.get(bing_url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        results = []
        for b in soup.find_all('li', class_='b_algo'):
            title_tag = b.find('h2')
            if title_tag:
                title = title_tag.text
                link = b.find('a')['href']
                snippet_tag = b.find('p')
                snippet = snippet_tag.text if snippet_tag else 'No snippet'
                favicon_url = get_favicon_url(link)

                results.append({'title': title, 'url': link, 'snippet': snippet, 'favicon': favicon_url})

        return results
    else:
        return []

# Function to extract favicon from the URL
def get_favicon_url(url):
    domain = urlparse(url).netloc
    return f"https://{domain}/favicon.ico"

# Function to remove duplicate results based on URL
def deduplicate(results):
    unique_results = {}

    for result in results:
        domain = urlparse(result['url']).netloc
        path = urlparse(result['url']).path
        url_key = f"{domain}{path}"

        if url_key not in unique_results:
            unique_results[url_key] = {'title': result['title'], 'url': result['url'], 'snippets': [result['snippet']], 'favicon': result['favicon']}
        else:
            unique_results[url_key]['snippets'].append(result['snippet'])

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

# Function that calls the appropriate search engines based on the ratio ('g', 'b', or 'm')
def scrape(query, ratio):
    results = []

    if ratio == 'g' or ratio == 'm':
        google_results = get_google_results(query)
        results.extend(google_results)

    if ratio == 'b' or ratio == 'm':
        bing_results = get_bing_results(query)
        results.extend(bing_results)

    if ratio == 'm':
        results = deduplicate(results)

    return results

# This part ensures the app doesn't start running if this file is imported in another file (i.e., in `app.py`)
if __name__ == "__main__":
    app.run(debug=True)
