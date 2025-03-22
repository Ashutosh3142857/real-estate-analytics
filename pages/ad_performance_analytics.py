"""
Ad Performance Analytics Page for displaying marketing performance metrics across platforms.
Provides integration with major ad platforms and campaign management capabilities.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import random
import json
from utils import social_media_manager
from utils import ad_platform_api

def get_mock_campaign_data():
    """Generate mock campaign data for demonstration purposes."""
    # Define platforms
    platforms = ["Facebook", "Instagram", "Google", "Twitter", "TikTok", "LinkedIn"]
    
    # Campaign types by platform
    campaign_types = {
        "Facebook": ["Property Listing", "Neighborhood Spotlight", "Open House", "Brand Awareness"],
        "Instagram": ["Property Showcase", "Agent Highlight", "Property Video Tour", "Story Ads"],
        "Google": ["Property Search", "Branded Search", "Neighborhood Display", "Remarketing"],
        "Twitter": ["Market Update", "New Listing", "Agent Promotion", "Community News"],
        "TikTok": ["Property Tour", "Neighborhood Review", "Agent Tips", "Testimonial"],
        "LinkedIn": ["Investment Property", "Commercial Listing", "Professional Network", "Market Analysis"]
    }
    
    # Create campaign data
    campaigns = []
    campaign_id = 1
    
    for platform in platforms:
        # Generate 2-5 campaigns per platform
        num_campaigns = random.randint(2, 5)
        for _ in range(num_campaigns):
            campaign_type = random.choice(campaign_types[platform])
            campaign_name = f"{platform} {campaign_type} {random.randint(1, 999)}"
            
            # Generate performance metrics
            impressions = random.randint(1000, 100000)
            ctr = random.uniform(0.5, 8.0)
            clicks = int(impressions * (ctr / 100))
            conversion_rate = random.uniform(1.0, 20.0)
            conversions = int(clicks * (conversion_rate / 100))
            
            # Generate financial metrics
            spend = random.uniform(50, 2000)
            cost_per_click = spend / clicks if clicks > 0 else 0
            cost_per_conversion = spend / conversions if conversions > 0 else 0
            
            # Calculate ROI (assuming $200 value per conversion)
            conversion_value = conversions * 200
            roi = ((conversion_value - spend) / spend * 100) if spend > 0 else 0
            
            # Create campaign record
            campaigns.append({
                "campaign_id": campaign_id,
                "platform": platform,
                "campaign_name": campaign_name,
                "campaign_type": campaign_type,
                "impressions": impressions,
                "clicks": clicks,
                "ctr": ctr,
                "conversions": conversions,
                "conversion_rate": conversion_rate,
                "spend": spend,
                "cost_per_click": cost_per_click,
                "cost_per_conversion": cost_per_conversion,
                "roi": roi,
                "start_date": datetime.now() - timedelta(days=random.randint(10, 90)),
                "status": random.choice(["Active", "Paused", "Completed"])
            })
            campaign_id += 1
    
    return pd.DataFrame(campaigns)

def show_ad_performance_analytics():
    """Display ad performance analytics dashboard."""
    st.title("Marketing Performance Analytics")
    
    st.markdown("""
    Track and analyze the performance of your real estate marketing campaigns across multiple platforms.
    Optimize your marketing strategy based on data-driven insights from all your digital advertising channels.
    """)
    
    # Check platform credentials
    platform_status = social_media_manager.check_platform_credentials()
    available_platforms = social_media_manager.get_available_platforms()
    
    # Get ad campaign data (using mock data for demo)
    # In a production environment, this would come from social_media_manager.get_ad_campaign_performance()
    campaign_data = get_mock_campaign_data()
    
    # Create tabs for different analytics views
    tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Platform Comparison", "Campaign Details", "Recommendations"])
    
    with tab1:
        # Overview tab
        st.subheader("Performance Overview")
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            date_range = st.selectbox(
                "Date Range",
                options=["Last 7 Days", "Last 30 Days", "Last 90 Days", "Year to Date", "All Time"],
                index=1
            )
        
        with col2:
            platforms = st.multiselect(
                "Platforms",
                options=campaign_data['platform'].unique(),
                default=campaign_data['platform'].unique()
            )
        
        with col3:
            metrics = st.multiselect(
                "Key Metrics",
                options=["Impressions", "Clicks", "CTR", "Conversions", "Conversion Rate", "Cost", "ROI"],
                default=["Impressions", "Clicks", "Conversions", "ROI"]
            )
            
        # Filter data based on selections
        filtered_data = campaign_data.copy()
        if platforms:
            filtered_data = filtered_data[filtered_data['platform'].isin(platforms)]
        
        # Display overall metrics
        st.markdown("### Overall Performance")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_impressions = filtered_data['impressions'].sum()
            st.metric("Total Impressions", f"{total_impressions:,}")
        
        with col2:
            total_clicks = filtered_data['clicks'].sum()
            st.metric("Total Clicks", f"{total_clicks:,}")
        
        with col3:
            total_conversions = filtered_data['conversions'].sum()
            st.metric("Total Conversions", f"{total_conversions:,}")
        
        with col4:
            total_spend = filtered_data['spend'].sum()
            st.metric("Total Spend", f"${total_spend:,.2f}")
        
        # Calculate overall metrics
        if total_impressions > 0:
            overall_ctr = (total_clicks / total_impressions) * 100
        else:
            overall_ctr = 0
        
        if total_clicks > 0:
            overall_conversion_rate = (total_conversions / total_clicks) * 100
        else:
            overall_conversion_rate = 0
        
        if total_spend > 0:
            overall_cpc = total_spend / total_clicks if total_clicks > 0 else 0
            overall_cost_per_conversion = total_spend / total_conversions if total_conversions > 0 else 0
            overall_roi = filtered_data['roi'].mean()
        else:
            overall_cpc = 0
            overall_cost_per_conversion = 0
            overall_roi = 0
        
        # Display overall ratios
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Overall CTR", f"{overall_ctr:.2f}%")
        
        with col2:
            st.metric("Overall Conv. Rate", f"{overall_conversion_rate:.2f}%")
        
        with col3:
            st.metric("Avg. CPC", f"${overall_cpc:.2f}")
        
        with col4:
            st.metric("Avg. ROI", f"{overall_roi:.2f}%")
        
        # Performance by platform charts
        st.markdown("### Performance by Platform")
        
        # Get performance metrics by platform
        platform_summary = filtered_data.groupby('platform').agg({
            'impressions': 'sum',
            'clicks': 'sum',
            'conversions': 'sum',
            'spend': 'sum',
            'roi': 'mean'
        }).reset_index()
        
        # Calculate CTR and conversion rate
        platform_summary['ctr'] = (platform_summary['clicks'] / platform_summary['impressions'] * 100).fillna(0)
        platform_summary['conversion_rate'] = (platform_summary['conversions'] / platform_summary['clicks'] * 100).fillna(0)
        
        # Create visualizations based on selected metrics
        if "Impressions" in metrics:
            fig = px.bar(
                platform_summary,
                x='platform',
                y='impressions',
                title='Impressions by Platform',
                color='platform',
                text_auto=True
            )
            st.plotly_chart(fig, use_container_width=True)
        
        if "Clicks" in metrics:
            fig = px.bar(
                platform_summary,
                x='platform',
                y='clicks',
                title='Clicks by Platform',
                color='platform',
                text_auto=True
            )
            st.plotly_chart(fig, use_container_width=True)
        
        if "Conversions" in metrics:
            fig = px.bar(
                platform_summary,
                x='platform',
                y='conversions',
                title='Conversions by Platform',
                color='platform',
                text_auto=True
            )
            st.plotly_chart(fig, use_container_width=True)
        
        if "ROI" in metrics:
            fig = px.bar(
                platform_summary,
                x='platform',
                y='roi',
                title='ROI by Platform',
                color='platform',
                text_auto=True
            )
            st.plotly_chart(fig, use_container_width=True)
            
    with tab2:
        # Platform comparison tab
        st.subheader("Platform Comparison")
        
        # Prepare comparison data
        platform_comparison = platform_summary.copy()
        platform_comparison['cpc'] = (platform_comparison['spend'] / platform_comparison['clicks']).fillna(0)
        platform_comparison['cost_per_conversion'] = (platform_comparison['spend'] / platform_comparison['conversions']).fillna(0)
        
        # Show platform comparison data
        st.dataframe(platform_comparison[[
            'platform', 'impressions', 'clicks', 'ctr', 'conversions', 
            'conversion_rate', 'spend', 'cpc', 'cost_per_conversion', 'roi'
        ]], use_container_width=True)
        
        # Create visualization for platform comparison
        metrics_to_plot = ['ctr', 'conversion_rate', 'cpc', 'roi']
        titles = ['Click-Through Rate (%)', 'Conversion Rate (%)', 'Cost per Click ($)', 'Return on Investment (%)']
        
        col1, col2 = st.columns(2)
        
        for i, (metric, title) in enumerate(zip(metrics_to_plot, titles)):
            fig = px.bar(
                platform_comparison,
                x='platform',
                y=metric,
                title=title,
                color='platform'
            )
            
            if i % 2 == 0:
                with col1:
                    st.plotly_chart(fig, use_container_width=True)
            else:
                with col2:
                    st.plotly_chart(fig, use_container_width=True)
        
        # Cost efficiency comparison
        st.subheader("Cost Efficiency by Platform")
        
        cost_comparison = platform_comparison[['platform', 'cost_per_conversion', 'roi']].copy()
        cost_comparison.columns = ['Platform', 'Cost per Conversion ($)', 'ROI (%)']
        
        fig = px.scatter(
            cost_comparison,
            x='Cost per Conversion ($)',
            y='ROI (%)',
            color='Platform',
            size=[100] * len(cost_comparison),
            hover_name='Platform',
            title='Cost Efficiency by Platform'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Platform recommendations
        best_roi_platform = platform_comparison.loc[platform_comparison['roi'].idxmax()]['platform']
        best_ctr_platform = platform_comparison.loc[platform_comparison['ctr'].idxmax()]['platform']
        best_conv_platform = platform_comparison.loc[platform_comparison['conversion_rate'].idxmax()]['platform']
        
        st.info(f"""
        ### Platform Insights
        
        - **Best ROI Platform:** {best_roi_platform} with {platform_comparison.loc[platform_comparison['roi'].idxmax()]['roi']:.2f}% ROI
        - **Best Engagement Platform:** {best_ctr_platform} with {platform_comparison.loc[platform_comparison['ctr'].idxmax()]['ctr']:.2f}% CTR
        - **Best Conversion Platform:** {best_conv_platform} with {platform_comparison.loc[platform_comparison['conversion_rate'].idxmax()]['conversion_rate']:.2f}% conversion rate
        """)
        
    with tab3:
        # Campaign details tab
        st.subheader("Campaign Details")
        
        # Platform filter
        platform_filter = st.selectbox(
            "Select Platform",
            options=['All Platforms'] + list(campaign_data['platform'].unique())
        )
        
        # Filter data
        if platform_filter != 'All Platforms':
            campaign_detail_data = campaign_data[campaign_data['platform'] == platform_filter].copy()
        else:
            campaign_detail_data = campaign_data.copy()
        
        # Sort options
        sort_by = st.selectbox(
            "Sort By",
            options=['ROI (High to Low)', 'Spend (High to Low)', 'Conversions (High to Low)', 'CTR (High to Low)']
        )
        
        if sort_by == 'ROI (High to Low)':
            campaign_detail_data = campaign_detail_data.sort_values('roi', ascending=False)
        elif sort_by == 'Spend (High to Low)':
            campaign_detail_data = campaign_detail_data.sort_values('spend', ascending=False)
        elif sort_by == 'Conversions (High to Low)':
            campaign_detail_data = campaign_detail_data.sort_values('conversions', ascending=False)
        else:  # CTR (High to Low)
            campaign_detail_data = campaign_detail_data.sort_values('ctr', ascending=False)
        
        # Display campaign data
        st.dataframe(campaign_detail_data[
            ['platform', 'campaign_name', 'campaign_type', 'status', 'impressions', 'clicks', 'ctr', 
             'conversions', 'conversion_rate', 'spend', 'cost_per_conversion', 'roi']
        ], use_container_width=True)
        
        # Display top campaigns
        st.subheader("Top Performing Campaigns")
        
        # Get top performing campaigns
        top_campaigns = campaign_detail_data.sort_values('roi', ascending=False).head(5)
        
        # Create performance visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            # ROI by campaign
            fig = px.bar(
                top_campaigns,
                x='campaign_name',
                y='roi',
                color='platform',
                title='Top Campaigns by ROI',
                labels={'roi': 'ROI (%)', 'campaign_name': 'Campaign'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Conversion rate by campaign
            fig = px.bar(
                top_campaigns,
                x='campaign_name',
                y='conversion_rate',
                color='platform',
                title='Top Campaigns by Conversion Rate',
                labels={'conversion_rate': 'Conversion Rate (%)', 'campaign_name': 'Campaign'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Campaign details expander
        for _, campaign in top_campaigns.iterrows():
            with st.expander(f"{campaign['campaign_name']} ({campaign['platform']})"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Impressions", f"{campaign['impressions']:,}")
                    st.metric("Clicks", f"{campaign['clicks']:,}")
                
                with col2:
                    st.metric("CTR", f"{campaign['ctr']:.2f}%")
                    st.metric("Conversions", f"{campaign['conversions']:,}")
                
                with col3:
                    st.metric("Spend", f"${campaign['spend']:.2f}")
                    st.metric("ROI", f"{campaign['roi']:.2f}%")
                
                st.write(f"**Estimated Revenue:** ${campaign['conversions'] * 200:.2f}")
                st.write(f"**Net Profit:** ${(campaign['conversions'] * 200) - campaign['spend']:.2f}")
    
    with tab4:
        # Recommendations tab
        st.subheader("Marketing Recommendations")
        
        # Budget allocation recommendation
        st.markdown("### Budget Allocation")
        
        # Current budget allocation
        current_allocation = filtered_data.groupby('platform').agg({'spend': 'sum'})
        total_spend = current_allocation['spend'].sum()
        current_allocation['percentage'] = (current_allocation['spend'] / total_spend) * 100
        
        # Recommended allocation based on ROI
        roi_based = platform_summary[['platform', 'roi']].copy()
        total_roi = roi_based['roi'].sum()
        roi_based['recommended_percentage'] = (roi_based['roi'] / total_roi) * 100
        
        # Merge current and recommended
        allocation_comparison = pd.merge(
            current_allocation.reset_index(), 
            roi_based, 
            on='platform'
        )
        
        # Create allocation visualization
        fig = px.bar(
            allocation_comparison,
            x='platform',
            y=['percentage', 'recommended_percentage'],
            barmode='group',
            title='Current vs. Recommended Budget Allocation',
            labels={
                'percentage': 'Current Allocation (%)',
                'recommended_percentage': 'Recommended Allocation (%)',
                'platform': 'Platform',
                'value': 'Percentage (%)'
            }
        )
        fig.update_layout(legend_title_text='')
        st.plotly_chart(fig, use_container_width=True)
        
        # Key recommendations
        st.markdown("### Key Recommendations")
        
        # Get top performing campaign
        top_campaign = filtered_data.loc[filtered_data['roi'].idxmax()]
        
        # Get worst performing campaign with significant spend
        significant_spend = filtered_data[filtered_data['spend'] > filtered_data['spend'].median()]
        worst_campaign = significant_spend.loc[significant_spend['roi'].idxmin()]
        
        st.markdown(f"""
        1. **Budget Reallocation:** Increase budget allocation to {best_roi_platform} by at least 15% to capitalize on its {platform_comparison.loc[platform_comparison['platform'] == best_roi_platform, 'roi'].values[0]:.2f}% ROI.
        
        2. **Top Campaign Scaling:** Expand your top-performing campaign "{top_campaign['campaign_name']}" on {top_campaign['platform']}, which has achieved {top_campaign['roi']:.2f}% ROI.
        
        3. **Campaign Optimization:** Review and optimize "{worst_campaign['campaign_name']}" on {worst_campaign['platform']}, which has a low ROI of {worst_campaign['roi']:.2f}% despite significant spend.
        
        4. **Cross-Platform Strategy:** Adapt successful content from {best_roi_platform} for use on other platforms, particularly targeting similar audience demographics.
        
        5. **Conversion Tracking:** Implement enhanced conversion tracking across all platforms to better attribute results from each marketing channel.
        """)
        
        # Platform-specific recommendations
        st.markdown("### Platform-Specific Recommendations")
        
        for platform in filtered_data['platform'].unique():
            platform_data = filtered_data[filtered_data['platform'] == platform]
            avg_roi = platform_data['roi'].mean()
            
            with st.expander(f"{platform} Recommendations"):
                # Get best and worst campaign for this platform
                best_plat_campaign = platform_data.loc[platform_data['roi'].idxmax()]
                worst_plat_campaign = platform_data.loc[platform_data['roi'].idxmin()]
                
                if platform == "Facebook" or platform == "Instagram":
                    st.markdown(f"""
                    - **Audience Targeting:** Refine lookalike audiences based on top-converting customers
                    - **Creative Strategy:** Implement more video content and carousel ads which typically have higher engagement
                    - **Best Campaign:** "{best_plat_campaign['campaign_name']}" with {best_plat_campaign['roi']:.2f}% ROI
                    - **Campaign to Optimize:** "{worst_plat_campaign['campaign_name']}" with {worst_plat_campaign['roi']:.2f}% ROI
                    """)
                elif platform == "Google":
                    st.markdown(f"""
                    - **Keyword Strategy:** Focus on long-tail, high-intent keywords with lower CPC
                    - **Ad Extensions:** Implement all available ad extensions to improve CTR
                    - **Best Campaign:** "{best_plat_campaign['campaign_name']}" with {best_plat_campaign['roi']:.2f}% ROI
                    - **Campaign to Optimize:** "{worst_plat_campaign['campaign_name']}" with {worst_plat_campaign['roi']:.2f}% ROI
                    """)
                elif platform == "LinkedIn":
                    st.markdown(f"""
                    - **Targeting Approach:** Target by job function and seniority for B2B real estate connections
                    - **Content Type:** Focus on thought leadership content for highest engagement
                    - **Best Campaign:** "{best_plat_campaign['campaign_name']}" with {best_plat_campaign['roi']:.2f}% ROI
                    - **Campaign to Optimize:** "{worst_plat_campaign['campaign_name']}" with {worst_plat_campaign['roi']:.2f}% ROI
                    """)
                else:
                    st.markdown(f"""
                    - **Overall Performance:** Average ROI of {avg_roi:.2f}%
                    - **Best Campaign:** "{best_plat_campaign['campaign_name']}" with {best_plat_campaign['roi']:.2f}% ROI
                    - **Campaign to Optimize:** "{worst_plat_campaign['campaign_name']}" with {worst_plat_campaign['roi']:.2f}% ROI
                    """)
        
        # Add a button to generate a detailed report
        if st.button("Generate Detailed Marketing Report"):
            st.success("Detailed marketing performance report would be generated and downloaded")
            st.info("This feature would export a comprehensive PDF or Excel report in a production environment")
        
        # Ad Platform API Integration section
        st.markdown("---")
        st.subheader("Ad Platform API Integration")
        
        # Check available ad platforms
        available_ad_platforms = ad_platform_api.get_available_platforms()
        
        # Create tabs for different integration features
        api_tab1, api_tab2, api_tab3 = st.tabs(["Connect Platforms", "Campaign Management", "Audience Insights"])
        
        with api_tab1:
            st.markdown("""
            Connect your real estate marketing campaigns with major advertising platforms using API integration.
            Direct API connections enable automated reporting, performance insights, and campaign optimization.
            """)
            
            # Platform connection status
            st.markdown("### Platform Connection Status")
            
            platforms = ["Facebook", "Google", "LinkedIn", "Twitter", "TikTok"]
            platform_status = {}
            
            for platform in platforms:
                platform_status[platform.lower()] = platform.lower() in available_ad_platforms
            
            # Display status and connection forms for each platform
            col1, col2 = st.columns(2)
            
            with col1:
                for platform in platforms[:3]:  # First 3 platforms in first column
                    with st.expander(f"{platform} Ads Integration"):
                        if platform_status[platform.lower()]:
                            st.success(f"✅ Connected to {platform} Ads API")
                            if st.button(f"Disconnect {platform}", key=f"disconnect_{platform.lower()}"):
                                st.info(f"This would disconnect the {platform} Ads API integration")
                        else:
                            st.warning(f"❌ Not connected to {platform} Ads API")
                            
                            # Display connection form based on platform
                            if platform == "Facebook":
                                st.text_input("App ID", key="fb_app_id", type="password")
                                st.text_input("App Secret", key="fb_app_secret", type="password")
                                st.text_input("Access Token", key="fb_access_token", type="password")
                                st.text_input("Ad Account ID", key="fb_ad_account_id")
                            elif platform == "Google":
                                st.text_input("Developer Token", key="google_developer_token", type="password")
                                st.text_input("Client ID", key="google_client_id", type="password")
                                st.text_input("Client Secret", key="google_client_secret", type="password")
                                st.text_input("Refresh Token", key="google_refresh_token", type="password")
                                st.text_input("Customer ID", key="google_customer_id")
                            elif platform == "LinkedIn":
                                st.text_input("Client ID", key="linkedin_client_id", type="password")
                                st.text_input("Client Secret", key="linkedin_client_secret", type="password")
                                st.text_input("Access Token", key="linkedin_access_token", type="password")
                                st.text_input("Organization ID", key="linkedin_organization_id")
                                
                            if st.button(f"Connect {platform}", key=f"connect_{platform.lower()}"):
                                st.info(f"This would connect to the {platform} Ads API using the provided credentials")
            
            with col2:
                for platform in platforms[3:]:  # Last 2 platforms in second column
                    with st.expander(f"{platform} Ads Integration"):
                        if platform_status[platform.lower()]:
                            st.success(f"✅ Connected to {platform} Ads API")
                            if st.button(f"Disconnect {platform}", key=f"disconnect_{platform.lower()}"):
                                st.info(f"This would disconnect the {platform} Ads API integration")
                        else:
                            st.warning(f"❌ Not connected to {platform} Ads API")
                            
                            # Display connection form based on platform
                            if platform == "Twitter":
                                st.text_input("API Key", key="twitter_api_key", type="password")
                                st.text_input("API Secret", key="twitter_api_secret", type="password")
                                st.text_input("Access Token", key="twitter_access_token", type="password")
                                st.text_input("Access Token Secret", key="twitter_access_token_secret", type="password")
                                st.text_input("Account ID", key="twitter_account_id")
                            elif platform == "TikTok":
                                st.text_input("App ID", key="tiktok_app_id", type="password")
                                st.text_input("App Secret", key="tiktok_app_secret", type="password")
                                st.text_input("Access Token", key="tiktok_access_token", type="password")
                                st.text_input("Advertiser ID", key="tiktok_advertiser_id")
                                
                            if st.button(f"Connect {platform}", key=f"connect_{platform.lower()}"):
                                st.info(f"This would connect to the {platform} Ads API using the provided credentials")
            
            # Bulk credentials upload option
            st.markdown("### Bulk Credentials Upload")
            st.markdown("""
            You can also upload a JSON file containing credentials for multiple platforms at once.
            This file should follow the structure defined in the documentation.
            """)
            
            uploaded_file = st.file_uploader("Upload credentials JSON file", type=["json"])
            if uploaded_file is not None:
                st.info("This would process the uploaded credentials file and connect to the specified ad platforms")
        
        with api_tab2:
            st.markdown("""
            Create, manage, and optimize your real estate advertising campaigns directly from this platform.
            Automated campaign management enables you to scale your marketing efforts efficiently.
            """)
            
            # Campaign management section
            st.markdown("### Campaign Management")
            
            # Platform selection for campaign management
            platform_options = ['Facebook', 'Google', 'LinkedIn', 'Twitter', 'TikTok']
            selected_platform = st.selectbox("Select Platform for Campaign Management", platform_options)
            
            if not platform_status.get(selected_platform.lower(), False):
                st.warning(f"You need to connect to {selected_platform} Ads API first to manage campaigns")
            else:
                # Campaign actions
                action = st.radio("Action", ["Create New Campaign", "Optimize Existing Campaigns", "View Campaign Performance"])
                
                if action == "Create New Campaign":
                    st.markdown("### Create New Real Estate Campaign")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        campaign_name = st.text_input("Campaign Name", value=f"RE Property Campaign {datetime.now().strftime('%b-%Y')}")
                        campaign_objective = st.selectbox(
                            "Campaign Objective", 
                            ["Property Listing Promotion", "Open House Awareness", "Agent Branding", "Market Report Distribution"]
                        )
                        
                        budget_type = st.radio("Budget Type", ["Daily", "Lifetime"])
                        budget_amount = st.number_input("Budget Amount ($)", min_value=5.0, max_value=10000.0, value=50.0)
                        
                    with col2:
                        start_date = st.date_input("Start Date", datetime.now())
                        end_date = st.date_input("End Date", datetime.now() + timedelta(days=30))
                        
                        target_audience = st.multiselect(
                            "Target Audience Interests",
                            ["Real Estate", "Home Buying", "Home Selling", "Interior Design", "Home Improvement", 
                             "Mortgage", "Investment Properties", "Luxury Living", "Residential Properties", "Commercial Properties"]
                        )
                        
                        location_targeting = st.text_input("Location Targeting", value="New York, NY")
                    
                    # Ad creative section
                    st.markdown("### Ad Creative")
                    
                    ad_headline = st.text_input("Ad Headline", value="Discover Your Dream Home")
                    ad_text = st.text_area(
                        "Ad Text", 
                        value="Explore our curated selection of premium properties in the most desirable neighborhoods. Schedule a viewing today!"
                    )
                    
                    # Image upload would be handled here
                    st.file_uploader("Upload Ad Image", type=["jpg", "jpeg", "png"])
                    
                    # Landing page URL
                    landing_page_url = st.text_input("Landing Page URL", value="https://yourrealestatesite.com/listings")
                    
                    # Call to action
                    call_to_action = st.selectbox(
                        "Call to Action",
                        ["Learn More", "Schedule Viewing", "Contact Agent", "See Listings", "Apply Now", "Download Guide"]
                    )
                    
                    if st.button("Create Campaign", key="create_campaign_button"):
                        # Prepare campaign data
                        campaign_data = {
                            "name": campaign_name,
                            "objective": campaign_objective,
                            "budget_type": budget_type,
                            "budget_amount": budget_amount,
                            "start_date": start_date.isoformat(),
                            "end_date": end_date.isoformat(),
                            "targeting": {
                                "interests": target_audience,
                                "location": location_targeting
                            },
                            "ad_creative": {
                                "headline": ad_headline,
                                "text": ad_text,
                                "cta": call_to_action,
                                "landing_page": landing_page_url
                            }
                        }
                        
                        # This would call the API to create the campaign in a production environment
                        result = ad_platform_api.create_ad_campaign(selected_platform.lower(), campaign_data)
                        
                        st.success(f"Campaign '{campaign_name}' would be created on {selected_platform} (simulation)")
                        st.info("In a production environment, this would use the API to create a real campaign")
                
                elif action == "Optimize Existing Campaigns":
                    st.markdown("### Optimize Existing Campaigns")
                    
                    # Get campaign IDs (simulated)
                    campaign_ids = [f"{selected_platform}_Campaign_{i}" for i in range(1, 6)]
                    campaign_names = [f"{selected_platform} Property Campaign {i}" for i in range(1, 6)]
                    
                    campaigns = pd.DataFrame({
                        "id": campaign_ids,
                        "name": campaign_names,
                        "status": ["Active", "Active", "Paused", "Active", "Completed"],
                        "budget": [50.0, 75.0, 100.0, 200.0, 150.0],
                        "roi": [120.5, 85.3, 45.7, 200.1, 75.9]
                    })
                    
                    st.dataframe(campaigns, use_container_width=True)
                    
                    # Select campaign to optimize
                    selected_campaign = st.selectbox("Select Campaign to Optimize", campaign_names)
                    selected_id = campaign_ids[campaign_names.index(selected_campaign)]
                    
                    if st.button("Run Optimization", key="run_optimization_button"):
                        with st.spinner(f"Analyzing {selected_campaign} for optimization opportunities..."):
                            # This would call the API to get optimization recommendations
                            optimization = ad_platform_api.optimize_ad_campaign(selected_platform.lower(), selected_id)
                            
                            st.success("Optimization analysis completed")
                            
                            # Show recommendations
                            st.markdown("### Optimization Recommendations")
                            
                            recommendations = [
                                {"type": "bidding", "action": "increase", "target": "cpc", "amount": "15%", "reason": "Underperforming on high-value keywords"},
                                {"type": "audience", "action": "expand", "target": "demographics", "detail": "Include 35-44 age group", "reason": "High conversion rate in similar campaigns"},
                                {"type": "creative", "action": "test", "target": "new_versions", "detail": "A/B test with property video content", "reason": "Video content showing 22% higher engagement"}
                            ]
                            
                            for i, rec in enumerate(recommendations):
                                st.info(f"""
                                **Recommendation {i+1}: {rec['action'].title()} {rec['target'].replace('_', ' ')}**
                                
                                Action: {rec['action'].title()} {rec['target'].replace('_', ' ')} {rec.get('amount', '')} {rec.get('detail', '')}
                                Reason: {rec['reason']}
                                """)
                                
                                # Add apply button for each recommendation
                                if st.button(f"Apply Recommendation {i+1}", key=f"apply_rec_{i}"):
                                    st.success(f"Recommendation would be applied to campaign '{selected_campaign}'")
                
                else:  # View Campaign Performance
                    st.markdown("### Campaign Performance")
                    
                    # Date range selection
                    col1, col2 = st.columns(2)
                    with col1:
                        start_date = st.date_input("Start Date", datetime.now() - timedelta(days=30))
                    with col2:
                        end_date = st.date_input("End Date", datetime.now())
                    
                    if st.button("Fetch Performance Data", key="fetch_performance_button"):
                        with st.spinner("Fetching campaign performance data..."):
                            # This would call the API to get performance data in a production environment
                            date_range = {
                                "start_date": start_date.isoformat(),
                                "end_date": end_date.isoformat()
                            }
                            
                            st.info(f"This would fetch real performance data from {selected_platform} Ads API in a production environment")
                            
                            # Show a placeholder for the results
                            st.markdown("### Performance Results")
                            st.markdown(f"Performance data for {selected_platform} campaigns from {start_date} to {end_date}")
                            
                            # Sample metrics (would come from API in production)
                            metrics = {
                                "impressions": random.randint(10000, 100000),
                                "clicks": random.randint(500, 5000),
                                "ctr": random.uniform(1.0, 8.0),
                                "conversions": random.randint(10, 500),
                                "conversion_rate": random.uniform(1.0, 20.0),
                                "spend": random.uniform(500, 5000),
                                "cost_per_click": random.uniform(0.5, 3.0),
                                "cost_per_conversion": random.uniform(10, 100),
                                "roi": random.uniform(50, 300)
                            }
                            
                            # Display metrics
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("Impressions", f"{metrics['impressions']:,}")
                                st.metric("Clicks", f"{metrics['clicks']:,}")
                                st.metric("CTR", f"{metrics['ctr']:.2f}%")
                            
                            with col2:
                                st.metric("Conversions", f"{metrics['conversions']:,}")
                                st.metric("Conversion Rate", f"{metrics['conversion_rate']:.2f}%") 
                                st.metric("Spend", f"${metrics['spend']:.2f}")
                            
                            with col3:
                                st.metric("Cost per Click", f"${metrics['cost_per_click']:.2f}")
                                st.metric("Cost per Conversion", f"${metrics['cost_per_conversion']:.2f}")
                                st.metric("ROI", f"{metrics['roi']:.2f}%")
        
        with api_tab3:
            st.markdown("""
            Gain deep insights into your target audience across different advertising platforms.
            Use these insights to refine your real estate marketing strategy and targeting.
            """)
            
            # Platform selection for audience insights
            selected_platform = st.selectbox("Select Platform for Audience Insights", platform_options, key="audience_platform")
            
            if not platform_status.get(selected_platform.lower(), False):
                st.warning(f"You need to connect to {selected_platform} Ads API first to access audience insights")
            else:
                # Button to fetch audience insights
                if st.button("Fetch Audience Insights", key="fetch_audience_button"):
                    with st.spinner(f"Fetching audience insights from {selected_platform}..."):
                        # This would call the API to get audience insights in a production environment
                        insights = ad_platform_api.get_platform_audience_insights(selected_platform.lower())
                        
                        # Display insights
                        st.markdown("### Audience Insights")
                        
                        # Demographics section
                        st.markdown("#### Demographics")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Age distribution
                            if selected_platform.lower() in ["facebook", "google"]:
                                age_data = {
                                    "Age Group": ["25-34", "35-44", "45-54", "55+"],
                                    "Percentage": [35, 28, 22, 15]
                                }
                                
                                age_df = pd.DataFrame(age_data)
                                
                                fig = px.bar(
                                    age_df,
                                    x="Age Group",
                                    y="Percentage",
                                    title="Age Distribution",
                                    text_auto=True
                                )
                                st.plotly_chart(fig, use_container_width=True)
                        
                        with col2:
                            # Gender distribution
                            if selected_platform.lower() in ["facebook", "google"]:
                                gender_data = {
                                    "Gender": ["Female", "Male"],
                                    "Percentage": [48, 52]
                                }
                                
                                gender_df = pd.DataFrame(gender_data)
                                
                                fig = px.pie(
                                    gender_df,
                                    names="Gender",
                                    values="Percentage",
                                    title="Gender Distribution"
                                )
                                st.plotly_chart(fig, use_container_width=True)
                        
                        # Interests section
                        st.markdown("#### Interests & Behaviors")
                        
                        if selected_platform.lower() == "facebook":
                            interests_data = {
                                "Interest": ["Home Improvement", "Real Estate", "Interior Design", "Finance", "Travel"],
                                "Strength": ["Very High", "Very High", "High", "Medium", "Medium"],
                                "Score": [90, 85, 75, 60, 55]
                            }
                            
                            interests_df = pd.DataFrame(interests_data)
                            
                            fig = px.bar(
                                interests_df,
                                x="Interest",
                                y="Score",
                                color="Strength",
                                title="Interest Categories",
                                text_auto=True
                            )
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Behaviors
                            behaviors_data = {
                                "Behavior": ["First-time Home Buyers", "Investors", "High Net Worth"],
                                "Affinity": [3.5, 2.8, 1.7]
                            }
                            
                            behaviors_df = pd.DataFrame(behaviors_data)
                            
                            fig = px.bar(
                                behaviors_df,
                                x="Behavior",
                                y="Affinity",
                                title="Behavior Affinity (Multiplier vs Average)",
                                text_auto=True
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        
                        elif selected_platform.lower() == "google":
                            # In-market segments
                            segments_data = {
                                "Segment": ["Real Estate", "Mortgages", "Home & Garden", "Luxury Goods"],
                                "Index": [5.7, 4.8, 3.2, 2.1]
                            }
                            
                            segments_df = pd.DataFrame(segments_data)
                            
                            fig = px.bar(
                                segments_df,
                                x="Segment",
                                y="Index",
                                title="In-Market Segments (Multiplier vs Average)",
                                text_auto=True
                            )
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Affinity categories
                            affinity_data = {
                                "Category": ["Home Decor Enthusiasts", "Avid Investors", "Luxury Shoppers"],
                                "Index": [4.2, 3.9, 2.8]
                            }
                            
                            affinity_df = pd.DataFrame(affinity_data)
                            
                            fig = px.bar(
                                affinity_df,
                                x="Category",
                                y="Index",
                                title="Affinity Categories (Multiplier vs Average)",
                                text_auto=True
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        
                        else:
                            st.markdown(f"Showing audience insights for {selected_platform}")
                            
                            # Generic interests for other platforms
                            interests_data = {
                                "Interest": ["Real Estate", "Investments", "Home Design"],
                                "Strength": ["High", "Medium", "Medium"],
                                "Score": [80, 65, 60]
                            }
                            
                            interests_df = pd.DataFrame(interests_data)
                            
                            fig = px.bar(
                                interests_df,
                                x="Interest",
                                y="Score",
                                color="Strength",
                                title="Interest Categories",
                                text_auto=True
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        
                        # Recommendations based on audience insights
                        st.markdown("#### Audience Targeting Recommendations")
                        
                        st.info("""
                        ### Based on your audience insights:
                        
                        1. **Primary Target:** Focus on professionals aged 35-44 interested in real estate and home improvement
                        2. **Secondary Target:** Expand to investors in the 45-54 age range with interests in finance
                        3. **Creative Approach:** Emphasize property features that appeal to identified interests
                        4. **Ad Scheduling:** Target weekday evenings when your audience is most active
                        5. **Geographic Focus:** Concentrate budget on high-performing locations
                        """)

if __name__ == "__main__":
    show_ad_performance_analytics()