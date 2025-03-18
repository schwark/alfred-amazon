#!/usr/bin/env python3
# encoding: utf-8

from workflow import web
from bs4 import BeautifulSoup
import sys
from urllib.parse import quote

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0'
}

def test_search(query):
    url = f"https://www.amazon.com/s?k={quote(query)}"
    r = web.get(url, headers=HEADERS)
    html = r.text
    
    # Save HTML for analysis
    with open('sample.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    soup = BeautifulSoup(html, 'html.parser')
    products = soup.find_all('div', {'data-component-type': 's-search-result'})
    print(f"Found {len(products)} products")
    
    for product in products[:3]:  # Look at first 3 products
        print("\nAnalyzing product structure:")
        
        # Method 1: h2 in a-section
        title_section = product.find('div', {'class': 'a-section'})
        if title_section:
            h2 = title_section.find('h2')
            if h2:
                link = h2.find('a')
                if link:
                    print("Method 1 found:")
                    print(f"Title: {link.get_text().strip()}")
                    print(f"URL: {link.get('href')}")
        
        # Method 2: span with a-text-normal
        title_span = product.find('span', {'class': 'a-text-normal'})
        if title_span:
            parent_link = title_span.find_parent('a')
            if parent_link:
                print("Method 2 found:")
                print(f"Title: {title_span.get_text().strip()}")
                print(f"URL: {parent_link.get('href')}")
        
        # Method 3: Direct product link
        product_link = product.find('a', {'class': 'a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal'})
        if product_link:
            print("Method 3 found:")
            print(f"Title: {product_link.get_text().strip()}")
            print(f"URL: {product_link.get('href')}")
        
        # Print raw HTML structure
        print("\nRaw HTML structure:")
        print(product.prettify()[:500] + "...")  # First 500 chars

if __name__ == '__main__':
    query = sys.argv[1] if len(sys.argv) > 1 else "samsung tv"
    test_search(query) 