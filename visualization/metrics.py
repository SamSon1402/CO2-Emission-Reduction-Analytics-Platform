"""
KPI display components for the CO2 Emission Reduction Analytics Platform
"""

import streamlit as st
import pandas as pd
import logging
from utils.helpers import format_number, format_percentage

logger = logging.getLogger(__name__)

def display_metric_card(title, value, prefix="", suffix="", is_positive=True, column=None):
    """
    Display a metric card
    
    Parameters:
    -----------
    title : str
        Metric title
    value : float
        Metric value
    prefix : str
        Prefix to display before value (e.g., "$")
    suffix : str
        Suffix to display after value (e.g., "kg")
    is_positive : bool
        Whether the value is considered positive (for coloring)
    column : streamlit.column, optional
        Streamlit column to display in (if None, creates its own)
    """
    color_class = "green-text" if is_positive else "red-text"
    
    if value is None:
        value_str = "N/A"
    else:
        value_str = f"{prefix}{format_number(value)}{suffix}"
    
    html = f"""
    <div class="metric-card">
        <h3>{title}</h3>
        <h2 class="{color_class}">{value_str}</h2>
    </div>
    """
    
    if column:
        with column:
            st.markdown(html, unsafe_allow_html=True)
    else:
        st.markdown(html, unsafe_allow_html=True)

def display_metric_row(metrics, num_columns=3):
    """
    Display a row of metric cards
    
    Parameters:
    -----------
    metrics : list
        List of dictionaries with keys: title, value, prefix, suffix, is_positive
    num_columns : int
        Number of columns to display
    """
    cols = st.columns(num_columns)
    
    for i, metric in enumerate(metrics):
        col_idx = i % num_columns
        
        display_metric_card(
            title=metric.get('title', ''),
            value=metric.get('value', None),
            prefix=metric.get('prefix', ''),
            suffix=metric.get('suffix', ''),
            is_positive=metric.get('is_positive', True),
            column=cols[col_idx]
        )

def display_comparison_metrics(baseline, scenario, title="Comparison"):
    """
    Display comparison metrics between baseline and scenario
    
    Parameters:
    -----------
    baseline : dict
        Baseline metrics
    scenario : dict
        Scenario metrics
    title : str
        Section title
    """
    st.markdown(f"<h3 class='sub-header'>{title}</h3>", unsafe_allow_html=True)
    
    # Calculate differences
    diff = {}
    diff_pct = {}
    
    for key in baseline:
        if key in scenario:
            diff[key] = scenario[key] - baseline[key]
            if baseline[key] != 0:
                diff_pct[key] = (diff[key] / baseline[key]) * 100
            else:
                diff_pct[key] = 0
    
    # Display metrics
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("<h4>Baseline</h4>", unsafe_allow_html=True)
        for key, value in baseline.items():
            if key in ['total_emissions_kg', 'total_fuel_kg']:
                st.markdown(f"**{key.replace('_', ' ').title()}**: {format_number(value/1000, 1)} tonnes")
            else:
                st.markdown(f"**{key.replace('_', ' ').title()}**: {format_number(value)}")
    
    with col2:
        st.markdown("<h4>Scenario</h4>", unsafe_allow_html=True)
        for key, value in scenario.items():
            if key in ['total_emissions_kg', 'total_fuel_kg']:
                st.markdown(f"**{key.replace('_', ' ').title()}**: {format_number(value/1000, 1)} tonnes")
            else:
                st.markdown(f"**{key.replace('_', ' ').title()}**: {format_number(value)}")
    
    with col3:
        st.markdown("<h4>Difference</h4>", unsafe_allow_html=True)
        for key, value in diff.items():
            is_positive = (key in ['total_distance_km']) or (value < 0 and key in ['total_emissions_kg', 'total_fuel_kg'])
            color = "green-text" if is_positive else "red-text"
            sign = "" if value < 0 else "+"
            
            if key in ['total_emissions_kg', 'total_fuel_kg']:
                st.markdown(f"**{key.replace('_', ' ').title()}**: <span class='{color}'>{sign}{format_number(value/1000, 1)} tonnes ({format_percentage(diff_pct[key], 1)})</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"**{key.replace('_', ' ').title()}**: <span class='{color}'>{sign}{format_number(value)} ({format_percentage(diff_pct[key], 1)})</span>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)