# AI-Powered Real Estate Analytics Platform

An advanced AI-powered real estate analytics platform designed to transform complex market data into actionable insights for investors, agents, and homebuyers.

## Features

- **Global Property Search**: Search real estate properties worldwide
- **Market Insights**: Comprehensive market trends and forecasting
- **Property Analysis**: Detailed property comparisons and analytics
- **Investment Calculator**: ROI metrics and investment opportunity analysis
- **AI Valuation**: Machine learning-based property valuation
- **Lead Management**: Lead qualification and nurturing automation
- **Property Matching**: Smart property recommendations based on preferences
- **Marketing Generator**: AI-powered marketing content creation
- **Market News**: Web-scraped real estate market news and insights
- **Integration System**: Connect to external systems (MLS, CRM, databases)

## Technology Stack

- **Backend**: Python
- **Frontend**: Streamlit
- **Database**: PostgreSQL
- **Data Processing**: Pandas, NumPy
- **Visualization**: Plotly, Folium
- **Machine Learning**: Scikit-learn, StatsModels
- **Web Scraping**: Trafilatura
- **API Integration**: Custom integration framework

## Setup and Installation

1. Clone the repository:
   ```
   git clone https://github.com/Ashutosh3142857/real-estate-analytics.git
   cd real-estate-analytics
   ```

2. Install dependencies:
   ```
   pip install -r dependencies.txt
   ```

3. Set up environment variables:
   Create a `.env` file with the following variables:
   ```
   DATABASE_URL=postgresql://username:password@localhost:5432/realestate
   RAPIDAPI_KEY=your_rapidapi_key
   ```

4. Initialize the database:
   ```
   python -c "from utils.database_init import initialize_database; initialize_database()"
   ```

5. Run the application:
   ```
   streamlit run app.py
   ```

## Usage Examples

### Property Search
Search for properties by location, filter by price, bedrooms, and property type.

### Market Insights
View market trends, price forecasts, and comparative market analysis.

### Integration with External Systems
Connect to MLS systems, CRM platforms, and other data sources using the integration framework:

```python
# Example: Connect to MLS system
from utils.integration_helpers import create_mls_integration

create_mls_integration(
    name="my_mls",
    mls_provider="rets",
    api_key="your_api_key",
    base_url="https://api.mls-provider.com/v1",
    make_default=True
)
```

### Web Scraping for Market News
Get the latest real estate market information using the web scraping module:

```python
# Example: Get market information for a location
from utils.web_scraper import get_real_estate_market_info

market_info = get_real_estate_market_info("New York")
```

## Project Structure

- `app.py`: Main application entry point
- `pages/`: Different pages/modules of the application
  - `market_insights.py`: Market trends and analysis
  - `property_analysis.py`: Property comparison and analysis
  - `investment_calculator.py`: Investment ROI calculations
  - `property_valuation.py`: AI-driven valuation models
  - `lead_management.py`: Lead scoring and management
  - `property_matching.py`: Smart property matching
  - `marketing_generator.py`: AI content generation
  - `market_news.py`: Web-scraped market information
  - `integration_settings.py`: External system integration settings
- `utils/`: Utility modules
  - `data_processing.py`: Data processing functions
  - `visualization.py`: Data visualization utilities
  - `prediction.py`: ML prediction models
  - `database.py`: Database models and operations
  - `real_estate_api.py`: External API integrations
  - `web_scraper.py`: Web scraping utilities
  - `integration.py`: Integration framework
  - `integration_helpers.py`: Helper functions for integrations
- `examples/`: Example code for integration and usage
  - `integration_example.py`: Examples of using the integration system
  - `web_scraping_example.py`: Examples of web scraping functionality

## License

MIT

## Contact

Ashutosh - [GitHub](https://github.com/Ashutosh3142857)