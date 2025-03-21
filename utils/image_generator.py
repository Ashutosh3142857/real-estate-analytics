"""
Image generation utility for creating real estate marketing visuals.
This module provides functions to generate realistic property images for marketing.
"""

import os
import random
import requests
import json
import base64
from io import BytesIO
from PIL import Image
import logging
import time
from urllib.parse import quote_plus

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define constants
DEFAULT_IMAGE_WIDTH = 1024
DEFAULT_IMAGE_HEIGHT = 768
CACHE_DIR = "cache/images"

# API keys - in production these would be in environment variables
UNSPLASH_ACCESS_KEY = os.environ.get("UNSPLASH_ACCESS_KEY", "")
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "")

def get_image_from_unsplash(search_query):
    """
    Get an image from Unsplash API based on search query.
    
    Args:
        search_query (str): Search query for finding images
        
    Returns:
        PIL.Image or None: Image from Unsplash or None if failed
    """
    try:
        # For development without a key, use direct image URLs (limited usage per hour)
        encoded_query = quote_plus(search_query)
        
        if UNSPLASH_ACCESS_KEY:
            # With API key
            url = f"https://api.unsplash.com/photos/random?query={encoded_query}&orientation=landscape"
            headers = {
                "Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"
            }
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                img_url = data['urls']['regular']
                img_response = requests.get(img_url)
                img = Image.open(BytesIO(img_response.content))
                return img
        else:
            # Without API key (development mode) - uses Unsplash Source service
            # Note: This is rate-limited and for development only
            img_url = f"https://source.unsplash.com/1200x800/?{encoded_query}"
            response = requests.get(img_url, allow_redirects=True)
            if response.status_code == 200:
                img = Image.open(BytesIO(response.content))
                return img
                
    except Exception as e:
        logger.error(f"Error fetching image from Unsplash: {e}")
    
    return None

def get_image_from_pexels(search_query):
    """
    Get an image from Pexels API based on search query.
    
    Args:
        search_query (str): Search query for finding images
        
    Returns:
        PIL.Image or None: Image from Pexels or None if failed
    """
    try:
        if PEXELS_API_KEY:
            url = f"https://api.pexels.com/v1/search?query={quote_plus(search_query)}&per_page=1"
            headers = {
                "Authorization": PEXELS_API_KEY
            }
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data['photos']:
                    img_url = data['photos'][0]['src']['large']
                    img_response = requests.get(img_url)
                    img = Image.open(BytesIO(img_response.content))
                    return img
        else:
            # Without API key, we can't use Pexels API
            pass
                
    except Exception as e:
        logger.error(f"Error fetching image from Pexels: {e}")
    
    return None

def ensure_cache_dir():
    """Ensure the cache directory exists."""
    os.makedirs(CACHE_DIR, exist_ok=True)

def get_cached_image(image_id):
    """
    Retrieve a cached image if available.
    
    Args:
        image_id (str): Unique identifier for the image
        
    Returns:
        PIL.Image or None: The cached image if available, None otherwise
    """
    image_path = os.path.join(CACHE_DIR, f"{image_id}.png")
    if os.path.exists(image_path):
        try:
            return Image.open(image_path)
        except Exception as e:
            logger.error(f"Error loading cached image: {e}")
    return None

def save_to_cache(image, image_id):
    """
    Save an image to the cache.
    
    Args:
        image (PIL.Image): The image to cache
        image_id (str): Unique identifier for the image
        
    Returns:
        bool: True if saved successfully, False otherwise
    """
    ensure_cache_dir()
    image_path = os.path.join(CACHE_DIR, f"{image_id}.png")
    try:
        image.save(image_path, "PNG")
        return True
    except Exception as e:
        logger.error(f"Error saving image to cache: {e}")
        return False

def generate_property_image(
    property_details, 
    image_type="exterior", 
    style="modern", 
    time_of_day="day", 
    weather="clear",
    use_cache=True
):
    """
    Generate a realistic property image based on the provided details.
    
    Uses Unsplash API or falls back to Pexels for free property images.
    
    Args:
        property_details (dict): Property details including type, features, etc.
        image_type (str): Type of image (exterior, interior, aerial, etc.)
        style (str): Architectural style (modern, traditional, etc.)
        time_of_day (str): Time of day for the image (day, sunset, night)
        weather (str): Weather conditions (clear, cloudy, rainy)
        use_cache (bool): Whether to use cached images if available
        
    Returns:
        PIL.Image: Generated property image
    """
    # Create a unique identifier for this image request
    property_id = property_details.get('property_id', 'unknown')
    property_type = property_details.get('property_type', 'house').lower()
    image_id = f"{property_id}_{image_type}_{style}_{time_of_day}_{weather}"
    
    # Check cache if enabled
    if use_cache:
        cached_image = get_cached_image(image_id)
        if cached_image:
            logger.info(f"Using cached image for {image_id}")
            return cached_image
    
    try:
        # Construct search query based on parameters
        search_terms = []
        
        # Add property type
        if property_type in ['apartment', 'condo', 'condominium']:
            search_terms.append('apartment')
        elif property_type in ['townhouse', 'townhome']:
            search_terms.append('townhouse')
        elif property_type in ['villa', 'mansion']:
            search_terms.append('luxury house')
        else:
            search_terms.append('house')
        
        # Add image type
        if image_type == 'interior':
            if 'apartment' in search_terms:
                search_terms = ['modern apartment interior']
            else:
                search_terms = ['house interior']
        elif image_type == 'aerial':
            search_terms.append('aerial view')
        elif image_type == 'kitchen':
            search_terms = ['modern kitchen']
        elif image_type == 'bathroom':
            search_terms = ['modern bathroom']
        elif image_type == 'bedroom':
            search_terms = ['modern bedroom']
        elif image_type == 'living-room':
            search_terms = ['modern living room']
        
        # Add style if exterior
        if image_type == 'exterior':
            if style == 'modern':
                search_terms.append('modern')
            elif style == 'traditional':
                search_terms.append('traditional')
            elif style == 'colonial':
                search_terms.append('colonial')
            elif style == 'luxury':
                search_terms = ['luxury home']
        
        # Add time of day for exterior shots
        if image_type == 'exterior' and time_of_day != 'day':
            if time_of_day == 'sunset':
                search_terms.append('sunset')
            elif time_of_day == 'night':
                search_terms.append('night')

        # Combine search terms
        search_query = ' '.join(search_terms)
        
        # Try to get an image from Unsplash (public API with no key required for development)
        img = get_image_from_unsplash(search_query)
        
        # If Unsplash fails, try with Pexels
        if img is None:
            img = get_image_from_pexels(search_query)
            
        # If both fail, try with a simpler query
        if img is None:
            img = get_image_from_unsplash("real estate")
            
        # If all API calls fail, use a local placeholder
        if img is None:
            background_color = (
                random.randint(200, 255),
                random.randint(200, 255),
                random.randint(200, 255)
            )
            img = Image.new('RGB', (DEFAULT_IMAGE_WIDTH, DEFAULT_IMAGE_HEIGHT), background_color)
        
        # Save to cache
        if use_cache:
            save_to_cache(img, image_id)
        
        return img
    
    except Exception as e:
        logger.error(f"Error generating property image: {e}")
        # Return a fallback image
        return Image.new('RGB', (DEFAULT_IMAGE_WIDTH, DEFAULT_IMAGE_HEIGHT), (240, 240, 240))

def generate_social_media_image(
    platform,
    property_details,
    theme="professional", 
    include_price=True,
    include_features=True,
    use_cache=True
):
    """
    Generate an image specifically designed for a social media platform.
    
    Args:
        platform (str): Target social media platform (Facebook, Instagram, etc.)
        property_details (dict): Property details including type, features, etc.
        theme (str): Visual theme for the image
        include_price (bool): Whether to include the price
        include_features (bool): Whether to include property features
        use_cache (bool): Whether to use cached images if available
        
    Returns:
        PIL.Image: Generated social media image
    """
    # Define dimensions based on platform
    if platform == "Instagram":
        width, height = 1080, 1080  # Square format
    elif platform == "Facebook":
        width, height = 1200, 630  # Landscape format
    elif platform == "Twitter":
        width, height = 1200, 675  # 16:9 format
    elif platform == "WhatsApp":
        width, height = 800, 800  # Square format for WhatsApp
    else:  # Default/LinkedIn
        width, height = 1200, 627  # LinkedIn format
    
    # Create a unique identifier for this image request
    property_id = property_details.get('property_id', 'unknown')
    property_type = property_details.get('property_type', 'house').lower()
    city = property_details.get('city', '').lower()
    image_id = f"social_{platform}_{property_id}_{theme}"
    
    # Check cache if enabled
    if use_cache:
        cached_image = get_cached_image(image_id)
        if cached_image:
            logger.info(f"Using cached social media image for {image_id}")
            return cached_image
    
    try:
        # Construct search query based on property details and platform
        search_terms = []
        
        # Add property type
        if property_type in ['apartment', 'condo', 'condominium']:
            search_terms.append('luxury apartment')
        elif property_type in ['townhouse', 'townhome']:
            search_terms.append('modern townhouse')
        else:
            search_terms.append('luxury house')
        
        # Add location if available
        if city:
            search_terms.append(city)
            
        # Add theme terms
        if theme == "professional":
            search_terms.append('professional real estate')
        elif theme == "luxury":
            search_terms.append('luxury property')
        elif theme == "modern":
            search_terms.append('modern architecture')
        else:  # Warm
            search_terms.append('cozy home')
            
        # Combine search terms
        search_query = ' '.join(search_terms)
        
        # Get base image from Unsplash or Pexels
        img = get_image_from_unsplash(search_query)
        
        if img is None:
            img = get_image_from_pexels(search_query)
            
        if img is None:
            # Fallback to simpler query
            img = get_image_from_unsplash("real estate photography")
            
        # If we still don't have an image, create a placeholder
        if img is None:
            # Create a canvas with themed background color
            if theme == "professional":
                background_color = (53, 86, 120)  # Deep blue
            elif theme == "luxury":
                background_color = (32, 32, 32)  # Near black
            elif theme == "modern":
                background_color = (66, 135, 245)  # Modern blue
            else:  # Warm
                background_color = (245, 166, 66)  # Warm orange/gold
                
            img = Image.new('RGB', (width, height), background_color)
        
        # Resize the image to match the platform dimensions
        img = img.resize((width, height), Image.LANCZOS)
        
        # Save to cache
        if use_cache:
            save_to_cache(img, image_id)
        
        return img
    
    except Exception as e:
        logger.error(f"Error generating social media image: {e}")
        # Return a fallback image
        return Image.new('RGB', (width, height), (240, 240, 240))

def generate_email_header_image(
    campaign_type,
    property_details=None,
    theme="professional",
    use_cache=True
):
    """
    Generate an email header image based on campaign type.
    
    Args:
        campaign_type (str): Type of email campaign
        property_details (dict, optional): Property details if applicable
        theme (str): Visual theme for the header
        use_cache (bool): Whether to use cached images if available
        
    Returns:
        PIL.Image: Generated email header image
    """
    # Email headers are typically wide and short
    width, height = 600, 200
    
    # Create a unique identifier for this image request
    campaign_id = campaign_type.replace(" ", "_").lower()
    property_id = property_details.get('property_id', 'unknown') if property_details else 'general'
    image_id = f"email_header_{campaign_id}_{property_id}_{theme}"
    
    # Check cache if enabled
    if use_cache:
        cached_image = get_cached_image(image_id)
        if cached_image:
            logger.info(f"Using cached email header image for {image_id}")
            return cached_image
    
    try:
        # Search query based on campaign type
        search_query = ""
        
        if campaign_type == "New Listing Announcement":
            search_query = "new home real estate"
        elif campaign_type == "Open House Invitation":
            search_query = "open house welcome"
        elif campaign_type == "Price Reduction Alert":
            search_query = "sale discount announcement"
        elif campaign_type == "Market Update Newsletter":
            search_query = "real estate market charts"
        elif campaign_type == "Investment Opportunity":
            search_query = "investment property finance"
        else:  # Default for other campaign types
            search_query = "real estate email header"
            
        # If property details are provided, add property type
        if property_details:
            property_type = property_details.get('property_type', '').lower()
            if property_type:
                if property_type in ['apartment', 'condo']:
                    search_query += " apartment"
                elif property_type in ['townhouse', 'townhome']:
                    search_query += " townhouse"
                elif property_type in ['villa', 'mansion']:
                    search_query += " luxury home"
                else:
                    search_query += " house"
        
        # Get an image from Unsplash
        img = get_image_from_unsplash(search_query)
        
        # If Unsplash fails, try Pexels
        if img is None:
            img = get_image_from_pexels(search_query)
            
        # If both fail, try with a simpler query
        if img is None:
            img = get_image_from_unsplash("real estate")
            
        # If all API calls fail, create a placeholder with color based on campaign type
        if img is None:
            if campaign_type == "New Listing Announcement":
                background_color = (66, 135, 245)  # Blue
            elif campaign_type == "Open House Invitation":
                background_color = (245, 166, 66)  # Orange
            elif campaign_type == "Price Reduction Alert":
                background_color = (245, 66, 66)  # Red
            elif campaign_type == "Market Update Newsletter":
                background_color = (66, 186, 120)  # Green
            else:  # Default
                background_color = (120, 120, 186)  # Purple-ish
                
            img = Image.new('RGB', (width, height), background_color)
        
        # Resize and crop the image to fit the email header dimensions (wide and short)
        img_width, img_height = img.size
        
        # If image is taller than our target ratio, crop it
        if img_width / img_height < width / height:
            # Image is too tall, crop from middle
            crop_height = int(img_width * height / width)
            top = (img_height - crop_height) // 2
            img = img.crop((0, top, img_width, top + crop_height))
        else:
            # Image is too wide, crop from middle
            crop_width = int(img_height * width / height)
            left = (img_width - crop_width) // 2
            img = img.crop((left, 0, left + crop_width, img_height))
            
        # Resize to final dimensions
        img = img.resize((width, height), Image.LANCZOS)
        
        # Save to cache
        if use_cache:
            save_to_cache(img, image_id)
        
        return img
    
    except Exception as e:
        logger.error(f"Error generating email header image: {e}")
        # Return a fallback image
        return Image.new('RGB', (width, height), (240, 240, 240))

def image_to_base64(image, format="PNG"):
    """
    Convert a PIL Image to a base64 string for embedding in HTML.
    
    Args:
        image (PIL.Image): The image to convert
        format (str): The format to save as (PNG, JPEG, etc.)
        
    Returns:
        str: Base64-encoded image string
    """
    buffer = BytesIO()
    image.save(buffer, format=format)
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/{format.lower()};base64,{img_str}"

def generate_image_with_external_api(prompt, api_key=None, width=1024, height=768):
    """
    Generate an image using an external AI image generation API.
    This function would connect to services like DALL-E, Midjourney API, or similar.
    
    Args:
        prompt (str): Text description of the image to generate
        api_key (str): API key for the image generation service
        width (int): Desired image width
        height (int): Desired image height
        
    Returns:
        PIL.Image or None: Generated image or None if generation failed
    """
    # This would be implemented with actual API calls in production
    # For now, we'll create a placeholder and log the prompt that would be sent
    logger.info(f"Would generate image with prompt: {prompt}")
    logger.info("This function requires integration with an external image generation API")
    
    # Create placeholder with dimensions
    return Image.new('RGB', (width, height), (random.randint(180, 255), random.randint(180, 255), random.randint(180, 255)))