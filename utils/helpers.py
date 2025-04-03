"""
Helper functions for the CO2 Emission Reduction Analytics Platform
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def format_number(value, decimal_places=0, suffix=''):
    """
    Format a number with thousands separator and specified decimal places
    
    Parameters:
    -----------
    value : float
        Number to format
    decimal_places : int
        Number of decimal places
    suffix : str
        Suffix to append (e.g., 'kg', '%')
        
    Returns:
    --------
    str
        Formatted number
    """
    if pd.isna(value):
        return 'N/A'
    
    try:
        if decimal_places == 0:
            formatted = f"{int(value):,}"
        else:
            formatted = f"{value:,.{decimal_places}f}"
        
        if suffix:
            formatted += f" {suffix}"
        
        return formatted
    except:
        return str(value)

def format_percentage(value, decimal_places=1):
    """
    Format a number as a percentage
    
    Parameters:
    -----------
    value : float
        Number to format (e.g., 0.25 for 25%)
    decimal_places : int
        Number of decimal places
        
    Returns:
    --------
    str
        Formatted percentage
    """
    if pd.isna(value):
        return 'N/A'
    
    try:
        if isinstance(value, float) and value < 1:
            # Convert decimal to percentage
            value *= 100
        
        return f"{value:,.{decimal_places}f}%"
    except:
        return str(value)

def date_range_selector(start_date=None, end_date=None, default_days=90):
    """
    Create a date range for filtering
    
    Parameters:
    -----------
    start_date : datetime, optional
        Start date
    end_date : datetime, optional
        End date
    default_days : int
        Default number of days to look back if start_date is not provided
        
    Returns:
    --------
    tuple
        (start_date, end_date)
    """
    if end_date is None:
        end_date = datetime.now().date()
    
    if start_date is None:
        start_date = end_date - timedelta(days=default_days)
    
    return start_date, end_date