"""
Ad platform integration module for connecting with various advertising platforms.
This module provides functionality for:
1. Connecting to ad platforms (Google Ads, Facebook, etc.)
2. Fetching ad performance data
3. Creating and managing ad campaigns
4. Analyzing ad performance
"""

import os
import json
import requests
import logging
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from utils.database import Base, get_session

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ad-related database models
class AdPlatform(Base):
    __tablename__ = "ad_platforms"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100))  # google_ads, facebook_ads, etc.
    display_name = Column(String(100))
    description = Column(Text)
    credentials_json = Column(Text)  # JSON string with API credentials
    connected = Column(Boolean, default=False)
    last_sync = Column(DateTime, nullable=True)
    
class AdCampaign(Base):
    __tablename__ = "ad_campaigns"
    
    id = Column(Integer, primary_key=True)
    platform_id = Column(Integer, ForeignKey("ad_platforms.id"))
    external_id = Column(String(100))  # ID on the ad platform
    name = Column(String(255))
    status = Column(String(50))  # active, paused, completed, etc.
    start_date = Column(DateTime)
    end_date = Column(DateTime, nullable=True)
    budget = Column(Float)
    budget_type = Column(String(50))  # daily, lifetime
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    platform = relationship("AdPlatform")
    metrics = relationship("AdCampaignMetrics", back_populates="campaign")
    
class AdCampaignMetrics(Base):
    __tablename__ = "ad_campaign_metrics"
    
    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, ForeignKey("ad_campaigns.id"))
    date = Column(DateTime)
    impressions = Column(Integer)
    clicks = Column(Integer)
    cost = Column(Float)
    conversions = Column(Integer)
    conversion_value = Column(Float)
    ctr = Column(Float)  # Click-through rate
    cpc = Column(Float)  # Cost per click
    conversion_rate = Column(Float)
    roas = Column(Float)  # Return on ad spend
    
    # Relationship
    campaign = relationship("AdCampaign", back_populates="metrics")

def get_credentials(platform_name):
    """
    Get credentials for a specific ad platform
    
    Args:
        platform_name (str): Name of the platform (google_ads, facebook_ads, etc.)
        
    Returns:
        dict: Platform credentials or None if not found
    """
    session = get_session()
    platform = session.query(AdPlatform).filter(AdPlatform.name == platform_name).first()
    session.close()
    
    if not platform or not platform.credentials_json:
        return None
    
    try:
        return json.loads(platform.credentials_json)
    except json.JSONDecodeError:
        logger.error(f"Invalid credentials JSON for platform {platform_name}")
        return None

def save_credentials(platform_name, display_name, credentials, description=None):
    """
    Save credentials for an ad platform
    
    Args:
        platform_name (str): Name of the platform
        display_name (str): Display name for the platform
        credentials (dict): Credentials to save
        description (str, optional): Platform description
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        credentials_json = json.dumps(credentials)
        
        session = get_session()
        platform = session.query(AdPlatform).filter(AdPlatform.name == platform_name).first()
        
        if platform:
            platform.display_name = display_name
            platform.credentials_json = credentials_json
            if description:
                platform.description = description
            platform.updated_at = datetime.utcnow()
        else:
            platform = AdPlatform(
                name=platform_name,
                display_name=display_name,
                credentials_json=credentials_json,
                description=description
            )
            session.add(platform)
        
        session.commit()
        session.close()
        return True
    except Exception as e:
        logger.error(f"Error saving credentials: {e}")
        if 'session' in locals():
            session.rollback()
            session.close()
        return False

def get_google_ads_performance(start_date=None, end_date=None):
    """
    Get performance data from Google Ads
    
    Args:
        start_date (datetime, optional): Start date for the data range
        end_date (datetime, optional): End date for the data range
        
    Returns:
        DataFrame: Performance data or None if error
    """
    credentials = get_credentials('google_ads')
    if not credentials:
        logger.error("Google Ads credentials not found")
        return None
    
    # Set default date range if not provided
    if not end_date:
        end_date = datetime.now()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    # Format dates
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')
    
    try:
        # In a real implementation, we would use the Google Ads API client
        # Here we'll use a simplified approach
        
        # Example implementation using requests for a hypothetical Google Ads API endpoint
        api_url = "https://googleads.googleapis.com/v11/customers/{customer_id}/googleAds:search"
        api_url = api_url.format(customer_id=credentials.get('customer_id'))
        
        headers = {
            "Authorization": f"Bearer {credentials.get('access_token')}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "query": f"""
                SELECT 
                    campaign.id, 
                    campaign.name, 
                    metrics.impressions, 
                    metrics.clicks, 
                    metrics.cost_micros, 
                    metrics.conversions,
                    metrics.conversions_value
                FROM campaign 
                WHERE segments.date BETWEEN '{start_str}' AND '{end_str}'
            """
        }
        
        # This is commented out since we don't have actual Google Ads credentials
        # response = requests.post(api_url, headers=headers, json=payload)
        # response.raise_for_status()
        # data = response.json()
        
        # Process and save the data
        # [Implementation details]
        
        # For now, let's load campaigns from our database
        session = get_session()
        campaigns = session.query(AdCampaign).filter(
            AdCampaign.platform_id == 1,  # Assuming Google Ads has ID 1
            AdCampaign.start_date >= start_date,
            AdCampaign.end_date <= end_date if AdCampaign.end_date else True
        ).all()
        
        metrics = []
        for campaign in campaigns:
            campaign_metrics = session.query(AdCampaignMetrics).filter(
                AdCampaignMetrics.campaign_id == campaign.id,
                AdCampaignMetrics.date >= start_date,
                AdCampaignMetrics.date <= end_date
            ).all()
            
            for metric in campaign_metrics:
                metrics.append({
                    'campaign_id': campaign.id,
                    'campaign_name': campaign.name,
                    'date': metric.date,
                    'impressions': metric.impressions,
                    'clicks': metric.clicks,
                    'cost': metric.cost,
                    'conversions': metric.conversions,
                    'conversion_value': metric.conversion_value,
                    'ctr': metric.ctr,
                    'cpc': metric.cpc,
                    'conversion_rate': metric.conversion_rate,
                    'roas': metric.roas
                })
        
        session.close()
        
        if not metrics:
            logger.warning("No Google Ads metrics found for the specified date range")
            return pd.DataFrame()
        
        return pd.DataFrame(metrics)
    
    except Exception as e:
        logger.error(f"Error getting Google Ads performance: {e}")
        return None

def get_facebook_ads_performance(start_date=None, end_date=None):
    """
    Get performance data from Facebook Ads
    
    Args:
        start_date (datetime, optional): Start date for the data range
        end_date (datetime, optional): End date for the data range
        
    Returns:
        DataFrame: Performance data or None if error
    """
    credentials = get_credentials('facebook_ads')
    if not credentials:
        logger.error("Facebook Ads credentials not found")
        return None
    
    # Set default date range if not provided
    if not end_date:
        end_date = datetime.now()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    # Format dates
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')
    
    try:
        # In a real implementation, we would use the Facebook Marketing API
        # Here we'll use a simplified approach
        
        # Example implementation using requests for Facebook Marketing API
        api_url = f"https://graph.facebook.com/v15.0/act_{credentials.get('ad_account_id')}/insights"
        
        params = {
            "access_token": credentials.get('access_token'),
            "level": "campaign",
            "fields": "campaign_id,campaign_name,impressions,clicks,spend,conversions,conversion_values",
            "time_range": json.dumps({
                "since": start_str,
                "until": end_str
            }),
            "time_increment": 1  # Daily breakdown
        }
        
        # This is commented out since we don't have actual Facebook credentials
        # response = requests.get(api_url, params=params)
        # response.raise_for_status()
        # data = response.json()
        
        # Process and save the data
        # [Implementation details]
        
        # For now, let's load campaigns from our database
        session = get_session()
        campaigns = session.query(AdCampaign).filter(
            AdCampaign.platform_id == 2,  # Assuming Facebook Ads has ID 2
            AdCampaign.start_date >= start_date,
            AdCampaign.end_date <= end_date if AdCampaign.end_date else True
        ).all()
        
        metrics = []
        for campaign in campaigns:
            campaign_metrics = session.query(AdCampaignMetrics).filter(
                AdCampaignMetrics.campaign_id == campaign.id,
                AdCampaignMetrics.date >= start_date,
                AdCampaignMetrics.date <= end_date
            ).all()
            
            for metric in campaign_metrics:
                metrics.append({
                    'campaign_id': campaign.id,
                    'campaign_name': campaign.name,
                    'date': metric.date,
                    'impressions': metric.impressions,
                    'clicks': metric.clicks,
                    'cost': metric.cost,
                    'conversions': metric.conversions,
                    'conversion_value': metric.conversion_value,
                    'ctr': metric.ctr,
                    'cpc': metric.cpc,
                    'conversion_rate': metric.conversion_rate,
                    'roas': metric.roas
                })
        
        session.close()
        
        if not metrics:
            logger.warning("No Facebook Ads metrics found for the specified date range")
            return pd.DataFrame()
        
        return pd.DataFrame(metrics)
    
    except Exception as e:
        logger.error(f"Error getting Facebook Ads performance: {e}")
        return None

def get_all_ad_performance(start_date=None, end_date=None, platforms=None):
    """
    Get performance data from all connected ad platforms
    
    Args:
        start_date (datetime, optional): Start date for the data range
        end_date (datetime, optional): End date for the data range
        platforms (list, optional): List of platform names to include
        
    Returns:
        dict: Dictionary with DataFrames for each platform
    """
    results = {}
    
    # Get all platforms if none specified
    if not platforms:
        session = get_session()
        all_platforms = session.query(AdPlatform).filter(AdPlatform.connected == True).all()
        session.close()
        platforms = [p.name for p in all_platforms]
    
    # Get data for each platform
    for platform in platforms:
        if platform == 'google_ads':
            results[platform] = get_google_ads_performance(start_date, end_date)
        elif platform == 'facebook_ads':
            results[platform] = get_facebook_ads_performance(start_date, end_date)
        # Add more platforms as needed
    
    return results

def save_ad_campaign(platform_id, external_id, name, status, start_date, end_date=None, 
                   budget=0, budget_type="daily"):
    """
    Save an ad campaign to the database
    
    Args:
        platform_id (int): Platform ID
        external_id (str): External campaign ID
        name (str): Campaign name
        status (str): Campaign status
        start_date (datetime): Campaign start date
        end_date (datetime, optional): Campaign end date
        budget (float): Campaign budget
        budget_type (str): Budget type (daily, lifetime)
        
    Returns:
        int: Campaign ID if successful, None otherwise
    """
    try:
        session = get_session()
        
        # Check if campaign already exists
        campaign = session.query(AdCampaign).filter(
            AdCampaign.platform_id == platform_id,
            AdCampaign.external_id == external_id
        ).first()
        
        if campaign:
            # Update existing campaign
            campaign.name = name
            campaign.status = status
            campaign.start_date = start_date
            campaign.end_date = end_date
            campaign.budget = budget
            campaign.budget_type = budget_type
            campaign.updated_at = datetime.utcnow()
        else:
            # Create new campaign
            campaign = AdCampaign(
                platform_id=platform_id,
                external_id=external_id,
                name=name,
                status=status,
                start_date=start_date,
                end_date=end_date,
                budget=budget,
                budget_type=budget_type
            )
            session.add(campaign)
        
        session.commit()
        campaign_id = campaign.id
        session.close()
        return campaign_id
    
    except Exception as e:
        logger.error(f"Error saving ad campaign: {e}")
        if 'session' in locals():
            session.rollback()
            session.close()
        return None

def save_ad_metrics(campaign_id, date, impressions, clicks, cost, conversions=0, 
                  conversion_value=0, ctr=None, cpc=None, conversion_rate=None, roas=None):
    """
    Save ad campaign metrics to the database
    
    Args:
        campaign_id (int): Campaign ID
        date (datetime): Metrics date
        impressions (int): Number of impressions
        clicks (int): Number of clicks
        cost (float): Campaign cost
        conversions (int, optional): Number of conversions
        conversion_value (float, optional): Conversion value
        ctr (float, optional): Click-through rate
        cpc (float, optional): Cost per click
        conversion_rate (float, optional): Conversion rate
        roas (float, optional): Return on ad spend
        
    Returns:
        int: Metrics ID if successful, None otherwise
    """
    try:
        # Calculate derived metrics if not provided
        if ctr is None and impressions > 0:
            ctr = (clicks / impressions) * 100
        
        if cpc is None and clicks > 0:
            cpc = cost / clicks
        
        if conversion_rate is None and clicks > 0:
            conversion_rate = (conversions / clicks) * 100
        
        if roas is None and cost > 0:
            roas = conversion_value / cost
        
        session = get_session()
        
        # Check if metrics for this date already exist
        metrics = session.query(AdCampaignMetrics).filter(
            AdCampaignMetrics.campaign_id == campaign_id,
            AdCampaignMetrics.date == date
        ).first()
        
        if metrics:
            # Update existing metrics
            metrics.impressions = impressions
            metrics.clicks = clicks
            metrics.cost = cost
            metrics.conversions = conversions
            metrics.conversion_value = conversion_value
            metrics.ctr = ctr
            metrics.cpc = cpc
            metrics.conversion_rate = conversion_rate
            metrics.roas = roas
        else:
            # Create new metrics
            metrics = AdCampaignMetrics(
                campaign_id=campaign_id,
                date=date,
                impressions=impressions,
                clicks=clicks,
                cost=cost,
                conversions=conversions,
                conversion_value=conversion_value,
                ctr=ctr,
                cpc=cpc,
                conversion_rate=conversion_rate,
                roas=roas
            )
            session.add(metrics)
        
        session.commit()
        metrics_id = metrics.id
        session.close()
        return metrics_id
    
    except Exception as e:
        logger.error(f"Error saving ad metrics: {e}")
        if 'session' in locals():
            session.rollback()
            session.close()
        return None

def get_ad_platforms():
    """
    Get all configured ad platforms
    
    Returns:
        list: Ad platforms
    """
    session = get_session()
    platforms = session.query(AdPlatform).all()
    session.close()
    return platforms

def get_ad_campaigns(platform_id=None, status=None):
    """
    Get ad campaigns, optionally filtered by platform and status
    
    Args:
        platform_id (int, optional): Filter by platform ID
        status (str, optional): Filter by campaign status
        
    Returns:
        list: Ad campaigns
    """
    session = get_session()
    query = session.query(AdCampaign)
    
    if platform_id:
        query = query.filter(AdCampaign.platform_id == platform_id)
    
    if status:
        query = query.filter(AdCampaign.status == status)
    
    campaigns = query.all()
    session.close()
    return campaigns

def get_campaign_metrics(campaign_id, start_date=None, end_date=None):
    """
    Get metrics for a specific campaign
    
    Args:
        campaign_id (int): Campaign ID
        start_date (datetime, optional): Filter by start date
        end_date (datetime, optional): Filter by end date
        
    Returns:
        list: Campaign metrics
    """
    session = get_session()
    query = session.query(AdCampaignMetrics).filter(AdCampaignMetrics.campaign_id == campaign_id)
    
    if start_date:
        query = query.filter(AdCampaignMetrics.date >= start_date)
    
    if end_date:
        query = query.filter(AdCampaignMetrics.date <= end_date)
    
    metrics = query.order_by(AdCampaignMetrics.date).all()
    session.close()
    return metrics

def sync_platform_data(platform_name, days=30):
    """
    Sync data from an ad platform for the last X days
    
    Args:
        platform_name (str): Platform name
        days (int): Number of days to sync
        
    Returns:
        bool: True if successful, False otherwise
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    try:
        if platform_name == 'google_ads':
            # Implementation for Google Ads
            # In a real implementation, you would call the API and process the data
            pass
        elif platform_name == 'facebook_ads':
            # Implementation for Facebook Ads
            pass
        # Add more platforms as needed
        
        # Update last sync time
        session = get_session()
        platform = session.query(AdPlatform).filter(AdPlatform.name == platform_name).first()
        
        if platform:
            platform.last_sync = datetime.utcnow()
            session.commit()
        
        session.close()
        return True
    
    except Exception as e:
        logger.error(f"Error syncing platform data: {e}")
        if 'session' in locals():
            session.close()
        return False