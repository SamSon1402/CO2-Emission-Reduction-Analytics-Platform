"""
Emission Reduction Scenarios page module for the CO2 Emission Reduction Analytics Platform
"""

import streamlit as st
import pandas as pd
import logging
from visualization.dashboard import display_metrics
from visualization.charts import create_intervention_savings_chart
from models.emissions_calculator import calculate_emission_reductions, calculate_financial_impact

logger = logging.getLogger(__name__)

def render_emission_reduction(data):
    """
    Render the emission reduction scenarios page
    
    Parameters:
    -----------
    data : pandas.DataFrame
        Flight data
    """
    logger.info("Rendering emission reduction page")
    
    st.markdown('<h1 class="main-header">Emission Reduction Scenarios</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="card">
        <p>This tool allows you to simulate the impact of various emission reduction interventions.
        Select different options to see how they would affect your overall carbon footprint.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display current emissions metrics
    display_metrics(data)
    
    # Intervention selection
    st.markdown('<h3 class="sub-header">Select Emission Reduction Interventions</h3>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="card">
            <h4>Flight Operations</h4>
        </div>
        """, unsafe_allow_html=True)
        
        optimize_climb = st.checkbox("Optimize Climb Profiles", value=True, 
                                    help="Apply SITA OptiClimb technology to calculate optimal climb speeds considering factors like air density and weight")
        
        efficient_routing = st.checkbox("Efficient Flight Routing", value=False,
                                       help="Optimize flight paths considering weather and airspace constraints")
    
    with col2:
        st.markdown("""
        <div class="card">
            <h4>Aircraft Optimizations</h4>
        </div>
        """, unsafe_allow_html=True)
        
        weight_reduction = st.checkbox("Aircraft Weight Reduction", value=False,
                                     help="Reduce unnecessary weight from aircraft (e.g., optimized water loads, lighter equipment)")
        
        engine_washing = st.checkbox("Regular Engine Washing", value=False,
                                   help="Implement regular engine washing to improve efficiency")
    
    # Create list of selected interventions
    selected_interventions = []
    if optimize_climb:
        selected_interventions.append('optimize_climb')
    if weight_reduction:
        selected_interventions.append('weight_reduction')
    if efficient_routing:
        selected_interventions.append('efficient_routing')
    if engine_washing:
        selected_interventions.append('engine_washing')
    
    # Calculate impact if any interventions are selected
    if selected_interventions:
        modified_data, total_reduction, savings_by_intervention = calculate_emission_reductions(data, selected_interventions)
        
        # Display metrics with comparison
        display_metrics(data, modified_data)
        
        # Show breakdown of savings by intervention
        st.markdown('<h3 class="sub-header">Emission Reduction by Intervention</h3>', unsafe_allow_html=True)
        
        if savings_by_intervention:
            fig = create_intervention_savings_chart(savings_by_intervention)
            st.plotly_chart(fig, use_container_width=True)
            
            # Show detailed savings breakdown
            st.markdown('<h3 class="sub-header">Detailed Savings Breakdown</h3>', unsafe_allow_html=True)
            
            # Prepare data for intervention labels
            interventions_labels = {
                'optimize_climb': 'Optimize Climb Profiles',
                'weight_reduction': 'Aircraft Weight Reduction',
                'efficient_routing': 'Efficient Flight Routing',
                'engine_washing': 'Regular Engine Washing'
            }
            
            savings_table = pd.DataFrame({
                'Intervention': [interventions_labels[i] for i in savings_by_intervention.keys()],
                'CO2 Reduction (kg)': [f"{val:.1f}" for val in savings_by_intervention.values()],
                'CO2 Reduction (tonnes)': [f"{val/1000:.2f}" for val in savings_by_intervention.values()],
                'Percentage of Total Reduction': [f"{(val/total_reduction)*100:.1f}%" for val in savings_by_intervention.values()]
            })
            
            st.table(savings_table)
            
            # ROI Calculator
            st.markdown('<h3 class="sub-header">Return on Investment Calculator</h3>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                carbon_price = st.number_input("Carbon Credit Price (EUR/tonne)", min_value=0, value=80, step=5)
                fuel_price = st.number_input("Jet Fuel Price (EUR/tonne)", min_value=0, value=800, step=50)
            
            # Calculate financial impact
            financial_impact = calculate_financial_impact(total_reduction, carbon_price, fuel_price)
            
            # Display financial impact
            st.markdown("""
            <div class="card">
                <h4>Financial Impact</h4>
                <p>Based on current prices, implementing the selected interventions would result in:</p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Fuel Savings</h3>
                    <h2 class="green-text">€{financial_impact['fuel_cost_savings_eur']:,.0f}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Carbon Credit Savings</h3>
                    <h2 class="green-text">€{financial_impact['carbon_savings_eur']:,.0f}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Total Savings</h3>
                    <h2 class="green-text">€{financial_impact['total_savings_eur']:,.0f}</h2>
                </div>
                """, unsafe_allow_html=True)