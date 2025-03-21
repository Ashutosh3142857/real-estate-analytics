import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from utils.visualization import plot_price_vs_sqft, plot_price_distribution, plot_price_heatmap
from utils.prediction import train_price_prediction_model, predict_property_price

def show_property_analysis(filtered_data):
    st.title("Property Analysis")
    
    st.markdown("""
    This page provides detailed analysis of property characteristics and their relationship to price.
    Use the filters in the sidebar to customize the data view.
    """)
    
    if filtered_data.empty:
        st.warning("No data available with the current filters. Please adjust your selection.")
        return
    
    # Property distribution by type and price
    st.subheader("Property Price Distribution")
    price_dist_fig = plot_price_distribution(filtered_data)
    st.plotly_chart(price_dist_fig, use_container_width=True)
    
    # Price vs Square Footage analysis
    st.subheader("Price vs. Square Footage Analysis")
    price_sqft_fig = plot_price_vs_sqft(filtered_data)
    st.plotly_chart(price_sqft_fig, use_container_width=True)
    
    # Price by bedrooms and bathrooms
    st.subheader("Price by Bedrooms and Bathrooms")
    heatmap_fig = plot_price_heatmap(filtered_data)
    st.plotly_chart(heatmap_fig, use_container_width=True)
    
    # Year built analysis
    st.subheader("Property Age Analysis")
    
    # Group by decade
    filtered_data['decade'] = (filtered_data['year_built'] // 10) * 10
    decade_data = filtered_data.groupby('decade')['price'].agg(['mean', 'count']).reset_index()
    decade_data = decade_data.sort_values('decade')
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Price by decade
        fig = px.bar(
            decade_data,
            x='decade',
            y='mean',
            title='Average Price by Decade Built',
            labels={'decade': 'Decade Built', 'mean': 'Average Price ($)'},
            template='plotly_white',
            text_auto='.2s'
        )
        
        fig.update_layout(yaxis_tickprefix='$', yaxis_tickformat=',')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Count by decade
        fig = px.bar(
            decade_data,
            x='decade',
            y='count',
            title='Number of Properties by Decade Built',
            labels={'decade': 'Decade Built', 'count': 'Number of Properties'},
            template='plotly_white',
            text_auto=True
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Property price prediction
    st.header("Property Price Predictor")
    
    st.markdown("""
    Use this tool to estimate property prices based on characteristics.
    Our AI model analyzes local market data to generate price estimates.
    """)
    
    # Train the prediction model
    model, preprocessor, features, mae, r2 = train_price_prediction_model(filtered_data)
    
    if model is not None:
        # Display model metrics
        st.info(f"""
        **Model Performance Metrics:**
        - Mean Absolute Error: ${mae:,.0f}
        - R² Score: {r2:.2f}
        """)
        
        # Create form for user input
        with st.form("property_prediction_form"):
            st.subheader("Enter Property Details")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Get available cities
                available_cities = sorted(filtered_data['city'].unique())
                city = st.selectbox("City", options=available_cities)
                
                # Get available property types
                property_types = sorted(filtered_data['property_type'].unique())
                property_type = st.selectbox("Property Type", options=property_types)
            
            with col2:
                # Get range of bedrooms and bathrooms
                min_beds, max_beds = int(filtered_data['bedrooms'].min()), int(filtered_data['bedrooms'].max())
                bedrooms = st.number_input("Bedrooms", min_value=min_beds, max_value=max_beds, value=3)
                
                min_baths, max_baths = int(filtered_data['bathrooms'].min()), int(filtered_data['bathrooms'].max())
                bathrooms = st.number_input("Bathrooms", min_value=min_baths, max_value=max_baths, value=2)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Square footage
                min_sqft, max_sqft = int(filtered_data['sqft'].min()), int(filtered_data['sqft'].max())
                sqft = st.number_input("Square Footage", min_value=min_sqft, max_value=max_sqft, value=2000)
            
            with col2:
                # Year built
                min_year, max_year = int(filtered_data['year_built'].min()), int(filtered_data['year_built'].max())
                year_built = st.number_input("Year Built", min_value=min_year, max_value=max_year, value=2000)
            
            submit_button = st.form_submit_button("Predict Price")
        
        # Make prediction when form is submitted
        if submit_button:
            property_data = {
                'city': city,
                'property_type': property_type,
                'bedrooms': bedrooms,
                'bathrooms': bathrooms,
                'sqft': sqft,
                'year_built': year_built
            }
            
            predicted_price = predict_property_price(model, features, property_data)
            
            if predicted_price is not None:
                # Display prediction
                st.success(f"### Estimated Property Price: ${predicted_price:,.0f}")
                
                # Show similar properties
                st.subheader("Similar Properties")
                
                # Filter similar properties
                similar = filtered_data[
                    (filtered_data['city'] == city) &
                    (filtered_data['property_type'] == property_type) &
                    (filtered_data['bedrooms'] == bedrooms) &
                    (filtered_data['bathrooms'] == bathrooms) &
                    (filtered_data['sqft'].between(sqft * 0.8, sqft * 1.2))
                ]
                
                if not similar.empty:
                    st.dataframe(
                        similar[['address', 'city', 'price', 'bedrooms', 'bathrooms', 'sqft', 'year_built']]
                        .sort_values(by='price')
                        .head(5)
                    )
                else:
                    st.info("No similar properties found in the database.")
                
                # Price comparison
                city_avg = filtered_data[filtered_data['city'] == city]['price'].mean()
                price_diff = predicted_price - city_avg
                price_diff_pct = (price_diff / city_avg) * 100
                
                # Market positioning
                if price_diff > 0:
                    st.info(f"This property is **${price_diff:,.0f} ({price_diff_pct:.1f}%)** above the average price in {city}.")
                else:
                    st.info(f"This property is **${abs(price_diff):,.0f} ({abs(price_diff_pct):.1f}%)** below the average price in {city}.")
            else:
                st.error("Unable to generate prediction. Please check your inputs.")
    else:
        st.warning("Not enough data available to build a reliable prediction model. Please adjust your filters.")
    
    # Property comparison tool
    st.header("Property Comparison Tool")
    
    st.markdown("""
    Compare properties side by side to analyze value and characteristics.
    """)
    
    if not filtered_data.empty and len(filtered_data) >= 2:
        # Get property IDs
        property_ids = filtered_data['property_id'].unique()
        
        col1, col2 = st.columns(2)
        
        with col1:
            property1 = st.selectbox(
                "Select First Property",
                options=property_ids,
                format_func=lambda x: f"ID: {x} - {filtered_data[filtered_data['property_id'] == x]['address'].values[0]}"
            )
        
        with col2:
            # Filter out the first property
            remaining_ids = [pid for pid in property_ids if pid != property1]
            property2 = st.selectbox(
                "Select Second Property",
                options=remaining_ids,
                format_func=lambda x: f"ID: {x} - {filtered_data[filtered_data['property_id'] == x]['address'].values[0]}"
            )
        
        # Get property data
        prop1_data = filtered_data[filtered_data['property_id'] == property1].iloc[0]
        prop2_data = filtered_data[filtered_data['property_id'] == property2].iloc[0]
        
        # Create comparison table
        comparison_data = {
            'Feature': ['Price', 'Price/Sqft', 'Bedrooms', 'Bathrooms', 'Square Footage', 
                        'Year Built', 'Days on Market', 'Property Type', 'City'],
            'Property 1': [
                f"${prop1_data['price']:,.0f}",
                f"${prop1_data['price']/prop1_data['sqft']:.2f}",
                prop1_data['bedrooms'],
                prop1_data['bathrooms'],
                f"{prop1_data['sqft']:,}",
                prop1_data['year_built'],
                prop1_data['days_on_market'],
                prop1_data['property_type'],
                prop1_data['city']
            ],
            'Property 2': [
                f"${prop2_data['price']:,.0f}",
                f"${prop2_data['price']/prop2_data['sqft']:.2f}",
                prop2_data['bedrooms'],
                prop2_data['bathrooms'],
                f"{prop2_data['sqft']:,}",
                prop2_data['year_built'],
                prop2_data['days_on_market'],
                prop2_data['property_type'],
                prop2_data['city']
            ]
        }
        
        comparison_df = pd.DataFrame(comparison_data)
        
        # Display comparison
        st.table(comparison_df)
        
        # Calculate and display difference
        price_diff = prop1_data['price'] - prop2_data['price']
        price_diff_pct = (price_diff / prop2_data['price']) * 100
        
        if price_diff > 0:
            st.info(f"Property 1 is **${price_diff:,.0f} ({price_diff_pct:.1f}%)** more expensive than Property 2.")
        else:
            st.info(f"Property 1 is **${abs(price_diff):,.0f} ({abs(price_diff_pct):.1f}%)** less expensive than Property 2.")
        
        # Value analysis
        price_per_sqft1 = prop1_data['price'] / prop1_data['sqft']
        price_per_sqft2 = prop2_data['price'] / prop2_data['sqft']
        
        if price_per_sqft1 < price_per_sqft2:
            st.success(f"Property 1 has better value in terms of price per square foot (${price_per_sqft1:.2f} vs ${price_per_sqft2:.2f}).")
        else:
            st.success(f"Property 2 has better value in terms of price per square foot (${price_per_sqft2:.2f} vs ${price_per_sqft1:.2f}).")
    else:
        st.warning("Need at least 2 properties in the dataset to use the comparison tool.")
