"""
Web crawler module for gathering lead information from search engines.
This module provides capabilities to search for keywords and extract contact information.
"""
import os
import json
import time
import random
import re
import hashlib
from datetime import datetime, timedelta
import pandas as pd
import requests
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from trafilatura import extract, fetch_url

# Cache directory for search results
CACHE_DIR = os.path.join("cache", "search_results")

def ensure_cache_dir():
    """Ensure the cache directory exists."""
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR, exist_ok=True)


def get_cache_path(query, search_engine):
    """
    Get the cache file path for a search query.
    
    Args:
        query (str): The search query
        search_engine (str): The search engine used
        
    Returns:
        str: The path to the cache file
    """
    ensure_cache_dir()
    query_hash = hashlib.md5(query.encode()).hexdigest()
    return os.path.join(CACHE_DIR, f"{search_engine}_{query_hash}.json")


def check_cache(query, search_engine, max_age_hours=24):
    """
    Check if cached search results exist and are recent enough.
    
    Args:
        query (str): The search query
        search_engine (str): The search engine used
        max_age_hours (int): Maximum age of cache in hours
        
    Returns:
        dict or None: The cached results if available and fresh, None otherwise
    """
    cache_path = get_cache_path(query, search_engine)
    
    if os.path.exists(cache_path):
        # Check if the cache is recent enough
        file_time = datetime.fromtimestamp(os.path.getmtime(cache_path))
        if datetime.now() - file_time < timedelta(hours=max_age_hours):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, UnicodeDecodeError):
                # If the cache is corrupted, ignore it
                pass
    
    return None


def save_to_cache(query, search_engine, results):
    """
    Save search results to the cache.
    
    Args:
        query (str): The search query
        search_engine (str): The search engine used
        results (dict): The search results to cache
        
    Returns:
        bool: True if saved successfully, False otherwise
    """
    cache_path = get_cache_path(query, search_engine)
    
    try:
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


def search_google(query, num_results=10, use_cache=True):
    """
    Search Google for the given query and return the results.
    
    Args:
        query (str): The search query
        num_results (int): Number of results to return
        use_cache (bool): Whether to use cached results if available
        
    Returns:
        list: List of search result dictionaries
    """
    if use_cache:
        cached = check_cache(query, "google")
        if cached:
            return cached
    
    # This function would use Google Custom Search API or similar
    # For demonstration, we'll return placeholder data
    # In a real implementation, you would make API calls to Google Custom Search
    
    results = []
    for i in range(min(num_results, 10)):
        results.append({
            "title": f"Sample Result {i+1} for '{query}'",
            "link": f"https://example.com/result/{i+1}",
            "snippet": f"This is a sample search result for the query '{query}'. " +
                      f"It provides information related to {query} and similar topics.",
        })
    
    if results:
        save_to_cache(query, "google", results)
    
    return results


def search_bing(query, num_results=10, use_cache=True):
    """
    Search Bing for the given query and return the results.
    
    Args:
        query (str): The search query
        num_results (int): Number of results to return
        use_cache (bool): Whether to use cached results if available
        
    Returns:
        list: List of search result dictionaries
    """
    if use_cache:
        cached = check_cache(query, "bing")
        if cached:
            return cached
    
    # This function would use Bing Search API
    # For demonstration, we'll return placeholder data
    # In a real implementation, you would make API calls to Bing Search API
    
    results = []
    for i in range(min(num_results, 10)):
        results.append({
            "title": f"Bing Result {i+1} for '{query}'",
            "link": f"https://example.com/bing-result/{i+1}",
            "snippet": f"This is a sample Bing search result for the query '{query}'. " +
                      f"It contains relevant information about {query}.",
        })
    
    if results:
        save_to_cache(query, "bing", results)
    
    return results


def extract_contact_info(url):
    """
    Extract contact information from a webpage.
    
    Args:
        url (str): URL of the webpage to analyze
        
    Returns:
        dict: Dictionary containing extracted contact information
    """
    # Download the page content
    try:
        downloaded = fetch_url(url)
        if not downloaded:
            return {
                "name": "",
                "email": "",
                "phone": "",
                "company": "",
                "source_url": url
            }
        
        # First extract readable text using trafilatura
        text_content = extract(downloaded)
        
        # Also parse with BeautifulSoup for structured extraction
        soup = BeautifulSoup(downloaded, 'html.parser')
        
        # Extract potential contact information
        # Email extraction
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, downloaded)
        email = emails[0] if emails else ""
        
        # Phone extraction
        phone_pattern = r'\b(?:\+\d{1,3}[-. ]?)?\(?\d{3}\)?[-. ]?\d{3}[-. ]?\d{4}\b'
        phones = re.findall(phone_pattern, downloaded)
        phone = phones[0] if phones else ""
        
        # Company name extraction - look for common patterns
        company = ""
        company_candidates = []
        
        # Look in meta tags
        og_site_name = soup.find('meta', property='og:site_name')
        if og_site_name and og_site_name.get('content'):
            company_candidates.append(og_site_name.get('content'))
        
        # Look for copyright statements
        copyright_pattern = r'©\s*(?:\d{4})?\s*([A-Za-z0-9][A-Za-z0-9\s&,.]+)'
        copyright_matches = re.findall(copyright_pattern, downloaded)
        if copyright_matches:
            company_candidates.extend(copyright_matches)
        
        # Check the title
        if soup.title:
            title_parts = soup.title.string.split('|')
            if len(title_parts) > 1:
                company_candidates.append(title_parts[-1].strip())
        
        # Use the most common company name found
        if company_candidates:
            company = max(set(company_candidates), key=company_candidates.count)
        
        # Name extraction - this is challenging and would require more sophisticated NLP
        # For demonstration, we'll look for common patterns that might indicate a person's name
        name = ""
        name_patterns = [
            r'(?:Contact|About)(?:\s+Us)?(?:\s*[-:])?\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'(?:Mr\.|Ms\.|Mrs\.|Dr\.)\s+([A-Z][a-z]+\s+[A-Z][a-z]+)'
        ]
        
        for pattern in name_patterns:
            name_matches = re.findall(pattern, text_content or downloaded)
            if name_matches:
                name = name_matches[0]
                break
        
        return {
            "name": name,
            "email": email,
            "phone": phone,
            "company": company,
            "source_url": url
        }
    
    except Exception as e:
        print(f"Error extracting contact info from {url}: {str(e)}")
        return {
            "name": "",
            "email": "",
            "phone": "",
            "company": "",
            "source_url": url,
            "error": str(e)
        }


def crawl_search_results(query, search_engines=None, num_results=10, use_cache=True):
    """
    Search multiple engines and crawl the results to extract contact information.
    
    Args:
        query (str): The search query
        search_engines (list): List of search engines to use
        num_results (int): Number of results to crawl per engine
        use_cache (bool): Whether to use cached results if available
        
    Returns:
        list: List of dictionaries containing contact information
    """
    if search_engines is None:
        search_engines = ["google", "bing"]
    
    all_results = []
    
    for engine in search_engines:
        if engine == "google":
            results = search_google(query, num_results, use_cache)
        elif engine == "bing":
            results = search_bing(query, num_results, use_cache)
        else:
            continue
        
        all_results.extend(results)
    
    # Deduplicate results by URL
    unique_urls = set()
    unique_results = []
    
    for result in all_results:
        if result["link"] not in unique_urls:
            unique_urls.add(result["link"])
            unique_results.append(result)
    
    # Extract contact information from each unique URL
    contact_info = []
    
    for result in unique_results[:num_results]:
        # Add a delay to avoid overloading servers
        time.sleep(random.uniform(1, 3))
        
        url = result["link"]
        contact_data = extract_contact_info(url)
        
        # Only include if we found at least one piece of contact information
        if contact_data["name"] or contact_data["email"] or contact_data["phone"] or contact_data["company"]:
            contact_data["query"] = query
            contact_data["title"] = result.get("title", "")
            contact_data["snippet"] = result.get("snippet", "")
            contact_info.append(contact_data)
    
    return contact_info


def calculate_lead_score(contact_info):
    """
    Calculate a lead score based on available contact information.
    
    Args:
        contact_info (dict): Dictionary containing contact information
        
    Returns:
        int: Lead score from 0-100
    """
    score = 0
    
    # Base points for having basic information
    if contact_info.get("name"):
        score += 15
    if contact_info.get("email"):
        score += 25
    if contact_info.get("phone"):
        score += 20
    if contact_info.get("company"):
        score += 15
    
    # Bonus points for email from a company domain (not gmail, hotmail, etc.)
    email = contact_info.get("email", "")
    if email and "@" in email:
        domain = email.split("@")[1].lower()
        if not any(free_domain in domain for free_domain in ["gmail", "yahoo", "hotmail", "outlook", "aol", "protonmail"]):
            score += 10
    
    # Bonus for complete information
    if all([contact_info.get("name"), contact_info.get("email"), 
            contact_info.get("phone"), contact_info.get("company")]):
        score += 15
    
    return min(score, 100)  # Cap at 100


def save_lead_campaign(campaign_name, keywords, search_engines, num_results=20):
    """
    Save a lead generation campaign configuration.
    
    Args:
        campaign_name (str): Name of the campaign
        keywords (list): List of keywords to search for
        search_engines (list): List of search engines to use
        num_results (int): Number of results to crawl per keyword
        
    Returns:
        str: ID of the saved campaign
    """
    ensure_cache_dir()
    
    # Generate a unique ID for the campaign
    campaign_id = hashlib.md5(f"{campaign_name}_{datetime.now().isoformat()}".encode()).hexdigest()[:10]
    
    campaign_data = {
        "id": campaign_id,
        "name": campaign_name,
        "keywords": keywords,
        "search_engines": search_engines,
        "num_results": num_results,
        "created_at": datetime.now().isoformat(),
        "last_run": None,
        "status": "created"
    }
    
    campaigns_file = os.path.join(CACHE_DIR, "lead_campaigns.json")
    
    # Load existing campaigns
    campaigns = []
    if os.path.exists(campaigns_file):
        try:
            with open(campaigns_file, 'r', encoding='utf-8') as f:
                campaigns = json.load(f)
        except (json.JSONDecodeError, UnicodeDecodeError):
            campaigns = []
    
    # Add the new campaign
    campaigns.append(campaign_data)
    
    # Save the updated list
    with open(campaigns_file, 'w', encoding='utf-8') as f:
        json.dump(campaigns, f, ensure_ascii=False, indent=2)
    
    return campaign_id


def get_lead_campaigns():
    """
    Get all saved lead generation campaigns.
    
    Returns:
        list: List of campaign dictionaries
    """
    ensure_cache_dir()
    campaigns_file = os.path.join(CACHE_DIR, "lead_campaigns.json")
    
    if os.path.exists(campaigns_file):
        try:
            with open(campaigns_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return []
    
    return []


def run_lead_campaign(campaign_id):
    """
    Run a saved lead generation campaign.
    
    Args:
        campaign_id (str): ID of the campaign to run
        
    Returns:
        list: List of extracted contacts
    """
    campaigns = get_lead_campaigns()
    campaign = next((c for c in campaigns if c["id"] == campaign_id), None)
    
    if not campaign:
        return []
    
    all_contacts = []
    
    for keyword in campaign["keywords"]:
        contacts = crawl_search_results(
            keyword, 
            search_engines=campaign["search_engines"],
            num_results=campaign["num_results"]
        )
        
        # Add lead scores
        for contact in contacts:
            contact["lead_score"] = calculate_lead_score(contact)
            contact["campaign_id"] = campaign_id
            contact["keyword"] = keyword
        
        all_contacts.extend(contacts)
    
    # Update campaign status
    campaign["last_run"] = datetime.now().isoformat()
    campaign["status"] = "completed"
    
    # Save the updated campaign
    campaigns_file = os.path.join(CACHE_DIR, "lead_campaigns.json")
    with open(campaigns_file, 'w', encoding='utf-8') as f:
        json.dump(campaigns, f, ensure_ascii=False, indent=2)
    
    # Save the contacts
    contacts_file = os.path.join(CACHE_DIR, f"campaign_{campaign_id}_contacts.json")
    with open(contacts_file, 'w', encoding='utf-8') as f:
        json.dump(all_contacts, f, ensure_ascii=False, indent=2)
    
    return all_contacts


def get_campaign_contacts(campaign_id):
    """
    Get contacts extracted from a specific campaign.
    
    Args:
        campaign_id (str): ID of the campaign
        
    Returns:
        list: List of contact dictionaries
    """
    contacts_file = os.path.join(CACHE_DIR, f"campaign_{campaign_id}_contacts.json")
    
    if os.path.exists(contacts_file):
        try:
            with open(contacts_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return []
    
    return []


def export_contacts_to_dataframe(contacts):
    """
    Convert contact dictionaries to a pandas DataFrame.
    
    Args:
        contacts (list): List of contact dictionaries
        
    Returns:
        DataFrame: DataFrame containing contact information
    """
    if not contacts:
        return pd.DataFrame()
    
    return pd.DataFrame(contacts)


def export_contacts_to_csv(contacts, file_path):
    """
    Export contacts to a CSV file.
    
    Args:
        contacts (list): List of contact dictionaries
        file_path (str): Path to save the CSV file
        
    Returns:
        bool: True if successful, False otherwise
    """
    df = export_contacts_to_dataframe(contacts)
    
    if df.empty:
        return False
    
    try:
        df.to_csv(file_path, index=False)
        return True
    except Exception:
        return False


def import_contacts_to_database(contacts, source="web_crawler"):
    """
    Import contacts to the database.
    
    Args:
        contacts (list): List of contact dictionaries
        source (str): Source of the contacts
        
    Returns:
        int: Number of contacts successfully imported
    """
    from utils.database import add_lead
    
    success_count = 0
    
    for contact in contacts:
        lead_data = {
            "name": contact.get("name", ""),
            "email": contact.get("email", ""),
            "phone": contact.get("phone", ""),
            "source": source,
            "lead_score": contact.get("lead_score", 0),
            "property_interest": contact.get("keyword", "unknown"),
            "price_range": "",
            "urgency": "medium",
            "status": "new"
        }
        
        if contact.get("company"):
            lead_data["notes"] = f"Company: {contact['company']}\nSource URL: {contact.get('source_url', '')}"
        
        try:
            add_lead(lead_data)
            success_count += 1
        except Exception as e:
            print(f"Error importing lead: {str(e)}")
    
    return success_count