"""
Helper functions for common integration scenarios.
This module provides ready-to-use functions for connecting to common external systems.
"""

import os
import json
import pandas as pd
from typing import Dict, List, Any, Optional, Union
import logging
from utils.integration import (
    add_data_source, get_data_source, fetch_data, push_data, 
    remove_data_source, close_all_connections
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_integrations_from_config(config_file: str = 'integrations.json') -> bool:
    """
    Load integration configurations from a JSON file.
    
    Args:
        config_file: Path to the JSON configuration file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if not os.path.exists(config_file):
            logger.warning(f"Integration configuration file not found: {config_file}")
            return False
        
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # Add each data source from the configuration
        for name, source_config in config.get('data_sources', {}).items():
            # Check if this source should be the default
            make_default = source_config.pop('default', False)
            
            # Add the data source
            add_data_source(name, source_config, make_default)
        
        logger.info(f"Loaded integrations from {config_file}")
        return True
        
    except Exception as e:
        logger.error(f"Error loading integrations: {str(e)}")
        return False

def create_mls_integration(
    name: str, 
    mls_provider: str, 
    api_key: str, 
    base_url: str, 
    access_token: Optional[str] = None,
    make_default: bool = False
) -> bool:
    """
    Create an integration with an MLS system.
    
    Args:
        name: Name for this integration
        mls_provider: Provider name (rets, spark, bridge, etc.)
        api_key: API key for authentication
        base_url: Base URL for the MLS API
        access_token: OAuth2 access token (if needed)
        make_default: Whether to make this the default data source
        
    Returns:
        True if successful, False otherwise
    """
    try:
        config = {
            'type': 'mls',
            'mls_provider': mls_provider,
            'base_url': base_url,
            'auth_type': 'api_key',
            'api_key': api_key,
            'api_key_header': 'X-API-Key'
        }
        
        # Add OAuth2 token if provided
        if access_token:
            config['auth_type'] = 'oauth2'
            config['access_token'] = access_token
        
        # Add response configuration
        config['response_format'] = 'json'
        config['data_path'] = 'data.results'
        
        # Add the data source
        add_data_source(name, config, make_default)
        return True
        
    except Exception as e:
        logger.error(f"Error creating MLS integration: {str(e)}")
        return False

def search_properties(
    location: str,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None, 
    bedrooms: Optional[int] = None,
    property_type: Optional[str] = None,
    data_source_name: Optional[str] = None
) -> pd.DataFrame:
    """
    Search for properties using an MLS integration.
    
    Args:
        location: Location to search (city, zip code, etc.)
        min_price: Minimum price
        max_price: Maximum price
        bedrooms: Minimum number of bedrooms
        property_type: Type of property
        data_source_name: Name of the data source to use
        
    Returns:
        DataFrame with property listings
    """
    query = {
        'location': location
    }
    
    # Add optional filters
    if min_price is not None:
        query['min_price'] = min_price
        
    if max_price is not None:
        query['max_price'] = max_price
        
    if bedrooms is not None:
        query['min_bedrooms'] = bedrooms
        
    if property_type is not None:
        query['property_type'] = property_type
    
    try:
        # Fetch the data
        return fetch_data(data_source_name, query)
        
    except Exception as e:
        logger.error(f"Error searching properties: {str(e)}")
        return pd.DataFrame()

def create_crm_integration(
    name: str,
    crm_provider: str,
    base_url: str,
    api_key: Optional[str] = None,
    access_token: Optional[str] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    make_default: bool = False
) -> bool:
    """
    Create an integration with a CRM system.
    
    Args:
        name: Name for this integration
        crm_provider: Provider name (salesforce, hubspot, zoho, etc.)
        base_url: Base URL for the CRM API
        api_key: API key for authentication
        access_token: OAuth2 access token
        username: Username for authentication
        password: Password for authentication
        make_default: Whether to make this the default data source
        
    Returns:
        True if successful, False otherwise
    """
    try:
        config = {
            'type': 'crm',
            'crm_provider': crm_provider,
            'base_url': base_url
        }
        
        # Set authentication method
        if api_key:
            config['auth_type'] = 'api_key'
            config['api_key'] = api_key
            
            # Set the appropriate header name based on the provider
            if crm_provider == 'hubspot':
                config['api_key_header'] = 'hapikey'
            elif crm_provider == 'zoho':
                config['api_key_header'] = 'AUTHTOKEN'
            else:
                config['api_key_header'] = 'X-API-Key'
                
        elif access_token:
            config['auth_type'] = 'oauth2'
            config['access_token'] = access_token
            
        elif username and password:
            config['auth_type'] = 'basic'
            config['username'] = username
            config['password'] = password
            
        else:
            logger.error("No authentication method provided")
            return False
        
        # Add response configuration
        config['response_format'] = 'json'
        
        # Add the data source
        add_data_source(name, config, make_default)
        return True
        
    except Exception as e:
        logger.error(f"Error creating CRM integration: {str(e)}")
        return False

def get_leads(
    status: Optional[str] = None,
    source: Optional[str] = None,
    data_source_name: Optional[str] = None
) -> pd.DataFrame:
    """
    Get leads from a CRM system.
    
    Args:
        status: Lead status filter
        source: Lead source filter
        data_source_name: Name of the data source to use
        
    Returns:
        DataFrame with leads
    """
    query = {
        'entity_type': 'leads',
        'fields': ['id', 'name', 'email', 'phone', 'source', 'status', 'created_at', 'updated_at']
    }
    
    # Add optional filters
    if status:
        query['status'] = status
        
    if source:
        query['source'] = source
    
    try:
        # Fetch the data
        return fetch_data(data_source_name, query)
        
    except Exception as e:
        logger.error(f"Error getting leads: {str(e)}")
        return pd.DataFrame()

def add_leads_to_crm(
    leads_df: pd.DataFrame,
    data_source_name: Optional[str] = None
) -> bool:
    """
    Add leads to a CRM system.
    
    Args:
        leads_df: DataFrame with lead data
        data_source_name: Name of the data source to use
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Set the entity type for pushing leads
        data_source = get_data_source(data_source_name)
        data_source.config.set('entity_type', 'leads')
        
        # Push the data
        return push_data(leads_df, data_source_name)
        
    except Exception as e:
        logger.error(f"Error adding leads to CRM: {str(e)}")
        return False

def create_database_integration(
    name: str,
    driver: str,
    connection_string: str,
    make_default: bool = False
) -> bool:
    """
    Create an integration with an external database.
    
    Args:
        name: Name for this integration
        driver: Database driver (sqlalchemy, psycopg2, sqlite3, mysql)
        connection_string: Database connection string
        make_default: Whether to make this the default data source
        
    Returns:
        True if successful, False otherwise
    """
    try:
        config = {
            'type': 'database',
            'driver': driver,
            'connection_string': connection_string
        }
        
        # Add the data source
        add_data_source(name, config, make_default)
        return True
        
    except Exception as e:
        logger.error(f"Error creating database integration: {str(e)}")
        return False

def query_external_database(
    query: str,
    data_source_name: Optional[str] = None
) -> pd.DataFrame:
    """
    Query an external database.
    
    Args:
        query: SQL query
        data_source_name: Name of the data source to use
        
    Returns:
        DataFrame with query results
    """
    try:
        # Fetch the data
        return fetch_data(data_source_name, query)
        
    except Exception as e:
        logger.error(f"Error querying external database: {str(e)}")
        return pd.DataFrame()

def export_data_to_external_database(
    data: pd.DataFrame,
    table: str,
    data_source_name: Optional[str] = None
) -> bool:
    """
    Export data to an external database.
    
    Args:
        data: DataFrame to export
        table: Target table name
        data_source_name: Name of the data source to use
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Set the target table
        data_source = get_data_source(data_source_name)
        data_source.config.set('table', table)
        
        # Push the data
        return push_data(data, data_source_name)
        
    except Exception as e:
        logger.error(f"Error exporting data to external database: {str(e)}")
        return False

def create_api_integration(
    name: str,
    base_url: str,
    auth_type: str = 'api_key',
    api_key: Optional[str] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    access_token: Optional[str] = None,
    make_default: bool = False
) -> bool:
    """
    Create an integration with a REST API.
    
    Args:
        name: Name for this integration
        base_url: Base URL for the API
        auth_type: Authentication type (api_key, basic, oauth2)
        api_key: API key for authentication
        username: Username for basic authentication
        password: Password for basic authentication
        access_token: OAuth2 access token
        make_default: Whether to make this the default data source
        
    Returns:
        True if successful, False otherwise
    """
    try:
        config = {
            'type': 'rest_api',
            'base_url': base_url,
            'auth_type': auth_type
        }
        
        # Add authentication details based on type
        if auth_type == 'api_key' and api_key:
            config['api_key'] = api_key
            config['api_key_header'] = 'X-API-Key'
            
        elif auth_type == 'basic' and username and password:
            config['username'] = username
            config['password'] = password
            
        elif auth_type == 'oauth2' and access_token:
            config['access_token'] = access_token
            
        else:
            logger.error("Invalid authentication configuration")
            return False
        
        # Add response configuration
        config['response_format'] = 'json'
        
        # Add the data source
        add_data_source(name, config, make_default)
        return True
        
    except Exception as e:
        logger.error(f"Error creating API integration: {str(e)}")
        return False

def call_api_endpoint(
    endpoint: str,
    params: Optional[Dict[str, Any]] = None,
    data_source_name: Optional[str] = None
) -> pd.DataFrame:
    """
    Call an API endpoint.
    
    Args:
        endpoint: API endpoint path
        params: Query parameters
        data_source_name: Name of the data source to use
        
    Returns:
        DataFrame with API response data
    """
    try:
        # Set the endpoint
        data_source = get_data_source(data_source_name)
        data_source.config.set('endpoint', endpoint)
        
        # Fetch the data
        return fetch_data(data_source_name, params)
        
    except Exception as e:
        logger.error(f"Error calling API endpoint: {str(e)}")
        return pd.DataFrame()

def create_file_integration(
    name: str,
    file_path: str,
    make_default: bool = False
) -> bool:
    """
    Create an integration with a CSV file.
    
    Args:
        name: Name for this integration
        file_path: Path to the CSV file
        make_default: Whether to make this the default data source
        
    Returns:
        True if successful, False otherwise
    """
    try:
        config = {
            'type': 'csv_file',
            'file_path': file_path
        }
        
        # Add the data source
        add_data_source(name, config, make_default)
        return True
        
    except Exception as e:
        logger.error(f"Error creating file integration: {str(e)}")
        return False

def import_data_from_csv(
    filters: Optional[Dict[str, Any]] = None,
    data_source_name: Optional[str] = None
) -> pd.DataFrame:
    """
    Import data from a CSV file.
    
    Args:
        filters: Dictionary with filter criteria
        data_source_name: Name of the data source to use
        
    Returns:
        DataFrame with the imported data
    """
    try:
        # Fetch the data
        return fetch_data(data_source_name, filters)
        
    except Exception as e:
        logger.error(f"Error importing data from CSV: {str(e)}")
        return pd.DataFrame()

def export_data_to_csv(
    data: pd.DataFrame,
    data_source_name: Optional[str] = None,
    write_mode: str = 'overwrite'
) -> bool:
    """
    Export data to a CSV file.
    
    Args:
        data: DataFrame to export
        data_source_name: Name of the data source to use
        write_mode: How to handle existing data (append or overwrite)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Set the write mode
        data_source = get_data_source(data_source_name)
        data_source.config.set('write_mode', write_mode)
        
        # Push the data
        return push_data(data, data_source_name)
        
    except Exception as e:
        logger.error(f"Error exporting data to CSV: {str(e)}")
        return False