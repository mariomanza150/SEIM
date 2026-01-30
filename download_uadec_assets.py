#!/usr/bin/env python
"""Download UAdeC logos and assets from their official website."""

import os
import requests
from pathlib import Path
from urllib.parse import urljoin, urlparse
import urllib3

# Disable SSL warnings for this script
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# UAdeC official website
UADEC_URL = "https://www.uadec.mx/"

# Common asset URLs (we'll try these)
POTENTIAL_ASSETS = [
    "/images/logo.png",
    "/images/logo-uadec.png",
    "/img/logo.png",
    "/img/logo-uadec.png",
    "/assets/img/logo.png",
    "/assets/images/logo.png",
    "/static/img/logo.png",
    "/static/images/logo.png",
]

# Output directory
STATIC_DIR = Path("staticfiles/images")
STATIC_DIR.mkdir(parents=True, exist_ok=True)

def download_asset(url, filename):
    """Download a single asset."""
    try:
        print(f"Trying to download: {url}")
        response = requests.get(url, timeout=10, allow_redirects=True, verify=False)
        
        if response.status_code == 200:
            output_path = STATIC_DIR / filename
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print(f"✓ Downloaded: {filename} ({len(response.content)} bytes)")
            return True
        else:
            print(f"✗ Failed: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def scrape_page_for_images():
    """Scrape the UAdeC homepage to find logo images."""
    try:
        print(f"\nFetching homepage: {UADEC_URL}")
        response = requests.get(UADEC_URL, timeout=10, verify=False)
        
        if response.status_code == 200:
            import re
            # Look for common logo patterns in the HTML
            patterns = [
                r'<img[^>]+src=["\']([^"\']*logo[^"\']*)["\']',
                r'<img[^>]+src=["\']([^"\']*uadec[^"\']*)["\']',
                r'background-image:\s*url\(["\']([^"\']*logo[^"\']*)["\']',
            ]
            
            found_urls = set()
            for pattern in patterns:
                matches = re.findall(pattern, response.text, re.IGNORECASE)
                found_urls.update(matches)
            
            print(f"Found {len(found_urls)} potential image URLs")
            
            # Download found images
            for i, img_url in enumerate(found_urls):
                if not img_url.startswith('http'):
                    img_url = urljoin(UADEC_URL, img_url)
                
                filename = f"uadec-asset-{i+1}" + Path(urlparse(img_url).path).suffix
                download_asset(img_url, filename)
        
    except Exception as e:
        print(f"Error scraping page: {e}")

def main():
    """Main download function."""
    print("=" * 60)
    print("UAdeC Asset Downloader")
    print("=" * 60)
    
    # Try common asset paths first
    print("\n1. Trying common logo paths...")
    for asset_path in POTENTIAL_ASSETS:
        url = urljoin(UADEC_URL, asset_path)
        if download_asset(url, "uadec-logo.png"):
            break
    
    # Scrape homepage for images
    print("\n2. Scraping homepage for images...")
    scrape_page_for_images()
    
    print("\n" + "=" * 60)
    print(f"Assets saved to: {STATIC_DIR.absolute()}")
    print("=" * 60)

if __name__ == "__main__":
    main()

