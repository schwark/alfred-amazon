#!/usr/bin/env python3
# encoding: utf-8

import re
from bs4 import BeautifulSoup
from urllib.parse import quote
from datetime import datetime
from workflow import web, Workflow

# Initialize workflow and logger
wf = Workflow()
log = wf.logger

# Amazon-specific constants
AMAZON_ASSOCIATE_TAG = 'dillz-20'
AMAZON_BASE_URL = 'https://www.amazon.com'
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15'
HEADERS = {
    'User-Agent': USER_AGENT,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0'
}
MAX_RESULTS = 30

def parse_delivery_date(date_str):
    """Convert delivery date to number of days from today."""
    try:
        # Parse the date string (e.g., "Tue, Mar 18")
        # First clean up the date string to ensure consistent format
        date_parts = date_str.replace(',', '').split()
        if len(date_parts) != 3:
            return date_str
            
        # Convert month abbreviation to number
        month_map = {
            'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
            'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
        }
        
        month = month_map.get(date_parts[1])
        if not month:
            return date_str
            
        day = int(date_parts[2])
        
        # Create date object
        current_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        delivery_date = datetime(current_date.year, month, day).replace(hour=0, minute=0, second=0, microsecond=0)
        
        # If the date is in the past for this year, it must be next year
        if delivery_date < current_date:
            delivery_date = datetime(current_date.year + 1, month, day)
        
        # Calculate days difference
        days_until = (delivery_date - current_date).days
        
        if days_until == 0:
            return "Delivery today"
        elif days_until == 1:
            return "Delivery tomorrow"
        else:
            return f"Delivery in {days_until} days"
            
    except Exception as e:
        return date_str  # Return original string if parsing fails

def normalize_amazon_url(url, asin=None):
    """Normalize Amazon URL to use dp format with associate tag."""
    # If no ASIN provided, try to extract it from the URL
    if not asin:
        # Look for ASIN in dp format
        asin_match = re.search(r'/dp/([A-Z0-9]{10})(?:/|\?|$)', url)
        if asin_match:
            asin = asin_match.group(1)
    
    if asin:
        # If we have an ASIN (either provided or extracted), use the dp format
        return f"https://www.amazon.com/dp/{asin}?tag={AMAZON_ASSOCIATE_TAG}"
    else:
        # Handle regular URLs
        if url.startswith('/'):
            url = f"https://www.amazon.com{url}"
        # Add associate tag if not present
        if '?' in url:
            url += f'&tag={AMAZON_ASSOCIATE_TAG}'
        else:
            url += f'?tag={AMAZON_ASSOCIATE_TAG}'
        return url

def shorten_title(title):
    """Intelligently shorten product title while retaining key information."""
    # Remove common filler words and phrases
    fillers = [
        'with', 'for', 'and', 'or', 'the', 'in', 'on', 'at', 'by', 'of',
        'Premium', 'New', 'Hot', 'Best', 'Latest', 'High Quality',
        '(Updated)', '(New)', '(Latest)', '(Official)', '(Original)',
        '- Perfect Gift', 'Perfect Gift',
        '100%', 'High-Quality', 'Professional'
    ]
    
    # Keep track of important parts
    parts = {
        'brand': '',
        'core': '',
        'color': '',
        'quantity': ''
    }
    
    # Extract quantity if present (e.g., "Pack of 2", "2-Pack", "Set of 3")
    quantity_patterns = [
        r'(?:pack of|set of)\s+(\d+)',
        r'(\d+)(?:-|\s+)?pack',
        r'(\d+)(?:-|\s+)?piece',
        r'(\d+)(?:-|\s+)?count'
    ]
    
    for pattern in quantity_patterns:
        match = re.search(pattern, title.lower())
        if match:
            parts['quantity'] = f"({match.group(1)}pk)"
            title = re.sub(pattern, '', title)
            break
    
    # Extract color if present
    color_pattern = r'(?:in|,)?\s*(black|white|red|blue|green|yellow|purple|pink|brown|grey|gray|gold|silver|rose gold|navy|beige|transparent|clear)(?:\s+color)?'
    color_match = re.search(color_pattern, title.lower())
    if color_match:
        parts['color'] = color_match.group(1).title()
        title = re.sub(color_pattern, '', title)
    
    # Split remaining title into words
    words = title.split()
    
    # First word is often the brand
    if words:
        parts['brand'] = words[0]
        words = words[1:]
    
    # Clean up remaining words
    cleaned_words = []
    for word in words:
        # Skip filler words
        if word.lower() in [f.lower() for f in fillers]:
            continue
        # Skip words in parentheses
        if word.startswith('(') and word.endswith(')'):
            continue
        cleaned_words.append(word)
    
    # Join remaining words for core description
    parts['core'] = ' '.join(cleaned_words)
    
    # Construct final title
    final_parts = []
    if parts['brand']:
        final_parts.append(parts['brand'])
    if parts['core']:
        # Limit core description to first 5 words
        core_words = parts['core'].split()[:5]
        final_parts.append(' '.join(core_words))
    if parts['color']:
        final_parts.append(parts['color'])
    if parts['quantity']:
        final_parts.append(parts['quantity'])
    
    return ' '.join(final_parts)

def get_search_results(wf, query):
    """Get search results from Amazon."""
    # Build search URL
    search_url = f"{AMAZON_BASE_URL}/s?k={quote(query)}"
    
    # Get search results
    try:
        # Use workflow's web module to fetch results
        r = web.get(search_url, headers=HEADERS)
        r.raise_for_status()
        html = r.text
        
        # For debugging: save the HTML to a file
        with open('sample.html', 'w', encoding='utf-8') as f:
            f.write(html)
        
        # Parse HTML
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find all product containers
        products = soup.find_all('div', {'data-component-type': 's-search-result'})
        
        results = []
        for product in products[:MAX_RESULTS]:
            try:
                # Get ASIN from data-asin attribute
                asin = product.get('data-asin')
                if not asin:
                    continue
                
                # Find title and URL using data-cy=title-recipe
                title = None
                url = None
                
                # Look for title-recipe div
                title_recipe = product.find('div', attrs={'data-cy': 'title-recipe'})
                if title_recipe:
                    # Get all text from title-recipe
                    title = ' '.join(title_recipe.stripped_strings)
                    # Get URL from the link
                    link = title_recipe.find('a', {'class': 'a-link-normal'})
                    if link:
                        url = link.get('href')
                
                if not title or not url:
                    continue
                
                # Clean up title
                if title:
                    # Remove extra whitespace and newlines
                    title = ' '.join(title.split())
                    # Check if item is sponsored (with or without brackets)
                    is_sponsored = bool(re.search(r'(?:\[)?Sponsored(?:\])?', title))
                    # Remove sponsored tag if present (with or without brackets)
                    title = re.sub(r'\s*(?:\[)?Sponsored(?:\])?\s*', '', title)
                    # Remove ad relevance text
                    title = re.sub(r"You\u2019re seeing this ad based on the product\u2019s relevance to your search query.", '', title)
                    # Remove leave ad feedback text
                    title = re.sub(r'Leave ad feedback', '', title)
                    # Remove any other common tags
                    title = re.sub(r'\s*\[(New|Limited Time|Sale|Deal|Prime)\]\s*', '', title)
                
                # Clean up title and URL
                title = title.strip()
                url = normalize_amazon_url(url, asin)
                
                # Extract price
                price_elem = product.find('span', {'class': 'a-price'})
                if price_elem:
                    price_span = price_elem.find('span', {'class': 'a-offscreen'})
                    price = price_span.get_text().strip() if price_span else None
                else:
                    price = None
                
                # Skip items with no price or zero price
                if not price:
                    continue
                    
                # Try to convert price to float for comparison (remove $ and ,)
                try:
                    price_float = float(price.replace('$', '').replace(',', ''))
                    if price_float <= 0:
                        continue
                except ValueError:
                    continue
                
                # Extract coupon if present
                coupon = None
                coupon_elem = product.find('span', {'class': 's-coupon-unclipped'})
                if coupon_elem:
                    coupon_text = coupon_elem.get_text().strip()
                    # Clean up coupon text
                    coupon_text = re.sub(r'\s+', ' ', coupon_text)  # Normalize whitespace
                    coupon_text = re.sub(r'^Save\s+', '', coupon_text)  # Remove "Save" prefix
                    coupon_text = re.sub(r'^Get\s+', '', coupon_text)  # Remove "Get" prefix
                    coupon_text = coupon_text.strip()
                    if coupon_text:
                        coupon = coupon_text
                
                # Extract delivery info
                delivery = None
                delivery_recipe = product.find('div', attrs={'data-cy': 'delivery-recipe'})
                if delivery_recipe:
                    delivery_text = ' '.join(delivery_recipe.stripped_strings)
                    # Try to find fastest delivery date
                    date_match = re.search(r'(?:fastest|FREE) delivery ([A-Za-z]+,?\s+[A-Za-z]+\s+\d+)', delivery_text)
                    if date_match:
                        delivery_date = date_match.group(1)
                        delivery = parse_delivery_date(delivery_date)
                
                # Extract rating
                rating_elem = product.find('span', {'class': 'a-icon-alt'})
                rating = rating_elem.get_text().strip() if rating_elem else None
                
                # Extract review count - try multiple methods
                review_count = None
                # Method 1: Look for review count in aria-label
                review_link = product.find('a', {'href': lambda x: x and 'customerReviews' in x})
                if review_link:
                    review_span = review_link.find('span', {'aria-label': True})
                    if review_span:
                        count_match = re.search(r'([\d,]+)\s+ratings?', review_span.get('aria-label', ''))
                        if count_match:
                            review_count = count_match.group(1)
                
                # Method 2: Look for review count in specific spans
                if not review_count:
                    review_spans = product.find_all('span', {'class': ['a-size-base', 's-underline-text']})
                    for span in review_spans:
                        text = span.get_text().strip()
                        # Match numbers with optional commas
                        count_match = re.match(r'^([\d,]+)$', text)
                        if count_match:
                            review_count = count_match.group(1)
                            break
                
                # Method 3: Look for review count in parentheses
                if not review_count:
                    for span in product.find_all('span'):
                        text = span.get_text().strip()
                        count_match = re.search(r'\(([\d,]+)\s*\)', text)
                        if count_match and span.find_parent('a', {'href': lambda x: x and 'customerReviews' in x}):
                            review_count = count_match.group(1)
                            break
                
                # Extract image URL
                image_elem = product.find('img', {'class': 's-image'})
                image_url = image_elem['src'] if image_elem else None
                
                # Create result dictionary
                result = {
                    'title': title,
                    'url': url,
                    'price': price,
                    'coupon': coupon,
                    'delivery': delivery,
                    'stars': rating,
                    'reviews': review_count,
                    'image_url': image_url,
                    'asin': asin,
                    'sponsored': is_sponsored
                }
                
                # Only add items that have at least a title and URL
                if result['title'] and result['url']:
                    results.append(result)
                
            except Exception:
                continue
        
        return results
        
    except Exception:
        return [] 