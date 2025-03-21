import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.database import get_market_trends
from utils.visualization import plot_market_trends, plot_city_comparison
from utils.prediction import forecast_market_trends
import numpy as np

def show_india_market_insights():
    """
    Display insights specifically for the Indian real estate market
    """
    st.title("Indian Real Estate Market Insights")
    
    st.markdown("""
    This page provides detailed analytics and insights into the Indian real estate market,
    covering major metropolitan areas and emerging markets across the country.
    """)
    
    # Get Indian market trend data from the database
    indian_cities = [
        "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai",
        "Kolkata", "Pune", "Ahmedabad", "Gurgaon", "Noida"
    ]
    
    # Fetch market trends for Indian cities
    indian_trends = get_market_trends(location=None, start_date=None, end_date=None)
    indian_trends = pd.DataFrame(indian_trends)
    
    # Filter for Indian cities only
    if not indian_trends.empty:
        indian_trends = indian_trends[indian_trends['country'] == 'India']
        
        if not indian_trends.empty:
            # Indian market overview section
            st.header("Indian Real Estate Market Overview")
            
            # Create tabs for different views
            tab1, tab2, tab3, tab4 = st.tabs([
                "Market Trends", "City Comparison", "Price Analysis", "Investment Hotspots"
            ])
            
            with tab1:
                st.subheader("Price Trends Across Major Indian Cities")
                
                # Filter for specific cities if needed
                selected_cities = st.multiselect(
                    "Select Cities", 
                    options=sorted(indian_trends['city'].unique()),
                    default=sorted(indian_trends['city'].unique())[:5]
                )
                
                if selected_cities:
                    city_trends = indian_trends[indian_trends['city'].isin(selected_cities)]
                    
                    # Plot median price trends
                    st.subheader("Median Property Prices (Historical)")
                    fig = px.line(
                        city_trends.sort_values('date'), 
                        x='date', 
                        y='median_price',
                        color='city',
                        title="Median Property Prices Over Time",
                        labels={"median_price": "Median Price (USD)", "date": "Date", "city": "City"}
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Plot year-over-year appreciation rates
                    st.subheader("Annual Appreciation Rates")
                    fig = px.line(
                        city_trends.sort_values('date'), 
                        x='date', 
                        y='year_over_year_change',
                        color='city',
                        title="Year-over-Year Price Changes",
                        labels={"year_over_year_change": "YoY Change (%)", "date": "Date", "city": "City"}
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Price forecast for selected cities
                    st.subheader("12-Month Price Forecast")
                    
                    # Create a forecast for each selected city
                    for city in selected_cities:
                        city_data = city_trends[city_trends['city'] == city].sort_values('date')
                        if len(city_data) > 6:  # Need enough data for forecasting
                            forecast = forecast_market_trends(city_data, forecast_months=12)
                            
                            # Combine historical and forecast data
                            historical = city_data[['date', 'median_price']].rename(
                                columns={'median_price': 'price'}
                            )
                            historical['type'] = 'Historical'
                            
                            forecast_df = forecast.rename(columns={'predicted_price': 'price'})
                            forecast_df['type'] = 'Forecast'
                            
                            combined = pd.concat([historical, forecast_df])
                            
                            # Create forecast plot
                            fig = px.line(
                                combined.sort_values('date'), 
                                x='date', 
                                y='price',
                                color='type',
                                title=f"{city} - Price Forecast",
                                labels={"price": "Price (USD)", "date": "Date", "type": "Data Type"}
                            )
                            st.plotly_chart(fig, use_container_width=True)
            
            with tab2:
                st.subheader("City Comparison")
                
                # Latest median prices by city
                latest_data = indian_trends.sort_values('date').groupby('city').last().reset_index()
                
                # Price comparison
                fig = px.bar(
                    latest_data.sort_values('median_price', ascending=False),
                    x='city',
                    y='median_price',
                    title="Current Median Property Prices by City",
                    labels={"median_price": "Median Price (USD)", "city": "City"},
                    color='median_price',
                    color_continuous_scale=px.colors.sequential.Viridis
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Appreciation comparison
                fig = px.bar(
                    latest_data.sort_values('year_over_year_change', ascending=False),
                    x='city',
                    y='year_over_year_change',
                    title="Annual Appreciation Rate by City",
                    labels={"year_over_year_change": "Annual Appreciation (%)", "city": "City"},
                    color='year_over_year_change',
                    color_continuous_scale=px.colors.sequential.Reds
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Days on market comparison
                fig = px.bar(
                    latest_data.sort_values('days_on_market'),
                    x='city',
                    y='days_on_market',
                    title="Average Days on Market by City",
                    labels={"days_on_market": "Days on Market", "city": "City"},
                    color='days_on_market',
                    color_continuous_scale=px.colors.sequential.Blues_r
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with tab3:
                st.subheader("Price Analysis")
                
                # Price per square foot analysis
                latest_data = indian_trends.sort_values('date').groupby('city').last().reset_index()
                
                # Price per sq ft comparison
                fig = px.bar(
                    latest_data.sort_values('price_per_sqft', ascending=False),
                    x='city',
                    y='price_per_sqft',
                    title="Price per Square Foot by City",
                    labels={"price_per_sqft": "Price per Sq.Ft. (USD)", "city": "City"},
                    color='price_per_sqft',
                    color_continuous_scale=px.colors.sequential.Plasma
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Affordability index (made-up for demonstration)
                latest_data['affordability_index'] = 100 * (50000 / latest_data['median_price'])
                
                fig = px.bar(
                    latest_data.sort_values('affordability_index', ascending=False),
                    x='city',
                    y='affordability_index',
                    title="Affordability Index by City (Higher is More Affordable)",
                    labels={"affordability_index": "Affordability Index", "city": "City"},
                    color='affordability_index',
                    color_continuous_scale=px.colors.sequential.Greens
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with tab4:
                st.subheader("Investment Hotspots")
                
                # Calculate investment score based on appreciation, affordability and inventory
                latest_data = indian_trends.sort_values('date').groupby('city').last().reset_index()
                
                # Normalize values between 0 and 1
                latest_data['norm_appreciation'] = (latest_data['year_over_year_change'] - latest_data['year_over_year_change'].min()) / (latest_data['year_over_year_change'].max() - latest_data['year_over_year_change'].min())
                latest_data['norm_affordability'] = 1 - ((latest_data['median_price'] - latest_data['median_price'].min()) / (latest_data['median_price'].max() - latest_data['median_price'].min()))
                latest_data['norm_inventory'] = (latest_data['inventory'] - latest_data['inventory'].min()) / (latest_data['inventory'].max() - latest_data['inventory'].min())
                
                # Calculate investment score
                latest_data['investment_score'] = (
                    latest_data['norm_appreciation'] * 0.5 + 
                    latest_data['norm_affordability'] * 0.3 + 
                    latest_data['norm_inventory'] * 0.2
                ) * 100
                
                # Create investment score visualization
                fig = px.bar(
                    latest_data.sort_values('investment_score', ascending=False),
                    x='city',
                    y='investment_score',
                    title="Investment Potential Score",
                    labels={"investment_score": "Investment Score", "city": "City"},
                    color='investment_score',
                    color_continuous_scale=px.colors.sequential.Viridis
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Top investment cities
                st.subheader("Top Investment Markets")
                top_investment = latest_data.sort_values('investment_score', ascending=False).head(3)
                
                for i, (_, city) in enumerate(top_investment.iterrows()):
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        st.markdown(f"### {i+1}. {city['city']}")
                        st.metric("Investment Score", f"{city['investment_score']:.1f}")
                    
                    with col2:
                        st.markdown(f"**Annual Appreciation:** {city['year_over_year_change']:.1f}%")
                        st.markdown(f"**Median Price:** ${city['median_price']:,.0f}")
                        st.markdown(f"**Price/Sqft:** ${city['price_per_sqft']:.2f}")
                        st.markdown(f"**Days on Market:** {city['days_on_market']:.0f}")
                    
                    st.markdown("---")
        
        else:
            st.warning("No Indian market trend data available. Please initialize the database with Indian cities.")
    else:
        st.warning("No market trend data available. Please ensure the database has been properly initialized.")

    # Additional resources section
    st.header("Indian Real Estate Resources")
    st.markdown("""
    ### Key Market Indicators
    
    The Indian real estate market is influenced by several key factors:
    
    - **Economic Growth**: India's GDP growth directly impacts real estate demand
    - **Urbanization Rate**: Increasing urbanization drives housing demand in metropolitan areas
    - **Foreign Direct Investment**: FDI regulations and investments shape commercial real estate
    - **Government Policies**: RERA, Smart Cities Mission, and Housing for All initiatives
    - **Infrastructure Development**: Metro expansions, highways, and airports boost property values
    
    ### Regional Market Characteristics
    
    | Region | Market Characteristics | Property Types | Investment Outlook |
    |--------|------------------------|----------------|-------------------|
    | Mumbai | High prices, limited space | Apartments, Luxury Homes | Long-term appreciation |
    | Bangalore | Tech-driven demand | Apartments, Villas, Plots | Strong growth potential |
    | Delhi-NCR | Mixed development | Apartments, Builder Floors | Location-dependent returns |
    | Hyderabad | Expanding market | Apartments, Plots | Emerging investment hotspot |
    | Chennai | Stable market | Apartments, Individual Houses | Moderate, steady growth |
    | Pune | Affordable alternative to Mumbai | Apartments, Townships | Good rental yields |
    
    ### Regulatory Framework
    
    The Real Estate (Regulation and Development) Act, 2016 (RERA) has transformed the Indian real estate landscape by:
    
    - Increasing transparency
    - Protecting buyer interests
    - Standardizing practices
    - Ensuring timely delivery
    - Creating accountability
    """)

    # India-specific search prompt
    st.sidebar.markdown("### Search Indian Properties")
    st.sidebar.markdown("""
    Try searching for properties in Indian cities:
    - Mumbai, Maharashtra
    - Bangalore, Karnataka
    - Delhi, Delhi
    - Pune, Maharashtra
    - Hyderabad, Telangana
    """)