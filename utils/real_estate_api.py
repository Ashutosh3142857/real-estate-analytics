import requests
import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random

# RapidAPI endpoints for real estate data
REALTY_MOLE_ENDPOINT = "https://realty-mole-property-api.p.rapidapi.com/properties"
REALTY_IN_US_ENDPOINT = "https://realty-in-us.p.rapidapi.com/properties/v2/list-for-sale"

def get_rapidapi_headers():
    """Get the headers needed for RapidAPI requests"""
    api_key = os.environ.get("RAPIDAPI_KEY")
    
    if not api_key:
        st.error("RapidAPI key not found. Please add your RAPIDAPI_KEY to the environment variables.")
        return None
    
    return {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "realty-mole-property-api.p.rapidapi.com"
    }

def search_properties_by_location(location, limit=10):
    """
    Search for properties by location (city, zip code, address, etc.)
    Returns a pandas DataFrame with property data
    Supports international searches with location format: 'City, Country'
    """
    headers = get_rapidapi_headers()
    
    if not headers:
        # If no API key, return an empty DataFrame
        return pd.DataFrame()
    
    # Update headers for the appropriate host
    if "," in location and any(country in location for country in 
                             ["UK", "France", "Germany", "Japan", "China", "Australia", 
                              "Brazil", "Canada", "Mexico", "India", "Singapore"]):
        # Use international API host for non-US locations
        headers["X-RapidAPI-Host"] = "realty-mole-property-api.p.rapidapi.com"
    
    params = {
        "address": location,
        "limit": limit
    }
    
    try:
        response = requests.get(REALTY_MOLE_ENDPOINT, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            if isinstance(data, list) and len(data) > 0:
                # Process the API data into a DataFrame
                properties = []
                for prop in data:
                    property_data = {
                        'property_id': prop.get('id', random.randint(10000, 99999)),
                        'address': prop.get('formattedAddress', 'Unknown Address'),
                        'city': prop.get('city', 'Unknown City'),
                        'state': prop.get('state', 'Unknown State'),
                        'zipcode': prop.get('zipCode', 'Unknown ZIP'),
                        'price': prop.get('price', 0),
                        'bedrooms': prop.get('bedrooms', 0),
                        'bathrooms': prop.get('bathrooms', 0),
                        'sqft': prop.get('squareFootage', 0),
                        'property_type': prop.get('propertyType', 'Unknown Type'),
                        'year_built': prop.get('yearBuilt', 2000),
                        'list_date': prop.get('listedDate', datetime.now().strftime('%Y-%m-%d')),
                        'latitude': prop.get('latitude', 0),
                        'longitude': prop.get('longitude', 0)
                    }
                    properties.append(property_data)
                
                df = pd.DataFrame(properties)
                
                # Add columns needed by the application if they don't exist
                if 'list_date' not in df.columns:
                    df['list_date'] = datetime.now().strftime('%Y-%m-%d')
                    
                # Add historical price data for market trends
                df = add_historical_prices(df)
                
                return df
            else:
                st.warning(f"No properties found for location: {location}")
                return pd.DataFrame()
        else:
            st.error(f"API request failed with status code: {response.status_code}")
            return pd.DataFrame()
    
    except Exception as e:
        st.error(f"Error fetching property data: {str(e)}")
        return pd.DataFrame()

def search_properties_zillow(location, limit=10):
    """
    Search for properties using the Zillow-like API (realty-in-us)
    Returns a pandas DataFrame with property data
    Supports international searches with location format: 'City, Country'
    """
    api_key = os.environ.get("RAPIDAPI_KEY")
    
    if not api_key:
        st.error("RapidAPI key not found. Please add your RAPIDAPI_KEY to the environment variables.")
        return pd.DataFrame()
    
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "realty-in-us.p.rapidapi.com"
    }
    
    # Parse location to handle international searches
    location_parts = location.split(',')
    city = location_parts[0].strip()
    
    # Extract country or state_code if provided
    country = ""
    state_code = ""
    if len(location_parts) > 1:
        country_or_state = location_parts[1].strip()
        # Check if it's a 2-letter state code
        if len(country_or_state) == 2 and country_or_state.isalpha():
            state_code = country_or_state
        else:
            country = country_or_state
    
    params = {
        "city": city,
        "limit": limit,
        "offset": "0",
        "state_code": state_code,
        "sort": "relevance",
        "country": country
    }
    
    try:
        response = requests.get(REALTY_IN_US_ENDPOINT, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'properties' in data and len(data['properties']) > 0:
                # Process the API data into a DataFrame
                properties = []
                for prop in data['properties']:
                    property_data = {
                        'property_id': prop.get('property_id', random.randint(10000, 99999)),
                        'address': f"{prop.get('address', {}).get('line', 'Unknown Address')}",
                        'city': prop.get('address', {}).get('city', 'Unknown City'),
                        'state': prop.get('address', {}).get('state_code', 'Unknown State'),
                        'zipcode': prop.get('address', {}).get('postal_code', 'Unknown ZIP'),
                        'price': prop.get('price', 0),
                        'bedrooms': prop.get('beds', 0),
                        'bathrooms': prop.get('baths', 0),
                        'sqft': prop.get('building_size', {}).get('size', 0),
                        'property_type': prop.get('prop_type', 'Unknown Type'),
                        'year_built': prop.get('year_built', 2000),
                        'list_date': datetime.now().strftime('%Y-%m-%d'),
                        'latitude': prop.get('address', {}).get('lat', 0),
                        'longitude': prop.get('address', {}).get('lon', 0)
                    }
                    properties.append(property_data)
                
                df = pd.DataFrame(properties)
                
                # Add historical price data for market trends
                df = add_historical_prices(df)
                
                return df
            else:
                st.warning(f"No properties found for location: {location}")
                return pd.DataFrame()
        else:
            st.error(f"API request failed with status code: {response.status_code}")
            return pd.DataFrame()
    
    except Exception as e:
        st.error(f"Error fetching property data: {str(e)}")
        return pd.DataFrame()

def add_historical_prices(df):
    """
    Add simulated historical price data for market trend analysis
    This function is from the existing utils/data_processing.py but included here
    for when we work with real API data
    """
    # Create a copy to avoid modifying the original dataframe
    result_df = df.copy()
    
    # Number of months to generate historical data for
    history_months = 24
    
    # Create columns for historical data
    for i in range(1, history_months + 1):
        month_date = (datetime.now() - timedelta(days=30 * i)).strftime('%Y-%m-%d')
        col_name = f'price_{i}m_ago'
        
        # Generate price variations (generally lower in the past)
        # The further back in time, the lower the price on average (simulating appreciation)
        appreciation_factor = 1 - (0.02 * i)  # e.g., 2% lower per month going back
        
        # Add some randomness to each property's appreciation
        result_df[col_name] = result_df['price'].apply(
            lambda x: int(x * appreciation_factor * random.uniform(0.95, 1.05))
        )
        
    return result_df

def get_location_suggestions(query):
    """
    Get location suggestions based on user input
    Returns a list of location suggestions including international locations
    """
    api_key = os.environ.get("RAPIDAPI_KEY")
    
    if not api_key:
        return []
    
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "realty-in-us.p.rapidapi.com"
    }
    
    params = {
        "q": query
    }
    
    try:
        # First try the US API for location suggestions
        response = requests.get(
            "https://realty-in-us.p.rapidapi.com/locations/auto-complete",
            headers=headers, 
            params=params
        )
        
        suggestions = []
        
        if response.status_code == 200:
            data = response.json()
            
            if 'autocomplete' in data:
                for item in data['autocomplete']:
                    suggestions.append(item.get('city', '') + ', ' + item.get('state_code', ''))
        
        # Supplement with global major cities if the query might be international
        if len(query) >= 3 and (len(suggestions) < 5 or any(
                country in query.lower() for country in 
                ["uk", "france", "germany", "japan", "china", "australia", "canada", 
                 "brazil", "mexico", "india", "singapore", "europe", "asia", "africa"]
            )):
            # Major global cities by continent
            global_cities = {
                "Europe": ["London, UK", "Paris, France", "Berlin, Germany", "Rome, Italy", 
                          "Madrid, Spain", "Amsterdam, Netherlands", "Vienna, Austria", 
                          "Moscow, Russia", "Stockholm, Sweden", "Athens, Greece"],
                "Asia": ["Tokyo, Japan", "Shanghai, China", "Singapore", "Seoul, South Korea", 
                        "Mumbai, India", "Bangkok, Thailand", "Dubai, UAE", 
                        "Hong Kong", "Beijing, China", "Istanbul, Turkey"],
                "Oceania": ["Sydney, Australia", "Melbourne, Australia", "Auckland, New Zealand", 
                           "Wellington, New Zealand", "Brisbane, Australia", "Perth, Australia"],
                "South America": ["Rio de Janeiro, Brazil", "Buenos Aires, Argentina", "Lima, Peru", 
                                 "Santiago, Chile", "Bogota, Colombia", "Sao Paulo, Brazil"],
                "Africa": ["Cape Town, South Africa", "Nairobi, Kenya", "Cairo, Egypt", 
                          "Johannesburg, South Africa", "Casablanca, Morocco", "Lagos, Nigeria"],
                "North America": ["Toronto, Canada", "Vancouver, Canada", "Montreal, Canada", 
                                 "Mexico City, Mexico", "Cancun, Mexico", "Ottawa, Canada"]
            }
            
            # Add matching global cities to suggestions
            for continent, cities in global_cities.items():
                for city in cities:
                    if query.lower() in city.lower() or query.lower() in continent.lower():
                        suggestions.append(city)
            
        return suggestions
    
    except Exception:
        return []