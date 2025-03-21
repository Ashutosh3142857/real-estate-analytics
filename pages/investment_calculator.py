import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.prediction import calculate_roi

def show_investment_calculator():
    st.title("Investment Opportunity Calculator")
    
    st.markdown("""
    This calculator helps real estate investors analyze potential investment opportunities.
    Enter property details and investment parameters to see projected returns.
    """)
    
    # Create form for user input
    with st.form("investment_calculator_form"):
        st.subheader("Property Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            purchase_price = st.number_input(
                "Purchase Price ($)",
                min_value=50000,
                max_value=10000000,
                value=350000,
                step=10000
            )
            
            monthly_rent = st.number_input(
                "Monthly Rental Income ($)",
                min_value=100,
                max_value=50000,
                value=2000,
                step=100
            )
        
        with col2:
            annual_property_tax = st.number_input(
                "Annual Property Tax ($)",
                min_value=0,
                max_value=100000,
                value=3500,
                step=100
            )
            
            annual_insurance = st.number_input(
                "Annual Insurance ($)",
                min_value=0,
                max_value=50000,
                value=1200,
                step=100
            )
        
        st.subheader("Operating Expenses")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            maintenance_pct = st.number_input(
                "Maintenance (% of rent)",
                min_value=0.0,
                max_value=50.0,
                value=5.0,
                step=0.5,
                format="%.1f"
            )
        
        with col2:
            vacancy_pct = st.number_input(
                "Vacancy (% of rent)",
                min_value=0.0,
                max_value=50.0,
                value=5.0,
                step=0.5,
                format="%.1f"
            )
        
        with col3:
            management_pct = st.number_input(
                "Property Management (% of rent)",
                min_value=0.0,
                max_value=50.0,
                value=8.0,
                step=0.5,
                format="%.1f"
            )
        
        st.subheader("Investment Parameters")
        
        col1, col2 = st.columns(2)
        
        with col1:
            appreciation_rate = st.number_input(
                "Annual Appreciation Rate (%)",
                min_value=0.0,
                max_value=20.0,
                value=3.0,
                step=0.1,
                format="%.1f"
            )
            
            holding_period = st.number_input(
                "Investment Holding Period (years)",
                min_value=1,
                max_value=30,
                value=5,
                step=1
            )
        
        with col2:
            down_payment_pct = st.number_input(
                "Down Payment (%)",
                min_value=0.0,
                max_value=100.0,
                value=20.0,
                step=5.0,
                format="%.1f"
            )
            
            mortgage_rate = st.number_input(
                "Mortgage Interest Rate (%)",
                min_value=0.0,
                max_value=20.0,
                value=4.5,
                step=0.1,
                format="%.1f"
            )
        
        calculate_button = st.form_submit_button("Calculate ROI")
    
    # Calculate ROI when form is submitted
    if calculate_button or 'roi_results' in st.session_state:
        # Calculate total annual expenses
        annual_maintenance = (monthly_rent * 12) * (maintenance_pct / 100)
        annual_vacancy = (monthly_rent * 12) * (vacancy_pct / 100)
        annual_management = (monthly_rent * 12) * (management_pct / 100)
        
        total_annual_expenses = (
            annual_property_tax +
            annual_insurance +
            annual_maintenance +
            annual_vacancy +
            annual_management
        )
        
        # Calculate down payment and loan details
        down_payment = purchase_price * (down_payment_pct / 100)
        loan_amount = purchase_price - down_payment
        
        # Calculate mortgage payment
        monthly_rate = mortgage_rate / 100 / 12
        loan_term_months = 30 * 12  # 30-year fixed mortgage
        
        if mortgage_rate > 0:
            monthly_mortgage = loan_amount * (monthly_rate * (1 + monthly_rate)**loan_term_months) / ((1 + monthly_rate)**loan_term_months - 1)
        else:
            monthly_mortgage = loan_amount / loan_term_months
        
        annual_mortgage = monthly_mortgage * 12
        
        # Calculate cash flow
        annual_rental_income = monthly_rent * 12
        annual_cash_flow = annual_rental_income - total_annual_expenses - annual_mortgage
        monthly_cash_flow = annual_cash_flow / 12
        
        # Calculate ROI metrics
        cash_on_cash_return = (annual_cash_flow / down_payment) * 100
        
        # Calculate future value with appreciation
        future_value = purchase_price * (1 + appreciation_rate / 100)**holding_period
        
        # Calculate remaining loan balance (simplified)
        payments_made = holding_period * 12
        if mortgage_rate > 0:
            remaining_balance = loan_amount * (1 - ((1 + monthly_rate)**payments_made - 1) / ((1 + monthly_rate)**loan_term_months - 1))
        else:
            remaining_balance = loan_amount - (loan_amount / loan_term_months) * payments_made
        
        # Calculate equity and total profit
        equity = future_value - remaining_balance
        total_profit = equity - down_payment + (annual_cash_flow * holding_period)
        total_roi = (total_profit / down_payment) * 100
        annualized_roi = ((1 + total_roi / 100)**(1 / holding_period) - 1) * 100
        
        # Calculate cap rate
        noi = annual_rental_income - total_annual_expenses
        cap_rate = (noi / purchase_price) * 100
        
        # Store results
        roi_results = {
            'purchase_price': purchase_price,
            'down_payment': down_payment,
            'loan_amount': loan_amount,
            'monthly_mortgage': monthly_mortgage,
            'annual_rental_income': annual_rental_income,
            'total_annual_expenses': total_annual_expenses,
            'annual_cash_flow': annual_cash_flow,
            'monthly_cash_flow': monthly_cash_flow,
            'cash_on_cash_return': cash_on_cash_return,
            'future_value': future_value,
            'remaining_balance': remaining_balance,
            'equity': equity,
            'total_profit': total_profit,
            'total_roi': total_roi,
            'annualized_roi': annualized_roi,
            'cap_rate': cap_rate
        }
        
        st.session_state.roi_results = roi_results
    
    # Display results if available
    if 'roi_results' in st.session_state:
        roi_results = st.session_state.roi_results
        
        st.header("Investment Analysis Results")
        
        # Key metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Monthly Cash Flow",
                f"${roi_results['monthly_cash_flow']:.2f}",
                delta=None
            )
        
        with col2:
            st.metric(
                "Cash on Cash Return",
                f"{roi_results['cash_on_cash_return']:.2f}%",
                delta=None
            )
        
        with col3:
            st.metric(
                "Cap Rate",
                f"{roi_results['cap_rate']:.2f}%",
                delta=None
            )
        
        # Long-term metrics
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "Total ROI",
                f"{roi_results['total_roi']:.2f}%",
                delta=None
            )
        
        with col2:
            st.metric(
                "Annualized ROI",
                f"{roi_results['annualized_roi']:.2f}%",
                delta=None
            )
        
        # Financial details
        st.subheader("Financial Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Purchase Details:**")
            st.markdown(f"- Purchase Price: ${roi_results['purchase_price']:,.2f}")
            st.markdown(f"- Down Payment: ${roi_results['down_payment']:,.2f}")
            st.markdown(f"- Loan Amount: ${roi_results['loan_amount']:,.2f}")
            st.markdown(f"- Monthly Mortgage: ${roi_results['monthly_mortgage']:,.2f}")
            
            st.markdown("**Cash Flow Details:**")
            st.markdown(f"- Annual Rental Income: ${roi_results['annual_rental_income']:,.2f}")
            st.markdown(f"- Annual Expenses: ${roi_results['total_annual_expenses']:,.2f}")
            st.markdown(f"- Annual Cash Flow: ${roi_results['annual_cash_flow']:,.2f}")
        
        with col2:
            st.markdown("**Equity & Profit (after holding period):**")
            st.markdown(f"- Future Property Value: ${roi_results['future_value']:,.2f}")
            st.markdown(f"- Remaining Loan Balance: ${roi_results['remaining_balance']:,.2f}")
            st.markdown(f"- Equity at Sale: ${roi_results['equity']:,.2f}")
            st.markdown(f"- Total Profit: ${roi_results['total_profit']:,.2f}")
        
        # Cash flow visualization
        st.subheader("Cash Flow Over Holding Period")
        
        # Generate year by year cash flow
        years = list(range(1, roi_results['holding_period'] + 1))
        annual_cf = roi_results['annual_cash_flow']
        cash_flows = [annual_cf] * roi_results['holding_period']
        
        # Calculate cumulative cash flow
        cumulative_cf = [sum(cash_flows[:i+1]) for i in range(len(cash_flows))]
        
        # Create the plot
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=years,
            y=cash_flows,
            name='Annual Cash Flow',
            marker_color='lightgreen'
        ))
        
        fig.add_trace(go.Scatter(
            x=years,
            y=cumulative_cf,
            mode='lines+markers',
            name='Cumulative Cash Flow',
            marker_color='darkgreen',
            yaxis='y2'
        ))
        
        fig.update_layout(
            title='Cash Flow Projection',
            xaxis_title='Year',
            yaxis_title='Annual Cash Flow ($)',
            yaxis2=dict(
                title='Cumulative Cash Flow ($)',
                overlaying='y',
                side='right',
                tickprefix='$',
                tickformat=','
            ),
            yaxis=dict(
                tickprefix='$',
                tickformat=','
            ),
            template='plotly_white',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Return breakdown chart
        st.subheader("Return Breakdown")
        
        # Create data for the breakdown
        rental_income = roi_results['annual_rental_income'] * roi_results['holding_period']
        expenses = roi_results['total_annual_expenses'] * roi_results['holding_period']
        mortgage_payments = roi_results['monthly_mortgage'] * 12 * roi_results['holding_period']
        appreciation = roi_results['future_value'] - roi_results['purchase_price']
        
        # Create a waterfall chart
        fig = go.Figure(go.Waterfall(
            name="Return Breakdown",
            orientation="v",
            measure=["absolute", "relative", "relative", "relative", "relative", "total"],
            x=["Initial Investment", "Rental Income", "Expenses", "Mortgage Payments", "Appreciation", "Total Profit"],
            textposition="outside",
            text=[f"${-roi_results['down_payment']:,.0f}", f"${rental_income:,.0f}", f"-${expenses:,.0f}", 
                  f"-${mortgage_payments:,.0f}", f"${appreciation:,.0f}", f"${roi_results['total_profit']:,.0f}"],
            y=[-roi_results['down_payment'], rental_income, -expenses, -mortgage_payments, appreciation, 0],
            connector={"line": {"color": "rgb(63, 63, 63)"}},
        ))
        
        fig.update_layout(
            title="Investment Return Breakdown",
            yaxis_title="Amount ($)",
            yaxis=dict(tickprefix='$', tickformat=','),
            template='plotly_white',
            height=500,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Investment recommendation
        st.subheader("Investment Analysis")
        
        # Determine if this is a good investment
        is_good_investment = roi_results['cash_on_cash_return'] > 5 and roi_results['monthly_cash_flow'] > 0
        
        if is_good_investment:
            st.success("""
            **Recommendation: Consider This Investment**
            
            This property shows positive cash flow and good returns. The cash-on-cash return exceeds 5%, 
            which is generally considered a good threshold for rental property investments.
            """)
        else:
            st.warning("""
            **Recommendation: Exercise Caution**
            
            This property may not generate sufficient cash flow or returns. Consider negotiating a lower
            purchase price or finding ways to increase rental income.
            """)
        
        # Risk factors
        st.subheader("Risk Factors to Consider")
        
        risk_items = []
        
        # Cash flow risk
        if roi_results['monthly_cash_flow'] < 0:
            risk_items.append("❌ Negative cash flow - property will require additional funding each month")
        elif roi_results['monthly_cash_flow'] < 100:
            risk_items.append("⚠️ Low cash flow margin - small unexpected expenses could result in negative cash flow")
        else:
            risk_items.append("✅ Positive cash flow provides a buffer against unexpected expenses")
        
        # Vacancy risk
        if vacancy_pct < 5:
            risk_items.append("⚠️ Vacancy rate may be underestimated (less than 5%)")
        
        # Appreciation risk
        if appreciation_rate > 5:
            risk_items.append("⚠️ High appreciation rate assumption may be optimistic")
        
        # Expense risk
        if maintenance_pct < 5:
            risk_items.append("⚠️ Maintenance costs may be underestimated (less than 5% of rent)")
        
        st.markdown("\n".join(risk_items))
