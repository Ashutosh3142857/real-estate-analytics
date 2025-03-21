"""
Web scraping module for gathering real estate market information and property details.
This module uses Trafilatura for content extraction, which provides cleaner text from HTML pages.

This module provides comprehensive web scraping capabilities for:
1. Market trends and news from global real estate sources
2. Property details from listing sites 
3. Economic indicators affecting real estate markets
4. International market data and insights
5. Rental market analysis
"""

import trafilatura
import logging
import re
import json
import time
import random
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Cache directory for storing scraped content to minimize repeated requests
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cache', 'web_scraping')
os.makedirs(CACHE_DIR, exist_ok=True)

def get_cache_path(url: str) -> str:
    """
    Get the cache file path for a URL.
    
    Args:
        url (str): The URL to get a cache path for
        
    Returns:
        str: The path to the cache file
    """
    # Create a safe filename from the URL
    import hashlib
    filename = hashlib.md5(url.encode()).hexdigest() + '.txt'
    return os.path.join(CACHE_DIR, filename)

def check_cache(url: str, max_age_hours: int = 24) -> Optional[str]:
    """
    Check if cached content exists and is recent enough.
    
    Args:
        url (str): The URL to check for in cache
        max_age_hours (int): Maximum age of cache in hours
        
    Returns:
        Optional[str]: The cached content if available and fresh, None otherwise
    """
    cache_path = get_cache_path(url)
    
    if not os.path.exists(cache_path):
        return None
    
    # Check if the cache is still fresh
    file_time = os.path.getmtime(cache_path)
    file_age = datetime.now().timestamp() - file_time
    max_age = max_age_hours * 3600  # Convert hours to seconds
    
    if file_age > max_age:
        logger.info(f"Cache for {url} is older than {max_age_hours} hours, will re-download")
        return None
    
    # Read the cached content
    try:
        with open(cache_path, 'r', encoding='utf-8') as f:
            content = f.read()
        logger.info(f"Retrieved content from cache for {url}")
        return content
    except Exception as e:
        logger.error(f"Error reading cache for {url}: {str(e)}")
        return None

def save_to_cache(url: str, content: str) -> bool:
    """
    Save content to the cache.
    
    Args:
        url (str): The URL the content was fetched from
        content (str): The content to cache
        
    Returns:
        bool: True if saved successfully, False otherwise
    """
    if not content:
        return False
    
    cache_path = get_cache_path(url)
    
    try:
        with open(cache_path, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"Saved content to cache for {url}")
        return True
    except Exception as e:
        logger.error(f"Error saving to cache for {url}: {str(e)}")
        return False

def get_website_text_content(url: str, use_cache: bool = True, max_cache_age_hours: int = 24) -> str:
    """
    Extract the main text content from a website.
    
    Args:
        url (str): The URL of the website to scrape
        use_cache (bool): Whether to use cached content if available
        max_cache_age_hours (int): Maximum age of cache in hours
        
    Returns:
        str: The main text content of the website
    """
    # Check cache first if enabled
    if use_cache:
        cached_content = check_cache(url, max_cache_age_hours)
        if cached_content:
            return cached_content
    
    try:
        # Add a small delay to be respectful to servers
        time.sleep(random.uniform(1.0, 3.0))
        
        # Download the webpage
        downloaded = trafilatura.fetch_url(url)
        
        if not downloaded:
            logger.error(f"Failed to download content from {url}")
            return ""
        
        # Extract the main content
        text = trafilatura.extract(downloaded)
        
        if not text:
            logger.error(f"Failed to extract content from {url}")
            return ""
        
        # Save to cache if content was successfully retrieved
        if use_cache:
            save_to_cache(url, text)
        
        return text
    except Exception as e:
        logger.error(f"Error extracting content from {url}: {str(e)}")
        return ""

def get_real_estate_market_info(location: str = "") -> str:
    """
    Scrape the latest real estate market information for a specific location
    or general market trends if no location is provided.
    
    Args:
        location (str, optional): The location to get market information for
        
    Returns:
        str: The scraped market information
    """
    try:
        # Base URLs for real estate market information
        urls = [
            "https://www.nar.realtor/research-and-statistics/housing-statistics",
            "https://www.zillow.com/research/",
            "https://www.realtor.com/research/",
            "https://www.corelogic.com/intelligence/latest-housing-data/"
        ]
        
        # If location is provided, try location-specific sources
        if location:
            location_slug = location.lower().replace(" ", "-")
            urls.extend([
                f"https://www.zillow.com/research/local-market-reports/{location_slug}/",
                f"https://www.realtor.com/realestateandhomes-search/{location_slug}/overview"
            ])
        
        # Try each URL until we get content
        for url in urls:
            logger.info(f"Trying to scrape market information from {url}")
            
            content = get_website_text_content(url)
            
            if content and len(content) > 500:  # Only accept substantial content
                logger.info(f"Successfully scraped {len(content)} characters from {url}")
                return content
        
        # If no successful scrape, return empty string
        logger.warning(f"Failed to scrape market information for {location or 'general market'}")
        return ""
    except Exception as e:
        logger.error(f"Error getting real estate market info: {str(e)}")
        return ""

def scrape_property_details(property_url: str) -> Dict[str, Any]:
    """
    Scrape detailed information about a specific property from its URL.
    
    Args:
        property_url (str): URL of the property listing
        
    Returns:
        dict: Dictionary containing property details
    """
    try:
        # Get the content from the URL
        content = get_website_text_content(property_url)
        
        if not content:
            logger.warning(f"No content extracted from {property_url}")
            return {}
        
        # Extract property details using regex patterns
        details = {}
        
        # Price
        price_match = re.search(r'\$[\d,]+(?:\.\d+)?', content)
        if price_match:
            details['price'] = price_match.group(0)
        
        # Bedrooms
        bedrooms_match = re.search(r'(\d+)\s*(?:bed|bedroom)', content, re.IGNORECASE)
        if bedrooms_match:
            details['bedrooms'] = int(bedrooms_match.group(1))
        
        # Bathrooms
        bathrooms_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:bath|bathroom)', content, re.IGNORECASE)
        if bathrooms_match:
            details['bathrooms'] = float(bathrooms_match.group(1))
        
        # Square footage
        sqft_match = re.search(r'(\d+[\d,]*)\s*(?:sq\.?\s*ft\.?|square\s*feet)', content, re.IGNORECASE)
        if sqft_match:
            details['sqft'] = int(sqft_match.group(1).replace(',', ''))
        
        # Address (simplified)
        address_match = re.search(r'\d+\s+[A-Za-z\s]+(?:Avenue|Ave|Street|St|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Court|Ct|Place|Pl|Way)[,\s]+[A-Za-z\s]+,\s+[A-Z]{2}', content)
        if address_match:
            details['address'] = address_match.group(0)
        
        # Property type
        property_types = ['Single Family', 'Condo', 'Townhouse', 'Multi Family', 'Apartment', 'Land', 'Mobile Home']
        for prop_type in property_types:
            if re.search(r'\b' + re.escape(prop_type) + r'\b', content, re.IGNORECASE):
                details['property_type'] = prop_type
                break
        
        # Year built
        year_match = re.search(r'(?:Built|Year built|Construction)[\s:]+(\d{4})', content, re.IGNORECASE)
        if year_match:
            details['year_built'] = int(year_match.group(1))
        
        # Add scrape timestamp
        details['scraped_at'] = datetime.now().isoformat()
        details['source_url'] = property_url
        
        logger.info(f"Extracted {len(details)} property details from {property_url}")
        return details
    except Exception as e:
        logger.error(f"Error scraping property details: {str(e)}")
        return {}

def get_international_market_info(country: str, city: str = "") -> str:
    """
    Scrape international real estate market information for a specific country or city.
    
    Args:
        country (str): The country to get market information for
        city (str, optional): The city within the country (if specified)
        
    Returns:
        str: The scraped market information
    """
    try:
        # Format the location strings
        country_slug = country.lower().replace(" ", "-")
        city_slug = city.lower().replace(" ", "-") if city else ""
        combined_slug = f"{city_slug}-{country_slug}" if city else country_slug
        
        # Global real estate portals and sources for international markets
        urls = [
            f"https://www.globalpropertyguide.com/real-estate-house-prices/{country_slug}",
            f"https://content.knightfrank.com/research/1026/documents/en/global-house-price-index-q4-2023.pdf",
            f"https://www.numbeo.com/property-investment/in/{combined_slug}"
        ]
        
        # Country-specific sources
        if country.lower() == "india":
            urls.extend([
                "https://www.99acres.com/microsite/real-estate-market-price-trends",
                "https://housing.com/news/real-estate-market-trends/",
                f"https://www.magicbricks.com/property-for-sale/residential-real-estate?proptype=Multistorey-Apartment,Builder-Floor-Apartment,Penthouse,Studio-Apartment,Residential-House,Villa&cityName={city}"
            ])
        elif country.lower() == "uk" or country.lower() == "united kingdom":
            urls.extend([
                "https://www.rightmove.co.uk/house-price-trend/",
                "https://www.zoopla.co.uk/house-prices/",
                "https://www.ons.gov.uk/economy/inflationandpriceindices/bulletins/housepriceindex/latest"
            ])
        elif country.lower() == "australia":
            urls.extend([
                "https://www.realestate.com.au/insights/property-market-trends/",
                "https://www.domain.com.au/research/",
                "https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/residential-property-price-indexes-eight-capital-cities/latest-release"
            ])
        elif country.lower() == "canada":
            urls.extend([
                "https://www.crea.ca/housing-market-stats/",
                "https://www.realtor.ca/blog/which-way-is-canadas-housing-market-headed/26017/1367",
                "https://wowa.ca/reports/canada-housing-market"
            ])
        elif country.lower() == "germany":
            urls.extend([
                "https://www.immobilienscout24.de/immobilienbewertung/ratgeber/preisatlas.html",
                "https://www.destatis.de/EN/Themes/Economy/Prices/House-Price-Index/_node.html",
                "https://www.pwc.de/en/real-estate/emerging-trends-in-real-estate.html"
            ])
        elif country.lower() == "japan":
            urls.extend([
                "https://www.retpc.jp/data/",
                "https://resources.realestate.co.jp/market-report/",
                "https://www.stat.go.jp/english/data/jyutaku/index.html"
            ])
        
        # Try each URL until we get substantial content
        for url in urls:
            logger.info(f"Trying to scrape international market information from {url}")
            
            content = get_website_text_content(url)
            
            if content and len(content) > 500:  # Only accept substantial content
                logger.info(f"Successfully scraped {len(content)} characters from {url}")
                return content
        
        # If no successful scrape, return empty string
        logger.warning(f"Failed to scrape market information for {city + ', ' if city else ''}{country}")
        return ""
    except Exception as e:
        logger.error(f"Error getting international real estate market info: {str(e)}")
        return ""

def get_rental_market_info(location: str) -> str:
    """
    Scrape rental market information for a specific location.
    
    Args:
        location (str): The location to get rental market information for
        
    Returns:
        str: The scraped rental market information
    """
    try:
        location_slug = location.lower().replace(" ", "-")
        
        # Rental market specific sources
        urls = [
            f"https://www.rentcafe.com/average-rent-market-trends/{location_slug}/",
            f"https://www.apartmentlist.com/research/national/",
            f"https://www.zillow.com/rental-manager/market-trends/",
            f"https://www.apartments.com/rental-trends/{location_slug}/"
        ]
        
        # Try each URL until we get substantial content
        for url in urls:
            logger.info(f"Trying to scrape rental market information from {url}")
            
            content = get_website_text_content(url)
            
            if content and len(content) > 500:
                logger.info(f"Successfully scraped {len(content)} characters from {url}")
                return content
        
        # If no successful scrape, return empty string
        logger.warning(f"Failed to scrape rental market information for {location}")
        return ""
    except Exception as e:
        logger.error(f"Error getting rental market info: {str(e)}")
        return ""

def get_investment_market_info(location: str) -> str:
    """
    Scrape real estate investment market information for a specific location.
    
    Args:
        location (str): The location to get investment market information for
        
    Returns:
        str: The scraped investment market information
    """
    try:
        location_slug = location.lower().replace(" ", "-")
        
        # Investment market specific sources
        urls = [
            f"https://www.mashvisor.com/blog/real-estate-market/{location_slug}/",
            f"https://www.biggerpockets.com/research/{location_slug}-real-estate-trends",
            "https://www.redfin.com/news/data-center/",
            f"https://www.fortunebuilders.com/real-estate-market/{location_slug}/"
        ]
        
        # Try each URL until we get substantial content
        for url in urls:
            logger.info(f"Trying to scrape investment market information from {url}")
            
            content = get_website_text_content(url)
            
            if content and len(content) > 500:
                logger.info(f"Successfully scraped {len(content)} characters from {url}")
                return content
        
        # If no successful scrape, return empty string
        logger.warning(f"Failed to scrape investment market information for {location}")
        return ""
    except Exception as e:
        logger.error(f"Error getting investment market info: {str(e)}")
        return ""

def extract_market_insights(text: str, market_type: str = "residential") -> Dict[str, Any]:
    """
    Extract key market insights from scraped text.
    
    Args:
        text (str): The scraped text content
        market_type (str): Type of market (residential, rental, investment)
        
    Returns:
        dict: Dictionary of extracted market insights
    """
    try:
        insights = {}
        
        # Common patterns for all market types
        
        # Median home price
        median_price_match = re.search(r'median(?:\s+home)?\s+price(?:\s+of)?\s+(?:is|was)?\s*\$?([\d,]+(?:\.\d+)?)', text, re.IGNORECASE)
        if median_price_match:
            insights['median_price'] = median_price_match.group(1).replace(',', '')
        
        # Average home price
        avg_price_match = re.search(r'average(?:\s+home)?\s+price(?:\s+of)?\s+(?:is|was)?\s*\$?([\d,]+(?:\.\d+)?)', text, re.IGNORECASE)
        if avg_price_match:
            insights['average_price'] = avg_price_match.group(1).replace(',', '')
        
        # Price change (year-over-year)
        yoy_change_match = re.search(r'(increased|decreased|rose|fell|up|down)(?:\s+by)?\s+(\d+(?:\.\d+)?)(?:\s*%|\s+percent)', text, re.IGNORECASE)
        if yoy_change_match:
            direction = yoy_change_match.group(1).lower()
            value = float(yoy_change_match.group(2))
            
            if direction in ['decreased', 'fell', 'down']:
                value = -value
                
            insights['price_change_pct'] = value
        
        # Days on market
        dom_match = re.search(r'(\d+)\s+days\s+on(?:\s+the)?\s+market', text, re.IGNORECASE)
        if dom_match:
            insights['days_on_market'] = int(dom_match.group(1))
        
        # Inventory / Supply
        inventory_match = re.search(r'(\d+(?:\.\d+)?)\s+months\s+(?:of\s+)?(?:inventory|supply)', text, re.IGNORECASE)
        if inventory_match:
            insights['months_of_supply'] = float(inventory_match.group(1))
        
        # Interest rate
        rate_match = re.search(r'(mortgage|interest)\s+rates?(?:\s+at|of)?\s+(\d+(?:\.\d+)?)(?:\s*%|\s+percent)', text, re.IGNORECASE)
        if rate_match:
            insights['interest_rate'] = float(rate_match.group(2))
        
        # Housing starts
        starts_match = re.search(r'housing\s+starts\s+(?:at|of|were)?\s+([\d,]+)', text, re.IGNORECASE)
        if starts_match:
            insights['housing_starts'] = int(starts_match.group(1).replace(',', ''))
        
        # Specific patterns based on market type
        if market_type == "rental":
            # Average rent
            rent_match = re.search(r'average(?:\s+monthly)?\s+rent(?:\s+of)?\s+(?:is|was)?\s*\$?([\d,]+(?:\.\d+)?)', text, re.IGNORECASE)
            if rent_match:
                insights['average_rent'] = rent_match.group(1).replace(',', '')
            
            # Rent growth rate
            rent_growth_match = re.search(r'rent(?:s|al)?\s+(?:prices|rates)?\s+(?:have|has)?\s+(increased|decreased|risen|fallen)(?:\s+by)?\s+(\d+(?:\.\d+)?)(?:\s*%|\s+percent)', text, re.IGNORECASE)
            if rent_growth_match:
                direction = rent_growth_match.group(1).lower()
                value = float(rent_growth_match.group(2))
                
                if direction in ['decreased', 'fallen']:
                    value = -value
                    
                insights['rent_growth_pct'] = value
            
            # Occupancy rate
            occupancy_match = re.search(r'occupancy\s+rate(?:s)?\s+(?:of|at|is|are)?\s+(\d+(?:\.\d+)?)(?:\s*%|\s+percent)', text, re.IGNORECASE)
            if occupancy_match:
                insights['occupancy_rate'] = float(occupancy_match.group(1))
            
            # Vacancy rate
            vacancy_match = re.search(r'vacancy\s+rate(?:s)?\s+(?:of|at|is|are)?\s+(\d+(?:\.\d+)?)(?:\s*%|\s+percent)', text, re.IGNORECASE)
            if vacancy_match:
                insights['vacancy_rate'] = float(vacancy_match.group(1))
        
        elif market_type == "investment":
            # Cap rate
            cap_rate_match = re.search(r'cap\s+rate(?:s)?\s+(?:of|at|is|are)?\s+(\d+(?:\.\d+)?)(?:\s*%|\s+percent)', text, re.IGNORECASE)
            if cap_rate_match:
                insights['cap_rate'] = float(cap_rate_match.group(1))
            
            # Cash on cash return
            coc_match = re.search(r'cash\s+on\s+cash\s+return(?:s)?\s+(?:of|at|is|are)?\s+(\d+(?:\.\d+)?)(?:\s*%|\s+percent)', text, re.IGNORECASE)
            if coc_match:
                insights['cash_on_cash_return'] = float(coc_match.group(1))
            
            # Price to rent ratio
            price_rent_match = re.search(r'price\s+to\s+rent\s+ratio(?:s)?\s+(?:of|at|is|are)?\s+(\d+(?:\.\d+)?)', text, re.IGNORECASE)
            if price_rent_match:
                insights['price_to_rent_ratio'] = float(price_rent_match.group(1))
            
            # GRM (Gross Rent Multiplier)
            grm_match = re.search(r'(?:gross\s+rent\s+multiplier|GRM)(?:s)?\s+(?:of|at|is|are)?\s+(\d+(?:\.\d+)?)', text, re.IGNORECASE)
            if grm_match:
                insights['gross_rent_multiplier'] = float(grm_match.group(1))
            
            # ROI
            roi_match = re.search(r'(?:return\s+on\s+investment|ROI)(?:s)?\s+(?:of|at|is|are)?\s+(\d+(?:\.\d+)?)(?:\s*%|\s+percent)', text, re.IGNORECASE)
            if roi_match:
                insights['roi'] = float(roi_match.group(1))
        
        # International market specific patterns
        currency_symbols = {
            '₹': 'INR',  # Indian Rupee
            '£': 'GBP',  # British Pound
            '€': 'EUR',  # Euro
            'AU$': 'AUD',  # Australian Dollar
            'C$': 'CAD',  # Canadian Dollar
            '¥': 'JPY',  # Japanese Yen
            'HK$': 'HKD',  # Hong Kong Dollar
            'S$': 'SGD',  # Singapore Dollar
            'R$': 'BRL',  # Brazilian Real
            'R': 'ZAR',  # South African Rand
        }
        
        # Detect currency
        for symbol, code in currency_symbols.items():
            if symbol in text:
                insights['currency'] = code
                break
        
        # Add extraction timestamp
        insights['extraction_date'] = datetime.now().strftime('%Y-%m-%d')
        insights['market_type'] = market_type
        
        logger.info(f"Extracted {len(insights)} market insights for {market_type} market")
        return insights
    except Exception as e:
        logger.error(f"Error extracting market insights: {str(e)}")
        return {}