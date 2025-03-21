import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

def show_lead_management():
    st.title("AI-Powered Lead Qualification & Nurturing")
    
    st.markdown("""
    Our AI-powered lead management system helps real estate professionals qualify, nurture, and convert leads more effectively.
    Automate follow-ups and prioritize the most promising prospects based on intent and behavior analysis.
    """)
    
    # Create tabs for different lead management functions
    tab1, tab2, tab3 = st.tabs(["Lead Dashboard", "Lead Qualification", "Automated Nurturing"])
    
    with tab1:
        show_lead_dashboard()
    
    with tab2:
        show_lead_qualification()
    
    with tab3:
        show_lead_nurturing()

def show_lead_dashboard():
    st.subheader("Lead Management Dashboard")
    
    st.markdown("""
    Track and manage your leads with our intelligent dashboard. See at a glance which leads are most promising
    and require immediate attention.
    """)
    
    # Sample lead data (in a real app, this would come from a database)
    if 'leads' not in st.session_state:
        # Generate sample lead data
        leads = generate_sample_leads(30)
        st.session_state.leads = leads
    
    leads = st.session_state.leads
    
    # Display summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_leads = len(leads)
        st.metric("Total Leads", f"{total_leads}")
    
    with col2:
        hot_leads = len(leads[leads['lead_score'] >= 80])
        st.metric("Hot Leads", f"{hot_leads}")
    
    with col3:
        conversion_rate = round((leads['status'] == 'Converted').mean() * 100, 1)
        st.metric("Conversion Rate", f"{conversion_rate}%")
    
    with col4:
        avg_response_time = round(leads['response_time_hours'].mean(), 1)
        st.metric("Avg. Response Time", f"{avg_response_time} hrs")
    
    # Lead funnel visualization
    st.subheader("Lead Funnel")
    
    funnel_data = [
        {'stage': 'Total Leads', 'count': len(leads)},
        {'stage': 'Contacted', 'count': len(leads[leads['status'].isin(['Contacted', 'Nurturing', 'Qualified', 'Converted'])])},
        {'stage': 'Nurturing', 'count': len(leads[leads['status'].isin(['Nurturing', 'Qualified', 'Converted'])])},
        {'stage': 'Qualified', 'count': len(leads[leads['status'].isin(['Qualified', 'Converted'])])},
        {'stage': 'Converted', 'count': len(leads[leads['status'] == 'Converted'])}
    ]
    
    funnel_df = pd.DataFrame(funnel_data)
    
    fig = px.funnel(
        funnel_df,
        x='count',
        y='stage',
        title='Lead Conversion Funnel'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Lead source breakdown
    st.subheader("Lead Sources")
    
    source_counts = leads['source'].value_counts().reset_index()
    source_counts.columns = ['source', 'count']
    
    fig = px.pie(
        source_counts,
        values='count',
        names='source',
        title='Leads by Source',
        hole=0.4
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Lead table with filtering
    st.subheader("Lead Management")
    
    # Filter controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.multiselect(
            "Filter by Status",
            options=sorted(leads['status'].unique()),
            default=sorted(leads['status'].unique())
        )
    
    with col2:
        source_filter = st.multiselect(
            "Filter by Source",
            options=sorted(leads['source'].unique()),
            default=sorted(leads['source'].unique())
        )
    
    with col3:
        score_range = st.slider(
            "Lead Score Range",
            min_value=0,
            max_value=100,
            value=(0, 100)
        )
    
    # Apply filters
    filtered_leads = leads.copy()
    
    if status_filter:
        filtered_leads = filtered_leads[filtered_leads['status'].isin(status_filter)]
    
    if source_filter:
        filtered_leads = filtered_leads[filtered_leads['source'].isin(source_filter)]
    
    filtered_leads = filtered_leads[
        (filtered_leads['lead_score'] >= score_range[0]) & 
        (filtered_leads['lead_score'] <= score_range[1])
    ]
    
    # Sort leads by score (descending)
    filtered_leads = filtered_leads.sort_values('lead_score', ascending=False)
    
    # Style the lead score
    def style_lead_score(val):
        if val >= 80:
            return f'<span style="color:green; font-weight:bold">{val}</span>'
        elif val >= 50:
            return f'<span style="color:orange">{val}</span>'
        else:
            return f'<span style="color:red">{val}</span>'
    
    # Format the created date
    filtered_leads['created_at'] = filtered_leads['created_at'].dt.strftime('%Y-%m-%d')
    
    # Prepare display DataFrame
    display_df = filtered_leads[['name', 'email', 'phone', 'status', 'source', 'lead_score', 'created_at', 'last_activity']]
    
    # Apply styling to lead score column
    display_df['lead_score'] = display_df['lead_score'].apply(style_lead_score)
    
    # Convert DataFrame to HTML with styled lead scores
    html = display_df.to_html(escape=False, index=False)
    st.write(html, unsafe_allow_html=True)
    
    # Action buttons for selected lead
    st.subheader("Lead Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        selected_lead = st.selectbox(
            "Select Lead for Action",
            options=filtered_leads['name'].tolist()
        )
    
    if selected_lead:
        lead_index = filtered_leads[filtered_leads['name'] == selected_lead].index[0]
        lead = filtered_leads.loc[lead_index]
        
        with col2:
            action = st.selectbox(
                "Select Action",
                options=["Update Status", "Add Note", "Send Email", "Schedule Call"]
            )
        
        with col3:
            if action == "Update Status":
                new_status = st.selectbox(
                    "New Status",
                    options=["New", "Contacted", "Nurturing", "Qualified", "Converted", "Lost"]
                )
                if st.button("Update"):
                    # Update the status in the session state
                    st.session_state.leads.loc[lead_index, 'status'] = new_status
                    st.session_state.leads.loc[lead_index, 'last_activity'] = 'Status updated'
                    st.success(f"Status updated to {new_status}")
                    st.rerun()
            
            elif action == "Add Note":
                note = st.text_area("Note Content")
                if st.button("Add Note"):
                    st.session_state.leads.loc[lead_index, 'last_activity'] = 'Note added'
                    st.success("Note added successfully")
                    st.rerun()
            
            elif action == "Send Email":
                email_subject = st.text_input("Email Subject")
                if st.button("Send Email"):
                    st.session_state.leads.loc[lead_index, 'last_activity'] = 'Email sent'
                    st.success(f"Email sent to {lead['email']}")
                    st.rerun()
            
            elif action == "Schedule Call":
                call_date = st.date_input("Call Date")
                if st.button("Schedule"):
                    st.session_state.leads.loc[lead_index, 'last_activity'] = f'Call scheduled on {call_date}'
                    st.success(f"Call scheduled with {lead['name']} on {call_date}")
                    st.rerun()

def show_lead_qualification():
    st.subheader("AI Lead Qualification")
    
    st.markdown("""
    Our AI system automatically qualifies leads based on their behavior, interactions, and property preferences.
    This helps you focus on leads with the highest likelihood of conversion.
    """)
    
    # Lead qualification form
    st.write("Enter lead information to get an AI-powered qualification score:")
    
    with st.form("lead_qualification_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Lead Name")
            email = st.text_input("Email")
            phone = st.text_input("Phone")
            source = st.selectbox(
                "Lead Source",
                options=["Website", "Referral", "Zillow", "Realtor.com", "Social Media", "Direct Mail", "Open House"]
            )
        
        with col2:
            property_interest = st.selectbox(
                "Property Interest",
                options=["Single Family", "Condo", "Townhouse", "Multi-Family", "Land", "Commercial"]
            )
            price_range = st.select_slider(
                "Price Range",
                options=["$100k-$200k", "$200k-$300k", "$300k-$500k", "$500k-$750k", "$750k-$1M", "$1M+"]
            )
            urgency = st.select_slider(
                "Purchase Timeline",
                options=["0-3 months", "3-6 months", "6-12 months", "12+ months", "Just browsing"]
            )
            website_visits = st.number_input("Number of Website Visits", min_value=0, max_value=100, value=1)
        
        # Behavioral signals
        st.subheader("Behavioral Signals")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            viewed_listings = st.number_input("Listings Viewed", min_value=0, max_value=100, value=0)
        
        with col2:
            saved_properties = st.number_input("Saved Properties", min_value=0, max_value=20, value=0)
        
        with col3:
            requested_showings = st.number_input("Requested Showings", min_value=0, max_value=10, value=0)
        
        # Financial qualification
        st.subheader("Financial Qualification")
        
        col1, col2 = st.columns(2)
        
        with col1:
            pre_approved = st.selectbox("Pre-Approved for Mortgage?", options=["Yes", "No", "In Process", "Unknown"])
        
        with col2:
            credit_score_range = st.select_slider(
                "Credit Score Range (if known)",
                options=["Unknown", "Below 620", "620-680", "680-720", "720-760", "760+"]
            )
        
        submit_button = st.form_submit_button("Calculate Lead Score")
    
    # Calculate and display lead score on submit
    if submit_button:
        if not name or not email:
            st.error("Please enter at least a name and email address.")
        else:
            # Calculate lead score based on inputs
            score = calculate_lead_score(
                source, property_interest, price_range, urgency, website_visits,
                viewed_listings, saved_properties, requested_showings, pre_approved, credit_score_range
            )
            
            # Display the score
            st.subheader("Lead Qualification Results")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Lead score gauge
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=score,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Lead Score"},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, 40], 'color': "red"},
                            {'range': [40, 70], 'color': "orange"},
                            {'range': [70, 100], 'color': "green"}
                        ],
                        'threshold': {
                            'line': {'color': "black", 'width': 4},
                            'thickness': 0.75,
                            'value': 80
                        }
                    }
                ))
                
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Lead classification and recommendations
                if score >= 80:
                    st.success("### Hot Lead - High Priority")
                    st.markdown("""
                    **Recommendations:**
                    - Contact immediately (within 1 hour)
                    - Offer personalized property recommendations
                    - Schedule showing for properties matching their criteria
                    """)
                elif score >= 60:
                    st.warning("### Warm Lead - Medium Priority")
                    st.markdown("""
                    **Recommendations:**
                    - Contact within 24 hours
                    - Provide market information and buying guides
                    - Set up automated property alerts
                    """)
                else:
                    st.info("### Cold Lead - Nurture")
                    st.markdown("""
                    **Recommendations:**
                    - Add to nurture campaign
                    - Send educational content weekly
                    - Re-evaluate after 30 days of engagement tracking
                    """)
            
            # Detailed score breakdown
            st.subheader("Score Breakdown")
            
            factor_scores = {
                "Lead Source Quality": get_source_score(source),
                "Property Interest Match": get_property_interest_score(property_interest, price_range),
                "Purchase Timeline": get_urgency_score(urgency),
                "Website Engagement": get_engagement_score(website_visits, viewed_listings, saved_properties),
                "Showing Requests": get_showing_score(requested_showings),
                "Financial Qualification": get_financial_score(pre_approved, credit_score_range)
            }
            
            # Create DataFrame for visualization
            breakdown_df = pd.DataFrame({
                'Factor': list(factor_scores.keys()),
                'Score Contribution': list(factor_scores.values())
            })
            
            # Sort by score contribution
            breakdown_df = breakdown_df.sort_values('Score Contribution', ascending=False)
            
            # Create horizontal bar chart
            fig = px.bar(
                breakdown_df,
                y='Factor',
                x='Score Contribution',
                orientation='h',
                title='Lead Score Contribution Factors',
                template='plotly_white',
                color='Score Contribution',
                color_continuous_scale=px.colors.sequential.Viridis
            )
            
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # Save this lead
            if st.button("Save Lead to Database"):
                if 'leads' not in st.session_state:
                    st.session_state.leads = generate_sample_leads(1)  # Start with an empty DataFrame
                
                # Add the new lead
                new_lead = {
                    'name': name,
                    'email': email,
                    'phone': phone,
                    'status': 'New',
                    'source': source,
                    'lead_score': score,
                    'created_at': datetime.now(),
                    'response_time_hours': 0,
                    'last_activity': 'Lead created',
                    'property_interest': property_interest,
                    'price_range': price_range
                }
                
                st.session_state.leads = pd.concat([st.session_state.leads, pd.DataFrame([new_lead])], ignore_index=True)
                st.success(f"Lead '{name}' saved successfully with a score of {score}")

def show_lead_nurturing():
    st.subheader("Automated Lead Nurturing")
    
    st.markdown("""
    Set up intelligent nurturing campaigns that automatically engage leads with personalized content
    based on their interests, behavior, and stage in the buying journey.
    """)
    
    # Display available nurturing campaigns
    st.write("### Available Nurturing Campaigns")
    
    campaigns = [
        {
            'name': 'First-time Homebuyer Education',
            'trigger': 'New lead identified as first-time buyer',
            'emails': 5,
            'duration': '45 days',
            'open_rate': '32%',
            'status': 'Active'
        },
        {
            'name': 'Luxury Property Showcase',
            'trigger': 'Interest in properties over $1M',
            'emails': 4,
            'duration': '30 days',
            'open_rate': '28%',
            'status': 'Active'
        },
        {
            'name': 'Investment Property Opportunities',
            'trigger': 'Interest in investment properties',
            'emails': 6,
            'duration': '60 days',
            'open_rate': '35%',
            'status': 'Active'
        },
        {
            'name': 'Neighborhood Spotlight Series',
            'trigger': 'Interest in specific neighborhoods',
            'emails': 8,
            'duration': '90 days',
            'open_rate': '26%',
            'status': 'Paused'
        },
        {
            'name': 'Re-engagement Campaign',
            'trigger': 'No activity for 30+ days',
            'emails': 3,
            'duration': '21 days',
            'open_rate': '18%',
            'status': 'Active'
        }
    ]
    
    campaign_df = pd.DataFrame(campaigns)
    
    # Create an expanded table view with colors
    for i, campaign in enumerate(campaigns):
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                status_color = "green" if campaign['status'] == 'Active' else "orange"
                st.markdown(f"""
                ### {campaign['name']} <span style='color:{status_color};font-size:0.8em;'>{campaign['status']}</span>
                **Trigger:** {campaign['trigger']}  
                **Sequence:** {campaign['emails']} emails over {campaign['duration']}  
                **Performance:** {campaign['open_rate']} open rate
                """, unsafe_allow_html=True)
            
            with col2:
                st.write("")
                st.write("")
                if campaign['status'] == 'Active':
                    st.button("Pause Campaign", key=f"pause_{i}")
                else:
                    st.button("Activate Campaign", key=f"activate_{i}")
                st.button("Edit Campaign", key=f"edit_{i}")
            
            st.markdown("---")
    
    # Create a new nurturing campaign
    st.subheader("Create New Nurturing Campaign")
    
    with st.form("create_campaign_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            campaign_name = st.text_input("Campaign Name")
            audience = st.selectbox(
                "Target Audience",
                options=[
                    "All Leads",
                    "New Leads",
                    "Cold Leads",
                    "Warm Leads",
                    "Hot Leads",
                    "Inactive Leads"
                ]
            )
            lead_stage = st.multiselect(
                "Lead Stage",
                options=["New", "Contacted", "Nurturing", "Qualified", "Lost"],
                default=["New", "Contacted"]
            )
        
        with col2:
            property_interest = st.multiselect(
                "Property Interest",
                options=["Single Family", "Condo", "Townhouse", "Multi-Family", "Land", "Commercial"],
                default=[]
            )
            price_range = st.multiselect(
                "Price Range",
                options=["$100k-$200k", "$200k-$300k", "$300k-$500k", "$500k-$750k", "$750k-$1M", "$1M+"],
                default=[]
            )
            duration = st.slider("Campaign Duration (days)", min_value=7, max_value=90, value=30)
        
        # Email sequence setup
        st.subheader("Email Sequence")
        
        num_emails = st.number_input("Number of Emails in Sequence", min_value=1, max_value=10, value=3)
        
        for i in range(int(num_emails)):
            st.write(f"**Email {i+1}**")
            col1, col2 = st.columns(2)
            
            with col1:
                st.text_input(f"Subject Line", key=f"subject_{i}")
                st.number_input(f"Send on Day", min_value=1, max_value=duration, value=i*7+1, key=f"day_{i}")
            
            with col2:
                st.selectbox(
                    f"Email Template",
                    options=[
                        "Property Recommendation",
                        "Market Update",
                        "Buyer's Guide",
                        "Neighborhood Spotlight",
                        "Success Story",
                        "Educational Content",
                        "Personalized Offer"
                    ],
                    key=f"template_{i}"
                )
        
        # AI personalization options
        st.subheader("AI Personalization")
        
        st.checkbox("Enable Dynamic Property Recommendations", value=True)
        st.checkbox("Personalize Email Content Based on Behavior", value=True)
        st.checkbox("Optimize Send Time for Each Recipient", value=True)
        st.checkbox("Automatically Adjust Sequence Based on Engagement", value=True)
        
        submit_button = st.form_submit_button("Create Campaign")
    
    if submit_button:
        if campaign_name:
            st.success(f"Campaign '{campaign_name}' created successfully!")
            
            # Display a sample of the campaign flow
            st.subheader("Campaign Flow Preview")
            
            # Create a Gantt chart to visualize the campaign sequence
            email_tasks = []
            
            for i in range(int(num_emails)):
                day = st.session_state[f"day_{i}"]
                template = st.session_state[f"template_{i}"]
                subject = st.session_state[f"subject_{i}"]
                
                start_date = datetime.now() + timedelta(days=day)
                end_date = start_date + timedelta(days=1)
                
                email_tasks.append({
                    'Task': f"Email {i+1}: {template}",
                    'Start': start_date,
                    'Finish': end_date,
                    'Subject': subject if subject else f"Default Subject for {template}"
                })
            
            # Create a DataFrame for the Gantt chart
            gantt_df = pd.DataFrame(email_tasks)
            
            fig = px.timeline(
                gantt_df,
                x_start='Start',
                x_end='Finish',
                y='Task',
                color='Task',
                hover_data=['Subject'],
                title=f"Email Sequence for '{campaign_name}' Campaign"
            )
            
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
            
            # Projected results
            st.subheader("Projected Campaign Results")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Est. Open Rate", "28-35%")
            
            with col2:
                st.metric("Est. Click Rate", "12-18%")
            
            with col3:
                st.metric("Est. Conversion Rate", "3-5%")
            
            st.info("""
            **Campaign Intelligence:**
            This campaign will automatically adjust based on recipient engagement. Leads who engage with
            earlier emails will receive more customized content in subsequent messages. The AI will also 
            optimize send times based on each lead's past email interaction patterns.
            """)
        else:
            st.error("Please enter a campaign name.")

def calculate_lead_score(source, property_interest, price_range, urgency, website_visits,
                         viewed_listings, saved_properties, requested_showings, pre_approved, credit_score_range):
    """Calculate a lead score based on various factors"""
    # Calculate individual factor scores
    source_score = get_source_score(source)
    property_score = get_property_interest_score(property_interest, price_range)
    urgency_score = get_urgency_score(urgency)
    engagement_score = get_engagement_score(website_visits, viewed_listings, saved_properties)
    showing_score = get_showing_score(requested_showings)
    financial_score = get_financial_score(pre_approved, credit_score_range)
    
    # Weighted sum of factors (customize these weights based on importance)
    score = (source_score * 0.1 +
             property_score * 0.15 +
             urgency_score * 0.25 +
             engagement_score * 0.2 +
             showing_score * 0.2 +
             financial_score * 0.1)
    
    # Ensure score is within 0-100 range
    score = min(max(score, 0), 100)
    
    return round(score)

def get_source_score(source):
    """Score based on lead source quality"""
    source_scores = {
        'Referral': 90,
        'Open House': 80,
        'Direct Mail': 70,
        'Zillow': 65,
        'Realtor.com': 65,
        'Website': 60,
        'Social Media': 50
    }
    return source_scores.get(source, 50)

def get_property_interest_score(property_interest, price_range):
    """Score based on property interest"""
    # Base score from property type
    property_scores = {
        'Single Family': 70,
        'Condo': 65,
        'Townhouse': 65,
        'Multi-Family': 75,
        'Land': 50,
        'Commercial': 80
    }
    
    # Adjust for price range (higher ranges often indicate more serious buyers)
    price_adjustments = {
        '$100k-$200k': 0,
        '$200k-$300k': 5,
        '$300k-$500k': 10,
        '$500k-$750k': 15,
        '$750k-$1M': 20,
        '$1M+': 25
    }
    
    base_score = property_scores.get(property_interest, 60)
    adjusted_score = base_score + price_adjustments.get(price_range, 0)
    
    return min(adjusted_score, 100)

def get_urgency_score(urgency):
    """Score based on buying timeline/urgency"""
    urgency_scores = {
        '0-3 months': 100,
        '3-6 months': 75,
        '6-12 months': 50,
        '12+ months': 25,
        'Just browsing': 10
    }
    return urgency_scores.get(urgency, 30)

def get_engagement_score(website_visits, viewed_listings, saved_properties):
    """Score based on website engagement"""
    # Base score from website visits
    visit_score = min(website_visits * 5, 40)
    
    # Add points for viewed listings
    listing_score = min(viewed_listings * 2, 30)
    
    # Add points for saved properties
    saved_score = min(saved_properties * 5, 30)
    
    # Combined score
    return min(visit_score + listing_score + saved_score, 100)

def get_showing_score(requested_showings):
    """Score based on showing requests (strong buying signal)"""
    # Each showing request is a very strong signal
    return min(requested_showings * 20, 100)

def get_financial_score(pre_approved, credit_score_range):
    """Score based on financial qualification"""
    # Pre-approval status
    if pre_approved == "Yes":
        pre_approval_score = 100
    elif pre_approved == "In Process":
        pre_approval_score = 70
    elif pre_approved == "No":
        pre_approval_score = 30
    else:  # Unknown
        pre_approval_score = 50
    
    # Credit score range
    credit_scores = {
        'Below 620': 20,
        '620-680': 50,
        '680-720': 70,
        '720-760': 85,
        '760+': 100,
        'Unknown': 50
    }
    credit_score = credit_scores.get(credit_score_range, 50)
    
    # Average of pre-approval and credit score
    return (pre_approval_score + credit_score) / 2

def generate_sample_leads(num_leads):
    """Generate sample lead data for demonstration"""
    names = [
        "John Smith", "Emma Johnson", "Michael Brown", "Sophia Davis", "James Wilson",
        "Olivia Martinez", "William Anderson", "Ava Taylor", "Alexander Thomas", "Isabella Jackson",
        "Daniel White", "Mia Harris", "Matthew Martin", "Charlotte Thompson", "Ethan Garcia",
        "Amelia Robinson", "Benjamin Lewis", "Harper Walker", "Sebastian Perez", "Abigail Hall",
        "Gabriel Young", "Elizabeth Allen", "Lucas King", "Sofia Wright", "Logan Scott",
        "Emily Green", "Aiden Baker", "Madison Nelson", "Henry Adams", "Avery Hill"
    ]
    
    sources = ["Website", "Referral", "Zillow", "Realtor.com", "Social Media", "Direct Mail", "Open House"]
    statuses = ["New", "Contacted", "Nurturing", "Qualified", "Converted", "Lost"]
    property_interests = ["Single Family", "Condo", "Townhouse", "Multi-Family", "Land", "Commercial"]
    price_ranges = ["$100k-$200k", "$200k-$300k", "$300k-$500k", "$500k-$750k", "$750k-$1M", "$1M+"]
    
    # Ensure we don't request more names than available
    num_leads = min(num_leads, len(names))
    
    # Generate leads
    leads = []
    
    for i in range(num_leads):
        name = names[i]
        email = f"{name.lower().replace(' ', '.')}@example.com"
        phone = f"555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
        
        source = random.choice(sources)
        status = random.choice(statuses)
        lead_score = random.randint(10, 100)
        
        # Generate a random date within the last 60 days
        days_ago = random.randint(1, 60)
        created_at = datetime.now() - timedelta(days=days_ago)
        
        # Response time (in hours)
        response_time_hours = random.randint(0, 48)
        
        # Last activity
        activities = ["Email sent", "Call made", "Property viewed", "Meeting scheduled", "Note added"]
        last_activity = random.choice(activities)
        
        # Property interests
        property_interest = random.choice(property_interests)
        price_range = random.choice(price_ranges)
        
        leads.append({
            'name': name,
            'email': email,
            'phone': phone,
            'status': status,
            'source': source,
            'lead_score': lead_score,
            'created_at': created_at,
            'response_time_hours': response_time_hours,
            'last_activity': last_activity,
            'property_interest': property_interest,
            'price_range': price_range
        })
    
    return pd.DataFrame(leads)