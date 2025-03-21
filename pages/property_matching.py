import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import random
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity

def show_property_matching():
    st.title("AI-Powered Property Matching")
    
    st.markdown("""
    Our intelligent property matching system goes beyond basic filters to understand your unique preferences,
    lifestyle needs, and priorities to find your ideal home.
    """)
    
    # Get data from session state
    if 'data' not in st.session_state:
        st.error("No property data available. Please return to the dashboard.")
        return
    
    data = st.session_state.data
    
    # Create tabs for different matching features
    tab1, tab2, tab3 = st.tabs(["Preference Matching", "Lifestyle Matching", "Investment Potential"])
    
    with tab1:
        show_preference_matching(data)
    
    with tab2:
        show_lifestyle_matching(data)
    
    with tab3:
        show_investment_matching(data)

def show_preference_matching(data):
    st.subheader("Smart Property Preference Matching")
    
    st.markdown("""
    Tell us about your ideal property, and our AI will find the best matches based on your preferences.
    Adjust the importance of each factor to personalize your results.
    """)
    
    # Property preference form
    with st.form("property_preference_form"):
        # Location preferences
        st.subheader("Location")
        
        cities = sorted(data['city'].unique())
        selected_cities = st.multiselect(
            "Preferred Cities/Areas",
            options=cities,
            default=cities[:3] if len(cities) >= 3 else cities
        )
        
        # Property details
        st.subheader("Property Details")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            min_price = int(data['price'].min())
            max_price = int(data['price'].max())
            price_range = st.slider(
                "Price Range ($)",
                min_value=min_price,
                max_value=max_price,
                value=(min_price, int(min_price + (max_price - min_price) * 0.3))
            )
            
            property_types = sorted(data['property_type'].unique())
            selected_property_types = st.multiselect(
                "Property Type",
                options=property_types,
                default=property_types[:2] if len(property_types) >= 2 else property_types
            )
        
        with col2:
            min_beds = int(data['bedrooms'].min())
            max_beds = int(data['bedrooms'].max())
            bedrooms = st.slider(
                "Bedrooms",
                min_value=min_beds,
                max_value=max_beds,
                value=(min_beds, min(min_beds + 2, max_beds))
            )
            
            min_baths = int(data['bathrooms'].min())
            max_baths = int(data['bathrooms'].max())
            bathrooms = st.slider(
                "Bathrooms",
                min_value=min_baths,
                max_value=max_baths,
                value=(min_baths, min(min_baths + 2, max_baths))
            )
        
        with col3:
            min_sqft = int(data['sqft'].min())
            max_sqft = int(data['sqft'].max())
            sqft_range = st.slider(
                "Square Footage",
                min_value=min_sqft,
                max_value=max_sqft,
                value=(min_sqft, int(min_sqft + (max_sqft - min_sqft) * 0.3))
            )
            
            min_year = int(data['year_built'].min())
            max_year = int(data['year_built'].max())
            year_built = st.slider(
                "Year Built",
                min_value=min_year,
                max_value=max_year,
                value=(min_year, max_year)
            )
        
        # Preference weights
        st.subheader("Feature Importance")
        st.write("Adjust the importance of each factor in finding your ideal property:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            price_weight = st.slider("Price", 1, 10, 8)
            location_weight = st.slider("Location", 1, 10, 9)
            property_type_weight = st.slider("Property Type", 1, 10, 7)
        
        with col2:
            size_weight = st.slider("Size (Sqft)", 1, 10, 6)
            beds_baths_weight = st.slider("Beds/Baths", 1, 10, 8)
            age_weight = st.slider("Property Age", 1, 10, 4)
        
        # Must-have features
        st.subheader("Must-Have Features")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            garage = st.checkbox("Garage")
        
        with col2:
            pool = st.checkbox("Swimming Pool")
        
        with col3:
            yard = st.checkbox("Large Yard")
        
        with col4:
            recent_renovation = st.checkbox("Recently Renovated")
        
        submit_button = st.form_submit_button("Find Matching Properties")
    
    # Generate matches on submit
    if submit_button:
        # Apply basic filtering
        filtered_data = data.copy()
        
        if selected_cities:
            filtered_data = filtered_data[filtered_data['city'].isin(selected_cities)]
        
        filtered_data = filtered_data[
            (filtered_data['price'] >= price_range[0]) &
            (filtered_data['price'] <= price_range[1]) &
            (filtered_data['bedrooms'] >= bedrooms[0]) &
            (filtered_data['bedrooms'] <= bedrooms[1]) &
            (filtered_data['bathrooms'] >= bathrooms[0]) &
            (filtered_data['bathrooms'] <= bathrooms[1]) &
            (filtered_data['sqft'] >= sqft_range[0]) &
            (filtered_data['sqft'] <= sqft_range[1]) &
            (filtered_data['year_built'] >= year_built[0]) &
            (filtered_data['year_built'] <= year_built[1])
        ]
        
        if selected_property_types:
            filtered_data = filtered_data[filtered_data['property_type'].isin(selected_property_types)]
        
        # Apply advanced matching
        if not filtered_data.empty:
            # Create feature vectors for matching
            feature_weights = {
                'price': price_weight,
                'city': location_weight,
                'property_type': property_type_weight,
                'sqft': size_weight,
                'bedrooms': beds_baths_weight,
                'bathrooms': beds_baths_weight,
                'year_built': age_weight
            }
            
            # Create a preference vector
            preference = {
                'price': (price_range[0] + price_range[1]) / 2,
                'sqft': (sqft_range[0] + sqft_range[1]) / 2,
                'bedrooms': (bedrooms[0] + bedrooms[1]) / 2,
                'bathrooms': (bathrooms[0] + bathrooms[1]) / 2,
                'year_built': (year_built[0] + year_built[1]) / 2
            }
            
            # Calculate match scores
            matches = calculate_match_scores(filtered_data, preference, feature_weights, 
                                           selected_cities, selected_property_types)
            
            # Display matches
            st.subheader("Your Top Matching Properties")
            
            if not matches.empty:
                # Show number of matches
                st.success(f"Found {len(matches)} properties matching your criteria!")
                
                # Display top matches as cards
                show_property_cards(matches.head(5))
                
                # Create a match distribution plot
                st.subheader("Match Score Distribution")
                
                fig = px.histogram(
                    matches,
                    x='match_score',
                    nbins=20,
                    title='Distribution of Property Match Scores',
                    labels={'match_score': 'Match Score (%)'},
                    template='plotly_white',
                    color_discrete_sequence=['#3366CC']
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Display all matches in a table
                st.subheader("All Matching Properties")
                
                st.dataframe(
                    matches[['address', 'city', 'price', 'bedrooms', 'bathrooms', 
                           'sqft', 'property_type', 'year_built', 'match_score']]
                    .sort_values('match_score', ascending=False)
                )
            else:
                st.warning("No properties match all your criteria. Try adjusting your preferences.")
        else:
            st.warning("No properties match your basic criteria. Please broaden your search parameters.")

def show_lifestyle_matching(data):
    st.subheader("Lifestyle-Based Property Matching")
    
    st.markdown("""
    Tell us about your lifestyle preferences, and we'll find properties that align with your ideal living situation.
    Our AI considers factors beyond the property itself, such as commute times, nearby amenities, and neighborhood characteristics.
    """)
    
    # Lifestyle preference form
    with st.form("lifestyle_preference_form"):
        # Work and commute
        st.subheader("Work & Commute")
        
        col1, col2 = st.columns(2)
        
        with col1:
            commute_importance = st.select_slider(
                "Commute Importance",
                options=["Not Important", "Somewhat Important", "Important", "Very Important", "Essential"],
                value="Important"
            )
            
            max_commute = st.slider("Maximum Commute Time (minutes)", 10, 90, 30)
        
        with col2:
            work_location = st.selectbox(
                "Work Location (City/Area)",
                options=["Work from Home"] + sorted(data['city'].unique().tolist())
            )
            
            commute_method = st.selectbox(
                "Primary Commute Method",
                options=["Driving", "Public Transit", "Walking/Biking", "Mixed"]
            )
        
        # Lifestyle priorities
        st.subheader("Lifestyle Priorities")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            dining_out = st.select_slider(
                "Dining & Nightlife",
                options=["Not Important", "Somewhat Important", "Important", "Very Important", "Essential"],
                value="Somewhat Important"
            )
            
            shopping = st.select_slider(
                "Shopping Access",
                options=["Not Important", "Somewhat Important", "Important", "Very Important", "Essential"],
                value="Somewhat Important"
            )
        
        with col2:
            outdoor_activities = st.select_slider(
                "Outdoor Activities",
                options=["Not Important", "Somewhat Important", "Important", "Very Important", "Essential"],
                value="Important"
            )
            
            arts_culture = st.select_slider(
                "Arts & Culture",
                options=["Not Important", "Somewhat Important", "Important", "Very Important", "Essential"],
                value="Somewhat Important"
            )
        
        with col3:
            quiet_neighborhood = st.select_slider(
                "Quiet Neighborhood",
                options=["Not Important", "Somewhat Important", "Important", "Very Important", "Essential"],
                value="Important"
            )
            
            family_friendly = st.select_slider(
                "Family-Friendly",
                options=["Not Important", "Somewhat Important", "Important", "Very Important", "Essential"],
                value="Somewhat Important"
            )
        
        # Family needs
        st.subheader("Family & Education")
        
        col1, col2 = st.columns(2)
        
        with col1:
            school_importance = st.select_slider(
                "School Quality Importance",
                options=["Not Important", "Somewhat Important", "Important", "Very Important", "Essential"],
                value="Somewhat Important"
            )
            
            has_children = st.radio(
                "Children in Household?",
                options=["No", "Yes - Young Children", "Yes - School Age", "Yes - College Age"],
                horizontal=True
            )
        
        with col2:
            safety_importance = st.select_slider(
                "Neighborhood Safety",
                options=["Not Important", "Somewhat Important", "Important", "Very Important", "Essential"],
                value="Very Important"
            )
            
            pets = st.multiselect(
                "Pets in Household",
                options=["None", "Dogs", "Cats", "Other"],
                default=["None"]
            )
        
        # Additional lifestyle factors
        st.subheader("Additional Factors")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            privacy = st.slider("Privacy Importance", 1, 10, 5)
        
        with col2:
            noise_tolerance = st.slider("Noise Tolerance", 1, 10, 5)
        
        with col3:
            social_life = st.slider("Social Life Importance", 1, 10, 5)
        
        submit_button = st.form_submit_button("Find Lifestyle Matches")
    
    # Generate lifestyle matches on submit
    if submit_button:
        # For demonstration, simulate neighborhood data that would normally come from external APIs
        if 'neighborhood_data' not in st.session_state:
            st.session_state.neighborhood_data = generate_neighborhood_data(data)
        
        neighborhood_data = st.session_state.neighborhood_data
        
        # Merge property and neighborhood data
        merged_data = pd.merge(
            data,
            neighborhood_data,
            on='city',
            how='left'
        )
        
        # Convert lifestyle preferences to scores
        importance_map = {
            "Not Important": 1,
            "Somewhat Important": 3,
            "Important": 5,
            "Very Important": 8,
            "Essential": 10
        }
        
        lifestyle_weights = {
            'dining_score': importance_map[dining_out],
            'shopping_score': importance_map[shopping],
            'outdoor_score': importance_map[outdoor_activities],
            'arts_score': importance_map[arts_culture],
            'quiet_score': 11 - importance_map[quiet_neighborhood],  # Inverse (higher = quieter)
            'family_score': importance_map[family_friendly],
            'school_score': importance_map[school_importance],
            'safety_score': importance_map[safety_importance],
            'commute_time': 10 if work_location == "Work from Home" else importance_map[commute_importance]
        }
        
        # Calculate lifestyle match scores
        matches = calculate_lifestyle_scores(merged_data, lifestyle_weights, work_location, max_commute)
        
        # Display matches
        st.subheader("Your Top Lifestyle-Matched Properties")
        
        if not matches.empty:
            # Show number of matches
            st.success(f"Found {len(matches)} properties matching your lifestyle preferences!")
            
            # Display top matches with neighborhood information
            for i, (_, prop) in enumerate(matches.head(5).iterrows()):
                with st.container():
                    col1, col2 = st.columns([2, 3])
                    
                    with col1:
                        # Property image placeholder (in a real app, this would be actual property images)
                        st.image(
                            "https://img.icons8.com/fluency/96/000000/real-estate.png", 
                            width=150,
                            caption=f"Property {i+1}"
                        )
                    
                    with col2:
                        st.markdown(f"### {prop['address']}, {prop['city']}")
                        st.markdown(f"**${prop['price']:,.0f}** • {prop['bedrooms']} bed • {prop['bathrooms']} bath • {prop['sqft']:,} sqft")
                        st.markdown(f"**Lifestyle Match:** {prop['lifestyle_score']:.0f}%")
                        
                        # Lifestyle highlights
                        highlights = []
                        
                        if prop['dining_score'] >= 7:
                            highlights.append("Great dining & nightlife")
                        
                        if prop['outdoor_score'] >= 7:
                            highlights.append("Excellent outdoor recreation")
                        
                        if prop['school_score'] >= 7 and has_children in ["Yes - Young Children", "Yes - School Age"]:
                            highlights.append("Top-rated schools")
                        
                        if prop['quiet_score'] >= 7 and importance_map[quiet_neighborhood] >= 5:
                            highlights.append("Quiet neighborhood")
                        
                        if prop['safety_score'] >= 8:
                            highlights.append("Very safe area")
                        
                        if work_location != "Work from Home" and prop['commute_time'] <= max_commute:
                            highlights.append(f"{prop['commute_time']} min commute to {work_location}")
                        
                        st.markdown("**Highlights:** " + ", ".join(highlights))
                
                st.markdown("---")
            
            # Neighborhood comparison
            st.subheader("Neighborhood Comparison")
            
            # Prepare data for radar chart
            top_neighborhoods = matches.head(3)['city'].unique()
            radar_data = []
            
            categories = ['Dining', 'Shopping', 'Outdoor', 'Arts', 'Quiet', 'Family', 'Schools', 'Safety']
            
            for neighborhood in top_neighborhoods:
                neighborhood_scores = neighborhood_data[neighborhood_data['city'] == neighborhood].iloc[0]
                
                radar_data.append({
                    'category': 'Dining',
                    'value': neighborhood_scores['dining_score'],
                    'neighborhood': neighborhood
                })
                radar_data.append({
                    'category': 'Shopping',
                    'value': neighborhood_scores['shopping_score'],
                    'neighborhood': neighborhood
                })
                radar_data.append({
                    'category': 'Outdoor',
                    'value': neighborhood_scores['outdoor_score'],
                    'neighborhood': neighborhood
                })
                radar_data.append({
                    'category': 'Arts',
                    'value': neighborhood_scores['arts_score'],
                    'neighborhood': neighborhood
                })
                radar_data.append({
                    'category': 'Quiet',
                    'value': neighborhood_scores['quiet_score'],
                    'neighborhood': neighborhood
                })
                radar_data.append({
                    'category': 'Family',
                    'value': neighborhood_scores['family_score'],
                    'neighborhood': neighborhood
                })
                radar_data.append({
                    'category': 'Schools',
                    'value': neighborhood_scores['school_score'],
                    'neighborhood': neighborhood
                })
                radar_data.append({
                    'category': 'Safety',
                    'value': neighborhood_scores['safety_score'],
                    'neighborhood': neighborhood
                })
            
            radar_df = pd.DataFrame(radar_data)
            
            fig = px.line_polar(
                radar_df, 
                r='value', 
                theta='category', 
                color='neighborhood', 
                line_close=True,
                title='Neighborhood Characteristic Comparison',
                template='plotly_white'
            )
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 10]
                    )
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Display all matches in a sortable table
            st.subheader("All Lifestyle-Matched Properties")
            
            # Prepare display DataFrame
            display_df = matches[['address', 'city', 'price', 'bedrooms', 'bathrooms', 
                                'sqft', 'property_type', 'lifestyle_score']]
            
            # Add neighborhood characteristics
            display_df['Neighborhood Type'] = matches.apply(
                lambda x: neighborhood_type(x), axis=1
            )
            
            display_df['Commute'] = matches['commute_time'].apply(
                lambda x: f"{x} min" if work_location != "Work from Home" else "N/A"
            )
            
            st.dataframe(
                display_df.sort_values('lifestyle_score', ascending=False)
            )
        else:
            st.warning("No properties match your lifestyle preferences. Try adjusting your criteria.")

def show_investment_matching(data):
    st.subheader("Investment Property Matching")
    
    st.markdown("""
    Find investment properties that match your financial goals and investment strategy.
    Our AI analyzes potential returns, cash flow, and appreciation to identify the best opportunities.
    """)
    
    # Investment preferences form
    with st.form("investment_preference_form"):
        # Investment strategy
        st.subheader("Investment Strategy")
        
        investment_strategy = st.radio(
            "Primary Investment Strategy",
            options=["Cash Flow (Rental Income)", "Appreciation (Long-term Growth)", "Balanced Approach"],
            horizontal=True
        )
        
        investment_horizon = st.slider("Investment Horizon (years)", 1, 30, 5)
        
        # Financial parameters
        st.subheader("Financial Parameters")
        
        col1, col2 = st.columns(2)
        
        with col1:
            min_price = int(data['price'].min())
            max_price = int(data['price'].max())
            budget_range = st.slider(
                "Investment Budget ($)",
                min_value=min_price,
                max_value=max_price,
                value=(min_price, int(min_price + (max_price - min_price) * 0.3))
            )
            
            down_payment_pct = st.slider("Down Payment (%)", 10, 100, 25, 5)
        
        with col2:
            target_cap_rate = st.slider("Minimum Cap Rate (%)", 3.0, 15.0, 6.0, 0.5)
            
            min_cash_flow = st.slider("Minimum Monthly Cash Flow ($)", 0, 3000, 200, 50)
        
        # Property preferences
        st.subheader("Property Preferences")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            cities = sorted(data['city'].unique())
            selected_cities = st.multiselect(
                "Target Markets",
                options=cities,
                default=cities[:3] if len(cities) >= 3 else cities
            )
        
        with col2:
            property_types = sorted(data['property_type'].unique())
            selected_property_types = st.multiselect(
                "Property Types",
                options=property_types,
                default=["Single Family", "Multi-Family"] if "Multi-Family" in property_types else property_types[:2]
            )
        
        with col3:
            min_beds = st.slider("Minimum Bedrooms", 1, 5, 2)
            min_baths = st.slider("Minimum Bathrooms", 1, 4, 1)
        
        # Risk tolerance
        st.subheader("Risk Profile")
        
        risk_tolerance = st.select_slider(
            "Risk Tolerance",
            options=["Very Conservative", "Conservative", "Moderate", "Aggressive", "Very Aggressive"],
            value="Moderate"
        )
        
        submit_button = st.form_submit_button("Find Investment Opportunities")
    
    # Generate investment matches on submit
    if submit_button:
        # Filter basic property criteria
        filtered_data = data.copy()
        
        if selected_cities:
            filtered_data = filtered_data[filtered_data['city'].isin(selected_cities)]
        
        filtered_data = filtered_data[
            (filtered_data['price'] >= budget_range[0]) &
            (filtered_data['price'] <= budget_range[1]) &
            (filtered_data['bedrooms'] >= min_beds) &
            (filtered_data['bathrooms'] >= min_baths)
        ]
        
        if selected_property_types:
            filtered_data = filtered_data[filtered_data['property_type'].isin(selected_property_types)]
        
        # Generate investment analysis
        if not filtered_data.empty:
            # In a real app, you'd use actual rental and market data
            # For this demo, we'll simulate realistic rental yields and appreciation rates
            filtered_data = generate_investment_metrics(filtered_data, down_payment_pct, investment_horizon)
            
            # Apply investment strategy filters
            if investment_strategy == "Cash Flow (Rental Income)":
                # Prioritize cash flow
                filtered_data['investment_score'] = filtered_data.apply(
                    lambda x: (x['cash_flow_score'] * 0.6) + 
                              (x['cap_rate_score'] * 0.3) + 
                              (x['appreciation_score'] * 0.1),
                    axis=1
                )
            elif investment_strategy == "Appreciation (Long-term Growth)":
                # Prioritize appreciation
                filtered_data['investment_score'] = filtered_data.apply(
                    lambda x: (x['cash_flow_score'] * 0.2) + 
                              (x['cap_rate_score'] * 0.2) + 
                              (x['appreciation_score'] * 0.6),
                    axis=1
                )
            else:  # Balanced
                # Even weighting
                filtered_data['investment_score'] = filtered_data.apply(
                    lambda x: (x['cash_flow_score'] * 0.33) + 
                              (x['cap_rate_score'] * 0.33) + 
                              (x['appreciation_score'] * 0.34),
                    axis=1
                )
            
            # Apply risk tolerance filter
            risk_map = {
                "Very Conservative": 1,
                "Conservative": 2,
                "Moderate": 3,
                "Aggressive": 4,
                "Very Aggressive": 5
            }
            
            risk_level = risk_map[risk_tolerance]
            
            # For demonstration purposes, we'll consider properties with higher ROI but lower cap rates as more risky
            if risk_level <= 2:  # Conservative
                filtered_data = filtered_data[filtered_data['cap_rate'] >= target_cap_rate]
            elif risk_level == 3:  # Moderate
                filtered_data = filtered_data[filtered_data['cap_rate'] >= (target_cap_rate - 1)]
            # For aggressive investors, we keep all properties
            
            # Filter by cash flow
            if min_cash_flow > 0:
                filtered_data = filtered_data[filtered_data['monthly_cash_flow'] >= min_cash_flow]
            
            # Sort by investment score
            matches = filtered_data.sort_values('investment_score', ascending=False)
            
            # Display investment opportunities
            if not matches.empty:
                st.subheader("Top Investment Opportunities")
                
                # Show number of matches
                st.success(f"Found {len(matches)} potential investment properties matching your criteria!")
                
                # Display top investment properties
                for i, (_, prop) in enumerate(matches.head(5).iterrows()):
                    with st.container():
                        col1, col2 = st.columns([1, 2])
                        
                        with col1:
                            # Property image placeholder (in a real app, this would be actual property images)
                            st.image(
                                "https://img.icons8.com/fluency/96/000000/real-estate.png", 
                                width=100,
                                caption=f"Investment {i+1}"
                            )
                        
                        with col2:
                            st.markdown(f"### {prop['address']}, {prop['city']}")
                            st.markdown(f"**${prop['price']:,.0f}** • {prop['bedrooms']} bed • {prop['bathrooms']} bath • {prop['sqft']:,} sqft")
                            
                            # Key investment metrics
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("Cap Rate", f"{prop['cap_rate']:.2f}%")
                            
                            with col2:
                                st.metric("Cash Flow", f"${prop['monthly_cash_flow']:.0f}/mo")
                            
                            with col3:
                                st.metric("Cash-on-Cash ROI", f"{prop['cash_on_cash_return']:.2f}%")
                            
                            # ROI breakdown
                            st.progress(int(prop['investment_score']))
                            st.caption(f"Investment Score: {prop['investment_score']:.0f}%")
                    
                    st.markdown("---")
                
                # Investment return comparison
                st.subheader("Investment Return Comparison")
                
                # Prepare data for chart
                comparison_data = matches.head(10)[['address', 'city', 'cap_rate', 'cash_on_cash_return', 'total_roi', 'appreciation_rate']].copy()
                
                # Simplify address for display
                comparison_data['property'] = comparison_data.apply(
                    lambda x: f"{x['address'].split(' ')[0]} {x['city']}", axis=1
                )
                
                # Create a grouped bar chart
                fig = px.bar(
                    comparison_data,
                    x='property',
                    y=['cap_rate', 'cash_on_cash_return', 'total_roi'],
                    title='Return Metrics Comparison (Top 10 Properties)',
                    labels={
                        'property': 'Property',
                        'value': 'Return (%)',
                        'variable': 'Metric'
                    },
                    template='plotly_white',
                    barmode='group',
                    height=500
                )
                
                # Update names in legend
                fig.update_layout(
                    legend_title_text='Return Metric',
                    xaxis_tickangle=-45
                )
                
                fig.for_each_trace(lambda t: t.update(name = {
                    'cap_rate': 'Cap Rate (%)',
                    'cash_on_cash_return': 'Cash-on-Cash ROI (%)',
                    'total_roi': f'Total {investment_horizon}-Year ROI (%)'
                }[t.name]))
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Cash flow vs. appreciation scatter plot
                st.subheader("Cash Flow vs. Appreciation Analysis")
                
                fig = px.scatter(
                    matches.head(20),
                    x='monthly_cash_flow',
                    y='appreciation_rate',
                    size='price',
                    color='cap_rate',
                    hover_name='address',
                    hover_data=['city', 'property_type', 'bedrooms', 'bathrooms', 'price'],
                    title='Cash Flow vs. Appreciation Rate (Top 20 Properties)',
                    labels={
                        'monthly_cash_flow': 'Monthly Cash Flow ($)',
                        'appreciation_rate': 'Annual Appreciation Rate (%)',
                        'price': 'Price ($)',
                        'cap_rate': 'Cap Rate (%)'
                    },
                    template='plotly_white',
                    color_continuous_scale=px.colors.sequential.Viridis
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Risk-return analysis
                st.subheader("Risk-Return Analysis")
                
                # Create a simulated risk score based on cap rate and property characteristics
                matches['risk_score'] = 10 - matches['cap_rate_score']  # Inverse of cap rate score (lower cap rate = higher risk)
                
                # Adjust risk based on property type (multi-family typically less risky)
                matches.loc[matches['property_type'] == 'Multi-Family', 'risk_score'] -= 1
                
                # Ensure risk score is within 1-10 range
                matches['risk_score'] = matches['risk_score'].clip(1, 10)
                
                fig = px.scatter(
                    matches.head(20),
                    x='risk_score',
                    y='total_roi',
                    size='price',
                    color='investment_score',
                    hover_name='address',
                    hover_data=['city', 'property_type', 'cap_rate', 'monthly_cash_flow'],
                    title='Risk vs. Return Analysis (Top 20 Properties)',
                    labels={
                        'risk_score': 'Risk Level (1-10)',
                        'total_roi': f'Total {investment_horizon}-Year ROI (%)',
                        'price': 'Price ($)',
                        'investment_score': 'Investment Score'
                    },
                    template='plotly_white',
                    color_continuous_scale=px.colors.sequential.Viridis
                )
                
                # Add a diagonal reference line (efficient frontier concept)
                x_range = matches['risk_score'].max() - matches['risk_score'].min()
                y_range = matches['total_roi'].max() - matches['total_roi'].min()
                
                if x_range > 0 and y_range > 0:
                    slope = y_range / x_range
                    y_intercept = matches['total_roi'].min() - (slope * matches['risk_score'].min())
                    
                    x_values = [matches['risk_score'].min(), matches['risk_score'].max()]
                    y_values = [slope * x + y_intercept for x in x_values]
                    
                    fig.add_trace(
                        px.line(
                            x=x_values, 
                            y=y_values
                        ).data[0]
                    )
                
                # Add risk tolerance reference line
                risk_tolerance_value = 2 + (risk_level * 1.5)  # Scale 1-5 to meaningful range
                
                fig.add_vline(
                    x=risk_tolerance_value,
                    line_dash="dash",
                    line_color="red",
                    annotation_text=f"Risk Tolerance: {risk_tolerance}",
                    annotation_position="top"
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Show all investment properties in a table
                st.subheader("All Investment Opportunities")
                
                display_df = matches[[
                    'address', 'city', 'price', 'property_type', 'bedrooms', 'bathrooms',
                    'monthly_cash_flow', 'cap_rate', 'cash_on_cash_return', 'total_roi', 'investment_score'
                ]].copy()
                
                # Format values
                display_df['monthly_cash_flow'] = display_df['monthly_cash_flow'].map('${:,.0f}'.format)
                display_df['cap_rate'] = display_df['cap_rate'].map('{:.2f}%'.format)
                display_df['cash_on_cash_return'] = display_df['cash_on_cash_return'].map('{:.2f}%'.format)
                display_df['total_roi'] = display_df['total_roi'].map('{:.2f}%'.format)
                display_df['investment_score'] = display_df['investment_score'].map('{:.0f}'.format)
                display_df['price'] = display_df['price'].map('${:,.0f}'.format)
                
                # Rename columns
                display_df.columns = [
                    'Address', 'City', 'Price', 'Type', 'Beds', 'Baths',
                    'Monthly Cash Flow', 'Cap Rate', 'Cash-on-Cash ROI', f'{investment_horizon}-Year ROI', 'Score'
                ]
                
                st.dataframe(display_df)
            else:
                st.warning("No properties match your investment criteria. Try adjusting your parameters.")
        else:
            st.warning("No properties match your basic criteria. Please broaden your search parameters.")

def calculate_match_scores(data, preference, feature_weights, selected_cities, selected_property_types):
    """Calculate match scores based on user preferences"""
    # Copy the data to avoid modifying the original
    matches = data.copy()
    
    # Normalize numerical features for fair comparison
    scaler = MinMaxScaler()
    
    # Fit scaler on the entire dataset to get proper min/max ranges
    numerical_features = ['price', 'sqft', 'bedrooms', 'bathrooms', 'year_built']
    scaled_data = scaler.fit_transform(data[numerical_features])
    
    # Create a DataFrame with the scaled data
    scaled_df = pd.DataFrame(scaled_data, columns=numerical_features)
    
    # Get the scaled preference vector
    preference_vector = np.array([preference['price'], preference['sqft'], 
                                 preference['bedrooms'], preference['bathrooms'], 
                                 preference['year_built']])
    scaled_preference = scaler.transform([preference_vector])[0]
    
    # Calculate the distance for each numerical feature
    for i, feature in enumerate(numerical_features):
        # Calculate the absolute difference (distance) between property and preference
        scaled_df[f'{feature}_distance'] = abs(scaled_df[feature] - scaled_preference[i])
        
        # Invert the distance to get a similarity score (1 - distance)
        scaled_df[f'{feature}_score'] = 1 - scaled_df[f'{feature}_distance']
        
        # Apply the feature weight
        scaled_df[f'{feature}_weighted'] = scaled_df[f'{feature}_score'] * feature_weights[feature]
    
    # Calculate city match (binary: 1 if matches preference, 0 otherwise)
    matches['city_score'] = matches['city'].apply(lambda x: 1 if x in selected_cities else 0)
    matches['city_weighted'] = matches['city_score'] * feature_weights['city']
    
    # Calculate property type match (binary: 1 if matches preference, 0 otherwise)
    matches['property_type_score'] = matches['property_type'].apply(lambda x: 1 if x in selected_property_types else 0)
    matches['property_type_weighted'] = matches['property_type_score'] * feature_weights['property_type']
    
    # Calculate the overall match score
    # First get the individual weighted scores for numerical features
    for feature in numerical_features:
        matches[f'{feature}_weighted'] = scaled_df[f'{feature}_weighted']
    
    # Sum all weighted scores
    total_weight = sum(feature_weights.values())
    
    weighted_features = [f'{feature}_weighted' for feature in numerical_features] + ['city_weighted', 'property_type_weighted']
    
    matches['total_weighted_score'] = matches[weighted_features].sum(axis=1)
    
    # Calculate the percentage match
    matches['match_score'] = (matches['total_weighted_score'] / total_weight) * 100
    
    # Ensure the score is within 0-100 range
    matches['match_score'] = matches['match_score'].clip(0, 100)
    
    # Round to nearest integer
    matches['match_score'] = matches['match_score'].round().astype(int)
    
    # Sort by match score
    matches = matches.sort_values('match_score', ascending=False)
    
    return matches

def calculate_lifestyle_scores(data, lifestyle_weights, work_location, max_commute):
    """Calculate lifestyle match scores based on preferences"""
    matches = data.copy()
    
    # Calculate weighted scores for each lifestyle factor
    lifestyle_factors = list(lifestyle_weights.keys())
    total_weight = sum(lifestyle_weights.values())
    
    # Calculate weighted score for each factor
    for factor in lifestyle_factors:
        if factor != 'commute_time':  # Handle commute separately
            matches[f'{factor}_weighted'] = matches[factor] * lifestyle_weights[factor]
    
    # Special handling for commute
    if work_location == "Work from Home":
        matches['commute_weighted'] = lifestyle_weights['commute_time']  # Full score if working from home
    else:
        # Inverse score - lower commute time is better
        # Scale so that commute times <= max_commute get proportionally higher scores
        # and times > max_commute get proportionally lower scores
        matches['commute_factor'] = matches.apply(
            lambda x: max(0, (max_commute - x['commute_time']) / max_commute), axis=1
        )
        matches['commute_weighted'] = matches['commute_factor'] * lifestyle_weights['commute_time']
    
    # Sum all weighted factors
    weighted_factors = [f'{factor}_weighted' for factor in lifestyle_factors[:-1]] + ['commute_weighted']
    matches['total_weighted_score'] = matches[weighted_factors].sum(axis=1)
    
    # Calculate percentage match
    matches['lifestyle_score'] = (matches['total_weighted_score'] / total_weight) * 100
    
    # Ensure the score is within 0-100 range
    matches['lifestyle_score'] = matches['lifestyle_score'].clip(0, 100)
    
    # Round to nearest integer
    matches['lifestyle_score'] = matches['lifestyle_score'].round().astype(int)
    
    # Sort by lifestyle score
    matches = matches.sort_values('lifestyle_score', ascending=False)
    
    return matches

def generate_neighborhood_data(data):
    """Generate simulated neighborhood data for the cities in the dataset"""
    cities = data['city'].unique()
    neighborhood_data = []
    
    for city in cities:
        # Generate realistic but randomized scores
        if city in ['New York', 'Los Angeles', 'San Francisco', 'Chicago']:
            # Urban centers
            dining_score = np.random.uniform(7, 10)
            shopping_score = np.random.uniform(7, 10)
            outdoor_score = np.random.uniform(4, 8)
            arts_score = np.random.uniform(7, 10)
            quiet_score = np.random.uniform(2, 6)
            family_score = np.random.uniform(3, 7)
            school_score = np.random.uniform(5, 9)
            safety_score = np.random.uniform(4, 8)
        elif city in ['Houston', 'Phoenix', 'Dallas', 'San Diego']:
            # Suburban mix
            dining_score = np.random.uniform(5, 8)
            shopping_score = np.random.uniform(6, 9)
            outdoor_score = np.random.uniform(5, 9)
            arts_score = np.random.uniform(4, 8)
            quiet_score = np.random.uniform(5, 8)
            family_score = np.random.uniform(6, 9)
            school_score = np.random.uniform(6, 9)
            safety_score = np.random.uniform(6, 9)
        else:
            # Smaller cities
            dining_score = np.random.uniform(4, 7)
            shopping_score = np.random.uniform(4, 7)
            outdoor_score = np.random.uniform(6, 9)
            arts_score = np.random.uniform(3, 7)
            quiet_score = np.random.uniform(6, 9)
            family_score = np.random.uniform(7, 10)
            school_score = np.random.uniform(6, 9)
            safety_score = np.random.uniform(7, 10)
        
        # Generate commute times for each city (to all other cities)
        commute_times = {}
        for dest_city in cities:
            if dest_city == city:
                commute_times[dest_city] = 10  # Short commute within same city
            else:
                # Generate a realistic commute time based on city pair
                commute_times[dest_city] = np.random.randint(20, 90)
        
        neighborhood_data.append({
            'city': city,
            'dining_score': dining_score,
            'shopping_score': shopping_score,
            'outdoor_score': outdoor_score,
            'arts_score': arts_score,
            'quiet_score': quiet_score,
            'family_score': family_score,
            'school_score': school_score,
            'safety_score': safety_score,
            'commute_times': commute_times
        })
    
    # Convert to DataFrame
    df = pd.DataFrame(neighborhood_data)
    
    # Expand commute times into separate columns for each destination city
    for city in cities:
        df[f'commute_to_{city}'] = df['commute_times'].apply(lambda x: x.get(city, 60))
    
    # Drop the dictionary column
    df = df.drop(columns=['commute_times'])
    
    return df

def neighborhood_type(row):
    """Determine neighborhood type based on scores"""
    if row['dining_score'] >= 7 and row['arts_score'] >= 7:
        return "Urban/Cultural"
    elif row['outdoor_score'] >= 7 and row['quiet_score'] >= 7:
        return "Suburban/Outdoor"
    elif row['family_score'] >= 7 and row['school_score'] >= 7:
        return "Family-Friendly"
    elif row['dining_score'] >= 6 and row['shopping_score'] >= 6:
        return "Mixed-Use"
    else:
        return "Residential"

def generate_investment_metrics(data, down_payment_pct, holding_period):
    """Generate investment metrics for properties based on their characteristics"""
    investment_data = data.copy()
    
    # Simulate rental income (typically 0.5-1% of property value monthly)
    investment_data['monthly_rent'] = investment_data.apply(
        lambda x: (x['price'] * np.random.uniform(0.005, 0.01)) / 12, axis=1
    )
    
    # Simulate annual property tax (1-2% of property value)
    investment_data['annual_property_tax'] = investment_data['price'] * np.random.uniform(0.01, 0.02)
    
    # Simulate annual insurance (0.3-0.5% of property value)
    investment_data['annual_insurance'] = investment_data['price'] * np.random.uniform(0.003, 0.005)
    
    # Simulate vacancy rate (3-8%)
    investment_data['vacancy_rate'] = np.random.uniform(0.03, 0.08, size=len(investment_data))
    
    # Simulate maintenance costs (5-10% of annual rent)
    investment_data['maintenance_rate'] = np.random.uniform(0.05, 0.1, size=len(investment_data))
    
    # Simulate property management costs (8-12% of rent)
    investment_data['management_rate'] = np.random.uniform(0.08, 0.12, size=len(investment_data))
    
    # Simulate mortgage details
    investment_data['down_payment'] = investment_data['price'] * (down_payment_pct / 100)
    investment_data['loan_amount'] = investment_data['price'] - investment_data['down_payment']
    
    # Assume a 30-year fixed mortgage at 4.5% interest
    mortgage_rate = 0.045
    investment_data['monthly_mortgage'] = investment_data.apply(
        lambda x: (x['loan_amount'] * (mortgage_rate/12 * (1 + mortgage_rate/12)**(30*12)) / 
                  ((1 + mortgage_rate/12)**(30*12) - 1)) if x['loan_amount'] > 0 else 0,
        axis=1
    )
    
    # Calculate annual income and expenses
    investment_data['annual_rental_income'] = investment_data['monthly_rent'] * 12
    investment_data['annual_vacancy_cost'] = investment_data['annual_rental_income'] * investment_data['vacancy_rate']
    investment_data['annual_maintenance'] = investment_data['annual_rental_income'] * investment_data['maintenance_rate']
    investment_data['annual_management'] = investment_data['annual_rental_income'] * investment_data['management_rate']
    
    investment_data['total_annual_expenses'] = (
        investment_data['annual_property_tax'] +
        investment_data['annual_insurance'] +
        investment_data['annual_vacancy_cost'] +
        investment_data['annual_maintenance'] +
        investment_data['annual_management']
    )
    
    investment_data['annual_mortgage_payments'] = investment_data['monthly_mortgage'] * 12
    
    # Calculate net operating income (NOI) and cash flow
    investment_data['noi'] = investment_data['annual_rental_income'] - investment_data['total_annual_expenses']
    investment_data['annual_cash_flow'] = investment_data['noi'] - investment_data['annual_mortgage_payments']
    investment_data['monthly_cash_flow'] = investment_data['annual_cash_flow'] / 12
    
    # Calculate cap rate
    investment_data['cap_rate'] = (investment_data['noi'] / investment_data['price']) * 100
    
    # Calculate cash-on-cash return
    investment_data['cash_on_cash_return'] = (investment_data['annual_cash_flow'] / investment_data['down_payment']) * 100
    
    # Simulate appreciation rates based on city and property type
    investment_data['appreciation_rate'] = investment_data.apply(
        lambda x: get_appreciation_rate(x['city'], x['property_type']), axis=1
    )
    
    # Calculate future value
    investment_data['future_value'] = investment_data.apply(
        lambda x: x['price'] * (1 + x['appreciation_rate']/100) ** holding_period, axis=1
    )
    
    # Calculate remaining loan balance (simplified)
    investment_data['remaining_loan'] = investment_data.apply(
        lambda x: max(0, x['loan_amount'] * (1 - (holding_period / 30))), axis=1
    )
    
    # Calculate equity and total return
    investment_data['future_equity'] = investment_data['future_value'] - investment_data['remaining_loan']
    investment_data['equity_gain'] = investment_data['future_equity'] - investment_data['down_payment']
    investment_data['total_cash_flow'] = investment_data['annual_cash_flow'] * holding_period
    investment_data['total_profit'] = investment_data['equity_gain'] + investment_data['total_cash_flow']
    investment_data['total_roi'] = (investment_data['total_profit'] / investment_data['down_payment']) * 100
    
    # Calculate normalized scores for comparison (0-100 scale)
    max_cap_rate = investment_data['cap_rate'].max()
    if max_cap_rate > 0:
        investment_data['cap_rate_score'] = (investment_data['cap_rate'] / max_cap_rate) * 100
    else:
        investment_data['cap_rate_score'] = 0
    
    max_cash_flow = investment_data['monthly_cash_flow'].max()
    if max_cash_flow > 0:
        investment_data['cash_flow_score'] = (investment_data['monthly_cash_flow'] / max_cash_flow) * 100
    else:
        investment_data['cash_flow_score'] = 0
    
    max_appreciation = investment_data['appreciation_rate'].max()
    if max_appreciation > 0:
        investment_data['appreciation_score'] = (investment_data['appreciation_rate'] / max_appreciation) * 100
    else:
        investment_data['appreciation_score'] = 0
    
    return investment_data

def get_appreciation_rate(city, property_type):
    """Simulate different appreciation rates based on city and property type"""
    # Define base rates for different cities
    city_rates = {
        'New York': np.random.uniform(3.5, 5.0),
        'Los Angeles': np.random.uniform(4.0, 5.5),
        'Chicago': np.random.uniform(2.0, 3.5),
        'Houston': np.random.uniform(2.5, 4.0),
        'Phoenix': np.random.uniform(3.0, 5.0),
        'Philadelphia': np.random.uniform(2.0, 3.5),
        'San Antonio': np.random.uniform(2.5, 4.0),
        'San Diego': np.random.uniform(3.5, 5.0),
        'Dallas': np.random.uniform(3.0, 4.5),
        'San Jose': np.random.uniform(4.0, 6.0)
    }
    
    # Get base rate for city, or use average if city not in dictionary
    base_rate = city_rates.get(city, np.random.uniform(2.5, 4.0))
    
    # Adjust for property type
    if property_type == 'Single Family':
        adjustment = np.random.uniform(0.0, 0.5)
    elif property_type == 'Multi-Family':
        adjustment = np.random.uniform(0.2, 0.7)
    elif property_type == 'Condo':
        adjustment = np.random.uniform(-0.5, 0.2)
    elif property_type == 'Townhouse':
        adjustment = np.random.uniform(-0.3, 0.3)
    else:
        adjustment = 0
    
    return base_rate + adjustment

def show_property_cards(properties):
    """Display property cards for top matches"""
    for i, (_, prop) in enumerate(properties.iterrows()):
        with st.container():
            col1, col2 = st.columns([1, 3])
            
            with col1:
                # Property image placeholder (in a real app, this would be actual property images)
                st.image(
                    "https://img.icons8.com/fluency/96/000000/real-estate.png", 
                    width=100,
                    caption=f"Property {i+1}"
                )
            
            with col2:
                st.markdown(f"### {prop['address']}, {prop['city']}")
                st.markdown(f"**${prop['price']:,.0f}** • {prop['bedrooms']} bed • {prop['bathrooms']} bath • {prop['sqft']:,} sqft")
                st.markdown(f"**Match Score:** {prop['match_score']}%")
                
                # Property features
                features = []
                
                if 'year_built' in prop:
                    features.append(f"Built in {int(prop['year_built'])}")
                
                if 'property_type' in prop:
                    features.append(prop['property_type'])
                
                if 'days_on_market' in prop:
                    features.append(f"{int(prop['days_on_market'])} days on market")
                
                st.markdown("**Features:** " + ", ".join(features))
        
        st.markdown("---")