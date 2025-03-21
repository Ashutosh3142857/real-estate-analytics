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

        st.write("---")
        st.subheader("Messaging Integration Settings")
        
        # Email configuration tab
        st.write("### Email Service Configuration")
        st.write("Configure SMTP settings for email messaging")
        
        smtp_server = st.text_input(
            "SMTP Server",
            value=os.getenv("SMTP_SERVER", ""),
            help="Enter your SMTP server address (e.g., smtp.gmail.com)"
        )
        
        smtp_port = st.text_input(
            "SMTP Port",
            value=os.getenv("SMTP_PORT", "587"),
            help="Enter your SMTP server port (e.g., 587 for TLS)"
        )
        
        smtp_username = st.text_input(
            "SMTP Username",
            value=os.getenv("SMTP_USERNAME", ""),
            help="Enter your SMTP username (usually your email address)"
        )
        
        smtp_password = st.text_input(
            "SMTP Password",
            value=os.getenv("SMTP_PASSWORD", ""),
            type="password",
            help="Enter your SMTP password or app password"
        )
        
        sender_email = st.text_input(
            "Sender Email",
            value=os.getenv("SENDER_EMAIL", ""),
            help="Enter the email address to send from"
        )
        
        sender_name = st.text_input(
            "Sender Name",
            value=os.getenv("SENDER_NAME", "Real Estate Analytics"),
            help="Enter the sender name to display in emails"
        )
        
        # WhatsApp Business API Configuration
        st.write("### WhatsApp Business API Configuration")
        st.write("Configure WhatsApp Business API access for WhatsApp messaging")
        
        whatsapp_phone_number_id = st.text_input(
            "WhatsApp Phone Number ID",
            value=os.getenv("WHATSAPP_PHONE_NUMBER_ID", ""),
            help="Enter your WhatsApp Phone Number ID from Meta Developer Dashboard"
        )
        
        whatsapp_business_account_id = st.text_input(
            "WhatsApp Business Account ID",
            value=os.getenv("WHATSAPP_BUSINESS_ACCOUNT_ID", ""),
            help="Enter your WhatsApp Business Account ID from Meta Developer Dashboard"
        )
        
        whatsapp_access_token = st.text_input(
            "WhatsApp Access Token",
            value=os.getenv("WHATSAPP_ACCESS_TOKEN", ""),
            type="password",
            help="Enter your WhatsApp Business API access token"
        )
        
        # Twilio SMS Configuration
        st.write("### Twilio SMS Configuration")
        st.write("Configure Twilio for SMS messaging")
        
        twilio_account_sid = st.text_input(
            "Twilio Account SID",
            value=os.getenv("TWILIO_ACCOUNT_SID", ""),
            help="Enter your Twilio Account SID from Twilio Dashboard"
        )
        
        twilio_auth_token = st.text_input(
            "Twilio Auth Token",
            value=os.getenv("TWILIO_AUTH_TOKEN", ""),
            type="password",
            help="Enter your Twilio Auth Token from Twilio Dashboard"
        )
        
        twilio_phone_number = st.text_input(
            "Twilio Phone Number",
            value=os.getenv("TWILIO_PHONE_NUMBER", ""),
            help="Enter your Twilio Phone Number with country code (e.g., +15551234567)"
        )
        
        # Submit button
        submitted = st.form_submit_button("Save All Settings")
        
        if submitted:
            # In a production environment, these would be stored securely
            # For this demo, we'll store them as environment variables
            temp_env_file = """# API Keys
RAPIDAPI_KEY="{}"
GOOGLE_MAPS_API_KEY="{}"
OPENAI_API_KEY="{}"
ZILLOW_API_KEY="{}"

# Email Settings
SMTP_SERVER="{}"
SMTP_PORT="{}"
SMTP_USERNAME="{}"
SMTP_PASSWORD="{}"
SENDER_EMAIL="{}"
SENDER_NAME="{}"

# WhatsApp Settings
WHATSAPP_PHONE_NUMBER_ID="{}"
WHATSAPP_BUSINESS_ACCOUNT_ID="{}"
WHATSAPP_ACCESS_TOKEN="{}"

# Twilio Settings
TWILIO_ACCOUNT_SID="{}"
TWILIO_AUTH_TOKEN="{}"
TWILIO_PHONE_NUMBER="{}"
"""
            
            # Write to .env file
            with open(".env", "w") as f:
                f.write(temp_env_file.format(
                    rapidapi_key,
                    google_maps_key,
                    openai_key,
                    zillow_key,
                    smtp_server,
                    smtp_port,
                    smtp_username,
                    smtp_password,
                    sender_email,
                    sender_name,
                    whatsapp_phone_number_id,
                    whatsapp_business_account_id,
                    whatsapp_access_token,
                    twilio_account_sid,
                    twilio_auth_token,
                    twilio_phone_number
                ))
            
            # Reload environment variables
            load_dotenv(override=True)
            
            st.success("All settings saved successfully! You may need to restart the application for changes to take effect.")
            
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
    
    # Test API and messaging connections
    st.write("---")
    st.subheader("Test Connections")
    
    # Add tabs for different connection tests
    api_tab, email_tab, whatsapp_tab, sms_tab = st.tabs(["API", "Email", "WhatsApp", "SMS"])
    
    with api_tab:
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
    
    with email_tab:
        st.write("Test the email configuration by sending a test email")
        
        test_recipient = st.text_input("Test Email Recipient")
        
        if st.button("Send Test Email"):
            if not test_recipient:
                st.error("Please enter a recipient email address")
            else:
                try:
                    with st.spinner("Sending test email..."):
                        # Import email sending function
                        from utils.email_service import send_email, get_available_email_providers
                        
                        # Check for available email providers
                        providers = get_available_email_providers()
                        
                        if not providers:
                            st.error("No email providers configured. Please set up your SMTP settings.")
                        else:
                            # Send test email
                            test_html = f"""
                            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                                <h2 style="color: #4285f4;">Email Configuration Test</h2>
                                <p>This is a test email from your Real Estate Analytics application.</p>
                                <p>If you're receiving this email, your email configuration is working correctly!</p>
                                <p>Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                            </div>
                            """
                            
                            result = send_email(
                                providers[0],
                                [test_recipient],
                                "Test Email from Real Estate Analytics",
                                test_html,
                                "This is a test email from your Real Estate Analytics application."
                            )
                            
                            if result.get("success"):
                                st.success("Test email sent successfully!")
                            else:
                                st.error(f"Failed to send test email: {result.get('message', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Error sending test email: {str(e)}")
    
    with whatsapp_tab:
        st.write("Test the WhatsApp configuration by sending a test message")
        
        test_phone = st.text_input("Test Phone Number (with country code)", placeholder="+15551234567")
        
        if st.button("Send Test WhatsApp Message"):
            if not test_phone:
                st.error("Please enter a recipient phone number")
            else:
                try:
                    with st.spinner("Sending test WhatsApp message..."):
                        # Import WhatsApp sending function
                        from utils.whatsapp_service import send_whatsapp_message, check_whatsapp_credentials
                        
                        # Check WhatsApp credentials
                        creds = check_whatsapp_credentials()
                        
                        if not creds.get("configured"):
                            st.error("WhatsApp Business API not configured. Please set up your WhatsApp settings.")
                        else:
                            # Send test message
                            test_message = f"This is a test message from your Real Estate Analytics application. Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                            
                            result = send_whatsapp_message(test_phone, test_message)
                            
                            if result.get("success"):
                                st.success("Test WhatsApp message sent successfully!")
                            else:
                                st.error(f"Failed to send test WhatsApp message: {result.get('message', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Error sending test WhatsApp message: {str(e)}")
    
    with sms_tab:
        st.write("Test the SMS configuration by sending a test message")
        
        test_sms_phone = st.text_input("Test Phone Number for SMS (with country code)", placeholder="+15551234567")
        
        if st.button("Send Test SMS"):
            if not test_sms_phone:
                st.error("Please enter a recipient phone number")
            else:
                try:
                    with st.spinner("Sending test SMS..."):
                        # Import SMS sending function
                        from utils.sms_service import send_sms, check_sms_credentials
                        
                        # Check SMS credentials
                        creds = check_sms_credentials()
                        
                        if not creds.get("configured"):
                            st.error("Twilio SMS not configured. Please set up your Twilio settings.")
                        else:
                            # Send test message
                            test_message = f"Test SMS from Real Estate Analytics. Test completed at: {datetime.now().strftime('%H:%M:%S')}"
                            
                            result = send_sms(test_sms_phone, test_message)
                            
                            if result.get("success"):
                                st.success("Test SMS sent successfully!")
                            else:
                                st.error(f"Failed to send test SMS: {result.get('message', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Error sending test SMS: {str(e)}")
                
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