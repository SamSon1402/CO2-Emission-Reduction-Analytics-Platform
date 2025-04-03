"""
Route Optimization page module for the CO2 Emission Reduction Analytics Platform
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import logging
from models.scenario_analyzer import analyze_route_optimization
from visualization.map_utils import create_route_map

logger = logging.getLogger(__name__)

def render_route_optimization(data):
    """
    Render the route optimization page
    
    Parameters:
    -----------
    data : pandas.DataFrame
        Flight data
    """
    logger.info("Rendering route optimization page")
    
    st.markdown('<h1 class="main-header">Route Optimization Analysis</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="card">
        <p>This page provides insights into route efficiency and identifies opportunities for optimization.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Select routes to analyze
    routes = data.groupby(['origin', 'destination']).size().reset_index().rename(columns={0: 'count'})
    routes['route'] = routes['origin'] + ' - ' + routes['destination']
    
    selected_routes = st.multiselect(
        "Select Routes to Analyze",
        options=routes['route'].tolist(),
        default=routes['route'].tolist()[:3]
    )
    
    if not selected_routes:
        st.warning("Please select at least one route to analyze.")
        return
    
    # Show route map
    st.markdown('<h3 class="sub-header">Route Map</h3>', unsafe_allow_html=True)
    
    map_color_by = st.radio("Color routes by:", ['emissions', 'frequency'], horizontal=True)
    route_map = create_route_map(data, selected_routes, map_color_by)
    st.plotly_chart(route_map, use_container_width=True)
    
    # Analyze selected routes
    route_analysis = analyze_route_optimization(data)
    route_metrics = route_analysis.get('route_metrics', pd.DataFrame())
    
    if not route_metrics.empty:
        # Filter for selected routes only
        route_metrics = route_metrics[route_metrics['route'].isin(selected_routes)]
        
        # Route efficiency metrics
        st.markdown('<h3 class="sub-header">Route Efficiency Metrics</h3>', unsafe_allow_html=True)
        
        # Display route metrics chart
        col1, col2 = st.columns(2)
        
        with col1:
            # Create chart showing min, mean, max emissions per route
            fig = go.Figure()
            
            for idx, row in route_metrics.iterrows():
                fig.add_trace(go.Bar(
                    x=[row['route']],
                    y=[row['emissions_per_km']],
                    name=row['route'],
                    text=[f"{row['emissions_per_km']:.2f}"],
                    textposition='outside'
                ))
                
                # Add error bars to show min and max
                fig.add_trace(go.Scatter(
                    x=[row['route'], row['route']],
                    y=[row['min_emissions_per_km'], row['co2_emissions_kg_max'] / row['distance_km_mean']],
                    mode='markers',
                    marker=dict(color='rgba(0,0,0,0.5)', size=8, symbol='line-ns'),
                    showlegend=False
                ))
            
            fig.update_layout(
                title="Emissions Efficiency by Route",
                xaxis_title="",
                yaxis_title="kg CO2 per km",
                height=400,
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Create chart showing potential savings percentage
            fig = px.bar(
                route_metrics,
                x='route',
                y='savings_percentage',
                color='savings_percentage',
                color_continuous_scale='Greens',
                labels={
                    'route': 'Route',
                    'savings_percentage': 'Potential Savings (%)'
                },
                text=route_metrics['savings_percentage'].round(1)
            )
            
            fig.update_layout(
                title="Potential Savings by Optimizing to Best Performance",
                height=400,
                coloraxis_showscale=False,
                xaxis_title="",
                yaxis_title="Potential Savings (%)"
            )
            
            fig.update_traces(texttemplate='%{text}%', textposition='outside')
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Detailed route analysis
        st.markdown('<h3 class="sub-header">Detailed Route Analysis</h3>', unsafe_allow_html=True)
        
        selected_route_detail = st.selectbox(
            "Select Route for Detailed Analysis",
            options=selected_routes
        )
        
        if selected_route_detail:
            origin, destination = selected_route_detail.split(' - ')
            route_detail_data = data[(data['origin'] == origin) & (data['destination'] == destination)].copy()
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Scatter plot of emissions vs flight level
                fig = px.scatter(
                    route_detail_data,
                    x='flight_level',
                    y='co2_emissions_kg',
                    color='optimal_climb_used',
                    size='takeoff_weight_kg',
                    hover_data=['flight_id', 'date', 'headwind_kmh'],
                    labels={
                        'flight_level': 'Flight Level (ft)',
                        'co2_emissions_kg': 'CO2 Emissions (kg)',
                        'optimal_climb_used': 'Optimal Climb Used',
                        'takeoff_weight_kg': 'Takeoff Weight (kg)'
                    }
                )
                
                fig.update_layout(
                    title=f"Emissions vs Flight Level: {selected_route_detail}",
                    height=400,
                    xaxis_title="Flight Level (ft)",
                    yaxis_title="CO2 Emissions (kg)"
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Emissions vs headwind
                fig = px.scatter(
                    route_detail_data,
                    x='headwind_kmh',
                    y='co2_emissions_kg',
                    color='optimal_climb_used',
                    size='takeoff_weight_kg',
                    hover_data=['flight_id', 'date', 'flight_level'],
                    labels={
                        'headwind_kmh': 'Headwind (km/h)',
                        'co2_emissions_kg': 'CO2 Emissions (kg)',
                        'optimal_climb_used': 'Optimal Climb Used',
                        'takeoff_weight_kg': 'Takeoff Weight (kg)'
                    }
                )
                
                # Add vertical line at 0 (no wind)
                fig.add_vline(x=0, line_dash="dash", line_color="gray")
                
                fig.update_layout(
                    title=f"Emissions vs Wind Conditions: {selected_route_detail}",
                    height=400,
                    xaxis_title="Headwind (km/h) | Negative = Tailwind",
                    yaxis_title="CO2 Emissions (kg)"
                )
                
                st.plotly_chart(fig, use_container_width=True)