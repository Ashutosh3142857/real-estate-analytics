"""
Ad Performance Analytics Page for displaying marketing performance metrics across platforms.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import random
from utils import social_media_manager

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

if __name__ == "__main__":
    show_ad_performance_analytics()