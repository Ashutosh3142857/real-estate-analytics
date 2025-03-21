import os
import psycopg2
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, Table, MetaData, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from dotenv import load_dotenv
import datetime

# Load environment variables
load_dotenv()

# Get database connection string from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

# Initialize SQLAlchemy base
Base = declarative_base()

# Define database models
class Property(Base):
    __tablename__ = "properties"
    
    id = Column(Integer, primary_key=True)
    address = Column(String(255))
    city = Column(String(100))
    state = Column(String(100))
    zip_code = Column(String(20))
    country = Column(String(100))
    property_type = Column(String(100))
    price = Column(Float)
    bedrooms = Column(Integer)
    bathrooms = Column(Float)
    sqft = Column(Float)
    year_built = Column(Integer)
    description = Column(Text)
    latitude = Column(Float)
    longitude = Column(Float)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    active = Column(Boolean, default=True)
    source = Column(String(100))  # API source or manual entry

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True)
    name = Column(String(255))
    user_type = Column(String(50))  # agent, buyer, seller, investor
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
class Lead(Base):
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    email = Column(String(255))
    phone = Column(String(50))
    source = Column(String(100))
    property_interest = Column(String(255))
    price_range = Column(String(100))
    urgency = Column(String(50))
    website_visits = Column(Integer, default=0)
    viewed_listings = Column(Integer, default=0)
    saved_properties = Column(Integer, default=0)
    requested_showings = Column(Integer, default=0)
    pre_approved = Column(Boolean, default=False)
    credit_score_range = Column(String(50))
    lead_score = Column(Integer)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    status = Column(String(50), default="new")  # new, contacted, qualified, nurturing, converted, closed
    
class MarketTrend(Base):
    __tablename__ = "market_trends"
    
    id = Column(Integer, primary_key=True)
    city = Column(String(100))
    state = Column(String(100))
    country = Column(String(100))
    date = Column(DateTime)
    median_price = Column(Float)
    avg_price = Column(Float)
    inventory = Column(Integer)
    days_on_market = Column(Integer)
    price_per_sqft = Column(Float)
    year_over_year_change = Column(Float)
    month_over_month_change = Column(Float)

class SearchHistory(Base):
    __tablename__ = "search_history"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    search_query = Column(String(255))
    location = Column(String(255))
    min_price = Column(Float, nullable=True)
    max_price = Column(Float, nullable=True)
    bedrooms = Column(Integer, nullable=True)
    property_type = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

# Database connection functions
def get_engine():
    """Get SQLAlchemy engine for database operations"""
    return create_engine(DATABASE_URL)

def init_db():
    """Initialize database with tables if they don't exist"""
    engine = get_engine()
    Base.metadata.create_all(engine)
    print("Database tables created successfully")
    return engine

def get_session():
    """Get a database session for transactions"""
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()

def add_property(property_data):
    """Add a new property to the database"""
    session = get_session()
    new_property = Property(**property_data)
    try:
        session.add(new_property)
        session.commit()
        return new_property.id
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_properties(filters=None):
    """
    Get properties with optional filtering
    
    Args:
        filters (dict): Filter criteria
        
    Returns:
        DataFrame: Properties as DataFrame
    """
    session = get_session()
    query = session.query(Property)
    
    # Apply filters if provided
    if filters:
        if filters.get('city'):
            query = query.filter(Property.city.ilike(f"%{filters['city']}%"))
        if filters.get('min_price'):
            query = query.filter(Property.price >= filters['min_price'])
        if filters.get('max_price'):
            query = query.filter(Property.price <= filters['max_price'])
        if filters.get('property_type'):
            query = query.filter(Property.property_type.in_(filters['property_type']))
        if filters.get('bedrooms'):
            query = query.filter(Property.bedrooms >= filters['bedrooms'])
    
    # Get results and convert to DataFrame
    properties = query.all()
    properties_dict = [prop.__dict__ for prop in properties]
    for prop in properties_dict:
        prop.pop('_sa_instance_state', None)
    
    session.close()
    return pd.DataFrame(properties_dict)

def add_lead(lead_data):
    """Add a new lead to the database"""
    session = get_session()
    new_lead = Lead(**lead_data)
    try:
        session.add(new_lead)
        session.commit()
        return new_lead.id
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_leads(filters=None):
    """Get leads with optional filtering"""
    session = get_session()
    query = session.query(Lead)
    
    # Apply filters if provided
    if filters:
        if filters.get('status'):
            query = query.filter(Lead.status == filters['status'])
        if filters.get('min_score'):
            query = query.filter(Lead.lead_score >= filters['min_score'])
    
    # Get results and convert to DataFrame
    leads = query.all()
    leads_dict = [lead.__dict__ for lead in leads]
    for lead in leads_dict:
        lead.pop('_sa_instance_state', None)
    
    session.close()
    return pd.DataFrame(leads_dict)

def add_market_trend(trend_data):
    """Add a new market trend entry to the database"""
    session = get_session()
    new_trend = MarketTrend(**trend_data)
    try:
        session.add(new_trend)
        session.commit()
        return new_trend.id
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_market_trends(location=None, start_date=None, end_date=None):
    """Get market trends with optional location and date filtering"""
    session = get_session()
    query = session.query(MarketTrend)
    
    # Apply filters if provided
    if location:
        query = query.filter(MarketTrend.city.ilike(f"%{location}%") | 
                            MarketTrend.state.ilike(f"%{location}%") |
                            MarketTrend.country.ilike(f"%{location}%"))
    if start_date:
        query = query.filter(MarketTrend.date >= start_date)
    if end_date:
        query = query.filter(MarketTrend.date <= end_date)
    
    # Get results and convert to DataFrame
    trends = query.all()
    trends_dict = [trend.__dict__ for trend in trends]
    for trend in trends_dict:
        trend.pop('_sa_instance_state', None)
    
    session.close()
    return pd.DataFrame(trends_dict)

def add_search_history(search_data):
    """Add a search query to the search history"""
    session = get_session()
    new_search = SearchHistory(**search_data)
    try:
        session.add(new_search)
        session.commit()
        return new_search.id
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()