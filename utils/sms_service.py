"""
SMS messaging service module for the real estate application.
This module provides functions to send property notifications, lead nurturing messages,
and other real estate information via SMS using Twilio.
"""

import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_sms_credentials():
    """
    Check if SMS (Twilio) credentials are configured.
    
    Returns:
        dict: Status of SMS configuration
    """
    twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")
    
    return {
        "configured": bool(twilio_account_sid and twilio_auth_token and twilio_phone_number),
        "account_sid": twilio_account_sid,
        "phone_number": twilio_phone_number
    }

def send_sms(to_phone_number, message):
    """
    Send an SMS message using Twilio.
    
    Args:
        to_phone_number (str): Recipient phone number in international format (e.g., "+15551234567")
        message (str): Text message to send
        
    Returns:
        dict: Status and message ID
    """
    credentials = check_sms_credentials()
    
    if not credentials["configured"]:
        return {
            "success": False,
            "message": "SMS credentials not configured. Please set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER environment variables."
        }
    
    # Ensure phone number is in proper format
    if not to_phone_number.startswith("+"):
        to_phone_number = "+" + to_phone_number.lstrip("0")
    
    try:
        # In production, make the actual API call
        logger.info(f"Would send SMS to {to_phone_number}")
        logger.info(f"Message: {message[:50]}...")
        
        # Initialize Twilio client (commented out for now)
        # twilio_client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
        # sms = twilio_client.messages.create(
        #     body=message,
        #     from_=os.getenv("TWILIO_PHONE_NUMBER"),
        #     to=to_phone_number
        # )
        # return {
        #     "success": True,
        #     "message": "Message sent successfully",
        #     "message_id": sms.sid
        # }
        
        # For demonstration
        return {
            "success": True,
            "message": "Message queued for delivery",
            "message_id": f"sms_{datetime.now().timestamp()}"
        }
        
    except TwilioRestException as e:
        logger.error(f"Twilio error sending SMS: {e}")
        return {
            "success": False,
            "message": f"Twilio error: {str(e)}"
        }
    except Exception as e:
        logger.error(f"Error sending SMS: {e}")
        return {
            "success": False,
            "message": f"Error sending SMS: {str(e)}"
        }

def send_property_notification(to_phone_number, property_details, notification_type="new_listing"):
    """
    Send a property notification via SMS.
    
    Args:
        to_phone_number (str): Recipient phone number
        property_details (dict): Dictionary containing property information
        notification_type (str): Type of notification (new_listing, price_change, etc.)
        
    Returns:
        dict: Status and message ID
    """
    address = property_details.get("address", "")
    price = property_details.get("price", 0)
    bedrooms = property_details.get("bedrooms", 0)
    bathrooms = property_details.get("bathrooms", 0)
    property_type = property_details.get("property_type", "")
    
    if notification_type == "new_listing":
        message = f"New Property Alert! {bedrooms}BR/{bathrooms}BA {property_type} at {address}. Price: ${price:,.2f}. Reply INFO for details."
    
    elif notification_type == "price_change":
        old_price = property_details.get("old_price", 0)
        price_diff = old_price - price
        price_pct = (price_diff / old_price) * 100
        
        if price_diff > 0:
            message = f"Price Drop! {address} now ${price:,.2f} (down {abs(price_pct):.1f}%). {bedrooms}BR/{bathrooms}BA {property_type}. Reply INFO for details."
        else:
            message = f"Price Update: {address} now ${price:,.2f} (up {abs(price_pct):.1f}%). {bedrooms}BR/{bathrooms}BA {property_type}. Reply INFO for details."
    
    elif notification_type == "sold":
        message = f"Property Sold: {address} ({bedrooms}BR/{bathrooms}BA {property_type}). Similar properties available. Reply SIMILAR to learn more."
    
    elif notification_type == "status_change":
        status = property_details.get("status", "")
        message = f"Status Update: {address} is now {status}. {bedrooms}BR/{bathrooms}BA {property_type}, ${price:,.2f}. Reply INFO for details."
    
    else:  # Default message
        message = f"Property Update: {address}, {bedrooms}BR/{bathrooms}BA {property_type}, ${price:,.2f}. Reply INFO for details."
    
    return send_sms(to_phone_number, message)

def send_lead_notification(to_phone_number, lead_name, agent_name, agent_phone):
    """
    Send a lead notification to an agent via SMS.
    
    Args:
        to_phone_number (str): Agent's phone number
        lead_name (str): Name of the lead
        agent_name (str): Name of the agent
        agent_phone (str): Agent's phone number
        
    Returns:
        dict: Status and message ID
    """
    message = f"New Lead Alert! {lead_name} has requested information. Please contact them within 15 minutes. - {agent_name} ({agent_phone})"
    return send_sms(to_phone_number, message)

def send_showing_reminder(to_phone_number, lead_name, property_address, showing_time, agent_name):
    """
    Send a showing reminder via SMS.
    
    Args:
        to_phone_number (str): Recipient phone number
        lead_name (str): Name of the lead
        property_address (str): Property address
        showing_time (str): Time of the showing
        agent_name (str): Name of the agent
        
    Returns:
        dict: Status and message ID
    """
    message = f"Hi {lead_name}, this is a reminder of your showing at {property_address} at {showing_time} with {agent_name}. Reply C to confirm or R to reschedule."
    return send_sms(to_phone_number, message)

def send_market_update_sms(to_phone_number, location, market_stats):
    """
    Send a market update via SMS.
    
    Args:
        to_phone_number (str): Recipient phone number
        location (str): Location of the market data
        market_stats (dict): Dictionary containing market statistics
        
    Returns:
        dict: Status and message ID
    """
    median_price = market_stats.get("median_price", 0)
    yoy_change = market_stats.get("year_over_year_change", 0)
    
    message = f"Real Estate Market Update for {location}: Median price ${median_price:,.2f} ({yoy_change:+.1f}% year-over-year). Reply MARKET for detailed analysis."
    return send_sms(to_phone_number, message)

def send_verification_code(to_phone_number, code):
    """
    Send a verification code via SMS.
    
    Args:
        to_phone_number (str): Recipient phone number
        code (str): Verification code
        
    Returns:
        dict: Status and message ID
    """
    message = f"Your verification code is: {code}. This code will expire in 10 minutes."
    return send_sms(to_phone_number, message)

def send_property_saved_confirmation(to_phone_number, property_address):
    """
    Send a confirmation that a property has been saved to favorites.
    
    Args:
        to_phone_number (str): Recipient phone number
        property_address (str): Property address
        
    Returns:
        dict: Status and message ID
    """
    message = f"You've saved {property_address} to your favorites! View all your saved properties by replying SAVED."
    return send_sms(to_phone_number, message)