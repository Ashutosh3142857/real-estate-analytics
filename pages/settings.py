import streamlit as st
import os
from dotenv import load_dotenv
import json
import requests
from utils.api_manager import check_api_keys
from utils.database_init import initialize_database

def show_settings():
    """Settings page for API keys and application configuration"""
    st.title("Settings & API Keys")
    
    st.write("""
    ## API Keys Configuration
    
    This application uses external APIs to provide real-time real estate data. 
    To use these features, you'll need to provide your own API keys.
    """)
    
    # Check which API keys are missing
    missing_keys = check_api_keys()
    
    # Show API key input fields
    with st.form("api_keys_form"):
        st.subheader("RapidAPI Key")
        st.write("""
        This key is used for accessing real estate listing data, property details, 
        and location services. [Get a RapidAPI key](https://rapidapi.com/)
        """)
        
        rapidapi_key = st.text_input(
            "RapidAPI Key",
            value=os.getenv("RAPIDAPI_KEY", ""),
            type="password",
            help="Enter your RapidAPI key for accessing real estate data APIs"
        )
        
        st.subheader("Google Maps API Key")
        st.write("""
        This key is used for enhanced mapping features and geocoding.
        [Get a Google Maps API key](https://developers.google.com/maps/documentation/javascript/get-api-key)
        """)
        
        google_maps_key = st.text_input(
            "Google Maps API Key",
            value=os.getenv("GOOGLE_MAPS_API_KEY", ""),
            type="password",
            help="Enter your Google Maps API key"
        )
        
        st.subheader("OpenAI API Key")
        st.write("""
        This key is used for AI-powered features like property description generation and market insights.
        [Get an OpenAI API key](https://platform.openai.com/signup)
        """)
        
        openai_key = st.text_input(
            "OpenAI API Key",
            value=os.getenv("OPENAI_API_KEY", ""),
            type="password",
            help="Enter your OpenAI API key"
        )
        
        st.subheader("Zillow API Key")
        st.write("""
        This key is used for additional property data and valuation information.
        [Get a Zillow API key](https://rapidapi.com/apimaker/api/zillow-com1/)
        """)
        
        zillow_key = st.text_input(
            "Zillow API Key",
            value=os.getenv("ZILLOW_API_KEY", ""),
            type="password",
            help="Enter your Zillow API key"
        )
        
        # Submit button
        submitted = st.form_submit_button("Save API Keys")
        
        if submitted:
            # In a production environment, these would be stored securely
            # For this demo, we'll store them as environment variables
            temp_env_file = """# API Keys
RAPIDAPI_KEY="{}"
GOOGLE_MAPS_API_KEY="{}"
OPENAI_API_KEY="{}"
ZILLOW_API_KEY="{}"
"""
            
            # Write to .env file
            with open(".env", "w") as f:
                f.write(temp_env_file.format(
                    rapidapi_key,
                    google_maps_key,
                    openai_key,
                    zillow_key
                ))
            
            # Reload environment variables
            load_dotenv(override=True)
            
            st.success("API Keys saved successfully! You may need to restart the application for changes to take effect.")
            
    # Database management section
    st.write("---")
    st.subheader("Database Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Initialize Database"):
            with st.spinner("Initializing database..."):
                success = initialize_database()
                if success:
                    st.success("Database initialized successfully!")
                else:
                    st.error("Failed to initialize database. Check logs for details.")
    
    with col2:
        if st.button("Test Database Connection"):
            with st.spinner("Testing database connection..."):
                try:
                    from utils.database import get_session
                    session = get_session()
                    session.execute("SELECT 1")
                    session.close()
                    st.success("Database connection successful!")
                except Exception as e:
                    st.error(f"Database connection failed: {str(e)}")
    
    # Test API connections
    st.write("---")
    st.subheader("Test API Connections")
    
    if st.button("Test RapidAPI Connection"):
        with st.spinner("Testing RapidAPI connection..."):
            rapidapi_key = os.getenv("RAPIDAPI_KEY")
            if not rapidapi_key:
                st.error("RapidAPI key not configured")
            else:
                try:
                    headers = {
                        "X-RapidAPI-Key": rapidapi_key,
                        "X-RapidAPI-Host": "realty-in-us.p.rapidapi.com"
                    }
                    
                    response = requests.get(
                        "https://realty-in-us.p.rapidapi.com/locations/auto-complete",
                        headers=headers,
                        params={"q": "New York"}
                    )
                    
                    if response.status_code == 200:
                        st.success("RapidAPI connection successful!")
                        with st.expander("API Response Sample"):
                            st.json(response.json())
                    else:
                        st.error(f"RapidAPI connection failed with status code: {response.status_code}")
                        st.write(response.text)
                except Exception as e:
                    st.error(f"RapidAPI connection error: {str(e)}")
                
    # Application performance metrics (in a real app, these would be populated from actual usage data)
    st.write("---")
    st.subheader("Application Performance")
    
    metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
    
    with metrics_col1:
        st.metric("API Requests Today", "0")
    
    with metrics_col2:
        st.metric("Database Size", "0 MB")
    
    with metrics_col3:
        st.metric("Active Users", "1")