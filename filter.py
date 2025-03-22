#!/usr/bin/env python3
# encoding: utf-8

"""Amazon Search

Usage:
    amazon.py <query> [srt:<sort>]
"""

import sys
import os
from workflow import Workflow, ICON_WEB, web
import amazon

CACHE_AGE = 1800  # 30 minutes

def parse_sort_param(query):
    """Parse sort parameter from query string."""
    if 'srt:' not in query:
        return query, None, None
        
    # Split query and sort parameter
    parts = query.split('srt:', 1)
    search_query = parts[0].strip()
    sort_param = parts[1].strip().lower()
    
    # Parse sort parameter
    if not sort_param:
        return search_query, None, None
        
    # Get first character (r or p)
    key = sort_param[0]
    if key not in ('r', 'p'):
        return search_query, None, None
        
    # Get direction if present
    direction = sort_param[1] if len(sort_param) > 1 else None
    if direction and direction not in ('a', 'd'):
        direction = None
        
    # Set defaults if direction not specified
    if not direction:
        direction = 'd' if key == 'r' else 'a'
        
    return search_query, ('rating' if key == 'r' else 'price'), (direction == 'd')

def download_image(url, asin):
    """Download an image from URL and save it to a temporary file using ASIN as filename."""
    try:
        # Download image
        r = web.get(url)
        r.raise_for_status()
        
        # Create a temporary file with .png extension using ASIN
        img_path = os.path.join(os.getenv('TMPDIR', '/tmp'), f"{asin}.png")
        
        # Save the image
        with open(img_path, 'wb') as f:
            f.write(r.content)
            
        return img_path
    except Exception as e:
        log.error(f"Error downloading image {url}: {str(e)}")
        return None

def main(wf):
    # Get query from user
    query = wf.args[0] if wf.args else None
    
    if not query:
        wf.add_item('Start typing to search Amazon...',
                   'Your search will be processed with associate tag',
                   icon='icon.png')
    else:
        try:
            # Parse query and sort parameter
            search_query, sort_key, sort_reverse = parse_sort_param(query)
            
            # Create cache key from query
            cache_key = f'search_{search_query}'
            
            # Try to get results from cache
            results = wf.cached_data(cache_key, lambda: amazon.get_search_results(wf, search_query), max_age=CACHE_AGE)
            
            if not results:
                wf.add_item('No results found',
                           'Try a different search term',
                           icon=ICON_WEB)
            
            # Sort results if sort parameter was provided
            if sort_key:
                if sort_key == 'rating':
                    # Calculate rating score (stars * number of reviews)
                    for item in results:
                        try:
                            stars = float(item.get('stars', '0').split()[0])
                            reviews = int(item.get('reviews', '0').replace(',', ''))
                            item['rating_score'] = stars * reviews
                        except (ValueError, IndexError):
                            item['rating_score'] = 0
                    results.sort(key=lambda x: x.get('rating_score', 0), reverse=sort_reverse)
                else:  # price
                    results.sort(key=lambda x: float(x.get('price', '0').replace('$', '').replace(',', '')), reverse=sort_reverse)
            
            for item in results:
                # Shorten the title intelligently
                shortened_title = amazon.shorten_title(item['title'])
                
                subtitle_parts = []
                
                # Add sponsored status if applicable
                if item.get('sponsored'):
                    subtitle_parts.append("📢 Sponsored")
                
                # Calculate effective price if coupon is available
                effective_price = None
                if item.get('price') and item.get('coupon'):
                    try:
                        price = float(item['price'].replace('$', '').replace(',', ''))
                        coupon = item['coupon'].strip()
                        log.debug(f"Processing coupon: '{coupon}' for price: ${price}")
                        
                        # Clean up coupon text
                        coupon = coupon.lower()
                        coupon = coupon.replace('with coupon', '').strip()
                        coupon = coupon.replace('off', '').strip()
                        coupon = coupon.replace('discount', '').strip()
                        
                        # Handle percentage discount
                        if '%' in coupon:
                            percent = float(coupon.replace('%', '').strip())
                            effective_price = price * (1 - percent/100)
                            log.debug(f"Percentage discount: {percent}% -> ${effective_price}")
                        # Handle absolute dollar discount
                        elif '$' in coupon:
                            discount = float(coupon.replace('$', '').strip())
                            effective_price = price - discount
                            log.debug(f"Dollar discount: ${discount} -> ${effective_price}")
                        
                        if effective_price and effective_price > 0:
                            effective_price = f"${effective_price:.2f}"
                            log.debug(f"Final effective price: {effective_price}")
                    except ValueError as e:
                        log.error(f"Error calculating effective price: {e}")
                        log.error(f"Price: {item['price']}, Coupon: {item['coupon']}")
                        effective_price = None
                
                # Price with 💰 emoji (show effective price if available)
                if effective_price:
                    subtitle_parts.append(f"🏷️ {effective_price}")
                elif item.get('price'):
                    subtitle_parts.append(f"💰 {item['price']}")
                
                # Reviews with ⭐ emoji
                if item.get('stars'):
                    review_text = item['stars'].split()[0]  # Just get the number
                    if item.get('reviews'):
                        review_text += f" ⭐ ({item['reviews']})"
                    else:
                        review_text += " ⭐"
                    subtitle_parts.append(review_text)
                
                # Delivery with 📦 emoji
                if item.get('delivery'):
                    subtitle_parts.append(f"📦 {item['delivery']}")
                
                subtitle = '   '.join(filter(None, subtitle_parts)) if subtitle_parts else 'No additional information available'
                
                # Get icon from product image
                icon = ICON_WEB
                if item.get('image_url') and item.get('asin'):
                    # Cache the image using ASIN as the key
                    icon = wf.cached_data(
                        f"img_{item['asin']}",  # Use ASIN as unique key
                        lambda: download_image(item['image_url'], item['asin']),
                        max_age=604800  # Cache for 1 week
                    )
                    # If image download/cache failed, use default icon
                    if not icon:
                        icon = ICON_WEB
                
                wf.add_item(
                    title=shortened_title,
                    subtitle=subtitle,
                    arg=item['url'],
                    valid=True,
                    icon=icon
                )
        except Exception as e:
            wf.add_item('Error fetching results',
                       str(e),
                       icon=ICON_WEB)

    wf.send_feedback()
    return 0

if __name__ == '__main__':
    wf = Workflow(update_settings={
        'github_slug': 'schwark/alfred-amazon'
    })
    log = wf.logger
    sys.exit(wf.run(main)) 