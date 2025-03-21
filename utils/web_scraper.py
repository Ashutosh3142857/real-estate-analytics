"""
Web scraping module for gathering real estate market information and property details.
This module uses Trafilatura for content extraction, which provides cleaner text from HTML pages.
"""

import trafilatura
import logging
import re
import json
from datetime import datetime
from typing import Dict, Any, Optional, List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_website_text_content(url: str) -> str:
    """
    Extract the main text content from a website.
    
    Args:
        url (str): The URL of the website to scrape
        
    Returns:
        str: The main text content of the website
    """
    try:
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

def extract_market_insights(text: str) -> Dict[str, Any]:
    """
    Extract key market insights from scraped text.
    
    Args:
        text (str): The scraped text content
        
    Returns:
        dict: Dictionary of extracted market insights
    """
    try:
        insights = {}
        
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
        
        # Add extraction timestamp
        insights['extraction_date'] = datetime.now().strftime('%Y-%m-%d')
        
        logger.info(f"Extracted {len(insights)} market insights")
        return insights
    except Exception as e:
        logger.error(f"Error extracting market insights: {str(e)}")
        return {}