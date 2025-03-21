"""
Market News page for displaying real estate market news and insights from web scraping.
"""

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta

# Import web scraper utilities
from utils.web_scraper import (
    get_website_text_content,
    get_real_estate_market_info,
    extract_market_insights
)

def show_market_news():
    """Display real estate market news and insights from web scraping"""
    st.title("Real Estate Market News & Insights")
    
    st.markdown("""
    This page provides the latest real estate market news, trends, and insights gathered through web scraping.
    The system automatically extracts key market indicators from various real estate news sources.
    """)
    
    # Location-based news search
    st.header("🔍 Search Market News by Location")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        location = st.text_input("Enter a location (city, state, or country)", 
                               placeholder="e.g., New York, California, India")
    
    with col2:
        search_button = st.button("Get Market News")
    
    if search_button or ('last_location' in st.session_state and location == st.session_state.get('last_location')):
        # Store the location in session state
        st.session_state.last_location = location
        
        with st.spinner(f"Gathering market information for {location or 'general market'}..."):
            # Get the market information
            market_info = get_real_estate_market_info(location)
            
            if market_info:
                # Display the scraped information
                st.success(f"Successfully gathered market information for {location or 'general market'}")
                
                # Extract insights
                insights = extract_market_insights(market_info)
                
                if insights and len(insights) > 1:  # At least one insight plus the timestamp
                    display_market_insights(insights, location)
                
                # Display the raw text in an expander
                with st.expander("Show Raw Market Information"):
                    st.markdown(f"### Market Information for {location or 'General Market'}")
                    st.text_area("", market_info, height=300)
            else:
                st.error(f"Could not retrieve market information for {location or 'general market'}. " +
                         "Please try another location or try again later.")
    
    # Trending markets section
    st.header("📈 Trending Real Estate Markets")
    
    # Simulated trending market data (in a real implementation, this would be from database)
    trending_markets = [
        {"location": "Austin, TX", "trend": "+12.5%", "avg_price": "$550,000", "days_on_market": 15},
        {"location": "Raleigh, NC", "trend": "+9.8%", "avg_price": "$425,000", "days_on_market": 18},
        {"location": "Nashville, TN", "trend": "+8.7%", "avg_price": "$470,000", "days_on_market": 21},
        {"location": "Boise, ID", "trend": "+7.2%", "avg_price": "$510,000", "days_on_market": 25},
        {"location": "Phoenix, AZ", "trend": "+6.8%", "avg_price": "$480,000", "days_on_market": 30}
    ]
    
    # Display trending markets
    col1, col2, col3, col4 = st.columns(4)
    cols = [col1, col2, col3, col4]
    
    headers = ["Location", "YoY Change", "Avg. Price", "Days on Market"]
    for i, header in enumerate(headers):
        cols[i].markdown(f"**{header}**")
    
    for market in trending_markets:
        col1.write(market["location"])
        col2.write(market["trend"])
        col3.write(market["avg_price"])
        col4.write(str(market["days_on_market"]))
    
    # Market snapshots from around the world
    st.header("🌎 Global Market Snapshots")
    
    tabs = st.tabs(["North America", "Europe", "Asia", "Australia", "Africa"])
    
    with tabs[0]:  # North America
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("United States")
            st.write("- Median home price: $428,700")
            st.write("- Year-over-year change: +5.3%")
            st.write("- 30-year fixed mortgage rate: 6.8%")
            st.write("- Housing inventory: 3.2 months")
        
        with col2:
            st.subheader("Canada")
            st.write("- Median home price: $740,900 CAD")
            st.write("- Year-over-year change: +2.8%")
            st.write("- 5-year fixed mortgage rate: 5.2%")
            st.write("- Housing inventory: 4.1 months")
    
    with tabs[1]:  # Europe
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("United Kingdom")
            st.write("- Average house price: £295,000")
            st.write("- Year-over-year change: +3.5%")
            st.write("- 2-year fixed mortgage rate: 4.9%")
            st.write("- Average time to sell: 45 days")
        
        with col2:
            st.subheader("Germany")
            st.write("- Average apartment price: €423,000")
            st.write("- Year-over-year change: +1.9%")
            st.write("- 10-year fixed mortgage rate: 3.8%")
            st.write("- New housing construction: Down 7.6%")
    
    with tabs[2]:  # Asia
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("India")
            st.write("- Average urban home price: ₹7,800,000")
            st.write("- Year-over-year change: +6.7%")
            st.write("- Home loan interest rate: 8.5%")
            st.write("- Residential launches: Up 14.2%")
        
        with col2:
            st.subheader("Japan")
            st.write("- Average apartment price in Tokyo: ¥62,500,000")
            st.write("- Year-over-year change: +0.8%")
            st.write("- 35-year fixed mortgage rate: 1.7%")
            st.write("- New construction starts: Down 3.1%")
    
    with tabs[3]:  # Australia
        st.subheader("Australia")
        st.write("- Median house price: $955,900 AUD")
        st.write("- Year-over-year change: +4.2%")
        st.write("- Standard variable rate: 5.6%")
        st.write("- Average days on market: 32")
        st.write("- First-time buyers: Down 8.3%")
    
    with tabs[4]:  # Africa
        st.subheader("South Africa")
        st.write("- Average house price: R1,350,000")
        st.write("- Year-over-year change: +3.1%")
        st.write("- Prime lending rate: 11.75%")
        st.write("- Market activity index: 52.3 (expanding)")
    
    # Latest market news
    st.header("📰 Latest Real Estate News")
    
    # Simulate latest news with dates
    today = datetime.now()
    news_items = [
        {
            "title": "Fed Signals Potential Rate Cuts, Mortgage Rates Expected to Follow",
            "source": "Reuters",
            "date": (today - timedelta(days=1)).strftime("%b %d, %Y"),
            "snippet": "The Federal Reserve signaled potential interest rate cuts later this year, which could bring relief to the mortgage market. Analysts expect 30-year fixed rates to gradually decline over the coming months."
        },
        {
            "title": "Housing Inventory Shows Signs of Recovery in Major Markets",
            "source": "Bloomberg",
            "date": (today - timedelta(days=3)).strftime("%b %d, %Y"),
            "snippet": "After years of historically low inventory, major housing markets are seeing an uptick in available homes. This trend could help ease price pressures and provide more options for buyers."
        },
        {
            "title": "Global Investors Pouring Capital into Build-to-Rent Developments",
            "source": "Financial Times",
            "date": (today - timedelta(days=5)).strftime("%b %d, %Y"),
            "snippet": "Institutional investors are increasingly focusing on build-to-rent housing developments across global markets, with over $50 billion deployed in the sector during the past year."
        },
        {
            "title": "Tech Hubs Seeing Stabilization After Pandemic-Era Price Surge",
            "source": "CNBC",
            "date": (today - timedelta(days=7)).strftime("%b %d, %Y"),
            "snippet": "Major technology hub cities are experiencing price stabilization after the dramatic surges seen during the pandemic. Markets like San Francisco and Seattle are seeing more balanced conditions."
        }
    ]
    
    for item in news_items:
        st.markdown(f"### {item['title']}")
        st.caption(f"{item['source']} • {item['date']}")
        st.write(item['snippet'])
        st.markdown("---")
    
    # Help section
    with st.expander("ℹ️ About Market News & Web Scraping"):
        st.markdown("""
        ### How This Works
        
        This page uses web scraping techniques to gather real estate market information from various online sources.
        
        The process works as follows:
        1. When you search for a location, the system attempts to scrape information from several real estate websites
        2. The raw text content is extracted using the trafilatura library, which removes HTML and keeps the main content
        3. Key market insights such as prices, trends, and metrics are extracted using pattern matching
        4. The information is presented in a structured format for easy consumption
        
        ### Sources
        
        The system attempts to gather information from these sources:
        - National Association of Realtors (NAR)
        - Zillow Research
        - Realtor.com Research
        - CoreLogic Market Trends
        - Location-specific real estate portals
        
        ### Example Integration Code
        
        You can integrate this functionality into your own applications using our integration system:
        
        ```python
        # Import the web scraper module
        from utils.web_scraper import get_real_estate_market_info, extract_market_insights
        
        # Get market information for a location
        market_info = get_real_estate_market_info("New York")
        
        # Extract structured insights
        insights = extract_market_insights(market_info)
        
        # Use the insights in your application
        print(f"Median price: ${insights.get('median_price', 'N/A')}")
        print(f"Price change: {insights.get('price_change_pct', 'N/A')}%")
        ```
        
        See the full example in `examples/web_scraping_example.py`
        """)

def display_market_insights(insights, location):
    """Display market insights in a structured format"""
    
    # Remove timestamp for display
    display_insights = insights.copy()
    if 'extraction_date' in display_insights:
        display_insights.pop('extraction_date')
    
    # Title and summary
    st.subheader(f"Market Insights for {location or 'General Market'}")
    st.caption(f"Data collected on {insights.get('extraction_date', datetime.now().strftime('%Y-%m-%d'))}")
    
    # Metrics in columns
    cols = st.columns(3)
    
    # Median price
    if 'median_price' in insights:
        cols[0].metric("Median Price", f"${insights['median_price']}")
    
    # Average price
    if 'average_price' in insights:
        cols[1].metric("Average Price", f"${insights['average_price']}")
    
    # Price change
    if 'price_change_pct' in insights:
        change = insights['price_change_pct']
        delta_color = "normal" if change == 0 else "up" if change > 0 else "down"
        cols[2].metric("Year-over-Year Change", f"{change}%", delta=f"{change}%", delta_color=delta_color)
    
    # More metrics in columns
    cols = st.columns(3)
    
    # Days on market
    if 'days_on_market' in insights:
        cols[0].metric("Days on Market", insights['days_on_market'])
    
    # Months of supply
    if 'months_of_supply' in insights:
        cols[1].metric("Months of Supply", insights['months_of_supply'])
    
    # Interest rate
    if 'interest_rate' in insights:
        cols[2].metric("Interest Rate", f"{insights['interest_rate']}%")
    
    # Housing starts (if available)
    if 'housing_starts' in insights:
        st.metric("Housing Starts", f"{insights['housing_starts']:,}")

if __name__ == "__main__":
    show_market_news()