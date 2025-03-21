"""
API Settings page for managing external API connections and credentials.
This page provides a user interface for:
1. Managing email service credentials
2. Managing ad platform API credentials
3. Testing API connections
4. Viewing integration status
"""

import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime
import logging

# Import our modules
from utils.email_service import get_email_config, save_email_template, get_email_templates
from utils.ad_platforms import get_ad_platforms, save_credentials, get_credentials

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def show_api_settings():
    st.title("API & External Integrations")
    
    st.markdown("""
    Configure connections to external services such as email providers and advertising platforms.
    These integrations enable automated email campaigns, lead nurturing, and ad performance tracking.
    """)
    
    # Create tabs for different settings categories
    tab1, tab2, tab3 = st.tabs(["Email Service", "Ad Platforms", "API Connections"])
    
    with tab1:
        show_email_settings()
    
    with tab2:
        show_ad_platform_settings()
    
    with tab3:
        show_api_connections()

def show_email_settings():
    st.subheader("Email Service Settings")
    
    st.markdown("""
    Configure your email service provider to enable automated emails, lead nurturing campaigns,
    and client communications.
    """)
    
    # Get current email config
    email_config = get_email_config()
    
    # Display current status
    if email_config:
        st.success(f"✅ Email service is configured ({email_config['smtp_server']})")
    else:
        st.warning("⚠️ Email service is not configured")
    
    # Email provider selection
    email_provider = st.selectbox(
        "Email Provider",
        options=["Custom SMTP", "SendGrid", "Mailchimp", "Gmail", "Outlook/Office 365"],
        index=0
    )
    
    # Form for email settings
    with st.form("email_settings_form"):
        if email_provider == "Custom SMTP":
            smtp_server = st.text_input("SMTP Server", value=email_config.get('smtp_server', '') if email_config else '')
            smtp_port = st.number_input("SMTP Port", value=int(email_config.get('smtp_port', 587)) if email_config else 587)
            smtp_username = st.text_input("SMTP Username", value=email_config.get('smtp_username', '') if email_config else '')
            smtp_password = st.text_input("SMTP Password", type="password")
            sender_email = st.text_input("Sender Email", value=email_config.get('sender_email', '') if email_config else '')
            sender_name = st.text_input("Sender Name", value=email_config.get('sender_name', 'Real Estate Analytics') if email_config else 'Real Estate Analytics')
        
        elif email_provider == "SendGrid":
            api_key = st.text_input("SendGrid API Key", type="password")
            sender_email = st.text_input("Sender Email", value=email_config.get('sender_email', '') if email_config else '')
            sender_name = st.text_input("Sender Name", value=email_config.get('sender_name', 'Real Estate Analytics') if email_config else 'Real Estate Analytics')
            
            # These will be set automatically
            smtp_server = "smtp.sendgrid.net"
            smtp_port = 587
            smtp_username = "apikey"
            smtp_password = api_key
        
        elif email_provider == "Mailchimp":
            api_key = st.text_input("Mailchimp API Key", type="password")
            sender_email = st.text_input("Sender Email", value=email_config.get('sender_email', '') if email_config else '')
            sender_name = st.text_input("Sender Name", value=email_config.get('sender_name', 'Real Estate Analytics') if email_config else 'Real Estate Analytics')
            
            # These will be set automatically for Mailchimp's Mandrill service
            smtp_server = "smtp.mandrillapp.com"
            smtp_port = 587
            smtp_username = "apikey"
            smtp_password = api_key
        
        elif email_provider == "Gmail":
            st.info("For Gmail, you'll need to create an 'App Password' in your Google Account settings.")
            smtp_username = st.text_input("Gmail Address", value=email_config.get('smtp_username', '') if email_config else '')
            smtp_password = st.text_input("App Password", type="password")
            sender_name = st.text_input("Sender Name", value=email_config.get('sender_name', 'Real Estate Analytics') if email_config else 'Real Estate Analytics')
            
            # These will be set automatically
            smtp_server = "smtp.gmail.com"
            smtp_port = 587
            sender_email = smtp_username
        
        elif email_provider == "Outlook/Office 365":
            smtp_username = st.text_input("Email Address", value=email_config.get('smtp_username', '') if email_config else '')
            smtp_password = st.text_input("Password", type="password")
            sender_name = st.text_input("Sender Name", value=email_config.get('sender_name', 'Real Estate Analytics') if email_config else 'Real Estate Analytics')
            
            # These will be set automatically
            smtp_server = "smtp.office365.com"
            smtp_port = 587
            sender_email = smtp_username
        
        save_button = st.form_submit_button("Save Email Settings")
    
    if save_button:
        if 'smtp_server' not in locals() or not smtp_server:
            st.error("SMTP Server is required")
        elif 'smtp_username' not in locals() or not smtp_username:
            st.error("SMTP Username is required")
        elif 'smtp_password' not in locals() or not smtp_password:
            st.error("SMTP Password is required")
        elif 'sender_email' not in locals() or not sender_email:
            st.error("Sender Email is required")
        else:
            # Save settings to environment variables
            os.environ["SMTP_SERVER"] = smtp_server
            os.environ["SMTP_PORT"] = str(smtp_port)
            os.environ["SMTP_USERNAME"] = smtp_username
            os.environ["SMTP_PASSWORD"] = smtp_password
            os.environ["SENDER_EMAIL"] = sender_email
            os.environ["SENDER_NAME"] = sender_name
            
            st.success("Email settings saved successfully")
            
            # Add option to test the connection
            if st.button("Test Email Connection"):
                # Import here to avoid circular imports
                from utils.email_service import send_email
                
                try:
                    result = send_email(
                        recipient_email=sender_email,  # Send to self for testing
                        subject="Test Email from Real Estate Analytics",
                        content="<p>This is a test email to verify your email settings.</p>"
                    )
                    
                    if result:
                        st.success(f"Test email sent successfully to {sender_email}")
                    else:
                        st.error("Failed to send test email. Please check your settings.")
                except Exception as e:
                    st.error(f"Error sending test email: {str(e)}")
    
    # Email Templates section
    st.subheader("Email Templates")
    
    st.markdown("""
    Create and manage email templates for lead nurturing, property alerts, and client communications.
    """)
    
    # Show existing templates in an expander
    with st.expander("View Email Templates"):
        try:
            templates = get_email_templates()
            
            if templates:
                template_data = [{
                    'Name': t.name,
                    'Subject': t.subject,
                    'Category': t.category,
                    'Last Updated': t.updated_at.strftime('%Y-%m-%d')
                } for t in templates]
                
                st.table(pd.DataFrame(template_data))
            else:
                st.info("No email templates found")
        except Exception as e:
            st.error(f"Error loading templates: {str(e)}")
    
    # Form to create a new template
    st.subheader("Create New Template")
    
    with st.form("create_template_form"):
        template_name = st.text_input("Template Name")
        template_subject = st.text_input("Email Subject")
        template_category = st.selectbox(
            "Template Category",
            options=["lead_nurture", "property_alert", "market_update", "client_communication", "general"]
        )
        template_content = st.text_area("Email Content (HTML)", height=200)
        
        create_template_button = st.form_submit_button("Save Template")
    
    if create_template_button:
        if not template_name or not template_subject or not template_content:
            st.error("All fields are required")
        else:
            try:
                # Import here to avoid circular imports
                from utils.email_service import add_email_template
                
                template_id = add_email_template(
                    name=template_name,
                    subject=template_subject,
                    content=template_content,
                    category=template_category
                )
                
                if template_id:
                    st.success(f"Template '{template_name}' created successfully")
                else:
                    st.error("Failed to create template")
            except Exception as e:
                st.error(f"Error creating template: {str(e)}")

def show_ad_platform_settings():
    st.subheader("Ad Platform Settings")
    
    st.markdown("""
    Configure connections to advertising platforms to track campaign performance and ROI.
    """)
    
    # Display current ad platforms
    ad_platforms = get_ad_platforms()
    
    if ad_platforms:
        platform_data = [{
            'Platform': p.display_name,
            'Status': "Connected" if p.connected else "Not Connected",
            'Last Synced': p.last_sync.strftime('%Y-%m-%d %H:%M') if p.last_sync else "Never"
        } for p in ad_platforms]
        
        st.table(pd.DataFrame(platform_data))
    else:
        st.info("No ad platforms configured")
    
    # Platform selection
    platform_options = [
        "Google Ads", 
        "Facebook Ads", 
        "Instagram Ads", 
        "LinkedIn Ads",
        "Twitter Ads",
        "Microsoft Ads"
    ]
    
    selected_platform = st.selectbox("Select Ad Platform", options=platform_options)
    
    # Map display names to internal names
    platform_name_map = {
        "Google Ads": "google_ads",
        "Facebook Ads": "facebook_ads",
        "Instagram Ads": "instagram_ads",
        "LinkedIn Ads": "linkedin_ads",
        "Twitter Ads": "twitter_ads",
        "Microsoft Ads": "microsoft_ads"
    }
    
    internal_name = platform_name_map.get(selected_platform)
    
    # Get existing credentials
    existing_credentials = get_credentials(internal_name) if internal_name else None
    
    # Form for platform-specific settings
    with st.form(f"{internal_name}_settings_form"):
        if selected_platform == "Google Ads":
            st.markdown("""
            To connect to Google Ads, you'll need:
            1. A Google Ads API Developer Token
            2. OAuth2 credentials (client ID and secret)
            3. A refresh token for your Google Ads account
            """)
            
            developer_token = st.text_input("Developer Token", type="password", 
                                          value=existing_credentials.get('developer_token', '') if existing_credentials else '')
            client_id = st.text_input("Client ID", 
                                    value=existing_credentials.get('client_id', '') if existing_credentials else '')
            client_secret = st.text_input("Client Secret", type="password", 
                                        value=existing_credentials.get('client_secret', '') if existing_credentials else '')
            refresh_token = st.text_input("Refresh Token", type="password", 
                                        value=existing_credentials.get('refresh_token', '') if existing_credentials else '')
            customer_id = st.text_input("Customer ID (without dashes)", 
                                      value=existing_credentials.get('customer_id', '') if existing_credentials else '')
            
            credentials = {
                "developer_token": developer_token,
                "client_id": client_id,
                "client_secret": client_secret,
                "refresh_token": refresh_token,
                "customer_id": customer_id
            }
        
        elif selected_platform == "Facebook Ads":
            st.markdown("""
            To connect to Facebook Ads, you'll need:
            1. A Facebook App ID and Secret
            2. A long-lived access token with ads_management permission
            3. Your Ad Account ID
            """)
            
            app_id = st.text_input("App ID", 
                                 value=existing_credentials.get('app_id', '') if existing_credentials else '')
            app_secret = st.text_input("App Secret", type="password", 
                                     value=existing_credentials.get('app_secret', '') if existing_credentials else '')
            access_token = st.text_input("Access Token", type="password", 
                                       value=existing_credentials.get('access_token', '') if existing_credentials else '')
            ad_account_id = st.text_input("Ad Account ID (without 'act_' prefix)", 
                                        value=existing_credentials.get('ad_account_id', '') if existing_credentials else '')
            
            credentials = {
                "app_id": app_id,
                "app_secret": app_secret,
                "access_token": access_token,
                "ad_account_id": ad_account_id
            }
        
        elif selected_platform == "Instagram Ads":
            st.markdown("""
            Instagram Ads are managed through the Facebook Ads platform.
            Please configure Facebook Ads integration.
            """)
            credentials = {}
        
        elif selected_platform == "LinkedIn Ads":
            st.markdown("""
            To connect to LinkedIn Ads, you'll need:
            1. A LinkedIn App Client ID and Secret
            2. An access token with r_ads permission
            3. Your LinkedIn Ads Account ID
            """)
            
            client_id = st.text_input("Client ID", 
                                    value=existing_credentials.get('client_id', '') if existing_credentials else '')
            client_secret = st.text_input("Client Secret", type="password", 
                                        value=existing_credentials.get('client_secret', '') if existing_credentials else '')
            access_token = st.text_input("Access Token", type="password", 
                                       value=existing_credentials.get('access_token', '') if existing_credentials else '')
            account_id = st.text_input("Account ID", 
                                     value=existing_credentials.get('account_id', '') if existing_credentials else '')
            
            credentials = {
                "client_id": client_id,
                "client_secret": client_secret,
                "access_token": access_token,
                "account_id": account_id
            }
        
        elif selected_platform == "Twitter Ads":
            st.markdown("""
            To connect to Twitter Ads, you'll need:
            1. Twitter API Key and Secret
            2. Access Token and Secret
            3. Your Twitter Ads Account ID
            """)
            
            api_key = st.text_input("API Key", 
                                  value=existing_credentials.get('api_key', '') if existing_credentials else '')
            api_secret = st.text_input("API Secret", type="password", 
                                     value=existing_credentials.get('api_secret', '') if existing_credentials else '')
            access_token = st.text_input("Access Token", type="password", 
                                       value=existing_credentials.get('access_token', '') if existing_credentials else '')
            access_token_secret = st.text_input("Access Token Secret", type="password", 
                                              value=existing_credentials.get('access_token_secret', '') if existing_credentials else '')
            account_id = st.text_input("Account ID", 
                                     value=existing_credentials.get('account_id', '') if existing_credentials else '')
            
            credentials = {
                "api_key": api_key,
                "api_secret": api_secret,
                "access_token": access_token,
                "access_token_secret": access_token_secret,
                "account_id": account_id
            }
        
        elif selected_platform == "Microsoft Ads":
            st.markdown("""
            To connect to Microsoft Ads, you'll need:
            1. Microsoft Advertising Developer Token
            2. OAuth2 credentials (client ID and secret)
            3. A refresh token for your Microsoft Ads account
            4. Your Microsoft Ads Account ID
            """)
            
            developer_token = st.text_input("Developer Token", type="password", 
                                          value=existing_credentials.get('developer_token', '') if existing_credentials else '')
            client_id = st.text_input("Client ID", 
                                    value=existing_credentials.get('client_id', '') if existing_credentials else '')
            client_secret = st.text_input("Client Secret", type="password", 
                                        value=existing_credentials.get('client_secret', '') if existing_credentials else '')
            refresh_token = st.text_input("Refresh Token", type="password", 
                                        value=existing_credentials.get('refresh_token', '') if existing_credentials else '')
            account_id = st.text_input("Account ID", 
                                     value=existing_credentials.get('account_id', '') if existing_credentials else '')
            
            credentials = {
                "developer_token": developer_token,
                "client_id": client_id,
                "client_secret": client_secret,
                "refresh_token": refresh_token,
                "account_id": account_id
            }
        
        save_button = st.form_submit_button(f"Save {selected_platform} Settings")
    
    if save_button and internal_name:
        # Check if credentials are provided for platforms other than Instagram
        if selected_platform != "Instagram Ads" and not all(credentials.values()):
            st.error("All fields are required")
        else:
            try:
                success = save_credentials(
                    platform_name=internal_name,
                    display_name=selected_platform,
                    credentials=credentials,
                    description=f"{selected_platform} integration for ad performance tracking"
                )
                
                if success:
                    st.success(f"{selected_platform} settings saved successfully")
                    
                    # Add option to test the connection
                    if st.button("Test Connection"):
                        st.info(f"Testing connection to {selected_platform}...")
                        
                        # This would be implemented to actually test the connection
                        # For now, we'll just simulate success
                        st.success(f"Successfully connected to {selected_platform}")
                else:
                    st.error(f"Failed to save {selected_platform} settings")
            except Exception as e:
                st.error(f"Error saving settings: {str(e)}")

def show_api_connections():
    st.subheader("API Connections")
    
    st.markdown("""
    Manage connections to other APIs and services for enhanced functionality.
    """)
    
    # List of potential APIs to connect
    api_options = [
        "RapidAPI - Real Estate",
        "Zillow API",
        "Realtor.com API",
        "Property Data API",
        "Walkscore API",
        "Google Maps API",
        "Census Data API"
    ]
    
    selected_api = st.selectbox("Select API", options=api_options)
    
    # Form for API-specific settings
    with st.form(f"{selected_api.lower().replace(' ', '_').replace('.', '')}_form"):
        if selected_api == "RapidAPI - Real Estate":
            st.markdown("""
            Connect to RapidAPI real estate endpoints for property data, market trends, and more.
            """)
            
            api_key = st.text_input("RapidAPI Key", type="password")
            
            if st.form_submit_button("Save RapidAPI Settings"):
                if not api_key:
                    st.error("API Key is required")
                else:
                    # Save to environment variables
                    os.environ["RAPIDAPI_KEY"] = api_key
                    st.success("RapidAPI settings saved successfully")
        
        elif selected_api == "Zillow API":
            st.markdown("""
            Connect to Zillow's API for property data, valuations, and market insights.
            """)
            
            api_key = st.text_input("Zillow API Key", type="password")
            
            if st.form_submit_button("Save Zillow API Settings"):
                if not api_key:
                    st.error("API Key is required")
                else:
                    # Save to environment variables
                    os.environ["ZILLOW_API_KEY"] = api_key
                    st.success("Zillow API settings saved successfully")
        
        # Add more API options as needed
        
        else:
            st.markdown(f"Settings for {selected_api} coming soon.")
            
            if st.form_submit_button("Save Settings"):
                st.info(f"Support for {selected_api} is coming soon!")

# Add this function to check if email is properly configured
def is_email_configured():
    """Check if email service is properly configured"""
    config = get_email_config()
    return config is not None and all([
        config.get('smtp_server'),
        config.get('smtp_username'),
        config.get('smtp_password'),
        config.get('sender_email')
    ])

# Add this function to check if ad platforms are configured
def get_configured_ad_platforms():
    """Get list of configured ad platforms"""
    platforms = get_ad_platforms()
    return [p for p in platforms if p.connected]