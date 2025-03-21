"""
Example script demonstrating how to use the integrations system.
This script shows how to:
1. Set up a connection to an external system
2. Import data from that system
3. Transform the data
4. Export it to another system
"""

import pandas as pd
import os
import sys
import json
from typing import Dict, Any

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the integration module
from utils.integration import (
    add_data_source, get_data_source, fetch_data, push_data, 
    remove_data_source, close_all_connections
)
from utils.integration_helpers import (
    create_mls_integration, create_crm_integration,
    create_database_integration, create_api_integration,
    create_file_integration, search_properties, get_leads
)

def example_mls_integration():
    """Example MLS integration to import property listings."""
    print("Setting up MLS integration...")
    
    # Set up MLS integration
    create_mls_integration(
        name="example_mls",
        mls_provider="rets",
        api_key="your_api_key_here",
        base_url="https://api.example-mls.com/v1",
        make_default=True
    )
    
    # Search for properties
    print("Searching for properties...")
    properties = search_properties(
        location="San Francisco, CA",
        min_price=500000,
        max_price=1000000,
        bedrooms=2,
        property_type="Single Family",
        data_source_name="example_mls"
    )
    
    print(f"Found {len(properties)} properties")
    
    # Transform the data (add calculations, cleanup, etc.)
    if not properties.empty:
        # Example transformation: Calculate price per square foot
        properties['price_per_sqft'] = properties['price'] / properties['sqft']
        
        # Example transformation: Standardize property types
        def standardize_property_type(prop_type):
            prop_type = str(prop_type).lower()
            if 'single' in prop_type:
                return 'Single Family'
            elif 'condo' in prop_type or 'apartment' in prop_type:
                return 'Condo/Apartment'
            elif 'town' in prop_type:
                return 'Townhouse'
            else:
                return 'Other'
        
        properties['property_type'] = properties['property_type'].apply(standardize_property_type)
        
        print("Data transformation complete")
    
    # Clean up
    remove_data_source("example_mls")
    
    return properties

def example_database_export(properties_df):
    """Example database export of property data."""
    print("Setting up database integration...")
    
    # Set up database integration
    create_database_integration(
        name="example_db",
        driver="sqlalchemy",
        connection_string="postgresql://username:password@localhost:5432/realestate"
    )
    
    # Export properties to database
    print("Exporting properties to database...")
    success = False
    
    if not properties_df.empty:
        # Get the data source
        data_source = get_data_source("example_db")
        
        # Set the target table
        data_source.config.set('table', 'imported_properties')
        
        # Export the data
        success = push_data(properties_df, "example_db")
    
    if success:
        print("Successfully exported properties to database")
    else:
        print("Failed to export properties to database")
    
    # Clean up
    remove_data_source("example_db")

def example_crm_integration():
    """Example CRM integration to fetch leads."""
    print("Setting up CRM integration...")
    
    # Set up CRM integration
    create_crm_integration(
        name="example_crm",
        crm_provider="hubspot",
        base_url="https://api.hubspot.com",
        api_key="your_api_key_here"
    )
    
    # Get leads from CRM
    print("Fetching leads from CRM...")
    leads = get_leads(
        status="open",
        source="website",
        data_source_name="example_crm"
    )
    
    print(f"Found {len(leads)} leads")
    
    # Process the leads
    if not leads.empty:
        # Example processing: Calculate lead age in days
        import datetime
        today = datetime.datetime.now()
        
        def calculate_lead_age(created_date):
            if pd.isna(created_date):
                return None
            
            if isinstance(created_date, str):
                try:
                    created_date = datetime.datetime.strptime(created_date, '%Y-%m-%dT%H:%M:%S.%fZ')
                except:
                    try:
                        created_date = datetime.datetime.strptime(created_date, '%Y-%m-%d')
                    except:
                        return None
            
            delta = today - created_date
            return delta.days
        
        if 'created_at' in leads.columns:
            leads['age_days'] = leads['created_at'].apply(calculate_lead_age)
            
        # Example processing: Categorize leads by priority
        def assign_priority(lead):
            if pd.isna(lead.get('age_days')):
                return 'Medium'
            
            # Newer leads get higher priority
            if lead.get('age_days', 0) <= 3:
                return 'High'
            elif lead.get('age_days', 0) <= 14:
                return 'Medium'
            else:
                return 'Low'
        
        leads['priority'] = leads.apply(assign_priority, axis=1)
        
        print("Lead processing complete")
    
    # Clean up
    remove_data_source("example_crm")
    
    return leads

def example_file_integration(data_df, filename="exported_data.csv"):
    """Example file integration to export data to CSV."""
    print("Setting up file integration...")
    
    # Set up file integration
    create_file_integration(
        name="example_file",
        file_path=filename
    )
    
    # Export data to CSV
    print(f"Exporting data to {filename}...")
    success = False
    
    if not data_df.empty:
        # Get the data source
        data_source = get_data_source("example_file")
        
        # Set the write mode
        data_source.config.set('write_mode', 'overwrite')
        
        # Export the data
        success = push_data(data_df, "example_file")
    
    if success:
        print(f"Successfully exported data to {filename}")
    else:
        print(f"Failed to export data to {filename}")
    
    # Clean up
    remove_data_source("example_file")

def example_api_integration():
    """Example API integration to fetch market data."""
    print("Setting up API integration...")
    
    # Set up API integration
    create_api_integration(
        name="example_api",
        base_url="https://api.example.com",
        auth_type="api_key",
        api_key="your_api_key_here"
    )
    
    # Set the endpoint and parameters
    data_source = get_data_source("example_api")
    data_source.config.set('endpoint', '/v1/market/stats')
    
    # Fetch market data
    print("Fetching market statistics...")
    params = {
        'location': 'San Francisco',
        'period': 'monthly',
        'months': 6
    }
    
    market_data = fetch_data("example_api", params)
    
    print(f"Fetched market data with {len(market_data)} records")
    
    # Clean up
    remove_data_source("example_api")
    
    return market_data

def run_all_examples():
    """Run all integration examples."""
    try:
        # Example 1: Import properties from MLS
        properties = example_mls_integration()
        
        # Example 2: Export properties to database
        if not isinstance(properties, pd.DataFrame) or properties.empty:
            # Create sample data for demo purposes
            properties = pd.DataFrame({
                'property_id': [1001, 1002, 1003],
                'address': ['123 Main St', '456 Oak Ave', '789 Pine Blvd'],
                'city': ['San Francisco', 'San Francisco', 'San Francisco'],
                'state': ['CA', 'CA', 'CA'],
                'price': [750000, 850000, 950000],
                'sqft': [1500, 1800, 2200],
                'bedrooms': [2, 3, 4],
                'bathrooms': [2, 2.5, 3],
                'property_type': ['Single Family', 'Condo/Apartment', 'Townhouse'],
                'year_built': [1985, 2005, 2015]
            })
        
        example_database_export(properties)
        
        # Example 3: Import leads from CRM
        leads = example_crm_integration()
        
        # Example 4: Export combined data to CSV
        if not isinstance(leads, pd.DataFrame) or leads.empty:
            # Create sample data for demo purposes
            leads = pd.DataFrame({
                'lead_id': [2001, 2002, 2003],
                'name': ['John Smith', 'Jane Doe', 'Bob Johnson'],
                'email': ['john@example.com', 'jane@example.com', 'bob@example.com'],
                'phone': ['555-123-4567', '555-234-5678', '555-345-6789'],
                'source': ['website', 'referral', 'website'],
                'status': ['open', 'contacted', 'qualified'],
                'created_at': ['2023-01-15', '2023-02-20', '2023-03-10']
            })
        
        # Export data to CSV
        example_file_integration(leads, "exported_leads.csv")
        
        # Example 5: Fetch market data from API
        market_data = example_api_integration()
        
        print("\nAll examples completed successfully!")
        
    except Exception as e:
        print(f"Error in examples: {str(e)}")
    finally:
        # Clean up all connections
        close_all_connections()

if __name__ == "__main__":
    run_all_examples()