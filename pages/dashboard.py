"""
Dashboard page module for the CO2 Emission Reduction Analytics Platform
"""

import streamlit as st
import pandas as pd
import logging
from visualization.dashboard import display_metrics, display_summary_charts, display_data_table
from visualization.charts import create_monthly_trend_chart, create_potential_savings_chart

logger = logging.getLogger(__name__)

def render_dashboard(data):
    """
    Render the main dashboard page
    
    Parameters:
    -----------
    data : pandas.DataFrame
        Flight data
    """
    logger.info("Rendering dashboard page")
    
    st.markdown('<h1 class="main-header">CO2 Emission Reduction Analytics Platform</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="card">
        This dashboard provides analytics for monitoring and reducing carbon emissions from flight operations.
        Analyze flight data, identify emission patterns, and simulate various intervention scenarios.
    </div>
    """, unsafe_allow_html=True)
    
    # Display key metrics
    display_metrics(data)
    
    # Display summary charts
    display_summary_charts(data)
    
    # Bottom row charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<h3 class="sub-header">Monthly Emissions Trend</h3>', unsafe_allow_html=True)
        fig = create_monthly_trend_chart(data)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown('<h3 class="sub-header">Potential Savings from Climb Optimization</h3>', unsafe_allow_html=True)
        fig = create_potential_savings_chart(data)
        st.plotly_chart(fig, use_container_width=True)
    
    # Data overview
    st.markdown("""
    <div class="card">
        <h3>Data Overview</h3>
        <p>Scroll through the table below to see detailed flight data.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display data table with key columns
    display_cols = ['flight_id', 'date', 'origin', 'destination', 'distance_km', 
                    'aircraft_type', 'fuel_consumed_kg', 'co2_emissions_kg', 'optimal_climb_used']
    display_data_table(data, display_cols)