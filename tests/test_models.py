"""
Tests for analytical models
"""

import unittest
import pandas as pd
import numpy as np
from models.emissions_calculator import calculate_emissions, calculate_fuel_consumption, calculate_emission_reductions
from models.scenario_analyzer import create_baseline_scenario, analyze_route_optimization

class TestEmissionsCalculator(unittest.TestCase):
    """Test emissions calculator functions"""
    
    def test_calculate_emissions(self):
        """Test calculate_emissions function"""
        # Test with single value
        self.assertEqual(calculate_emissions(1000), 3160)
        
        # Test with array
        fuel_values = [1000, 2000, 3000]
        expected = [3160, 6320, 9480]
        np.testing.assert_array_equal(calculate_emissions(fuel_values), expected)
    
    def test_calculate_fuel_consumption(self):
        """Test calculate_fuel_consumption function"""
        result = calculate_fuel_consumption(
            distance_km=1000,
            aircraft_type='A320',
            takeoff_weight_kg=70000,
            flight_level=36000,
            headwind_kmh=20,
            temperature_deviation=5,
            optimal_climb=True
        )
        
        # Check keys in result
        self.assertTrue('fuel_consumed_kg' in result)
        self.assertTrue('co2_emissions_kg' in result)
        self.assertTrue('potential_fuel_savings_kg' in result)
        
        # Check fuel to CO2 ratio
        self.assertAlmostEqual(result['co2_emissions_kg'] / result['fuel_consumed_kg'], 3.16, places=2)
        
        # Test with optimal_climb=False
        result2 = calculate_fuel_consumption(
            distance_km=1000,
            aircraft_type='A320',
            takeoff_weight_kg=70000,
            flight_level=36000,
            headwind_kmh=20,
            temperature_deviation=5,
            optimal_climb=False
        )
        
        # Should have potential savings
        self.assertGreater(result2['potential_fuel_savings_kg'], 0)
    
    def test_calculate_emission_reductions(self):
        """Test calculate_emission_reductions function"""
        # Create sample data
        data = pd.DataFrame({
            'flight_id': ['FL001', 'FL002'],
            'fuel_consumed_kg': [1000, 2000],
            'co2_emissions_kg': [3160, 6320],
            'optimal_climb_used': [True, False],
            'potential_fuel_savings_kg': [0, 40]
        })
        
        # Test with optimize_climb intervention
        modified_data, reduction, savings = calculate_emission_reductions(
            data, interventions=['optimize_climb']
        )
        
        # Check results
        self.assertAlmostEqual(reduction, 40 * 3.16, places=2)
        self.assertTrue('optimize_climb' in savings)
        self.assertAlmostEqual(savings['optimize_climb'], 40 * 3.16, places=2)

class TestScenarioAnalyzer(unittest.TestCase):
    """Test scenario analyzer functions"""
    
    def setUp(self):
        """Set up test data"""
        self.sample_data = pd.DataFrame({
            'flight_id': ['FL001', 'FL002', 'FL003', 'FL004'],
            'origin': ['Paris', 'Paris', 'London', 'Paris'],
            'destination': ['London', 'Berlin', 'Paris', 'Madrid'],
            'distance_km': [350, 880, 350, 1050],
            'fuel_consumed_kg': [1000, 2500, 1100, 7000],
            'co2_emissions_kg': [3160, 7900, 3476, 22120]
        })
    
    def test_create_baseline_scenario(self):
        """Test create_baseline_scenario function"""
        baseline = create_baseline_scenario(self.sample_data)
        
        # Check keys
        self.assertTrue('total_flights' in baseline)
        self.assertTrue('total_distance_km' in baseline)
        self.assertTrue('total_fuel_kg' in baseline)
        self.assertTrue('total_emissions_kg' in baseline)
        
        # Check values
        self.assertEqual(baseline['total_flights'], 4)
        self.assertEqual(baseline['total_distance_km'], 350 + 880 + 350 + 1050)
        self.assertEqual(baseline['total_fuel_kg'], 1000 + 2500 + 1100 + 7000)
        self.assertEqual(baseline['total_emissions_kg'], 3160 + 7900 + 3476 + 22120)

if __name__ == '__main__':
    unittest.main()