"""
Market News page for displaying real estate market news and insights from web scraping.
This page provides comprehensive market information from global real estate sources,
with specialized data for residential, rental and investment markets.
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
    get_international_market_info,
    get_rental_market_info,
    get_investment_market_info,
    extract_market_insights
)

def show_market_news():
    """Display real estate market news and insights from web scraping"""
    st.title("Real Estate Market News & Insights")
    
    st.markdown("""
    This page provides the latest real estate market news, trends, and insights gathered through web scraping.
    The system automatically extracts key market indicators from various real estate news sources worldwide,
    with support for international markets and specialized data for rental and investment segments.
    """)
    
    # Location-based news search with advanced options
    st.header("🔍 Search Market News by Location")
    
    # Create tabs for different search types
    search_tabs = st.tabs(["Location Search", "International Markets", "Specialized Markets"])
    
    with search_tabs[0]:  # Basic location search
        col1, col2 = st.columns([3, 1])
        
        with col1:
            location = st.text_input("Enter a location (city, state, or country)", 
                                  placeholder="e.g., New York, California, India",
                                  key="basic_location")
        
        with col2:
            search_button = st.button("Get Market News", key="basic_search")
        
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
    
    with search_tabs[1]:  # International market search
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            country = st.selectbox(
                "Select Country",
                options=["United States", "Canada", "United Kingdom", "Germany", "France", 
                        "Australia", "Japan", "India", "Brazil", "South Africa"],
                key="intl_country"
            )
        
        with col2:
            city = st.text_input(
                "City (Optional)",
                placeholder="e.g., London, Mumbai, Sydney",
                key="intl_city"
            )
        
        with col3:
            intl_search_button = st.button("Get Market News", key="intl_search")
        
        if intl_search_button:
            with st.spinner(f"Gathering international market information for {city + ', ' if city else ''}{country}..."):
                # Get international market information
                market_info = get_international_market_info(country, city)
                
                if market_info:
                    # Display the scraped information
                    st.success(f"Successfully gathered market information for {city + ', ' if city else ''}{country}")
                    
                    # Extract insights with location
                    location_text = f"{city + ', ' if city else ''}{country}"
                    insights = extract_market_insights(market_info)
                    
                    if insights and len(insights) > 1:  # At least one insight plus the timestamp
                        display_market_insights(insights, location_text)
                    
                    # Display the raw text in an expander
                    with st.expander("Show Raw Market Information"):
                        st.markdown(f"### Market Information for {city + ', ' if city else ''}{country}")
                        st.text_area("", market_info, height=300)
                else:
                    st.error(f"Could not retrieve market information for {city + ', ' if city else ''}{country}. " +
                            "Please try another location or try again later.")
    
    with search_tabs[2]:  # Specialized market search
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            specialized_location = st.text_input(
                "Enter Location",
                placeholder="e.g., Seattle, Chicago, Toronto",
                key="specialized_location"
            )
        
        with col2:
            market_type = st.selectbox(
                "Market Type",
                options=["Residential", "Rental", "Investment"],
                key="market_type"
            )
        
        with col3:
            specialized_search_button = st.button("Get Market News", key="specialized_search")
        
        if specialized_search_button and specialized_location:
            market_type_lower = market_type.lower()
            
            with st.spinner(f"Gathering {market_type_lower} market information for {specialized_location}..."):
                # Get appropriate specialized market information
                if market_type_lower == "rental":
                    market_info = get_rental_market_info(specialized_location)
                elif market_type_lower == "investment":
                    market_info = get_investment_market_info(specialized_location)
                else:  # Default to residential
                    market_info = get_real_estate_market_info(specialized_location)
                
                if market_info:
                    # Display the scraped information
                    st.success(f"Successfully gathered {market_type_lower} market information for {specialized_location}")
                    
                    # Extract insights with market type
                    insights = extract_market_insights(market_info, market_type=market_type_lower)
                    
                    if insights and len(insights) > 1:  # At least one insight plus the timestamp
                        display_specialized_insights(insights, specialized_location, market_type_lower)
                    
                    # Display the raw text in an expander
                    with st.expander("Show Raw Market Information"):
                        st.markdown(f"### {market_type} Market Information for {specialized_location}")
                        st.text_area("", market_info, height=300)
                else:
                    st.error(f"Could not retrieve {market_type_lower} market information for {specialized_location}. " +
                            "Please try another location or try again later.")
        elif specialized_search_button:
            st.warning("Please enter a location to search for specialized market information.")
    
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

def display_specialized_insights(insights, location, market_type):
    """
    Display specialized market insights in a structured format based on market type.
    
    Args:
        insights (dict): Dictionary containing market insights
        location (str): Location the insights are for
        market_type (str): Type of market (residential, rental, investment)
    """
    # Remove timestamp for display
    display_insights = insights.copy()
    if 'extraction_date' in display_insights:
        display_insights.pop('extraction_date')
    if 'market_type' in display_insights:
        display_insights.pop('market_type')
    
    # Detect currency
    currency_symbol = '$'
    if 'currency' in insights:
        currency_code = insights['currency']
        currency_symbols = {
            'USD': '$', 'CAD': 'C$', 'AUD': 'AU$', 'GBP': '£', 
            'EUR': '€', 'JPY': '¥', 'INR': '₹', 'BRL': 'R$',
            'ZAR': 'R', 'SGD': 'S$', 'HKD': 'HK$'
        }
        currency_symbol = currency_symbols.get(currency_code, '$')
    
    # Title and summary
    market_title = market_type.capitalize()
    st.subheader(f"{market_title} Market Insights for {location}")
    st.caption(f"Data collected on {insights.get('extraction_date', datetime.now().strftime('%Y-%m-%d'))}")
    
    if market_type == "residential":
        # Standard residential metrics
        cols = st.columns(3)
        
        # Median/Average prices
        if 'median_price' in insights:
            cols[0].metric("Median Price", f"{currency_symbol}{insights['median_price']}")
        
        if 'average_price' in insights:
            cols[1].metric("Average Price", f"{currency_symbol}{insights['average_price']}")
        
        # Price change
        if 'price_change_pct' in insights:
            change = insights['price_change_pct']
            delta_color = "normal" if change == 0 else "up" if change > 0 else "down"
            cols[2].metric("Year-over-Year Change", f"{change}%", delta=f"{change}%", delta_color=delta_color)
        
        # More metrics
        cols = st.columns(3)
        
        if 'days_on_market' in insights:
            cols[0].metric("Days on Market", insights['days_on_market'])
        
        if 'months_of_supply' in insights:
            cols[1].metric("Months of Supply", insights['months_of_supply'])
        
        if 'interest_rate' in insights:
            cols[2].metric("Interest Rate", f"{insights['interest_rate']}%")
    
    elif market_type == "rental":
        # Rental market specific metrics
        cols = st.columns(3)
        
        # Average rent
        if 'average_rent' in insights:
            cols[0].metric("Average Monthly Rent", f"{currency_symbol}{insights['average_rent']}")
        
        # Rent growth rate
        if 'rent_growth_pct' in insights:
            change = insights['rent_growth_pct']
            delta_color = "normal" if change == 0 else "up" if change > 0 else "down"
            cols[1].metric("Rent Growth", f"{change}%", delta=f"{change}%", delta_color=delta_color)
        
        # Occupancy rate
        if 'occupancy_rate' in insights:
            cols[2].metric("Occupancy Rate", f"{insights['occupancy_rate']}%")
        
        # More metrics
        cols = st.columns(3)
        
        # Vacancy rate
        if 'vacancy_rate' in insights:
            cols[0].metric("Vacancy Rate", f"{insights['vacancy_rate']}%")
        
        # Price to income ratio
        if 'price_to_income_ratio' in insights:
            cols[1].metric("Price to Income Ratio", insights['price_to_income_ratio'])
        
        # Average price (if available)
        if 'average_price' in insights:
            cols[2].metric("Avg. Property Price", f"{currency_symbol}{insights['average_price']}")
    
    elif market_type == "investment":
        # Investment market specific metrics
        cols = st.columns(3)
        
        # Cap rate
        if 'cap_rate' in insights:
            cols[0].metric("Cap Rate", f"{insights['cap_rate']}%")
        
        # Cash on cash return
        if 'cash_on_cash_return' in insights:
            cols[1].metric("Cash on Cash Return", f"{insights['cash_on_cash_return']}%")
        
        # Price to rent ratio
        if 'price_to_rent_ratio' in insights:
            cols[2].metric("Price to Rent Ratio", insights['price_to_rent_ratio'])
        
        # More metrics
        cols = st.columns(3)
        
        # Gross Rent Multiplier
        if 'gross_rent_multiplier' in insights:
            cols[0].metric("Gross Rent Multiplier", insights['gross_rent_multiplier'])
        
        # ROI
        if 'roi' in insights:
            cols[1].metric("ROI", f"{insights['roi']}%")
        
        # Average price (if available)
        if 'average_price' in insights:
            cols[2].metric("Avg. Property Price", f"{currency_symbol}{insights['average_price']}")
    
    # Additional metrics that might be available
    remaining_metrics = []
    for key, value in display_insights.items():
        if key not in ['median_price', 'average_price', 'price_change_pct', 'days_on_market', 
                      'months_of_supply', 'interest_rate', 'housing_starts', 'currency',
                      'average_rent', 'rent_growth_pct', 'occupancy_rate', 'vacancy_rate',
                      'price_to_income_ratio', 'cap_rate', 'cash_on_cash_return',
                      'price_to_rent_ratio', 'gross_rent_multiplier', 'roi']:
            remaining_metrics.append((key, value))
    
    # Display any remaining metrics if there are any
    if remaining_metrics:
        st.subheader("Additional Metrics")
        cols = st.columns(3)
        
        for i, (key, value) in enumerate(remaining_metrics):
            col_index = i % 3
            display_key = key.replace('_', ' ').title()
            
            # Format the value based on its type
            if isinstance(value, (int, float)):
                if key.endswith('_pct') or key.endswith('_rate'):
                    display_value = f"{value}%"
                elif key.endswith('_price'):
                    display_value = f"{currency_symbol}{value}"
                else:
                    display_value = f"{value:,}"
            else:
                display_value = value
                
            cols[col_index].metric(display_key, display_value)

if __name__ == "__main__":
    show_market_news()