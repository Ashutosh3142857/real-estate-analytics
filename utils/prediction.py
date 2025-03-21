import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression, Lasso, Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error
from sklearn.inspection import permutation_importance
import joblib
import os
import shap
import json

def train_price_prediction_model(df, model_type='advanced'):
    """
    Train a machine learning model to predict property prices
    
    Args:
        df: DataFrame with property data
        model_type: String indicating which model to use ('simple', 'intermediate', or 'advanced')
    
    Returns:
        tuple: (trained_model, preprocessor, features, mae, r2, feature_importance)
    """
    if df.empty or len(df) < 50:  # Need sufficient data for training
        return None, None, None, None, None, None
    
    try:
        # Features for prediction
        basic_features = ['bedrooms', 'bathrooms', 'sqft', 'year_built', 'city', 'property_type']
        
        # Advanced features that might be available
        advanced_features = []
        for feature in ['garage_spaces', 'lot_size', 'stories', 'pool', 'fireplace', 'has_view', 'condition']:
            if feature in df.columns:
                advanced_features.append(feature)
        
        # Combine features based on what's available
        if model_type == 'simple' or not advanced_features:
            features = basic_features
        else:
            features = basic_features + advanced_features
            
        # Check if all required features are available
        for feature in basic_features:
            if feature not in df.columns:
                return None, None, None, None, None, None
        
        # Prepare the data
        X = df[features].copy()
        y = df['price']
        
        # Handle missing values, if any
        X = X.fillna(X.median(numeric_only=True))
        
        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Create preprocessor
        categorical_features = [col for col in X.columns if X[col].dtype == 'object']
        numeric_features = [col for col in X.columns if col not in categorical_features]
        
        # Define transformers
        categorical_transformer = OneHotEncoder(handle_unknown='ignore')
        numeric_transformer = StandardScaler()
        
        # Create column transformer
        preprocessor = ColumnTransformer(
            transformers=[
                ('cat', categorical_transformer, categorical_features),
                ('num', numeric_transformer, numeric_features)
            ]
        )
        
        # Define model based on complexity level
        if model_type == 'simple':
            regressor = LinearRegression()
        elif model_type == 'intermediate':
            regressor = RandomForestRegressor(n_estimators=100, random_state=42)
        else:  # advanced
            regressor = GradientBoostingRegressor(
                n_estimators=200, 
                learning_rate=0.1, 
                max_depth=5, 
                random_state=42,
                subsample=0.8,
                max_features=0.8
            )
        
        # Create and train the model pipeline
        model = Pipeline([
            ('preprocessor', preprocessor),
            ('regressor', regressor)
        ])
        
        # Fit the model
        model.fit(X_train, y_train)
        
        # Evaluate the model
        y_pred = model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        
        # Compute feature importance
        if model_type == 'simple':
            # For linear models, use coefficients
            feature_importance = _get_linear_feature_importance(model, features, preprocessor)
        else:
            # For tree-based models, use built-in feature importance
            feature_importance = _get_tree_feature_importance(model, features, X_test)
        
        # Save model metadata with feature importance
        model_metadata = {
            'model_type': model_type,
            'features': features,
            'performance': {
                'mae': float(mae),
                'rmse': float(rmse),
                'r2': float(r2)
            },
            'feature_importance': {str(k): float(v) for k, v in feature_importance.items()}
        }
        
        # Return all components
        return model, preprocessor, features, mae, r2, feature_importance
        
    except Exception as e:
        print(f"Error training model: {e}")
        return None, None, None, None, None, None

def _get_linear_feature_importance(model, features, preprocessor):
    """Extract feature importance from linear model coefficients"""
    # Get feature names from preprocessor
    feature_names = preprocessor.get_feature_names_out()
    
    # Extract coefficients
    coefficients = model.named_steps['regressor'].coef_
    
    # Map coefficients to features
    importance_dict = {}
    
    # For categorical features, sum the absolute values of coefficients
    cat_features = [f for f in features if f in preprocessor.transformers_[0][2]]
    for feature in cat_features:
        feature_cols = [col for col in feature_names if col.startswith(f'cat__{feature}')]
        importance = sum(abs(coefficients[feature_names.get_loc(col)]) for col in feature_cols)
        importance_dict[feature] = importance
    
    # For numeric features, use absolute coefficient values
    num_features = [f for f in features if f in preprocessor.transformers_[1][2]]
    for feature in num_features:
        feature_col = f'num__{feature}'
        importance = abs(coefficients[feature_names.get_loc(feature_col)])
        importance_dict[feature] = importance
    
    # Normalize importance to sum to 100
    total_importance = sum(importance_dict.values())
    if total_importance > 0:
        importance_dict = {k: (v / total_importance) * 100 for k, v in importance_dict.items()}
    
    return importance_dict

def _get_tree_feature_importance(model, features, X_test):
    """Extract feature importance from tree-based models"""
    # Get importances
    importances = model.named_steps['regressor'].feature_importances_
    
    # Get preprocessed feature names
    feature_names = model.named_steps['preprocessor'].get_feature_names_out()
    
    # Map importances to original features
    importance_dict = {}
    
    # For categorical features, sum the values
    cat_features = [f for f in features if isinstance(f, str) and f in X_test.select_dtypes(include=['object']).columns]
    for feature in cat_features:
        feature_cols = [i for i, name in enumerate(feature_names) if name.startswith(f'cat__{feature}')]
        importance = sum(importances[i] for i in feature_cols)
        importance_dict[feature] = importance
    
    # For numeric features, use direct values
    num_features = [f for f in features if f not in cat_features]
    for feature in num_features:
        feature_cols = [i for i, name in enumerate(feature_names) if name == f'num__{feature}']
        if feature_cols:
            importance_dict[feature] = importances[feature_cols[0]]
    
    # Normalize to sum to 100
    total_importance = sum(importance_dict.values())
    if total_importance > 0:
        importance_dict = {k: (v / total_importance) * 100 for k, v in importance_dict.items()}
    
    # Sort by importance (descending)
    importance_dict = dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True))
    
    return importance_dict

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

def get_property_value_explainer(model, features, property_data, comparable_properties=None):
    """
    Generate detailed explanation for property valuation prediction
    
    Args:
        model: Trained model
        features: List of feature names used by the model
        property_data: Dictionary with property features
        comparable_properties: Optional DataFrame with comparable properties
        
    Returns:
        dict: Explanation data including feature impacts, comparables, and market position
    """
    try:
        # Get the prediction
        prediction = predict_property_price(model, features, property_data)
        if prediction is None:
            return None
            
        # Create a dataframe with property data
        property_df = pd.DataFrame([property_data])
        
        # Get feature importance and contribution to prediction
        feature_contributions = {}
        
        if hasattr(model, 'named_steps') and 'regressor' in model.named_steps:
            regressor = model.named_steps['regressor']
            
            # For tree-based models
            if hasattr(regressor, 'feature_importances_'):
                # Get feature names after preprocessing
                feature_names = model.named_steps['preprocessor'].get_feature_names_out()
                
                # Create SHAP explainer for more accurate feature importance
                try:
                    # Create a background dataset
                    if comparable_properties is not None and len(comparable_properties) > 10:
                        background_data = comparable_properties[features].sample(min(10, len(comparable_properties)))
                    else:
                        background_data = property_df.copy()
                    
                    # Transform the data
                    transformed_background = model.named_steps['preprocessor'].transform(background_data)
                    transformed_instance = model.named_steps['preprocessor'].transform(property_df)
                    
                    # Create explainer
                    explainer = shap.Explainer(regressor, transformed_background)
                    shap_values = explainer(transformed_instance)
                    
                    # Map SHAP values back to original features
                    for feature in features:
                        if feature in property_data:
                            # For categorical features, we need to sum the SHAP values of all one-hot encoded columns
                            if feature in ['city', 'property_type'] or property_df[feature].dtype == 'object':
                                feature_cols = [i for i, name in enumerate(feature_names) if name.startswith(f'cat__{feature}')]
                                contribution = sum(shap_values.values[0][i] for i in feature_cols)
                            else:
                                feature_cols = [i for i, name in enumerate(feature_names) if name == f'num__{feature}']
                                contribution = shap_values.values[0][feature_cols[0]] if feature_cols else 0
                                
                            feature_contributions[feature] = float(contribution)
                            
                except Exception as e:
                    print(f"Error creating SHAP explainer: {e}")
                    # Fallback to simpler approach
                    feature_importances = regressor.feature_importances_
                    for i, feature in enumerate(features):
                        feature_contributions[feature] = float(property_df[feature].iloc[0] * feature_importances[i])
            
            # For linear models
            elif hasattr(regressor, 'coef_'):
                # Get coefficients
                coefficients = regressor.coef_
                
                # Get feature names after preprocessing
                feature_names = model.named_steps['preprocessor'].get_feature_names_out()
                
                # Calculate contribution of each feature
                for feature in features:
                    if feature in property_data:
                        # For categorical features
                        if feature in ['city', 'property_type'] or property_df[feature].dtype == 'object':
                            # Find the one-hot encoded column for this feature value
                            feature_value = property_df[feature].iloc[0]
                            feature_col = f'cat__{feature}_{feature_value}'
                            
                            # Find the coefficient index
                            try:
                                idx = list(feature_names).index(feature_col)
                                contribution = coefficients[idx] * 1  # Binary feature is 1 when active
                            except (ValueError, IndexError):
                                contribution = 0
                        else:
                            # For numerical features
                            feature_col = f'num__{feature}'
                            try:
                                idx = list(feature_names).index(feature_col)
                                # For standardized features, need to consider the scaling
                                contribution = coefficients[idx] * property_df[feature].iloc[0]
                            except (ValueError, IndexError):
                                contribution = 0
                                
                        feature_contributions[feature] = float(contribution)
        
        # Sort features by absolute contribution
        feature_contributions = dict(sorted(feature_contributions.items(), 
                                          key=lambda x: abs(x[1]), 
                                          reverse=True))
        
        # Calculate total contribution
        total_contribution = sum(feature_contributions.values())
        
        # Convert contributions to percentages
        feature_impacts = {}
        for feature, contribution in feature_contributions.items():
            if total_contribution != 0:
                impact_pct = (abs(contribution) / abs(total_contribution)) * 100
            else:
                impact_pct = 0
                
            direction = "positive" if contribution > 0 else "negative"
            feature_impacts[feature] = {
                "impact_percentage": min(max(impact_pct, 0), 100),  # Cap between 0-100
                "direction": direction,
                "value": property_data.get(feature)
            }
        
        # Calculate confidence interval
        confidence_interval = {
            "lower": max(prediction * 0.9, 0),
            "upper": prediction * 1.1
        }
        
        # Compare with similar properties if available
        comparables_info = []
        if comparable_properties is not None and not comparable_properties.empty:
            # Calculate similarity to each comparable property
            for _, comp in comparable_properties.iterrows():
                similarity_score = calculate_property_similarity(property_data, comp, features)
                
                if similarity_score >= 0.7:  # Only include reasonably similar properties
                    comparables_info.append({
                        "id": comp.get("id", None) or comp.get("property_id", None),
                        "address": comp.get("address", "Unknown"),
                        "price": float(comp.get("price", 0)),
                        "bedrooms": int(comp.get("bedrooms", 0)),
                        "bathrooms": float(comp.get("bathrooms", 0)),
                        "sqft": float(comp.get("sqft", 0)),
                        "property_type": comp.get("property_type", "Unknown"),
                        "similarity_score": float(similarity_score)
                    })
            
            # Sort by similarity score (descending)
            comparables_info = sorted(comparables_info, key=lambda x: x["similarity_score"], reverse=True)[:5]
        
        # Compile all explanation data
        explanation = {
            "predicted_price": float(prediction),
            "confidence_interval": confidence_interval,
            "feature_impacts": feature_impacts,
            "comparable_properties": comparables_info
        }
        
        return explanation
        
    except Exception as e:
        print(f"Error generating property valuation explanation: {e}")
        return None

def calculate_property_similarity(property1, property2, features):
    """
    Calculate similarity score between two properties
    
    Args:
        property1: Dictionary or Series with first property features
        property2: Dictionary or Series with second property features
        features: List of features to consider for similarity
        
    Returns:
        float: Similarity score between 0 and 1
    """
    try:
        # Define feature weights
        feature_weights = {
            'sqft': 0.25,
            'bedrooms': 0.15,
            'bathrooms': 0.15,
            'year_built': 0.1,
            'city': 0.2,
            'property_type': 0.15
        }
        
        # Add default weights for any other features
        for feature in features:
            if feature not in feature_weights:
                feature_weights[feature] = 0.05
                
        # Normalize weights to sum to 1
        total_weight = sum(feature_weights.values())
        feature_weights = {k: v/total_weight for k, v in feature_weights.items()}
        
        # Calculate weighted similarity
        similarity = 0
        
        for feature in features:
            if feature in property1 and feature in property2:
                # Get values (convert to appropriate type)
                val1 = property1[feature]
                val2 = property2[feature]
                
                # Skip if either value is missing
                if pd.isna(val1) or pd.isna(val2):
                    continue
                    
                # For categorical features
                if feature in ['city', 'property_type'] or isinstance(val1, str):
                    # Exact match gets full similarity
                    feature_sim = 1 if str(val1).lower() == str(val2).lower() else 0
                
                # For numerical features
                else:
                    try:
                        # Convert to float
                        num1 = float(val1)
                        num2 = float(val2)
                        
                        # Normalize by feature
                        if feature == 'bedrooms' or feature == 'bathrooms':
                            # Difference of 1 bedroom/bathroom = 0.75 similarity
                            feature_sim = max(0, 1 - abs(num1 - num2) * 0.25)
                        elif feature == 'sqft':
                            # 20% difference = 0.5 similarity
                            max_val = max(num1, num2)
                            min_val = min(num1, num2)
                            if max_val > 0:
                                feature_sim = min(1, min_val / max_val)
                            else:
                                feature_sim = 1
                        elif feature == 'year_built':
                            # 10 years difference = 0.5 similarity
                            feature_sim = max(0, 1 - abs(num1 - num2) / 20)
                        else:
                            # Default numerical comparison
                            max_val = max(abs(num1), abs(num2))
                            if max_val > 0:
                                feature_sim = max(0, 1 - abs(num1 - num2) / max_val)
                            else:
                                feature_sim = 1
                    except (ValueError, TypeError):
                        feature_sim = 0
                
                # Add weighted similarity
                similarity += feature_sim * feature_weights.get(feature, 0)
        
        return similarity
        
    except Exception as e:
        print(f"Error calculating property similarity: {e}")
        return 0

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

def train_lead_scoring_model(leads_df):
    """
    Train an ML model to score leads based on their characteristics and behaviors
    
    Args:
        leads_df: DataFrame containing lead data with features and target scores
        
    Returns:
        tuple: (model, features, feature_importance, accuracy)
    """
    if leads_df is None or len(leads_df) < 20:  # Need sufficient data for training
        return None, None, None, None
    
    try:
        # Define features to use for scoring
        categorical_features = ['source', 'property_interest', 'price_range', 'urgency', 'credit_score_range']
        numeric_features = ['website_visits', 'viewed_listings', 'saved_properties', 'requested_showings']
        
        # Add pre_approved status as a binary feature
        leads_df['pre_approved_binary'] = leads_df['pre_approved'].apply(
            lambda x: 1 if x == 'Yes' else 0.5 if x == 'In Process' else 0
        )
        numeric_features.append('pre_approved_binary')
        
        # Combine all features
        features = categorical_features + numeric_features
        
        # Ensure all required features are available
        for feature in features:
            if feature not in leads_df.columns:
                print(f"Missing required feature: {feature}")
                return None, None, None, None
        
        # Prepare target variable (lead score)
        if 'lead_score' in leads_df.columns:
            y = leads_df['lead_score']
        else:
            # If no lead score, try to use status as a proxy
            if 'status' in leads_df.columns:
                # Convert status to numeric scores
                status_scores = {
                    'Converted': 100,
                    'Qualified': 80,
                    'Nurturing': 60,
                    'Contacted': 40,
                    'New': 20,
                    'Lost': 10
                }
                y = leads_df['status'].map(status_scores).fillna(50)
            else:
                print("No target variable (lead_score or status) available")
                return None, None, None, None
        
        # Prepare features
        X = leads_df[features].copy()
        
        # Handle missing values
        for col in numeric_features:
            X[col] = X[col].fillna(0)
            
        for col in categorical_features:
            X[col] = X[col].fillna('Unknown')
        
        # Split the data for training and evaluation
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Create preprocessing pipeline
        categorical_transformer = OneHotEncoder(handle_unknown='ignore')
        numeric_transformer = StandardScaler()
        
        preprocessor = ColumnTransformer(
            transformers=[
                ('cat', categorical_transformer, categorical_features),
                ('num', numeric_transformer, numeric_features)
            ]
        )
        
        # Choose model - GradientBoostingRegressor works well for lead scoring
        regressor = GradientBoostingRegressor(
            n_estimators=100, 
            learning_rate=0.1,
            max_depth=3,
            random_state=42
        )
        
        # Create pipeline
        model = Pipeline([
            ('preprocessor', preprocessor),
            ('regressor', regressor)
        ])
        
        # Train the model
        model.fit(X_train, y_train)
        
        # Evaluate the model
        y_pred = model.predict(X_test)
        
        # Calculate metrics
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        
        # Get feature importances
        feature_importances = _get_tree_feature_importance(model, features, X_test)
        
        # Calculate accuracy (within ±10 points on a 100-point scale)
        within_range = np.abs(y_test - y_pred) <= 10
        accuracy = within_range.mean() * 100
        
        return model, features, feature_importances, accuracy
        
    except Exception as e:
        print(f"Error training lead scoring model: {e}")
        return None, None, None, None

def predict_lead_score(model, features, lead_data):
    """
    Predict a lead score based on lead characteristics and behaviors
    
    Args:
        model: Trained lead scoring model
        features: List of features used by the model
        lead_data: Dictionary with lead features
        
    Returns:
        float: Predicted lead score (0-100)
    """
    if model is None:
        return None
    
    try:
        # Create a DataFrame with the lead data
        lead_df = pd.DataFrame([lead_data])
        
        # Handle pre_approved field if present
        if 'pre_approved' in lead_df.columns and 'pre_approved_binary' not in lead_df.columns:
            lead_df['pre_approved_binary'] = lead_df['pre_approved'].apply(
                lambda x: 1.0 if x == 'Yes' else 0.5 if x == 'In Process' else 0.0
            )
            
        # Ensure all required features are present
        missing_features = [f for f in features if f not in lead_df.columns]
        if missing_features:
            # For categorical features, set to 'Unknown'
            # For numeric features, set to 0
            for feature in missing_features:
                if feature in ['website_visits', 'viewed_listings', 'saved_properties', 
                               'requested_showings', 'pre_approved_binary']:
                    lead_df[feature] = 0
                else:
                    lead_df[feature] = 'Unknown'
        
        # Predict the score
        score = model.predict(lead_df[features])[0]
        
        # Ensure score is within 0-100 range
        score = min(max(score, 0), 100)
        
        return round(score)
        
    except Exception as e:
        print(f"Error predicting lead score: {e}")
        return None

def get_lead_insights(model, features, lead_data, feature_importance=None):
    """
    Generate insights and recommendations based on lead data and model
    
    Args:
        model: Trained lead scoring model
        features: List of features used by the model
        lead_data: Dictionary with lead features
        feature_importance: Optional dict with feature importance values
        
    Returns:
        dict: Lead insights including score factors and recommendations
    """
    try:
        # Get the lead score
        lead_score = predict_lead_score(model, features, lead_data)
        if lead_score is None:
            return None
            
        # Create a dataframe with lead data
        lead_df = pd.DataFrame([lead_data])
        
        # Calculate feature contributions if possible
        feature_contributions = {}
        
        # If we have an ensemble model and preprocessor
        if hasattr(model, 'named_steps') and 'regressor' in model.named_steps:
            regressor = model.named_steps['regressor']
            
            if hasattr(regressor, 'feature_importances_'):
                # Get feature names after preprocessing
                preprocessor = model.named_steps['preprocessor']
                feature_names = preprocessor.get_feature_names_out()
                
                # Transform the lead data
                transformed_lead = preprocessor.transform(lead_df)
                
                # Try to use SHAP for explanation
                try:
                    explainer = shap.Explainer(regressor)
                    shap_values = explainer(transformed_lead)
                    
                    # Map SHAP values back to original features
                    for feature in features:
                        if feature in lead_data:
                            # For categorical features
                            if feature in ['source', 'property_interest', 'price_range', 'urgency', 'credit_score_range']:
                                # Find all columns related to this feature
                                feature_cols = [i for i, name in enumerate(feature_names) if name.startswith(f'cat__{feature}')]
                                contribution = sum(shap_values.values[0][i] for i in feature_cols)
                            else:
                                # For numeric features
                                feature_cols = [i for i, name in enumerate(feature_names) if name == f'num__{feature}']
                                contribution = shap_values.values[0][feature_cols[0]] if feature_cols else 0
                                
                            feature_contributions[feature] = float(contribution)
                            
                except Exception as e:
                    print(f"Error using SHAP for lead insights: {e}")
                    # If SHAP fails, use feature importance as a fallback
                    if feature_importance:
                        feature_contributions = {f: feature_importance.get(f, 0) for f in features if f in lead_data}
        
        # If we couldn't get contributions but have importance, use that
        if not feature_contributions and feature_importance:
            # Scale importance by the value (approximate)
            feature_contributions = {}
            for feature in features:
                if feature in lead_data and feature in feature_importance:
                    value = lead_data[feature]
                    importance = feature_importance[feature]
                    
                    # For numeric features, higher values generally mean higher contribution
                    if feature in ['website_visits', 'viewed_listings', 'saved_properties', 
                                  'requested_showings', 'pre_approved_binary']:
                        # Normalize relative to typical ranges
                        if feature == 'website_visits':
                            norm_value = min(float(value) / 10, 1)  # Assume 10+ visits is high
                        elif feature == 'viewed_listings':
                            norm_value = min(float(value) / 20, 1)  # Assume 20+ listings is high
                        elif feature == 'saved_properties':
                            norm_value = min(float(value) / 5, 1)   # Assume 5+ saved props is high
                        elif feature == 'requested_showings':
                            norm_value = min(float(value) / 3, 1)   # Assume 3+ showings is high
                        elif feature == 'pre_approved_binary':
                            norm_value = float(value)                # Already normalized (0-1)
                        else:
                            norm_value = 0.5  # Default
                            
                        feature_contributions[feature] = importance * norm_value
                    else:
                        # For categorical features, just use the importance
                        feature_contributions[feature] = importance
        
        # Start building insights
        insights = {
            "lead_score": lead_score,
            "score_category": "Hot" if lead_score >= 80 else "Warm" if lead_score >= 60 else "Cold",
            "contributing_factors": [],
            "recommendations": []
        }
        
        # Add contributing factors based on feature contributions or importance
        if feature_contributions:
            # Sort by contribution
            sorted_contributions = sorted(
                feature_contributions.items(), 
                key=lambda x: abs(x[1]), 
                reverse=True
            )
            
            # Take top 5 contributing factors
            for feature, contribution in sorted_contributions[:5]:
                # Get the actual value from lead data
                value = lead_data.get(feature, None)
                if value is not None:
                    # Format the value for display
                    if feature == 'pre_approved_binary':
                        value = lead_data.get('pre_approved', 'Unknown')
                    
                    insights["contributing_factors"].append({
                        "feature": feature,
                        "value": value,
                        "impact": "high" if abs(contribution) > 0.2 else "medium" if abs(contribution) > 0.1 else "low",
                        "direction": "positive" if contribution > 0 else "negative"
                    })
        
        # Generate recommendations based on the lead score and data
        if lead_score >= 80:
            insights["recommendations"].append({
                "priority": "high",
                "action": "Immediate personal contact",
                "description": "Contact this lead within 1 hour. Personalize communication based on their interests."
            })
            
            if lead_data.get('requested_showings', 0) > 0:
                insights["recommendations"].append({
                    "priority": "high",
                    "action": "Schedule property showing",
                    "description": "Lead has already requested showings. Prioritize scheduling immediately."
                })
            
            if lead_data.get('pre_approved', 'No') != 'Yes':
                insights["recommendations"].append({
                    "priority": "medium",
                    "action": "Discuss mortgage pre-approval",
                    "description": "Lead is not yet pre-approved. Suggest mortgage lenders and explain benefits."
                })
                
        elif lead_score >= 60:
            insights["recommendations"].append({
                "priority": "medium",
                "action": "Follow up within 24 hours",
                "description": "Send personalized email or call within one business day."
            })
            
            insights["recommendations"].append({
                "priority": "medium",
                "action": "Provide market information",
                "description": "Share relevant market reports and property listings matching their criteria."
            })
            
            if lead_data.get('website_visits', 0) > 5:
                insights["recommendations"].append({
                    "priority": "medium",
                    "action": "Set up property alerts",
                    "description": "Lead is actively browsing. Set up automated property alerts based on their search criteria."
                })
                
        else:  # Cold leads
            insights["recommendations"].append({
                "priority": "low",
                "action": "Add to nurture campaign",
                "description": "Place in automated email campaign with educational content."
            })
            
            insights["recommendations"].append({
                "priority": "low",
                "action": "Re-evaluate in 30 days",
                "description": "Monitor engagement and re-score after 30 days of nurturing."
            })
        
        # Add timeline-specific recommendations
        if lead_data.get('urgency', '') in ['0-3 months', '3-6 months']:
            insights["recommendations"].append({
                "priority": "high" if lead_score >= 70 else "medium",
                "action": "Highlight time-sensitive opportunities",
                "description": "Emphasize market timing, interest rates, and limited inventory to create urgency."
            })
            
        return insights
        
    except Exception as e:
        print(f"Error generating lead insights: {e}")
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
