import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def load_sample_data():
    """
    Load sample real estate data
    In a production environment, this would fetch data from an API or database
    """
    try:
        # In a real application, this would be replaced with actual API calls or database queries
        # For demonstration, we'll create a structured dataset that mimics real estate data
        
        # Define cities with realistic price ranges
        cities = {
            'New York': {'min_price': 500000, 'max_price': 5000000, 'price_sqft': 1000},
            'Los Angeles': {'min_price': 400000, 'max_price': 3000000, 'price_sqft': 800},
            'Chicago': {'min_price': 200000, 'max_price': 1500000, 'price_sqft': 400},
            'Houston': {'min_price': 150000, 'max_price': 1000000, 'price_sqft': 200},
            'Phoenix': {'min_price': 200000, 'max_price': 800000, 'price_sqft': 250},
            'Philadelphia': {'min_price': 180000, 'max_price': 900000, 'price_sqft': 300},
            'San Antonio': {'min_price': 150000, 'max_price': 700000, 'price_sqft': 180},
            'San Diego': {'min_price': 400000, 'max_price': 2000000, 'price_sqft': 650},
            'Dallas': {'min_price': 200000, 'max_price': 1200000, 'price_sqft': 220},
            'San Jose': {'min_price': 600000, 'max_price': 2500000, 'price_sqft': 900}
        }
        
        property_types = ['Single Family', 'Condo', 'Townhouse', 'Multi-Family']
        
        # Generate sample data
        num_records = 1000
        data = []
        
        # Current date for reference
        today = datetime.now()
        
        # Realistic property IDs
        property_ids = np.arange(10001, 10001 + num_records)
        
        for i in range(num_records):
            # Select a random city
            city = random.choice(list(cities.keys()))
            city_data = cities[city]
            
            # Generate property details
            property_type = random.choice(property_types)
            
            # Adjust square footage based on property type
            if property_type == 'Condo':
                sqft = np.random.randint(600, 1800)
            elif property_type == 'Townhouse':
                sqft = np.random.randint(1200, 2500)
            elif property_type == 'Multi-Family':
                sqft = np.random.randint(2000, 5000)
            else:  # Single Family
                sqft = np.random.randint(1500, 4000)
            
            # Price calculation with some randomness
            base_price = sqft * city_data['price_sqft']
            random_factor = np.random.uniform(0.8, 1.2)  # ±20% price variation
            price = int(base_price * random_factor)
            
            # Ensure price is within city's range
            price = max(city_data['min_price'], min(price, city_data['max_price']))
            
            # Generate other property attributes
            bedrooms = np.random.randint(1, 6)
            bathrooms = np.random.randint(1, 5)
            
            # Generate a random listing date within the past year
            days_back = np.random.randint(1, 365)
            list_date = today - timedelta(days=days_back)
            
            # Generate year built between 1950 and 2023
            year_built = np.random.randint(1950, 2024)
            
            # Create street address
            street_numbers = np.random.randint(100, 9999)
            streets = ['Main St', 'Oak Ave', 'Maple Dr', 'Washington Blvd', 'Park Ave', 
                      'Lake St', 'River Rd', 'Forest Dr', 'Highland Ave', 'Valley Blvd']
            address = f"{street_numbers} {random.choice(streets)}"
            
            # Generate zip code (simplified)
            zip_code = f"{np.random.randint(10000, 99999)}"
            
            # Generate lat/long coordinates (simplified approximation)
            latitude = np.random.uniform(25.0, 48.0)
            longitude = np.random.uniform(-125.0, -70.0)
            
            # Market trend data (days on market)
            days_on_market = int(np.random.exponential(30))  # Exponential distribution with mean of 30 days
            
            data.append({
                'property_id': property_ids[i],
                'address': address,
                'city': city,
                'zip_code': zip_code,
                'price': price,
                'bedrooms': bedrooms,
                'bathrooms': bathrooms,
                'sqft': sqft,
                'property_type': property_type,
                'year_built': year_built,
                'list_date': list_date,
                'days_on_market': days_on_market,
                'latitude': latitude,
                'longitude': longitude
            })
        
        df = pd.DataFrame(data)
        
        # Add time-series price data
        df = add_historical_prices(df)
        
        return df
        
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame()  # Return empty DataFrame on error

def add_historical_prices(df):
    """Add simulated historical price data for market trend analysis"""
    # Create month-to-month variations in average price
    months = 12
    today = datetime.now()
    
    # Create historical monthly average data
    monthly_data = []
    
    # Let's generate historical data for each city
    for city in df['city'].unique():
        city_avg_price = df[df['city'] == city]['price'].mean()
        
        # Generate monthly averages with a realistic trend (generally upward with fluctuations)
        base_trend = np.linspace(0.9, 1.0, months)  # Slight upward trend
        
        # Add seasonality
        seasonality = 0.05 * np.sin(np.linspace(0, 2*np.pi, months))
        
        # Add some random noise
        noise = np.random.normal(0, 0.02, months)
        
        # Combine components
        price_factors = base_trend + seasonality + noise
        
        for i in range(months):
            month_date = today - timedelta(days=30*(months-i))
            monthly_avg_price = city_avg_price * price_factors[i]
            
            monthly_data.append({
                'date': month_date.strftime('%Y-%m'),
                'city': city,
                'avg_price': monthly_avg_price,
                'num_listings': int(np.random.normal(df[df['city'] == city].shape[0]/12, 10))
            })
    
    # Convert to DataFrame
    historical_df = pd.DataFrame(monthly_data)
    
    # Add the historical data to the original DataFrame as a new column
    df['historical_prices'] = df.apply(
        lambda x: historical_df[historical_df['city'] == x['city']].to_dict('records'),
        axis=1
    )
    
    return df

def filter_data(df, cities=None, min_price=None, max_price=None, property_types=None, bedrooms=None):
    """Filter the real estate data based on user selections"""
    filtered_df = df.copy()
    
    if cities:
        filtered_df = filtered_df[filtered_df['city'].isin(cities)]
    
    if min_price is not None:
        filtered_df = filtered_df[filtered_df['price'] >= min_price]
    
    if max_price is not None:
        filtered_df = filtered_df[filtered_df['price'] <= max_price]
    
    if property_types:
        filtered_df = filtered_df[filtered_df['property_type'].isin(property_types)]
    
    if bedrooms:
        filtered_df = filtered_df[filtered_df['bedrooms'] == bedrooms]
    
    return filtered_df

def get_market_trends(df):
    """Extract market trend data from the dataset"""
    if df.empty:
        return pd.DataFrame()
    
    # Create a DataFrame with monthly average prices by city
    market_data = []
    
    for _, row in df.iterrows():
        city = row['city']
        historical_prices = row['historical_prices']
        
        for month_data in historical_prices:
            market_data.append({
                'date': month_data['date'],
                'city': city,
                'avg_price': month_data['avg_price'],
                'num_listings': month_data['num_listings']
            })
    
    market_df = pd.DataFrame(market_data)
    
    # Remove duplicates (since we added the same historical data to each property)
    market_df = market_df.drop_duplicates(['date', 'city'])
    
    # Sort by date
    market_df['date'] = pd.to_datetime(market_df['date'])
    market_df = market_df.sort_values('date')
    
    return market_df

def calculate_price_metrics(df):
    """Calculate important price metrics for the dataset"""
    if df.empty:
        return {}
    
    metrics = {
        'avg_price': df['price'].mean(),
        'median_price': df['price'].median(),
        'min_price': df['price'].min(),
        'max_price': df['price'].max(),
        'price_std': df['price'].std(),
        'avg_price_sqft': (df['price'] / df['sqft']).mean(),
        'total_properties': len(df),
        'avg_days_on_market': df['days_on_market'].mean()
    }
    
    return metrics
