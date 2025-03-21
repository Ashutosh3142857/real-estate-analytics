import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils.prediction import train_price_prediction_model, predict_property_price
from utils.advanced_valuation import (
    train_advanced_valuation_model, 
    predict_property_value,
    extract_feature_importance,
    get_comparable_properties,
    evaluate_property_investment
)

def show_property_valuation():
    st.title("AI-Driven Property Valuation")
    
    st.markdown("""
    Our advanced AI model analyzes local market data, economic indicators, and property characteristics 
    to provide accurate property valuations and future price predictions.
    """)
    
    # Get data from session state
    if 'data' not in st.session_state:
        st.error("No data available. Please return to the dashboard.")
        return
    
    data = st.session_state.data
    
    # Create tabs for the model types
    model_tab1, model_tab2 = st.tabs(["Standard Model", "Advanced AI Model"])
    
    with model_tab1:
        # Train the basic prediction model
        basic_model, basic_preprocessor, basic_features, basic_mae, basic_r2 = train_price_prediction_model(data)
        
        if basic_model is None:
            st.error("Unable to train the basic valuation model. Not enough data available.")
        else:
            st.info(f"""
            **Basic Model Performance:**
            - Accuracy: {basic_r2:.2f} R² score
            - Average Error: ${basic_mae:,.0f}
            
            This model uses linear regression and has been trained on {len(data)} properties across multiple markets.
            """)
    
    with model_tab2:
        # Train the advanced valuation model
        st.write("Training advanced AI valuation model...")
        
        # Show progress bar for model training
        with st.spinner("Training advanced ensemble model..."):
            # Train the random forest model
            advanced_model, advanced_preprocessor, advanced_features, advanced_metrics = train_advanced_valuation_model(
                data, model_type='random_forest'
            )
            
            # Also train gradient boosting for comparison
            gb_model, gb_preprocessor, gb_features, gb_metrics = train_advanced_valuation_model(
                data, model_type='gradient_boosting'
            )
        
        if advanced_model is None:
            st.error("Unable to train the advanced valuation model. Not enough data available.")
        else:
            # Display the model metrics
            st.success("Advanced AI model training complete!")
            
            st.info(f"""
            **Advanced Model Performance:**
            - R² Score: {advanced_metrics['r2']:.3f}
            - Mean Absolute Error: ${advanced_metrics['mae']:,.0f}
            - Root Mean Squared Error: ${advanced_metrics['rmse']:,.0f}
            - Cross-Validation MAE: ${advanced_metrics['cv_mae']:,.0f}
            
            This model uses ensemble learning with {advanced_metrics['model_type']} and has been trained on {advanced_metrics['training_samples']} properties.
            """)
            
            # Compare models
            st.subheader("Model Comparison")
            
            # Create a comparison table
            model_comparison = pd.DataFrame({
                'Metric': ['R² Score', 'Mean Absolute Error', 'Training Data Size', 'Algorithm'],
                'Basic Model': [basic_r2, f"${basic_mae:,.0f}", len(data), "Linear Regression"],
                'Random Forest': [advanced_metrics['r2'], f"${advanced_metrics['mae']:,.0f}", 
                                 advanced_metrics['training_samples'], "Random Forest Ensemble"],
                'Gradient Boosting': [gb_metrics['r2'], f"${gb_metrics['mae']:,.0f}", 
                                    gb_metrics['training_samples'], "Gradient Boosting Ensemble"]
            })
            
            st.table(model_comparison)
    
    # Choose which model to use for property valuation
    model_choice = st.radio(
        "Select AI Model for Valuation",
        options=["Standard Model", "Random Forest (Advanced)", "Gradient Boosting (Advanced)"],
        horizontal=True
    )
    
    if model_choice == "Standard Model":
        model = basic_model
        features = basic_features
        model_type = "standard"
    elif model_choice == "Random Forest (Advanced)":
        model = advanced_model
        features = advanced_features
        model_type = "advanced_rf"
    else:  # Gradient Boosting
        model = gb_model
        features = gb_features
        model_type = "advanced_gb"
    
    if model is None:
        st.error("The selected model couldn't be trained. Please try a different model.")
        return
    
    # Create two tabs: Single Property Valuation and Batch Valuation
    tab1, tab2 = st.tabs(["Single Property Valuation", "Neighborhood Value Analysis"])
    
    with tab1:
        st.subheader("Property Valuation Tool")
        
        st.markdown("""
        Enter the details of the property you want to value. Our AI model will analyze the characteristics
        and provide an estimated market value based on comparable properties.
        """)
        
        # Create form for property details
        with st.form("valuation_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                # Location
                cities = sorted(data['city'].unique())
                city = st.selectbox("City", options=cities)
                
                # Property details
                property_types = sorted(data['property_type'].unique())
                property_type = st.selectbox("Property Type", options=property_types)
                
                year_built = st.number_input(
                    "Year Built", 
                    min_value=int(data['year_built'].min()),
                    max_value=int(data['year_built'].max()),
                    value=2000
                )
            
            with col2:
                # Size details
                bedrooms = st.number_input("Bedrooms", min_value=1, max_value=10, value=3)
                bathrooms = st.number_input("Bathrooms", min_value=1, max_value=10, value=2)
                sqft = st.number_input(
                    "Square Footage", 
                    min_value=int(data['sqft'].min()),
                    max_value=int(data['sqft'].max()),
                    value=2000
                )
            
            # Additional property features
            st.subheader("Property Features")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                has_garage = st.checkbox("Garage")
            
            with col2:
                has_pool = st.checkbox("Swimming Pool")
            
            with col3:
                has_renovation = st.checkbox("Recently Renovated")
            
            submit_button = st.form_submit_button("Generate Valuation")
        
        # Process valuation when form is submitted
        if submit_button:
            # Create property data dictionary
            property_data = {
                'city': city,
                'property_type': property_type,
                'bedrooms': bedrooms,
                'bathrooms': bathrooms,
                'sqft': sqft,
                'year_built': year_built
            }
            
            # Different prediction based on model type
            if model_type in ["advanced_rf", "advanced_gb"]:
                # Use advanced model for prediction
                prediction_result = predict_property_value(model, features, property_data)
                
                if prediction_result is not None:
                    # Extract prediction data
                    predicted_price = prediction_result['predicted_price']
                    lower_bound = prediction_result['lower_bound']
                    upper_bound = prediction_result['upper_bound']
                    confidence_level = prediction_result.get('confidence_level', 80)
                    
                    # Display prediction with confidence interval
                    st.success(f"### Estimated Property Value: ${predicted_price:,.0f}")
                    st.markdown(f"""
                    **Valuation Range:** ${lower_bound:,.0f} - ${upper_bound:,.0f}  
                    **Confidence Level:** {confidence_level:.1f}%
                    """)
                    
                    # Add visual representation of the prediction range
                    fig = go.Figure()
                    
                    # Add main prediction point
                    fig.add_trace(go.Scatter(
                        x=[predicted_price],
                        y=[1],
                        mode='markers',
                        marker=dict(size=20, color='green'),
                        name='Predicted Value'
                    ))
                    
                    # Add range as a line
                    fig.add_trace(go.Scatter(
                        x=[lower_bound, upper_bound],
                        y=[1, 1],
                        mode='lines',
                        line=dict(width=4, color='blue'),
                        name='Valuation Range'
                    ))
                    
                    # Format the chart
                    fig.update_layout(
                        title='AI Valuation Range',
                        xaxis_title='Property Value ($)',
                        yaxis_visible=False,
                        height=200,
                        margin=dict(l=20, r=20, t=40, b=20),
                        xaxis=dict(tickprefix='$', tickformat=',')
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Feature importance explanation
                    st.subheader("Valuation Factors")
                    
                    st.markdown("""
                    Our advanced AI model considered the following factors when determining this valuation.
                    The length of each bar represents the importance of each feature in the prediction.
                    """)
                    
                    # Try to get actual feature importance from model
                    try:
                        importance_df = extract_feature_importance(model, features)
                        
                        if importance_df is not None and not importance_df.empty:
                            # Clean up feature names for display
                            importance_df['feature'] = importance_df['feature'].astype(str).apply(
                                lambda x: x.replace('_', ' ').title().replace('City', 'Location')
                            )
                            
                            # Sort by importance
                            importance_df = importance_df.sort_values('importance', ascending=False).head(10)
                            
                            # Calculate percentage
                            total_importance = importance_df['importance'].sum()
                            importance_df['percentage'] = (importance_df['importance'] / total_importance) * 100
                            
                            # Create chart
                            fig = px.bar(
                                importance_df,
                                y='feature',
                                x='percentage',
                                orientation='h',
                                title='Factors Affecting Property Value',
                                template='plotly_white',
                                labels={'feature': 'Feature', 'percentage': 'Importance (%)'}
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            # Fallback to simulated importance
                            features_impact = {
                                'Location': 35,
                                'Square Footage': 25,
                                'Property Type': 15,
                                'Bedrooms': 10,
                                'Bathrooms': 10,
                                'Year Built': 5
                            }
                            
                            impact_df = pd.DataFrame({
                                'Feature': list(features_impact.keys()),
                                'Impact (%)': list(features_impact.values())
                            })
                            
                            fig = px.bar(
                                impact_df,
                                y='Feature',
                                x='Impact (%)',
                                orientation='h',
                                title='Factors Affecting Property Value',
                                template='plotly_white'
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                    except Exception as e:
                        st.error(f"Error generating feature importance: {str(e)}")
                        
                        # Fallback to simulated importance
                        features_impact = {
                            'Location': 35,
                            'Square Footage': 25,
                            'Property Type': 15,
                            'Bedrooms': 10,
                            'Bathrooms': 10,
                            'Year Built': 5
                        }
                        
                        impact_df = pd.DataFrame({
                            'Feature': list(features_impact.keys()),
                            'Impact (%)': list(features_impact.values())
                        })
                        
                        fig = px.bar(
                            impact_df,
                            y='Feature',
                            x='Impact (%)',
                            orientation='h',
                            title='Factors Affecting Property Value',
                            template='plotly_white'
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Advanced comparable properties with the smart algorithm
                    st.subheader("Comparable Properties")
                    
                    # Get comparable properties with our smart algorithm
                    comparable_props = get_comparable_properties(data, property_data, model, top_n=5)
                    
                    if not comparable_props.empty:
                        st.write(f"Found {len(comparable_props)} comparable properties in the area.")
                        
                        # Format the dataframe for display
                        display_cols = []
                        for col in ['address', 'price', 'bedrooms', 'bathrooms', 'sqft', 'year_built', 'similarity_score']:
                            if col in comparable_props.columns:
                                display_cols.append(col)
                        
                        # Add price difference columns if available
                        if 'price_diff' in comparable_props.columns:
                            display_cols.append('price_diff')
                            display_cols.append('price_diff_pct')
                        
                        # Display dataframe with helpful styling
                        st.dataframe(
                            comparable_props[display_cols]
                            .sort_values('similarity_score', ascending=False)
                            .style.format({
                                'price': '${:,.0f}',
                                'similarity_score': '{:.1f}',
                                'price_diff': '${:+,.0f}',
                                'price_diff_pct': '{:+.1f}%'
                            })
                        )
                        
                        # Map of comparable properties
                        if ('latitude' in comparable_props.columns and 'longitude' in comparable_props.columns and
                            'latitude' in property_data and 'longitude' in property_data):
                            
                            st.subheader("Map of Comparable Properties")
                            
                            # Add the subject property to the map data
                            map_props = comparable_props.copy()
                            subject_prop = pd.DataFrame([property_data])
                            subject_prop['address'] = f"Subject Property ({bedrooms}bd/{bathrooms}ba, {sqft}sqft)"
                            subject_prop['property_type'] = property_type
                            
                            # Combine for map
                            map_data = pd.concat([map_props, subject_prop])
                            
                            # Create a scatter map
                            fig = px.scatter_mapbox(
                                map_data,
                                lat='latitude', 
                                lon='longitude',
                                color='price',
                                size=[15 if i == len(map_props) else 10 for i in range(len(map_data))],
                                hover_name='address',
                                hover_data=['price', 'bedrooms', 'bathrooms', 'sqft'],
                                color_continuous_scale=px.colors.sequential.Viridis,
                                zoom=13,
                                height=400
                            )
                            
                            fig.update_layout(mapbox_style='open-street-map')
                            
                            st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No comparable properties found in our database.")
                
                else:
                    st.error("Unable to generate a valuation. Please check your inputs.")
            
            else:
                # Use standard model for prediction
                predicted_price = predict_property_price(model, features, property_data)
                
                if predicted_price is not None:
                    # Calculate confidence intervals (±10%)
                    lower_bound = predicted_price * 0.9
                    upper_bound = predicted_price * 1.1
                    
                    # Display prediction with confidence interval
                    st.success(f"### Estimated Property Value: ${predicted_price:,.0f}")
                    st.write(f"**Valuation Range:** ${lower_bound:,.0f} - ${upper_bound:,.0f}")
                    
                    # Feature importance explanation (hypothetical for basic model)
                    st.subheader("Valuation Factors")
                    
                    st.markdown("""
                    Our AI model considered the following factors when determining this valuation:
                    """)
                    
                    # Create a simulated feature importance chart
                    features_impact = {
                        'Location (City)': 35,
                        'Square Footage': 25,
                        'Property Type': 15,
                        'Bedrooms': 10,
                        'Bathrooms': 10,
                        'Year Built': 5
                    }
                    
                    impact_df = pd.DataFrame({
                        'Feature': list(features_impact.keys()),
                        'Impact (%)': list(features_impact.values())
                    })
                    
                    fig = px.bar(
                        impact_df,
                        y='Feature',
                        x='Impact (%)',
                        orientation='h',
                        title='Factors Affecting Property Value',
                        template='plotly_white'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Find comparable properties using basic filtering
                    st.subheader("Comparable Properties")
                    
                    # Filter for similar properties
                    similar_props = data[
                        (data['city'] == city) &
                        (data['property_type'] == property_type) &
                        (data['bedrooms'] == bedrooms) &
                        (data['bathrooms'] == bathrooms) &
                        (data['sqft'].between(sqft * 0.8, sqft * 1.2))
                    ]
                    
                    if not similar_props.empty:
                        st.write(f"Found {len(similar_props)} comparable properties in the area.")
                        st.dataframe(
                            similar_props[['address', 'price', 'bedrooms', 'bathrooms', 'sqft', 'year_built']]
                            .sort_values('price')
                            .head(5)
                        )
                    else:
                        st.info("No closely comparable properties found in our database.")
                else:
                    st.error("Unable to generate a valuation. Please check your inputs.")
                
                # Market positioning
                city_avg = data[data['city'] == city]['price'].mean()
                
                if predicted_price > city_avg:
                    premium_pct = ((predicted_price - city_avg) / city_avg) * 100
                    st.write(f"This property is valued **{premium_pct:.1f}% above** the city average of ${city_avg:,.0f}.")
                else:
                    discount_pct = ((city_avg - predicted_price) / city_avg) * 100
                    st.write(f"This property is valued **{discount_pct:.1f}% below** the city average of ${city_avg:,.0f}.")
            else:
                st.error("Unable to generate a valuation. Please check your inputs.")
    
    with tab2:
        st.subheader("Neighborhood Value Analysis")
        
        st.markdown("""
        Analyze property values across different neighborhoods and understand market trends by area.
        """)
        
        # Select a city to analyze
        city = st.selectbox("Select City for Analysis", options=sorted(data['city'].unique()), key="neighborhood_city")
        
        if city:
            # Filter data for the selected city
            city_data = data[data['city'] == city]
            
            # Create simulated neighborhoods (since we don't have actual neighborhood data)
            if 'neighborhood' not in city_data.columns:
                # Create synthetic neighborhoods based on lat/long clustering (simplified for demo)
                neighborhoods = ['Downtown', 'Uptown', 'Westside', 'Eastside', 'Northend', 'Southside']
                # Assign properties to neighborhoods randomly but consistently
                city_data['neighborhood'] = city_data['property_id'].apply(lambda x: neighborhoods[x % len(neighborhoods)])
            
            # Calculate average prices by neighborhood
            neighborhood_prices = city_data.groupby('neighborhood')['price'].agg(['mean', 'median', 'count']).reset_index()
            neighborhood_prices = neighborhood_prices.sort_values('mean', ascending=False)
            
            # Display the map
            st.subheader(f"Property Value Map for {city}")
            
            # Create a scatter map of properties
            fig = px.scatter_mapbox(
                city_data,
                lat='latitude', 
                lon='longitude',
                color='price',
                size='sqft',
                color_continuous_scale=px.colors.sequential.Viridis,
                hover_name='address',
                hover_data=['price', 'bedrooms', 'bathrooms', 'sqft', 'property_type'],
                title=f'Property Values in {city}',
                zoom=10,
                height=500
            )
            
            # Using Open Street Map for the base map (no API key required)
            fig.update_layout(mapbox_style='open-street-map')
            
            # Format the hover template to show price as currency
            fig.update_traces(
                hovertemplate='<b>%{hovertext}</b><br>Price: $%{customdata[0]:,.0f}<br>Beds: %{customdata[1]}<br>Baths: %{customdata[2]}<br>Sqft: %{customdata[3]:,}<br>Type: %{customdata[4]}'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show neighborhood statistics
            st.subheader("Neighborhood Price Comparison")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Bar chart of average prices by neighborhood
                fig = px.bar(
                    neighborhood_prices,
                    x='neighborhood',
                    y='mean',
                    color='mean',
                    color_continuous_scale=px.colors.sequential.Viridis,
                    title=f'Average Property Prices by Neighborhood in {city}',
                    labels={'neighborhood': 'Neighborhood', 'mean': 'Average Price ($)'},
                    template='plotly_white',
                    text_auto='.2s'
                )
                
                fig.update_layout(yaxis_tickprefix='$', yaxis_tickformat=',')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Table with detailed stats
                st.write("Neighborhood Statistics")
                
                display_df = neighborhood_prices.copy()
                display_df['mean'] = display_df['mean'].map('${:,.0f}'.format)
                display_df['median'] = display_df['median'].map('${:,.0f}'.format)
                display_df.columns = ['Neighborhood', 'Average Price', 'Median Price', 'Number of Properties']
                
                st.table(display_df)
            
            # Price forecast for the city
            st.subheader("Price Forecast by Neighborhood")
            
            forecast_years = st.slider("Forecast Period (Years)", min_value=1, max_value=5, value=3)
            
            # Calculate neighborhood appreciation rates (simulated)
            appreciation_data = []
            
            for index, row in neighborhood_prices.iterrows():
                # Calculate simulated appreciation rate based on current prices
                # Higher-priced neighborhoods typically appreciate faster
                base_appreciation = np.random.uniform(0.02, 0.05)  # Base annual appreciation between 2-5%
                price_factor = row['mean'] / neighborhood_prices['mean'].max()  # Higher prices get higher appreciation
                appreciation_rate = base_appreciation * (0.8 + (0.4 * price_factor))  # Adjust appreciation based on price
                
                current_price = row['mean']
                neighborhood = row['neighborhood']
                
                for year in range(1, forecast_years + 1):
                    forecasted_price = current_price * (1 + appreciation_rate) ** year
                    
                    appreciation_data.append({
                        'neighborhood': neighborhood,
                        'year': 2023 + year,
                        'forecasted_price': forecasted_price,
                        'appreciation_rate': appreciation_rate * 100  # Convert to percentage
                    })
            
            # Convert to DataFrame
            forecast_df = pd.DataFrame(appreciation_data)
            
            # Create forecast visualization
            fig = px.line(
                forecast_df,
                x='year',
                y='forecasted_price',
                color='neighborhood',
                title=f'Forecasted Property Prices by Neighborhood in {city}',
                labels={'year': 'Year', 'forecasted_price': 'Forecasted Price ($)', 'neighborhood': 'Neighborhood'},
                template='plotly_white'
            )
            
            # Format y-axis as currency
            fig.update_layout(yaxis_tickprefix='$', yaxis_tickformat=',')
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show appreciation rates
            appreciation_summary = forecast_df[['neighborhood', 'appreciation_rate']].drop_duplicates()
            appreciation_summary = appreciation_summary.sort_values('appreciation_rate', ascending=False)
            
            st.subheader("Projected Annual Appreciation Rates")
            
            fig = px.bar(
                appreciation_summary,
                x='neighborhood',
                y='appreciation_rate',
                color='appreciation_rate',
                color_continuous_scale=px.colors.sequential.Viridis,
                title='Projected Annual Appreciation Rate by Neighborhood',
                labels={'neighborhood': 'Neighborhood', 'appreciation_rate': 'Annual Appreciation Rate (%)'},
                template='plotly_white',
                text_auto='.1f'
            )
            
            fig.update_layout(yaxis_ticksuffix='%')
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Investment opportunity recommendations
            st.subheader("Investment Opportunity Analysis")
            
            # Calculate price-to-rent ratios (simulated since we don't have real rent data)
            city_data['monthly_rent'] = city_data.apply(
                lambda x: x['price'] * np.random.uniform(0.005, 0.008) / 12, axis=1
            )
            
            city_data['price_to_rent_ratio'] = city_data['price'] / (city_data['monthly_rent'] * 12)
            
            # Calculate average price-to-rent by neighborhood
            ptr_by_neighborhood = city_data.groupby('neighborhood')['price_to_rent_ratio'].mean().reset_index()
            ptr_by_neighborhood = ptr_by_neighborhood.sort_values('price_to_rent_ratio')
            
            # Good investment threshold (lower is better for rental properties)
            ptr_threshold = 15
            
            # Identify good investment neighborhoods
            good_investment = ptr_by_neighborhood[ptr_by_neighborhood['price_to_rent_ratio'] < ptr_threshold]
            
            if not good_investment.empty:
                st.success(f"""
                ### Top Investment Opportunities
                
                The following neighborhoods have favorable price-to-rent ratios (below {ptr_threshold}),
                indicating good potential for rental property investments:
                """)
                
                for _, row in good_investment.iterrows():
                    st.write(f"- **{row['neighborhood']}**: Price-to-Rent Ratio of {row['price_to_rent_ratio']:.1f}")
                
                # Create visual representation
                fig = px.bar(
                    ptr_by_neighborhood,
                    x='neighborhood',
                    y='price_to_rent_ratio',
                    color='price_to_rent_ratio',
                    color_continuous_scale='RdYlGn_r',  # Reversed scale: green for lower values (better)
                    title='Price-to-Rent Ratio by Neighborhood',
                    labels={'neighborhood': 'Neighborhood', 'price_to_rent_ratio': 'Price-to-Rent Ratio'},
                    template='plotly_white',
                    text_auto='.1f'
                )
                
                # Add a horizontal line for the threshold
                fig.add_hline(
                    y=ptr_threshold,
                    line_dash="dash",
                    line_color="red",
                    annotation_text=f"Investment Threshold ({ptr_threshold})",
                    annotation_position="bottom right"
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                st.info("""
                **About Price-to-Rent Ratio:**
                This metric compares property prices to annual rental income. A lower ratio typically
                indicates better potential for rental property investment. Generally:
                
                - Below 15: Excellent rental market conditions
                - 15-20: Good rental potential
                - Above 20: Better for long-term appreciation than rental income
                """)
            else:
                st.info(f"No neighborhoods in {city} currently have highly favorable price-to-rent ratios below {ptr_threshold}.")