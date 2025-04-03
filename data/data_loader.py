"""
Data loading utilities for the CO2 Emission Reduction Analytics Platform
"""

import os
import pandas as pd
import logging
from utils.config import load_config
from data.data_generator import generate_flight_data

logger = logging.getLogger(__name__)

def load_flight_data():
    """
    Load flight data from CSV file or generate if not available
    
    Returns:
    --------
    pandas.DataFrame
        Flight data
    """
    config = load_config()
    file_path = os.path.join(config['data_path'], config['sample_data_file'])
    
    # Check if file exists
    if os.path.exists(file_path):
        logger.info(f"Loading data from {file_path}")
        try:
            data = pd.read_csv(file_path)
            logger.info(f"Loaded {len(data)} records from {file_path}")
            return data
        except Exception as e:
            logger.error(f"Error loading data from {file_path}: {str(e)}")
            logger.info("Falling back to generating synthetic data")
    else:
        logger.warning(f"Data file {file_path} not found, generating synthetic data")
    
    # Make sure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Generate data
    data = generate_flight_data()
    
    # Save for future use
    data.to_csv(file_path, index=False)
    logger.info(f"Saved generated data to {file_path}")
    
    return data