#!/usr/bin/env python3
# encoding: utf-8

"""Amazon Search

Usage:
    amazon.py <query>
"""

import sys
import os
from workflow import Workflow, ICON_WEB, web
import amazon

CACHE_AGE = 1800  # 30 minutes

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
            # Create cache key from query
            cache_key = f'search_{query}'
            
            # Try to get results from cache
            # results = wf.cached_data(cache_key, lambda: amazon.get_search_results(wf, query), max_age=CACHE_AGE)
            results = amazon.get_search_results(wf, query)
            
            if not results:
                wf.add_item('No results found',
                           'Try a different search term',
                           icon=ICON_WEB)
            
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