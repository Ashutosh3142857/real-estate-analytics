"""
WhatsApp messaging service module for the real estate application.
This module provides functions to send property listing updates, open house invitations,
and other real estate information via WhatsApp Business API.
"""

import os
import json
import logging
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# WhatsApp API constants
WHATSAPP_API_URL = "https://graph.facebook.com/v18.0"

def check_whatsapp_credentials():
    """
    Check if WhatsApp Business API credentials are configured.
    
    Returns:
        dict: Status of WhatsApp configuration
    """
    whatsapp_phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
    whatsapp_business_account_id = os.getenv("WHATSAPP_BUSINESS_ACCOUNT_ID")
    whatsapp_access_token = os.getenv("WHATSAPP_ACCESS_TOKEN")
    
    return {
        "configured": bool(whatsapp_phone_number_id and whatsapp_business_account_id and whatsapp_access_token),
        "phone_number_id": whatsapp_phone_number_id,
        "business_account_id": whatsapp_business_account_id
    }

def send_whatsapp_message(to_phone_number, message, template_name=None, template_params=None):
    """
    Send a WhatsApp message using the WhatsApp Business API.
    
    Args:
        to_phone_number (str): Recipient phone number in international format (e.g., "15551234567")
        message (str): Text message to send (for text messages only)
        template_name (str, optional): Name of WhatsApp template to use
        template_params (dict, optional): Parameters for the template
        
    Returns:
        dict: Status and message ID
    """
    credentials = check_whatsapp_credentials()
    
    if not credentials["configured"]:
        return {
            "success": False,
            "message": "WhatsApp credentials not configured. Please set WHATSAPP_PHONE_NUMBER_ID, WHATSAPP_BUSINESS_ACCOUNT_ID, and WHATSAPP_ACCESS_TOKEN environment variables."
        }
    
    # WhatsApp API requires the phone number to include country code without "+" sign
    to_phone_number = to_phone_number.replace("+", "").strip()
    
    # API endpoint for sending messages
    phone_number_id = credentials["phone_number_id"]
    access_token = os.getenv("WHATSAPP_ACCESS_TOKEN")
    url = f"{WHATSAPP_API_URL}/{phone_number_id}/messages"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    try:
        # Prepare the message payload
        if template_name:
            # Template message
            components = []
            if template_params:
                parameters = []
                for param in template_params:
                    parameters.append({
                        "type": "text",
                        "text": str(param)
                    })
                components.append({
                    "type": "body",
                    "parameters": parameters
                })
            
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": to_phone_number,
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {
                        "code": "en_US"
                    },
                    "components": components
                }
            }
        else:
            # Text message
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": to_phone_number,
                "type": "text",
                "text": {
                    "preview_url": True,
                    "body": message
                }
            }
        
        # In production, make the actual API call
        logger.info(f"Would send WhatsApp message to {to_phone_number}")
        logger.info(f"Payload: {json.dumps(payload, indent=2)}")
        
        # Simulated response for now
        # In production, uncomment this code:
        # response = requests.post(url, headers=headers, json=payload)
        # response_data = response.json()
        # success = response.status_code == 200
        # return {
        #     "success": success,
        #     "message": "Message sent successfully" if success else "Failed to send message",
        #     "message_id": response_data.get("messages", [{}])[0].get("id") if success else None,
        #     "error": response_data.get("error") if not success else None
        # }
        
        # For demonstration
        return {
            "success": True,
            "message": "Message queued for delivery",
            "message_id": f"whatsapp_msg_{datetime.now().timestamp()}"
        }
        
    except Exception as e:
        logger.error(f"Error sending WhatsApp message: {e}")
        return {
            "success": False,
            "message": f"Error sending WhatsApp message: {str(e)}"
        }

def send_property_listing(to_phone_number, property_details):
    """
    Send a property listing via WhatsApp.
    
    Args:
        to_phone_number (str): Recipient phone number
        property_details (dict): Dictionary containing property information
        
    Returns:
        dict: Status and message ID
    """
    # Format a nice message with property details
    address = property_details.get("address", "")
    price = property_details.get("price", 0)
    bedrooms = property_details.get("bedrooms", 0)
    bathrooms = property_details.get("bathrooms", 0)
    sqft = property_details.get("sqft", 0)
    property_type = property_details.get("property_type", "")
    url = property_details.get("listing_url", "")
    
    message = f"*New Property Listing*\n\n"
    message += f"📍 {address}\n"
    message += f"💰 ${price:,.2f}\n"
    message += f"🛏️ {bedrooms} bedrooms | 🚿 {bathrooms} bathrooms\n"
    message += f"📏 {sqft} sq.ft.\n"
    message += f"🏠 {property_type}\n\n"
    
    if url:
        message += f"View this property: {url}"
    
    return send_whatsapp_message(to_phone_number, message)

def send_open_house_invitation(to_phone_number, property_details, date_time, virtual=False, virtual_link=None):
    """
    Send an open house invitation via WhatsApp.
    
    Args:
        to_phone_number (str): Recipient phone number
        property_details (dict): Dictionary containing property information
        date_time (str): Date and time of the open house
        virtual (bool): Whether this is a virtual open house
        virtual_link (str, optional): Link for virtual open house
        
    Returns:
        dict: Status and message ID
    """
    address = property_details.get("address", "")
    price = property_details.get("price", 0)
    bedrooms = property_details.get("bedrooms", 0)
    bathrooms = property_details.get("bathrooms", 0)
    property_type = property_details.get("property_type", "")
    
    event_type = "Virtual Open House" if virtual else "Open House"
    
    message = f"*{event_type} Invitation*\n\n"
    message += f"You're invited to an {event_type.lower()} for:\n\n"
    message += f"📍 {address}\n"
    message += f"💰 ${price:,.2f}\n"
    message += f"🛏️ {bedrooms} bedrooms | 🚿 {bathrooms} bathrooms\n"
    message += f"🏠 {property_type}\n\n"
    message += f"📅 *When:* {date_time}\n\n"
    
    if virtual and virtual_link:
        message += f"🖥️ *Join here:* {virtual_link}\n\n"
    
    message += "Reply 'YES' if you'll be attending!"
    
    return send_whatsapp_message(to_phone_number, message)

def send_price_drop_alert(to_phone_number, property_details, old_price, new_price):
    """
    Send a price drop alert via WhatsApp.
    
    Args:
        to_phone_number (str): Recipient phone number
        property_details (dict): Dictionary containing property information
        old_price (float): Previous property price
        new_price (float): New property price
        
    Returns:
        dict: Status and message ID
    """
    address = property_details.get("address", "")
    bedrooms = property_details.get("bedrooms", 0)
    bathrooms = property_details.get("bathrooms", 0)
    sqft = property_details.get("sqft", 0)
    url = property_details.get("listing_url", "")
    
    price_difference = old_price - new_price
    price_percentage = (price_difference / old_price) * 100
    
    message = f"*Price Drop Alert! 🔻*\n\n"
    message += f"Good news! This property has just been reduced in price:\n\n"
    message += f"📍 {address}\n"
    message += f"💰 *New Price:* ${new_price:,.2f}\n"
    message += f"💸 *Price Drop:* ${price_difference:,.2f} ({price_percentage:.1f}%)\n"
    message += f"🛏️ {bedrooms} bedrooms | 🚿 {bathrooms} bathrooms\n"
    message += f"📏 {sqft} sq.ft.\n\n"
    
    if url:
        message += f"View this property: {url}\n\n"
    
    message += "Interested? Reply 'INFO' to learn more!"
    
    return send_whatsapp_message(to_phone_number, message)

def send_market_update(to_phone_number, location, market_data):
    """
    Send a real estate market update via WhatsApp.
    
    Args:
        to_phone_number (str): Recipient phone number
        location (str): Location of the market data
        market_data (dict): Dictionary containing market statistics
        
    Returns:
        dict: Status and message ID
    """
    median_price = market_data.get("median_price", 0)
    avg_price = market_data.get("avg_price", 0)
    inventory = market_data.get("inventory", 0)
    days_on_market = market_data.get("days_on_market", 0)
    yoy_change = market_data.get("year_over_year_change", 0)
    mom_change = market_data.get("month_over_month_change", 0)
    
    message = f"*Real Estate Market Update for {location}*\n\n"
    message += f"📊 *Market Snapshot:*\n"
    message += f"• Median Price: ${median_price:,.2f}\n"
    message += f"• Average Price: ${avg_price:,.2f}\n"
    message += f"• Available Properties: {inventory}\n"
    message += f"• Average Days on Market: {days_on_market}\n"
    message += f"• Year-over-Year Change: {yoy_change:.1f}%\n"
    message += f"• Month-over-Month Change: {mom_change:.1f}%\n\n"
    
    if yoy_change > 0:
        message += f"The market in {location} is showing strong growth with property values up {yoy_change:.1f}% from last year.\n\n"
    elif yoy_change < 0:
        message += f"The market in {location} is showing a price correction with values down {abs(yoy_change):.1f}% from last year.\n\n"
    else:
        message += f"The market in {location} remains stable with little change in property values from last year.\n\n"
    
    message += "Want a personalized market analysis? Reply 'ANALYSIS'!"
    
    return send_whatsapp_message(to_phone_number, message)

def send_lead_nurture_message(to_phone_number, lead_name, message_type="follow_up"):
    """
    Send a lead nurturing message via WhatsApp.
    
    Args:
        to_phone_number (str): Recipient phone number
        lead_name (str): Name of the lead
        message_type (str): Type of nurture message to send
        
    Returns:
        dict: Status and message ID
    """
    if message_type == "follow_up":
        message = f"Hi {lead_name},\n\n"
        message += "Thank you for your interest in our properties! I'm following up to see if you had any questions or if you'd like to schedule a viewing?\n\n"
        message += "I'm available to help you find your perfect property. Just let me know what you're looking for!"
    
    elif message_type == "check_in":
        message = f"Hello {lead_name},\n\n"
        message += "Just checking in to see how your property search is going. Have your requirements changed or would you like to see new listings that match your criteria?\n\n"
        message += "I'm here to help whenever you're ready to take the next step."
    
    elif message_type == "market_intelligence":
        message = f"Hi {lead_name},\n\n"
        message += "I thought you might be interested in some new market trends we're seeing. Property values in your area of interest have been changing, which could impact your buying decision.\n\n"
        message += "Would you like to discuss how these trends might affect your property search?"
    
    else:  # Default generic message
        message = f"Hello {lead_name},\n\n"
        message += "I hope this message finds you well. I'm reaching out regarding your property search. Please let me know if there's anything specific you're looking for, and I'll be happy to assist you.\n\n"
        message += "Looking forward to hearing from you!"
    
    return send_whatsapp_message(to_phone_number, message)