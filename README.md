# Oda Scraper

A scraper for the [Oda](https://oda.com) website that transforms product and category pages into JSON data consumable by other systems.

## Overview

Oda organises its catalogue into categories and products. This tool lets you list all available categories, browse products within a category, and read individual product details — with disk-based caching to avoid redundant requests.

## Technologies

| Library | Purpose |
|---|---|
| [uv](https://github.com/astral-sh/uv) | Python dependency manager (automatic venv support) |
| `requests` | HTTP calls |
| `BeautifulSoup` | HTML parsing and DOM traversal |

## Usage

```bash
# List all categories
python cli.py list

# List products in a category
python cli.py categories products <category-id>

# Read a single product
python cli.py products read <product-path>

```

## Features

### Performance
- Pages are cached to disk after the first visit, so repeat calls never hit the network.
- HTTP responses and file I/O use streams to keep memory usage low.

### Reusability
- The `Product` and `Category` types are independent of Oda and could be reused for other sites.
- `read_a_product`, `read_products`, `get_category_products`, and `get_categories` could form a common interface implemented per site.
- `cli.py` consumes `main.py` as a module, keeping concerns separate.

### Good citizenship
- The caching mechanism ensures each page is visited at most once unless the cache is cleared.
- The scraper does not crawl automatically; it exposes functions that a caller controls. Automated crawling would require an explicit pacing strategy.

## Configuration
- Room for improvement currently logic for traversing the DOME is hard-coded.

## Visualization

All commands output JSON, making it straightforward to pipe results into a dashboard or further processing tools.
