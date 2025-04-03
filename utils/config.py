"""
Configuration management for the CO2 Emission Reduction Analytics Platform
"""

import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

def load_config():
    """
    Load configuration from environment variables or default values
    
    Returns:
    --------
    dict
        Configuration dictionary
    """
    # Load environment variables from .env file if it exists
    load_dotenv()
    
    config = {
        'app_name': os.getenv('APP_NAME', 'CO2 Emission Reduction Analytics Platform'),
        'debug': os.getenv('DEBUG', 'False').lower() == 'true',
        'data_path': os.getenv('DATA_PATH', 'assets/data'),
        'sample_data_file': os.getenv('SAMPLE_DATA_FILE', 'sample_flights.csv'),
        'log_level': os.getenv('LOG_LEVEL', 'INFO'),
        'carbon_price': float(os.getenv('CARBON_PRICE', '80')),
        'fuel_price': float(os.getenv('FUEL_PRICE', '800')),
    }
    
    logger.info("Configuration loaded")
    return config