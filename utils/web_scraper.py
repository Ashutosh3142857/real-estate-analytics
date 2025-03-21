import trafilatura
import streamlit as st
import pandas as pd
from datetime import datetime

def get_website_text_content(url: str) -> str:
    """
    This function takes a url and returns the main text content of the website.
    The text content is extracted using trafilatura and easier to understand
    than raw HTML.
    
    Args:
        url (str): The URL of the website to scrape
        
    Returns:
        str: The main text content of the website
    """
    try:
        # Send a request to the website
        downloaded = trafilatura.fetch_url(url)
        
        if not downloaded:
            return f"Failed to download content from {url}"
        
        # Extract the main text content
        text = trafilatura.extract(downloaded)
        
        if not text:
            return f"No content could be extracted from {url}"
        
        return text
    
    except Exception as e:
        return f"Error scraping website: {str(e)}"

def get_real_estate_market_info(location: str = "") -> str:
    """
    Scrape the latest real estate market information for a specific location
    or general market trends if no location is provided.
    
    Args:
        location (str, optional): The location to get market information for
        
    Returns:
        str: The scraped market information
    """
    # Default URLs for real estate market information
    default_urls = [
        "https://www.nar.realtor/research-and-statistics/housing-statistics",
        "https://www.zillow.com/research/",
        "https://www.redfin.com/news/housing-market-news/"
    ]
    
    # If location is provided, try to find location-specific information
    if location and location.strip():
        # Construct location-specific URLs
        # Note: These are examples and might not work for all locations
        location_formatted = location.replace(" ", "-").lower()
        location_urls = [
            f"https://www.zillow.com/market-report/{location_formatted}/",
            f"https://www.redfin.com/{location_formatted}-housing-market/",
            f"https://www.realtor.com/realestateandhomes-search/{location_formatted}/overview"
        ]
        
        # Try each URL until we get content
        for url in location_urls:
            content = get_website_text_content(url)
            if content and "Error" not in content and "Failed" not in content:
                return content
    
    # If no location-specific content found or no location provided, use default URLs
    combined_content = []
    for url in default_urls:
        content = get_website_text_content(url)
        if content and "Error" not in content and "Failed" not in content:
            combined_content.append(content)
    
    if not combined_content:
        return "Unable to retrieve real estate market information."
    
    return "\n\n===\n\n".join(combined_content)

def scrape_property_details(property_url: str) -> dict:
    """
    Scrape detailed information about a specific property from its URL
    
    Args:
        property_url (str): URL of the property listing
        
    Returns:
        dict: Dictionary containing property details
    """
    try:
        # Download the content
        downloaded = trafilatura.fetch_url(property_url)
        
        if not downloaded:
            return {"error": f"Failed to download content from {property_url}"}
        
        # Extract the text
        text = trafilatura.extract(downloaded)
        
        if not text:
            return {"error": f"No content could be extracted from {property_url}"}
        
        # Parse the extracted text to identify property details
        # This is a simplified example - in a real application, 
        # you would need more sophisticated parsing or use specific APIs
        
        property_details = {
            "url": property_url,
            "scraped_date": datetime.now().strftime("%Y-%m-%d"),
            "full_description": text[:1000] + "..." if len(text) > 1000 else text,
            "scraped_text": text
        }
        
        return property_details
    
    except Exception as e:
        return {"error": f"Error scraping property details: {str(e)}"}

def extract_market_insights(text: str) -> dict:
    """
    Extract key market insights from scraped text
    
    Args:
        text (str): The scraped text content
        
    Returns:
        dict: Dictionary of extracted market insights
    """
    # This is a simplified example - in a real application, you would use 
    # NLP techniques or an LLM to extract structured information from the text
    
    insights = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "content_length": len(text),
        "excerpt": text[:500] + "..." if len(text) > 500 else text
    }
    
    # Simple keyword-based extraction
    market_indicators = {
        "price_increase": ["price increase", "rising prices", "appreciation"],
        "price_decrease": ["price decrease", "falling prices", "depreciation"],
        "high_demand": ["high demand", "seller's market", "competitive market"],
        "low_inventory": ["low inventory", "shortage", "limited supply"],
        "buyer_opportunity": ["buyer's market", "opportunity", "good time to buy"]
    }
    
    insights["detected_trends"] = []
    
    for trend, keywords in market_indicators.items():
        for keyword in keywords:
            if keyword.lower() in text.lower():
                insights["detected_trends"].append(trend)
                break
    
    return insights