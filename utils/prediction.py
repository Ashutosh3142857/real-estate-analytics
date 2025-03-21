import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

def train_price_prediction_model(df):
    """
    Train a machine learning model to predict property prices
    
    Returns:
        tuple: (trained_model, preprocessor, features, mae, r2)
    """
    if df.empty or len(df) < 50:  # Need sufficient data for training
        return None, None, None, None, None
    
    try:
        # Features for prediction
        features = ['bedrooms', 'bathrooms', 'sqft', 'year_built', 'city', 'property_type']
        
        # Check if all features are available
        for feature in features:
            if feature not in df.columns:
                return None, None, None, None, None
        
        # Prepare the data
        X = df[features].copy()
        y = df['price']
        
        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Create preprocessor
        categorical_features = ['city', 'property_type']
        categorical_transformer = OneHotEncoder(handle_unknown='ignore')
        
        preprocessor = ColumnTransformer(
            transformers=[
                ('cat', categorical_transformer, categorical_features)
            ],
            remainder='passthrough'
        )
        
        # Create and train the model
        model = Pipeline([
            ('preprocessor', preprocessor),
            ('regressor', LinearRegression())
        ])
        
        model.fit(X_train, y_train)
        
        # Evaluate the model
        y_pred = model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        return model, preprocessor, features, mae, r2
        
    except Exception as e:
        print(f"Error training model: {e}")
        return None, None, None, None, None

def predict_property_price(model, features, property_data):
    """
    Predict the price of a property based on its features
    
    Args:
        model: Trained model
        features: List of feature names used by the model
        property_data: Dictionary with property features
        
    Returns:
        float: Predicted price
    """
    if model is None:
        return None
    
    try:
        # Create a DataFrame with the property data
        property_df = pd.DataFrame([property_data])
        
        # Ensure all required features are present
        for feature in features:
            if feature not in property_df.columns:
                return None
        
        # Make prediction
        predicted_price = model.predict(property_df[features])[0]
        
        return predicted_price
        
    except Exception as e:
        print(f"Error making prediction: {e}")
        return None

def calculate_roi(purchase_price, monthly_rent, annual_expenses, appreciation_rate=0.03, holding_period=5):
    """
    Calculate the Return on Investment (ROI) for a real estate investment
    
    Args:
        purchase_price: Purchase price of the property
        monthly_rent: Monthly rental income
        annual_expenses: Annual expenses (taxes, insurance, maintenance, etc.)
        appreciation_rate: Annual appreciation rate (default: 3%)
        holding_period: Investment holding period in years (default: 5)
        
    Returns:
        dict: ROI metrics including cash flow, cash on cash return, total ROI
    """
    try:
        # Down payment (assuming 20%)
        down_payment = purchase_price * 0.2
        
        # Loan amount
        loan_amount = purchase_price - down_payment
        
        # Annual rental income
        annual_rent = monthly_rent * 12
        
        # Net operating income (NOI)
        noi = annual_rent - annual_expenses
        
        # Mortgage payment (simplified calculation assuming 30-year fixed at 4.5%)
        mortgage_rate = 0.045
        monthly_mortgage = loan_amount * (mortgage_rate/12 * (1 + mortgage_rate/12)**(30*12)) / ((1 + mortgage_rate/12)**(30*12) - 1)
        annual_mortgage = monthly_mortgage * 12
        
        # Cash flow
        annual_cash_flow = noi - annual_mortgage
        
        # Property value after appreciation
        future_value = purchase_price * (1 + appreciation_rate)**holding_period
        
        # Remaining loan balance (simplified)
        # This is a simplification; a real amortization schedule would be more accurate
        remaining_principal = loan_amount * (1 - holding_period/30)
        
        # Equity at sale
        equity_at_sale = future_value - remaining_principal
        
        # Total profit
        total_profit = equity_at_sale - down_payment + (annual_cash_flow * holding_period)
        
        # ROI calculations
        cash_on_cash_return = (annual_cash_flow / down_payment) * 100
        total_roi = (total_profit / down_payment) * 100
        annualized_roi = ((1 + total_roi/100)**(1/holding_period) - 1) * 100
        
        # Cap rate
        cap_rate = (noi / purchase_price) * 100
        
        # Return results
        return {
            'monthly_cash_flow': annual_cash_flow / 12,
            'annual_cash_flow': annual_cash_flow,
            'cash_on_cash_return': cash_on_cash_return,
            'future_value': future_value,
            'equity_at_sale': equity_at_sale,
            'total_profit': total_profit,
            'total_roi': total_roi,
            'annualized_roi': annualized_roi,
            'cap_rate': cap_rate
        }
        
    except Exception as e:
        print(f"Error calculating ROI: {e}")
        return None

def forecast_market_trends(df, forecast_months=12):
    """
    Generate a market trend forecast based on historical data
    
    Args:
        df: DataFrame with historical price data
        forecast_months: Number of months to forecast
        
    Returns:
        DataFrame: Forecast data with date and predicted average prices
    """
    if df.empty:
        return pd.DataFrame()
    
    try:
        # Get market trend data
        market_data = []
        
        for _, row in df.iterrows():
            city = row['city']
            historical_prices = row['historical_prices']
            
            for month_data in historical_prices:
                market_data.append({
                    'date': month_data['date'],
                    'city': city,
                    'avg_price': month_data['avg_price']
                })
        
        market_df = pd.DataFrame(market_data)
        
        # Remove duplicates
        market_df = market_df.drop_duplicates(['date', 'city'])
        
        # Convert date to datetime
        market_df['date'] = pd.to_datetime(market_df['date'])
        
        # Sort by date
        market_df = market_df.sort_values('date')
        
        # Add a numeric month feature for modeling
        min_date = market_df['date'].min()
        market_df['month_num'] = ((market_df['date'].dt.year - min_date.year) * 12 + 
                                  (market_df['date'].dt.month - min_date.month))
        
        # Create forecast data for each city
        forecast_data = []
        
        for city in market_df['city'].unique():
            city_data = market_df[market_df['city'] == city]
            
            if len(city_data) < 3:  # Need at least 3 data points
                continue
            
            # Simple linear regression for forecasting
            X = city_data[['month_num']]
            y = city_data['avg_price']
            
            model = LinearRegression()
            model.fit(X, y)
            
            # Create forecast months
            last_month_num = city_data['month_num'].max()
            forecast_months_nums = np.arange(last_month_num + 1, last_month_num + forecast_months + 1)
            
            # Generate predictions
            for month_num in forecast_months_nums:
                # Convert month_num back to date
                forecast_date = min_date + pd.DateOffset(months=int(month_num))
                
                # Predict price
                predicted_price = model.predict([[month_num]])[0]
                
                forecast_data.append({
                    'date': forecast_date,
                    'city': city,
                    'avg_price': predicted_price,
                    'is_forecast': True
                })
        
        # Combine historical and forecast data
        historical_data = market_df.copy()
        historical_data['is_forecast'] = False
        
        forecast_df = pd.DataFrame(forecast_data)
        
        combined_df = pd.concat([historical_data[['date', 'city', 'avg_price', 'is_forecast']], 
                                 forecast_df])
        
        # Sort by city and date
        combined_df = combined_df.sort_values(['city', 'date'])
        
        return combined_df
        
    except Exception as e:
        print(f"Error forecasting market trends: {e}")
        return pd.DataFrame()
