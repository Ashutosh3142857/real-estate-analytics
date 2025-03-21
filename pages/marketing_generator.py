import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import random
from datetime import datetime, timedelta

def show_marketing_generator():
    st.title("AI-Powered Hyperlocal Real Estate Marketing")
    
    st.markdown("""
    Generate optimized, targeted marketing content for your real estate listings.
    Our AI analyzes property details, local market trends, and target audience preferences to create
    compelling marketing materials that highlight the most attractive features of each property.
    """)
    
    # Get data from session state
    if 'data' not in st.session_state:
        st.error("No property data available. Please return to the dashboard.")
        return
    
    data = st.session_state.data
    
    # Create tabs for different marketing content types
    tab1, tab2, tab3, tab4 = st.tabs([
        "Property Listing Description", 
        "Social Media Posts", 
        "Email Campaigns",
        "Ad Performance Analytics"
    ])
    
    with tab1:
        show_listing_description_generator(data)
    
    with tab2:
        show_social_media_generator(data)
    
    with tab3:
        show_email_campaign_generator(data)
    
    with tab4:
        show_ad_performance_analytics()

def show_listing_description_generator(data):
    st.subheader("AI Listing Description Generator")
    
    st.markdown("""
    Generate compelling property descriptions that highlight key features and selling points.
    Our AI analyzes the property details and creates SEO-optimized content for maximum impact.
    """)
    
    # Property selection
    col1, col2 = st.columns(2)
    
    with col1:
        # Select a property from the dataset
        selected_property = st.selectbox(
            "Select a Property",
            options=data['property_id'].tolist(),
            format_func=lambda x: f"ID: {x} - {data[data['property_id'] == x]['address'].values[0]}"
        )
    
    # Get the selected property details
    property_details = data[data['property_id'] == selected_property].iloc[0]
    
    with col2:
        # Listing description style
        description_style = st.selectbox(
            "Description Style",
            options=[
                "Professional & Formal",
                "Warm & Inviting",
                "Luxury & Upscale",
                "Modern & Urban",
                "Family-Friendly",
                "Investment-Focused"
            ]
        )
    
    # Target audience selection
    target_audience = st.multiselect(
        "Target Audience",
        options=[
            "First-time Homebuyers",
            "Families with Children",
            "Retirees/Downsizers",
            "Investors",
            "Luxury Buyers",
            "Urban Professionals"
        ],
        default=["First-time Homebuyers"]
    )
    
    # Key features to highlight
    st.subheader("Key Features to Highlight")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        highlight_location = st.checkbox("Location", value=True)
        highlight_size = st.checkbox("Size & Layout", value=True)
    
    with col2:
        highlight_features = st.checkbox("Property Features", value=True)
        highlight_outdoor = st.checkbox("Outdoor Space", value=False)
    
    with col3:
        highlight_investment = st.checkbox("Investment Potential", value=False)
        highlight_neighborhood = st.checkbox("Neighborhood", value=False)
    
    # Property image
    st.image(
        "https://img.icons8.com/fluency/96/000000/real-estate.png", 
        width=100,
        caption=property_details['address']
    )
    
    # Display property details
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Address:** {property_details['address']}")
        st.write(f"**City:** {property_details['city']}")
        st.write(f"**Price:** ${property_details['price']:,.0f}")
    
    with col2:
        st.write(f"**Bedrooms:** {property_details['bedrooms']}")
        st.write(f"**Bathrooms:** {property_details['bathrooms']}")
        st.write(f"**Square Footage:** {property_details['sqft']:,}")
    
    # Generate button
    if st.button("Generate Listing Description"):
        # Generate description based on property details and selected options
        description = generate_property_description(
            property_details, 
            description_style, 
            target_audience,
            highlight_location,
            highlight_size,
            highlight_features,
            highlight_outdoor,
            highlight_investment,
            highlight_neighborhood
        )
        
        # Display the generated description
        st.subheader("Generated Listing Description")
        st.markdown(f"**{description['headline']}**")
        st.write(description['body'])
        
        # Copy button
        if st.button("Copy to Clipboard"):
            st.success("Description copied to clipboard!")
        
        # SEO analysis
        st.subheader("SEO Analysis")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Word Count", f"{len(description['body'].split())}")
        
        with col2:
            st.metric("SEO Score", f"{random.randint(85, 98)}/100")
        
        with col3:
            st.metric("Readability", "Good")
        
        # SEO recommendations
        st.markdown("""
        **SEO Recommendations:**
        - Add more details about the neighborhood amenities
        - Include nearby schools and their ratings
        - Mention recent upgrades or renovations
        """)

def show_social_media_generator(data):
    st.subheader("Social Media Content Generator")
    
    st.markdown("""
    Create engaging social media posts for your listings across multiple platforms.
    Our AI generates platform-specific content optimized for maximum engagement.
    """)
    
    # Property selection
    selected_property = st.selectbox(
        "Select a Property",
        options=data['property_id'].tolist(),
        format_func=lambda x: f"ID: {x} - {data[data['property_id'] == x]['address'].values[0]}",
        key="social_media_property"
    )
    
    # Get the selected property details
    property_details = data[data['property_id'] == selected_property].iloc[0]
    
    # Platform selection
    platforms = st.multiselect(
        "Select Platforms",
        options=["Facebook", "Instagram", "Twitter", "LinkedIn"],
        default=["Facebook", "Instagram"]
    )
    
    # Content style
    content_style = st.select_slider(
        "Content Style",
        options=["Informative", "Engaging", "Visual", "Story-based"],
        value="Engaging"
    )
    
    # Include options
    col1, col2 = st.columns(2)
    
    with col1:
        include_photos = st.checkbox("Include Photo Suggestions", value=True)
        include_hashtags = st.checkbox("Include Hashtags", value=True)
    
    with col2:
        include_call_to_action = st.checkbox("Include Call to Action", value=True)
        include_questions = st.checkbox("Include Engagement Questions", value=True)
    
    # Generate button
    if st.button("Generate Social Media Content"):
        # Generate content for each selected platform
        for platform in platforms:
            st.subheader(f"{platform} Post")
            
            post_content = generate_social_media_post(
                property_details,
                platform,
                content_style,
                include_photos,
                include_hashtags,
                include_call_to_action,
                include_questions
            )
            
            # Display the generated content
            with st.container():
                st.markdown(f"**{post_content['headline']}**")
                st.write(post_content['body'])
                
                if include_hashtags and 'hashtags' in post_content:
                    st.write(post_content['hashtags'])
                
                if include_photos and 'photo_suggestion' in post_content:
                    st.info(post_content['photo_suggestion'])
                
                # Engagement metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Est. Reach", f"{random.randint(500, 5000):,}")
                
                with col2:
                    st.metric("Est. Engagement", f"{random.randint(1, 10)}%")
                
                with col3:
                    if platform == "Facebook" or platform == "Instagram":
                        metric_name = "Est. Likes"
                    elif platform == "Twitter":
                        metric_name = "Est. Retweets"
                    else:  # LinkedIn
                        metric_name = "Est. Interactions"
                    
                    st.metric(metric_name, f"{random.randint(10, 200)}")
            
            st.markdown("---")
        
        # Best posting times
        st.subheader("Recommended Posting Schedule")
        
        posting_schedule = {
            "Facebook": "Tuesday or Thursday, 1-3 PM",
            "Instagram": "Wednesday, 11 AM or 2 PM",
            "Twitter": "Wednesday or Friday, 9 AM",
            "LinkedIn": "Tuesday through Thursday, 10-11 AM"
        }
        
        for platform in platforms:
            st.write(f"**{platform}:** {posting_schedule.get(platform, 'Anytime')}")

def show_email_campaign_generator(data):
    st.subheader("Email Campaign Generator")
    
    st.markdown("""
    Create targeted email campaigns for different segments of your client base.
    Our AI generates personalized email content that drives engagement and conversions.
    """)
    
    # Campaign type selection
    campaign_type = st.selectbox(
        "Campaign Type",
        options=[
            "New Listing Announcement",
            "Open House Invitation",
            "Price Reduction Alert",
            "Market Update Newsletter",
            "Just Sold Announcement",
            "Buyer/Seller Tips",
            "Neighborhood Spotlight"
        ]
    )
    
    # Recipient segment
    recipient_segment = st.selectbox(
        "Recipient Segment",
        options=[
            "All Clients",
            "Past Buyers",
            "Current Sellers",
            "Potential Buyers",
            "Investors",
            "First-time Homebuyers",
            "Luxury Market Clients"
        ]
    )
    
    # Property selection (for property-specific campaigns)
    if campaign_type in ["New Listing Announcement", "Open House Invitation", "Price Reduction Alert", "Just Sold Announcement"]:
        selected_property = st.selectbox(
            "Select a Property",
            options=data['property_id'].tolist(),
            format_func=lambda x: f"ID: {x} - {data[data['property_id'] == x]['address'].values[0]}",
            key="email_property"
        )
        
        property_details = data[data['property_id'] == selected_property].iloc[0]
    else:
        property_details = None
    
    # Email customization
    st.subheader("Email Customization")
    
    col1, col2 = st.columns(2)
    
    with col1:
        sender_name = st.text_input("Sender Name", value="Your Name")
        email_subject_prefix = st.text_input("Email Subject Prefix", value="")
    
    with col2:
        include_personal_note = st.checkbox("Include Personal Note", value=True)
        include_market_stats = st.checkbox("Include Market Statistics", value=True)
    
    # Additional content
    include_testimonials = st.checkbox("Include Client Testimonials", value=True)
    
    # For open house, we need date and time
    if campaign_type == "Open House Invitation":
        st.subheader("Open House Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            open_house_date = st.date_input("Open House Date", datetime.now() + timedelta(days=7))
        
        with col2:
            open_house_time = st.time_input("Open House Time")
    
    # Generate button
    if st.button("Generate Email Campaign"):
        # Generate email content
        email_content = generate_email_campaign(
            campaign_type,
            recipient_segment,
            property_details,
            sender_name,
            email_subject_prefix,
            include_personal_note,
            include_market_stats,
            include_testimonials
        )
        
        # Add open house details if applicable
        if campaign_type == "Open House Invitation":
            open_house_datetime = f"{open_house_date.strftime('%A, %B %d, %Y')} at {open_house_time.strftime('%I:%M %p')}"
            email_content['body'] = email_content['body'].replace("[OPEN_HOUSE_DATE_TIME]", open_house_datetime)
        
        # Display the generated email
        st.subheader("Generated Email")
        
        # Email preview container
        with st.container():
            st.markdown(f"**From:** {sender_name}")
            st.markdown(f"**To:** {recipient_segment}")
            st.markdown(f"**Subject:** {email_content['subject']}")
            st.markdown("---")
            st.markdown(email_content['body'], unsafe_allow_html=True)
        
        # Email performance metrics
        st.subheader("Projected Email Performance")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Est. Open Rate", f"{random.randint(15, 35)}%")
        
        with col2:
            st.metric("Est. Click Rate", f"{random.randint(2, 10)}%")
        
        with col3:
            st.metric("Est. Response Rate", f"{random.randint(1, 5)}%")
        
        with col4:
            st.metric("Est. Unsubscribe Rate", f"{random.uniform(0.1, 0.5):.1f}%")
        
        # Send options
        st.subheader("Sending Options")
        
        col1, col2 = st.columns(2)
        
        with col1:
            num_recipients = st.number_input("Number of Recipients", min_value=1, value=100)
            
            # Schedule send
            schedule_send = st.checkbox("Schedule Send", value=False)
            
            if schedule_send:
                send_date = st.date_input("Send Date", datetime.now() + timedelta(days=1))
                send_time = st.time_input("Send Time", datetime.now().time())
        
        with col2:
            st.write("**A/B Testing Options:**")
            ab_testing = st.checkbox("Enable A/B Testing", value=False)
            
            if ab_testing:
                test_variable = st.selectbox(
                    "Test Variable",
                    options=["Subject Line", "Sender Name", "Content", "Call to Action"]
                )
                
                test_size = st.slider("Test Size (% of Recipients)", 10, 50, 20)
        
        # Send button
        if st.button("Prepare to Send"):
            if schedule_send:
                st.success(f"Email campaign prepared and scheduled for {send_date.strftime('%B %d, %Y')} at {send_time.strftime('%I:%M %p')}")
            else:
                st.success(f"Email campaign prepared and ready to send to {num_recipients} recipients")

def show_ad_performance_analytics():
    st.subheader("Marketing Performance Analytics")
    
    st.markdown("""
    Track and analyze the performance of your real estate marketing campaigns.
    Optimize your marketing strategy based on data-driven insights.
    """)
    
    # Generate sample marketing performance data
    if 'marketing_data' not in st.session_state:
        st.session_state.marketing_data = generate_marketing_data()
    
    marketing_data = st.session_state.marketing_data
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        date_range = st.selectbox(
            "Date Range",
            options=["Last 7 Days", "Last 30 Days", "Last 90 Days", "Year to Date", "All Time"],
            index=1
        )
    
    with col2:
        channel_filter = st.multiselect(
            "Marketing Channels",
            options=marketing_data['channel'].unique(),
            default=marketing_data['channel'].unique()
        )
    
    with col3:
        metric_view = st.selectbox(
            "Primary Metric",
            options=["Impressions", "Clicks", "Inquiries", "Cost", "ROI"]
        )
    
    # Filter data based on selections
    filtered_marketing = marketing_data.copy()
    
    if channel_filter:
        filtered_marketing = filtered_marketing[filtered_marketing['channel'].isin(channel_filter)]
    
    # Apply date filter
    today = datetime.now()
    if date_range == "Last 7 Days":
        start_date = today - timedelta(days=7)
        filtered_marketing = filtered_marketing[filtered_marketing['date'] >= start_date]
    elif date_range == "Last 30 Days":
        start_date = today - timedelta(days=30)
        filtered_marketing = filtered_marketing[filtered_marketing['date'] >= start_date]
    elif date_range == "Last 90 Days":
        start_date = today - timedelta(days=90)
        filtered_marketing = filtered_marketing[filtered_marketing['date'] >= start_date]
    elif date_range == "Year to Date":
        start_date = datetime(today.year, 1, 1)
        filtered_marketing = filtered_marketing[filtered_marketing['date'] >= start_date]
    
    # Key performance metrics
    st.subheader("Key Performance Metrics")
    
    # Calculate metrics
    total_impressions = filtered_marketing['impressions'].sum()
    total_clicks = filtered_marketing['clicks'].sum()
    total_inquiries = filtered_marketing['inquiries'].sum()
    total_cost = filtered_marketing['cost'].sum()
    
    # Calculate derived metrics
    ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
    cpc = (total_cost / total_clicks) if total_clicks > 0 else 0
    cpl = (total_cost / total_inquiries) if total_inquiries > 0 else 0
    inquiry_rate = (total_inquiries / total_clicks * 100) if total_clicks > 0 else 0
    
    # Estimated ROI (assuming 3% of inquiries convert to sales with average $5k commission)
    estimated_sales = total_inquiries * 0.03
    estimated_revenue = estimated_sales * 5000
    roi = ((estimated_revenue - total_cost) / total_cost * 100) if total_cost > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Impressions", f"{total_impressions:,}")
        st.metric("Click-Through Rate", f"{ctr:.2f}%")
    
    with col2:
        st.metric("Clicks", f"{total_clicks:,}")
        st.metric("Cost per Click", f"${cpc:.2f}")
    
    with col3:
        st.metric("Inquiries", f"{total_inquiries:,}")
        st.metric("Inquiry Rate", f"{inquiry_rate:.2f}%")
    
    with col4:
        st.metric("Total Cost", f"${total_cost:,.2f}")
        st.metric("Est. ROI", f"{roi:.2f}%")
    
    # Performance by channel
    st.subheader("Performance by Marketing Channel")
    
    # Aggregate data by channel
    channel_performance = filtered_marketing.groupby('channel').agg({
        'impressions': 'sum',
        'clicks': 'sum',
        'inquiries': 'sum',
        'cost': 'sum'
    }).reset_index()
    
    # Calculate CTR and CPC for each channel
    channel_performance['ctr'] = (channel_performance['clicks'] / channel_performance['impressions'] * 100).fillna(0)
    channel_performance['cpc'] = (channel_performance['cost'] / channel_performance['clicks']).fillna(0)
    channel_performance['inquiry_rate'] = (channel_performance['inquiries'] / channel_performance['clicks'] * 100).fillna(0)
    
    # Estimate ROI
    channel_performance['estimated_sales'] = channel_performance['inquiries'] * 0.03
    channel_performance['estimated_revenue'] = channel_performance['estimated_sales'] * 5000
    channel_performance['roi'] = ((channel_performance['estimated_revenue'] - channel_performance['cost']) / 
                                 channel_performance['cost'] * 100).fillna(0)
    
    # Create visualization based on selected metric
    if metric_view == "Impressions":
        fig = px.bar(
            channel_performance,
            x='channel',
            y='impressions',
            color='ctr',
            color_continuous_scale=px.colors.sequential.Viridis,
            title='Impressions by Channel',
            labels={'channel': 'Channel', 'impressions': 'Impressions', 'ctr': 'CTR (%)'},
            text_auto=True
        )
    elif metric_view == "Clicks":
        fig = px.bar(
            channel_performance,
            x='channel',
            y='clicks',
            color='cpc',
            color_continuous_scale=px.colors.sequential.Viridis,
            title='Clicks by Channel',
            labels={'channel': 'Channel', 'clicks': 'Clicks', 'cpc': 'CPC ($)'},
            text_auto=True
        )
    elif metric_view == "Inquiries":
        fig = px.bar(
            channel_performance,
            x='channel',
            y='inquiries',
            color='inquiry_rate',
            color_continuous_scale=px.colors.sequential.Viridis,
            title='Inquiries by Channel',
            labels={'channel': 'Channel', 'inquiries': 'Inquiries', 'inquiry_rate': 'Inquiry Rate (%)'},
            text_auto=True
        )
    elif metric_view == "Cost":
        fig = px.bar(
            channel_performance,
            x='channel',
            y='cost',
            color='cpc',
            color_continuous_scale=px.colors.sequential.Viridis,
            title='Marketing Cost by Channel',
            labels={'channel': 'Channel', 'cost': 'Cost ($)', 'cpc': 'CPC ($)'},
            text_auto=True
        )
    else:  # ROI
        fig = px.bar(
            channel_performance,
            x='channel',
            y='roi',
            color='roi',
            color_continuous_scale=px.colors.sequential.Viridis,
            title='ROI by Channel',
            labels={'channel': 'Channel', 'roi': 'ROI (%)'},
            text_auto=True
        )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Performance over time
    st.subheader("Performance Trends")
    
    # Aggregate data by date and channel
    daily_performance = filtered_marketing.groupby(['date', 'channel']).agg({
        'impressions': 'sum',
        'clicks': 'sum',
        'inquiries': 'sum',
        'cost': 'sum'
    }).reset_index()
    
    # Create time series visualization
    metric_mapping = {
        "Impressions": "impressions",
        "Clicks": "clicks", 
        "Inquiries": "inquiries",
        "Cost": "cost",
        "ROI": "roi"  # We'll handle this special case separately
    }
    
    y_column = metric_mapping[metric_view]
    
    if y_column == "roi":
        # Need to calculate ROI first
        daily_performance['estimated_sales'] = daily_performance['inquiries'] * 0.03
        daily_performance['estimated_revenue'] = daily_performance['estimated_sales'] * 5000
        daily_performance['roi'] = ((daily_performance['estimated_revenue'] - daily_performance['cost']) / 
                                   daily_performance['cost'] * 100).fillna(0)
    
    fig = px.line(
        daily_performance,
        x='date',
        y=y_column,
        color='channel',
        title=f'{metric_view} Over Time by Channel',
        labels={'date': 'Date', y_column: metric_view},
        template='plotly_white'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Campaign recommendations
    st.subheader("AI-Generated Marketing Recommendations")
    
    # Find best and worst performing channels based on ROI
    best_channel = channel_performance.loc[channel_performance['roi'].idxmax()]
    worst_channel = channel_performance.loc[channel_performance['roi'].idxmin()]
    
    st.info(f"""
    **Based on your marketing performance data, here are our AI-generated recommendations:**
    
    1. **Budget Allocation:** Increase investment in {best_channel['channel']} which shows the highest ROI at {best_channel['roi']:.2f}%.
    
    2. **Strategy Adjustment:** Review your approach for {worst_channel['channel']} which has the lowest ROI at {worst_channel['roi']:.2f}%.
    
    3. **Content Optimization:** Focus on highlighting property features that generate the most engagement.
    
    4. **Audience Targeting:** Refine your audience targeting to improve the inquiry rate across all channels.
    
    5. **Testing:** Implement A/B testing of ad creatives and messages to identify what resonates best with your audience.
    """)
    
    # Campaign planning
    st.subheader("AI-Powered Campaign Planning")
    
    col1, col2 = st.columns(2)
    
    with col1:
        budget = st.number_input("Monthly Marketing Budget ($)", min_value=100, value=2000, step=100)
    
    with col2:
        goal = st.selectbox(
            "Primary Campaign Goal",
            options=["Maximize Inquiries", "Maximize Brand Awareness", "Optimize ROI", "Promote Specific Listings"]
        )
    
    if st.button("Generate Optimal Campaign Plan"):
        # Calculate budget allocation based on performance
        if channel_performance.empty:
            st.error("No data available for campaign planning.")
        else:
            # For ROI optimization, allocate more to higher ROI channels
            if goal == "Optimize ROI":
                channel_performance['allocation_weight'] = channel_performance['roi'].clip(lower=1)
            
            # For inquiries, allocate based on inquiry performance
            elif goal == "Maximize Inquiries":
                channel_performance['allocation_weight'] = (channel_performance['inquiries'] / channel_performance['cost']).clip(lower=0.01)
            
            # For awareness, allocate based on impression performance
            elif goal == "Maximize Brand Awareness":
                channel_performance['allocation_weight'] = (channel_performance['impressions'] / channel_performance['cost']).clip(lower=0.01)
            
            # For specific listings, equal distribution
            else:
                channel_performance['allocation_weight'] = 1
            
            # Normalize weights to sum to 1
            total_weight = channel_performance['allocation_weight'].sum()
            if total_weight > 0:
                channel_performance['allocation_weight'] = channel_performance['allocation_weight'] / total_weight
            else:
                channel_performance['allocation_weight'] = 1 / len(channel_performance)
            
            # Calculate budget allocation
            channel_performance['budget_allocation'] = channel_performance['allocation_weight'] * budget
            
            # Display budget allocation
            st.subheader("Recommended Budget Allocation")
            
            # Create a pie chart
            fig = px.pie(
                channel_performance,
                values='budget_allocation',
                names='channel',
                title=f'Optimized Budget Allocation for {goal}',
                template='plotly_white',
                hole=0.4
            )
            
            # Add currency formatting to values
            fig.update_traces(
                texttemplate='%{label}: $%{value:.0f}',
                textposition='inside'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Display allocation table
            st.write("**Detailed Budget Allocation:**")
            
            allocation_df = channel_performance[['channel', 'budget_allocation']].copy()
            allocation_df['budget_allocation'] = allocation_df['budget_allocation'].map('${:,.2f}'.format)
            allocation_df.columns = ['Channel', 'Recommended Budget']
            
            st.table(allocation_df)
            
            # Campaign calendar
            st.subheader("Monthly Campaign Calendar")
            
            # Create a calendar visualization
            today = datetime.now()
            month_start = datetime(today.year, today.month, 1)
            next_month = month_start.replace(day=28) + timedelta(days=4)
            month_end = next_month - timedelta(days=next_month.day)
            
            days = (month_end - month_start).days + 1
            
            # Generate some campaign events
            events = []
            
            # Add some Facebook posts
            for _ in range(4):
                day = random.randint(1, days)
                event_date = month_start + timedelta(days=day-1)
                events.append({
                    'date': event_date,
                    'channel': 'Facebook',
                    'activity': 'Property Post',
                    'details': 'Featured property post with photos and video'
                })
            
            # Add some Google Ads
            for _ in range(2):
                day = random.randint(1, days)
                event_date = month_start + timedelta(days=day-1)
                events.append({
                    'date': event_date,
                    'channel': 'Google Ads',
                    'activity': 'Campaign Start',
                    'details': 'Start new search campaign for high-value properties'
                })
            
            # Add some Instagram posts
            for _ in range(6):
                day = random.randint(1, days)
                event_date = month_start + timedelta(days=day-1)
                events.append({
                    'date': event_date,
                    'channel': 'Instagram',
                    'activity': 'Story + Post',
                    'details': 'Property highlight with virtual tour link'
                })
            
            # Add email campaigns
            for _ in range(2):
                day = random.randint(1, days)
                event_date = month_start + timedelta(days=day-1)
                events.append({
                    'date': event_date,
                    'channel': 'Email',
                    'activity': 'Newsletter',
                    'details': 'Monthly market update and featured properties'
                })
            
            # Convert to DataFrame and sort by date
            events_df = pd.DataFrame(events)
            events_df = events_df.sort_values('date')
            
            # Display events
            for _, event in events_df.iterrows():
                date_str = event['date'].strftime('%A, %B %d')
                st.write(f"**{date_str}:** {event['channel']} - {event['activity']} ({event['details']})")

def generate_property_description(property_details, style, audience, highlight_location=True, 
                               highlight_size=True, highlight_features=True, highlight_outdoor=False,
                               highlight_investment=False, highlight_neighborhood=False):
    """Generate a property description based on details and preferences"""
    # Property basics
    address = property_details['address']
    city = property_details['city']
    bedrooms = property_details['bedrooms']
    bathrooms = property_details['bathrooms']
    sqft = property_details['sqft']
    price = property_details['price']
    property_type = property_details['property_type']
    year_built = property_details['year_built']
    
    # Generate headline based on style
    if style == "Professional & Formal":
        headline = f"Exceptional {bedrooms} Bedroom {property_type} in {city}"
    elif style == "Warm & Inviting":
        headline = f"Charming {bedrooms} Bedroom {property_type} - Your Dream Home Awaits!"
    elif style == "Luxury & Upscale":
        headline = f"Exquisite {bedrooms} Bedroom {property_type} in Prestigious {city}"
    elif style == "Modern & Urban":
        headline = f"Stylish {bedrooms} Bedroom {property_type} in the Heart of {city}"
    elif style == "Family-Friendly":
        headline = f"Perfect Family {property_type} with {bedrooms} Bedrooms in {city}"
    else:  # Investment-Focused
        headline = f"High-Potential {bedrooms} Bedroom {property_type} Investment in {city}"
    
    # Generate description paragraphs
    paragraphs = []
    
    # Introduction
    if style == "Professional & Formal":
        intro = f"Presenting this immaculate {bedrooms} bedroom, {bathrooms} bathroom {property_type.lower()} situated in {city}. Built in {year_built}, this {sqft:,} square foot residence offers exceptional quality and value at ${price:,}."
    elif style == "Warm & Inviting":
        intro = f"Welcome home to this beautiful {bedrooms} bedroom, {bathrooms} bathroom {property_type.lower()} nestled in {city}. With {sqft:,} square feet of living space, this charming home built in {year_built} offers the perfect blend of comfort and style for ${price:,}."
    elif style == "Luxury & Upscale":
        intro = f"Experience luxury living in this magnificent {bedrooms} bedroom, {bathrooms} bathroom {property_type.lower()} in prestigious {city}. Constructed in {year_built}, this opulent {sqft:,} square foot estate represents sophisticated design and premium craftsmanship at ${price:,}."
    elif style == "Modern & Urban":
        intro = f"Discover urban sophistication in this contemporary {bedrooms} bedroom, {bathrooms} bathroom {property_type.lower()} in vibrant {city}. Featuring {sqft:,} square feet of thoughtfully designed space, this {year_built} property embodies modern living at ${price:,}."
    elif style == "Family-Friendly":
        intro = f"The perfect family home awaits with this wonderful {bedrooms} bedroom, {bathrooms} bathroom {property_type.lower()} in {city}. Offering {sqft:,} square feet of functional living space, this {year_built} home provides room for everyone and everything at ${price:,}."
    else:  # Investment-Focused
        intro = f"Outstanding investment opportunity in {city} with this well-positioned {bedrooms} bedroom, {bathrooms} bathroom {property_type.lower()}. Built in {year_built} and offering {sqft:,} square feet, this property presents excellent potential for returns with an asking price of ${price:,}."
    
    paragraphs.append(intro)
    
    # Location paragraph
    if highlight_location:
        if style == "Professional & Formal":
            location = f"Situated in a prime location in {city}, this property offers convenient access to major transportation routes, business districts, and amenities."
        elif style == "Warm & Inviting":
            location = f"Located in a friendly neighborhood in {city}, you'll love being close to local shops, parks, and community amenities."
        elif style == "Luxury & Upscale":
            location = f"Set in one of {city}'s most coveted locations, this address offers prestige and proximity to upscale dining, boutique shopping, and cultural attractions."
        elif style == "Modern & Urban":
            location = f"Centrally located in {city}, this property puts you steps from trendy restaurants, cafes, entertainment venues, and urban conveniences."
        elif style == "Family-Friendly":
            location = f"Nestled in a safe, family-oriented neighborhood in {city}, you'll appreciate the nearby schools, parks, recreational facilities, and family-friendly amenities."
        else:  # Investment-Focused
            location = f"Strategically located in a growing area of {city}, this property benefits from strong rental demand, appreciated value trends, and development in the surrounding area."
        
        paragraphs.append(location)
    
    # Size and layout paragraph
    if highlight_size:
        if style == "Professional & Formal":
            size = f"The property features a practical layout with {bedrooms} well-proportioned bedrooms, {bathrooms} bathrooms, and {sqft:,} square feet of living space optimized for comfort and functionality."
        elif style == "Warm & Inviting":
            size = f"You'll feel right at home in this cozy yet spacious layout featuring {bedrooms} comfortable bedrooms, {bathrooms} bathrooms, and {sqft:,} square feet of welcoming living space."
        elif style == "Luxury & Upscale":
            size = f"An expansive floor plan encompasses {bedrooms} generously sized bedrooms, {bathrooms} luxurious bathrooms, and {sqft:,} square feet of meticulously designed living space with premium finishes throughout."
        elif style == "Modern & Urban":
            size = f"The thoughtfully designed interior offers {bedrooms} stylish bedrooms, {bathrooms} contemporary bathrooms, and {sqft:,} square feet of efficient, open-concept living space perfect for modern lifestyles."
        elif style == "Family-Friendly":
            size = f"Growing families will appreciate the spacious layout featuring {bedrooms} comfortable bedrooms, {bathrooms} convenient bathrooms, and {sqft:,} square feet with plenty of space for family activities and gatherings."
        else:  # Investment-Focused
            size = f"The property's practical configuration includes {bedrooms} bedrooms, {bathrooms} bathrooms, and {sqft:,} square feet - an optimal layout for attracting quality tenants and maximizing rental income."
        
        paragraphs.append(size)
    
    # Features paragraph - generic since we don't have detailed feature data
    if highlight_features:
        if style == "Professional & Formal":
            features = "The residence showcases quality features including updated appliances, durable flooring, and energy-efficient fixtures throughout."
        elif style == "Warm & Inviting":
            features = "You'll love the home's charming details, from the inviting kitchen with quality appliances to the comfortable living areas perfect for relaxing and entertaining."
        elif style == "Luxury & Upscale":
            features = "Indulge in premium amenities including high-end kitchen appliances, custom cabinetry, luxury fixtures, and designer finishes that define sophisticated living."
        elif style == "Modern & Urban":
            features = "Contemporary features abound, including sleek finishes, integrated technology, and stylish fixtures that complement today's urban lifestyle."
        elif style == "Family-Friendly":
            features = "Family-friendly features include a spacious kitchen, versatile living areas, ample storage, and practical amenities designed with everyday family living in mind."
        else:  # Investment-Focused
            features = "The property includes desirable rental features such as updated appliances, durable finishes, and low-maintenance design elements that appeal to quality tenants."
        
        paragraphs.append(features)
    
    # Outdoor space paragraph - if requested
    if highlight_outdoor:
        if style == "Professional & Formal":
            outdoor = "The exterior space offers a well-maintained setting with practical landscaping and appropriate outdoor amenities."
        elif style == "Warm & Inviting":
            outdoor = "Step outside to enjoy the lovely outdoor space, perfect for relaxing or entertaining family and friends in your private retreat."
        elif style == "Luxury & Upscale":
            outdoor = "The exquisite grounds complement the interior luxury, featuring sophisticated landscaping and premium outdoor living amenities."
        elif style == "Modern & Urban":
            outdoor = "The thoughtfully designed outdoor space provides an urban oasis with contemporary landscaping and stylish amenities."
        elif style == "Family-Friendly":
            outdoor = "The family-friendly yard offers plenty of space for children to play, pets to roam, and adults to relax and entertain."
        else:  # Investment-Focused
            outdoor = "The low-maintenance exterior enhances the property's appeal to tenants while minimizing ongoing maintenance costs."
        
        paragraphs.append(outdoor)
    
    # Investment potential paragraph - if requested
    if highlight_investment:
        if style == "Investment-Focused":
            investment = f"This property presents exceptional investment potential with strong rental demand in {city}, projected appreciation, and attractive cash flow opportunities. Comparable properties in the area command monthly rents that provide competitive returns on investment."
        else:
            investment = f"Beyond being a wonderful place to live, this property also offers solid investment value in the growing {city} market, with strong potential for appreciation and rental income should you consider it as an investment in the future."
        
        paragraphs.append(investment)
    
    # Neighborhood paragraph - if requested
    if highlight_neighborhood:
        if style == "Professional & Formal":
            neighborhood = f"The neighborhood offers a professional atmosphere with convenient access to business centers, retail establishments, and essential services."
        elif style == "Warm & Inviting":
            neighborhood = f"You'll love the friendly neighborhood atmosphere with community parks, local shops, and welcoming neighbors that make this area so special."
        elif style == "Luxury & Upscale":
            neighborhood = f"The prestigious surroundings feature upscale amenities, fine dining establishments, boutique shopping, and cultural attractions befitting the discerning resident."
        elif style == "Modern & Urban":
            neighborhood = f"The vibrant neighborhood puts you at the center of urban life with trending restaurants, artisan coffee shops, cultural venues, and contemporary conveniences just steps away."
        elif style == "Family-Friendly":
            neighborhood = f"Families appreciate this safe, established neighborhood with top-rated schools, community parks, recreational facilities, and family-oriented services nearby."
        else:  # Investment-Focused
            neighborhood = f"The surrounding area shows strong economic indicators with employment growth, infrastructure development, and increasing property values that support a positive investment outlook."
        
        paragraphs.append(neighborhood)
    
    # Target audience specific closing
    if "First-time Homebuyers" in audience:
        closing = "This property represents an excellent opportunity for first-time homebuyers looking to establish themselves in the real estate market with a quality home that offers both comfort and value."
    elif "Families with Children" in audience:
        closing = "Families will appreciate how this home accommodates both everyday living and special moments, with space for children to grow and convenient access to schools and family amenities."
    elif "Retirees/Downsizers" in audience:
        closing = "This property offers the perfect blend of comfort, convenience, and low-maintenance living that appeals to those looking to rightsize their lifestyle without sacrificing quality."
    elif "Investors" in audience:
        closing = "Investors will recognize the significant potential this property offers, with strong rental demand, value appreciation prospects, and the opportunity for impressive returns."
    elif "Luxury Buyers" in audience:
        closing = "Discerning buyers who appreciate refined living will find this property meets their expectations for quality, sophistication, and prestige in the competitive luxury market."
    else:  # Urban Professionals
        closing = "This property perfectly complements the dynamic lifestyle of urban professionals, offering a sophisticated living space in a location that balances work accessibility with lifestyle amenities."
    
    paragraphs.append(closing)
    
    # Call to action
    cta = f"Schedule your private viewing today to experience everything this exceptional property has to offer."
    paragraphs.append(cta)
    
    # Join paragraphs with line breaks
    body = "\n\n".join(paragraphs)
    
    return {
        'headline': headline,
        'body': body
    }

def generate_social_media_post(property_details, platform, style, include_photos, 
                            include_hashtags, include_call_to_action, include_questions):
    """Generate social media content based on platform and preferences"""
    # Property basics
    address = property_details['address']
    city = property_details['city']
    bedrooms = property_details['bedrooms']
    bathrooms = property_details['bathrooms']
    sqft = property_details['sqft']
    price = property_details['price']
    property_type = property_details['property_type']
    
    # Generate headline
    if platform == "Facebook":
        headline = f"JUST LISTED: Stunning {bedrooms} Bed, {bathrooms} Bath {property_type} in {city}"
    elif platform == "Instagram":
        headline = f"✨ Gorgeous {bedrooms}BD/{bathrooms}BA {property_type} in {city} ✨"
    elif platform == "Twitter":
        headline = f"New Listing Alert! {bedrooms}bd/{bathrooms}ba {property_type} in {city} for ${price:,}"
    else:  # LinkedIn
        headline = f"New Real Estate Opportunity: {bedrooms} Bedroom {property_type} in {city}"
    
    # Generate body content based on platform, style and property
    if platform == "Facebook":
        if style == "Informative":
            body = f"We're excited to present this beautiful {property_type.lower()} at {address}, {city}. Featuring {bedrooms} bedrooms, {bathrooms} bathrooms, and {sqft:,} square feet of living space, this home is priced at ${price:,}.\n\nHighlights include updated kitchen, spacious living areas, and a convenient location."
        elif style == "Engaging":
            body = f"Have you been searching for the perfect home in {city}? Look no further! This gorgeous {bedrooms} bedroom, {bathrooms} bathroom {property_type.lower()} could be your dream home! With {sqft:,} square feet and priced at ${price:,}, it offers the perfect blend of comfort, style, and value."
        elif style == "Visual":
            body = f"STUNNING HOME ALERT! 📸\n\nCheck out this beautiful {property_type.lower()} in {city}:\n✅ {bedrooms} spacious bedrooms\n✅ {bathrooms} stylish bathrooms\n✅ {sqft:,} square feet of living space\n✅ Priced at ${price:,}\n\nSwipe through the photos to see all the amazing features!"
        else:  # Story-based
            body = f"Sarah and Mike thought finding their perfect family home in {city} would take months... until they discovered this incredible {property_type.lower()} at {address}! With {bedrooms} bedrooms for their growing family and {bathrooms} bathrooms to eliminate morning rush hour, this {sqft:,} square foot home checked every box on their wishlist."
    
    elif platform == "Instagram":
        if style == "Informative":
            body = f"New listing in {city}! This {property_type.lower()} offers {bedrooms} bedrooms, {bathrooms} bathrooms, and {sqft:,} square feet of beautifully designed space. Priced at ${price:,}."
        elif style == "Engaging":
            body = f"This gorgeous {city} home is giving us serious real estate goals! 😍\n\n{bedrooms} bedrooms • {bathrooms} bathrooms • {sqft:,} sqft\n\nDouble tap if you could see yourself living here! ❤️"
        elif style == "Visual":
            body = f"✨ HOME TOUR ✨\n\nSwipe to explore this beautiful {property_type.lower()} in {city}!\n\n{bedrooms}BD • {bathrooms}BA • {sqft:,}sqft • ${price:,}"
        else:  # Story-based
            body = f"Behind every door is a story waiting to unfold. This {bedrooms} bedroom beauty in {city} is ready for its next chapter. Will you be the one to write it? ✨🏠✨"
    
    elif platform == "Twitter":
        if style == "Informative":
            body = f"New on the market: {bedrooms}bd/{bathrooms}ba {property_type} in {city}, {sqft:,}sqft, priced at ${price:,}. Schedule a showing today!"
        elif style == "Engaging":
            body = f"This {city} gem won't last long! {bedrooms} beds, {bathrooms} baths, and all the charm you could want in a {property_type.lower()}. Asking ${price:,}."
        elif style == "Visual":
            body = f"📸 Picture yourself in this gorgeous {city} home! {bedrooms}bd/{bathrooms}ba, ${price:,}"
        else:  # Story-based
            body = f"From morning coffee on the porch to evening gatherings in the spacious living room, this {city} {property_type.lower()} is where memories are made. {bedrooms}bd/{bathrooms}ba, ${price:,}"
    
    else:  # LinkedIn
        if style == "Informative":
            body = f"NEW LISTING: Professional opportunity in {city}. This well-appointed {property_type.lower()} features {bedrooms} bedrooms, {bathrooms} bathrooms, and {sqft:,} square feet of functional space. Offered at ${price:,}."
        elif style == "Engaging":
            body = f"Seeking a property that balances professional success with personal comfort? This exceptional {bedrooms} bedroom, {bathrooms} bathroom residence in {city} offers {sqft:,} square feet of thoughtfully designed space at ${price:,}."
        elif style == "Visual":
            body = f"PROPERTY HIGHLIGHT | {city}\n\nExecutive-level {property_type.lower()} with:\n• {bedrooms} bedrooms\n• {bathrooms} bathrooms\n• {sqft:,} square feet\n• ${price:,}\n\nView additional images in the comments."
        else:  # Story-based
            body = f"Real estate represents more than just property—it's an investment in lifestyle and future opportunities. This exceptional {city} residence exemplifies that philosophy, offering {bedrooms} bedrooms, {bathrooms} bathrooms, and {sqft:,} square feet of strategic living space."
    
    # Add call to action if requested
    if include_call_to_action:
        if platform == "Facebook":
            body += f"\n\nClick the link to schedule a showing or call us at 555-123-4567 for more information."
        elif platform == "Instagram":
            body += f"\n\nLink in bio to schedule a showing! 👆"
        elif platform == "Twitter":
            body += f"\nDM for details or click link to schedule a showing!"
        else:  # LinkedIn
            body += f"\n\nContact us directly or visit the link in comments to arrange a private viewing of this exceptional property."
    
    # Add engagement question if requested
    if include_questions:
        if platform == "Facebook":
            body += f"\n\nWhat feature do you love most about this home? Comment below!"
        elif platform == "Instagram":
            body += f"\n\nWhich room would you renovate first? 🏠 Drop your thoughts below! 👇"
        elif platform == "Twitter":
            body += f"\nWhat's your must-have feature in a {city} home?"
        else:  # LinkedIn
            body += f"\n\nWhat aspects of a property do you find most important when making a real estate investment decision?"
    
    # Add hashtags if requested
    hashtags = ""
    if include_hashtags:
        if platform == "Facebook":
            hashtags = f"\n\n#RealEstate #{city.replace(' ', '')} #{property_type.replace(' ', '')} #NewListing #DreamHome"
        elif platform == "Instagram":
            hashtags = f"\n\n.\n.\n.\n#RealEstate #{city.replace(' ', '')} #{property_type.replace(' ', '')} #HomeSweetHome #DreamHome #NewListing #HouseHunting #RealEstateLife #HomeInspo #PropertyForSale #LuxuryRealEstate"
        elif platform == "Twitter":
            hashtags = f"\n\n#RealEstate #{city.replace(' ', '')} #NewListing #HomeBuying"
        else:  # LinkedIn
            hashtags = f"\n\n#RealEstate #PropertyInvestment #{city.replace(' ', '')} #MarketOpportunity"
    
    # Photo suggestion if requested
    photo_suggestion = ""
    if include_photos:
        if platform == "Facebook":
            photo_suggestion = "Include 5-10 high-quality photos showcasing the property's exterior, key rooms, and unique features."
        elif platform == "Instagram":
            photo_suggestion = "Create a carousel of 4-5 eye-catching photos with the first image being the most stunning exterior or interior shot to capture attention."
        elif platform == "Twitter":
            photo_suggestion = "Include 1-2 high-impact photos that showcase the property's best feature."
        else:  # LinkedIn
            photo_suggestion = "Include 3-4 professional-quality photos highlighting the property's most impressive aspects."
    
    return {
        'headline': headline,
        'body': body,
        'hashtags': hashtags,
        'photo_suggestion': photo_suggestion
    }

def generate_email_campaign(campaign_type, recipient_segment, property_details=None, 
                         sender_name="Your Name", email_subject_prefix="", 
                         include_personal_note=True, include_market_stats=True,
                         include_testimonials=True):
    """Generate an email campaign based on type and preferences"""
    # Base email structure
    email_content = {}
    
    # Generate subject line
    if campaign_type == "New Listing Announcement":
        if property_details is not None:
            address = property_details['address']
            city = property_details['city']
            bedrooms = property_details['bedrooms']
            bathrooms = property_details['bathrooms']
            property_type = property_details['property_type']
            price = property_details['price']
            
            subject = f"Just Listed: {bedrooms}BD/{bathrooms}BA {property_type} in {city} - ${price:,}"
        else:
            subject = "Exciting New Property Just Listed"
    
    elif campaign_type == "Open House Invitation":
        if property_details is not None:
            address = property_details['address']
            city = property_details['city']
            
            subject = f"You're Invited: Open House at {address}, {city}"
        else:
            subject = "Join Us for an Exclusive Open House"
    
    elif campaign_type == "Price Reduction Alert":
        if property_details is not None:
            address = property_details['address']
            city = property_details['city']
            
            subject = f"Price Reduced on {address}, {city} - Great Opportunity!"
        else:
            subject = "Price Reduction Alert - Act Fast on This Amazing Deal"
    
    elif campaign_type == "Market Update Newsletter":
        subject = "Your Monthly Real Estate Market Update"
    
    elif campaign_type == "Just Sold Announcement":
        if property_details is not None:
            address = property_details['address']
            city = property_details['city']
            
            subject = f"Just Sold: {address}, {city} - Market Is Hot!"
        else:
            subject = "Just Sold! Another Happy Client in Today's Market"
    
    elif campaign_type == "Buyer/Seller Tips":
        subject = "Expert Tips for Today's Real Estate Market"
    
    else:  # Neighborhood Spotlight
        subject = "Neighborhood Spotlight: Discover Your Perfect Area"
    
    # Add prefix if provided
    if email_subject_prefix:
        subject = f"{email_subject_prefix} {subject}"
    
    email_content['subject'] = subject
    
    # Generate email body based on campaign type
    # Use HTML for better formatting
    body = ""
    
    # Add personalized greeting based on recipient segment
    if recipient_segment == "All Clients":
        greeting = "Dear Valued Client,"
    elif recipient_segment == "Past Buyers":
        greeting = "Dear Homeowner,"
    elif recipient_segment == "Current Sellers":
        greeting = "Dear Seller,"
    elif recipient_segment == "Potential Buyers":
        greeting = "Dear Future Homeowner,"
    elif recipient_segment == "Investors":
        greeting = "Dear Real Estate Investor,"
    elif recipient_segment == "First-time Homebuyers":
        greeting = "Dear First-Time Homebuyer,"
    else:  # Luxury Market Clients
        greeting = "Dear Valued Client,"
    
    body += f"<p>{greeting}</p>"
    
    # Add personal note if requested
    if include_personal_note:
        body += f"""
        <p>I hope this email finds you well. I'm reaching out with information that I believe will be valuable 
        to you in your real estate journey.</p>
        """
    
    # Main content based on campaign type
    if campaign_type == "New Listing Announcement":
        if property_details is not None:
            address = property_details['address']
            city = property_details['city']
            bedrooms = property_details['bedrooms']
            bathrooms = property_details['bathrooms']
            sqft = property_details['sqft']
            price = property_details['price']
            property_type = property_details['property_type']
            year_built = property_details['year_built']
            
            body += f"""
            <h2>Exciting New Listing Just Hit the Market!</h2>
            
            <p>I'm thrilled to present this beautiful {property_type.lower()} located at {address}, {city}.</p>
            
            <h3>Property Highlights:</h3>
            <ul>
                <li><strong>Price:</strong> ${price:,}</li>
                <li><strong>Bedrooms:</strong> {bedrooms}</li>
                <li><strong>Bathrooms:</strong> {bathrooms}</li>
                <li><strong>Square Footage:</strong> {sqft:,}</li>
                <li><strong>Year Built:</strong> {year_built}</li>
            </ul>
            
            <p>This exceptional home features [property features], making it perfect for [target buyer]. 
            The convenient location provides easy access to [nearby amenities].</p>
            
            <p><strong>Don't miss your chance to view this property!</strong> Contact me to schedule a private showing.</p>
            
            <div style="text-align: center; margin: 20px 0;">
                <a href="#" style="background-color: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Schedule a Showing</a>
            </div>
            """
        else:
            body += """
            <h2>Exciting New Listing Just Hit the Market!</h2>
            
            <p>I'm thrilled to present a beautiful new property that just hit the market.</p>
            
            <p>This exceptional home features all the amenities you've been looking for. 
            Don't miss your chance to view this property!</p>
            
            <div style="text-align: center; margin: 20px 0;">
                <a href="#" style="background-color: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">View Property Details</a>
            </div>
            """
    
    elif campaign_type == "Open House Invitation":
        if property_details is not None:
            address = property_details['address']
            city = property_details['city']
            bedrooms = property_details['bedrooms']
            bathrooms = property_details['bathrooms']
            sqft = property_details['sqft']
            property_type = property_details['property_type']
            
            body += f"""
            <h2>You're Invited to an Exclusive Open House!</h2>
            
            <p>I'm hosting an open house for the beautiful {bedrooms} bedroom, {bathrooms} bathroom {property_type.lower()} 
            located at {address}, {city}.</p>
            
            <div style="background-color: #f5f5f5; padding: 15px; margin: 15px 0; border-radius: 5px;">
                <h3 style="color: #3498db; margin-top: 0;">Open House Details:</h3>
                <p><strong>When:</strong> [OPEN_HOUSE_DATE_TIME]</p>
                <p><strong>Where:</strong> {address}, {city}</p>
                <p><strong>Property:</strong> {bedrooms} bedroom, {bathrooms} bathroom {property_type.lower()} with {sqft:,} square feet</p>
            </div>
            
            <p>Light refreshments will be served, and I'll be available to answer all your questions about this amazing property
            and the surrounding neighborhood.</p>
            
            <div style="text-align: center; margin: 20px 0;">
                <a href="#" style="background-color: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">RSVP to Open House</a>
            </div>
            """
        else:
            body += """
            <h2>You're Invited to an Exclusive Open House!</h2>
            
            <div style="background-color: #f5f5f5; padding: 15px; margin: 15px 0; border-radius: 5px;">
                <h3 style="color: #3498db; margin-top: 0;">Open House Details:</h3>
                <p><strong>When:</strong> [OPEN_HOUSE_DATE_TIME]</p>
                <p><strong>Where:</strong> [PROPERTY_ADDRESS]</p>
            </div>
            
            <p>Light refreshments will be served, and I'll be available to answer all your questions about this amazing property
            and the surrounding neighborhood.</p>
            
            <div style="text-align: center; margin: 20px 0;">
                <a href="#" style="background-color: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">RSVP to Open House</a>
            </div>
            """
    
    elif campaign_type == "Price Reduction Alert":
        if property_details is not None:
            address = property_details['address']
            city = property_details['city']
            bedrooms = property_details['bedrooms']
            bathrooms = property_details['bathrooms']
            sqft = property_details['sqft']
            price = property_details['price']
            property_type = property_details['property_type']
            
            # Simulate a previous price about 5-10% higher
            previous_price = price * random.uniform(1.05, 1.1)
            
            body += f"""
            <h2>Price Reduction Alert: Great Opportunity!</h2>
            
            <p>I wanted to let you know about a significant price reduction on the {bedrooms} bedroom, {bathrooms} bathroom 
            {property_type.lower()} located at {address}, {city}.</p>
            
            <div style="background-color: #f5f5f5; padding: 15px; margin: 15px 0; border-radius: 5px;">
                <h3 style="color: #e74c3c; margin-top: 0;">Price Update:</h3>
                <p><strong>Previous Price:</strong> <span style="text-decoration: line-through;">${previous_price:,.0f}</span></p>
                <p><strong>New Price:</strong> <span style="color: #e74c3c; font-size: 1.2em;">${price:,.0f}</span></p>
                <p><strong>Savings:</strong> ${previous_price - price:,.0f}</p>
            </div>
            
            <p>This is an excellent opportunity to own this {sqft:,} square foot home at a compelling price point. 
            The property won't last long at this new price!</p>
            
            <div style="text-align: center; margin: 20px 0;">
                <a href="#" style="background-color: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Schedule a Showing</a>
            </div>
            """
        else:
            body += """
            <h2>Price Reduction Alert: Great Opportunity!</h2>
            
            <p>I wanted to let you know about a significant price reduction on a property that might interest you.</p>
            
            <p>This is an excellent opportunity to own this home at a compelling price point. 
            The property won't last long at this new price!</p>
            
            <div style="text-align: center; margin: 20px 0;">
                <a href="#" style="background-color: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">View Property Details</a>
            </div>
            """
    
    elif campaign_type == "Market Update Newsletter":
        body += """
        <h2>Your Monthly Real Estate Market Update</h2>
        
        <p>I'm pleased to share this month's real estate market insights to keep you informed about the latest trends.</p>
        """
        
        if include_market_stats:
            # Generate some random but realistic market statistics
            avg_price = random.randint(350000, 650000)
            prev_avg_price = avg_price * random.uniform(0.95, 1.05)
            price_change = ((avg_price - prev_avg_price) / prev_avg_price) * 100
            
            avg_days = random.randint(15, 45)
            prev_avg_days = avg_days * random.uniform(0.9, 1.1)
            days_change = ((avg_days - prev_avg_days) / prev_avg_days) * 100
            
            new_listings = random.randint(50, 200)
            prev_new_listings = new_listings * random.uniform(0.9, 1.1)
            listings_change = ((new_listings - prev_new_listings) / prev_new_listings) * 100
            
            body += f"""
            <h3>Market Statistics at a Glance:</h3>
            
            <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                <tr style="background-color: #f5f5f5;">
                    <th style="padding: 10px; text-align: left; border-bottom: 1px solid #ddd;">Metric</th>
                    <th style="padding: 10px; text-align: right; border-bottom: 1px solid #ddd;">Current</th>
                    <th style="padding: 10px; text-align: right; border-bottom: 1px solid #ddd;">Change</th>
                </tr>
                <tr>
                    <td style="padding: 10px; border-bottom: 1px solid #ddd;">Average Sales Price</td>
                    <td style="padding: 10px; text-align: right; border-bottom: 1px solid #ddd;">${avg_price:,}</td>
                    <td style="padding: 10px; text-align: right; border-bottom: 1px solid #ddd; color: {'#27ae60' if price_change > 0 else '#e74c3c'};">
                        {price_change:.1f}%
                    </td>
                </tr>
                <tr>
                    <td style="padding: 10px; border-bottom: 1px solid #ddd;">Average Days on Market</td>
                    <td style="padding: 10px; text-align: right; border-bottom: 1px solid #ddd;">{avg_days}</td>
                    <td style="padding: 10px; text-align: right; border-bottom: 1px solid #ddd; color: {'#e74c3c' if days_change < 0 else '#27ae60'};">
                        {days_change:.1f}%
                    </td>
                </tr>
                <tr>
                    <td style="padding: 10px; border-bottom: 1px solid #ddd;">New Listings</td>
                    <td style="padding: 10px; text-align: right; border-bottom: 1px solid #ddd;">{new_listings}</td>
                    <td style="padding: 10px; text-align: right; border-bottom: 1px solid #ddd; color: {'#27ae60' if listings_change > 0 else '#e74c3c'};">
                        {listings_change:.1f}%
                    </td>
                </tr>
            </table>
            """
        
        body += """
        <h3>Market Trends This Month:</h3>
        <ul>
            <li>The market continues to show strength in the mid-range price points, with strong demand for homes priced between $300,000 and $500,000.</li>
            <li>Interest rates have stabilized, providing buyers with more confidence in their purchasing decisions.</li>
            <li>Inventory levels remain tight, creating favorable conditions for sellers in most neighborhoods.</li>
        </ul>
        
        <h3>Featured Listings This Month:</h3>
        <p>Check out these exceptional properties that just hit the market:</p>
        <ul>
            <li><a href="#">Beautiful 4BD/3BA Home in Riverside - $495,000</a></li>
            <li><a href="#">Renovated 3BD/2BA Townhouse in Downtown - $325,000</a></li>
            <li><a href="#">Luxury 5BD/4BA Estate with Pool - $789,000</a></li>
        </ul>
        
        <div style="text-align: center; margin: 20px 0;">
            <a href="#" style="background-color: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">View All Listings</a>
        </div>
        """
    
    elif campaign_type == "Just Sold Announcement":
        if property_details is not None:
            address = property_details['address']
            city = property_details['city']
            bedrooms = property_details['bedrooms']
            bathrooms = property_details['bathrooms']
            sqft = property_details['sqft']
            price = property_details['price']
            property_type = property_details['property_type']
            
            days_on_market = random.randint(7, 60)
            offers = random.randint(1, 8)
            
            body += f"""
            <h2>Just Sold! Another Happy Client in Today's Market</h2>
            
            <p>I'm excited to announce the successful sale of the {bedrooms} bedroom, {bathrooms} bathroom 
            {property_type.lower()} located at {address}, {city}.</p>
            
            <div style="background-color: #f5f5f5; padding: 15px; margin: 15px 0; border-radius: 5px;">
                <h3 style="color: #27ae60; margin-top: 0;">Sale Details:</h3>
                <ul style="list-style-type: none; padding-left: 0;">
                    <li><strong>Sale Price:</strong> ${price:,}</li>
                    <li><strong>Days on Market:</strong> {days_on_market}</li>
                    <li><strong>Number of Offers:</strong> {offers}</li>
                </ul>
            </div>
            
            <p>This successful sale demonstrates the continued strong demand for quality homes in {city}. 
            If you're considering selling your property, now might be the perfect time to maximize your return!</p>
            """
        else:
            body += """
            <h2>Just Sold! Another Happy Client in Today's Market</h2>
            
            <p>I'm excited to announce another successful sale in today's competitive market!</p>
            
            <p>This successful sale demonstrates the continued strong demand for quality homes in our area. 
            If you're considering selling your property, now might be the perfect time to maximize your return!</p>
            """
    
    elif campaign_type == "Buyer/Seller Tips":
        # Determine if tips for buyers or sellers based on recipient segment
        if recipient_segment in ["Potential Buyers", "First-time Homebuyers"]:
            body += """
            <h2>Essential Tips for Today's Homebuyers</h2>
            
            <p>In today's competitive real estate market, being well-prepared can make all the difference in your home buying journey.
            Here are some expert tips to help you succeed:</p>
            
            <ol>
                <li><strong>Get pre-approved for financing</strong> before starting your home search to understand your budget and strengthen your offers.</li>
                <li><strong>Identify your non-negotiables</strong> versus nice-to-haves to focus your search efficiently.</li>
                <li><strong>Work with an experienced real estate agent</strong> who understands the local market and can advocate for your interests.</li>
                <li><strong>Be prepared to act quickly</strong> when you find the right property, as desirable homes are moving fast.</li>
                <li><strong>Consider looking slightly under your maximum budget</strong> to leave room for competitive offers.</li>
            </ol>
            
            <p>Remember, buying a home is a significant investment, and having the right guidance can make the process smoother and more successful.</p>
            """
        else:
            body += """
            <h2>Maximize Your Home's Value: Expert Seller Tips</h2>
            
            <p>If you're considering selling your home, these expert tips can help you maximize your property's value and appeal to today's buyers:</p>
            
            <ol>
                <li><strong>Make strategic pre-listing improvements</strong> that offer the best return on investment, such as fresh paint, updated fixtures, and curb appeal enhancements.</li>
                <li><strong>Price your home correctly from the start</strong> based on a comprehensive market analysis to attract serious buyers.</li>
                <li><strong>Stage your home effectively</strong> to help buyers envision themselves living in the space.</li>
                <li><strong>Ensure professional-quality photography</strong> to make your listing stand out online where most buyers begin their search.</li>
                <li><strong>Be flexible with showings</strong> to accommodate potential buyers' schedules and maximize exposure.</li>
            </ol>
            
            <p>The right preparation and marketing strategy can significantly impact your selling experience and final sale price.</p>
            """
        
        body += """
        <div style="text-align: center; margin: 20px 0;">
            <a href="#" style="background-color: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Schedule a Consultation</a>
        </div>
        """
    
    else:  # Neighborhood Spotlight
        body += """
        <h2>Neighborhood Spotlight: Finding Your Perfect Location</h2>
        
        <p>Location is one of the most critical factors in real estate decisions. This month, we're highlighting 
        three distinct neighborhoods, each offering unique advantages for different lifestyles and preferences.</p>
        
        <div style="margin: 20px 0;">
            <h3 style="color: #3498db;">Riverside Heights</h3>
            <p><strong>Highlights:</strong> Excellent schools, family-friendly parks, and community events make this area 
            perfect for families. The median home price is $425,000, with properties ranging from classic colonials to 
            modern constructions.</p>
            
            <h3 style="color: #3498db;">Downtown District</h3>
            <p><strong>Highlights:</strong> For those seeking an urban lifestyle, this area offers walkability to restaurants, 
            shops, and entertainment venues. Condos and lofts range from $275,000 to $650,000, with strong rental potential.</p>
            
            <h3 style="color: #3498db;">Oakwood Estates</h3>
            <p><strong>Highlights:</strong> This established neighborhood features larger lots, mature trees, and a mix of 
            architectural styles. With excellent privacy and a serene atmosphere, homes typically range from $500,000 to $850,000.</p>
        </div>
        
        <p>Each of these neighborhoods offers distinct advantages. I'd be happy to arrange tours of properties in any of 
        these areas that match your specific needs and preferences.</p>
        
        <div style="text-align: center; margin: 20px 0;">
            <a href="#" style="background-color: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Explore Neighborhoods</a>
        </div>
        """
    
    # Add testimonials if requested
    if include_testimonials:
        body += """
        <div style="background-color: #f9f9f9; padding: 15px; margin: 25px 0; border-left: 4px solid #3498db;">
            <h3 style="margin-top: 0;">What Our Clients Say:</h3>
            <p style="font-style: italic;">"Working with this team made my home buying process smooth and stress-free. 
            Their knowledge of the market and dedication to understanding my needs resulted in finding my perfect home!"</p>
            <p style="margin-bottom: 0;"><strong>- Sarah J., Recent Homebuyer</strong></p>
        </div>
        """
    
    # Add closing
    body += f"""
    <p>Please don't hesitate to reach out if you have any questions or if I can be of assistance with your real estate needs.</p>
    
    <p>Best regards,<br>
    {sender_name}</p>
    
    <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; font-size: 0.9em; color: #777;">
        <p>You're receiving this email because you've expressed interest in real estate services. 
        If you'd prefer not to receive these updates, you can <a href="#">unsubscribe here</a>.</p>
    </div>
    """
    
    email_content['body'] = body
    
    return email_content

def generate_marketing_data():
    """Generate sample marketing performance data for demonstration"""
    # Define marketing channels
    channels = ['Facebook Ads', 'Google Ads', 'Email Campaigns', 'Instagram', 'Zillow', 'Realtor.com']
    
    # Generate data for the past 90 days
    today = datetime.now()
    start_date = today - timedelta(days=90)
    
    marketing_data = []
    
    for channel in channels:
        # Define channel-specific baseline metrics
        if channel == 'Facebook Ads':
            base_impressions = random.randint(5000, 15000)
            base_ctr = random.uniform(1.0, 2.5)
            base_inquiry_rate = random.uniform(2.0, 5.0)
            daily_cost = random.uniform(20, 50)
        elif channel == 'Google Ads':
            base_impressions = random.randint(2000, 7000)
            base_ctr = random.uniform(2.0, 4.0)
            base_inquiry_rate = random.uniform(5.0, 8.0)
            daily_cost = random.uniform(30, 70)
        elif channel == 'Email Campaigns':
            base_impressions = random.randint(1000, 3000)
            base_ctr = random.uniform(2.5, 5.0)
            base_inquiry_rate = random.uniform(1.0, 3.0)
            daily_cost = random.uniform(5, 15)
        elif channel == 'Instagram':
            base_impressions = random.randint(3000, 10000)
            base_ctr = random.uniform(0.8, 2.0)
            base_inquiry_rate = random.uniform(1.5, 4.0)
            daily_cost = random.uniform(15, 40)
        elif channel == 'Zillow':
            base_impressions = random.randint(1500, 5000)
            base_ctr = random.uniform(3.0, 6.0)
            base_inquiry_rate = random.uniform(7.0, 12.0)
            daily_cost = random.uniform(40, 90)
        else:  # Realtor.com
            base_impressions = random.randint(1200, 4000)
            base_ctr = random.uniform(2.5, 5.5)
            base_inquiry_rate = random.uniform(6.0, 10.0)
            daily_cost = random.uniform(35, 80)
        
        # Generate daily data
        current_date = start_date
        while current_date <= today:
            # Add some randomness to daily metrics
            daily_variation = random.uniform(0.7, 1.3)
            
            # Add weekly patterns
            day_of_week = current_date.weekday()
            if day_of_week >= 5:  # Weekend
                weekend_factor = random.uniform(0.6, 0.9)
                daily_variation *= weekend_factor
            
            # Add some trend over time (generally improving)
            days_from_start = (current_date - start_date).days
            trend_factor = 1 + (days_from_start / 90 * random.uniform(0.1, 0.3))
            
            # Calculate metrics
            impressions = int(base_impressions * daily_variation * trend_factor)
            clicks = int(impressions * (base_ctr / 100) * daily_variation)
            inquiries = int(clicks * (base_inquiry_rate / 100) * daily_variation)
            cost = daily_cost * daily_variation
            
            marketing_data.append({
                'date': current_date,
                'channel': channel,
                'impressions': impressions,
                'clicks': clicks,
                'inquiries': inquiries,
                'cost': cost
            })
            
            current_date += timedelta(days=1)
    
    return pd.DataFrame(marketing_data)