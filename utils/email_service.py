"""
Email service module for sending emails and managing email campaigns.
This module provides functionality for:
1. Sending individual emails
2. Managing email templates
3. Tracking email engagement metrics
4. Scheduling automated email campaigns
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging
import pandas as pd
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from utils.database import Base, get_session

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Email-related database models
class EmailTemplate(Base):
    __tablename__ = "email_templates"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    subject = Column(String(255))
    content = Column(Text)
    category = Column(String(50))  # property_alert, lead_nurture, market_update, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
class EmailCampaign(Base):
    __tablename__ = "email_campaigns"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    description = Column(Text)
    status = Column(String(20))  # active, paused, completed, draft
    trigger_type = Column(String(50))  # scheduled, event_based, manual
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to campaign steps
    steps = relationship("EmailCampaignStep", back_populates="campaign")
    
class EmailCampaignStep(Base):
    __tablename__ = "email_campaign_steps"
    
    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, ForeignKey("email_campaigns.id"))
    template_id = Column(Integer, ForeignKey("email_templates.id"))
    delay_days = Column(Integer)  # Days after previous step or campaign start
    condition = Column(String(255), nullable=True)  # Optional condition for sending this step
    order = Column(Integer)  # Order in the sequence
    
    # Relationships
    campaign = relationship("EmailCampaign", back_populates="steps")
    template = relationship("EmailTemplate")
    
class EmailLog(Base):
    __tablename__ = "email_logs"
    
    id = Column(Integer, primary_key=True)
    recipient_email = Column(String(255))
    subject = Column(String(255))
    campaign_id = Column(Integer, ForeignKey("email_campaigns.id"), nullable=True)
    template_id = Column(Integer, ForeignKey("email_templates.id"), nullable=True)
    sent_at = Column(DateTime, default=datetime.utcnow)
    opened = Column(Boolean, default=False)
    clicked = Column(Boolean, default=False)
    bounced = Column(Boolean, default=False)
    
    # Relationships
    campaign = relationship("EmailCampaign")
    template = relationship("EmailTemplate")

def get_email_config():
    """
    Get email configuration from environment variables
    
    Returns:
        dict: Email configuration parameters
    """
    config = {
        "smtp_server": os.getenv("SMTP_SERVER"),
        "smtp_port": int(os.getenv("SMTP_PORT", "587")),
        "smtp_username": os.getenv("SMTP_USERNAME"),
        "smtp_password": os.getenv("SMTP_PASSWORD"),
        "sender_email": os.getenv("SENDER_EMAIL"),
        "sender_name": os.getenv("SENDER_NAME", "Real Estate Analytics")
    }
    
    # Check if configuration is complete
    required_fields = ["smtp_server", "smtp_username", "smtp_password", "sender_email"]
    missing_fields = [field for field in required_fields if not config[field]]
    
    if missing_fields:
        missing_fields_str = ", ".join(missing_fields)
        logger.warning(f"Email configuration incomplete. Missing: {missing_fields_str}")
        return None
    
    return config

def send_email(recipient_email, subject, content, campaign_id=None, template_id=None):
    """
    Send an email using the configured email service
    
    Args:
        recipient_email (str): Recipient's email address
        subject (str): Email subject
        content (str): Email content (HTML format)
        campaign_id (int, optional): ID of the associated campaign
        template_id (int, optional): ID of the template used
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    config = get_email_config()
    if not config:
        logger.error("Cannot send email: Email configuration is incomplete")
        return False
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = f"{config['sender_name']} <{config['sender_email']}>"
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(content, 'html'))
    
    # Send email
    try:
        server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
        server.starttls()
        server.login(config['smtp_username'], config['smtp_password'])
        server.send_message(msg)
        server.quit()
        
        # Log the email
        log_email(recipient_email, subject, campaign_id, template_id)
        
        return True
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        return False

def log_email(recipient_email, subject, campaign_id=None, template_id=None):
    """
    Log an email that was sent
    
    Args:
        recipient_email (str): Recipient's email address
        subject (str): Email subject
        campaign_id (int, optional): ID of the associated campaign
        template_id (int, optional): ID of the template used
    """
    try:
        session = get_session()
        email_log = EmailLog(
            recipient_email=recipient_email,
            subject=subject,
            campaign_id=campaign_id,
            template_id=template_id
        )
        session.add(email_log)
        session.commit()
        session.close()
    except Exception as e:
        logger.error(f"Error logging email: {e}")

def get_email_templates(category=None):
    """
    Get email templates, optionally filtered by category
    
    Args:
        category (str, optional): Template category filter
        
    Returns:
        list: Email templates
    """
    session = get_session()
    query = session.query(EmailTemplate)
    
    if category:
        query = query.filter(EmailTemplate.category == category)
    
    templates = query.all()
    session.close()
    
    return templates

def add_email_template(name, subject, content, category):
    """
    Add a new email template
    
    Args:
        name (str): Template name
        subject (str): Email subject
        content (str): Email content (HTML)
        category (str): Template category
        
    Returns:
        int: Template ID if successful, None otherwise
    """
    try:
        session = get_session()
        template = EmailTemplate(
            name=name,
            subject=subject,
            content=content,
            category=category
        )
        session.add(template)
        session.commit()
        template_id = template.id
        session.close()
        return template_id
    except Exception as e:
        logger.error(f"Error adding email template: {e}")
        return None

def create_email_campaign(name, description, steps, status="draft", trigger_type="manual"):
    """
    Create a new email campaign
    
    Args:
        name (str): Campaign name
        description (str): Campaign description
        steps (list): List of dictionaries with template_id, delay_days, condition, order
        status (str): Campaign status
        trigger_type (str): Campaign trigger type
        
    Returns:
        int: Campaign ID if successful, None otherwise
    """
    try:
        session = get_session()
        
        # Create campaign
        campaign = EmailCampaign(
            name=name,
            description=description,
            status=status,
            trigger_type=trigger_type
        )
        session.add(campaign)
        session.flush()
        
        # Add campaign steps
        for step in steps:
            campaign_step = EmailCampaignStep(
                campaign_id=campaign.id,
                template_id=step['template_id'],
                delay_days=step['delay_days'],
                condition=step.get('condition'),
                order=step['order']
            )
            session.add(campaign_step)
        
        session.commit()
        campaign_id = campaign.id
        session.close()
        return campaign_id
    except Exception as e:
        logger.error(f"Error creating email campaign: {e}")
        if 'session' in locals():
            session.rollback()
            session.close()
        return None

def get_email_campaigns(status=None):
    """
    Get email campaigns, optionally filtered by status
    
    Args:
        status (str, optional): Campaign status filter
        
    Returns:
        list: Email campaigns
    """
    session = get_session()
    query = session.query(EmailCampaign)
    
    if status:
        query = query.filter(EmailCampaign.status == status)
    
    campaigns = query.all()
    session.close()
    
    return campaigns

def get_campaign_steps(campaign_id):
    """
    Get steps for a specific campaign
    
    Args:
        campaign_id (int): Campaign ID
        
    Returns:
        list: Campaign steps ordered by sequence
    """
    session = get_session()
    steps = session.query(EmailCampaignStep).filter(
        EmailCampaignStep.campaign_id == campaign_id
    ).order_by(EmailCampaignStep.order).all()
    session.close()
    
    return steps

def update_campaign_status(campaign_id, status):
    """
    Update the status of an email campaign
    
    Args:
        campaign_id (int): Campaign ID
        status (str): New status
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        session = get_session()
        campaign = session.query(EmailCampaign).filter(EmailCampaign.id == campaign_id).first()
        
        if not campaign:
            logger.error(f"Campaign with ID {campaign_id} not found")
            session.close()
            return False
        
        campaign.status = status
        campaign.updated_at = datetime.utcnow()
        session.commit()
        session.close()
        return True
    except Exception as e:
        logger.error(f"Error updating campaign status: {e}")
        if 'session' in locals():
            session.rollback()
            session.close()
        return False

def get_email_performance(campaign_id=None, start_date=None, end_date=None):
    """
    Get email performance metrics
    
    Args:
        campaign_id (int, optional): Filter by campaign ID
        start_date (datetime, optional): Filter by start date
        end_date (datetime, optional): Filter by end date
        
    Returns:
        dict: Performance metrics
    """
    session = get_session()
    query = session.query(EmailLog)
    
    if campaign_id:
        query = query.filter(EmailLog.campaign_id == campaign_id)
    
    if start_date:
        query = query.filter(EmailLog.sent_at >= start_date)
    
    if end_date:
        query = query.filter(EmailLog.sent_at <= end_date)
    
    emails = query.all()
    session.close()
    
    if not emails:
        return {
            "total_sent": 0,
            "open_rate": 0,
            "click_rate": 0,
            "bounce_rate": 0
        }
    
    total_sent = len(emails)
    opened = sum(1 for email in emails if email.opened)
    clicked = sum(1 for email in emails if email.clicked)
    bounced = sum(1 for email in emails if email.bounced)
    
    return {
        "total_sent": total_sent,
        "open_rate": (opened / total_sent) * 100 if total_sent > 0 else 0,
        "click_rate": (clicked / total_sent) * 100 if total_sent > 0 else 0,
        "bounce_rate": (bounced / total_sent) * 100 if total_sent > 0 else 0
    }

def send_campaign_email(campaign_id, recipient_email):
    """
    Send the first email in a campaign to a recipient
    
    Args:
        campaign_id (int): Campaign ID
        recipient_email (str): Recipient email address
        
    Returns:
        bool: True if successful, False otherwise
    """
    session = get_session()
    
    # Get campaign
    campaign = session.query(EmailCampaign).filter(EmailCampaign.id == campaign_id).first()
    if not campaign or campaign.status != "active":
        logger.error(f"Campaign {campaign_id} not found or not active")
        session.close()
        return False
    
    # Get first step
    first_step = session.query(EmailCampaignStep).filter(
        EmailCampaignStep.campaign_id == campaign_id,
        EmailCampaignStep.order == 1
    ).first()
    
    if not first_step:
        logger.error(f"No steps found for campaign {campaign_id}")
        session.close()
        return False
    
    # Get template
    template = session.query(EmailTemplate).filter(EmailTemplate.id == first_step.template_id).first()
    if not template:
        logger.error(f"Template {first_step.template_id} not found")
        session.close()
        return False
    
    session.close()
    
    # Send email
    return send_email(
        recipient_email=recipient_email,
        subject=template.subject,
        content=template.content,
        campaign_id=campaign_id,
        template_id=template.id
    )