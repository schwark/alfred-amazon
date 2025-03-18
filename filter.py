#!/usr/bin/env python3
# encoding: utf-8

import sys
import argparse
import os
import re
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
    parser = argparse.ArgumentParser()
    parser.add_argument('query', nargs='?', default=None)
    args = parser.parse_args(wf.args)

    if not args.query:
        wf.add_item('Start typing to search Amazon...',
                   'Your search will be processed with associate tag',
                   icon='icon.png')
    else:
        try:
            # Create cache key from query
            cache_key = f'search_{args.query}'
            
            # Try to get results from cache
            results = wf.cached_data(cache_key, lambda: amazon.get_search_results(wf, args.query), max_age=CACHE_AGE)
            
            if not results:
                wf.add_item('No results found',
                           'Try a different search term',
                           icon=ICON_WEB)
            
            for item in results:
                # Shorten the title intelligently
                shortened_title = amazon.shorten_title(item['title'])
                
                subtitle_parts = []
                
                # Price with 💰 emoji
                if item.get('price'):
                    subtitle_parts.append(f"💰 {item['price']}")
                if item.get('coupon'):
                    subtitle_parts.append(f"🏷️ {item['coupon']}")
                
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