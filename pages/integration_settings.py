"""
Integration settings page for configuring connections to external systems.
"""

import os
import streamlit as st
import pandas as pd
import json
import logging
from typing import Dict, Any
import time

# Import integration utilities
from utils.integration import (
    add_data_source, get_data_source, fetch_data, push_data, 
    remove_data_source, close_all_connections
)
from utils.integration_helpers import (
    create_mls_integration, create_crm_integration,
    create_database_integration, create_api_integration,
    create_file_integration, search_properties, get_leads,
    load_integrations_from_config
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
INTEGRATION_CONFIG_FILE = "integrations.json"

def save_integrations_config(integrations: Dict[str, Any]) -> bool:
    """Save integrations configuration to file."""
    try:
        with open(INTEGRATION_CONFIG_FILE, "w") as f:
            json.dump(integrations, f, indent=4)
        return True
    except Exception as e:
        logger.error(f"Error saving integrations config: {str(e)}")
        return False

def load_integrations_config() -> Dict[str, Any]:
    """Load integrations configuration from file."""
    try:
        if os.path.exists(INTEGRATION_CONFIG_FILE):
            with open(INTEGRATION_CONFIG_FILE, "r") as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.error(f"Error loading integrations config: {str(e)}")
        return {}

def show_new_integration_form():
    """Show form for adding a new integration."""
    st.subheader("Add New Integration")
    
    # Initialization
    if "integration_tab" not in st.session_state:
        st.session_state.integration_tab = "api"
    
    if "integration_data" not in st.session_state:
        st.session_state.integration_data = {
            "name": "",
            "type": "api",
            "api": {
                "base_url": "",
                "auth_type": "api_key",
                "api_key": "",
                "username": "",
                "password": "",
                "access_token": "",
            },
            "database": {
                "driver": "sqlalchemy",
                "connection_string": "",
            },
            "file": {
                "file_path": "",
            },
            "mls": {
                "mls_provider": "rets",
                "base_url": "",
                "api_key": "",
                "use_oauth": False,
                "access_token": "",
            },
            "crm": {
                "crm_provider": "salesforce",
                "base_url": "",
                "auth_type": "api_key",
                "api_key": "",
                "username": "",
                "password": "",
                "access_token": "",
            }
        }
    
    # Integration type selection
    integration_type = st.selectbox(
        "Integration Type",
        options=["REST API", "Database", "File", "MLS System", "CRM System"],
        key="integration_type_select"
    )
    
    # Map selection to internal type
    type_map = {
        "REST API": "api",
        "Database": "database",
        "File": "file",
        "MLS System": "mls",
        "CRM System": "crm"
    }
    st.session_state.integration_data["type"] = type_map[integration_type]
    
    # Integration name (must be unique)
    integration_name = st.text_input(
        "Integration Name (must be unique)",
        value=st.session_state.integration_data["name"],
        key="integration_name"
    )
    st.session_state.integration_data["name"] = integration_name
    
    # Form fields based on integration type
    with st.form(key="integration_form"):
        if st.session_state.integration_data["type"] == "api":
            base_url = st.text_input(
                "API Base URL", 
                value=st.session_state.integration_data["api"]["base_url"],
                help="The base URL for the API, e.g., https://api.example.com"
            )
            
            auth_type = st.selectbox(
                "Authentication Type",
                options=["API Key", "Basic Auth", "OAuth2"],
                index=0,
                key="api_auth_type"
            )
            
            if auth_type == "API Key":
                api_key = st.text_input(
                    "API Key", 
                    type="password",
                    value=st.session_state.integration_data["api"]["api_key"]
                )
            elif auth_type == "Basic Auth":
                username = st.text_input(
                    "Username",
                    value=st.session_state.integration_data["api"]["username"]
                )
                password = st.text_input(
                    "Password", 
                    type="password",
                    value=st.session_state.integration_data["api"]["password"]
                )
            elif auth_type == "OAuth2":
                access_token = st.text_input(
                    "OAuth2 Access Token", 
                    type="password",
                    value=st.session_state.integration_data["api"]["access_token"]
                )
                
        elif st.session_state.integration_data["type"] == "database":
            connection_string = st.text_input(
                "Database Connection String", 
                value=st.session_state.integration_data["database"]["connection_string"],
                help="Example: postgresql://username:password@localhost:5432/dbname"
            )
            
            driver = st.selectbox(
                "Database Driver",
                options=["sqlalchemy", "psycopg2", "sqlite3", "mysql"],
                index=0,
                key="db_driver"
            )
            
        elif st.session_state.integration_data["type"] == "file":
            file_path = st.text_input(
                "File Path", 
                value=st.session_state.integration_data["file"]["file_path"],
                help="Absolute path to the CSV file"
            )
            
        elif st.session_state.integration_data["type"] == "mls":
            mls_provider = st.selectbox(
                "MLS Provider",
                options=["RETS", "Spark API", "Bridge API", "MLS Grid", "Other"],
                index=0,
                key="mls_provider"
            )
            
            base_url = st.text_input(
                "MLS API Base URL", 
                value=st.session_state.integration_data["mls"]["base_url"]
            )
            
            api_key = st.text_input(
                "API Key", 
                type="password",
                value=st.session_state.integration_data["mls"]["api_key"]
            )
            
            use_oauth = st.checkbox(
                "Use OAuth Authentication",
                value=st.session_state.integration_data["mls"]["use_oauth"]
            )
            
            if use_oauth:
                access_token = st.text_input(
                    "OAuth Access Token", 
                    type="password",
                    value=st.session_state.integration_data["mls"]["access_token"]
                )
            
        elif st.session_state.integration_data["type"] == "crm":
            crm_provider = st.selectbox(
                "CRM Provider",
                options=["Salesforce", "HubSpot", "Zoho", "Other"],
                index=0,
                key="crm_provider"
            )
            
            base_url = st.text_input(
                "CRM API Base URL", 
                value=st.session_state.integration_data["crm"]["base_url"]
            )
            
            auth_type = st.selectbox(
                "Authentication Type",
                options=["API Key", "OAuth2", "Basic Auth"],
                index=0,
                key="crm_auth_type"
            )
            
            if auth_type == "API Key":
                api_key = st.text_input(
                    "API Key", 
                    type="password",
                    value=st.session_state.integration_data["crm"]["api_key"]
                )
            elif auth_type == "OAuth2":
                access_token = st.text_input(
                    "OAuth2 Access Token", 
                    type="password",
                    value=st.session_state.integration_data["crm"]["access_token"]
                )
            elif auth_type == "Basic Auth":
                username = st.text_input(
                    "Username",
                    value=st.session_state.integration_data["crm"]["username"]
                )
                password = st.text_input(
                    "Password", 
                    type="password",
                    value=st.session_state.integration_data["crm"]["password"]
                )
                
        # Make default integration checkbox
        make_default = st.checkbox(
            "Make this the default data source for its type",
            value=False,
            key="make_default"
        )
        
        # Test connection & save buttons
        col1, col2 = st.columns(2)
        with col1:
            test_button = st.form_submit_button("Test Connection")
        with col2:
            save_button = st.form_submit_button("Save Integration")
        
        # Handle button actions
        if test_button:
            with st.spinner("Testing connection..."):
                # Capture form data to session state before testing
                if st.session_state.integration_data["type"] == "api":
                    st.session_state.integration_data["api"]["base_url"] = base_url
                    if auth_type == "API Key":
                        st.session_state.integration_data["api"]["auth_type"] = "api_key"
                        st.session_state.integration_data["api"]["api_key"] = api_key
                    elif auth_type == "Basic Auth":
                        st.session_state.integration_data["api"]["auth_type"] = "basic"
                        st.session_state.integration_data["api"]["username"] = username
                        st.session_state.integration_data["api"]["password"] = password
                    elif auth_type == "OAuth2":
                        st.session_state.integration_data["api"]["auth_type"] = "oauth2"
                        st.session_state.integration_data["api"]["access_token"] = access_token
                
                elif st.session_state.integration_data["type"] == "database":
                    st.session_state.integration_data["database"]["connection_string"] = connection_string
                    st.session_state.integration_data["database"]["driver"] = driver
                
                elif st.session_state.integration_data["type"] == "file":
                    st.session_state.integration_data["file"]["file_path"] = file_path
                
                elif st.session_state.integration_data["type"] == "mls":
                    st.session_state.integration_data["mls"]["mls_provider"] = mls_provider.lower()
                    st.session_state.integration_data["mls"]["base_url"] = base_url
                    st.session_state.integration_data["mls"]["api_key"] = api_key
                    st.session_state.integration_data["mls"]["use_oauth"] = use_oauth
                    if use_oauth:
                        st.session_state.integration_data["mls"]["access_token"] = access_token
                
                elif st.session_state.integration_data["type"] == "crm":
                    st.session_state.integration_data["crm"]["crm_provider"] = crm_provider.lower()
                    st.session_state.integration_data["crm"]["base_url"] = base_url
                    st.session_state.integration_data["crm"]["auth_type"] = auth_type.lower().replace(" ", "_")
                    
                    if auth_type == "API Key":
                        st.session_state.integration_data["crm"]["api_key"] = api_key
                    elif auth_type == "OAuth2":
                        st.session_state.integration_data["crm"]["access_token"] = access_token
                    elif auth_type == "Basic Auth":
                        st.session_state.integration_data["crm"]["username"] = username
                        st.session_state.integration_data["crm"]["password"] = password
                
                # Test the integration
                success = test_integration(
                    st.session_state.integration_data["name"],
                    st.session_state.integration_data
                )
                
                if success:
                    st.success("Connection successful! You can now save this integration.")
                else:
                    st.error("Failed to connect. Please check your settings and try again.")
        
        if save_button:
            if not integration_name:
                st.error("Please provide a name for the integration.")
            else:
                # Capture form data to session state before saving
                if st.session_state.integration_data["type"] == "api":
                    st.session_state.integration_data["api"]["base_url"] = base_url
                    if auth_type == "API Key":
                        st.session_state.integration_data["api"]["auth_type"] = "api_key"
                        st.session_state.integration_data["api"]["api_key"] = api_key
                    elif auth_type == "Basic Auth":
                        st.session_state.integration_data["api"]["auth_type"] = "basic"
                        st.session_state.integration_data["api"]["username"] = username
                        st.session_state.integration_data["api"]["password"] = password
                    elif auth_type == "OAuth2":
                        st.session_state.integration_data["api"]["auth_type"] = "oauth2"
                        st.session_state.integration_data["api"]["access_token"] = access_token
                
                elif st.session_state.integration_data["type"] == "database":
                    st.session_state.integration_data["database"]["connection_string"] = connection_string
                    st.session_state.integration_data["database"]["driver"] = driver
                
                elif st.session_state.integration_data["type"] == "file":
                    st.session_state.integration_data["file"]["file_path"] = file_path
                
                elif st.session_state.integration_data["type"] == "mls":
                    st.session_state.integration_data["mls"]["mls_provider"] = mls_provider.lower()
                    st.session_state.integration_data["mls"]["base_url"] = base_url
                    st.session_state.integration_data["mls"]["api_key"] = api_key
                    st.session_state.integration_data["mls"]["use_oauth"] = use_oauth
                    if use_oauth:
                        st.session_state.integration_data["mls"]["access_token"] = access_token
                
                elif st.session_state.integration_data["type"] == "crm":
                    st.session_state.integration_data["crm"]["crm_provider"] = crm_provider.lower()
                    st.session_state.integration_data["crm"]["base_url"] = base_url
                    st.session_state.integration_data["crm"]["auth_type"] = auth_type.lower().replace(" ", "_")
                    
                    if auth_type == "API Key":
                        st.session_state.integration_data["crm"]["api_key"] = api_key
                    elif auth_type == "OAuth2":
                        st.session_state.integration_data["crm"]["access_token"] = access_token
                    elif auth_type == "Basic Auth":
                        st.session_state.integration_data["crm"]["username"] = username
                        st.session_state.integration_data["crm"]["password"] = password
                
                # Save the integration
                integrations = load_integrations_config()
                
                # Check if the integration name already exists
                if integration_name in integrations:
                    if st.warning(f"Integration '{integration_name}' already exists. Overwrite?"):
                        # User confirmed overwrite
                        pass
                    else:
                        st.stop()
                
                # Add the integration to the configuration
                integrations[integration_name] = {
                    "type": st.session_state.integration_data["type"],
                    "config": st.session_state.integration_data[st.session_state.integration_data["type"]],
                    "default": make_default
                }
                
                # Save the configuration
                if save_integrations_config(integrations):
                    st.success(f"Integration '{integration_name}' saved successfully.")
                    
                    # Create data source in integration system
                    try:
                        # Create the actual integration in the system
                        if st.session_state.integration_data["type"] == "api":
                            config = st.session_state.integration_data["api"]
                            create_api_integration(
                                name=integration_name,
                                base_url=config["base_url"],
                                auth_type=config["auth_type"],
                                api_key=config.get("api_key"),
                                username=config.get("username"),
                                password=config.get("password"),
                                access_token=config.get("access_token"),
                                make_default=make_default
                            )
                        elif st.session_state.integration_data["type"] == "database":
                            config = st.session_state.integration_data["database"]
                            create_database_integration(
                                name=integration_name,
                                driver=config["driver"],
                                connection_string=config["connection_string"],
                                make_default=make_default
                            )
                        elif st.session_state.integration_data["type"] == "file":
                            config = st.session_state.integration_data["file"]
                            create_file_integration(
                                name=integration_name,
                                file_path=config["file_path"],
                                make_default=make_default
                            )
                        elif st.session_state.integration_data["type"] == "mls":
                            config = st.session_state.integration_data["mls"]
                            create_mls_integration(
                                name=integration_name,
                                mls_provider=config["mls_provider"],
                                api_key=config["api_key"],
                                base_url=config["base_url"],
                                access_token=config.get("access_token") if config.get("use_oauth") else None,
                                make_default=make_default
                            )
                        elif st.session_state.integration_data["type"] == "crm":
                            config = st.session_state.integration_data["crm"]
                            auth_type = config["auth_type"]
                            
                            if auth_type == "api_key":
                                create_crm_integration(
                                    name=integration_name,
                                    crm_provider=config["crm_provider"],
                                    base_url=config["base_url"],
                                    api_key=config["api_key"],
                                    make_default=make_default
                                )
                            elif auth_type == "oauth2":
                                create_crm_integration(
                                    name=integration_name,
                                    crm_provider=config["crm_provider"],
                                    base_url=config["base_url"],
                                    access_token=config["access_token"],
                                    make_default=make_default
                                )
                            elif auth_type == "basic_auth":
                                create_crm_integration(
                                    name=integration_name,
                                    crm_provider=config["crm_provider"],
                                    base_url=config["base_url"],
                                    username=config["username"],
                                    password=config["password"],
                                    make_default=make_default
                                )
                        
                        # Clear the form
                        st.session_state.integration_data = {
                            "name": "",
                            "type": "api",
                            "api": {
                                "base_url": "",
                                "auth_type": "api_key",
                                "api_key": "",
                                "username": "",
                                "password": "",
                                "access_token": "",
                            },
                            "database": {
                                "driver": "sqlalchemy",
                                "connection_string": "",
                            },
                            "file": {
                                "file_path": "",
                            },
                            "mls": {
                                "mls_provider": "rets",
                                "base_url": "",
                                "api_key": "",
                                "use_oauth": False,
                                "access_token": "",
                            },
                            "crm": {
                                "crm_provider": "salesforce",
                                "base_url": "",
                                "auth_type": "api_key",
                                "api_key": "",
                                "username": "",
                                "password": "",
                                "access_token": "",
                            }
                        }
                        
                        # Force page refresh to update the list of integrations
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error creating integration: {str(e)}")
                else:
                    st.error("Failed to save integration configuration.")

def test_integration(name: str, config: Dict[str, Any]) -> bool:
    """Test an integration connection."""
    try:
        # For this demo, we'll simulate a connection test
        # In a real implementation, we would create the data source
        # and try to fetch some test data
        
        # Simulate connection delay
        with st.spinner(f"Testing connection to {name}..."):
            time.sleep(2)  # Simulate a 2-second connection test
        
        # For demo purposes, connections always succeed except for specific test cases
        if "fail" in name.lower():
            return False
        return True
    except Exception as e:
        logger.error(f"Error testing integration {name}: {str(e)}")
        return False

def show_integrations():
    """Show existing integrations."""
    st.subheader("Configured Integrations")
    
    integrations = load_integrations_config()
    
    if not integrations:
        st.info("No integrations configured yet. Use the form above to add a new integration.")
        return
    
    # Display integrations in tabs
    tabs = st.tabs(list(integrations.keys()))
    
    for i, (name, config) in enumerate(integrations.items()):
        with tabs[i]:
            st.json(config)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("Test Connection", key=f"test_{name}"):
                    with st.spinner(f"Testing connection to {name}..."):
                        success = test_integration(name, config)
                        
                        if success:
                            st.success("Connection successful!")
                        else:
                            st.error("Failed to connect. Please check your settings.")
            
            with col2:
                if st.button("Edit", key=f"edit_{name}"):
                    # Load this integration into the form for editing
                    st.session_state.integration_data = {
                        "name": name,
                        "type": config["type"],
                        "api": config["config"] if config["type"] == "api" else {
                            "base_url": "",
                            "auth_type": "api_key",
                            "api_key": "",
                            "username": "",
                            "password": "",
                            "access_token": "",
                        },
                        "database": config["config"] if config["type"] == "database" else {
                            "driver": "sqlalchemy",
                            "connection_string": "",
                        },
                        "file": config["config"] if config["type"] == "file" else {
                            "file_path": "",
                        },
                        "mls": config["config"] if config["type"] == "mls" else {
                            "mls_provider": "rets",
                            "base_url": "",
                            "api_key": "",
                            "use_oauth": False,
                            "access_token": "",
                        },
                        "crm": config["config"] if config["type"] == "crm" else {
                            "crm_provider": "salesforce",
                            "base_url": "",
                            "auth_type": "api_key",
                            "api_key": "",
                            "username": "",
                            "password": "",
                            "access_token": "",
                        }
                    }
                    
                    # Scroll to the form
                    js = f"""
                    <script>
                    document.querySelector('[data-testid="stVerticalBlock"]').scrollTo({{
                        top: 0,
                        behavior: 'smooth'
                    }});
                    </script>
                    """
                    st.components.v1.html(js)
            
            with col3:
                if st.button("Delete", key=f"delete_{name}"):
                    if st.session_state.get("confirm_delete") == name:
                        # User confirmed delete
                        integrations.pop(name)
                        save_integrations_config(integrations)
                        st.success(f"Integration '{name}' deleted.")
                        st.rerun()
                    else:
                        # Ask for confirmation
                        st.session_state.confirm_delete = name
                        st.warning(f"Are you sure you want to delete '{name}'? Click Delete again to confirm.")

def show_import_export():
    """Show import/export options for integrations configuration."""
    st.subheader("Import/Export Integrations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("Export Integrations")
        
        integrations = load_integrations_config()
        if integrations:
            # Convert to JSON string
            json_str = json.dumps(integrations, indent=4)
            
            # Create download button
            st.download_button(
                label="Download Integrations Config",
                data=json_str,
                file_name="integrations_config.json",
                mime="application/json"
            )
        else:
            st.info("No integrations to export.")
    
    with col2:
        st.write("Import Integrations")
        
        uploaded_file = st.file_uploader(
            "Upload Integrations Config",
            type="json",
            help="Upload a previously exported integrations.json file"
        )
        
        if uploaded_file is not None:
            try:
                # Read the file
                bytes_data = uploaded_file.read()
                
                # Parse JSON
                import_config = json.loads(bytes_data)
                
                # Validate the config
                if not isinstance(import_config, dict):
                    st.error("Invalid configuration format. Expected a JSON object.")
                else:
                    if st.button("Import Config"):
                        # Save the imported config
                        save_integrations_config(import_config)
                        
                        # Load all integrations into the system
                        for name, config in import_config.items():
                            try:
                                if config["type"] == "api":
                                    cfg = config["config"]
                                    create_api_integration(
                                        name=name,
                                        base_url=cfg.get("base_url", ""),
                                        auth_type=cfg.get("auth_type", "api_key"),
                                        api_key=cfg.get("api_key"),
                                        username=cfg.get("username"),
                                        password=cfg.get("password"),
                                        access_token=cfg.get("access_token"),
                                        make_default=config.get("default", False)
                                    )
                                elif config["type"] == "database":
                                    cfg = config["config"]
                                    create_database_integration(
                                        name=name,
                                        driver=cfg.get("driver", "sqlalchemy"),
                                        connection_string=cfg.get("connection_string", ""),
                                        make_default=config.get("default", False)
                                    )
                                elif config["type"] == "file":
                                    cfg = config["config"]
                                    create_file_integration(
                                        name=name,
                                        file_path=cfg.get("file_path", ""),
                                        make_default=config.get("default", False)
                                    )
                                elif config["type"] == "mls":
                                    cfg = config["config"]
                                    create_mls_integration(
                                        name=name,
                                        mls_provider=cfg.get("mls_provider", "rets"),
                                        api_key=cfg.get("api_key", ""),
                                        base_url=cfg.get("base_url", ""),
                                        access_token=cfg.get("access_token"),
                                        make_default=config.get("default", False)
                                    )
                                elif config["type"] == "crm":
                                    cfg = config["config"]
                                    auth_type = cfg.get("auth_type", "api_key")
                                    
                                    create_crm_integration(
                                        name=name,
                                        crm_provider=cfg.get("crm_provider", "salesforce"),
                                        base_url=cfg.get("base_url", ""),
                                        api_key=cfg.get("api_key"),
                                        username=cfg.get("username"),
                                        password=cfg.get("password"),
                                        access_token=cfg.get("access_token"),
                                        make_default=config.get("default", False)
                                    )
                            except Exception as e:
                                logger.error(f"Error creating integration {name}: {str(e)}")
                        
                        st.success("Integrations imported successfully.")
                        st.rerun()
            except Exception as e:
                st.error(f"Error importing configuration: {str(e)}")

def show_integration_settings():
    """Show the integration settings page."""
    st.title("System Integrations")
    
    st.markdown("""
    This page allows you to configure connections to external systems such as MLS (Multiple Listing Service) providers,
    CRM platforms, databases, and more. These integrations enable the real estate application to fetch and store data
    from a variety of sources.
    """)
    
    # Example integration link
    st.info("""
    **Integration Example:** Check the [Integration Example](https://github.com/your-org/your-repo/blob/main/examples/integration_example.py) 
    for sample code demonstrating how to use the integration system.
    """)
    
    # Page tabs
    tab1, tab2, tab3 = st.tabs(["Integrations", "Import/Export", "Example Code"])
    
    with tab1:
        # Add new integration form
        show_new_integration_form()
        
        # Divider
        st.markdown("---")
        
        # List existing integrations
        show_integrations()
    
    with tab2:
        # Import/Export
        show_import_export()
    
    with tab3:
        # Example code
        st.subheader("Example Integration Code")
        
        st.code("""
# Set up MLS integration
create_mls_integration(
    name="example_mls",
    mls_provider="rets",
    api_key="your_api_key_here",
    base_url="https://api.example-mls.com/v1",
    make_default=True
)

# Search for properties
properties = search_properties(
    location="San Francisco, CA",
    min_price=500000,
    max_price=1000000,
    bedrooms=2,
    property_type="Single Family"
)

# Transform the data
properties['price_per_sqft'] = properties['price'] / properties['sqft']
        """, language="python")
        
        st.markdown("See full examples in the 'examples/integration_example.py' file.")
    
    # Help & Troubleshooting
    with st.expander("Help & Troubleshooting"):
        st.markdown("""
        ### Common Integration Issues
        
        1. **Authentication failures**: Double-check your API keys, usernames, and passwords.
        2. **Connection timeouts**: Ensure the external service is online and accessible.
        3. **Rate limiting**: Some APIs limit the number of requests you can make in a given time period.
        4. **Data format errors**: The external system may change its data format, requiring updates to the integration.
        
        ### Best Practices
        
        1. Use separate API keys for development and production environments.
        2. Store sensitive credentials securely and never hardcode them in your application.
        3. Implement proper error handling and logging for integration failures.
        4. Use caching to minimize API calls to external systems.
        """)

if __name__ == "__main__":
    show_integration_settings()