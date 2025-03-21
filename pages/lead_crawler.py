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
    
    tab1, tab2, tab3 = st.tabs(["Search Campaigns", "Contact Results", "Import & Export"])
    
    with tab1:
        show_search_campaigns_tab()
    
    with tab2:
        show_contact_results_tab()
    
    with tab3:
        show_import_export_tab()


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
        
        # Number of results per keyword
        num_results = st.slider("Results per Keyword", 5, 50, 20)
        
        if st.button("Create Campaign"):
            if not campaign_name:
                st.error("Please enter a campaign name.")
            elif not keywords_text:
                st.error("Please enter at least one keyword.")
            elif not search_engines:
                st.error("Please select at least one search engine.")
            else:
                keywords = [k.strip() for k in keywords_text.split("\n") if k.strip()]
                
                campaign_id = save_lead_campaign(
                    campaign_name, 
                    keywords, 
                    search_engines, 
                    num_results
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
                    else:
                        st.write("Status: Not run yet")
                    
                    if st.button(f"Run Campaign", key=f"run_{campaign['id']}"):
                        with st.spinner(f"Running campaign '{campaign['name']}' - this may take a few minutes..."):
                            contacts = run_lead_campaign(campaign['id'])
                            st.success(f"Campaign completed! Found {len(contacts)} potential contacts.")
                            # Add a tab switch button here
                            st.button(f"View Results", key=f"view_{campaign['id']}")
            
            st.divider()


def show_contact_results_tab():
    """Display contact results from campaigns"""
    st.header("Contact Results")
    
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
        index=0
    )
    
    # Extract campaign ID from selection
    selected_id = selected_campaign.split("ID: ")[1].strip(")")
    
    # Get contacts for the selected campaign
    contacts = get_campaign_contacts(selected_id)
    
    if not contacts:
        st.info(f"No contacts found for this campaign. Run the campaign first.")
        return
    
    # Display contacts
    st.write(f"Found {len(contacts)} potential contacts.")
    
    # Filter options
    col1, col2 = st.columns(2)
    
    with col1:
        min_score = st.slider("Minimum Lead Score", 0, 100, 20)
    
    with col2:
        required_fields = st.multiselect(
            "Required Fields",
            ["name", "email", "phone", "company"],
            default=["email"]
        )
    
    # Apply filters
    filtered_contacts = []
    for contact in contacts:
        if contact.get("lead_score", 0) >= min_score:
            if all(contact.get(field) for field in required_fields):
                filtered_contacts.append(contact)
    
    st.write(f"Displaying {len(filtered_contacts)} contacts after filtering.")
    
    # Sort by score
    filtered_contacts.sort(key=lambda x: x.get("lead_score", 0), reverse=True)
    
    # Display as table
    if filtered_contacts:
        # Convert to DataFrame for display
        df = pd.DataFrame(filtered_contacts)
        
        # Select and reorder columns
        display_columns = ["name", "email", "phone", "company", "lead_score", "keyword"]
        display_df = df[display_columns] if all(col in df.columns for col in display_columns) else df
        
        # Show table
        st.dataframe(display_df, use_container_width=True)
        
        # Display contact details in expanders
        for i, contact in enumerate(filtered_contacts):
            with st.expander(f"Contact Details: {contact.get('name') or contact.get('email') or f'Contact #{i+1}'}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Name:** {contact.get('name', 'Not found')}")
                    st.write(f"**Email:** {contact.get('email', 'Not found')}")
                    st.write(f"**Phone:** {contact.get('phone', 'Not found')}")
                    st.write(f"**Company:** {contact.get('company', 'Not found')}")
                
                with col2:
                    st.write(f"**Lead Score:** {contact.get('lead_score', 0)}")
                    st.write(f"**Keyword:** {contact.get('keyword', 'Not specified')}")
                    st.write(f"**Source URL:** [{contact.get('source_url', 'Unknown').split('/')[2]}]({contact.get('source_url', '#')})")
                
                # Snippet from the source page
                if contact.get("snippet"):
                    st.write("**Page Snippet:**")
                    st.info(contact.get("snippet"))
                
                # Import single contact
                if st.button("Import as Lead", key=f"import_{i}"):
                    try:
                        import_contacts_to_database([contact])
                        st.success(f"Contact imported successfully as a lead!")
                    except Exception as e:
                        st.error(f"Error importing contact: {str(e)}")
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