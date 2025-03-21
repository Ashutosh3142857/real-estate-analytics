import os
import streamlit as st
from dotenv import load_dotenv
import json
import requests
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# API Keys and service configuration
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
ZILLOW_API_KEY = os.getenv("ZILLOW_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# API endpoints and hosts
REALTY_API_HOST = "realty-in-us.p.rapidapi.com"
PROPERTY_API_HOST = "zillow-com1.p.rapidapi.com"
REALTOR_API_HOST = "realtor.p.rapidapi.com"

def check_api_keys():
    """Check if required API keys are available"""
    missing_keys = []
    
    if not RAPIDAPI_KEY:
        missing_keys.append("RAPIDAPI_KEY")
    if not GOOGLE_MAPS_API_KEY:
        missing_keys.append("GOOGLE_MAPS_API_KEY")
    if not ZILLOW_API_KEY:
        missing_keys.append("ZILLOW_API_KEY")
    if not OPENAI_API_KEY:
        missing_keys.append("OPENAI_API_KEY")
        
    return missing_keys

def get_rapidapi_headers(host=REALTY_API_HOST):
    """Get the headers needed for RapidAPI requests"""
    return {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": host
    }

def make_api_request(url, headers, params=None, method="GET"):
    """
    Make API request with error handling and rate limiting
    
    Args:
        url (str): API endpoint URL
        headers (dict): Request headers
        params (dict, optional): Query parameters
        method (str): HTTP method (GET, POST)
        
    Returns:
        dict: API response
    """
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        else:  # POST
            response = requests.post(url, headers=headers, json=params)
            
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        if response.status_code == 429:
            # Handle rate limiting
            st.error("API rate limit exceeded. Please try again later.")
        elif response.status_code == 401:
            # Handle authentication error
            st.error("API authentication failed. Please check your API key.")
        else:
            st.error(f"HTTP Error: {err}")
        return None
    except requests.exceptions.RequestException as err:
        st.error(f"Request Error: {err}")
        return None
    except json.JSONDecodeError:
        st.error("Error parsing API response")
        return None

def cache_api_response(function_name, params, response, expiration_hours=24):
    """
    Cache API response to minimize API calls
    
    Args:
        function_name (str): Name of the function making the API call
        params (dict): Parameters used for the API call
        response (dict): API response to cache
        expiration_hours (int): Cache expiration time in hours
        
    Returns:
        None
    """
    # Convert params to string for cache key
    params_str = json.dumps(params, sort_keys=True)
    
    # Create cache key
    cache_key = f"{function_name}:{params_str}"
    
    # Create cache entry with expiration
    cache_entry = {
        "data": response,
        "expires_at": (datetime.now() + timedelta(hours=expiration_hours)).isoformat()
    }
    
    # Store in Streamlit session state as cache
    if "api_cache" not in st.session_state:
        st.session_state.api_cache = {}
    
    st.session_state.api_cache[cache_key] = cache_entry

def get_cached_response(function_name, params):
    """
    Get cached API response if available and not expired
    
    Args:
        function_name (str): Name of the function making the API call
        params (dict): Parameters used for the API call
        
    Returns:
        dict or None: Cached response or None if not available/expired
    """
    if "api_cache" not in st.session_state:
        return None
    
    # Convert params to string for cache key
    params_str = json.dumps(params, sort_keys=True)
    
    # Create cache key
    cache_key = f"{function_name}:{params_str}"
    
    # Check if cache entry exists
    if cache_key not in st.session_state.api_cache:
        return None
    
    # Get cache entry
    cache_entry = st.session_state.api_cache[cache_key]
    
    # Check if expired
    expires_at = datetime.fromisoformat(cache_entry["expires_at"])
    if datetime.now() > expires_at:
        # Remove expired entry
        del st.session_state.api_cache[cache_key]
        return None
    
    return cache_entry["data"]