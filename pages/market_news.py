import streamlit as st
import pandas as pd
from utils.web_scraper import get_real_estate_market_info, extract_market_insights
import time
from datetime import datetime

def show_market_news():
    """Display real estate market news and insights from web scraping"""
    st.title("🌍 Real Estate Market News & Insights")
    
    st.markdown("""
    This page provides the latest real estate market news and insights gathered from various sources.
    Get up-to-date information on market trends, price movements, and housing statistics.
    """)
    
    # Initialize session state for market data
    if 'market_info' not in st.session_state:
        st.session_state.market_info = None
        
    if 'last_scrape_time' not in st.session_state:
        st.session_state.last_scrape_time = None
        
    if 'scraping_location' not in st.session_state:
        st.session_state.scraping_location = ""
    
    # Location input for location-specific market information
    location = st.text_input(
        "Enter location for market insights (city, state, or leave blank for general market news):", 
        value=st.session_state.scraping_location
    )
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.write("Click the button to fetch the latest market information. This may take a few moments.")
    
    with col2:
        scrape_button = st.button("Get Market News", key="scrape_btn")
    
    # Display last scrape time if available
    if st.session_state.last_scrape_time:
        st.info(f"Last updated: {st.session_state.last_scrape_time}")
    
    if scrape_button:
        st.session_state.scraping_location = location
        
        # Show loading spinner while scraping
        with st.spinner("Fetching the latest real estate market information..."):
            # Fetch market information
            market_info = get_real_estate_market_info(location)
            
            if market_info and len(market_info) > 100:  # Ensure we got meaningful content
                st.session_state.market_info = market_info
                st.session_state.last_scrape_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Also extract insights
                insights = extract_market_insights(market_info)
                st.session_state.market_insights = insights
                
                st.success("Market information updated successfully!")
                st.rerun()
            else:
                st.error("Unable to retrieve market information. Please try a different location or try again later.")
    
    # Display market information if available
    if st.session_state.market_info:
        # Display extracted insights if available
        if 'market_insights' in st.session_state:
            insights = st.session_state.market_insights
            
            st.subheader("📊 Market Trends Detected")
            
            if insights.get("detected_trends"):
                trends_html = ""
                for trend in insights["detected_trends"]:
                    formatted_trend = trend.replace("_", " ").title()
                    trends_html += f"- **{formatted_trend}**<br>"
                
                st.markdown(trends_html, unsafe_allow_html=True)
            else:
                st.info("No specific trends detected in the scraped content.")
        
        # Display the raw market information
        st.subheader("📰 Market Information")
        
        with st.expander("View Full Market Information", expanded=True):
            st.markdown(st.session_state.market_info[:5000] + "..." 
                       if len(st.session_state.market_info) > 5000 
                       else st.session_state.market_info)
    
    # Disclaimer
    st.markdown("---")
    st.caption("""
    **Disclaimer**: The information provided here is gathered from public sources and may not be complete 
    or up-to-date. Always consult with a real estate professional before making investment decisions.
    """)