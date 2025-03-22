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

## Usage

1. Type `az` followed by your search query
2. Press Enter to open the selected product in your browser

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
