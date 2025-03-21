import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import folium
from streamlit_folium import folium_static
from utils.data_processing import get_market_trends

def plot_market_trends(df):
    """Create a line chart showing property price trends over time"""
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available", showarrow=False)
        return fig
    
    market_df = get_market_trends(df)
    
    if market_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No trend data available", showarrow=False)
        return fig
    
    # Calculate average price by date across all selected cities
    avg_by_date = market_df.groupby('date')['avg_price'].mean().reset_index()
    avg_by_city_date = market_df.groupby(['city', 'date'])['avg_price'].mean().reset_index()
    
    # Create the plot
    fig = px.line(
        avg_by_city_date, 
        x='date', 
        y='avg_price', 
        color='city',
        title='Average Property Prices Over Time',
        labels={'avg_price': 'Average Price ($)', 'date': 'Month', 'city': 'City'},
        template='plotly_white'
    )
    
    # Add overall average line
    fig.add_trace(
        go.Scatter(
            x=avg_by_date['date'],
            y=avg_by_date['avg_price'],
            mode='lines',
            line=dict(width=3, color='black', dash='dash'),
            name='Overall Average'
        )
    )
    
    # Update layout
    fig.update_layout(
        legend=dict(orientation='h', yanchor='top', y=-0.2),
        xaxis_title='Month',
        yaxis_title='Average Price ($)',
        height=500
    )
    
    # Format y-axis as currency
    fig.update_layout(yaxis_tickprefix='$', yaxis_tickformat=',')
    
    return fig

def plot_property_distribution(df):
    """Create a pie chart showing distribution of property types"""
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available", showarrow=False)
        return fig
    
    property_counts = df['property_type'].value_counts().reset_index()
    property_counts.columns = ['property_type', 'count']
    
    fig = px.pie(
        property_counts,
        values='count',
        names='property_type',
        title='Property Type Distribution',
        template='plotly_white',
        hole=0.4
    )
    
    # Update layout
    fig.update_layout(
        legend=dict(orientation='h', yanchor='bottom', y=-0.2),
        height=400
    )
    
    return fig

def plot_price_distribution(df):
    """Create a histogram showing the distribution of property prices"""
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available", showarrow=False)
        return fig
    
    fig = px.histogram(
        df,
        x='price',
        nbins=20,
        color='property_type',
        title='Price Distribution by Property Type',
        template='plotly_white',
        labels={'price': 'Price ($)', 'property_type': 'Property Type'},
        opacity=0.7
    )
    
    # Add median line
    median_price = df['price'].median()
    fig.add_vline(
        x=median_price,
        line_dash='dash',
        line_color='red',
        annotation_text=f'Median: ${median_price:,.0f}',
        annotation_position='top right'
    )
    
    # Update layout
    fig.update_layout(
        xaxis_title='Price ($)',
        yaxis_title='Number of Properties',
        legend=dict(orientation='h', yanchor='top', y=-0.2),
        height=500
    )
    
    # Format x-axis as currency
    fig.update_layout(xaxis_tickprefix='$', xaxis_tickformat=',')
    
    return fig

def plot_price_vs_sqft(df):
    """Create a scatter plot of price vs. square footage"""
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available", showarrow=False)
        return fig
    
    fig = px.scatter(
        df,
        x='sqft',
        y='price',
        color='property_type',
        title='Price vs. Square Footage',
        template='plotly_white',
        labels={'sqft': 'Square Footage', 'price': 'Price ($)', 'property_type': 'Property Type'},
        opacity=0.7,
        hover_data=['address', 'city', 'bedrooms', 'bathrooms']
    )
    
    # Add trendline
    fig.update_traces(marker=dict(size=8))
    
    # Add overall trendline
    fig.add_trace(
        px.scatter(
            df, x='sqft', y='price', trendline='ols'
        ).data[1]
    )
    
    # Update layout
    fig.update_layout(
        xaxis_title='Square Footage',
        yaxis_title='Price ($)',
        legend=dict(orientation='h', yanchor='top', y=-0.2),
        height=500
    )
    
    # Format y-axis as currency
    fig.update_layout(yaxis_tickprefix='$', yaxis_tickformat=',')
    
    return fig

def plot_city_comparison(df):
    """Create a bar chart comparing average prices by city"""
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available", showarrow=False)
        return fig
    
    city_avg = df.groupby('city')['price'].mean().reset_index().sort_values('price', ascending=False)
    
    fig = px.bar(
        city_avg,
        x='city',
        y='price',
        title='Average Property Price by City',
        template='plotly_white',
        labels={'price': 'Average Price ($)', 'city': 'City'},
        color='price',
        color_continuous_scale=px.colors.sequential.Bluered
    )
    
    # Update layout
    fig.update_layout(
        xaxis_title='City',
        yaxis_title='Average Price ($)',
        height=500,
        coloraxis_showscale=False
    )
    
    # Format y-axis as currency
    fig.update_layout(yaxis_tickprefix='$', yaxis_tickformat=',')
    
    return fig

def plot_price_heatmap(df):
    """Create a heatmap of average price by bedrooms and bathrooms"""
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available", showarrow=False)
        return fig
    
    # Create a pivot table of average price by bedrooms and bathrooms
    heatmap_data = df.pivot_table(
        values='price',
        index='bedrooms',
        columns='bathrooms',
        aggfunc='mean'
    ).round(0)
    
    # Create annotation text with currency formatting
    annotations = []
    for i, row in enumerate(heatmap_data.values):
        for j, value in enumerate(row):
            if not np.isnan(value):
                annotations.append(
                    dict(
                        x=heatmap_data.columns[j],
                        y=heatmap_data.index[i],
                        text=f"${value:,.0f}",
                        showarrow=False,
                        font=dict(color="white" if value > 500000 else "black")
                    )
                )
    
    fig = px.imshow(
        heatmap_data,
        labels=dict(x="Bathrooms", y="Bedrooms", color="Average Price"),
        x=heatmap_data.columns,
        y=heatmap_data.index,
        color_continuous_scale='Blues',
        template='plotly_white',
        title='Average Price by Bedrooms and Bathrooms'
    )
    
    fig.update_layout(
        annotations=annotations,
        height=500
    )
    
    # Format colorbar as currency
    fig.update_layout(coloraxis_colorbar=dict(title="Price", tickprefix="$", tickformat=","))
    
    return fig

def create_property_map(df):
    """
    Create an interactive map with property markers
    
    Args:
        df: DataFrame with latitude, longitude, and property information
        
    Returns:
        folium.Map: A map object that can be displayed with folium_static
    """
    if df.empty or 'latitude' not in df.columns or 'longitude' not in df.columns:
        # Return an empty map centered on the US if no data
        return folium.Map(location=[37.0902, -95.7129], zoom_start=4)
    
    # Remove rows with missing lat/long
    map_data = df.dropna(subset=['latitude', 'longitude']).copy()
    
    if map_data.empty:
        # Return an empty map centered on the US if no valid lat/long
        return folium.Map(location=[37.0902, -95.7129], zoom_start=4)
    
    # Determine map center (average of lat/long)
    center_lat = map_data['latitude'].mean()
    center_lng = map_data['longitude'].mean()
    
    # Create the map
    property_map = folium.Map(location=[center_lat, center_lng], zoom_start=12)
    
    # Add property markers to the map
    for _, row in map_data.iterrows():
        # Create popup content with property details
        popup_content = f"""
        <b>{row['address']}</b><br>
        {row['city']}, {row.get('state', '')}<br>
        <b>${row['price']:,.0f}</b><br>
        {row['bedrooms']} bed, {row['bathrooms']} bath<br>
        {row['sqft']} sqft<br>
        {row['property_type']}
        """
        
        # Determine marker color based on property type
        if 'Condo' in str(row['property_type']):
            color = 'blue'
        elif 'Multi-Family' in str(row['property_type']):
            color = 'purple'
        elif 'Apartment' in str(row['property_type']):
            color = 'pink'
        elif 'Townhouse' in str(row['property_type']):
            color = 'green'
        else:  # Single-Family, etc.
            color = 'red'
        
        # Add the marker to the map
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=folium.Popup(popup_content, max_width=300),
            tooltip=f"${row['price']:,.0f} - {row['address']}",
            icon=folium.Icon(color=color, icon='home', prefix='fa')
        ).add_to(property_map)
    
    return property_map
