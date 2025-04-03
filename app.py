import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Set page configuration
st.set_page_config(
    page_title="CO2 Emission Reduction Analytics Platform",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem !important;
        color: #1E3F66 !important;
    }
    .sub-header {
        font-size: 1.5rem !important;
        color: #2E5984 !important;
    }
    .card {
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        background-color: #f8f9fa;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .metric-card {
        text-align: center;
        padding: 15px;
        border-radius: 10px;
        background-color: #e9ecef;
        margin: 5px;
    }
    .green-text {
        color: #28a745;
    }
    .red-text {
        color: #dc3545;
    }
</style>
""", unsafe_allow_html=True)

# Helper functions for data generation
def generate_flight_data(num_flights=1000):
    """Generate synthetic flight data for demonstration"""
    np.random.seed(42)
    
    # Create base dataframe
    today = datetime.now()
    
    # Aircraft types with different emissions profiles
    aircraft_types = ['A320', 'B737', 'A350', 'B777', 'A220', 'B787']
    aircraft_weights = {
        'A320': (65000, 78000),
        'B737': (62000, 82000),
        'A350': (185000, 220000),
        'B777': (190000, 247000),
        'A220': (45000, 60000),
        'B787': (150000, 180000)
    }
    
    routes = [
        ('Paris', 'London', 350),
        ('Paris', 'Madrid', 1050),
        ('Paris', 'Rome', 1100),
        ('Paris', 'Berlin', 880),
        ('Paris', 'Istanbul', 2200),
        ('Paris', 'Dubai', 5200),
        ('Paris', 'New York', 5800),
        ('Paris', 'Tokyo', 9700),
        ('Paris', 'Singapore', 10700)
    ]
    
    data = []
    flight_ids = [f"FL{i:04d}" for i in range(1, num_flights + 1)]
    
    for flight_id in flight_ids:
        # Select random route
        origin, destination, distance = routes[np.random.randint(0, len(routes))]
        
        # Select random aircraft
        aircraft = np.random.choice(aircraft_types)
        min_weight, max_weight = aircraft_weights[aircraft]
        takeoff_weight = np.random.randint(min_weight, max_weight)
        
        # Generate flight parameters
        flight_date = today - timedelta(days=np.random.randint(0, 90))
        flight_hour = np.random.randint(0, 24)
        flight_minute = np.random.choice([0, 15, 30, 45])
        departure_time = flight_date.replace(hour=flight_hour, minute=flight_minute)
        
        # Calculate flight parameters
        flight_level = np.random.randint(300, 410) * 100  # FL300-FL410
        avg_speed = np.random.randint(750, 900)  # km/h
        
        # Weather conditions (simplified)
        headwind = np.random.randint(-50, 80)  # negative for tailwind
        temperature_deviation = np.random.randint(-15, 15)  # from ISA
        
        # Calculate fuel and emissions
        base_fuel_per_km = {
            'A320': 3.0,
            'B737': 3.2,
            'A350': 7.5,
            'B777': 8.0,
            'A220': 2.5,
            'B787': 6.8
        }
        
        # Add some randomness to fuel consumption
        fuel_efficiency_factor = 0.85 + (np.random.rand() * 0.3)  # 0.85 to 1.15
        
        # Weather impact - headwind increases fuel consumption
        weather_factor = 1.0 + (headwind / 500)
        
        # Weight impact
        weight_factor = 0.9 + ((takeoff_weight - min_weight) / (max_weight - min_weight)) * 0.2
        
        # Calculate total fuel based on factors
        fuel_per_km = base_fuel_per_km[aircraft]
        total_fuel = fuel_per_km * distance * fuel_efficiency_factor * weather_factor * weight_factor
        
        # CO2 emissions: ~3.16 kg CO2 per kg of jet fuel
        co2_emissions = total_fuel * 3.16
        
        # Optimize climb calculation
        optimal_climb = np.random.choice([True, False], p=[0.4, 0.6])
        potential_savings = 0
        if not optimal_climb:
            # If not using optimal climb, calculate potential savings (1-3% of fuel)
            saving_percentage = 0.01 + (np.random.rand() * 0.02)
            potential_savings = total_fuel * saving_percentage
        
        # Add row to data
        data.append({
            'flight_id': flight_id,
            'date': flight_date.strftime('%Y-%m-%d'),
            'origin': origin,
            'destination': destination,
            'distance_km': distance,
            'aircraft_type': aircraft,
            'takeoff_weight_kg': takeoff_weight,
            'flight_level': flight_level,
            'avg_speed_kmh': avg_speed,
            'headwind_kmh': headwind,
            'temperature_deviation': temperature_deviation,
            'fuel_consumed_kg': total_fuel,
            'co2_emissions_kg': co2_emissions,
            'optimal_climb_used': optimal_climb,
            'potential_fuel_savings_kg': potential_savings,
            'departure_time': departure_time
        })
    
    return pd.DataFrame(data)

def calculate_emission_reduction(data, interventions):
    """Calculate the emission reduction based on selected interventions"""
    total_emissions = data['co2_emissions_kg'].sum()
    total_fuel = data['fuel_consumed_kg'].sum()
    
    # Copy the data to avoid modifying the original
    modified_data = data.copy()
    savings = {}
    
    # Apply selected interventions
    if 'optimize_climb' in interventions:
        # Calculate savings for flights not using optimal climb
        non_optimal_flights = modified_data[~modified_data['optimal_climb_used']]
        climb_savings = non_optimal_flights['potential_fuel_savings_kg'].sum()
        modified_data.loc[~modified_data['optimal_climb_used'], 'fuel_consumed_kg'] -= modified_data.loc[~modified_data['optimal_climb_used'], 'potential_fuel_savings_kg']
        co2_reduction = climb_savings * 3.16
        savings['optimize_climb'] = co2_reduction
    
    if 'weight_reduction' in interventions:
        # Simulate 1% weight reduction = ~0.6% fuel savings
        weight_factor = 0.006
        weight_savings = modified_data['fuel_consumed_kg'] * weight_factor
        modified_data['fuel_consumed_kg'] -= weight_savings
        co2_reduction = weight_savings.sum() * 3.16
        savings['weight_reduction'] = co2_reduction
    
    if 'efficient_routing' in interventions:
        # Simulate more efficient routes (1-2% savings)
        route_factor = 0.015
        route_savings = modified_data['fuel_consumed_kg'] * route_factor
        modified_data['fuel_consumed_kg'] -= route_savings
        co2_reduction = route_savings.sum() * 3.16
        savings['efficient_routing'] = co2_reduction
    
    if 'engine_washing' in interventions:
        # Engine washing can save ~0.5-1% fuel
        engine_factor = 0.008
        engine_savings = modified_data['fuel_consumed_kg'] * engine_factor
        modified_data['fuel_consumed_kg'] -= engine_savings
        co2_reduction = engine_savings.sum() * 3.16
        savings['engine_washing'] = co2_reduction
    
    # Recalculate CO2 emissions
    modified_data['co2_emissions_kg'] = modified_data['fuel_consumed_kg'] * 3.16
    
    # Calculate total savings
    new_total_emissions = modified_data['co2_emissions_kg'].sum()
    emission_reduction = total_emissions - new_total_emissions
    
    return modified_data, emission_reduction, savings

# Function to create dashboard components
def display_metrics(data, modified_data=None):
    """Display key metrics in the dashboard"""
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
            <h2>{total_flights:,}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Total Distance</h3>
            <h2>{total_distance:,.0f} km</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Total Fuel</h3>
            <h2>{total_fuel/1000:,.1f} tonnes</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Total CO2</h3>
            <h2>{total_emissions/1000:,.1f} tonnes</h2>
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
                <h2>{new_total_emissions/1000:,.1f} tonnes</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3>CO2 Reduction</h3>
                <h2 class="green-text">{reduction/1000:,.1f} tonnes</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h3>Reduction Percentage</h3>
                <h2 class="green-text">{reduction_percent:.2f}%</h2>
            </div>
            """, unsafe_allow_html=True)

# Navigation and content setup
def main():
    # Sidebar navigation
    st.sidebar.image("https://via.placeholder.com/150x80?text=SITA+Air", width=150)
    st.sidebar.title("Navigation")
    
    page = st.sidebar.radio("Select Page", [
        "Dashboard", 
        "Flight Analysis", 
        "Emission Reduction Scenarios", 
        "Route Optimization"
    ])
    
    # Generate sample data (in real app, this would be loaded from a database)
    data = generate_flight_data(500)
    
    if page == "Dashboard":
        dashboard_page(data)
    elif page == "Flight Analysis":
        flight_analysis_page(data)
    elif page == "Emission Reduction Scenarios":
        emission_reduction_page(data)
    elif page == "Route Optimization":
        route_optimization_page(data)

def dashboard_page(data):
    st.markdown('<h1 class="main-header">CO2 Emission Reduction Analytics Platform</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="card">
        This dashboard provides analytics for monitoring and reducing carbon emissions from flight operations.
        Analyze flight data, identify emission patterns, and simulate various intervention scenarios.
    </div>
    """, unsafe_allow_html=True)
    
    # Display key metrics
    display_metrics(data)
    
    # Top charts row
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<h3 class="sub-header">Emissions by Aircraft Type</h3>', unsafe_allow_html=True)
        
        # Group data by aircraft type
        aircraft_emissions = data.groupby('aircraft_type').agg({
            'co2_emissions_kg': 'sum',
            'distance_km': 'sum',
            'flight_id': 'count'
        }).reset_index()
        
        aircraft_emissions['emissions_per_km'] = aircraft_emissions['co2_emissions_kg'] / aircraft_emissions['distance_km']
        aircraft_emissions = aircraft_emissions.sort_values('emissions_per_km', ascending=False)
        
        # Create a custom color scale
        color_scale = px.colors.sequential.Blues
        
        fig = px.bar(
            aircraft_emissions,
            x='aircraft_type',
            y='emissions_per_km',
            color='emissions_per_km',
            color_continuous_scale=color_scale,
            labels={
                'aircraft_type': 'Aircraft Type',
                'emissions_per_km': 'CO2 Emissions (kg) per km'
            },
            text=aircraft_emissions['emissions_per_km'].round(2)
        )
        
        fig.update_layout(
            height=400,
            coloraxis_showscale=False,
            title_x=0.5,
            xaxis_title="",
            yaxis_title="kg CO2 per km",
        )
        
        fig.update_traces(texttemplate='%{text}', textposition='outside')
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown('<h3 class="sub-header">Emissions by Route Distance</h3>', unsafe_allow_html=True)
        
        # Create bins for route distances
        data['distance_bin'] = pd.cut(
            data['distance_km'], 
            bins=[0, 1000, 3000, 6000, 12000],
            labels=['Short (<1000km)', 'Medium (1000-3000km)', 'Long (3000-6000km)', 'Ultra-Long (>6000km)']
        )
        
        distance_emissions = data.groupby('distance_bin').agg({
            'co2_emissions_kg': 'sum',
            'distance_km': 'sum',
            'flight_id': 'count'
        }).reset_index()
        
        distance_emissions['emissions_per_flight'] = distance_emissions['co2_emissions_kg'] / distance_emissions['flight_id']
        
        fig = px.bar(
            distance_emissions,
            x='distance_bin',
            y='emissions_per_flight',
            color='emissions_per_flight',
            color_continuous_scale='Reds',
            labels={
                'distance_bin': 'Route Distance Category',
                'emissions_per_flight': 'Avg CO2 Emissions per Flight (kg)'
            },
            text=distance_emissions['emissions_per_flight'].round(0)
        )
        
        fig.update_layout(
            height=400,
            coloraxis_showscale=False,
            title_x=0.5,
            xaxis_title="",
            yaxis_title="kg CO2 per flight"
        )
        
        fig.update_traces(texttemplate='%{text:.0f}', textposition='outside')
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Bottom row charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<h3 class="sub-header">Monthly Emissions Trend</h3>', unsafe_allow_html=True)
        
        # Convert date string to datetime for grouping
        data['date'] = pd.to_datetime(data['date'])
        data['month'] = data['date'].dt.strftime('%Y-%m')
        
        monthly_emissions = data.groupby('month').agg({
            'co2_emissions_kg': 'sum',
            'flight_id': 'count'
        }).reset_index()
        
        # Sort by month
        monthly_emissions = monthly_emissions.sort_values('month')
        
        fig = px.line(
            monthly_emissions, 
            x='month', 
            y='co2_emissions_kg',
            markers=True,
            labels={
                'month': 'Month',
                'co2_emissions_kg': 'Total CO2 Emissions (kg)'
            }
        )
        
        fig.update_layout(
            height=400,
            title_x=0.5,
            xaxis_title="",
            yaxis_title="kg CO2"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown('<h3 class="sub-header">Potential Savings from Climb Optimization</h3>', unsafe_allow_html=True)
        
        # Calculate potential savings from optimizing climb profiles
        non_optimal = data[~data['optimal_climb_used']]
        potential_savings = non_optimal.groupby('aircraft_type').agg({
            'potential_fuel_savings_kg': 'sum',
            'flight_id': 'count'
        }).reset_index()
        
        # Calculate CO2 savings (3.16 kg CO2 per kg fuel)
        potential_savings['co2_savings_kg'] = potential_savings['potential_fuel_savings_kg'] * 3.16
        
        # Sort by potential savings
        potential_savings = potential_savings.sort_values('co2_savings_kg', ascending=False)
        
        fig = px.bar(
            potential_savings,
            x='aircraft_type',
            y='co2_savings_kg',
            color='co2_savings_kg',
            color_continuous_scale='Greens',
            labels={
                'aircraft_type': 'Aircraft Type',
                'co2_savings_kg': 'Potential CO2 Savings (kg)'
            },
            text=potential_savings['co2_savings_kg'].round(0)
        )
        
        fig.update_layout(
            height=400,
            coloraxis_showscale=False,
            title_x=0.5,
            xaxis_title="",
            yaxis_title="kg CO2 Savings"
        )
        
        fig.update_traces(texttemplate='%{text:.0f}', textposition='outside')
        
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("""
    <div class="card">
        <h3>Data Overview</h3>
        <p>Scroll through the table below to see detailed flight data.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display data table with pagination
    display_cols = ['flight_id', 'date', 'origin', 'destination', 'distance_km', 
                    'aircraft_type', 'fuel_consumed_kg', 'co2_emissions_kg', 'optimal_climb_used']
    
    st.dataframe(data[display_cols], height=300)

def flight_analysis_page(data):
    st.markdown('<h1 class="main-header">Flight Emissions Analysis</h1>', unsafe_allow_html=True)
    
    # Filter section
    st.markdown('<h3 class="sub-header">Filter Data</h3>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        aircraft_options = ['All'] + sorted(data['aircraft_type'].unique().tolist())
        selected_aircraft = st.selectbox("Aircraft Type", aircraft_options)
    
    with col2:
        route_options = ['All'] + sorted([f"{o} - {d}" for o, d in 
                                        zip(data['origin'].unique(), data['destination'].unique())])
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
    
    # Apply filters
    filtered_data = data.copy()
    
    if selected_aircraft != 'All':
        filtered_data = filtered_data[filtered_data['aircraft_type'] == selected_aircraft]
    
    if selected_route != 'All':
        origin, destination = selected_route.split(' - ')
        filtered_data = filtered_data[(filtered_data['origin'] == origin) & 
                                       (filtered_data['destination'] == destination)]
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_data = filtered_data[(filtered_data['date'].dt.date >= start_date) & 
                                       (filtered_data['date'].dt.date <= end_date)]
    
    # Display metrics for filtered data
    display_metrics(filtered_data)
    
    # Analysis charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<h3 class="sub-header">Emissions vs Flight Level</h3>', unsafe_allow_html=True)
        
        # Group by flight level
        fl_data = filtered_data.groupby('flight_level').agg({
            'co2_emissions_kg': 'mean',
            'distance_km': 'mean',
            'flight_id': 'count'
        }).reset_index()
        
        fl_data['emissions_per_km'] = fl_data['co2_emissions_kg'] / fl_data['distance_km']
        
        fig = px.scatter(
            fl_data,
            x='flight_level',
            y='emissions_per_km',
            size='flight_id',
            color='emissions_per_km',
            color_continuous_scale='Blues',
            labels={
                'flight_level': 'Flight Level (ft)',
                'emissions_per_km': 'Avg CO2 per km (kg)',
                'flight_id': 'Number of Flights'
            }
        )
        
        fig.update_layout(
            height=400,
            title_x=0.5,
            xaxis_title="Flight Level (ft)",
            yaxis_title="kg CO2 per km"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown('<h3 class="sub-header">Impact of Headwind on Emissions</h3>', unsafe_allow_html=True)
        
        # Create bins for headwind
        filtered_data['headwind_bin'] = pd.cut(
            filtered_data['headwind_kmh'], 
            bins=[-50, -20, 0, 20, 40, 80],
            labels=['Strong Tailwind', 'Light Tailwind', 'Neutral', 'Light Headwind', 'Strong Headwind']
        )
        
        wind_data = filtered_data.groupby('headwind_bin').agg({
            'co2_emissions_kg': 'mean',
            'distance_km': 'mean',
            'flight_id': 'count'
        }).reset_index()
        
        wind_data['emissions_per_km'] = wind_data['co2_emissions_kg'] / wind_data['distance_km']
        
        # Sort by headwind category
        wind_category_order = ['Strong Tailwind', 'Light Tailwind', 'Neutral', 'Light Headwind', 'Strong Headwind']
        wind_data['headwind_bin'] = pd.Categorical(wind_data['headwind_bin'], categories=wind_category_order, ordered=True)
        wind_data = wind_data.sort_values('headwind_bin')
        
        fig = px.bar(
            wind_data,
            x='headwind_bin',
            y='emissions_per_km',
            color='emissions_per_km',
            color_continuous_scale='RdBu_r',
            labels={
                'headwind_bin': 'Wind Condition',
                'emissions_per_km': 'Avg CO2 per km (kg)'
            },
            text=wind_data['emissions_per_km'].round(2)
        )
        
        fig.update_layout(
            height=400,
            coloraxis_showscale=False,
            title_x=0.5,
            xaxis_title="",
            yaxis_title="kg CO2 per km"
        )
        
        fig.update_traces(texttemplate='%{text}', textposition='outside')
        
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

def emission_reduction_page(data):
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
        modified_data, total_reduction, savings_by_intervention = calculate_emission_reduction(data, selected_interventions)
        
        # Display metrics with comparison
        display_metrics(data, modified_data)
        
        # Show breakdown of savings by intervention
        st.markdown('<h3 class="sub-header">Emission Reduction by Intervention</h3>', unsafe_allow_html=True)
        
        if savings_by_intervention:
            # Prepare data for chart
            interventions_labels = {
                'optimize_climb': 'Optimize Climb Profiles',
                'weight_reduction': 'Aircraft Weight Reduction',
                'efficient_routing': 'Efficient Flight Routing',
                'engine_washing': 'Regular Engine Washing'
            }
            
            savings_data = pd.DataFrame({
                'intervention': [interventions_labels[i] for i in savings_by_intervention.keys()],
                'co2_reduction_kg': list(savings_by_intervention.values())
            })
            
            # Sort by impact
            savings_data = savings_data.sort_values('co2_reduction_kg', ascending=False)
            
            # Create chart
            fig = px.bar(
                savings_data,
                x='intervention',
                y='co2_reduction_kg',
                color='co2_reduction_kg',
                color_continuous_scale='Greens',
                labels={
                    'intervention': 'Intervention',
                    'co2_reduction_kg': 'CO2 Reduction (kg)'
                },
                text=savings_data['co2_reduction_kg'].round(0)
            )
            
            fig.update_layout(
                height=400,
                coloraxis_showscale=False,
                title_x=0.5,
                xaxis_title="",
                yaxis_title="kg CO2 Reduction"
            )
            
            fig.update_traces(texttemplate='%{text:.0f}', textposition='outside')
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show detailed savings breakdown
            st.markdown('<h3 class="sub-header">Detailed Savings Breakdown</h3>', unsafe_allow_html=True)
            
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
            
            # Calculate fuel savings (CO2 / 3.16)
            total_fuel_savings = total_reduction / 3.16
            
            # Calculate financial savings
            carbon_savings = (total_reduction / 1000) * carbon_price
            fuel_savings = (total_fuel_savings / 1000) * fuel_price
            total_savings = carbon_savings + fuel_savings
            
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
                    <h2 class="green-text">€{fuel_savings:,.0f}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Carbon Credit Savings</h3>
                    <h2 class="green-text">€{carbon_savings:,.0f}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Total Savings</h3>
                    <h2 class="green-text">€{total_savings:,.0f}</h2>
                </div>
                """, unsafe_allow_html=True)

def route_optimization_page(data):
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
    
    # Filter data for selected routes
    filtered_data = pd.DataFrame()
    for route in selected_routes:
        origin, destination = route.split(' - ')
        route_data = data[(data['origin'] == origin) & (data['destination'] == destination)].copy()
        route_data['route'] = route
        filtered_data = pd.concat([filtered_data, route_data])
    
    # Route efficiency metrics
    st.markdown('<h3 class="sub-header">Route Efficiency Metrics</h3>', unsafe_allow_html=True)
    
    route_metrics = filtered_data.groupby('route').agg({
        'co2_emissions_kg': ['mean', 'min', 'max', 'std'],
        'distance_km': 'mean',
        'fuel_consumed_kg': ['mean', 'min', 'max'],
        'flight_id': 'count'
    }).reset_index()
    
    # Flatten the multi-index columns
    route_metrics.columns = ['_'.join(col).strip('_') for col in route_metrics.columns.values]
    
    # Calculate emissions per km
    route_metrics['emissions_per_km'] = route_metrics['co2_emissions_kg_mean'] / route_metrics['distance_km_mean']
    route_metrics['min_emissions_per_km'] = route_metrics['co2_emissions_kg_min'] / route_metrics['distance_km_mean']
    route_metrics['max_emissions_per_km'] = route_metrics['co2_emissions_kg_max'] / route_metrics['distance_km_mean']
    
    # Calculate potential savings
    route_metrics['potential_savings_kg'] = route_metrics['co2_emissions_kg_mean'] - route_metrics['co2_emissions_kg_min']
    route_metrics['savings_percentage'] = (route_metrics['potential_savings_kg'] / route_metrics['co2_emissions_kg_mean']) * 100
    
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
                y=[row['min_emissions_per_km'], row['max_emissions_per_km']],
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
        
        # Find best and worst performers
        best_flight = route_detail_data.loc[route_detail_data['co2_emissions_kg'].idxmin()]
        worst_flight = route_detail_data.loc[route_detail_data['co2_emissions_kg'].idxmax()]
        
        st.markdown('<h3 class="sub-header">Best vs Worst Performance Analysis</h3>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class="card">
                <h4>Best Performing Flight: {best_flight['flight_id']}</h4>
                <p><strong>Date:</strong> {best_flight['date'].strftime('%Y-%m-%d')}</p>
                <p><strong>Aircraft:</strong> {best_flight['aircraft_type']}</p>
                <p><strong>Flight Level:</strong> {best_flight['flight_level']} ft</p>
                <p><strong>Takeoff Weight:</strong> {best_flight['takeoff_weight_kg']:,.0f} kg</p>
                <p><strong>Wind:</strong> {best_flight['headwind_kmh']:.1f} km/h {'headwind' if best_flight['headwind_kmh'] > 0 else 'tailwind'}</p>
                <p><strong>Optimal Climb:</strong> {'Yes' if best_flight['optimal_climb_used'] else 'No'}</p>
                <p><strong>CO2 Emissions:</strong> {best_flight['co2_emissions_kg']:,.1f} kg</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="card">
                <h4>Worst Performing Flight: {worst_flight['flight_id']}</h4>
                <p><strong>Date:</strong> {worst_flight['date'].strftime('%Y-%m-%d')}</p>
                <p><strong>Aircraft:</strong> {worst_flight['aircraft_type']}</p>
                <p><strong>Flight Level:</strong> {worst_flight['flight_level']} ft</p>
                <p><strong>Takeoff Weight:</strong> {worst_flight['takeoff_weight_kg']:,.0f} kg</p>
                <p><strong>Wind:</strong> {worst_flight['headwind_kmh']:.1f} km/h {'headwind' if worst_flight['headwind_kmh'] > 0 else 'tailwind'}</p>
                <p><strong>Optimal Climb:</strong> {'Yes' if worst_flight['optimal_climb_used'] else 'No'}</p>
                <p><strong>CO2 Emissions:</strong> {worst_flight['co2_emissions_kg']:,.1f} kg</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Calculate difference and savings potential
        emissions_diff = worst_flight['co2_emissions_kg'] - best_flight['co2_emissions_kg']
        emissions_diff_percent = (emissions_diff / worst_flight['co2_emissions_kg']) * 100
        
        st.markdown(f"""
        <div class="card">
            <h4>Optimization Potential</h4>
            <p>By optimizing all flights on this route to match the best performer, you could save up to 
            <span class="green-text"><strong>{emissions_diff:,.1f} kg CO2</strong></span> per flight, 
            representing a <span class="green-text"><strong>{emissions_diff_percent:.1f}%</strong></span> reduction.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Key recommendations
        st.markdown('<h3 class="sub-header">Key Recommendations</h3>', unsafe_allow_html=True)
        
        recommendations = []
        
        # Based on climb profile
        if not best_flight['optimal_climb_used'] and worst_flight['optimal_climb_used']:
            recommendations.append("Despite the best flight not using optimal climb profiles, it performed better. Investigate other factors affecting this route.")
        elif best_flight['optimal_climb_used'] and not worst_flight['optimal_climb_used']:
            recommendations.append("Implement optimal climb profiles for all flights on this route to reduce emissions.")
        
        # Based on flight level
        if abs(best_flight['flight_level'] - worst_flight['flight_level']) > 1000:
            recommendations.append(f"Consider standardizing flight level around {best_flight['flight_level']} ft, which showed better efficiency.")
        
        # Based on weight
        if best_flight['takeoff_weight_kg'] < worst_flight['takeoff_weight_kg']:
            weight_diff = worst_flight['takeoff_weight_kg'] - best_flight['takeoff_weight_kg']
            weight_diff_percent = (weight_diff / worst_flight['takeoff_weight_kg']) * 100
            if weight_diff_percent > 5:  # If difference is significant
                recommendations.append(f"Review weight management. The best flight was {weight_diff_percent:.1f}% lighter.")
        
        # Based on wind
        if (best_flight['headwind_kmh'] < 0 and worst_flight['headwind_kmh'] > 0) or (abs(best_flight['headwind_kmh'] - worst_flight['headwind_kmh']) > 20):
            recommendations.append("Consider wind patterns when planning flights on this route. The best performing flight had more favorable wind conditions.")
        
        # Display recommendations
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                st.markdown(f"""
                <div class="card">
                    <p><strong>{i}.</strong> {rec}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="card">
                <p>No clear pattern distinguishes the best and worst performers. Further data collection and analysis recommended.</p>
            </div>
            """, unsafe_allow_html=True)

# Run the app
if __name__ == "__main__":
    main()
