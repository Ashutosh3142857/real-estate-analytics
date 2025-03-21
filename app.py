import streamlit as st
import pandas as pd
import numpy as np
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

# Import utility modules
from utils.data_processing import load_sample_data
from utils.visualization import plot_market_trends, plot_property_distribution, create_property_map
from utils.real_estate_api import search_properties_by_location, search_properties_zillow, get_location_suggestions
from utils.database_init import initialize_database
from utils.api_manager import check_api_keys
from streamlit_folium import st_folium

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize database if not already initialized
try:
    initialize_database()
except Exception as e:
    logger.error(f"Error initializing database: {str(e)}")

# Page configuration
st.set_page_config(
    page_title="AI-Powered Real Estate Analytics Dashboard",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables if they don't exist
if 'data' not in st.session_state:
    st.session_state.data = load_sample_data()
    
if 'location_search' not in st.session_state:
    st.session_state.location_search = ""
    
if 'search_results' not in st.session_state:
    st.session_state.search_results = pd.DataFrame()

# Sidebar
st.sidebar.title("Real Estate Analytics")
st.sidebar.image("https://img.icons8.com/fluency/96/000000/real-estate.png", width=100)

# Navigation
page = st.sidebar.radio(
    "Navigate to",
    ["Dashboard", "Market Insights", "Indian Market", "Market News", "Property Analysis", "Property Valuation", 
     "Property Matching", "Lead Management", "Investment Calculator", "Marketing Generator", "Settings"]
)

# Filter section in sidebar
st.sidebar.header("Filters")
if not st.session_state.data.empty:
    # Location filter
    available_cities = sorted(st.session_state.data['city'].unique())
    selected_cities = st.sidebar.multiselect(
        "Select Cities",
        options=available_cities,
        default=available_cities[:3] if available_cities else None
    )
    
    # Price range filter
    min_price = int(st.session_state.data['price'].min())
    max_price = int(st.session_state.data['price'].max())
    price_range = st.sidebar.slider(
        "Price Range ($)",
        min_price,
        max_price,
        (min_price, max_price)
    )
    
    # Property type filter
    property_types = sorted(st.session_state.data['property_type'].unique())
    selected_property_types = st.sidebar.multiselect(
        "Property Type",
        options=property_types,
        default=property_types
    )
    
    # Apply filters
    filtered_data = st.session_state.data.copy()
    if selected_cities:
        filtered_data = filtered_data[filtered_data['city'].isin(selected_cities)]
    filtered_data = filtered_data[
        (filtered_data['price'] >= price_range[0]) & 
        (filtered_data['price'] <= price_range[1])
    ]
    if selected_property_types:
        filtered_data = filtered_data[filtered_data['property_type'].isin(selected_property_types)]
else:
    filtered_data = pd.DataFrame()
    st.sidebar.warning("No data available for filtering")

# Main content based on selected page
if page == "Dashboard":
    st.title("AI-Powered Real Estate Analytics Dashboard")
    
    # Global property search feature
    st.header("🔍 Search Real Estate Worldwide")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        location_search = st.text_input(
            "Enter Location (City, ZIP, Address, etc.)",
            value=st.session_state.location_search,
            key="location_input"
        )
    
    with col2:
        search_api = st.radio(
            "Data Source",
            options=["Realty Mole", "Realty in US"],
            horizontal=True
        )
        
        search_button = st.button("Search Properties", key="search_btn")
    
    if search_button and location_search:
        st.session_state.location_search = location_search
        
        # Show loading spinner
        with st.spinner(f"Searching properties in {location_search}..."):
            # Check if RapidAPI key is set in environment variables
            if not os.environ.get("RAPIDAPI_KEY"):
                # User input for API key (temporarily stored in session state)
                if 'api_key' not in st.session_state:
                    st.session_state.api_key = ""
                
                api_key = st.text_input(
                    "Enter your RapidAPI Key to search for properties:", 
                    type="password",
                    value=st.session_state.api_key
                )
                
                if api_key:
                    st.session_state.api_key = api_key
                    # Set the API key in environment variables
                    os.environ["RAPIDAPI_KEY"] = api_key
                else:
                    st.info("You need a RapidAPI key to use this feature. Visit RapidAPI.com to obtain a key.")
                    st.stop()  # Stop execution if no API key
            
            # Call the appropriate API based on selection
            if search_api == "Realty Mole":
                results = search_properties_by_location(location_search, limit=20)
            else:
                results = search_properties_zillow(location_search, limit=20)
            
            # Store results in session state
            if not results.empty:
                st.session_state.search_results = results
                st.session_state.data = results  # Update the main dataset with search results
                st.success(f"Found {len(results)} properties in {location_search}")
                st.rerun()  # Rerun app to refresh filters with new data
            else:
                st.error(f"No properties found in {location_search} or your API key doesn't have access to this service.")
    
    # Help text with API key information
    with st.expander("ℹ️ About Property Search"):
        st.write("""
        This feature allows you to search for real estate properties worldwide using external data APIs.
        
        To use this feature, you need to:
        1. Obtain a RapidAPI key from [RapidAPI](https://rapidapi.com)
        2. Subscribe to either the "Realty Mole Property API" or "Realty in US API" (or both)
        3. Add your API key to the environment variables as `RAPIDAPI_KEY`
        
        The search will return actual property listings with prices, features, and location data.
        """)
    
    st.markdown("""
    Welcome to the AI-powered Real Estate Analytics Dashboard. This platform provides comprehensive market insights and 
    property analysis to help real estate professionals make data-driven decisions.
    
    ### Featured Insights:
    - Market trends and price forecasting
    - Property valuation analysis and comparables
    - Investment opportunity calculator with ROI metrics
    - Neighborhood analytics and lifestyle matching
    - Lead qualification and nurturing automation
    - AI-powered marketing content generation
    """)
    
    # Dashboard metrics
    if not filtered_data.empty:
        col1, col2, col3 = st.columns(3)
        with col1:
            avg_price = filtered_data['price'].mean()
            st.metric("Average Property Price", f"${avg_price:,.0f}")
        
        with col2:
            median_price = filtered_data['price'].median()
            st.metric("Median Property Price", f"${median_price:,.0f}")
        
        with col3:
            avg_price_sqft = filtered_data['price'] / filtered_data['sqft']
            st.metric("Average Price/Sqft", f"${avg_price_sqft.mean():.2f}")
            
        # Featured modules section
        st.header("Featured AI-Powered Tools")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🔮 Property Valuation")
            st.write("AI-driven property valuations with comparable analysis and future price predictions")
            if st.button("Open Valuation Tool", key="valuation_btn"):
                st.session_state.page = "Property Valuation"
                st.rerun()
        
        with col2:
            st.subheader("🤖 Lead Management")
            st.write("AI-powered lead qualification, scoring, and automated nurturing campaigns")
            if st.button("Open Lead Management", key="lead_btn"):
                st.session_state.page = "Lead Management"
                st.rerun()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🏡 Smart Property Matching")
            st.write("Find ideal properties based on lifestyle, preferences, and investment potential")
            if st.button("Open Property Matching", key="matching_btn"):
                st.session_state.page = "Property Matching"
                st.rerun()
                
        with col2:
            st.subheader("📣 Marketing Generator")
            st.write("AI-powered content creation for listings, social media, and email campaigns")
            if st.button("Open Marketing Generator", key="marketing_btn"):
                st.session_state.page = "Marketing Generator"
                st.rerun()
        
        # Market trends visualization
        st.subheader("Market Price Trends")
        fig = plot_market_trends(filtered_data)
        st.plotly_chart(fig, use_container_width=True)
        
        # Property distribution
        st.subheader("Property Distribution by Type")
        fig2 = plot_property_distribution(filtered_data)
        st.plotly_chart(fig2, use_container_width=True)
        
        # Property Map Visualization
        st.subheader("Property Map")
        property_map = create_property_map(filtered_data)
        st_folium(property_map, width=1200, height=600, returned_objects=[])
        
        # Recent listings
        st.subheader("Recent Listings")
        st.dataframe(
            filtered_data.sort_values(by='list_date', ascending=False)
            .head(5)[['address', 'city', 'price', 'bedrooms', 'bathrooms', 'sqft', 'property_type']]
        )
    else:
        st.warning("No data available to display. Please adjust your filters or check the data source.")

elif page == "Market Insights":
    # Import and run market insights page
    from pages.market_insights import show_market_insights
    show_market_insights(filtered_data)
    
elif page == "Indian Market":
    # Import and run Indian market insights page
    from pages.india_market_insights import show_india_market_insights
    show_india_market_insights()
    
elif page == "Market News":
    # Import and run market news page
    from pages.market_news import show_market_news
    show_market_news()

elif page == "Property Analysis":
    # Import and run property analysis page
    from pages.property_analysis import show_property_analysis
    show_property_analysis(filtered_data)

elif page == "Property Valuation":
    # Import and run property valuation page
    from pages.property_valuation import show_property_valuation
    show_property_valuation()

elif page == "Property Matching":
    # Import and run property matching page
    from pages.property_matching import show_property_matching
    show_property_matching()

elif page == "Lead Management":
    # Import and run lead management page
    from pages.lead_management import show_lead_management
    show_lead_management()

elif page == "Investment Calculator":
    # Import and run investment calculator page
    from pages.investment_calculator import show_investment_calculator
    show_investment_calculator()
    
elif page == "Marketing Generator":
    # Import and run marketing generator page
    from pages.marketing_generator import show_marketing_generator
    show_marketing_generator()
    
elif page == "Settings":
    # Import and run settings page
    from pages.settings import show_settings
    show_settings()

# Footer
st.sidebar.markdown("---")
current_year = datetime.now().year
st.sidebar.info(f"© {current_year} AI-Powered Real Estate Analytics Dashboard")

# Add beta mode toggle
st.sidebar.markdown("---")
beta_mode = st.sidebar.checkbox("Enable Beta Features", value=False)

if beta_mode:
    st.sidebar.info("""
    **Beta Features Enabled:**
    - AI Chatbot for personalized property recommendations
    - Hyperlocal market predictions
    - Advanced investment risk analysis
    """)
