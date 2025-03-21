"""
Email service utility for sending marketing emails and newsletters.
This module provides functions to send emails through various email service providers.
"""

import os
import json
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import base64
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
EMAIL_PROVIDERS = {
    "smtp": "SMTP Server (Generic)",
    "mailchimp": "Mailchimp",
    "sendgrid": "SendGrid",
    "constant_contact": "Constant Contact",
    "mailgun": "Mailgun"
}

def check_email_credentials():
    """
    Check if email service credentials are configured.
    
    Returns:
        dict: Status of available email service configurations
    """
    credentials = {}
    
    # Check generic SMTP
    smtp_server = os.getenv("EMAIL_SMTP_SERVER")
    smtp_port = os.getenv("EMAIL_SMTP_PORT")
    smtp_user = os.getenv("EMAIL_SMTP_USER")
    smtp_password = os.getenv("EMAIL_SMTP_PASSWORD")
    
    credentials["smtp"] = {
        "configured": bool(smtp_server and smtp_port and smtp_user and smtp_password),
        "server": smtp_server
    }
    
    # Check SendGrid
    sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
    credentials["sendgrid"] = {
        "configured": bool(sendgrid_api_key)
    }
    
    # Check Mailchimp
    mailchimp_api_key = os.getenv("MAILCHIMP_API_KEY")
    credentials["mailchimp"] = {
        "configured": bool(mailchimp_api_key)
    }
    
    # Check Mailgun
    mailgun_api_key = os.getenv("MAILGUN_API_KEY")
    mailgun_domain = os.getenv("MAILGUN_DOMAIN")
    credentials["mailgun"] = {
        "configured": bool(mailgun_api_key and mailgun_domain),
        "domain": mailgun_domain
    }
    
    # Check Constant Contact
    constant_contact_api_key = os.getenv("CONSTANT_CONTACT_API_KEY")
    constant_contact_token = os.getenv("CONSTANT_CONTACT_ACCESS_TOKEN")
    credentials["constant_contact"] = {
        "configured": bool(constant_contact_api_key and constant_contact_token)
    }
    
    return credentials

def get_available_email_providers():
    """
    Get a list of configured email providers.
    
    Returns:
        list: Names of available email providers
    """
    credentials = check_email_credentials()
    available_providers = [
        {"id": provider_id, "name": EMAIL_PROVIDERS[provider_id]} 
        for provider_id in credentials 
        if credentials[provider_id]["configured"]
    ]
    return available_providers

def send_test_email(provider, to_email, from_email=None, subject="Test Email"):
    """
    Send a test email to verify the configuration.
    
    Args:
        provider (str): Email provider to use (smtp, sendgrid, etc.)
        to_email (str): Recipient email address
        from_email (str, optional): Sender email address
        subject (str): Email subject
        
    Returns:
        dict: Status and message
    """
    try:
        # Simple plain text email for testing
        html_content = "<html><body><h1>Test Email</h1><p>This is a test email from your real estate marketing system.</p></body></html>"
        text_content = "Test Email\n\nThis is a test email from your real estate marketing system."
        
        # Send the email
        status = send_email(
            provider=provider,
            to_emails=[to_email],
            subject=subject,
            html_content=html_content,
            text_content=text_content,
            from_email=from_email
        )
        
        return status
        
    except Exception as e:
        logger.error(f"Error sending test email: {e}")
        return {"success": False, "message": f"Error: {str(e)}"}

def send_email(
    provider, 
    to_emails, 
    subject, 
    html_content, 
    text_content=None, 
    from_email=None, 
    from_name=None,
    reply_to=None,
    attachments=None,
    embedded_images=None,
    campaign_name=None
):
    """
    Send an email using the specified provider.
    
    Args:
        provider (str): Email provider to use (smtp, sendgrid, etc.)
        to_emails (list): List of recipient email addresses
        subject (str): Email subject
        html_content (str): HTML content of the email
        text_content (str, optional): Plain text content for email clients that don't support HTML
        from_email (str, optional): Sender email address
        from_name (str, optional): Sender name
        reply_to (str, optional): Reply-to email address
        attachments (list, optional): List of file paths to attach
        embedded_images (dict, optional): Dictionary of image IDs to image data
        campaign_name (str, optional): Name for tracking the campaign
        
    Returns:
        dict: Status and message
    """
    credentials = check_email_credentials()
    
    # Validate input
    if not to_emails or not isinstance(to_emails, list):
        return {"success": False, "message": "Invalid recipient list"}
    
    if not subject or not html_content:
        return {"success": False, "message": "Subject and HTML content are required"}
    
    # Check if provider is configured
    if provider not in credentials or not credentials[provider]["configured"]:
        available_providers = ", ".join([p for p in credentials if credentials[p]["configured"]])
        return {
            "success": False, 
            "message": f"Provider '{provider}' is not configured. Available providers: {available_providers}"
        }
    
    # Set default sender
    if not from_email:
        from_email = os.getenv("DEFAULT_EMAIL_SENDER", "noreply@example.com")
    
    if not from_name:
        from_name = os.getenv("DEFAULT_EMAIL_SENDER_NAME", "Real Estate Marketing")
    
    try:
        # Call the appropriate sending function based on provider
        if provider == "smtp":
            result = _send_via_smtp(
                to_emails, subject, html_content, text_content, 
                from_email, from_name, reply_to, attachments, embedded_images
            )
        elif provider == "sendgrid":
            result = _send_via_sendgrid(
                to_emails, subject, html_content, text_content, 
                from_email, from_name, reply_to, attachments, embedded_images, campaign_name
            )
        elif provider == "mailchimp":
            result = _send_via_mailchimp(
                to_emails, subject, html_content, text_content, 
                from_email, from_name, reply_to, attachments, embedded_images, campaign_name
            )
        elif provider == "mailgun":
            result = _send_via_mailgun(
                to_emails, subject, html_content, text_content, 
                from_email, from_name, reply_to, attachments, embedded_images, campaign_name
            )
        elif provider == "constant_contact":
            result = _send_via_constant_contact(
                to_emails, subject, html_content, text_content, 
                from_email, from_name, reply_to, attachments, embedded_images, campaign_name
            )
        else:
            return {"success": False, "message": f"Unknown provider: {provider}"}
        
        return result
        
    except Exception as e:
        logger.error(f"Error sending email with {provider}: {e}")
        return {"success": False, "message": f"Error: {str(e)}"}

def _send_via_smtp(
    to_emails, subject, html_content, text_content, 
    from_email, from_name, reply_to, attachments, embedded_images
):
    """Send email via SMTP server."""
    try:
        # Get SMTP settings from environment
        smtp_server = os.getenv("EMAIL_SMTP_SERVER")
        smtp_port = int(os.getenv("EMAIL_SMTP_PORT", 587))
        smtp_user = os.getenv("EMAIL_SMTP_USER")
        smtp_password = os.getenv("EMAIL_SMTP_PASSWORD")
        use_tls = os.getenv("EMAIL_SMTP_USE_TLS", "True").lower() == "true"
        
        # Create message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{from_name} <{from_email}>" if from_name else from_email
        msg["To"] = ", ".join(to_emails)
        
        if reply_to:
            msg["Reply-To"] = reply_to
        
        # Attach plain text and HTML parts
        if text_content:
            msg.attach(MIMEText(text_content, "plain"))
        msg.attach(MIMEText(html_content, "html"))
        
        # Attach files if provided
        if attachments:
            for file_path in attachments:
                with open(file_path, "rb") as file:
                    attachment = MIMEImage(file.read())
                    attachment.add_header("Content-Disposition", f"attachment; filename={os.path.basename(file_path)}")
                    msg.attach(attachment)
        
        # Embed images if provided
        if embedded_images:
            for img_id, img_data in embedded_images.items():
                img = MIMEImage(img_data)
                img.add_header("Content-ID", f"<{img_id}>")
                img.add_header("Content-Disposition", "inline")
                msg.attach(img)
        
        # Connect to SMTP server and send
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            if use_tls:
                server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        
        return {"success": True, "message": f"Email sent to {len(to_emails)} recipients"}
        
    except Exception as e:
        logger.error(f"SMTP error: {e}")
        return {"success": False, "message": f"SMTP error: {str(e)}"}

def _send_via_sendgrid(
    to_emails, subject, html_content, text_content, 
    from_email, from_name, reply_to, attachments, embedded_images, campaign_name
):
    """Send email via SendGrid API."""
    # In a production environment, this would use the SendGrid API
    logger.info("SendGrid implementation would be called here")
    return {
        "success": False, 
        "message": "SendGrid integration requires API key. Please configure SENDGRID_API_KEY."
    }

def _send_via_mailchimp(
    to_emails, subject, html_content, text_content, 
    from_email, from_name, reply_to, attachments, embedded_images, campaign_name
):
    """Send email via Mailchimp API."""
    # In a production environment, this would use the Mailchimp API
    logger.info("Mailchimp implementation would be called here")
    return {
        "success": False, 
        "message": "Mailchimp integration requires API key. Please configure MAILCHIMP_API_KEY."
    }

def _send_via_mailgun(
    to_emails, subject, html_content, text_content, 
    from_email, from_name, reply_to, attachments, embedded_images, campaign_name
):
    """Send email via Mailgun API."""
    # In a production environment, this would use the Mailgun API
    logger.info("Mailgun implementation would be called here")
    return {
        "success": False, 
        "message": "Mailgun integration requires API key. Please configure MAILGUN_API_KEY and MAILGUN_DOMAIN."
    }

def _send_via_constant_contact(
    to_emails, subject, html_content, text_content, 
    from_email, from_name, reply_to, attachments, embedded_images, campaign_name
):
    """Send email via Constant Contact API."""
    # In a production environment, this would use the Constant Contact API
    logger.info("Constant Contact implementation would be called here")
    return {
        "success": False, 
        "message": "Constant Contact integration requires API key. Please configure CONSTANT_CONTACT_API_KEY."
    }

def save_email_template(name, subject, html_content, text_content=None, category="general"):
    """
    Save an email template for future use.
    
    Args:
        name (str): Template name
        subject (str): Email subject
        html_content (str): HTML content
        text_content (str, optional): Plain text content
        category (str): Template category
        
    Returns:
        bool: True if saved successfully, False otherwise
    """
    try:
        # Ensure templates directory exists
        os.makedirs("templates/email", exist_ok=True)
        
        # Create template object
        template = {
            "name": name,
            "subject": subject,
            "html_content": html_content,
            "text_content": text_content,
            "category": category
        }
        
        # Generate filename from name
        filename = name.lower().replace(" ", "_") + ".json"
        filepath = os.path.join("templates/email", filename)
        
        # Save template to file
        with open(filepath, "w") as f:
            json.dump(template, f, indent=2)
        
        return True
        
    except Exception as e:
        logger.error(f"Error saving email template: {e}")
        return False

def get_email_templates(category=None):
    """
    Get available email templates.
    
    Args:
        category (str, optional): Filter templates by category
        
    Returns:
        list: Available templates
    """
    templates = []
    
    try:
        # Check if templates directory exists
        if not os.path.exists("templates/email"):
            return []
        
        # List template files
        template_files = [f for f in os.listdir("templates/email") if f.endswith(".json")]
        
        for filename in template_files:
            filepath = os.path.join("templates/email", filename)
            with open(filepath, "r") as f:
                template = json.load(f)
                
            # Apply category filter if specified
            if category and template.get("category") != category:
                continue
                
            template["filename"] = filename
            templates.append(template)
        
    except Exception as e:
        logger.error(f"Error getting email templates: {e}")
    
    return templates

def get_email_template(name=None, filename=None):
    """
    Get a specific email template.
    
    Args:
        name (str, optional): Template name
        filename (str, optional): Template filename
        
    Returns:
        dict: Template data or None if not found
    """
    try:
        if not os.path.exists("templates/email"):
            return None
        
        if filename:
            filepath = os.path.join("templates/email", filename)
            if os.path.exists(filepath):
                with open(filepath, "r") as f:
                    return json.load(f)
        
        if name:
            # Normalize name to filename format
            normalized_name = name.lower().replace(" ", "_") + ".json"
            filepath = os.path.join("templates/email", normalized_name)
            if os.path.exists(filepath):
                with open(filepath, "r") as f:
                    return json.load(f)
            
            # If exact match not found, search all templates
            templates = get_email_templates()
            for template in templates:
                if template.get("name").lower() == name.lower():
                    return template
        
    except Exception as e:
        logger.error(f"Error getting email template: {e}")
    
    return None

def get_email_lists():
    """
    Get available email lists/segments.
    
    Returns:
        list: Available email lists
    """
    # In a production environment, this would fetch from a database or email service API
    
    # Sample lists for demonstration
    sample_lists = [
        {"id": "all_clients", "name": "All Clients", "count": 1250},
        {"id": "buyers", "name": "Active Buyers", "count": 458},
        {"id": "sellers", "name": "Current Sellers", "count": 127},
        {"id": "past_clients", "name": "Past Clients", "count": 765},
        {"id": "investors", "name": "Real Estate Investors", "count": 186},
        {"id": "luxury", "name": "Luxury Market Clients", "count": 93},
        {"id": "first_time", "name": "First-time Homebuyers", "count": 274},
        {"id": "newsletter", "name": "Newsletter Subscribers", "count": 1892}
    ]
    
    return sample_lists

def add_email_subscriber(email, name=None, lists=None, custom_fields=None):
    """
    Add a new subscriber to email lists.
    
    Args:
        email (str): Subscriber email
        name (str, optional): Subscriber name
        lists (list, optional): List IDs to subscribe to
        custom_fields (dict, optional): Additional custom fields
        
    Returns:
        dict: Status and message
    """
    # In a production environment, this would add to database or call email service API
    logger.info(f"Would add subscriber {email} to lists: {lists}")
    
    # For demonstration purposes
    return {
        "success": True,
        "message": f"Subscriber {email} would be added to {len(lists) if lists else 0} lists"
    }

def remove_email_subscriber(email, lists=None):
    """
    Remove a subscriber from email lists.
    
    Args:
        email (str): Subscriber email
        lists (list, optional): List IDs to unsubscribe from (None for all)
        
    Returns:
        dict: Status and message
    """
    # In a production environment, this would remove from database or call email service API
    logger.info(f"Would remove subscriber {email} from lists: {lists if lists else 'all'}")
    
    # For demonstration purposes
    return {
        "success": True,
        "message": f"Subscriber {email} would be removed from specified lists"
    }

def schedule_email_campaign(
    name,
    provider,
    list_ids,
    subject,
    html_content,
    text_content=None,
    from_email=None,
    from_name=None,
    scheduled_time=None
):
    """
    Schedule an email campaign for future delivery.
    
    Args:
        name (str): Campaign name
        provider (str): Email provider to use
        list_ids (list): Lists to send to
        subject (str): Email subject
        html_content (str): HTML content
        text_content (str, optional): Plain text content
        from_email (str, optional): Sender email
        from_name (str, optional): Sender name
        scheduled_time (str, optional): ISO format time for sending
        
    Returns:
        dict: Status and campaign ID
    """
    # In a production environment, this would schedule via the email provider's API
    logger.info(f"Would schedule campaign '{name}' to lists: {list_ids} at {scheduled_time}")
    
    # For demonstration purposes
    return {
        "success": True,
        "message": f"Campaign '{name}' scheduled successfully",
        "campaign_id": f"campaign_{hash(name)}"
    }