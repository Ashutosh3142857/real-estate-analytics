"""
Advanced AI Property Valuation Model

This module provides enhanced machine learning models for accurate property valuation.
It uses ensemble methods, feature engineering, and advanced evaluation metrics to
provide more accurate price predictions than basic linear models.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import OneHotEncoder, StandardScaler, MinMaxScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.impute import SimpleImputer
import pickle
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create models directory if it doesn't exist
MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
os.makedirs(MODELS_DIR, exist_ok=True)

def train_advanced_valuation_model(df, model_type='random_forest'):
    """
    Train an advanced property valuation model using ensemble methods
    
    Args:
        df: DataFrame with property data
        model_type: Type of model to train ('random_forest' or 'gradient_boosting')
    
    Returns:
        tuple: (trained_model, preprocessor, features, evaluation_metrics)
    """
    if df.empty or len(df) < 50:  # Need sufficient data for training
        logger.warning("Not enough data for training (minimum 50 records required)")
        return None, None, None, None
    
    try:
        # Define features with importance weights
        # These weights will be used for feature selection and importance analysis
        feature_weights = {
            'bedrooms': 0.7,
            'bathrooms': 0.8,
            'sqft': 0.9,
            'year_built': 0.6,
            'city': 0.8,
            'property_type': 0.7,
            'days_on_market': 0.4,
            'latitude': 0.3,
            'longitude': 0.3
        }
        
        # Select features that exist in the dataframe
        features = [f for f in feature_weights.keys() if f in df.columns]
        
        if len(features) < 3:
            logger.warning(f"Not enough features available. Found only: {features}")
            return None, None, None, None
        
        logger.info(f"Training with features: {features}")
        
        # Classify features
        numeric_features = []
        categorical_features = []
        
        for feature in features:
            if pd.api.types.is_numeric_dtype(df[feature]):
                numeric_features.append(feature)
            else:
                categorical_features.append(feature)
        
        # Prepare the data
        X = df[features].copy()
        y = df['price']
        
        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Create preprocessing pipeline
        numeric_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ])
        
        categorical_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='most_frequent')),
            ('onehot', OneHotEncoder(handle_unknown='ignore'))
        ])
        
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, numeric_features),
                ('cat', categorical_transformer, categorical_features)
            ]
        )
        
        # Choose model type
        if model_type == 'gradient_boosting':
            model = GradientBoostingRegressor(
                n_estimators=200,
                learning_rate=0.1,
                max_depth=5,
                min_samples_split=5,
                min_samples_leaf=2,
                max_features='sqrt',
                random_state=42
            )
        else:  # Default to Random Forest
            model = RandomForestRegressor(
                n_estimators=150,
                max_depth=15,
                min_samples_split=5,
                min_samples_leaf=2,
                max_features='sqrt',
                bootstrap=True,
                random_state=42
            )
        
        # Create and train the pipeline
        full_pipeline = Pipeline([
            ('preprocessor', preprocessor),
            ('model', model)
        ])
        
        # Train the model
        logger.info(f"Training {model_type} model with {len(X_train)} samples")
        full_pipeline.fit(X_train, y_train)
        
        # Evaluate the model
        y_pred = full_pipeline.predict(X_test)
        
        # Calculate metrics
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        
        # Perform cross-validation for more robust evaluation
        cv_scores = cross_val_score(full_pipeline, X, y, cv=5, scoring='neg_mean_absolute_error')
        cv_mae = -np.mean(cv_scores)
        
        # Create evaluation metrics dictionary
        metrics = {
            'mae': mae,
            'rmse': rmse,
            'r2': r2,
            'cv_mae': cv_mae,
            'training_samples': len(X_train),
            'test_samples': len(X_test),
            'model_type': model_type
        }
        
        logger.info(f"Model evaluation: MAE=${mae:,.0f}, RMSE=${rmse:,.0f}, R²={r2:.3f}, CV MAE=${cv_mae:,.0f}")
        
        # Save the model if desired
        model_path = os.path.join(MODELS_DIR, f'property_valuation_{model_type}.pkl')
        with open(model_path, 'wb') as f:
            pickle.dump(full_pipeline, f)
        logger.info(f"Model saved to {model_path}")
        
        return full_pipeline, preprocessor, features, metrics
        
    except Exception as e:
        logger.error(f"Error training model: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return None, None, None, None

def predict_property_value(model, features, property_data):
    """
    Predict property value using the advanced valuation model
    
    Args:
        model: Trained valuation model (Pipeline object)
        features: List of features used by the model
        property_data: Dictionary with property features
        
    Returns:
        dict: Dictionary with prediction and confidence interval
    """
    if model is None:
        logger.warning("No model provided for prediction")
        return None
    
    try:
        # Create a DataFrame with the property data
        property_df = pd.DataFrame([property_data])
        
        # Ensure all required features are present
        missing_features = [f for f in features if f not in property_df.columns]
        if missing_features:
            logger.warning(f"Missing features for prediction: {missing_features}")
            # Add missing features with None values
            for feature in missing_features:
                property_df[feature] = None
        
        # Make prediction
        predicted_price = model.predict(property_df[features])[0]
        
        # For Random Forest or Gradient Boosting, we can generate prediction intervals
        # by extracting individual predictions from each tree in the ensemble
        if hasattr(model.named_steps['model'], 'estimators_'):
            # If we have a RandomForestRegressor or similar ensemble method
            individual_predictions = []
            
            # Use the preprocessed data
            preprocessed_data = model.named_steps['preprocessor'].transform(property_df[features])
            
            for estimator in model.named_steps['model'].estimators_:
                individual_predictions.append(estimator.predict(preprocessed_data)[0])
            
            # Calculate confidence intervals
            prediction_std = np.std(individual_predictions)
            lower_bound = predicted_price - 1.96 * prediction_std
            upper_bound = predicted_price + 1.96 * prediction_std
            
            # Ensure lower bound is not negative
            lower_bound = max(0, lower_bound)
            
            # Calculate confidence level based on standard deviation
            confidence_level = 100 - min(80, (prediction_std / predicted_price) * 100)
            
            return {
                'predicted_price': predicted_price,
                'lower_bound': lower_bound,
                'upper_bound': upper_bound,
                'confidence_level': confidence_level,
                'prediction_std': prediction_std
            }
        else:
            # For other model types that don't have estimators, just return the prediction
            return {
                'predicted_price': predicted_price,
                'lower_bound': predicted_price * 0.9,  # Estimated lower bound
                'upper_bound': predicted_price * 1.1,  # Estimated upper bound
                'confidence_level': 70  # Default confidence level
            }
    
    except Exception as e:
        logger.error(f"Error predicting property value: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return None

def extract_feature_importance(model, features):
    """
    Extract feature importance from the trained model
    
    Args:
        model: Trained model
        features: List of feature names
        
    Returns:
        DataFrame: Feature importance data
    """
    try:
        # If the model is a Pipeline with a RandomForestRegressor or GradientBoostingRegressor
        if hasattr(model, 'named_steps') and hasattr(model.named_steps['model'], 'feature_importances_'):
            model_step = model.named_steps['model']
            
            # For Random Forest and Gradient Boosting, feature importances are available directly
            importances = model_step.feature_importances_
            
            # The challenge is mapping these back to the original features after preprocessing
            # We'll use a simplified approach for now
            if hasattr(model.named_steps['preprocessor'], 'transformers_'):
                # Get the preprocessor
                preprocessor = model.named_steps['preprocessor']
                
                # Get all transformed feature names
                transformed_features = []
                
                for name, transformer, cols in preprocessor.transformers_:
                    if name == 'num':
                        transformed_features.extend(cols)
                    elif name == 'cat' and hasattr(transformer, 'named_steps') and 'onehot' in transformer.named_steps:
                        onehot = transformer.named_steps['onehot']
                        if hasattr(onehot, 'get_feature_names_out'):
                            for col in cols:
                                # Get OneHot encoded feature names
                                encoded_names = onehot.get_feature_names_out([col])
                                for encoded_name in encoded_names:
                                    transformed_features.append(f"{col}_{encoded_name.split('_')[-1]}")
                        else:
                            # Fallback for older scikit-learn versions
                            for col in cols:
                                transformed_features.append(f"{col}")
            
                # If the number of transformed features matches the number of importances
                if len(transformed_features) == len(importances):
                    # Create a DataFrame with feature importances
                    importance_df = pd.DataFrame({
                        'feature': transformed_features,
                        'importance': importances
                    })
                    return importance_df.sort_values('importance', ascending=False)
            
            # Fallback: just return numeric indices if we can't map to feature names
            importance_df = pd.DataFrame({
                'feature_index': np.arange(len(importances)),
                'importance': importances
            })
            return importance_df.sort_values('importance', ascending=False)
            
        return None
    
    except Exception as e:
        logger.error(f"Error extracting feature importance: {str(e)}")
        return None

def get_comparable_properties(df, property_data, model=None, top_n=5):
    """
    Find comparable properties based on similarities and model
    
    Args:
        df: DataFrame with property data
        property_data: Dictionary with target property features
        model: Trained valuation model (optional)
        top_n: Number of comparable properties to return
        
    Returns:
        DataFrame: Top comparable properties
    """
    if df.empty:
        return pd.DataFrame()
    
    try:
        # Create a DataFrame for the property data
        property_df = pd.DataFrame([property_data])
        
        # Get key features for similarity
        key_features = ['bedrooms', 'bathrooms', 'sqft', 'property_type']
        
        # Add location features if available
        if 'city' in df.columns and 'city' in property_data:
            key_features.append('city')
        
        if 'latitude' in df.columns and 'longitude' in df.columns and \
           'latitude' in property_data and 'longitude' in property_data:
            location_based = True
        else:
            location_based = False
        
        # Filter out properties with missing key features
        df_filtered = df.dropna(subset=[f for f in key_features if f in df.columns])
        
        if df_filtered.empty:
            return pd.DataFrame()
        
        # Calculate similarity scores
        scores = []
        
        for idx, row in df_filtered.iterrows():
            score = 0
            
            # Property type (exact match)
            if 'property_type' in key_features and row['property_type'] == property_data.get('property_type'):
                score += 30
            
            # Location (exact match or distance-based)
            if 'city' in key_features and row['city'] == property_data.get('city'):
                score += 25
            
            # Distance-based scoring if coordinates available
            if location_based:
                # Calculate geographic distance
                lat_diff = row['latitude'] - property_data['latitude']
                long_diff = row['longitude'] - property_data['longitude']
                distance = np.sqrt(lat_diff**2 + long_diff**2)
                
                # Closer properties get higher scores
                # Convert distance to a 0-20 score (higher for closer properties)
                distance_score = 20 * np.exp(-distance * 100)
                score += distance_score
            
            # Bedrooms (closer = better score)
            if 'bedrooms' in key_features:
                bed_diff = abs(row['bedrooms'] - property_data.get('bedrooms', 0))
                score += 15 * np.exp(-0.5 * bed_diff)
            
            # Bathrooms (closer = better score)
            if 'bathrooms' in key_features:
                bath_diff = abs(row['bathrooms'] - property_data.get('bathrooms', 0))
                score += 15 * np.exp(-0.5 * bath_diff)
            
            # Square footage (closer = better score)
            if 'sqft' in key_features:
                sqft_target = property_data.get('sqft', 0)
                if sqft_target > 0:
                    sqft_ratio = min(row['sqft'] / sqft_target, sqft_target / row['sqft'])
                    score += 15 * sqft_ratio
            
            # Year built (if available)
            if 'year_built' in df.columns and 'year_built' in property_data:
                year_diff = abs(row['year_built'] - property_data.get('year_built', 0))
                score += 10 * np.exp(-0.05 * year_diff)
            
            scores.append((idx, score))
        
        # Sort by score (descending)
        scores.sort(key=lambda x: x[1], reverse=True)
        
        # Get top comparable properties
        top_indices = [idx for idx, _ in scores[:top_n]]
        comparable_properties = df_filtered.loc[top_indices].copy()
        
        # Add similarity score to the results
        comparable_properties['similarity_score'] = [score for _, score in scores[:top_n]]
        
        # If we have a valuation model, add price delta
        if model is not None and hasattr(model, 'predict'):
            try:
                property_features = [f for f in key_features if f in df.columns]
                predicted_price = model.predict(property_df[property_features])[0]
                
                comparable_properties['price_diff'] = comparable_properties['price'] - predicted_price
                comparable_properties['price_diff_pct'] = (comparable_properties['price_diff'] / predicted_price) * 100
            except Exception as e:
                logger.warning(f"Error calculating price differences: {str(e)}")
        
        return comparable_properties
    
    except Exception as e:
        logger.error(f"Error finding comparable properties: {str(e)}")
        return pd.DataFrame()

def evaluate_property_investment(property_data, market_trends=None):
    """
    Evaluate investment potential of a property
    
    Args:
        property_data: Dictionary with property features including price
        market_trends: Market trend data (optional)
        
    Returns:
        dict: Investment metrics
    """
    try:
        # Extract property price
        price = property_data.get('price', 0)
        if price <= 0:
            logger.warning("Invalid property price for investment evaluation")
            return None
        
        # Default values if not provided
        rental_estimate = property_data.get('rental_estimate', price * 0.007)  # 0.7% of price monthly
        property_type = property_data.get('property_type', 'Single Family')
        city = property_data.get('city', 'Unknown')
        
        # Customize appreciation rate based on property type and location
        base_appreciation = 0.03  # 3% annual appreciation
        
        # Adjust based on property type
        if 'Condo' in property_type:
            appreciation_factor = 0.9  # Condos appreciate slightly slower
        elif 'Multi-Family' in property_type:
            appreciation_factor = 1.1  # Multi-family appreciates faster
        else:
            appreciation_factor = 1.0
        
        # Adjust based on market trends if available
        if market_trends is not None and city in market_trends:
            city_trend = market_trends[city]
            # Use recent appreciation rate if available
            if 'recent_appreciation' in city_trend:
                market_appreciation = city_trend['recent_appreciation']
                # Clip to reasonable values (0-15%)
                market_appreciation = max(0, min(0.15, market_appreciation))
            else:
                market_appreciation = base_appreciation
        else:
            market_appreciation = base_appreciation
        
        # Calculate final appreciation rate
        appreciation_rate = market_appreciation * appreciation_factor
        
        # Investment parameters
        down_payment_pct = 0.2  # 20% down payment
        down_payment = price * down_payment_pct
        loan_amount = price - down_payment
        
        # Loan terms
        interest_rate = 0.06  # 6% interest rate
        loan_term_years = 30
        
        # Calculate monthly mortgage payment
        monthly_mortgage = (loan_amount * (interest_rate / 12) * (1 + interest_rate / 12) ** (loan_term_years * 12)) / ((1 + interest_rate / 12) ** (loan_term_years * 12) - 1)
        
        # Estimate annual expenses
        property_tax_rate = 0.01  # 1% property tax
        insurance_rate = 0.005  # 0.5% insurance
        maintenance_rate = 0.01  # 1% maintenance
        vacancy_rate = 0.08  # 8% vacancy
        
        # Calculate annual cash flow
        annual_rental_income = rental_estimate * 12
        annual_property_tax = price * property_tax_rate
        annual_insurance = price * insurance_rate
        annual_maintenance = price * maintenance_rate
        annual_vacancy_cost = annual_rental_income * vacancy_rate
        
        annual_expenses = annual_property_tax + annual_insurance + annual_maintenance + annual_vacancy_cost
        annual_mortgage_payments = monthly_mortgage * 12
        annual_cash_flow = annual_rental_income - annual_expenses - annual_mortgage_payments
        
        # Calculate investment metrics
        monthly_cash_flow = annual_cash_flow / 12
        cash_on_cash_return = (annual_cash_flow / down_payment) * 100
        cap_rate = ((annual_rental_income - annual_expenses) / price) * 100
        gross_rent_multiplier = price / annual_rental_income
        
        # 5-year forecast
        forecast_years = 5
        future_value = price * (1 + appreciation_rate) ** forecast_years
        
        # Principal paid down (simplified calculation)
        principal_paid = (monthly_mortgage * 12 * forecast_years) - (loan_amount * interest_rate * forecast_years)
        remaining_loan = loan_amount - principal_paid
        
        # Equity after 5 years
        equity_5yr = future_value - remaining_loan
        
        # Total ROI
        total_investment = down_payment + annual_expenses  # Down payment + initial expenses
        total_return = (equity_5yr - down_payment) + (annual_cash_flow * forecast_years)
        total_roi = (total_return / total_investment) * 100
        
        # Annualized ROI
        annualized_roi = ((1 + total_roi / 100) ** (1 / forecast_years) - 1) * 100
        
        # Return all investment metrics
        return {
            'purchase_price': price,
            'monthly_rental_income': rental_estimate,
            'down_payment': down_payment,
            'loan_amount': loan_amount,
            'monthly_mortgage': monthly_mortgage,
            'annual_expenses': annual_expenses,
            'annual_cash_flow': annual_cash_flow,
            'monthly_cash_flow': monthly_cash_flow,
            'cash_on_cash_return': cash_on_cash_return,
            'cap_rate': cap_rate,
            'gross_rent_multiplier': gross_rent_multiplier,
            'appreciation_rate': appreciation_rate * 100,  # Convert to percentage
            'future_value_5yr': future_value,
            'equity_5yr': equity_5yr,
            'total_roi_5yr': total_roi,
            'annualized_roi': annualized_roi,
            'expense_breakdown': {
                'property_tax': annual_property_tax,
                'insurance': annual_insurance,
                'maintenance': annual_maintenance,
                'vacancy': annual_vacancy_cost
            }
        }
    
    except Exception as e:
        logger.error(f"Error evaluating property investment: {str(e)}")
        return None