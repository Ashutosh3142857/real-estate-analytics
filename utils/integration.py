"""
Integration module for connecting the real estate application with external systems.
This module provides a standardized interface for integrating with:
- MLS (Multiple Listing Service) systems
- CRM platforms
- External databases
- Third-party APIs
- Enterprise systems and data warehouses
"""

import os
import json
import requests
import pandas as pd
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import logging
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntegrationError(Exception):
    """Exception raised for integration-related errors."""
    pass

class DataSourceConfig:
    """Configuration class for external data sources."""
    
    def __init__(self, config_dict: Dict[str, Any] = None):
        """
        Initialize a data source configuration.
        
        Args:
            config_dict: Dictionary containing configuration parameters
        """
        self.config = config_dict or {}
        self.required_fields = []
        
    def set(self, key: str, value: Any) -> None:
        """Set a configuration parameter."""
        self.config[key] = value
        
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration parameter."""
        return self.config.get(key, default)
    
    def validate(self) -> bool:
        """Validate that all required fields are present."""
        for field in self.required_fields:
            if field not in self.config:
                logger.error(f"Missing required configuration field: {field}")
                return False
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return self.config
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'DataSourceConfig':
        """Create configuration from dictionary."""
        config = cls()
        for key, value in config_dict.items():
            config.set(key, value)
        return config
    
    @classmethod
    def from_json_file(cls, file_path: str) -> 'DataSourceConfig':
        """Load configuration from JSON file."""
        try:
            with open(file_path, 'r') as f:
                config_dict = json.load(f)
            return cls.from_dict(config_dict)
        except Exception as e:
            logger.error(f"Error loading configuration from {file_path}: {str(e)}")
            raise IntegrationError(f"Failed to load configuration: {str(e)}")

class DataSource(ABC):
    """Abstract base class for all data sources."""
    
    def __init__(self, config: DataSourceConfig):
        """
        Initialize a data source with the given configuration.
        
        Args:
            config: Configuration for the data source
        """
        self.config = config
        if not self.config.validate():
            raise IntegrationError("Invalid data source configuration")
    
    @abstractmethod
    def connect(self) -> bool:
        """Establish connection to the data source."""
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Close connection to the data source."""
        pass
    
    @abstractmethod
    def fetch_data(self, query: Any = None) -> pd.DataFrame:
        """
        Fetch data from the source.
        
        Args:
            query: Query parameters or filter criteria
            
        Returns:
            DataFrame containing the fetched data
        """
        pass
    
    @abstractmethod
    def push_data(self, data: pd.DataFrame) -> bool:
        """
        Push data to the source.
        
        Args:
            data: DataFrame containing the data to push
            
        Returns:
            True if successful, False otherwise
        """
        pass

class RESTAPIConfig(DataSourceConfig):
    """Configuration for REST API data sources."""
    
    def __init__(self, config_dict: Dict[str, Any] = None):
        super().__init__(config_dict)
        self.required_fields = ['base_url', 'auth_type']

class RESTAPIDataSource(DataSource):
    """Data source implementation for REST APIs."""
    
    def __init__(self, config: RESTAPIConfig):
        """
        Initialize a REST API data source.
        
        Args:
            config: Configuration for the REST API
        """
        super().__init__(config)
        self.session = None
        self.headers = {}
        
        # Set up authentication headers based on auth_type
        auth_type = self.config.get('auth_type')
        if auth_type == 'api_key':
            api_key = self.config.get('api_key')
            api_key_header = self.config.get('api_key_header', 'Authorization')
            if api_key:
                self.headers[api_key_header] = api_key
        elif auth_type == 'oauth2':
            token = self.config.get('access_token')
            if token:
                self.headers['Authorization'] = f"Bearer {token}"
        
        # Add any additional headers
        additional_headers = self.config.get('headers', {})
        self.headers.update(additional_headers)
    
    def connect(self) -> bool:
        """Establish connection to the REST API."""
        try:
            self.session = requests.Session()
            self.session.headers.update(self.headers)
            
            # Test connection with a ping endpoint if specified
            ping_endpoint = self.config.get('ping_endpoint')
            if ping_endpoint:
                base_url = self.config.get('base_url')
                response = self.session.get(f"{base_url}{ping_endpoint}")
                return response.status_code < 400
            
            return True
        except Exception as e:
            logger.error(f"Error connecting to REST API: {str(e)}")
            return False
    
    def disconnect(self) -> None:
        """Close connection to the REST API."""
        if self.session:
            self.session.close()
            self.session = None
    
    def fetch_data(self, query: Dict[str, Any] = None) -> pd.DataFrame:
        """
        Fetch data from the REST API.
        
        Args:
            query: Dictionary containing query parameters
            
        Returns:
            DataFrame containing the fetched data
        """
        if not self.session:
            self.connect()
        
        try:
            base_url = self.config.get('base_url')
            endpoint = self.config.get('endpoint', '')
            url = f"{base_url}{endpoint}"
            
            # Make the request
            response = self.session.get(url, params=query)
            
            if response.status_code >= 400:
                logger.error(f"API request failed with status {response.status_code}: {response.text}")
                return pd.DataFrame()
            
            # Extract data based on the specified response format
            response_format = self.config.get('response_format', 'json')
            if response_format == 'json':
                data = response.json()
                
                # Extract the relevant data array using the data_path if specified
                data_path = self.config.get('data_path', '')
                if data_path:
                    for key in data_path.split('.'):
                        if key in data:
                            data = data[key]
                        else:
                            logger.warning(f"Data path key '{key}' not found in response")
                            return pd.DataFrame()
                
                # Convert to DataFrame
                if isinstance(data, list):
                    return pd.DataFrame(data)
                elif isinstance(data, dict):
                    return pd.DataFrame([data])
                else:
                    logger.warning(f"Unexpected data format: {type(data)}")
                    return pd.DataFrame()
            
            elif response_format == 'csv':
                return pd.read_csv(pd.StringIO(response.text))
            
            else:
                logger.warning(f"Unsupported response format: {response_format}")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error fetching data from REST API: {str(e)}")
            return pd.DataFrame()
    
    def push_data(self, data: pd.DataFrame) -> bool:
        """
        Push data to the REST API.
        
        Args:
            data: DataFrame containing the data to push
            
        Returns:
            True if successful, False otherwise
        """
        if not self.session:
            self.connect()
        
        try:
            base_url = self.config.get('base_url')
            push_endpoint = self.config.get('push_endpoint', '')
            url = f"{base_url}{push_endpoint}"
            
            # Convert DataFrame to the format expected by the API
            push_format = self.config.get('push_format', 'json')
            
            if push_format == 'json':
                # Convert to records format (list of dictionaries)
                records = data.to_dict(orient='records')
                
                # Check if a specific root element is needed
                root_element = self.config.get('push_root_element')
                if root_element:
                    payload = {root_element: records}
                else:
                    payload = records
                
                # Make the request
                response = self.session.post(url, json=payload)
            
            elif push_format == 'csv':
                csv_data = data.to_csv(index=False)
                response = self.session.post(url, data=csv_data, 
                                            headers={'Content-Type': 'text/csv'})
            
            else:
                logger.warning(f"Unsupported push format: {push_format}")
                return False
            
            # Check if request was successful
            if response.status_code < 400:
                return True
            else:
                logger.error(f"API push failed with status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error pushing data to REST API: {str(e)}")
            return False

class DatabaseConfig(DataSourceConfig):
    """Configuration for database data sources."""
    
    def __init__(self, config_dict: Dict[str, Any] = None):
        super().__init__(config_dict)
        self.required_fields = ['connection_string', 'driver']

class DatabaseDataSource(DataSource):
    """Data source implementation for databases."""
    
    def __init__(self, config: DatabaseConfig):
        """
        Initialize a database data source.
        
        Args:
            config: Configuration for the database
        """
        super().__init__(config)
        self.connection = None
        self.driver = self.config.get('driver')
    
    def connect(self) -> bool:
        """Establish connection to the database."""
        try:
            if self.driver == 'sqlalchemy':
                from sqlalchemy import create_engine
                from sqlalchemy.orm import sessionmaker
                
                connection_string = self.config.get('connection_string')
                self.engine = create_engine(connection_string)
                self.Session = sessionmaker(bind=self.engine)
                self.connection = self.Session()
                return True
            
            elif self.driver == 'psycopg2':
                import psycopg2
                
                connection_string = self.config.get('connection_string')
                self.connection = psycopg2.connect(connection_string)
                return True
            
            elif self.driver == 'sqlite3':
                import sqlite3
                
                db_path = self.config.get('connection_string').replace('sqlite:///', '')
                self.connection = sqlite3.connect(db_path)
                return True
            
            elif self.driver == 'mysql':
                import mysql.connector
                
                # Parse connection string for MySQL
                conn_parts = self.config.get('connection_string').replace('mysql://', '').split('@')
                user_pass = conn_parts[0].split(':')
                host_db = conn_parts[1].split('/')
                
                config = {
                    'user': user_pass[0],
                    'password': user_pass[1],
                    'host': host_db[0],
                    'database': host_db[1]
                }
                
                self.connection = mysql.connector.connect(**config)
                return True
            
            else:
                logger.error(f"Unsupported database driver: {self.driver}")
                return False
                
        except Exception as e:
            logger.error(f"Error connecting to database: {str(e)}")
            return False
    
    def disconnect(self) -> None:
        """Close connection to the database."""
        if self.connection:
            if self.driver == 'sqlalchemy':
                self.connection.close()
            else:
                self.connection.close()
            
            self.connection = None
    
    def fetch_data(self, query: str = None) -> pd.DataFrame:
        """
        Fetch data from the database.
        
        Args:
            query: SQL query string
            
        Returns:
            DataFrame containing the query results
        """
        if not self.connection:
            self.connect()
        
        try:
            if not query:
                table = self.config.get('table')
                if not table:
                    logger.error("No query or table specified for fetch_data")
                    return pd.DataFrame()
                
                query = f"SELECT * FROM {table}"
            
            if self.driver == 'sqlalchemy':
                import pandas as pd
                from sqlalchemy import text
                
                result = self.connection.execute(text(query))
                data = pd.DataFrame(result.fetchall())
                if not data.empty:
                    data.columns = result.keys()
                return data
            
            else:
                # For other drivers, use pandas' built-in SQL support
                return pd.read_sql(query, self.connection)
                
        except Exception as e:
            logger.error(f"Error fetching data from database: {str(e)}")
            return pd.DataFrame()
    
    def push_data(self, data: pd.DataFrame) -> bool:
        """
        Push data to the database.
        
        Args:
            data: DataFrame containing the data to push
            
        Returns:
            True if successful, False otherwise
        """
        if not self.connection:
            self.connect()
        
        try:
            table = self.config.get('table')
            if not table:
                logger.error("No table specified for push_data")
                return False
            
            if self.driver == 'sqlalchemy':
                # Use pandas to_sql for SQLAlchemy
                data.to_sql(table, self.engine, if_exists='append', index=False)
                self.connection.commit()
                return True
            
            elif self.driver in ['psycopg2', 'sqlite3', 'mysql']:
                # For these drivers, use pandas to_sql with connection
                data.to_sql(table, self.connection, if_exists='append', index=False)
                if self.driver != 'sqlite3':  # SQLite doesn't need explicit commit
                    self.connection.commit()
                return True
            
            else:
                logger.error(f"Unsupported database driver for push_data: {self.driver}")
                return False
                
        except Exception as e:
            logger.error(f"Error pushing data to database: {str(e)}")
            return False

class CSVFileConfig(DataSourceConfig):
    """Configuration for CSV file data sources."""
    
    def __init__(self, config_dict: Dict[str, Any] = None):
        super().__init__(config_dict)
        self.required_fields = ['file_path']

class CSVFileDataSource(DataSource):
    """Data source implementation for CSV files."""
    
    def __init__(self, config: CSVFileConfig):
        """
        Initialize a CSV file data source.
        
        Args:
            config: Configuration for the CSV file
        """
        super().__init__(config)
    
    def connect(self) -> bool:
        """Verify that the CSV file exists and is accessible."""
        file_path = self.config.get('file_path')
        return os.path.exists(file_path)
    
    def disconnect(self) -> None:
        """No actual disconnection needed for CSV files."""
        pass
    
    def fetch_data(self, query: Dict[str, Any] = None) -> pd.DataFrame:
        """
        Fetch data from the CSV file.
        
        Args:
            query: Dictionary with filter criteria (optional)
            
        Returns:
            DataFrame containing the data
        """
        try:
            file_path = self.config.get('file_path')
            
            if not os.path.exists(file_path):
                logger.error(f"CSV file not found: {file_path}")
                return pd.DataFrame()
            
            # Load the CSV file
            data = pd.read_csv(file_path)
            
            # Apply filters if specified
            if query:
                for column, value in query.items():
                    if column in data.columns:
                        if isinstance(value, list):
                            data = data[data[column].isin(value)]
                        else:
                            data = data[data[column] == value]
            
            return data
            
        except Exception as e:
            logger.error(f"Error fetching data from CSV file: {str(e)}")
            return pd.DataFrame()
    
    def push_data(self, data: pd.DataFrame) -> bool:
        """
        Push data to the CSV file.
        
        Args:
            data: DataFrame containing the data to push
            
        Returns:
            True if successful, False otherwise
        """
        try:
            file_path = self.config.get('file_path')
            
            # Check if the file already exists
            if os.path.exists(file_path):
                # Read existing data
                existing_data = pd.read_csv(file_path)
                
                # Determine how to handle existing data
                mode = self.config.get('write_mode', 'append')
                
                if mode == 'append':
                    # Append new data to existing data
                    combined_data = pd.concat([existing_data, data], ignore_index=True)
                    combined_data.to_csv(file_path, index=False)
                
                elif mode == 'overwrite':
                    # Overwrite existing data
                    data.to_csv(file_path, index=False)
                
                else:
                    logger.error(f"Invalid write mode: {mode}")
                    return False
            
            else:
                # File doesn't exist, create it
                data.to_csv(file_path, index=False)
            
            return True
            
        except Exception as e:
            logger.error(f"Error pushing data to CSV file: {str(e)}")
            return False

class MLSConfig(RESTAPIConfig):
    """Configuration for MLS (Multiple Listing Service) data sources."""
    
    def __init__(self, config_dict: Dict[str, Any] = None):
        super().__init__(config_dict)
        self.required_fields.extend(['mls_provider'])

class MLSDataSource(RESTAPIDataSource):
    """Data source implementation for MLS systems."""
    
    def __init__(self, config: MLSConfig):
        """
        Initialize an MLS data source.
        
        Args:
            config: Configuration for the MLS
        """
        super().__init__(config)
        self.mls_provider = self.config.get('mls_provider')
    
    def fetch_data(self, query: Dict[str, Any] = None) -> pd.DataFrame:
        """
        Fetch data from the MLS.
        
        Args:
            query: Dictionary with property search criteria
            
        Returns:
            DataFrame containing the property listings
        """
        # Customize query parameters based on MLS provider
        if self.mls_provider == 'rets':
            # Format query for RETS protocol
            rets_query = self._format_rets_query(query)
            return super().fetch_data(rets_query)
        
        elif self.mls_provider == 'spark':
            # Format query for Spark API
            spark_query = self._format_spark_query(query)
            return super().fetch_data(spark_query)
        
        elif self.mls_provider == 'bridge':
            # Format query for Bridge API
            bridge_query = self._format_bridge_query(query)
            return super().fetch_data(bridge_query)
        
        else:
            # For other providers, use the query as is
            return super().fetch_data(query)
    
    def _format_rets_query(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Format query for RETS protocol."""
        if not query:
            return {}
        
        rets_query = {
            'SearchType': 'Property',
            'Class': query.get('property_type', 'ALL'),
            'Query': self._build_rets_filter_string(query),
            'Limit': query.get('limit', 100)
        }
        
        return rets_query
    
    def _build_rets_filter_string(self, query: Dict[str, Any]) -> str:
        """Build RETS filter string from query parameters."""
        filters = []
        
        # Map common query parameters to RETS fields
        field_mapping = {
            'city': 'City',
            'state': 'StateOrProvince',
            'min_price': 'ListPrice',
            'max_price': 'ListPrice',
            'min_bedrooms': 'Bedrooms',
            'min_bathrooms': 'Bathrooms',
            'property_type': 'PropertyType'
        }
        
        for key, value in query.items():
            if key in field_mapping:
                rets_field = field_mapping[key]
                
                if key == 'min_price':
                    filters.append(f"{rets_field} >= {value}")
                elif key == 'max_price':
                    filters.append(f"{rets_field} <= {value}")
                elif key == 'min_bedrooms':
                    filters.append(f"{rets_field} >= {value}")
                elif key == 'min_bathrooms':
                    filters.append(f"{rets_field} >= {value}")
                else:
                    filters.append(f"{rets_field} = {value}")
        
        return ','.join(filters)
    
    def _format_spark_query(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Format query for Spark API."""
        if not query:
            return {}
        
        # Map common query parameters to Spark API fields
        spark_query = {
            'includetypes': 'A'  # Active listings
        }
        
        if 'city' in query:
            spark_query['city'] = query['city']
        
        if 'state' in query:
            spark_query['state'] = query['state']
        
        if 'min_price' in query:
            spark_query['minimalprice'] = query['min_price']
        
        if 'max_price' in query:
            spark_query['maximalprice'] = query['max_price']
        
        if 'min_bedrooms' in query:
            spark_query['minimalbeds'] = query['min_bedrooms']
        
        if 'min_bathrooms' in query:
            spark_query['minimalbaths'] = query['min_bathrooms']
        
        if 'property_type' in query:
            spark_query['propertytype'] = query['property_type']
        
        return spark_query
    
    def _format_bridge_query(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Format query for Bridge API."""
        if not query:
            return {}
        
        # Map common query parameters to Bridge API fields
        bridge_query = {
            'access_token': self.config.get('access_token'),
            'offset': 0,
            'limit': query.get('limit', 100)
        }
        
        # Add filter parameters
        filter_params = {}
        
        if 'city' in query:
            filter_params['City'] = query['city']
        
        if 'state' in query:
            filter_params['StateOrProvince'] = query['state']
        
        if 'min_price' in query:
            filter_params['ListPrice.min'] = query['min_price']
        
        if 'max_price' in query:
            filter_params['ListPrice.max'] = query['max_price']
        
        if 'min_bedrooms' in query:
            filter_params['BedroomsTotal.min'] = query['min_bedrooms']
        
        if 'min_bathrooms' in query:
            filter_params['BathroomsTotalDecimal.min'] = query['min_bathrooms']
        
        if 'property_type' in query:
            filter_params['PropertyType'] = query['property_type']
        
        # Encode filter parameters as JSON and add to query
        if filter_params:
            bridge_query['filter'] = json.dumps(filter_params)
        
        return bridge_query

class CRMConfig(RESTAPIConfig):
    """Configuration for CRM data sources."""
    
    def __init__(self, config_dict: Dict[str, Any] = None):
        super().__init__(config_dict)
        self.required_fields.extend(['crm_provider'])

class CRMDataSource(RESTAPIDataSource):
    """Data source implementation for CRM systems."""
    
    def __init__(self, config: CRMConfig):
        """
        Initialize a CRM data source.
        
        Args:
            config: Configuration for the CRM
        """
        super().__init__(config)
        self.crm_provider = self.config.get('crm_provider')
    
    def fetch_data(self, query: Dict[str, Any] = None) -> pd.DataFrame:
        """
        Fetch data from the CRM.
        
        Args:
            query: Dictionary with filter criteria and entity type
            
        Returns:
            DataFrame containing the CRM records
        """
        if not query:
            query = {}
        
        # Get the entity type to fetch (contacts, leads, opportunities, etc.)
        entity_type = query.pop('entity_type', 'contacts')
        
        # Customize endpoint and query parameters based on CRM provider
        if self.crm_provider == 'salesforce':
            return self._fetch_salesforce_data(entity_type, query)
        
        elif self.crm_provider == 'hubspot':
            return self._fetch_hubspot_data(entity_type, query)
        
        elif self.crm_provider == 'zoho':
            return self._fetch_zoho_data(entity_type, query)
        
        else:
            # For other providers, use the base implementation
            # Set the endpoint based on entity type
            self.config.set('endpoint', f"/{entity_type}")
            return super().fetch_data(query)
    
    def _fetch_salesforce_data(self, entity_type: str, query: Dict[str, Any]) -> pd.DataFrame:
        """Fetch data from Salesforce CRM."""
        # Map common entity types to Salesforce objects
        entity_mapping = {
            'contacts': 'Contact',
            'leads': 'Lead',
            'opportunities': 'Opportunity',
            'accounts': 'Account',
            'properties': 'Property__c'  # Custom object
        }
        
        sf_object = entity_mapping.get(entity_type, entity_type)
        
        # Build SOQL query
        fields = query.pop('fields', '*')
        if isinstance(fields, list):
            fields = ','.join(fields)
        
        # Start building the SOQL query
        soql = f"SELECT {fields} FROM {sf_object}"
        
        # Add WHERE clause for filters
        where_clauses = []
        for key, value in query.items():
            if isinstance(value, str):
                where_clauses.append(f"{key} = '{value}'")
            else:
                where_clauses.append(f"{key} = {value}")
        
        if where_clauses:
            soql += " WHERE " + " AND ".join(where_clauses)
        
        # Add LIMIT clause
        limit = query.get('limit', 100)
        soql += f" LIMIT {limit}"
        
        # Set the endpoint for the SOQL query
        self.config.set('endpoint', f"/services/data/v52.0/query/")
        
        # Update query for Salesforce
        sf_query = {'q': soql}
        
        return super().fetch_data(sf_query)
    
    def _fetch_hubspot_data(self, entity_type: str, query: Dict[str, Any]) -> pd.DataFrame:
        """Fetch data from HubSpot CRM."""
        # Map common entity types to HubSpot endpoints
        endpoint_mapping = {
            'contacts': '/crm/v3/objects/contacts',
            'deals': '/crm/v3/objects/deals',
            'companies': '/crm/v3/objects/companies',
            'tickets': '/crm/v3/objects/tickets'
        }
        
        # Set the endpoint based on entity type
        endpoint = endpoint_mapping.get(entity_type, f"/crm/v3/objects/{entity_type}")
        self.config.set('endpoint', endpoint)
        
        # Update the data path to extract records from the HubSpot response
        self.config.set('data_path', 'results')
        
        # Format query parameters for HubSpot
        hubspot_query = {}
        
        if 'limit' in query:
            hubspot_query['limit'] = query.pop('limit')
        
        if 'properties' in query:
            properties = query.pop('properties')
            if isinstance(properties, list):
                hubspot_query['properties'] = ','.join(properties)
            else:
                hubspot_query['properties'] = properties
        
        # Add remaining parameters as filters
        if query:
            filters = []
            for key, value in query.items():
                filters.append({
                    'propertyName': key,
                    'operator': 'EQ',
                    'value': value
                })
            
            if filters:
                filter_groups = [{'filters': filters}]
                hubspot_query['filterGroups'] = json.dumps(filter_groups)
        
        return super().fetch_data(hubspot_query)
    
    def _fetch_zoho_data(self, entity_type: str, query: Dict[str, Any]) -> pd.DataFrame:
        """Fetch data from Zoho CRM."""
        # Map common entity types to Zoho endpoints
        endpoint_mapping = {
            'contacts': '/crm/v2/Contacts',
            'leads': '/crm/v2/Leads',
            'deals': '/crm/v2/Deals',
            'accounts': '/crm/v2/Accounts'
        }
        
        # Set the endpoint based on entity type
        endpoint = endpoint_mapping.get(entity_type, f"/crm/v2/{entity_type}")
        self.config.set('endpoint', endpoint)
        
        # Update the data path to extract records from the Zoho response
        self.config.set('data_path', 'data')
        
        # Format query parameters for Zoho
        zoho_query = {}
        
        if 'limit' in query:
            zoho_query['per_page'] = query.pop('limit')
        
        if 'fields' in query:
            fields = query.pop('fields')
            if isinstance(fields, list):
                zoho_query['fields'] = ','.join(fields)
            else:
                zoho_query['fields'] = fields
        
        # Add remaining parameters as criteria
        if query:
            criteria = []
            for key, value in query.items():
                if isinstance(value, str):
                    criteria.append(f"({key}:equals:{value})")
                else:
                    criteria.append(f"({key}:equals:{value})")
            
            if criteria:
                zoho_query['criteria'] = ''.join(criteria)
        
        return super().fetch_data(zoho_query)
    
    def push_data(self, data: pd.DataFrame) -> bool:
        """
        Push data to the CRM.
        
        Args:
            data: DataFrame containing the data to push
            
        Returns:
            True if successful, False otherwise
        """
        if data.empty:
            logger.warning("Empty DataFrame provided for CRM push_data")
            return False
        
        # Get the entity type from the configuration
        entity_type = self.config.get('entity_type', 'contacts')
        
        # Customize endpoint and payload format based on CRM provider
        if self.crm_provider == 'salesforce':
            return self._push_salesforce_data(entity_type, data)
        
        elif self.crm_provider == 'hubspot':
            return self._push_hubspot_data(entity_type, data)
        
        elif self.crm_provider == 'zoho':
            return self._push_zoho_data(entity_type, data)
        
        else:
            # For other providers, use the base implementation
            # Set the endpoint based on entity type
            self.config.set('endpoint', f"/{entity_type}")
            self.config.set('push_endpoint', f"/{entity_type}")
            return super().push_data(data)
    
    def _push_salesforce_data(self, entity_type: str, data: pd.DataFrame) -> bool:
        """Push data to Salesforce CRM."""
        # Map common entity types to Salesforce objects
        entity_mapping = {
            'contacts': 'Contact',
            'leads': 'Lead',
            'opportunities': 'Opportunity',
            'accounts': 'Account',
            'properties': 'Property__c'  # Custom object
        }
        
        sf_object = entity_mapping.get(entity_type, entity_type)
        
        # Set the endpoint for the composite API (allows multiple records)
        self.config.set('push_endpoint', '/services/data/v52.0/composite/tree/' + sf_object)
        
        # Format the data for Salesforce's batch API
        records = data.to_dict(orient='records')
        payload = {
            'records': []
        }
        
        for i, record in enumerate(records):
            # Clean up the record (remove NaN values)
            clean_record = {k: v for k, v in record.items() if pd.notna(v)}
            
            # Add attributes for Salesforce
            sf_record = {
                'attributes': {'type': sf_object, 'referenceId': f"ref{i}"},
                **clean_record
            }
            
            payload['records'].append(sf_record)
        
        # Use custom payload instead of DataFrame
        if not self.session:
            self.connect()
        
        try:
            base_url = self.config.get('base_url')
            push_endpoint = self.config.get('push_endpoint')
            url = f"{base_url}{push_endpoint}"
            
            # Make the request
            response = self.session.post(url, json=payload)
            
            # Check if request was successful
            if response.status_code < 400:
                return True
            else:
                logger.error(f"Salesforce push failed with status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error pushing data to Salesforce: {str(e)}")
            return False
    
    def _push_hubspot_data(self, entity_type: str, data: pd.DataFrame) -> bool:
        """Push data to HubSpot CRM."""
        # Map common entity types to HubSpot endpoints
        endpoint_mapping = {
            'contacts': '/crm/v3/objects/contacts/batch/create',
            'deals': '/crm/v3/objects/deals/batch/create',
            'companies': '/crm/v3/objects/companies/batch/create',
            'tickets': '/crm/v3/objects/tickets/batch/create'
        }
        
        # Set the endpoint based on entity type
        endpoint = endpoint_mapping.get(entity_type, f"/crm/v3/objects/{entity_type}/batch/create")
        self.config.set('push_endpoint', endpoint)
        
        # Format the data for HubSpot's batch API
        records = data.to_dict(orient='records')
        
        # HubSpot expects a specific format
        inputs = []
        for record in records:
            # Clean up the record (remove NaN values)
            properties = {k: v for k, v in record.items() if pd.notna(v)}
            
            inputs.append({
                'properties': properties
            })
        
        payload = {'inputs': inputs}
        
        # Use custom payload instead of DataFrame
        if not self.session:
            self.connect()
        
        try:
            base_url = self.config.get('base_url')
            push_endpoint = self.config.get('push_endpoint')
            url = f"{base_url}{push_endpoint}"
            
            # Make the request
            response = self.session.post(url, json=payload)
            
            # Check if request was successful
            if response.status_code < 400:
                return True
            else:
                logger.error(f"HubSpot push failed with status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error pushing data to HubSpot: {str(e)}")
            return False
    
    def _push_zoho_data(self, entity_type: str, data: pd.DataFrame) -> bool:
        """Push data to Zoho CRM."""
        # Map common entity types to Zoho endpoints
        endpoint_mapping = {
            'contacts': '/crm/v2/Contacts',
            'leads': '/crm/v2/Leads',
            'deals': '/crm/v2/Deals',
            'accounts': '/crm/v2/Accounts'
        }
        
        # Set the endpoint based on entity type
        endpoint = endpoint_mapping.get(entity_type, f"/crm/v2/{entity_type}")
        self.config.set('push_endpoint', endpoint)
        
        # Format the data for Zoho's API
        records = data.to_dict(orient='records')
        
        # Clean up the records (remove NaN values)
        clean_records = []
        for record in records:
            clean_record = {k: v for k, v in record.items() if pd.notna(v)}
            clean_records.append(clean_record)
        
        payload = {'data': clean_records}
        
        # Use custom payload instead of DataFrame
        if not self.session:
            self.connect()
        
        try:
            base_url = self.config.get('base_url')
            push_endpoint = self.config.get('push_endpoint')
            url = f"{base_url}{push_endpoint}"
            
            # Make the request
            response = self.session.post(url, json=payload)
            
            # Check if request was successful
            if response.status_code < 400:
                return True
            else:
                logger.error(f"Zoho push failed with status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error pushing data to Zoho: {str(e)}")
            return False

# Factory function to create data sources based on config
def create_data_source(config_dict: Dict[str, Any]) -> DataSource:
    """
    Create a data source based on configuration.
    
    Args:
        config_dict: Dictionary with data source configuration
        
    Returns:
        DataSource object
        
    Raises:
        IntegrationError: If the data source type is invalid or configuration is incomplete
    """
    if not config_dict or 'type' not in config_dict:
        raise IntegrationError("Invalid data source configuration: missing 'type'")
    
    source_type = config_dict.pop('type')
    
    if source_type == 'rest_api':
        config = RESTAPIConfig(config_dict)
        return RESTAPIDataSource(config)
    
    elif source_type == 'database':
        config = DatabaseConfig(config_dict)
        return DatabaseDataSource(config)
    
    elif source_type == 'csv_file':
        config = CSVFileConfig(config_dict)
        return CSVFileDataSource(config)
    
    elif source_type == 'mls':
        config = MLSConfig(config_dict)
        return MLSDataSource(config)
    
    elif source_type == 'crm':
        config = CRMConfig(config_dict)
        return CRMDataSource(config)
    
    else:
        raise IntegrationError(f"Invalid data source type: {source_type}")

# Integration manager to handle multiple data sources
class IntegrationManager:
    """Manager for handling multiple data source integrations."""
    
    def __init__(self):
        """Initialize the integration manager."""
        self.data_sources = {}
        self.default_source = None
    
    def add_data_source(self, name: str, config_dict: Dict[str, Any], make_default: bool = False) -> None:
        """
        Add a data source to the manager.
        
        Args:
            name: Unique name for the data source
            config_dict: Configuration dictionary for the data source
            make_default: Whether to make this the default data source
        """
        try:
            data_source = create_data_source(config_dict)
            self.data_sources[name] = data_source
            
            if make_default or not self.default_source:
                self.default_source = name
                
            logger.info(f"Added data source: {name}")
            
        except Exception as e:
            logger.error(f"Error adding data source {name}: {str(e)}")
            raise IntegrationError(f"Failed to add data source {name}: {str(e)}")
    
    def get_data_source(self, name: str = None) -> DataSource:
        """
        Get a data source by name.
        
        Args:
            name: Name of the data source to get (uses default if None)
            
        Returns:
            DataSource object
            
        Raises:
            IntegrationError: If the data source is not found
        """
        if name is None:
            name = self.default_source
            
        if name not in self.data_sources:
            raise IntegrationError(f"Data source not found: {name}")
            
        return self.data_sources[name]
    
    def remove_data_source(self, name: str) -> None:
        """
        Remove a data source from the manager.
        
        Args:
            name: Name of the data source to remove
            
        Raises:
            IntegrationError: If the data source is not found
        """
        if name not in self.data_sources:
            raise IntegrationError(f"Data source not found: {name}")
        
        # Disconnect the data source before removing
        data_source = self.data_sources[name]
        try:
            data_source.disconnect()
        except:
            pass
        
        # Remove the data source
        del self.data_sources[name]
        
        # Update default source if needed
        if self.default_source == name:
            if self.data_sources:
                self.default_source = next(iter(self.data_sources.keys()))
            else:
                self.default_source = None
        
        logger.info(f"Removed data source: {name}")
    
    def fetch_data(self, name: str = None, query: Any = None) -> pd.DataFrame:
        """
        Fetch data from a data source.
        
        Args:
            name: Name of the data source to use (uses default if None)
            query: Query parameters for the data source
            
        Returns:
            DataFrame containing the fetched data
        """
        data_source = self.get_data_source(name)
        
        try:
            return data_source.fetch_data(query)
        except Exception as e:
            logger.error(f"Error fetching data from {name}: {str(e)}")
            return pd.DataFrame()
    
    def push_data(self, data: pd.DataFrame, name: str = None) -> bool:
        """
        Push data to a data source.
        
        Args:
            data: DataFrame containing the data to push
            name: Name of the data source to use (uses default if None)
            
        Returns:
            True if successful, False otherwise
        """
        data_source = self.get_data_source(name)
        
        try:
            return data_source.push_data(data)
        except Exception as e:
            logger.error(f"Error pushing data to {name}: {str(e)}")
            return False
    
    def close_all_connections(self) -> None:
        """Close all data source connections."""
        for name, data_source in self.data_sources.items():
            try:
                data_source.disconnect()
                logger.info(f"Disconnected data source: {name}")
            except Exception as e:
                logger.warning(f"Error disconnecting data source {name}: {str(e)}")

# Singleton instance of IntegrationManager
integration_manager = IntegrationManager()

def get_integration_manager() -> IntegrationManager:
    """Get the singleton instance of IntegrationManager."""
    return integration_manager

# Convenience functions for working with the integration manager

def add_data_source(name: str, config_dict: Dict[str, Any], make_default: bool = False) -> None:
    """Add a data source to the integration manager."""
    integration_manager.add_data_source(name, config_dict, make_default)

def get_data_source(name: str = None) -> DataSource:
    """Get a data source from the integration manager."""
    return integration_manager.get_data_source(name)

def fetch_data(name: str = None, query: Any = None) -> pd.DataFrame:
    """Fetch data from a data source."""
    return integration_manager.fetch_data(name, query)

def push_data(data: pd.DataFrame, name: str = None) -> bool:
    """Push data to a data source."""
    return integration_manager.push_data(data, name)

def remove_data_source(name: str) -> None:
    """Remove a data source from the integration manager."""
    integration_manager.remove_data_source(name)

def close_all_connections() -> None:
    """Close all data source connections."""
    integration_manager.close_all_connections()