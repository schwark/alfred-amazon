# Alfred Amazon Search

A simple Alfred workflow to search Amazon products directly from Alfred.

## Features

- 🔍 Quick Amazon product search
- 🏷️ Shows product prices with support for:
  - Regular prices
  - Coupon discounts (both percentage and absolute dollar amounts)
  - Effective price calculation when coupons are applied
- 📢 Indicates sponsored items
- ⭐ Displays product ratings and review counts
- 📦 Shows delivery information
- 🖼️ Product images as icons
- 🔗 Amazon affiliate links (using tag: dillz-20)
- 🔄 Sort results by rating or price

## Usage

1. Type `az` followed by your search query
2. Optionally add `srt:` followed by:
   - `r` to sort by rating (default: descending by rating × reviews)
   - `p` to sort by price (default: ascending)
   - Add `a` after `r` or `p` for ascending order
   - Add `d` after `r` or `p` for descending order
3. Press Enter to open the selected product in your browser

Examples:
- `az macbook srt:r` - Sort by rating (descending)
- `az macbook srt:ra` - Sort by rating (ascending)
- `az macbook srt:p` - Sort by price (ascending)
- `az macbook srt:pd` - Sort by price (descending)

## Example Results

Each result shows:
- Product title (intelligently shortened)
- Price (with 💰 emoji)
  - If a coupon is available, shows the effective price with 🏷️ emoji
- Rating and review count (with ⭐ emoji)
- Delivery information (with 📦 emoji)
- Sponsored status (with 📢 emoji) if applicable

## Requirements

- Alfred 4 or later
- Python 3.9 or later
- BeautifulSoup4

## Installation

1. Download the latest release
2. Double-click the workflow file to install in Alfred
3. The workflow will be ready to use

## Development

The workflow consists of two main Python files:
- `filter.py`: Main workflow script that handles user input and displays results
- `amazon.py`: Amazon-specific functionality for searching and parsing results

## License

MIT License - feel free to use and modify as needed.
