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
    
    # Check if we have the year_built data
    if 'year_built' in filtered_data.columns and not filtered_data['year_built'].isna().all():
        try:
            # Drop rows with missing year_built
            year_data = filtered_data.dropna(subset=['year_built']).copy()
            
            if not year_data.empty:
                # Group by decade - ensure year_built is numeric
                year_data['year_built'] = pd.to_numeric(year_data['year_built'], errors='coerce')
                year_data = year_data.dropna(subset=['year_built'])
                
                # Only proceed if we still have data
                if not year_data.empty:
                    year_data['decade'] = (year_data['year_built'] // 10) * 10
                    decade_data = year_data.groupby('decade')['price'].agg(['mean', 'count']).reset_index()
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
                else:
                    st.warning("Not enough valid year data to analyze property age distribution.")
            else:
                st.warning("No valid year built data available for analysis.")
        except Exception as e:
            st.warning(f"Error analyzing property age data: {str(e)}")
    else:
        st.warning("Year built data not available for the current selection.")
    
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
                try:
                    # Get available cities
                    available_cities = sorted(filtered_data['city'].unique().tolist())
                    # Remove any NaN values
                    available_cities = [city for city in available_cities if isinstance(city, str) or not pd.isna(city)]
                    if available_cities:
                        city = st.selectbox("City", options=available_cities)
                    else:
                        st.error("No valid city data available.")
                        return
                    
                    # Get available property types
                    property_types = sorted(filtered_data['property_type'].unique().tolist())
                    # Remove any NaN values
                    property_types = [pt for pt in property_types if isinstance(pt, str) or not pd.isna(pt)]
                    if property_types:
                        property_type = st.selectbox("Property Type", options=property_types)
                    else:
                        st.error("No valid property type data available.")
                        return
                except Exception as e:
                    st.error(f"Error loading property categories: {str(e)}")
                    return
            
            with col2:
                try:
                    # Get valid bedroom values (filter out NaN and invalid)
                    bed_values = filtered_data['bedrooms'].dropna()
                    if len(bed_values) > 0:
                        min_beds = max(1, int(bed_values.min()))
                        max_beds = min(10, int(bed_values.max()))  # Limit to reasonable values
                        default_beds = min(3, max_beds)  # Default value capped at 3 or max available
                        bedrooms = st.number_input("Bedrooms", min_value=min_beds, max_value=max_beds, value=default_beds)
                    else:
                        st.error("No valid bedroom data available.")
                        return
                    
                    # Get valid bathroom values (filter out NaN and invalid)
                    bath_values = filtered_data['bathrooms'].dropna()
                    if len(bath_values) > 0:
                        min_baths = max(1, int(bath_values.min()))
                        max_baths = min(10, int(bath_values.max()))  # Limit to reasonable values
                        default_baths = min(2, max_baths)  # Default value capped at 2 or max available
                        bathrooms = st.number_input("Bathrooms", min_value=min_baths, max_value=max_baths, value=default_baths)
                    else:
                        st.error("No valid bathroom data available.")
                        return
                except Exception as e:
                    st.error(f"Error loading property room data: {str(e)}")
                    return
            
            col1, col2 = st.columns(2)
            
            with col1:
                try:
                    # Get valid square footage values (filter out NaN, zero, and negative)
                    sqft_values = filtered_data['sqft'][filtered_data['sqft'] > 0].dropna()
                    if len(sqft_values) > 0:
                        min_sqft = max(100, int(sqft_values.min()))
                        max_sqft = min(10000, int(sqft_values.max()))  # Limit to reasonable values
                        default_sqft = min(2000, max_sqft)  # Default value capped at 2000 or max available
                        sqft = st.number_input("Square Footage", min_value=min_sqft, max_value=max_sqft, value=default_sqft)
                    else:
                        st.error("No valid square footage data available.")
                        return
                except Exception as e:
                    st.error(f"Error loading square footage data: {str(e)}")
                    return
            
            with col2:
                try:
                    # Get valid year built values (filter out NaN and future years)
                    current_year = 2025  # Hard-coded current year
                    year_values = filtered_data['year_built'][filtered_data['year_built'] <= current_year].dropna()
                    if len(year_values) > 0:
                        min_year = max(1900, int(year_values.min()))  # Limit to reasonable values
                        max_year = min(current_year, int(year_values.max()))
                        default_year = min(2000, max_year)  # Default value capped at 2000 or max available
                        year_built = st.number_input("Year Built", min_value=min_year, max_value=max_year, value=default_year)
                    else:
                        st.error("No valid year built data available.")
                        return
                except Exception as e:
                    st.error(f"Error loading year built data: {str(e)}")
                    return
            
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
                
                try:
                    # Filter similar properties with relaxed criteria to ensure we find some matches
                    # Start with strict criteria
                    similar = filtered_data[
                        (filtered_data['city'] == city) &
                        (filtered_data['property_type'] == property_type) &
                        (filtered_data['bedrooms'] == bedrooms) &
                        (filtered_data['bathrooms'] == bathrooms) &
                        (filtered_data['sqft'].between(sqft * 0.8, sqft * 1.2))
                    ]
                    
                    # If we don't find any properties, relax the criteria
                    if similar.empty:
                        similar = filtered_data[
                            (filtered_data['city'] == city) &
                            (filtered_data['property_type'] == property_type) &
                            (filtered_data['bedrooms'].between(bedrooms-1, bedrooms+1)) &
                            (filtered_data['sqft'].between(sqft * 0.7, sqft * 1.3))
                        ]
                    
                    # If we still don't find any, further relax criteria
                    if similar.empty:
                        similar = filtered_data[
                            (filtered_data['city'] == city) &
                            (filtered_data['bedrooms'].between(bedrooms-1, bedrooms+1))
                        ]
                    
                    # Display properties if we found any
                    if not similar.empty:
                        # Only include columns that exist in the dataframe
                        display_columns = []
                        for col in ['address', 'city', 'price', 'bedrooms', 'bathrooms', 'sqft', 'year_built']:
                            if col in similar.columns:
                                display_columns.append(col)
                        
                        if display_columns:
                            st.dataframe(
                                similar[display_columns]
                                .sort_values(by='price')
                                .head(5)
                            )
                        else:
                            st.info("Found similar properties but couldn't display details due to missing columns.")
                    else:
                        st.info("No similar properties found in the database.")
                    
                    # Price comparison
                    city_properties = filtered_data[filtered_data['city'] == city]
                    if not city_properties.empty and 'price' in city_properties.columns:
                        city_prices = city_properties['price'].dropna()
                        if len(city_prices) > 0:
                            city_avg = city_prices.mean()
                            price_diff = predicted_price - city_avg
                            price_diff_pct = (price_diff / city_avg) * 100
                            
                            # Market positioning
                            if price_diff > 0:
                                st.info(f"This property is **${price_diff:,.0f} ({price_diff_pct:.1f}%)** above the average price in {city}.")
                            else:
                                st.info(f"This property is **${abs(price_diff):,.0f} ({abs(price_diff_pct):.1f}%)** below the average price in {city}.")
                        else:
                            st.info(f"No price data available for {city} to make a comparison.")
                    else:
                        st.info(f"No price data available for {city} to make a comparison.")
                    
                except Exception as e:
                    st.warning(f"Error finding similar properties: {str(e)}")
            else:
                st.error("Unable to generate prediction. Please check your inputs.")
    else:
        st.warning("Not enough data available to build a reliable prediction model. Please adjust your filters.")
    
    # Property comparison tool
    st.header("Property Comparison Tool")
    
    st.markdown("""
    Compare properties side by side to analyze value and characteristics.
    """)
    
    # Check if the dataset has the necessary columns and at least 2 properties
    required_comparison_columns = ['property_id', 'address', 'price', 'sqft', 'bedrooms', 'bathrooms', 
                                 'year_built', 'days_on_market', 'property_type', 'city']
    
    if (not filtered_data.empty and len(filtered_data) >= 2 and 
        all(col in filtered_data.columns for col in required_comparison_columns)):
        
        try:
            # Get property IDs
            property_ids = filtered_data['property_id'].unique()
            
            # Make sure we have valid address data
            valid_addresses = True
            for pid in property_ids:
                address_values = filtered_data[filtered_data['property_id'] == pid]['address'].values
                if len(address_values) == 0 or pd.isna(address_values[0]):
                    valid_addresses = False
                    break
            
            if valid_addresses:
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
                prop1_data = filtered_data[filtered_data['property_id'] == property1]
                prop2_data = filtered_data[filtered_data['property_id'] == property2]
                
                if not prop1_data.empty and not prop2_data.empty:
                    prop1_data = prop1_data.iloc[0]
                    prop2_data = prop2_data.iloc[0]
                    
                    # Ensure all required numeric fields are available and valid
                    if (all(field in prop1_data and field in prop2_data for field in ['price', 'sqft']) and
                        not pd.isna(prop1_data['price']) and not pd.isna(prop1_data['sqft']) and
                        not pd.isna(prop2_data['price']) and not pd.isna(prop2_data['sqft']) and
                        prop1_data['sqft'] > 0 and prop2_data['sqft'] > 0):
                        
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
                        st.warning("Missing or invalid price/square footage data for comparison.")
                else:
                    st.warning("Error retrieving property data for comparison.")
            else:
                st.warning("Some properties are missing address information needed for comparison.")
        except Exception as e:
            st.warning(f"Error in property comparison tool: {str(e)}")
    else:
        missing_cols = [col for col in required_comparison_columns if col not in filtered_data.columns]
        if missing_cols:
            st.warning(f"Missing data columns required for comparison: {', '.join(missing_cols)}")
        else:
            st.warning("Need at least 2 properties in the dataset to use the comparison tool.")
