# Alfred Amazon Search

A powerful Alfred workflow for searching Amazon products with smart filtering and sorting capabilities.

## Features

- 🔍 Fast Amazon product search
- 💰 Price and coupon display
  - Regular prices shown with 💰
  - Coupon discounts shown with 🏷️
  - Supports both percentage and dollar amount discounts
  - Automatically calculates final price after discounts
- ⭐ Rating and review count display
- 📦 Delivery time information
- 🖼️ Product images in results
- 🔄 Smart caching for faster results
- 📊 Sort results by rating or price
- 🚚 Filter results by delivery time
- 🔗 Amazon affiliate links support

## Usage

1. Type `az` followed by your search query
2. Optional parameters:
   - `srt:r` - Sort by rating (highest first)
     - Calculates score as rating × number of reviews
     - Example: 4.5 stars with 1000 reviews = 4500 points
   - `srt:ra` - Sort by rating (lowest first)
   - `srt:p` - Sort by price (lowest first)
   - `srt:pd` - Sort by price (highest first)
   - `dl:0` - Show only items available for delivery today
   - `dl:1` - Show items available for delivery today or tomorrow
   - `dl:2` - Show items available for delivery in 2 days or less
   - etc.

### Examples

- `az laptop` - Basic search
- `az headphones srt:r` - Search headphones, sorted by rating
- `az monitor srt:p` - Search monitors, sorted by price (lowest first)
- `az keyboard dl:1` - Search keyboards available for delivery tomorrow or less
- `az mouse dl:0 srt:p` - Search mice available for delivery today, sorted by price
- `az tablet srt:r dl:2` - Search tablets available in 2 days or less, sorted by rating

### Smart Caching

The workflow uses intelligent caching to improve performance:
- Search results are cached for 30 minutes
- The cache is based on the base search term (without modifiers)
- Modifiers (`srt:` and `dl:`) are applied to cached results
- This means changing sort or delivery filters is instant
- Product images are cached for 1 week

## Installation

1. Download the [latest release](https://github.com/schwark/alfred-amazon/releases/latest)
2. Double-click the workflow file to install in Alfred
3. The workflow will be ready to use

## Notes

- Results are cached for 30 minutes to improve performance
- Product images are cached for 1 week
- Delivery times are based on Amazon's estimates
- Prices include applicable discounts and coupons
- Affiliate links are used to support development

## License

MIT License - see LICENSE file for details
