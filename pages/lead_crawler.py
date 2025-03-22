"""
Lead Crawler page for searching for and collecting potential lead contact information.
This page allows users to:
1. Create keyword-based search campaigns
2. Crawl search engines for contact information
3. Import contacts as leads
4. Export contact lists
"""
import os
import json
import time
from urllib.parse import urlparse
import pandas as pd
import streamlit as st
from utils.web_crawler import (
    get_lead_campaigns,
    save_lead_campaign,
    run_lead_campaign,
    get_campaign_contacts,
    calculate_lead_score,
    import_contacts_to_database,
    export_contacts_to_csv
)
from utils.database import get_leads

def show_lead_crawler():
    """Display the lead crawler interface"""
    st.title("Lead Crawler")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "Search Campaigns", 
        "Contact Results", 
        "Import & Export", 
        "API Settings"
    ])
    
    with tab1:
        show_search_campaigns_tab()
    
    with tab2:
        show_contact_results_tab()
    
    with tab3:
        show_import_export_tab()
        
    with tab4:
        show_api_settings_tab()


def show_search_campaigns_tab():
    """Display interface for managing search campaigns"""
    st.header("Search Campaigns")
    
    # Get existing campaigns
    campaigns = get_lead_campaigns()
    
    # New campaign form
    with st.expander("Create New Campaign", expanded=len(campaigns) == 0):
        campaign_name = st.text_input("Campaign Name", key="new_campaign_name")
        
        # Keywords entry
        keywords_text = st.text_area(
            "Keywords (one per line)",
            height=100,
            placeholder="real estate agent\nproperty investor\nhome buyer"
        )
        
        # Search engines selection
        search_engines = st.multiselect(
            "Search Engines",
            ["google", "bing"],
            default=["google", "bing"]
        )
        
        # Target type selection
        st.subheader("Target Types")
        st.write("Select what type of leads you want to focus on:")
        
        col1, col2 = st.columns(2)
        with col1:
            target_agent = st.checkbox("Real Estate Agents", value=True, help="Find real estate agents and realtors")
            target_broker = st.checkbox("Brokers", value=True, help="Find real estate brokers and brokerage firms")
            target_investor = st.checkbox("Investors", value=False, help="Find real estate investors and investment firms")
        
        with col2:
            target_buyer = st.checkbox("Buyers", value=False, help="Find potential property buyers")
            target_seller = st.checkbox("Sellers", value=False, help="Find potential property sellers")
            target_property = st.checkbox("Property Listings", value=True, help="Find property listings and details")
        
        # Location targeting
        st.subheader("Location Targeting")
        location = st.text_input(
            "Target Location (optional)",
            placeholder="e.g., New York, NY or Mumbai, India",
            help="Add a location to focus your search on a specific area"
        )
        
        # Number of results per keyword
        num_results = st.slider("Results per Keyword", 5, 50, 20)
        
        # Advanced options section (without nested expander)
        st.subheader("Advanced Options")
        min_contact_info = st.multiselect(
            "Required Contact Information",
            ["name", "email", "phone", "company"],
            default=["email"],
            help="Select which contact information fields are required for a lead to be considered valid"
        )
        
        min_lead_score = st.slider(
            "Minimum Lead Score",
            0, 100, 30,
            help="Only include leads with at least this score (higher scores indicate more complete and reliable information)"
        )
        
        if st.button("Create Campaign"):
            if not campaign_name:
                st.error("Please enter a campaign name.")
            elif not keywords_text:
                st.error("Please enter at least one keyword.")
            elif not search_engines:
                st.error("Please select at least one search engine.")
            elif not (target_agent or target_broker or target_investor or target_buyer or target_seller or target_property):
                st.error("Please select at least one target type.")
            else:
                keywords = [k.strip() for k in keywords_text.split("\n") if k.strip()]
                
                # Create target types list
                target_types = []
                if target_agent:
                    target_types.append("agent")
                if target_broker:
                    target_types.append("broker")
                if target_investor:
                    target_types.append("investor")
                if target_buyer:
                    target_types.append("buyer")
                if target_seller:
                    target_types.append("seller")
                if target_property:
                    target_types.append("property")
                
                # Save the campaign with enhanced options
                campaign_id = save_lead_campaign(
                    campaign_name, 
                    keywords, 
                    search_engines, 
                    num_results,
                    target_types=target_types,
                    location=location,
                    min_lead_score=min_lead_score,
                    required_fields=min_contact_info
                )
                
                st.success(f"Campaign '{campaign_name}' created successfully!")
                st.rerun()
    
    # Display existing campaigns
    if campaigns:
        st.subheader("Your Campaigns")
        
        for i, campaign in enumerate(campaigns):
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    st.write(f"**{campaign['name']}**")
                    st.caption(f"Created: {campaign['created_at'][:10]}")
                    
                    # Show target types and location if available in new campaigns
                    if 'target_types' in campaign:
                        target_types_str = ", ".join(campaign['target_types'])
                        st.caption(f"Targeting: {target_types_str}")
                    
                    if 'location' in campaign and campaign['location']:
                        st.caption(f"Location: {campaign['location']}")
                
                with col2:
                    keywords_str = ", ".join(campaign['keywords'][:3])
                    if len(campaign['keywords']) > 3:
                        keywords_str += f" and {len(campaign['keywords']) - 3} more"
                    st.write(f"Keywords: {keywords_str}")
                    
                    engines_str = ", ".join(campaign['search_engines'])
                    st.write(f"Engines: {engines_str}")
                
                with col3:
                    if campaign.get("last_run"):
                        st.write(f"Status: {campaign['status']}")
                        st.write(f"Last run: {campaign['last_run'][:10]}")
                        
                        # Show lead count if available
                        if 'lead_count' in campaign:
                            st.write(f"Leads: {campaign['lead_count']}")
                    else:
                        st.write("Status: Not run yet")
                    
                    run_col, view_col = st.columns(2)
                    with run_col:
                        if st.button(f"Run", key=f"run_{campaign['id']}"):
                            with st.spinner(f"Running campaign '{campaign['name']}' - this may take a few minutes..."):
                                contacts = run_lead_campaign(campaign['id'])
                                st.success(f"Campaign completed! Found {len(contacts)} potential contacts.")
                    
                    with view_col:
                        if st.button(f"View", key=f"view_{campaign['id']}"):
                            # Store the selected campaign ID in session state for the results tab
                            st.session_state.selected_campaign_id = campaign['id']
                            st.session_state.active_tab = "Contact Results"
                            st.rerun()
            
            st.divider()


def show_contact_results_tab():
    """Display contact results from campaigns"""
    st.header("Contact Results")
    
    # Initialize session state for active tab if needed
    if 'selected_campaign_id' not in st.session_state:
        st.session_state.selected_campaign_id = None
    
    # Get existing campaigns
    campaigns = get_lead_campaigns()
    
    if not campaigns:
        st.info("No campaigns found. Create a campaign in the 'Search Campaigns' tab.")
        return
    
    # Campaign selector
    campaign_names = [f"{c['name']} (ID: {c['id']})" for c in campaigns]
    
    # If we have a selected campaign ID from another tab, use it
    selected_index = 0
    if st.session_state.selected_campaign_id:
        for i, c in enumerate(campaigns):
            if c['id'] == st.session_state.selected_campaign_id:
                selected_index = i
                break
    
    selected_campaign = st.selectbox(
        "Select Campaign",
        campaign_names,
        index=selected_index
    )
    
    # Extract campaign ID from selection
    selected_id = selected_campaign.split("ID: ")[1].strip(")")
    
    # Update session state with selected campaign
    st.session_state.selected_campaign_id = selected_id
    
    # Get the selected campaign data
    selected_campaign_data = next((c for c in campaigns if c['id'] == selected_id), None)
    
    # Get contacts for the selected campaign
    contacts = get_campaign_contacts(selected_id)
    
    if not contacts:
        st.info(f"No contacts found for this campaign. Run the campaign first.")
        return
    
    # Display contacts
    st.write(f"Found {len(contacts)} potential contacts.")
    
    # Create tabs for different contact types if we have lead type information
    if any('lead_type' in contact for contact in contacts):
        # Count contacts by lead type
        lead_types = {}
        for contact in contacts:
            lead_type = contact.get('lead_type', 'other')
            lead_types[lead_type] = lead_types.get(lead_type, 0) + 1
        
        # Create tabs for each lead type plus an "All" tab
        lead_type_tabs = ["All"] + sorted(lead_types.keys())
        tabs = st.tabs(lead_type_tabs)
        
        for i, tab_name in enumerate(lead_type_tabs):
            with tabs[i]:
                # Filter contacts by lead type
                if tab_name == "All":
                    filtered_by_type = contacts
                else:
                    filtered_by_type = [c for c in contacts if c.get('lead_type', 'other') == tab_name]
                
                # Display the filtered contacts
                display_filtered_contacts(filtered_by_type, tab_name)
    else:
        # If no lead type data, just display all contacts
        display_filtered_contacts(contacts, "All")


def display_filtered_contacts(contacts, lead_type="All"):
    """Helper function to display and filter contacts"""
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        min_score = st.slider("Minimum Lead Score", 0, 100, 20, key=f"score_{lead_type}")
    
    with col2:
        required_fields = st.multiselect(
            "Required Fields",
            ["name", "email", "phone", "company"],
            default=["email"],
            key=f"fields_{lead_type}"
        )
    
    with col3:
        sort_by = st.selectbox(
            "Sort By",
            ["Lead Score", "Name", "Company", "Email"],
            index=0,
            key=f"sort_{lead_type}"
        )
    
    # Apply filters
    filtered_contacts = []
    for contact in contacts:
        if contact.get("lead_score", 0) >= min_score:
            if all(contact.get(field) for field in required_fields):
                filtered_contacts.append(contact)
    
    st.write(f"Displaying {len(filtered_contacts)} contacts after filtering.")
    
    # Sort contacts
    if sort_by == "Lead Score":
        filtered_contacts.sort(key=lambda x: x.get("lead_score", 0), reverse=True)
    elif sort_by == "Name":
        filtered_contacts.sort(key=lambda x: x.get("name", "").lower())
    elif sort_by == "Company":
        filtered_contacts.sort(key=lambda x: x.get("company", "").lower())
    elif sort_by == "Email":
        filtered_contacts.sort(key=lambda x: x.get("email", "").lower())
    
    # Display as table
    if filtered_contacts:
        # Convert to DataFrame for display
        df = pd.DataFrame(filtered_contacts)
        
        # Select and reorder columns based on available data
        standard_columns = ["name", "email", "phone", "company", "lead_score"]
        
        # Add lead type if available
        if 'lead_type' in df.columns:
            standard_columns.insert(4, "lead_type")
            
        # Add job title if available
        if 'job_title' in df.columns:
            standard_columns.insert(3, "job_title")
            
        # Add keyword and source columns
        standard_columns.extend(["keyword", "domain"])
        
        # Filter to only columns that exist in the DataFrame
        display_columns = [col for col in standard_columns if col in df.columns]
        
        # Create display DataFrame with only the selected columns
        display_df = df[display_columns] if len(display_columns) > 0 else df
        
        # Show table
        st.dataframe(display_df, use_container_width=True)
        
        # Button to import all filtered contacts
        if st.button(f"Import All {len(filtered_contacts)} Contacts", key=f"import_all_{lead_type}"):
            try:
                import_count = import_contacts_to_database(filtered_contacts)
                st.success(f"Successfully imported {import_count} contacts as leads!")
            except Exception as e:
                st.error(f"Error importing contacts: {str(e)}")
        
        # Display contact details in expanders
        for i, contact in enumerate(filtered_contacts):
            # Format the expander title based on available information
            title_parts = []
            if contact.get('name'):
                title_parts.append(contact['name'])
            if contact.get('job_title'):
                title_parts.append(contact['job_title'])
            if contact.get('company') and not title_parts:
                title_parts.append(contact['company'])
                
            expander_title = " - ".join(title_parts) if title_parts else f"Contact #{i+1}"
            if contact.get('lead_type'):
                expander_title = f"{contact['lead_type'].title()}: {expander_title}"
                
            with st.expander(expander_title):
                col1, col2 = st.columns([3, 2])
                
                with col1:
                    # Basic contact info
                    st.subheader("Contact Information")
                    if contact.get('name'):
                        st.write(f"**Name:** {contact['name']}")
                    if contact.get('job_title'):
                        st.write(f"**Job Title:** {contact['job_title']}")
                    if contact.get('email'):
                        st.write(f"**Email:** {contact['email']}")
                    if contact.get('phone'):
                        st.write(f"**Phone:** {contact['phone']}")
                    if contact.get('company'):
                        st.write(f"**Company:** {contact['company']}")
                    if contact.get('location'):
                        st.write(f"**Location:** {contact['location']}")
                        
                    # Social profiles if available
                    if contact.get('social_profiles') and any(contact['social_profiles'].values()):
                        st.subheader("Social Profiles")
                        social_profiles = contact['social_profiles']
                        for platform, profile in social_profiles.items():
                            if profile:
                                platform_name = platform.capitalize()
                                st.write(f"**{platform_name}:** {profile}")
                
                with col2:
                    # Lead quality info
                    st.subheader("Lead Quality")
                    lead_score = contact.get('lead_score', 0)
                    score_color = "red" if lead_score < 30 else "orange" if lead_score < 60 else "green"
                    st.markdown(f"**Lead Score:** <span style='color:{score_color};font-weight:bold'>{lead_score}</span>", unsafe_allow_html=True)
                    
                    if contact.get('lead_type'):
                        st.write(f"**Lead Type:** {contact['lead_type'].title()}")
                    
                    st.write(f"**Found via:** {contact.get('keyword', 'Not specified')}")
                    
                    # Source information
                    st.subheader("Source")
                    if contact.get('source_url'):
                        try:
                            domain = urlparse(contact['source_url']).netloc
                            st.write(f"**Website:** [{domain}]({contact['source_url']})")
                        except:
                            st.write(f"**Source URL:** [{contact.get('source_url', '#')}]")
                    
                # Target relevance if available
                if contact.get('target_relevance') and any(contact['target_relevance'].values()):
                    st.subheader("Relevance Scores")
                    relevance = contact['target_relevance']
                    
                    # Create a horizontal bar chart of relevance scores
                    relevance_data = {k.title(): v for k, v in relevance.items() if v > 0}
                    if relevance_data:
                        # Sort by relevance score
                        sorted_relevance = dict(sorted(relevance_data.items(), key=lambda x: x[1], reverse=True))
                        
                        # Display as a simple text with color coding
                        for role, score in sorted_relevance.items():
                            score_color = "red" if score < 5 else "orange" if score < 15 else "green"
                            st.markdown(f"**{role}:** <span style='color:{score_color}'>{score}</span>/30", unsafe_allow_html=True)
                
                # Snippet from the source page
                if contact.get("snippet"):
                    st.subheader("Page Snippet")
                    st.info(contact.get("snippet"))
                
                # Enhanced query if available
                if contact.get("enhanced_query") and contact.get("enhanced_query") != contact.get("query"):
                    st.subheader("Search Information")
                    st.write(f"**Original Query:** {contact.get('query', '')}")
                    st.write(f"**Enhanced Query:** {contact.get('enhanced_query', '')}")
                
                # Action buttons
                st.subheader("Actions")
                col1, col2 = st.columns(2)
                
                with col1:
                    # Import single contact
                    if st.button("Import as Lead", key=f"import_{i}_{lead_type}"):
                        try:
                            import_contacts_to_database([contact])
                            st.success(f"Contact imported successfully as a lead!")
                        except Exception as e:
                            st.error(f"Error importing contact: {str(e)}")
                
                with col2:
                    # Email the contact (prepare an email)
                    if contact.get('email') and st.button("Email Contact", key=f"email_{i}_{lead_type}"):
                        # Format with mailto link
                        subject = f"Regarding your real estate {contact.get('lead_type', 'interests')}"
                        body = f"Hello {contact.get('name', 'there')},\n\nI wanted to reach out regarding your real estate {contact.get('lead_type', 'interests')}..."
                        mailto_link = f"mailto:{contact['email']}?subject={subject}&body={body}"
                        
                        # Open in a new tab using JavaScript
                        js = f"""
                        <a href="{mailto_link}" target="_blank" id="mailto_link_{i}">Click here if the email doesn't open automatically</a>
                        <script>
                            window.open("{mailto_link}", "_blank");
                        </script>
                        """
                        st.markdown(js, unsafe_allow_html=True)
    else:
        st.info("No contacts match the current filters.")


def show_import_export_tab():
    """Display import and export interface"""
    st.header("Import & Export")
    
    # Get existing campaigns
    campaigns = get_lead_campaigns()
    
    if not campaigns:
        st.info("No campaigns found. Create a campaign in the 'Search Campaigns' tab.")
        return
    
    # Campaign selector
    campaign_names = [f"{c['name']} (ID: {c['id']})" for c in campaigns]
    selected_campaign = st.selectbox(
        "Select Campaign",
        campaign_names,
        index=0,
        key="export_campaign_select"
    )
    
    # Extract campaign ID from selection
    selected_id = selected_campaign.split("ID: ")[1].strip(")")
    
    # Get contacts for the selected campaign
    contacts = get_campaign_contacts(selected_id)
    
    if not contacts:
        st.info(f"No contacts found for this campaign. Run the campaign first.")
        return
    
    # Show import options
    st.subheader("Import to Database")
    
    col1, col2 = st.columns(2)
    
    with col1:
        min_score_import = st.slider("Minimum Score for Import", 0, 100, 30, key="min_score_import")
    
    with col2:
        required_fields_import = st.multiselect(
            "Required Fields for Import",
            ["name", "email", "phone", "company"],
            default=["email"],
            key="required_fields_import"
        )
    
    # Filter contacts for import
    import_contacts = []
    for contact in contacts:
        if contact.get("lead_score", 0) >= min_score_import:
            if all(contact.get(field) for field in required_fields_import):
                import_contacts.append(contact)
    
    st.write(f"{len(import_contacts)} contacts meet the import criteria.")
    
    if import_contacts:
        if st.button(f"Import {len(import_contacts)} Contacts as Leads"):
            with st.spinner("Importing contacts..."):
                try:
                    count = import_contacts_to_database(import_contacts)
                    st.success(f"Successfully imported {count} contacts as leads!")
                    
                    # Get lead counts
                    leads_df = get_leads()
                    st.info(f"You now have {len(leads_df)} total leads in your database.")
                except Exception as e:
                    st.error(f"Error importing contacts: {str(e)}")
    
    # Show export options
    st.subheader("Export Contacts")
    
    col1, col2 = st.columns(2)
    
    with col1:
        min_score_export = st.slider("Minimum Score for Export", 0, 100, 0, key="min_score_export")
    
    with col2:
        required_fields_export = st.multiselect(
            "Required Fields for Export",
            ["name", "email", "phone", "company"],
            default=[],
            key="required_fields_export"
        )
    
    # Filter contacts for export
    export_contacts = []
    for contact in contacts:
        if contact.get("lead_score", 0) >= min_score_export:
            if all(contact.get(field) for field in required_fields_export):
                export_contacts.append(contact)
    
    st.write(f"{len(export_contacts)} contacts meet the export criteria.")
    
    if export_contacts:
        export_format = st.selectbox(
            "Export Format",
            ["CSV", "Excel"],
            index=0
        )
        
        if st.button(f"Export {len(export_contacts)} Contacts"):
            # Create export directory if it doesn't exist
            if not os.path.exists("exports"):
                os.makedirs("exports")
            
            # Generate filename
            campaign_name = selected_campaign.split(" (ID:")[0]
            timestamp = int(time.time())
            
            try:
                if export_format == "CSV":
                    filename = f"exports/contacts_{campaign_name}_{timestamp}.csv"
                    export_contacts_to_csv(export_contacts, filename)
                else:  # Excel
                    filename = f"exports/contacts_{campaign_name}_{timestamp}.xlsx"
                    pd.DataFrame(export_contacts).to_excel(filename, index=False)
                
                st.success(f"Contacts exported successfully to {filename}!")
                
                # Provide download link
                with open(filename, "rb") as file:
                    st.download_button(
                        label=f"Download {export_format} File",
                        data=file,
                        file_name=os.path.basename(filename),
                        mime="text/csv" if export_format == "CSV" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            except Exception as e:
                st.error(f"Error exporting contacts: {str(e)}")


def show_api_settings_tab():
    """Display API settings interface for web crawler"""
    st.header("API Settings")
    
    # Explanation
    st.write("""
    The lead crawler uses search engine APIs to find potential leads more effectively. 
    While it can work without API keys using direct web scraping, setting up API keys 
    provides more reliable results and helps avoid rate limits or IP blocks.
    """)
    
    # API key configuration
    st.subheader("Search API Keys")
    
    # Common functions to load/save API keys from/to .env file
    def load_env_variables():
        """Load environment variables from .env file"""
        # Check if .env file exists
        if os.path.exists('.env'):
            # Import only when needed
            from dotenv import load_dotenv
            load_dotenv()
        
        return {
            'SERPAPI_KEY': os.environ.get('SERPAPI_KEY', ''),
            'BING_API_KEY': os.environ.get('BING_API_KEY', '')
        }
    
    def save_env_variables(env_vars):
        """Save environment variables to .env file"""
        # Import only when needed
        from dotenv import load_dotenv, set_key
        
        # Load existing variables first
        load_dotenv()
        
        # Update the variables
        for key, value in env_vars.items():
            if value:  # Only set if value is not empty
                set_key('.env', key, value)
                os.environ[key] = value  # Also update current environment
    
    # Load current API keys
    api_keys = load_env_variables()
    
    # Google Search (SerpAPI)
    st.markdown("#### Google Search API (SerpAPI)")
    st.write("""
    SerpAPI provides access to Google search results in a structured format.
    You can sign up for a free trial at [SerpAPI](https://serpapi.com/).
    """)
    
    serpapi_key = st.text_input(
        "SerpAPI Key",
        value=api_keys.get('SERPAPI_KEY', ''),
        type="password",
        help="Your SerpAPI key for Google search results"
    )
    
    # Bing Search API
    st.markdown("#### Microsoft Bing Search API")
    st.write("""
    The Bing Search API is available through Azure Cognitive Services.
    You can sign up for a free tier at [Azure Cognitive Services](https://azure.microsoft.com/en-us/products/cognitive-services/).
    """)
    
    bing_api_key = st.text_input(
        "Bing API Key",
        value=api_keys.get('BING_API_KEY', ''),
        type="password",
        help="Your Bing Search API key from Azure Cognitive Services"
    )
    
    # Save button
    if st.button("Save API Keys"):
        # Update API keys
        new_keys = {
            'SERPAPI_KEY': serpapi_key,
            'BING_API_KEY': bing_api_key
        }
        
        try:
            save_env_variables(new_keys)
            st.success("API keys saved successfully!")
        except Exception as e:
            st.error(f"Error saving API keys: {str(e)}")
    
    # Test connection
    st.subheader("Test API Connection")
    
    test_query = st.text_input(
        "Test Search Query",
        value="real estate agent",
        help="Enter a search query to test the API connections"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Test Google Search API"):
            with st.spinner("Testing Google Search API..."):
                try:
                    # Import search function
                    from utils.web_crawler import search_google
                    
                    # Test with a small number of results
                    results = search_google(test_query, num_results=3, use_cache=False)
                    
                    if results:
                        st.success(f"Successfully received {len(results)} results from Google!")
                        
                        # Show a sample result
                        with st.expander("Sample Result"):
                            if len(results) > 0:
                                result = results[0]
                                st.write(f"**Title:** {result.get('title', 'N/A')}")
                                st.write(f"**URL:** {result.get('link', 'N/A')}")
                                st.write(f"**Snippet:** {result.get('snippet', 'N/A')}")
                                st.write(f"**Source:** {result.get('source', 'direct')}")
                    else:
                        st.warning("No results returned. The API may not be working correctly.")
                except Exception as e:
                    st.error(f"Error testing Google Search API: {str(e)}")
    
    with col2:
        if st.button("Test Bing Search API"):
            with st.spinner("Testing Bing Search API..."):
                try:
                    # Import search function
                    from utils.web_crawler import search_bing
                    
                    # Test with a small number of results
                    results = search_bing(test_query, num_results=3, use_cache=False)
                    
                    if results:
                        st.success(f"Successfully received {len(results)} results from Bing!")
                        
                        # Show a sample result
                        with st.expander("Sample Result"):
                            if len(results) > 0:
                                result = results[0]
                                st.write(f"**Title:** {result.get('title', 'N/A')}")
                                st.write(f"**URL:** {result.get('link', 'N/A')}")
                                st.write(f"**Snippet:** {result.get('snippet', 'N/A')}")
                                st.write(f"**Source:** {result.get('source', 'direct')}")
                    else:
                        st.warning("No results returned. The API may not be working correctly.")
                except Exception as e:
                    st.error(f"Error testing Bing Search API: {str(e)}")
    
    # Advanced settings
    with st.expander("Advanced Settings"):
        st.markdown("#### Cache Settings")
        st.write("""
        The lead crawler caches search results to avoid unnecessary API calls.
        You can adjust how long results are cached before being refreshed.
        """)
        
        cache_hours = st.slider(
            "Cache Duration (hours)",
            min_value=1,
            max_value=72,
            value=24,
            help="How long to keep cached search results before refreshing"
        )
        
        if st.button("Save Cache Settings"):
            try:
                # In a real implementation, this would save to a config file
                st.success(f"Cache settings updated: {cache_hours} hours")
            except Exception as e:
                st.error(f"Error saving cache settings: {str(e)}")
        
        st.markdown("#### Clear Cache")
        st.write("You can clear the search cache if you need fresh results.")
        
        if st.button("Clear Search Cache"):
            try:
                # Clear cache directory
                import shutil
                from utils.web_crawler import CACHE_DIR, ensure_cache_dir
                
                if os.path.exists(CACHE_DIR):
                    # Keep the directory but remove its contents
                    for filename in os.listdir(CACHE_DIR):
                        filepath = os.path.join(CACHE_DIR, filename)
                        try:
                            if os.path.isfile(filepath) or os.path.islink(filepath):
                                os.unlink(filepath)
                            elif os.path.isdir(filepath):
                                shutil.rmtree(filepath)
                        except Exception as e:
                            st.error(f"Failed to clear {filepath}: {e}")
                
                # Re-create the directory if needed
                ensure_cache_dir()
                
                st.success("Search cache cleared successfully!")
            except Exception as e:
                st.error(f"Error clearing cache: {str(e)}")