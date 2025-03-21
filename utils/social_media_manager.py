"""
Social media and ad campaign management utility.
This module provides functions to manage social media posts and advertising campaigns
across multiple platforms including Facebook, Instagram, Google, Twitter, TikTok, and LinkedIn.
"""

import os
import json
import logging
import random
from datetime import datetime, timedelta
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
PLATFORMS = {
    "facebook": "Facebook",
    "instagram": "Instagram",
    "google": "Google",
    "twitter": "Twitter",
    "tiktok": "TikTok",
    "linkedin": "LinkedIn",
    "whatsapp": "WhatsApp",
    "sms": "SMS"
}

AD_TYPES = {
    "facebook": ["Image", "Carousel", "Video", "Collection", "Instant Experience"],
    "instagram": ["Image", "Carousel", "Video", "Story", "Reels"],
    "google": ["Search", "Display", "Discovery", "Video", "Local"],
    "twitter": ["Promoted Tweet", "Promoted Account", "Promoted Trend", "Image", "Video"],
    "tiktok": ["In-Feed", "TopView", "Branded Effect", "Branded Hashtag Challenge"],
    "linkedin": ["Sponsored Content", "Text Ad", "Dynamic Ad", "Message Ad", "Conversation Ad"],
    "whatsapp": ["Template Message", "List Message", "Button Message", "Interactive Message"],
    "sms": ["Standard SMS", "Promotional SMS", "OTP Message", "Transaction Notification"]
}

def check_platform_credentials():
    """
    Check if social media platform credentials are configured.
    
    Returns:
        dict: Status of available platform configurations
    """
    credentials = {}
    
    # Check Facebook/Instagram (Meta)
    meta_app_id = os.getenv("META_APP_ID")
    meta_app_secret = os.getenv("META_APP_SECRET")
    meta_access_token = os.getenv("META_ACCESS_TOKEN")
    
    credentials["facebook"] = {
        "configured": bool(meta_app_id and meta_app_secret and meta_access_token)
    }
    credentials["instagram"] = {
        "configured": bool(meta_app_id and meta_app_secret and meta_access_token)
    }
    
    # Check Google
    google_client_id = os.getenv("GOOGLE_CLIENT_ID")
    google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    google_refresh_token = os.getenv("GOOGLE_REFRESH_TOKEN")
    
    credentials["google"] = {
        "configured": bool(google_client_id and google_client_secret and google_refresh_token)
    }
    
    # Check Twitter
    twitter_api_key = os.getenv("TWITTER_API_KEY")
    twitter_api_secret = os.getenv("TWITTER_API_SECRET")
    twitter_access_token = os.getenv("TWITTER_ACCESS_TOKEN")
    twitter_token_secret = os.getenv("TWITTER_TOKEN_SECRET")
    
    credentials["twitter"] = {
        "configured": bool(twitter_api_key and twitter_api_secret and twitter_access_token and twitter_token_secret)
    }
    
    # Check TikTok
    tiktok_app_id = os.getenv("TIKTOK_APP_ID")
    tiktok_app_secret = os.getenv("TIKTOK_APP_SECRET")
    tiktok_access_token = os.getenv("TIKTOK_ACCESS_TOKEN")
    
    credentials["tiktok"] = {
        "configured": bool(tiktok_app_id and tiktok_app_secret and tiktok_access_token)
    }
    
    # Check LinkedIn
    linkedin_client_id = os.getenv("LINKEDIN_CLIENT_ID")
    linkedin_client_secret = os.getenv("LINKEDIN_CLIENT_SECRET")
    linkedin_access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
    
    credentials["linkedin"] = {
        "configured": bool(linkedin_client_id and linkedin_client_secret and linkedin_access_token)
    }
    
    # Check WhatsApp Business API
    whatsapp_phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
    whatsapp_business_account_id = os.getenv("WHATSAPP_BUSINESS_ACCOUNT_ID")
    whatsapp_access_token = os.getenv("WHATSAPP_ACCESS_TOKEN")
    
    credentials["whatsapp"] = {
        "configured": bool(whatsapp_phone_number_id and whatsapp_business_account_id and whatsapp_access_token)
    }
    
    # Check SMS Provider (Twilio)
    twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")
    
    credentials["sms"] = {
        "configured": bool(twilio_account_sid and twilio_auth_token and twilio_phone_number)
    }
    
    return credentials

def get_available_platforms():
    """
    Get a list of configured social media platforms.
    
    Returns:
        list: Names of available platforms
    """
    credentials = check_platform_credentials()
    available_platforms = [
        {"id": platform_id, "name": PLATFORMS[platform_id]} 
        for platform_id in credentials 
        if credentials[platform_id]["configured"]
    ]
    return available_platforms

def create_social_post(
    platform, 
    content, 
    media_urls=None, 
    schedule_time=None, 
    location=None, 
    link=None,
    hashtags=None
):
    """
    Create a social media post on the specified platform.
    
    Args:
        platform (str): Target platform ID (facebook, instagram, etc.)
        content (str): Post text content
        media_urls (list, optional): URLs to media files to attach
        schedule_time (str, optional): ISO format time for scheduled posting
        location (str, optional): Location tag for the post
        link (str, optional): URL to include with the post
        hashtags (list, optional): List of hashtags for the post
        
    Returns:
        dict: Status and post ID
    """
    credentials = check_platform_credentials()
    
    # Check if platform is configured
    if platform not in credentials or not credentials[platform]["configured"]:
        available_platforms = ", ".join([p for p in credentials if credentials[p]["configured"]])
        return {
            "success": False, 
            "message": f"Platform '{platform}' is not configured. Available platforms: {available_platforms}"
        }
    
    # Format hashtags
    formatted_hashtags = ""
    if hashtags:
        formatted_hashtags = " ".join([f"#{tag.strip('#')}" for tag in hashtags])
    
    # In a production environment, this would call the platform's API
    logger.info(f"Would create post on {platform}: {content[:50]}...")
    
    if schedule_time:
        logger.info(f"Post scheduled for {schedule_time}")
    
    # For demonstration purposes
    return {
        "success": True,
        "message": f"Post created successfully on {PLATFORMS[platform]}",
        "post_id": f"{platform}_post_{hash(content)}"
    }

def create_ad_campaign(
    platform,
    name,
    ad_type,
    content,
    media_urls=None,
    target_audience=None,
    budget=None,
    duration=None,
    landing_page=None,
    objectives=None
):
    """
    Create an advertising campaign on the specified platform.
    
    Args:
        platform (str): Target platform ID (facebook, instagram, etc.)
        name (str): Campaign name
        ad_type (str): Type of ad for this platform
        content (str): Ad text content
        media_urls (list, optional): URLs to media files for the ad
        target_audience (dict, optional): Targeting parameters
        budget (dict, optional): Budget information (amount, currency, type)
        duration (dict, optional): Campaign duration
        landing_page (str, optional): URL for the ad destination
        objectives (str, optional): Campaign objectives
        
    Returns:
        dict: Status and campaign ID
    """
    credentials = check_platform_credentials()
    
    # Check if platform is configured
    if platform not in credentials or not credentials[platform]["configured"]:
        available_platforms = ", ".join([p for p in credentials if credentials[p]["configured"]])
        return {
            "success": False, 
            "message": f"Platform '{platform}' is not configured. Available platforms: {available_platforms}"
        }
    
    # Validate ad type
    valid_ad_types = AD_TYPES.get(platform, [])
    if ad_type not in valid_ad_types:
        return {
            "success": False,
            "message": f"Invalid ad type '{ad_type}' for {PLATFORMS[platform]}. Valid types: {', '.join(valid_ad_types)}"
        }
    
    # In a production environment, this would call the platform's advertising API
    logger.info(f"Would create {ad_type} campaign '{name}' on {platform}")
    
    if budget:
        budget_amount = budget.get("amount", 0)
        budget_currency = budget.get("currency", "USD")
        budget_type = budget.get("type", "daily")
        logger.info(f"Budget: {budget_amount} {budget_currency} ({budget_type})")
    
    if duration:
        start_date = duration.get("start_date", datetime.now().isoformat())
        end_date = duration.get("end_date", (datetime.now() + timedelta(days=30)).isoformat())
        logger.info(f"Campaign duration: {start_date} to {end_date}")
    
    # For demonstration purposes
    return {
        "success": True,
        "message": f"Ad campaign '{name}' created successfully on {PLATFORMS[platform]}",
        "campaign_id": f"{platform}_campaign_{hash(name)}"
    }

def get_ad_campaign_performance(
    platform=None,
    campaign_ids=None,
    date_range=None
):
    """
    Get performance metrics for ad campaigns.
    
    Args:
        platform (str, optional): Filter by platform
        campaign_ids (list, optional): Specific campaign IDs to retrieve
        date_range (dict, optional): Start and end dates for metrics
        
    Returns:
        DataFrame: Campaign performance data
    """
    # In a production environment, this would fetch actual metrics from the platforms
    
    # Generate sample data for demonstration
    platforms_to_include = [platform] if platform else list(PLATFORMS.keys())
    
    data = []
    
    for p in platforms_to_include:
        # Number of campaigns to generate
        num_campaigns = random.randint(3, 8)
        
        for i in range(num_campaigns):
            campaign_id = f"{p}_campaign_{i}" if not campaign_ids else campaign_ids[i % len(campaign_ids)]
            campaign_name = f"{PLATFORMS[p]} Campaign {i+1}"
            
            # Generate performance metrics
            if p in ["facebook", "instagram"]:
                impressions = random.randint(5000, 50000)
                ctr = random.uniform(0.5, 3.0)
                cpc = random.uniform(0.5, 2.5)
                conversions = random.randint(10, 200)
                spend = random.uniform(250, 2000)
            elif p == "google":
                impressions = random.randint(10000, 100000)
                ctr = random.uniform(1.0, 5.0)
                cpc = random.uniform(0.8, 3.0)
                conversions = random.randint(20, 300)
                spend = random.uniform(500, 3000)
            elif p == "twitter":
                impressions = random.randint(3000, 30000)
                ctr = random.uniform(0.3, 2.0)
                cpc = random.uniform(0.5, 2.0)
                conversions = random.randint(5, 100)
                spend = random.uniform(200, 1500)
            elif p == "tiktok":
                impressions = random.randint(20000, 200000)
                ctr = random.uniform(1.0, 4.0)
                cpc = random.uniform(0.3, 1.5)
                conversions = random.randint(30, 400)
                spend = random.uniform(300, 2500)
            else:  # LinkedIn
                impressions = random.randint(2000, 20000)
                ctr = random.uniform(0.2, 1.5)
                cpc = random.uniform(2.0, 6.0)
                conversions = random.randint(5, 80)
                spend = random.uniform(400, 3000)
            
            clicks = int(impressions * (ctr / 100))
            conversion_rate = (conversions / clicks) * 100 if clicks > 0 else 0
            cost_per_conversion = spend / conversions if conversions > 0 else 0
            roi = ((conversions * 200) - spend) / spend * 100  # Assuming $200 value per conversion
            
            data.append({
                "platform": PLATFORMS[p],
                "campaign_id": campaign_id,
                "campaign_name": campaign_name,
                "impressions": impressions,
                "clicks": clicks,
                "ctr": ctr,
                "cpc": cpc,
                "conversions": conversions,
                "conversion_rate": conversion_rate,
                "spend": spend,
                "cost_per_conversion": cost_per_conversion,
                "roi": roi
            })
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    return df

def get_best_performing_campaigns(metrics_df, metric="roi", top_n=3):
    """
    Get the best performing campaigns based on a specific metric.
    
    Args:
        metrics_df (DataFrame): Campaign metrics data
        metric (str): Metric to sort by (roi, ctr, conversion_rate, etc.)
        top_n (int): Number of top campaigns to return
        
    Returns:
        DataFrame: Top performing campaigns
    """
    if metrics_df.empty:
        return pd.DataFrame()
    
    # Sort by the specified metric in descending order
    sorted_df = metrics_df.sort_values(by=metric, ascending=False)
    
    # Return the top N campaigns
    return sorted_df.head(top_n)

def get_platform_performance_comparison(metrics_df):
    """
    Compare performance across different platforms.
    
    Args:
        metrics_df (DataFrame): Campaign metrics data
        
    Returns:
        DataFrame: Platform performance summary
    """
    if metrics_df.empty:
        return pd.DataFrame()
    
    # Group by platform and calculate average metrics
    platform_summary = metrics_df.groupby("platform").agg({
        "impressions": "sum",
        "clicks": "sum",
        "conversions": "sum",
        "spend": "sum",
        "ctr": "mean",
        "conversion_rate": "mean",
        "cpc": "mean",
        "cost_per_conversion": "mean",
        "roi": "mean"
    }).reset_index()
    
    # Calculate additional metrics
    platform_summary["total_campaigns"] = metrics_df.groupby("platform").size().values
    
    return platform_summary

def get_ad_formats_by_platform():
    """
    Get available ad formats for each platform.
    
    Returns:
        dict: Ad formats by platform
    """
    return AD_TYPES

def get_targeting_options(platform):
    """
    Get available targeting options for a specific platform.
    
    Args:
        platform (str): Platform ID
        
    Returns:
        dict: Targeting options
    """
    # Common targeting options across platforms
    common_options = {
        "demographics": {
            "age_ranges": ["18-24", "25-34", "35-44", "45-54", "55-64", "65+"],
            "genders": ["Male", "Female", "All"]
        },
        "locations": {
            "types": ["Countries", "Regions", "Cities", "Postal Codes", "Radius"]
        },
        "interests": {
            "categories": ["Real Estate", "Home & Garden", "Finance", "Family", "Luxury Goods"]
        }
    }
    
    # Platform-specific options
    platform_options = {
        "facebook": {
            "detailed_targeting": {
                "behaviors": ["First-time homebuyers", "Likely to move", "Recently moved", "Engaged shoppers"],
                "life_events": ["Recently graduated", "Newly engaged", "Recently moved", "New job"],
                "custom_audiences": ["Website visitors", "Property inquiries", "Past clients"]
            },
            "placements": ["Facebook Feed", "Instagram Feed", "Stories", "Right Column", "Marketplace"]
        },
        "instagram": {
            "detailed_targeting": {
                "behaviors": ["Luxury shoppers", "Travel enthusiasts", "Home decor interests"],
                "hashtags": ["realestate", "dreamhome", "luxuryliving", "homebuying"],
                "custom_audiences": ["App users", "Engaged with content", "Similar audiences"]
            },
            "placements": ["Instagram Feed", "Instagram Explore", "Stories", "Reels"]
        },
        "google": {
            "keywords": ["real estate", "homes for sale", "real estate agent", "property listings"],
            "topics": ["Real Estate", "Real Estate Services", "Apartments & Residential Rentals"],
            "placements": ["Search", "Display Network", "YouTube", "Gmail", "Maps"],
            "audience_targeting": ["In-market", "Affinity", "Custom intent", "Remarketing"]
        },
        "twitter": {
            "followers": ["Follow real estate influencers", "Similar to followers"],
            "behaviors": ["Frequent travelers", "High-end retail shoppers", "Business decision-makers"],
            "events": ["Local events", "Seasonal targeting", "Industry events"],
            "conversation_topics": ["Real estate", "Home improvement", "Interior design", "Mortgage", "Investing"]
        },
        "tiktok": {
            "video_interactions": ["Watched real estate videos", "Engaged with property content"],
            "creators": ["Follow home/design creators", "Real estate influencers"],
            "content_categories": ["Luxury", "DIY", "Before & After", "Home Tours"]
        },
        "linkedin": {
            "company_targeting": ["Industry", "Company size", "Company names", "Growth rate", "Connections"],
            "professional": ["Job titles", "Job functions", "Job seniority", "Skills", "Groups"],
            "education": ["Fields of study", "Degrees", "Schools"]
        }
    }
    
    # Return common options plus platform-specific options
    if platform in platform_options:
        return {**common_options, **platform_options[platform]}
    else:
        return common_options

def create_audience(
    name,
    platform,
    criteria,
    description=None
):
    """
    Create a custom audience for ad targeting.
    
    Args:
        name (str): Audience name
        platform (str): Platform ID
        criteria (dict): Targeting criteria
        description (str, optional): Audience description
        
    Returns:
        dict: Status and audience ID
    """
    credentials = check_platform_credentials()
    
    # Check if platform is configured
    if platform not in credentials or not credentials[platform]["configured"]:
        available_platforms = ", ".join([p for p in credentials if credentials[p]["configured"]])
        return {
            "success": False, 
            "message": f"Platform '{platform}' is not configured. Available platforms: {available_platforms}"
        }
    
    # In a production environment, this would call the platform's audience API
    logger.info(f"Would create audience '{name}' on {platform}")
    
    # For demonstration purposes
    return {
        "success": True,
        "message": f"Audience '{name}' created successfully on {PLATFORMS[platform]}",
        "audience_id": f"{platform}_audience_{hash(name)}"
    }

def get_best_posting_times(platform):
    """
    Get recommended posting times for a specific platform.
    
    Args:
        platform (str): Platform ID
        
    Returns:
        dict: Recommended posting times by day
    """
    # Best practices for posting times by platform
    posting_times = {
        "facebook": {
            "Monday": ["8:00 AM", "1:00 PM", "3:00 PM"],
            "Tuesday": ["8:00 AM", "10:00 AM", "1:00 PM", "3:00 PM"],
            "Wednesday": ["8:00 AM", "12:00 PM", "3:00 PM"],
            "Thursday": ["8:00 AM", "10:00 AM", "2:00 PM", "4:00 PM"],
            "Friday": ["8:00 AM", "12:00 PM", "3:00 PM"],
            "Saturday": ["8:00 AM", "12:00 PM", "3:00 PM"],
            "Sunday": ["8:00 AM", "1:00 PM", "7:00 PM"]
        },
        "instagram": {
            "Monday": ["11:00 AM", "2:00 PM", "7:00 PM"],
            "Tuesday": ["11:00 AM", "3:00 PM", "9:00 PM"],
            "Wednesday": ["11:00 AM", "3:00 PM", "8:00 PM"],
            "Thursday": ["11:00 AM", "2:00 PM", "7:00 PM"],
            "Friday": ["10:00 AM", "2:00 PM", "9:00 PM"],
            "Saturday": ["10:00 AM", "3:00 PM", "9:00 PM"],
            "Sunday": ["9:00 AM", "2:00 PM", "8:00 PM"]
        },
        "twitter": {
            "Monday": ["8:00 AM", "12:00 PM", "5:00 PM"],
            "Tuesday": ["8:00 AM", "10:00 AM", "3:00 PM", "5:00 PM"],
            "Wednesday": ["8:00 AM", "12:00 PM", "5:00 PM", "6:00 PM"],
            "Thursday": ["8:00 AM", "11:00 AM", "3:00 PM", "5:00 PM"],
            "Friday": ["8:00 AM", "12:00 PM", "4:00 PM"],
            "Saturday": ["9:00 AM", "2:00 PM"],
            "Sunday": ["9:00 AM", "1:00 PM", "6:00 PM"]
        },
        "linkedin": {
            "Monday": ["8:00 AM", "10:00 AM", "1:00 PM", "5:00 PM"],
            "Tuesday": ["8:00 AM", "10:00 AM", "1:00 PM", "5:00 PM"],
            "Wednesday": ["8:00 AM", "12:00 PM", "3:00 PM", "5:00 PM"],
            "Thursday": ["8:00 AM", "1:00 PM", "5:00 PM"],
            "Friday": ["8:00 AM", "12:00 PM", "3:00 PM"],
            "Saturday": ["10:00 AM"],
            "Sunday": ["10:00 AM"]
        },
        "tiktok": {
            "Monday": ["6:00 AM", "10:00 AM", "2:00 PM", "9:00 PM"],
            "Tuesday": ["2:00 AM", "9:00 AM", "1:00 PM", "9:00 PM"],
            "Wednesday": ["7:00 AM", "11:00 AM", "3:00 PM", "9:00 PM"],
            "Thursday": ["9:00 AM", "12:00 PM", "7:00 PM", "10:00 PM"],
            "Friday": ["5:00 AM", "10:00 AM", "3:00 PM", "10:00 PM"],
            "Saturday": ["11:00 AM", "6:00 PM", "10:00 PM"],
            "Sunday": ["7:00 AM", "2:00 PM", "9:00 PM"]
        }
    }
    
    if platform in posting_times:
        return posting_times[platform]
    else:
        # Return Facebook times as default
        return posting_times["facebook"]

def save_content_calendar(
    calendar_name,
    posts,
    description=None
):
    """
    Save a content calendar for future scheduling.
    
    Args:
        calendar_name (str): Name for the calendar
        posts (list): List of post objects with platform, content, scheduled time
        description (str, optional): Calendar description
        
    Returns:
        dict: Status and calendar ID
    """
    try:
        # Ensure calendars directory exists
        os.makedirs("calendars", exist_ok=True)
        
        # Create calendar object
        calendar = {
            "name": calendar_name,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "posts": posts
        }
        
        # Generate filename from name
        filename = calendar_name.lower().replace(" ", "_") + ".json"
        filepath = os.path.join("calendars", filename)
        
        # Save calendar to file
        with open(filepath, "w") as f:
            json.dump(calendar, f, indent=2)
        
        return {
            "success": True,
            "message": f"Content calendar '{calendar_name}' saved successfully",
            "calendar_id": filename
        }
        
    except Exception as e:
        logger.error(f"Error saving content calendar: {e}")
        return {
            "success": False,
            "message": f"Error saving content calendar: {str(e)}"
        }