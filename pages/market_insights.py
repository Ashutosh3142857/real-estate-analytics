import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_processing import get_market_trends, calculate_price_metrics
from utils.visualization import plot_city_comparison, plot_market_trends
from utils.prediction import forecast_market_trends

def show_market_insights(filtered_data):
    st.title("Market Insights")
    
    st.markdown("""
    This page provides detailed market insights and trend analysis for the real estate market.
    Use the filters in the sidebar to customize the data view.
    """)
    
    if filtered_data.empty:
        st.warning("No data available with the current filters. Please adjust your selection.")
        return
    
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
    
    if not forecast_data.empty:
        # Create plot
        fig = go.Figure()
        
        # Add historical data for each city
        for city in forecast_data['city'].unique():
            city_data = forecast_data[forecast_data['city'] == city]
            
            # Historical data
            historical = city_data[city_data['is_forecast'] == False]
            if not historical.empty:
                fig.add_trace(go.Scatter(
                    x=historical['date'],
                    y=historical['avg_price'],
                    mode='lines+markers',
                    name=f"{city} (Historical)",
                    line=dict(width=2)
                ))
            
            # Forecast data
            forecast = city_data[city_data['is_forecast'] == True]
            if not forecast.empty:
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
    
    if not market_df.empty:
        # Calculate month-over-month changes
        market_df = market_df.sort_values(['city', 'date'])
        market_df['prev_price'] = market_df.groupby('city')['avg_price'].shift(1)
        market_df['price_change_pct'] = (market_df['avg_price'] - market_df['prev_price']) / market_df['prev_price'] * 100
        
        # Filter out NaN values
        market_df = market_df.dropna(subset=['price_change_pct'])
        
        # Create a monthly change heatmap
        pivot_df = market_df.pivot(index='city', columns='date', values='price_change_pct')
        
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
        
        # Overall market summary
        st.subheader("Market Summary")
        
        # Calculate recent market metrics
        recent_months = market_df.sort_values('date')['date'].unique()[-2:]
        recent_data = market_df[market_df['date'].isin(recent_months)]
        
        # Get city with highest appreciation
        city_changes = recent_data.groupby('city')['price_change_pct'].mean().sort_values(ascending=False)
        top_city = city_changes.index[0]
        top_appreciation = city_changes.iloc[0]
        
        # Get city with lowest appreciation
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
        st.warning("Not enough data to calculate monthly changes.")
    
    # Add a data table with the raw data
    st.subheader("Market Data Table")
    st.dataframe(
        filtered_data[['address', 'city', 'price', 'bedrooms', 'bathrooms', 'sqft', 'property_type', 'year_built', 'days_on_market']]
        .sort_values(by='price', ascending=False)
    )
