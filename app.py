import streamlit as st
import pandas as pd
import numpy as np
from utils.data_processing import load_sample_data
from utils.visualization import plot_market_trends, plot_property_distribution
import os

# Page configuration
st.set_page_config(
    page_title="Real Estate Analytics Dashboard",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables if they don't exist
if 'data' not in st.session_state:
    st.session_state.data = load_sample_data()

# Sidebar
st.sidebar.title("Real Estate Analytics")
st.sidebar.image("https://img.icons8.com/fluency/96/000000/real-estate.png", width=100)

# Navigation
page = st.sidebar.radio(
    "Navigate to",
    ["Dashboard", "Market Insights", "Property Analysis", "Investment Calculator"]
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
    st.title("Real Estate Analytics Dashboard")
    
    st.markdown("""
    Welcome to the AI-powered Real Estate Analytics Dashboard. This platform provides comprehensive market insights and 
    property analysis to help real estate professionals make data-driven decisions.
    
    ### Featured Insights:
    - Market trends and price forecasting
    - Property valuation analysis
    - Investment opportunity calculator
    - Neighborhood analytics
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
            
        # Market trends visualization
        st.subheader("Market Price Trends")
        fig = plot_market_trends(filtered_data)
        st.plotly_chart(fig, use_container_width=True)
        
        # Property distribution
        st.subheader("Property Distribution by Type")
        fig2 = plot_property_distribution(filtered_data)
        st.plotly_chart(fig2, use_container_width=True)
        
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

elif page == "Property Analysis":
    # Import and run property analysis page
    from pages.property_analysis import show_property_analysis
    show_property_analysis(filtered_data)

elif page == "Investment Calculator":
    # Import and run investment calculator page
    from pages.investment_calculator import show_investment_calculator
    show_investment_calculator()

# Footer
st.sidebar.markdown("---")
st.sidebar.info("© 2023 Real Estate Analytics Dashboard")
