"""
Example script demonstrating how to use web scraping to gather real estate market information.
This example shows how to:
1. Scrape real estate market news and trends from websites
2. Extract structured data from the text content
3. Save the data for use in the application
"""

import os
import sys
import json
import pandas as pd
from datetime import datetime

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the web scraper module
from utils.web_scraper import (
    get_website_text_content, 
    get_real_estate_market_info,
    scrape_property_details,
    extract_market_insights
)

def scrape_market_news(location=""):
    """
    Scrape real estate market news and trends for a specific location.
    
    Args:
        location (str, optional): City or region to get information for
                                  If not provided, get general market trends
    
    Returns:
        str: Scraped text content
    """
    print(f"Scraping market information for {location or 'general market trends'}...")
    
    market_info = get_real_estate_market_info(location)
    
    if market_info:
        print(f"Successfully scraped {len(market_info)} characters of market information")
        # Save to file for demonstration
        filename = f"market_info_{location.replace(' ', '_').lower() or 'general'}.txt"
        with open(filename, "w") as f:
            f.write(market_info)
        print(f"Saved to {filename}")
    else:
        print("No market information found")
    
    return market_info

def extract_insights_from_text(text):
    """
    Extract structured insights from scraped text.
    
    Args:
        text (str): Scraped text content
    
    Returns:
        dict: Structured market insights
    """
    print("Extracting insights from scraped content...")
    
    insights = extract_market_insights(text)
    
    if insights:
        print("Successfully extracted market insights")
        # Print the extracted insights
        for key, value in insights.items():
            print(f"{key}: {value}")
    else:
        print("No insights could be extracted")
    
    return insights

def scrape_specific_property(property_url):
    """
    Scrape details for a specific property.
    
    Args:
        property_url (str): URL of the property listing
    
    Returns:
        dict: Property details
    """
    print(f"Scraping property details from {property_url}...")
    
    property_details = scrape_property_details(property_url)
    
    if property_details:
        print("Successfully scraped property details:")
        # Print the property details
        for key, value in property_details.items():
            print(f"{key}: {value}")
    else:
        print("No property details found")
    
    return property_details

def scrape_real_estate_trends(locations):
    """
    Scrape real estate trends for multiple locations and save as CSV.
    
    Args:
        locations (list): List of locations to scrape
    
    Returns:
        DataFrame: Combined market data
    """
    print(f"Scraping real estate trends for {len(locations)} locations...")
    
    all_insights = []
    
    for location in locations:
        print(f"\nProcessing {location}...")
        
        # Scrape market information
        market_info = get_real_estate_market_info(location)
        
        if not market_info:
            print(f"No information found for {location}")
            continue
        
        # Extract insights
        insights = extract_market_insights(market_info)
        
        if not insights:
            print(f"No insights could be extracted for {location}")
            continue
        
        # Add location and timestamp
        insights['location'] = location
        insights['scraped_date'] = datetime.now().strftime('%Y-%m-%d')
        
        # Add to collection
        all_insights.append(insights)
    
    # Convert to DataFrame
    if all_insights:
        df = pd.DataFrame(all_insights)
        
        # Save to CSV
        csv_filename = "real_estate_trends.csv"
        df.to_csv(csv_filename, index=False)
        print(f"\nSaved trends data to {csv_filename}")
        
        return df
    else:
        print("No trend data could be collected")
        return None

def demo_web_scraping():
    """Run a demonstration of web scraping capabilities."""
    try:
        print("=" * 50)
        print("REAL ESTATE WEB SCRAPING DEMONSTRATION")
        print("=" * 50)
        
        # Example 1: Scrape general market trends
        print("\n[Example 1: General Market Trends]")
        market_info = scrape_market_news()
        
        # Example 2: Extract insights from the scraped content
        if market_info:
            print("\n[Example 2: Extracting Insights]")
            insights = extract_insights_from_text(market_info)
        
        # Example 3: Scrape market information for a specific location
        print("\n[Example 3: Location-Specific Market Information]")
        location_info = scrape_market_news("New York")
        
        # Example 4: Scrape multiple locations and create a CSV
        print("\n[Example 4: Multi-Location Trend Analysis]")
        locations = ["New York", "Los Angeles", "Chicago", "Miami", "Seattle", "Austin"]
        trends_df = scrape_real_estate_trends(locations)
        
        # Example 5: Scrape a specific property listing
        print("\n[Example 5: Specific Property Details]")
        # Note: This is a placeholder URL for demonstration
        property_url = "https://www.example-realestate.com/listing/123456"
        property_details = scrape_specific_property(property_url)
        
        print("\n" + "=" * 50)
        print("DEMONSTRATION COMPLETE")
        print("=" * 50)
        
    except Exception as e:
        print(f"Error in web scraping demonstration: {str(e)}")

if __name__ == "__main__":
    demo_web_scraping()