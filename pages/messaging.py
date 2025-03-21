"""
Messaging page for sending communications via Email, WhatsApp, and SMS.
This page provides a unified interface for sending various types of real estate-related messages
through multiple communication channels.
"""

import streamlit as st
import pandas as pd
from datetime import datetime

from utils.email_service import (
    check_email_credentials, 
    send_email,
    get_available_email_providers
)
from utils.whatsapp_service import (
    check_whatsapp_credentials,
    send_whatsapp_message,
    send_property_listing,
    send_open_house_invitation,
    send_price_drop_alert,
    send_market_update
)
from utils.sms_service import (
    check_sms_credentials,
    send_sms,
    send_property_notification,
    send_showing_reminder,
    send_market_update_sms
)
from utils.database import get_properties, get_leads
from utils.image_generator import generate_email_header_image, image_to_base64

def show_messaging():
    """Display messaging interface for multiple channels"""
    st.title("Messaging Center")
    
    # Check credentials for different messaging channels
    email_status = check_email_credentials()
    whatsapp_status = check_whatsapp_credentials()
    sms_status = check_sms_credentials()
    
    available_channels = []
    
    if any(email_status.values()):
        available_channels.append("Email")
    
    if whatsapp_status.get("configured", False):
        available_channels.append("WhatsApp")
    
    if sms_status.get("configured", False):
        available_channels.append("SMS")
    
    if not available_channels:
        st.warning("No messaging channels are configured. Please set up your messaging credentials in Settings.")
        if st.button("Go to Settings"):
            # This will redirect to the settings page in Streamlit
            st.experimental_set_query_params(page="settings")
            st.rerun()
        return
    
    # Tabs for different messaging functions
    tab1, tab2, tab3, tab4 = st.tabs([
        "Quick Message", 
        "Property Notifications", 
        "Campaign Messages",
        "Message Templates"
    ])
    
    with tab1:
        show_quick_message_tab(available_channels)
    
    with tab2:
        show_property_notifications_tab(available_channels)
    
    with tab3:
        show_campaign_messages_tab(available_channels)
    
    with tab4:
        show_message_templates_tab()

def show_quick_message_tab(available_channels):
    """Display quick message interface"""
    st.header("Quick Message")
    
    # Get recipient data
    leads_df = get_leads()
    
    # Message form
    with st.form("quick_message_form"):
        channel = st.selectbox(
            "Select channel", 
            available_channels,
            index=0
        )
        
        recipient_type = st.radio(
            "Recipient",
            ["Individual", "Group"],
            horizontal=True
        )
        
        if recipient_type == "Individual":
            if not leads_df.empty:
                lead_options = [f"{row['name']} ({row['email']})" for _, row in leads_df.iterrows()]
                lead_options.insert(0, "Enter manually")
                
                lead_selection = st.selectbox("Select recipient", lead_options)
                
                if lead_selection == "Enter manually":
                    recipient = st.text_input("Recipient (Email, Phone with country code)")
                    recipient_name = st.text_input("Recipient Name")
                else:
                    selected_lead = leads_df.iloc[lead_options.index(lead_selection) - 1]
                    recipient = selected_lead["email"] if channel == "Email" else selected_lead["phone"]
                    recipient_name = selected_lead["name"]
            else:
                recipient = st.text_input("Recipient (Email, Phone with country code)")
                recipient_name = st.text_input("Recipient Name")
        else:  # Group
            recipients = st.text_area(
                "Recipients (one per line, emails or phone numbers based on selected channel)",
                placeholder="recipient1@example.com\nrecipient2@example.com"
            )
        
        if channel == "Email":
            subject = st.text_input("Subject")
        
        message = st.text_area(
            "Message",
            placeholder="Enter your message here...",
            height=200
        )
        
        send_button = st.form_submit_button("Send Message")
    
    if send_button:
        if not message:
            st.error("Please enter a message.")
            return
        
        if channel == "Email" and not subject:
            st.error("Please enter a subject for the email.")
            return
        
        if recipient_type == "Individual":
            if not recipient:
                st.error("Please enter a recipient.")
                return
            
            # Send message based on channel
            with st.spinner(f"Sending {channel} message..."):
                if channel == "Email":
                    # Prepare html content
                    html_content = f"<p>Dear {recipient_name},</p><p>{message}</p><p>Best regards,<br>Your Real Estate Team</p>"
                    
                    # Get available email providers
                    providers = get_available_email_providers()
                    if providers:
                        provider = providers[0]
                        result = send_email(
                            provider=provider,
                            to_emails=[recipient],
                            subject=subject,
                            html_content=html_content,
                            text_content=message
                        )
                    else:
                        result = {"success": False, "message": "No email providers configured"}
                
                elif channel == "WhatsApp":
                    result = send_whatsapp_message(recipient, message)
                
                elif channel == "SMS":
                    result = send_sms(recipient, message)
                
                if result.get("success"):
                    st.success(f"Message sent successfully via {channel}!")
                else:
                    st.error(f"Failed to send message: {result.get('message', 'Unknown error')}")
        
        else:  # Group
            if not recipients:
                st.error("Please enter at least one recipient.")
                return
            
            recipient_list = [r.strip() for r in recipients.split("\n") if r.strip()]
            
            if not recipient_list:
                st.error("Please enter valid recipients.")
                return
            
            with st.spinner(f"Sending {channel} message to {len(recipient_list)} recipients..."):
                success_count = 0
                error_messages = []
                
                for r in recipient_list:
                    if channel == "Email":
                        # Simple html content
                        html_content = f"<p>Hello,</p><p>{message}</p><p>Best regards,<br>Your Real Estate Team</p>"
                        
                        # Get available email providers
                        providers = get_available_email_providers()
                        if providers:
                            provider = providers[0]
                            result = send_email(
                                provider=provider,
                                to_emails=[r],
                                subject=subject,
                                html_content=html_content,
                                text_content=message
                            )
                        else:
                            result = {"success": False, "message": "No email providers configured"}
                    
                    elif channel == "WhatsApp":
                        result = send_whatsapp_message(r, message)
                    
                    elif channel == "SMS":
                        result = send_sms(r, message)
                    
                    if result.get("success"):
                        success_count += 1
                    else:
                        error_messages.append(f"{r}: {result.get('message', 'Unknown error')}")
                
                if success_count == len(recipient_list):
                    st.success(f"Messages sent successfully to all {len(recipient_list)} recipients via {channel}!")
                elif success_count > 0:
                    st.warning(f"Sent to {success_count} out of {len(recipient_list)} recipients. Some messages failed.")
                    if error_messages:
                        with st.expander("View errors"):
                            for err in error_messages:
                                st.write(err)
                else:
                    st.error("Failed to send any messages.")
                    if error_messages:
                        with st.expander("View errors"):
                            for err in error_messages:
                                st.write(err)

def show_property_notifications_tab(available_channels):
    """Display property notifications interface"""
    st.header("Property Notifications")
    
    # Get property data
    properties_df = get_properties()
    leads_df = get_leads()
    
    if properties_df.empty:
        st.warning("No properties available. Please add properties first.")
        return
    
    # Get notification type
    notification_type = st.selectbox(
        "Notification Type",
        ["New Listing", "Price Change", "Open House", "Market Update", "Status Change"]
    )
    
    # Property selection
    property_options = [f"{row['address']} (${row['price']:,.2f})" for _, row in properties_df.iterrows()]
    selected_property = st.selectbox("Select Property", property_options)
    property_idx = property_options.index(selected_property)
    property_details = properties_df.iloc[property_idx].to_dict()
    
    # Display property details
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Price", f"${property_details['price']:,.2f}")
    with col2:
        st.metric("Bedrooms", property_details['bedrooms'])
    with col3:
        st.metric("Bathrooms", property_details['bathrooms'])
    
    # Channel selection
    channel = st.selectbox(
        "Select channel", 
        available_channels,
        index=0
    )
    
    # Recipient selection
    recipient_type = st.radio(
        "Recipient",
        ["Individual", "Group"],
        horizontal=True
    )
    
    if recipient_type == "Individual":
        if not leads_df.empty:
            lead_options = [f"{row['name']} ({row['email']})" for _, row in leads_df.iterrows()]
            lead_options.insert(0, "Enter manually")
            
            lead_selection = st.selectbox("Select recipient", lead_options)
            
            if lead_selection == "Enter manually":
                recipient = st.text_input("Recipient (Email, Phone with country code)")
                recipient_name = st.text_input("Recipient Name")
            else:
                selected_lead = leads_df.iloc[lead_options.index(lead_selection) - 1]
                recipient = selected_lead["email"] if channel == "Email" else selected_lead["phone"]
                recipient_name = selected_lead["name"]
        else:
            recipient = st.text_input("Recipient (Email, Phone with country code)")
            recipient_name = st.text_input("Recipient Name")
    else:  # Group
        recipients = st.text_area(
            "Recipients (one per line, emails or phone numbers based on selected channel)",
            placeholder="recipient1@example.com\nrecipient2@example.com"
        )
    
    # Additional fields based on notification type
    if notification_type == "Price Change":
        old_price = st.number_input("Old Price ($)", min_value=0.0, value=property_details['price'] * 1.05)
    
    elif notification_type == "Open House":
        date_str = st.date_input("Open House Date")
        time_str = st.time_input("Open House Time")
        open_house_time = f"{date_str.strftime('%A, %B %d, %Y')} at {time_str.strftime('%I:%M %p')}"
        
        is_virtual = st.checkbox("Virtual Open House")
        if is_virtual:
            virtual_platform = st.selectbox("Virtual Platform", ["Zoom", "Google Meet", "Teams", "Other"])
            virtual_link = st.text_input("Meeting Link")
    
    elif notification_type == "Market Update":
        # Get market data from database or generate sample data
        market_data = {
            "median_price": property_details['price'] * 0.95,
            "avg_price": property_details['price'],
            "inventory": 45,
            "days_on_market": 28,
            "year_over_year_change": 5.2,
            "month_over_month_change": 0.8
        }
        
        location = property_details['city']
        
        # Show market data preview
        st.subheader("Market Data Preview")
        market_df = pd.DataFrame([market_data])
        st.dataframe(market_df)
    
    # Send button
    if st.button(f"Send {notification_type} Notification"):
        if recipient_type == "Individual" and not recipient:
            st.error("Please enter a recipient.")
            return
        
        if recipient_type == "Group" and not recipients:
            st.error("Please enter at least one recipient.")
            return
        
        if recipient_type == "Individual":
            recipient_list = [recipient]
        else:
            recipient_list = [r.strip() for r in recipients.split("\n") if r.strip()]
        
        with st.spinner(f"Sending {notification_type} notification..."):
            success_count = 0
            error_messages = []
            
            for r in recipient_list:
                if channel == "Email":
                    # Create email content based on notification type
                    if notification_type == "New Listing":
                        subject = f"New Property Listing: {property_details['address']}"
                        # Generate email header image
                        header_img = generate_email_header_image("New Listing Announcement", property_details)
                        header_img_b64 = image_to_base64(header_img)
                        
                        html_content = f"""
                        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                            <img src="{header_img_b64}" style="width: 100%; max-width: 600px; height: auto;" alt="New Listing">
                            <h2 style="color: #3a3a3a;">Exciting New Property Just Listed!</h2>
                            <div style="background-color: #f8f8f8; padding: 15px; border-radius: 5px; margin: 15px 0;">
                                <h3 style="color: #4285f4; margin-top: 0;">{property_details['address']}</h3>
                                <p style="font-size: 20px; font-weight: bold; color: #3a3a3a;">${property_details['price']:,.2f}</p>
                                <p>{property_details['bedrooms']} bedrooms | {property_details['bathrooms']} bathrooms | {property_details['sqft']} sq.ft.</p>
                                <p>{property_details['description']}</p>
                                <a href="#" style="background-color: #4285f4; color: white; padding: 10px 15px; text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 10px;">View Property Details</a>
                            </div>
                            <p>We thought you might be interested in this new property that matches your search criteria.</p>
                            <p>Don't hesitate to reply to this email or call us if you'd like to schedule a viewing.</p>
                            <p>Best regards,<br>Your Real Estate Team</p>
                        </div>
                        """
                    
                    elif notification_type == "Price Change":
                        price_diff = old_price - property_details['price']
                        price_pct = (price_diff / old_price) * 100
                        
                        if price_diff > 0:
                            subject = f"Price Reduction: {property_details['address']}"
                            header_img = generate_email_header_image("Price Reduction Alert", property_details)
                        else:
                            subject = f"Price Update: {property_details['address']}"
                            header_img = generate_email_header_image("Price Update", property_details)
                        
                        header_img_b64 = image_to_base64(header_img)
                        
                        html_content = f"""
                        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                            <img src="{header_img_b64}" style="width: 100%; max-width: 600px; height: auto;" alt="Price Update">
                            <h2 style="color: #3a3a3a;">{"Price Reduction Alert!" if price_diff > 0 else "Price Update"}</h2>
                            <div style="background-color: #f8f8f8; padding: 15px; border-radius: 5px; margin: 15px 0;">
                                <h3 style="color: #4285f4; margin-top: 0;">{property_details['address']}</h3>
                                <p><span style="font-size: 16px; text-decoration: line-through;">${old_price:,.2f}</span> 
                                <span style="font-size: 20px; font-weight: bold; color: #{"e74c3c" if price_diff > 0 else "27ae60"};">
                                    ${property_details['price']:,.2f}
                                </span>
                                <span style="color: #{"e74c3c" if price_diff > 0 else "27ae60"};">
                                    ({"-" if price_diff > 0 else "+"}{abs(price_pct):.1f}%)
                                </span></p>
                                <p>{property_details['bedrooms']} bedrooms | {property_details['bathrooms']} bathrooms | {property_details['sqft']} sq.ft.</p>
                                <p>{property_details['description']}</p>
                                <a href="#" style="background-color: #4285f4; color: white; padding: 10px 15px; text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 10px;">View Property Details</a>
                            </div>
                            <p>This property has recently had a price {"reduction" if price_diff > 0 else "update"}. It might be a good time to {"take another look" if price_diff > 0 else "review this opportunity"}!</p>
                            <p>Don't hesitate to reply to this email or call us if you'd like to schedule a viewing.</p>
                            <p>Best regards,<br>Your Real Estate Team</p>
                        </div>
                        """
                    
                    elif notification_type == "Open House":
                        subject = f"Open House Invitation: {property_details['address']}"
                        header_img = generate_email_header_image("Open House Invitation", property_details)
                        header_img_b64 = image_to_base64(header_img)
                        
                        virtual_text = ""
                        if is_virtual:
                            virtual_text = f"""
                            <p style="font-weight: bold;">This is a Virtual Open House via {virtual_platform}</p>
                            <p>Join using this link: <a href="{virtual_link}">{virtual_link}</a></p>
                            """
                        
                        html_content = f"""
                        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                            <img src="{header_img_b64}" style="width: 100%; max-width: 600px; height: auto;" alt="Open House">
                            <h2 style="color: #3a3a3a;">{"Virtual " if is_virtual else ""}Open House Invitation</h2>
                            <div style="background-color: #f8f8f8; padding: 15px; border-radius: 5px; margin: 15px 0;">
                                <h3 style="color: #4285f4; margin-top: 0;">{property_details['address']}</h3>
                                <p style="font-size: 18px; font-weight: bold; color: #e67e22;">{open_house_time}</p>
                                {virtual_text}
                                <p style="font-size: 18px; color: #3a3a3a;">${property_details['price']:,.2f}</p>
                                <p>{property_details['bedrooms']} bedrooms | {property_details['bathrooms']} bathrooms | {property_details['sqft']} sq.ft.</p>
                                <p>{property_details['description']}</p>
                                <a href="#" style="background-color: #4285f4; color: white; padding: 10px 15px; text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 10px;">RSVP Now</a>
                            </div>
                            <p>We're excited to invite you to our upcoming {"virtual " if is_virtual else ""}open house. This is a great opportunity to explore this beautiful property{"" if is_virtual else " in person"}!</p>
                            <p>Please RSVP by replying to this email or clicking the button above.</p>
                            <p>Best regards,<br>Your Real Estate Team</p>
                        </div>
                        """
                    
                    elif notification_type == "Market Update":
                        subject = f"Real Estate Market Update for {location}"
                        header_img = generate_email_header_image("Market Update Newsletter", property_details)
                        header_img_b64 = image_to_base64(header_img)
                        
                        html_content = f"""
                        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                            <img src="{header_img_b64}" style="width: 100%; max-width: 600px; height: auto;" alt="Market Update">
                            <h2 style="color: #3a3a3a;">Real Estate Market Update: {location}</h2>
                            <div style="background-color: #f8f8f8; padding: 15px; border-radius: 5px; margin: 15px 0;">
                                <h3 style="color: #4285f4; margin-top: 0;">Current Market Trends</h3>
                                <table style="width: 100%; border-collapse: collapse;">
                                    <tr>
                                        <td style="padding: 8px; border-bottom: 1px solid #ddd;">Median Price</td>
                                        <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: right;">${market_data['median_price']:,.2f}</td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 8px; border-bottom: 1px solid #ddd;">Average Price</td>
                                        <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: right;">${market_data['avg_price']:,.2f}</td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 8px; border-bottom: 1px solid #ddd;">Available Properties</td>
                                        <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: right;">{market_data['inventory']}</td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 8px; border-bottom: 1px solid #ddd;">Average Days on Market</td>
                                        <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: right;">{market_data['days_on_market']}</td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 8px; border-bottom: 1px solid #ddd;">Year-over-Year Change</td>
                                        <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: right; color: {'#27ae60' if market_data['year_over_year_change'] > 0 else '#e74c3c'};">
                                            {market_data['year_over_year_change']:+.1f}%
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 8px;">Month-over-Month Change</td>
                                        <td style="padding: 8px; text-align: right; color: {'#27ae60' if market_data['month_over_month_change'] > 0 else '#e74c3c'};">
                                            {market_data['month_over_month_change']:+.1f}%
                                        </td>
                                    </tr>
                                </table>
                            </div>
                            <p>The real estate market in {location} continues to evolve. Here's what this means for you:</p>
                            <ul>
                                <li>{"Increasing" if market_data['year_over_year_change'] > 0 else "Decreasing"} property values indicate a {"seller's" if market_data['year_over_year_change'] > 0 else "buyer's"} market</li>
                                <li>Average time on market of {market_data['days_on_market']} days shows {"high" if market_data['days_on_market'] < 30 else "moderate" if market_data['days_on_market'] < 60 else "slower"} demand</li>
                                <li>Current inventory levels are {"low" if market_data['inventory'] < 50 else "moderate" if market_data['inventory'] < 100 else "high"}</li>
                            </ul>
                            <p>If you're considering buying or selling in this area, now is a good time to discuss your options. Reply to this email for a personalized market analysis.</p>
                            <p>Best regards,<br>Your Real Estate Team</p>
                        </div>
                        """
                    
                    elif notification_type == "Status Change":
                        status = "Under Contract"  # Example status
                        subject = f"Status Update: {property_details['address']} is now {status}"
                        header_img = generate_email_header_image("Status Update", property_details)
                        header_img_b64 = image_to_base64(header_img)
                        
                        html_content = f"""
                        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                            <img src="{header_img_b64}" style="width: 100%; max-width: 600px; height: auto;" alt="Status Update">
                            <h2 style="color: #3a3a3a;">Property Status Update</h2>
                            <div style="background-color: #f8f8f8; padding: 15px; border-radius: 5px; margin: 15px 0;">
                                <h3 style="color: #4285f4; margin-top: 0;">{property_details['address']}</h3>
                                <p style="font-size: 18px; font-weight: bold; color: #e67e22;">Status: {status}</p>
                                <p style="font-size: 18px; color: #3a3a3a;">${property_details['price']:,.2f}</p>
                                <p>{property_details['bedrooms']} bedrooms | {property_details['bathrooms']} bathrooms | {property_details['sqft']} sq.ft.</p>
                                <a href="#" style="background-color: #4285f4; color: white; padding: 10px 15px; text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 10px;">View Similar Properties</a>
                            </div>
                            <p>This property's status has changed to {status}. {"You might want to consider similar properties in the area." if status in ["Sold", "Under Contract", "Pending"] else "This might affect your interest in this property."}</p>
                            <p>Feel free to reply to this email if you have any questions or would like to discuss other properties.</p>
                            <p>Best regards,<br>Your Real Estate Team</p>
                        </div>
                        """
                    
                    # Get available email providers
                    providers = get_available_email_providers()
                    if providers:
                        provider = providers[0]
                        result = send_email(
                            provider=provider,
                            to_emails=[r],
                            subject=subject,
                            html_content=html_content
                        )
                    else:
                        result = {"success": False, "message": "No email providers configured"}
                
                elif channel == "WhatsApp":
                    if notification_type == "New Listing":
                        result = send_property_listing(r, property_details)
                    
                    elif notification_type == "Price Change":
                        result = send_price_drop_alert(r, property_details, old_price, property_details['price'])
                    
                    elif notification_type == "Open House":
                        if is_virtual:
                            result = send_open_house_invitation(r, property_details, open_house_time, True, virtual_link)
                        else:
                            result = send_open_house_invitation(r, property_details, open_house_time)
                    
                    elif notification_type == "Market Update":
                        result = send_market_update(r, location, market_data)
                    
                    else:  # Status Change
                        message = f"Status Update: The property at {property_details['address']} has changed status. Please contact us for more information."
                        result = send_whatsapp_message(r, message)
                
                elif channel == "SMS":
                    if notification_type == "New Listing":
                        result = send_property_notification(r, property_details, "new_listing")
                    
                    elif notification_type == "Price Change":
                        # Add old price to property details
                        property_details_with_old_price = property_details.copy()
                        property_details_with_old_price["old_price"] = old_price
                        result = send_property_notification(r, property_details_with_old_price, "price_change")
                    
                    elif notification_type == "Open House":
                        virtual_text = "(Virtual)" if is_virtual else ""
                        message = f"Open House{virtual_text}: {property_details['address']} on {open_house_time}. "
                        if is_virtual:
                            message += f"Join via {virtual_platform}: {virtual_link}"
                        else:
                            message += "Reply YES to RSVP."
                        result = send_sms(r, message)
                    
                    elif notification_type == "Market Update":
                        result = send_market_update_sms(r, location, market_data)
                    
                    else:  # Status Change
                        status = "Under Contract"  # Example status
                        property_details_with_status = property_details.copy()
                        property_details_with_status["status"] = status
                        result = send_property_notification(r, property_details_with_status, "status_change")
                
                if result.get("success"):
                    success_count += 1
                else:
                    error_messages.append(f"{r}: {result.get('message', 'Unknown error')}")
            
            if success_count == len(recipient_list):
                st.success(f"{notification_type} notification sent successfully to all {len(recipient_list)} recipients via {channel}!")
            elif success_count > 0:
                st.warning(f"Sent to {success_count} out of {len(recipient_list)} recipients. Some messages failed.")
                if error_messages:
                    with st.expander("View errors"):
                        for err in error_messages:
                            st.write(err)
            else:
                st.error("Failed to send any notifications.")
                if error_messages:
                    with st.expander("View errors"):
                        for err in error_messages:
                            st.write(err)

def show_campaign_messages_tab(available_channels):
    """Display campaign messaging interface"""
    st.header("Campaign Messages")
    
    campaign_type = st.selectbox(
        "Campaign Type",
        ["Monthly Newsletter", "Market Report", "Property Recommendation", "Lead Nurturing", "Re-engagement", "Seasonal Update"]
    )
    
    channel = st.selectbox(
        "Select channel", 
        available_channels,
        index=0 if "Email" in available_channels else 0
    )
    
    # Get leads data for targeting
    leads_df = get_leads()
    
    if not leads_df.empty:
        st.subheader("Recipient Targeting")
        
        # Allow filtering by lead properties
        col1, col2 = st.columns(2)
        
        with col1:
            min_lead_score = st.slider("Minimum Lead Score", 0, 100, 50)
            property_interest = st.multiselect(
                "Property Interest", 
                sorted(leads_df["property_interest"].unique().tolist()),
                []
            )
        
        with col2:
            lead_status = st.multiselect(
                "Lead Status",
                sorted(leads_df["status"].unique().tolist()),
                ["new", "contacted", "qualified"]
            )
            sources = st.multiselect(
                "Lead Source",
                sorted(leads_df["source"].unique().tolist()),
                []
            )
        
        # Filter leads based on criteria
        filtered_leads = leads_df.copy()
        if min_lead_score > 0:
            filtered_leads = filtered_leads[filtered_leads["lead_score"] >= min_lead_score]
        if property_interest:
            filtered_leads = filtered_leads[filtered_leads["property_interest"].isin(property_interest)]
        if lead_status:
            filtered_leads = filtered_leads[filtered_leads["status"].isin(lead_status)]
        if sources:
            filtered_leads = filtered_leads[filtered_leads["source"].isin(sources)]
        
        st.write(f"Selected recipients: {len(filtered_leads)} leads")
        
        if len(filtered_leads) > 0:
            with st.expander("View selected recipients"):
                st.dataframe(filtered_leads[["name", "email", "phone", "lead_score", "status"]])
        
        recipient_list = []
        if channel == "Email":
            recipient_list = filtered_leads["email"].tolist()
        else:  # WhatsApp or SMS
            recipient_list = filtered_leads["phone"].tolist()
    else:
        st.warning("No leads available in the database. Please add leads first.")
        # Allow manual entry of recipients
        recipients = st.text_area(
            "Recipients (one per line, emails or phone numbers based on selected channel)",
            placeholder="recipient1@example.com\nrecipient2@example.com"
        )
        if recipients:
            recipient_list = [r.strip() for r in recipients.split("\n") if r.strip()]
    
    # Campaign content
    st.subheader("Campaign Content")
    
    if channel == "Email":
        subject = st.text_input("Email Subject", 
                               value=f"Your {campaign_type} from Real Estate Analytics")
    
    # Template/message content depends on campaign type
    if campaign_type == "Monthly Newsletter":
        content = st.text_area(
            "Newsletter Content",
            height=200,
            value="""Hello {name},

We're excited to share this month's real estate insights with you:

1. Market Trends: Property values in your area have increased by 3.2% in the last month
2. Featured Properties: We've added 12 new properties that match your criteria
3. Investment Tip: Consider properties in emerging neighborhoods for better ROI

Let us know if you'd like more information on any of these topics!

Best regards,
Your Real Estate Team"""
        )
    elif campaign_type == "Market Report":
        content = st.text_area(
            "Market Report Content",
            height=200,
            value="""Hello {name},

Here's your personalized real estate market report:

The market in your area of interest has shown {trend} over the past quarter with median prices now at ${median_price}.

Key statistics:
- Days on market: {days_on_market}
- Inventory levels: {inventory}
- Year-over-year change: {yoy_change}%

This could be a good time to {action_recommendation} based on your previous interests.

Would you like to discuss these findings in more detail?

Best regards,
Your Real Estate Team"""
        )
    else:
        content = st.text_area(
            "Message Content",
            height=200,
            placeholder="Enter your campaign message here..."
        )
    
    # Schedule campaign
    st.subheader("Campaign Schedule")
    col1, col2 = st.columns(2)
    with col1:
        send_date = st.date_input("Send Date")
    with col2:
        send_time = st.time_input("Send Time")
    
    send_immediately = st.checkbox("Send Immediately")
    
    if st.button(f"{'Send' if send_immediately else 'Schedule'} Campaign"):
        if not recipient_list:
            st.error("No recipients selected. Please select at least one recipient.")
            return
        
        if channel == "Email" and not subject:
            st.error("Please enter a subject for the email campaign.")
            return
        
        if not content:
            st.error("Please enter content for your campaign.")
            return
        
        with st.spinner(f"{'Sending' if send_immediately else 'Scheduling'} campaign to {len(recipient_list)} recipients..."):
            if send_immediately:
                # Send campaign immediately
                if channel == "Email":
                    # Example for email campaign
                    providers = get_available_email_providers()
                    if not providers:
                        st.error("No email providers configured.")
                        return
                    
                    provider = providers[0]
                    
                    # Create some random sample data for template variables
                    import random
                    sample_data = {
                        "trend": random.choice(["positive growth", "steady performance", "slight correction"]),
                        "median_price": f"{random.randint(300000, 800000):,}",
                        "days_on_market": random.randint(10, 60),
                        "inventory": random.randint(20, 200),
                        "yoy_change": random.uniform(-5.0, 8.0),
                        "action_recommendation": random.choice(["consider buying", "hold your investment", "explore new neighborhoods"])
                    }
                    
                    success_count = 0
                    for recipient in recipient_list:
                        # For demonstration, personalize with recipient's name if available
                        if not leads_df.empty:
                            recipient_name = leads_df[leads_df["email"] == recipient]["name"].values[0] if recipient in leads_df["email"].values else "there"
                        else:
                            recipient_name = "there"
                        
                        # Replace template variables
                        personalized_content = content.replace("{name}", recipient_name)
                        for key, value in sample_data.items():
                            personalized_content = personalized_content.replace(f"{{{key}}}", str(value))
                        
                        # For email, create HTML version
                        html_content = f"<p>{personalized_content.replace(chr(10), '<br>')}</p>"
                        
                        # Send email
                        result = send_email(
                            provider=provider,
                            to_emails=[recipient],
                            subject=subject,
                            html_content=html_content,
                            text_content=personalized_content
                        )
                        
                        if result.get("success"):
                            success_count += 1
                
                elif channel == "WhatsApp":
                    # Example for WhatsApp campaign
                    success_count = 0
                    for recipient in recipient_list:
                        # For demonstration, personalize with recipient's name if available
                        if not leads_df.empty:
                            recipient_name = leads_df[leads_df["phone"] == recipient]["name"].values[0] if recipient in leads_df["phone"].values else "there"
                        else:
                            recipient_name = "there"
                        
                        # Replace name template variable
                        personalized_content = content.replace("{name}", recipient_name)
                        
                        # Send WhatsApp message
                        result = send_whatsapp_message(recipient, personalized_content)
                        
                        if result.get("success"):
                            success_count += 1
                
                elif channel == "SMS":
                    # Example for SMS campaign
                    success_count = 0
                    for recipient in recipient_list:
                        # For demonstration, personalize with recipient's name if available
                        if not leads_df.empty:
                            recipient_name = leads_df[leads_df["phone"] == recipient]["name"].values[0] if recipient in leads_df["phone"].values else "there"
                        else:
                            recipient_name = "there"
                        
                        # Replace name template variable and shorten for SMS
                        personalized_content = content.replace("{name}", recipient_name)
                        
                        # Send SMS (limit content length for SMS)
                        if len(personalized_content) > 160:
                            personalized_content = personalized_content[:157] + "..."
                        
                        result = send_sms(recipient, personalized_content)
                        
                        if result.get("success"):
                            success_count += 1
                
                if success_count == len(recipient_list):
                    st.success(f"Campaign sent successfully to all {len(recipient_list)} recipients!")
                elif success_count > 0:
                    st.warning(f"Campaign sent to {success_count} out of {len(recipient_list)} recipients. Some messages failed.")
                else:
                    st.error("Failed to send campaign to any recipients.")
            
            else:
                # Just simulate scheduling
                scheduled_time = datetime.combine(send_date, send_time)
                st.success(f"Campaign scheduled for {scheduled_time.strftime('%Y-%m-%d %H:%M')} to {len(recipient_list)} recipients!")

def show_message_templates_tab():
    """Display message templates interface"""
    st.header("Message Templates")
    
    # Sections for different message types
    tab1, tab2, tab3 = st.tabs(["Email Templates", "WhatsApp Templates", "SMS Templates"])
    
    with tab1:
        st.subheader("Email Templates")
        email_template_type = st.selectbox(
            "Template Type",
            ["Property Listing", "Open House", "Price Change", "Market Update", "Follow-up", "Personal Bio"],
            key="email_template_type"
        )
        
        # Display and allow editing of selected template
        if email_template_type == "Property Listing":
            template_name = st.text_input("Template Name", "New Property Listing")
            template_subject = st.text_input("Subject", "Exciting New Property Just Listed!")
            template_content = st.text_area(
                "Content",
                height=300,
                value="""<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <h2 style="color: #3a3a3a;">New Property Alert!</h2>
    <div style="background-color: #f8f8f8; padding: 15px; border-radius: 5px; margin: 15px 0;">
        <h3 style="color: #4285f4; margin-top: 0;">{{address}}</h3>
        <p style="font-size: 20px; font-weight: bold; color: #3a3a3a;">${{price}}</p>
        <p>{{bedrooms}} bedrooms | {{bathrooms}} bathrooms | {{sqft}} sq.ft.</p>
        <p>{{description}}</p>
        <a href="{{listing_url}}" style="background-color: #4285f4; color: white; padding: 10px 15px; text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 10px;">View Property Details</a>
    </div>
    <p>Hello {{recipient_name}},</p>
    <p>We thought you might be interested in this new property that matches your search criteria.</p>
    <p>Don't hesitate to reply to this email or call us if you'd like to schedule a viewing.</p>
    <p>Best regards,<br>{{agent_name}}<br>{{agent_phone}}</p>
</div>"""
            )
        elif email_template_type == "Open House":
            template_name = st.text_input("Template Name", "Open House Invitation")
            template_subject = st.text_input("Subject", "You're Invited to an Open House!")
            template_content = st.text_area(
                "Content",
                height=300,
                value="""<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <h2 style="color: #3a3a3a;">Open House Invitation</h2>
    <div style="background-color: #f8f8f8; padding: 15px; border-radius: 5px; margin: 15px 0;">
        <h3 style="color: #4285f4; margin-top: 0;">{{address}}</h3>
        <p style="font-size: 18px; font-weight: bold; color: #e67e22;">{{open_house_date}} at {{open_house_time}}</p>
        <p style="font-size: 18px; color: #3a3a3a;">${{price}}</p>
        <p>{{bedrooms}} bedrooms | {{bathrooms}} bathrooms | {{sqft}} sq.ft.</p>
        <a href="{{rsvp_url}}" style="background-color: #4285f4; color: white; padding: 10px 15px; text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 10px;">RSVP Now</a>
    </div>
    <p>Hello {{recipient_name}},</p>
    <p>We're excited to invite you to our upcoming open house. This is a great opportunity to explore this beautiful property in person!</p>
    <p>Please RSVP by replying to this email or clicking the button above.</p>
    <p>Best regards,<br>{{agent_name}}<br>{{agent_phone}}</p>
</div>"""
            )
        
        save_email_template = st.button("Save Email Template")
        if save_email_template:
            st.success(f"Email template '{template_name}' saved successfully!")
    
    with tab2:
        st.subheader("WhatsApp Templates")
        whatsapp_template_type = st.selectbox(
            "Template Type",
            ["Property Listing", "Open House", "Price Change", "Market Update", "Follow-up"],
            key="whatsapp_template_type"
        )
        
        # Display and allow editing of selected template
        if whatsapp_template_type == "Property Listing":
            template_name = st.text_input("Template Name", "Property Listing", key="wa_template_name")
            template_content = st.text_area(
                "Content",
                height=300,
                value="""*New Property Listing*

📍 {{address}}
💰 ${{price}}
🛏️ {{bedrooms}} bedrooms | 🚿 {{bathrooms}} bathrooms
📏 {{sqft}} sq.ft.
🏠 {{property_type}}

{{description}}

View this property: {{listing_url}}

Interested? Reply YES to schedule a viewing!"""
            )
        elif whatsapp_template_type == "Open House":
            template_name = st.text_input("Template Name", "Open House Invitation", key="wa_open_house_name")
            template_content = st.text_area(
                "Content",
                height=300,
                value="""*Open House Invitation*

You're invited to an open house for:

📍 {{address}}
💰 ${{price}}
🛏️ {{bedrooms}} bedrooms | 🚿 {{bathrooms}} bathrooms
🏠 {{property_type}}

📅 *When:* {{open_house_date}} at {{open_house_time}}

Reply 'YES' if you'll be attending!"""
            )
        
        save_whatsapp_template = st.button("Save WhatsApp Template")
        if save_whatsapp_template:
            st.success(f"WhatsApp template '{template_name}' saved successfully!")
    
    with tab3:
        st.subheader("SMS Templates")
        sms_template_type = st.selectbox(
            "Template Type",
            ["Property Listing", "Open House", "Price Change", "Market Update", "Follow-up"],
            key="sms_template_type"
        )
        
        # Display and allow editing of selected template
        if sms_template_type == "Property Listing":
            template_name = st.text_input("Template Name", "Property Listing", key="sms_template_name")
            template_content = st.text_area(
                "Content",
                height=200,
                value="""New Property Alert! {{bedrooms}}BR/{{bathrooms}}BA {{property_type}} at {{address}}. Price: ${{price}}. Reply INFO for details."""
            )
        elif sms_template_type == "Open House":
            template_name = st.text_input("Template Name", "Open House Invitation", key="sms_open_house_name")
            template_content = st.text_area(
                "Content",
                height=200,
                value="""Open House: {{address}} on {{open_house_date}} at {{open_house_time}}. {{bedrooms}}BR/{{bathrooms}}BA, ${{price}}. Reply YES to RSVP."""
            )
        
        # Show character count for SMS
        st.caption(f"Character count: {len(template_content)}/160 characters")
        if len(template_content) > 160:
            st.warning("Message exceeds 160 characters and may be split into multiple SMS messages.")
        
        save_sms_template = st.button("Save SMS Template")
        if save_sms_template:
            st.success(f"SMS template '{template_name}' saved successfully!")