"""
Flight Analysis page module for the CO2 Emission Reduction Analytics Platform
"""

import streamlit as st
import pandas as pd
import logging
from datetime import datetime, timedelta
import plotly.express as px
from visualization.dashboard import display_metrics
from visualization.charts import create_emissions_flight_level_chart, create_headwind_impact_chart
from data.data_processor import filter_data

logger = logging.getLogger(__name__)

def render_flight_analysis(data):
    """
    Render the flight analysis page
    
    Parameters:
    -----------
    data : pandas.DataFrame
        Flight data
    """
    logger.info("Rendering flight analysis page")
    
    st.markdown('<h1 class="main-header">Flight Emissions Analysis</h1>', unsafe_allow_html=True)
    
    # Filter section
    st.markdown('<h3 class="sub-header">Filter Data</h3>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        aircraft_options = ['All'] + sorted(data['aircraft_type'].unique().tolist())
        selected_aircraft = st.selectbox("Aircraft Type", aircraft_options)
    
    with col2:
        # Create route options
        routes = data.groupby(['origin', 'destination']).size().reset_index()
        routes['route'] = routes['origin'] + ' - ' + routes['destination']
        route_options = ['All'] + sorted(routes['route'].tolist())
        selected_route = st.selectbox("Route", route_options)
    
    with col3:
        # Convert date string to datetime for the date picker
        data['date'] = pd.to_datetime(data['date'])
        min_date = data['date'].min().date()
        max_date = data['date'].max().date()
        
        date_range = st.date_input(
            "Date Range",
            [min_date, max_date],
            min_value=min_date,
            max_value=max_date
        )
    
    # Filter data based on selections
    filtered_data = filter_data(data, selected_aircraft, selected_route, date_range)
    
    # Display metrics for filtered data
    display_metrics(filtered_data)
    
    # Analysis charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<h3 class="sub-header">Emissions vs Flight Level</h3>', unsafe_allow_html=True)
        fig = create_emissions_flight_level_chart(filtered_data)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown('<h3 class="sub-header">Impact of Headwind on Emissions</h3>', unsafe_allow_html=True)
        fig = create_headwind_impact_chart(filtered_data)
        st.plotly_chart(fig, use_container_width=True)
    
    # More in-depth analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<h3 class="sub-header">Takeoff Weight vs Emissions</h3>', unsafe_allow_html=True)
        
        # Create scatter plot of takeoff weight vs emissions
        fig = px.scatter(
            filtered_data,
            x='takeoff_weight_kg',
            y='co2_emissions_kg',
            color='aircraft_type',
            size='distance_km',
            hover_data=['flight_id', 'origin', 'destination'],
            labels={
                'takeoff_weight_kg': 'Takeoff Weight (kg)',
                'co2_emissions_kg': 'CO2 Emissions (kg)',
                'aircraft_type': 'Aircraft Type',
                'distance_km': 'Distance (km)'
            }
        )
        
        fig.update_layout(
            height=400,
            title_x=0.5,
            xaxis_title="Takeoff Weight (kg)",
            yaxis_title="CO2 Emissions (kg)"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown('<h3 class="sub-header">Optimal Climb Impact Analysis</h3>', unsafe_allow_html=True)
        
        # Compare emissions between flights with and without optimal climb
        climb_data = filtered_data.groupby(['aircraft_type', 'optimal_climb_used']).agg({
            'co2_emissions_kg': 'mean',
            'distance_km': 'mean',
            'flight_id': 'count'
        }).reset_index()
        
        climb_data['emissions_per_km'] = climb_data['co2_emissions_kg'] / climb_data['distance_km']
        
        # Create a more informative label
        climb_data['climb_profile'] = climb_data['optimal_climb_used'].apply(
            lambda x: 'Optimal Climb' if x else 'Standard Climb'
        )
        
        fig = px.bar(
            climb_data,
            x='aircraft_type',
            y='emissions_per_km',
            color='climb_profile',
            barmode='group',
            labels={
                'aircraft_type': 'Aircraft Type',
                'emissions_per_km': 'Avg CO2 per km (kg)',
                'climb_profile': 'Climb Profile'
            }
        )
        
        fig.update_layout(
            height=400,
            title_x=0.5,
            xaxis_title="",
            yaxis_title="kg CO2 per km",
            legend_title="Climb Profile"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Display detailed data table
    st.markdown('<h3 class="sub-header">Detailed Flight Data</h3>', unsafe_allow_html=True)
    
    display_cols = ['flight_id', 'date', 'origin', 'destination', 'distance_km', 
                    'aircraft_type', 'takeoff_weight_kg', 'flight_level',
                    'headwind_kmh', 'fuel_consumed_kg', 'co2_emissions_kg', 
                    'optimal_climb_used', 'potential_fuel_savings_kg']
    
    st.dataframe(filtered_data[display_cols], height=300)