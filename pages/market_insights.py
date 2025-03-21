import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_processing import get_market_trends, calculate_price_metrics
from utils.visualization import plot_city_comparison, plot_market_trends
from utils.prediction import forecast_market_trends

def show_market_insights(filtered_data):
    st.title("Global Market Insights")
    
    # Initial check for empty data
    if filtered_data is None or (hasattr(filtered_data, 'empty') and filtered_data.empty):
        st.warning("No data available with the current filters. Please adjust your selection.")
        
        # We'll still continue to show the global market insights from the database
        # which doesn't rely on the filtered_data parameter
        
    st.markdown("""
    This page provides detailed market insights and trend analysis for real estate markets worldwide.
    Select a country to view detailed market data and trends for major cities in that region.
    """)
    
    # Import required libraries
    import folium
    from streamlit_folium import st_folium
    from utils.visualization import create_property_map
    
    # Get market trends from database
    from utils.database import get_market_trends as get_db_market_trends
    
    # Get all available countries from the database
    all_market_trends = get_db_market_trends()
    all_market_trends_df = pd.DataFrame(all_market_trends)
    
    if not all_market_trends_df.empty:
        # Get unique countries
        countries = sorted(all_market_trends_df['country'].unique())
        
        # Add an "All Countries" option
        countries = ["All Countries"] + countries
        
        # Country selection
        selected_country = st.selectbox(
            "Select a Country to View Market Insights",
            options=countries,
            index=0
        )
        
        # Filter data based on selected country
        if selected_country != "All Countries":
            country_market_data = all_market_trends_df[all_market_trends_df['country'] == selected_country]
            st.subheader(f"Real Estate Market Insights for {selected_country}")
            
            # Country-specific overview (only shown when a specific country is selected)
            # Calculate country-level metrics
            country_metrics = country_market_data.groupby('date')[['median_price', 'avg_price', 'inventory', 'days_on_market']].mean().reset_index()
            country_metrics = country_metrics.sort_values('date')
            latest_metrics = country_metrics.iloc[-1] if not country_metrics.empty else None
            
            if latest_metrics is not None:
                # Display country-level metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "Median Price", 
                        f"${latest_metrics['median_price']:,.0f}",
                        delta=f"{((latest_metrics['median_price'] / country_metrics.iloc[-2]['median_price'] - 1) * 100):.1f}%" 
                        if len(country_metrics) > 1 else None
                    )
                
                with col2:
                    st.metric(
                        "Average Price", 
                        f"${latest_metrics['avg_price']:,.0f}",
                        delta=f"{((latest_metrics['avg_price'] / country_metrics.iloc[-2]['avg_price'] - 1) * 100):.1f}%" 
                        if len(country_metrics) > 1 else None
                    )
                
                with col3:
                    st.metric(
                        "Inventory", 
                        f"{latest_metrics['inventory']:,.0f}",
                        delta=f"{(latest_metrics['inventory'] - country_metrics.iloc[-2]['inventory']):+.0f}" 
                        if len(country_metrics) > 1 else None
                    )
                
                with col4:
                    st.metric(
                        "Days on Market", 
                        f"{latest_metrics['days_on_market']:.1f}",
                        delta=f"{(latest_metrics['days_on_market'] - country_metrics.iloc[-2]['days_on_market']):+.1f}" 
                        if len(country_metrics) > 1 else None,
                        delta_color="inverse"  # Lower is better for days on market
                    )
                
                # Country price trend chart
                st.subheader(f"Price Trends in {selected_country}")
                
                fig = px.line(
                    country_metrics,
                    x='date',
                    y=['median_price', 'avg_price'],
                    title=f"Historical Price Trends in {selected_country}",
                    labels={
                        "value": "Price ($)",
                        "date": "Date",
                        "variable": "Metric"
                    },
                    color_discrete_map={
                        "median_price": "blue",
                        "avg_price": "red"
                    }
                )
                fig.update_layout(
                    yaxis_tickprefix='$', 
                    yaxis_tickformat=',',
                    legend=dict(
                        title=None,
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                # Rename legend items
                newnames = {'median_price': 'Median Price', 'avg_price': 'Average Price'}
                fig.for_each_trace(lambda t: t.update(name = newnames[t.name]))
                
                st.plotly_chart(fig, use_container_width=True)
        else:
            country_market_data = all_market_trends_df
            st.subheader("Global Real Estate Market Insights")
            
            # Global market comparison (top countries by median price)
            st.markdown("### Global Market Comparison")
            
            # Get the latest data for each country
            latest_global_data = all_market_trends_df.sort_values('date').groupby('country').last().reset_index()
            
            # Plot top countries by median price
            top_countries = latest_global_data.sort_values('median_price', ascending=False).head(10)
            
            fig = px.bar(
                top_countries,
                x='country',
                y='median_price',
                title="Top Countries by Median Property Price",
                color='median_price',
                labels={"median_price": "Median Price ($)", "country": "Country"},
                color_continuous_scale=px.colors.sequential.Viridis
            )
            fig.update_layout(yaxis_tickprefix='$', yaxis_tickformat=',')
            st.plotly_chart(fig, use_container_width=True)
            
            # Plot global price per sqft comparison
            fig = px.bar(
                latest_global_data.sort_values('price_per_sqft', ascending=False).head(10),
                x='country',
                y='price_per_sqft',
                title="Top Countries by Price per Square Foot",
                color='price_per_sqft',
                labels={"price_per_sqft": "Price per Sq.Ft. ($)", "country": "Country"},
                color_continuous_scale=px.colors.sequential.Plasma
            )
            fig.update_layout(yaxis_tickprefix='$', yaxis_tickformat=',')
            st.plotly_chart(fig, use_container_width=True)
            
            # Global market map visualization
            st.subheader("Global Market Map")
            
            # Get coordinates for each city
            city_locations = []
            for _, city_row in latest_global_data.iterrows():
                # Skip if missing coordinates
                if pd.isna(city_row.get('latitude', None)) or pd.isna(city_row.get('longitude', None)):
                    continue
                    
                city_locations.append({
                    'country': city_row['country'],
                    'city': city_row.get('city', 'Unknown'),
                    'latitude': city_row.get('latitude', 0),
                    'longitude': city_row.get('longitude', 0),
                    'median_price': city_row['median_price'],
                    'avg_price': city_row['avg_price'],
                    'price_per_sqft': city_row['price_per_sqft'],
                    'year_over_year_change': city_row['year_over_year_change']
                })
            
            if city_locations:
                # Create a DataFrame for map plotting
                map_df = pd.DataFrame(city_locations)
                
                # Create a world map
                world_map = folium.Map(location=[0, 0], zoom_start=2, tiles='CartoDB positron')
                
                # Add markers for each country
                for _, row in map_df.iterrows():
                    # Create a tooltip with country information
                    tooltip = f"""
                    <b>{row['country']}</b><br>
                    Median Price: ${row['median_price']:,.0f}<br>
                    Avg Price: ${row['avg_price']:,.0f}<br>
                    Price/Sqft: ${row['price_per_sqft']:.2f}<br>
                    Annual Change: {row['year_over_year_change']:.1f}%
                    """
                    
                    # Determine marker color based on price
                    if row['median_price'] > map_df['median_price'].quantile(0.75):
                        color = 'red'
                    elif row['median_price'] > map_df['median_price'].median():
                        color = 'orange' 
                    elif row['median_price'] > map_df['median_price'].quantile(0.25):
                        color = 'green'
                    else:
                        color = 'blue'
                        
                    # Add marker
                    folium.CircleMarker(
                        location=[row['latitude'], row['longitude']],
                        radius=5,
                        color=color,
                        fill=True,
                        fill_color=color,
                        fill_opacity=0.7,
                        tooltip=folium.Tooltip(tooltip)
                    ).add_to(world_map)
                
                # Display the map
                st_folium(world_map, width=1000, height=500, returned_objects=[])
        
        # Show cities available in selected country
        cities_in_country = sorted(country_market_data['city'].unique())
        
        # Custom filtering for selected country data
        st.markdown(f"### Major Cities in {selected_country if selected_country != 'All Countries' else 'Selected Markets'}")
        
        selected_cities = st.multiselect(
            "Select Cities to Compare",
            options=cities_in_country,
            default=cities_in_country[:5] if len(cities_in_country) > 5 else cities_in_country
        )
        
        if selected_cities:
            city_data = country_market_data[country_market_data['city'].isin(selected_cities)]
            
            # Convert to filtered_data format for compatibility with existing code
            if filtered_data is not None and not getattr(filtered_data, 'empty', True):
                filtered_data = filtered_data[filtered_data['city'].isin(selected_cities)]
            
            # Add city data metrics
            latest_city_data = (city_data.sort_values('date')
                               .groupby('city').last()
                               .reset_index())
            
            # Display city metrics in a table
            metrics_df = (
                latest_city_data[['city', 'median_price', 'avg_price', 'price_per_sqft', 'days_on_market', 'year_over_year_change']]
                .rename(columns={
                    'median_price': 'Median Price ($)',
                    'avg_price': 'Average Price ($)',
                    'price_per_sqft': 'Price/Sqft ($)',
                    'days_on_market': 'Days on Market',
                    'year_over_year_change': 'Annual Appreciation (%)'
                })
                .set_index('city')
                .sort_values('Median Price ($)', ascending=False)
            )
            st.dataframe(metrics_df)
            
            # Add country-specific visualizations
            st.subheader(f"Market Metrics: {selected_country if selected_country != 'All Countries' else 'Global Markets'}")
            
            # Tab-based visualizations for different metrics
            metric_tabs = st.tabs(["Median Prices", "Price/Sqft", "Days on Market", "Appreciation Rates"])
            
            # Tab 1: Median Prices by City
            with metric_tabs[0]:
                fig = px.bar(
                    latest_city_data.sort_values('median_price', ascending=False),
                    x='city',
                    y='median_price',
                    title=f"Median Property Prices by City in {selected_country if selected_country != 'All Countries' else 'Global Markets'}",
                    labels={"median_price": "Median Price ($)", "city": "City"},
                    color='median_price',
                    color_continuous_scale=px.colors.sequential.Viridis
                )
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
            
            # Tab 2: Price per Square Foot
            with metric_tabs[1]:
                fig = px.bar(
                    latest_city_data.sort_values('price_per_sqft', ascending=False),
                    x='city',
                    y='price_per_sqft',
                    title=f"Price per Square Foot by City in {selected_country if selected_country != 'All Countries' else 'Global Markets'}",
                    labels={"price_per_sqft": "Price per Sq.Ft. ($)", "city": "City"},
                    color='price_per_sqft',
                    color_continuous_scale=px.colors.sequential.Plasma
                )
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
            
            # Tab 3: Days on Market
            with metric_tabs[2]:
                fig = px.bar(
                    latest_city_data.sort_values('days_on_market'),
                    x='city',
                    y='days_on_market',
                    title=f"Average Days on Market by City in {selected_country if selected_country != 'All Countries' else 'Global Markets'}",
                    labels={"days_on_market": "Days on Market", "city": "City"},
                    color='days_on_market',
                    color_continuous_scale=px.colors.sequential.Blues_r
                )
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
            
            # Tab 4: Annual Appreciation Rates
            with metric_tabs[3]:
                fig = px.bar(
                    latest_city_data.sort_values('year_over_year_change', ascending=False),
                    x='city',
                    y='year_over_year_change',
                    title=f"Annual Appreciation Rate by City in {selected_country if selected_country != 'All Countries' else 'Global Markets'}",
                    labels={"year_over_year_change": "Annual Appreciation (%)", "city": "City"},
                    color='year_over_year_change',
                    color_continuous_scale=px.colors.sequential.Reds
                )
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
                
            # Historical price trends for selected cities
            st.subheader(f"Historical Price Trends: {selected_country if selected_country != 'All Countries' else 'Global Markets'}")
            
            # Group by city and date, and get the median price for each month
            city_trends = city_data.groupby(['city', 'date'])['median_price'].mean().reset_index()
            
            # Plot historical price trends
            fig = px.line(
                city_trends,
                x='date',
                y='median_price',
                color='city',
                title=f"Historical Median Prices in {selected_country if selected_country != 'All Countries' else 'Selected Markets'}",
                labels={"median_price": "Median Price ($)", "date": "Date", "city": "City"}
            )
            fig.update_layout(yaxis_tickprefix='$', yaxis_tickformat=',')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Please select at least one city to view market insights.")
            return
    else:
        st.warning("No market trend data available in the database.")
        
    # Handle the case where we don't have selected cities yet
    if (filtered_data is None or getattr(filtered_data, 'empty', True)) and 'selected_cities' not in locals():
        st.warning("No data available with the current filters. Please adjust your selection.")
        return
    
    # Only proceed with this section if we have valid filtered data
    if filtered_data is not None and not getattr(filtered_data, 'empty', True):
        # Market overview metrics
        metrics = calculate_price_metrics(filtered_data)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Median Price", f"${metrics['median_price']:,.0f}")
        
        with col2:
            st.metric("Avg. Price/Sqft", f"${metrics['avg_price_sqft']:.2f}")
        
        with col3:
            st.metric("Properties", f"{metrics['total_properties']}")
        
        with col4:
            st.metric("Avg. Days on Market", f"{metrics['avg_days_on_market']:.1f}")
        
        # City comparison
        st.subheader("City Comparison")
        city_fig = plot_city_comparison(filtered_data)
        st.plotly_chart(city_fig, use_container_width=True)
        
        # Market trends with forecast
        st.subheader("Market Trends with Price Forecast")
        
        # Get forecast data
        forecast_data = forecast_market_trends(filtered_data, forecast_months=6)
        
        if forecast_data is not None and not getattr(forecast_data, 'empty', True):
            # Create plot
            fig = go.Figure()
            
            # Add historical data for each city
            for city in forecast_data['city'].unique():
                city_data = forecast_data[forecast_data['city'] == city]
                
                # Historical data
                historical = city_data[city_data['is_forecast'] == False]
                if historical is not None and not getattr(historical, 'empty', True):
                    fig.add_trace(go.Scatter(
                        x=historical['date'],
                        y=historical['avg_price'],
                        mode='lines+markers',
                        name=f"{city} (Historical)",
                        line=dict(width=2)
                    ))
                
                # Forecast data
                forecast = city_data[city_data['is_forecast'] == True]
                if forecast is not None and not getattr(forecast, 'empty', True):
                    fig.add_trace(go.Scatter(
                        x=forecast['date'],
                        y=forecast['avg_price'],
                        mode='lines',
                        line=dict(dash='dash', width=2),
                        name=f"{city} (Forecast)"
                    ))
            
            # Update layout
            fig.update_layout(
                title="Property Price Forecast",
                xaxis_title="Date",
                yaxis_title="Average Price ($)",
                legend=dict(orientation='h', yanchor='top', y=-0.2),
                height=500,
                template='plotly_white'
            )
            
            # Format y-axis as currency
            fig.update_layout(yaxis_tickprefix='$', yaxis_tickformat=',')
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Add explanation of forecast
            st.info("""
            **About the Forecast**: This forecast uses linear regression based on historical price trends.
            The dashed lines represent projected prices for the next 6 months.
            """)
        else:
            st.warning("Unable to generate forecast with the current data selection.")
            
        # Monthly price changes
        st.subheader("Monthly Price Changes")
        
        market_df = get_market_trends(filtered_data)
        
        if market_df is not None and not getattr(market_df, 'empty', True):
            # Calculate month-over-month changes
            market_df = market_df.sort_values(['city', 'date'])
            market_df['prev_price'] = market_df.groupby('city')['avg_price'].shift(1)
            market_df['price_change_pct'] = (market_df['avg_price'] - market_df['prev_price']) / market_df['prev_price'] * 100
            
            # Filter out NaN values
            market_df = market_df.dropna(subset=['price_change_pct'])
            
            # Create a monthly change heatmap
            try:
                # Initialize variables
                pivot_df = None
                annotations = []
                continue_with_heatmap = False
                
                # Create the pivot table
                if len(market_df) > 0:
                    pivot_df = market_df.pivot(index='city', columns='date', values='price_change_pct')
                    
                    # Check if we have a valid pivot table with data
                    if pivot_df is not None and not pivot_df.empty and len(pivot_df) > 0:
                        # Create annotations
                        annotations = []
                        for i, row in enumerate(pivot_df.values):
                            for j, value in enumerate(row):
                                if not pd.isna(value):
                                    color = "green" if value >= 0 else "red"
                                    annotations.append(
                                        dict(
                                            x=pivot_df.columns[j],
                                            y=pivot_df.index[i],
                                            text=f"{value:.1f}%",
                                            showarrow=False,
                                            font=dict(color=color)
                                        )
                                    )
                        
                        # Flag that we can proceed with creating the heatmap
                        continue_with_heatmap = True
                    else:
                        st.warning("Not enough price change data to create the heatmap.")
                else:
                    st.warning("No market data available for heatmap visualization.")
                
                # Only create the heatmap if we have valid data
                if continue_with_heatmap and pivot_df is not None and not pivot_df.empty:
                    fig = px.imshow(
                        pivot_df,
                        labels=dict(x="Month", y="City", color="% Change"),
                        x=pivot_df.columns.strftime('%b %Y'),
                        y=pivot_df.index,
                        color_continuous_scale='RdYlGn',
                        template='plotly_white',
                        aspect="auto"
                    )
                    
                    fig.update_layout(
                        annotations=annotations,
                        height=500
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.warning(f"Error creating or displaying price change heatmap: {str(e)}")
            
            # Overall market summary
            st.subheader("Market Summary")
            
            try:
                # Check if we have enough data for market metrics
                if len(market_df) > 0 and 'date' in market_df.columns and 'price_change_pct' in market_df.columns:
                    # Get unique dates and sort them
                    sorted_dates = sorted(market_df['date'].unique())
                    
                    # Make sure we have at least 2 months of data
                    if len(sorted_dates) >= 2:
                        # Take the most recent 2 months
                        recent_months = sorted_dates[-2:]
                        recent_data = market_df[market_df['date'].isin(recent_months)]
                        
                        # Check if we have data for the recent months
                        if len(recent_data) > 0:
                            # Group by city and calculate average change
                            city_changes = recent_data.groupby('city')['price_change_pct'].mean().sort_values(ascending=False)
                            
                            # Make sure we have cities with data
                            if len(city_changes) > 0:
                                top_city = city_changes.index[0]
                                top_appreciation = city_changes.iloc[0]
                                
                                bottom_city = city_changes.index[-1]
                                bottom_appreciation = city_changes.iloc[-1]
                                
                                # Calculate overall market average change
                                overall_change = recent_data['price_change_pct'].mean()
                                
                                st.markdown(f"""
                                - Overall market change: **{overall_change:.1f}%** in the last month
                                - Highest appreciation: **{top_city}** at **{top_appreciation:.1f}%**
                                - Lowest appreciation: **{bottom_city}** at **{bottom_appreciation:.1f}%**
                                """)
                                
                                # Display market hotness indicators
                                if abs(overall_change) < 1:
                                    market_status = "Stable market conditions with minimal price changes"
                                elif overall_change > 1:
                                    market_status = "Hot market with increasing prices - good for sellers"
                                else:
                                    market_status = "Buyer's market with decreasing prices - good for buyers"
                                
                                st.info(f"**Market Status**: {market_status}")
                            else:
                                st.warning("Not enough data to identify top performing cities.")
                        else:
                            st.warning("Not enough recent data for market summary.")
                    else:
                        st.warning("Need at least 2 months of data for market comparison.")
                else:
                    st.warning("Not enough data available for market summary.")
            except Exception as e:
                st.warning(f"Error calculating market summary: {str(e)}")
        else:
            st.warning("Not enough data to calculate monthly changes.")
        
        # Add a data table with the raw data
        st.subheader("Market Data Table")
        
        # Check if the necessary columns exist in the filtered_data
        required_columns = ['address', 'city', 'price', 'bedrooms', 'bathrooms', 'sqft', 'property_type', 'year_built', 'days_on_market']
        if filtered_data is not None and all(col in filtered_data.columns for col in required_columns):
            st.dataframe(
                filtered_data[required_columns].sort_values(by='price', ascending=False)
            )
        else:
            st.warning("No detailed property data available for the current selection.")
