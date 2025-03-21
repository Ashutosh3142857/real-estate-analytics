import os
import logging
from utils.database import init_db, get_session, Property, User, Lead, MarketTrend, SearchHistory
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def initialize_database():
    """Initialize the database schema and setup initial data if needed"""
    try:
        # Initialize the database schema
        engine = init_db()
        logger.info("Database initialized successfully")
        
        # Check if we need to create initial data
        session = get_session()
        property_count = session.query(Property).count()
        
        if property_count == 0:
            logger.info("No properties found in database. Adding initial market trend data.")
            # Add some basic market trend data
            add_initial_market_trends(session)
            
        session.close()
        return True
        
    except SQLAlchemyError as e:
        logger.error(f"Database initialization error: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during database initialization: {str(e)}")
        return False

def add_initial_market_trends(session):
    """Add initial market trend data for major markets"""
    from datetime import datetime, timedelta
    import pandas as pd
    
    # Major US cities
    us_cities = [
        {"city": "New York", "state": "NY", "country": "USA"},
        {"city": "Los Angeles", "state": "CA", "country": "USA"},
        {"city": "Chicago", "state": "IL", "country": "USA"},
        {"city": "Houston", "state": "TX", "country": "USA"},
        {"city": "Phoenix", "state": "AZ", "country": "USA"},
        {"city": "Philadelphia", "state": "PA", "country": "USA"},
        {"city": "San Antonio", "state": "TX", "country": "USA"},
        {"city": "San Diego", "state": "CA", "country": "USA"},
        {"city": "Dallas", "state": "TX", "country": "USA"},
        {"city": "San Francisco", "state": "CA", "country": "USA"}
    ]
    
    # Major international cities
    international_cities = [
        {"city": "London", "state": "", "country": "UK"},
        {"city": "Paris", "state": "", "country": "France"},
        {"city": "Tokyo", "state": "", "country": "Japan"},
        {"city": "Berlin", "state": "", "country": "Germany"},
        {"city": "Sydney", "state": "", "country": "Australia"},
        {"city": "Toronto", "state": "", "country": "Canada"},
        {"city": "Dubai", "state": "", "country": "UAE"},
        {"city": "Singapore", "state": "", "country": "Singapore"},
        {"city": "São Paulo", "state": "", "country": "Brazil"},
        {"city": "Cape Town", "state": "", "country": "South Africa"}
    ]
    
    # Major Indian cities
    indian_cities = [
        {"city": "Mumbai", "state": "Maharashtra", "country": "India"},
        {"city": "Delhi", "state": "Delhi", "country": "India"},
        {"city": "Bangalore", "state": "Karnataka", "country": "India"},
        {"city": "Hyderabad", "state": "Telangana", "country": "India"},
        {"city": "Chennai", "state": "Tamil Nadu", "country": "India"},
        {"city": "Kolkata", "state": "West Bengal", "country": "India"},
        {"city": "Pune", "state": "Maharashtra", "country": "India"},
        {"city": "Ahmedabad", "state": "Gujarat", "country": "India"},
        {"city": "Gurgaon", "state": "Haryana", "country": "India"},
        {"city": "Noida", "state": "Uttar Pradesh", "country": "India"}
    ]
    
    # Combine all cities
    all_cities = us_cities + international_cities + indian_cities
    
    # Generate 24 months of market trend data for each city
    today = datetime.now()
    start_date = today - timedelta(days=24*30)  # 24 months ago
    
    # Base prices for different markets (approximate median home values)
    base_prices = {
        "New York": 650000, "Los Angeles": 750000, "Chicago": 290000, "Houston": 220000,
        "Phoenix": 350000, "Philadelphia": 225000, "San Antonio": 210000, "San Diego": 650000,
        "Dallas": 280000, "San Francisco": 1200000, "London": 650000, "Paris": 580000,
        "Tokyo": 450000, "Berlin": 420000, "Sydney": 830000, "Toronto": 750000,
        "Dubai": 500000, "Singapore": 880000, "São Paulo": 180000, "Cape Town": 150000,
        # Indian cities in INR converted to USD (approximate values)
        "Mumbai": 120000, "Delhi": 95000, "Bangalore": 110000, "Hyderabad": 85000,
        "Chennai": 80000, "Kolkata": 70000, "Pune": 90000, "Ahmedabad": 65000,
        "Gurgaon": 115000, "Noida": 85000
    }
    
    # Annual appreciation rates for different markets (percentage)
    appreciation_rates = {
        "New York": 4.5, "Los Angeles": 5.2, "Chicago": 2.8, "Houston": 3.5,
        "Phoenix": 7.8, "Philadelphia": 3.2, "San Antonio": 4.1, "San Diego": 6.3,
        "Dallas": 5.8, "San Francisco": 5.5, "London": 3.8, "Paris": 3.5,
        "Tokyo": 2.5, "Berlin": 4.8, "Sydney": 6.2, "Toronto": 5.3,
        "Dubai": 7.5, "Singapore": 4.5, "São Paulo": 6.0, "Cape Town": 5.5,
        # Indian cities appreciation rates (percentage)
        "Mumbai": 8.2, "Delhi": 7.5, "Bangalore": 9.3, "Hyderabad": 8.8,
        "Chennai": 7.2, "Kolkata": 6.5, "Pune": 8.5, "Ahmedabad": 7.8,
        "Gurgaon": 9.0, "Noida": 8.3
    }
    
    # Days on market by city
    days_on_market = {
        "New York": 45, "Los Angeles": 38, "Chicago": 55, "Houston": 48,
        "Phoenix": 32, "Philadelphia": 50, "San Antonio": 42, "San Diego": 30,
        "Dallas": 35, "San Francisco": 28, "London": 40, "Paris": 45,
        "Tokyo": 55, "Berlin": 42, "Sydney": 35, "Toronto": 32,
        "Dubai": 60, "Singapore": 70, "São Paulo": 75, "Cape Town": 65,
        # Indian cities days on market
        "Mumbai": 50, "Delhi": 55, "Bangalore": 45, "Hyderabad": 60,
        "Chennai": 65, "Kolkata": 70, "Pune": 50, "Ahmedabad": 75,
        "Gurgaon": 40, "Noida": 45
    }
    
    # Create a list to hold all trend records
    trend_records = []
    
    # Generate monthly data for each city
    for city_data in all_cities:
        city_name = city_data["city"]
        state = city_data["state"]
        country = city_data["country"]
        
        # Get base values for this city
        base_price = base_prices.get(city_name, 300000)  # Default if city not found
        annual_appreciation = appreciation_rates.get(city_name, 4.0) / 100  # Convert percentage to decimal
        monthly_appreciation = annual_appreciation / 12
        dom_base = days_on_market.get(city_name, 45)
        
        # Generate data for each month
        for month in range(24):
            # Calculate date for this data point
            date = start_date + timedelta(days=month*30)
            
            # Calculate price metrics with some randomness
            # Prices generally increase over time with seasonal variations
            seasonal_factor = 1.0 + 0.02 * ((month % 12) / 12.0)  # Seasonal variation up to 2%
            cumulative_appreciation = (1 + monthly_appreciation) ** month
            
            median_price = base_price * cumulative_appreciation * seasonal_factor
            avg_price = median_price * 1.1  # Average typically higher than median
            
            # Calculate inventory and days on market with seasonal variation
            # More inventory and faster sales in spring/summer
            season = month % 12
            seasonal_inventory_boost = 1.0 + 0.15 * max(0, 1 - abs(season - 6) / 6)  # Peak in summer
            inventory = int(250 * seasonal_inventory_boost)
            
            # DOM tends to decrease in hot markets
            dom_seasonal = dom_base * (1.0 - 0.1 * max(0, 1 - abs(season - 6) / 6))  # Faster in summer
            dom = max(15, int(dom_seasonal / cumulative_appreciation))
            
            # Calculate price per square foot
            price_per_sqft = avg_price / 2000  # Assuming 2000 sqft average home
            
            # Calculate year-over-year and month-over-month changes
            yoy_change = annual_appreciation * 100  # Just use the baseline appreciation rate for simplicity
            mom_change = monthly_appreciation * 100
            
            # Add some randomness to make it realistic
            # In a real scenario, we would use actual historical data
            import random
            yoy_factor = random.uniform(0.7, 1.3)
            mom_factor = random.uniform(0.5, 1.5)
            
            yoy_change *= yoy_factor
            mom_change *= mom_factor
            
            # Create a trend record
            trend = MarketTrend(
                city=city_name,
                state=state,
                country=country,
                date=date,
                median_price=median_price,
                avg_price=avg_price,
                inventory=inventory,
                days_on_market=dom,
                price_per_sqft=price_per_sqft,
                year_over_year_change=yoy_change,
                month_over_month_change=mom_change
            )
            
            trend_records.append(trend)
    
    # Add all trend records to the database
    try:
        session.add_all(trend_records)
        session.commit()
        logger.info(f"Added {len(trend_records)} market trend records for {len(all_cities)} cities")
    except Exception as e:
        session.rollback()
        logger.error(f"Error adding market trend data: {str(e)}")