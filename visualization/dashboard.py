"""
Dashboard layout components for the CO2 Emission Reduction Analytics Platform
"""

import streamlit as st
import pandas as pd
import logging
from utils.helpers import format_number
from visualization.charts import create_emissions_by_aircraft_chart, create_emissions_by_distance_chart

logger = logging.getLogger(__name__)

def display_metrics(data, modified_data=None):
    """
    Display key metrics in the dashboard
    
    Parameters:
    -----------
    data : pandas.DataFrame
        Flight data
    modified_data : pandas.DataFrame, optional
        Modified data after applying interventions
    """
    logger.info("Displaying metrics dashboard")
    
    total_flights = len(data)
    total_distance = data['distance_km'].sum()
    total_fuel = data['fuel_consumed_kg'].sum()
    total_emissions = data['co2_emissions_kg'].sum()
    
    avg_emission_per_km = total_emissions / total_distance
    
    # Create metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Total Flights</h3>
            <h2>{format_number(total_flights)}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Total Distance</h3>
            <h2>{format_number(total_distance)} km</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Total Fuel</h3>
            <h2>{format_number(total_fuel/1000, 1)} tonnes</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Total CO2</h3>
            <h2>{format_number(total_emissions/1000, 1)} tonnes</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # If we have modified data, show the comparison
    if modified_data is not None:
        st.markdown("### Emissions After Interventions")
        
        new_total_emissions = modified_data['co2_emissions_kg'].sum()
        reduction = total_emissions - new_total_emissions
        reduction_percent = (reduction / total_emissions) * 100
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>New Total CO2</h3>
                <h2>{format_number(new_total_emissions/1000, 1)} tonnes</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3>CO2 Reduction</h3>
                <h2 class="green-text">{format_number(reduction/1000, 1)} tonnes</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h3>Reduction Percentage</h3>
                <h2 class="green-text">{format_number(reduction_percent, 2)}%</h2>
            </div>
            """, unsafe_allow_html=True)

def display_summary_charts(data):
    """
    Display summary charts in the dashboard
    
    Parameters:
    -----------
    data : pandas.DataFrame
        Flight data
    """
    logger.info("Displaying summary charts")
    
    # Top charts row
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<h3 class="sub-header">Emissions by Aircraft Type</h3>', unsafe_allow_html=True)
        fig = create_emissions_by_aircraft_chart(data)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown('<h3 class="sub-header">Emissions by Route Distance</h3>', unsafe_allow_html=True)
        fig = create_emissions_by_distance_chart(data)
        st.plotly_chart(fig, use_container_width=True)

def display_data_table(data, columns=None):
    """
    Display data table with selected columns
    
    Parameters:
    -----------
    data : pandas.DataFrame
        Flight data
    columns : list, optional
        List of columns to display
    """
    logger.info("Displaying data table")
    
    if columns is None:
        # Default columns to display
        columns = ['flight_id', 'date', 'origin', 'destination', 'distance_km', 
                   'aircraft_type', 'fuel_consumed_kg', 'co2_emissions_kg']
    
    st.dataframe(data[columns], height=300)