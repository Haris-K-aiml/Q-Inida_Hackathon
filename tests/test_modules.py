"""
Unit and Integration Tests for QuantumGreen Fleet AI Modules.
Tests maritime physics models, validation rules, IMO compliance, and optimization solvers.
"""

import unittest
from datetime import datetime, timedelta

from modules.data_models import (
    VesselInfo, VoyageInfo, OperatingConditions, ScenarioInput,
    VesselType, FuelType, DataProvenance
)
from modules.validation import MaritimeValidator, validate_imo, validate_mmsi, convert_distance, convert_speed
from modules.fuel_model import MaritimeFuelModel
from modules.emissions_calculator import EmissionsCalculator
from modules.voyage_planner import VoyagePlanner
from modules.ais_service import AISService
from modules.weather_service import WeatherService
from modules.scheduling_engine import SchedulingEngine
from modules.classical_optimizer import ClassicalOptimizer
from modules.quantum_optimizer import QuantumInspiredFleetOptimizer
from modules.ai_engine import MaritimeAIEngine
from modules.scenario_engine import ScenarioEngine


class TestMaritimeValidation(unittest.TestCase):
    """Tests for input validation, IMO checksums, bounds, and contradictions."""

    def test_valid_imo_checksum(self):
        # 9345673: 9*7 + 3*6 + 4*5 + 5*4 + 6*3 + 7*2 = 63+18+20+20+18+14 = 153 -> 3.
        valid, msg = validate_imo("9345673")
        self.assertTrue(valid, msg)

    def test_invalid_imo_checksum(self):
        # Corrupted checksum
        valid, msg = validate_imo("9345674")
        self.assertFalse(valid)
        self.assertIn("checksum validation failed", msg)

    def test_invalid_imo_length(self):
        valid, msg = validate_imo("12345")
        self.assertFalse(valid)
        self.assertIn("must be exactly 7 digits", msg)

    def test_valid_mmsi(self):
        valid, msg = validate_mmsi("419001234")
        self.assertTrue(valid)

    def test_invalid_mmsi(self):
        valid, msg = validate_mmsi("123")
        self.assertFalse(valid)

    def test_contradiction_cargo_exceeds_capacity(self):
        v = VesselInfo(max_cargo_capacity_tonnes=5000.0, current_cargo_weight_tonnes=8000.0)
        voy = VoyageInfo(departure_port="Chennai Port", destination_port="Singapore")
        c = OperatingConditions()
        scenario = ScenarioInput(vessel=v, voyage=voy, conditions=c, problem_statement="Test cargo overload")
        
        is_valid, errors, _ = MaritimeValidator.validate_scenario(scenario)
        self.assertFalse(is_valid)
        self.assertTrue(any("exceeds vessel maximum cargo capacity" in err for err in errors))

    def test_contradiction_departure_after_deadline(self):
        now = datetime.now()
        v = VesselInfo()
        voy = VoyageInfo(
            departure_port="Chennai Port",
            destination_port="Singapore",
            departure_time=now + timedelta(days=5),
            delivery_deadline=now + timedelta(days=2)
        )
        c = OperatingConditions()
        scenario = ScenarioInput(vessel=v, voyage=voy, conditions=c, problem_statement="Test schedule breach")
        
        is_valid, errors, _ = MaritimeValidator.validate_scenario(scenario)
        self.assertFalse(is_valid)
        self.assertTrue(any("Departure time" in err and "deadline" in err for err in errors))

    def test_unit_conversions(self):
        # 100 NM to km
        km = convert_distance(100.0, "NM", "km")
        self.assertAlmostEqual(km, 185.2, places=1)
        # 185.2 km to NM
        nm = convert_distance(185.2, "km", "NM")
        self.assertAlmostEqual(nm, 100.0, places=1)
        # Knots to km/h
        kmh = convert_speed(12.0, "knots", "km/h")
        self.assertAlmostEqual(kmh, 12.0 * 1.852, places=1)


class TestHydrodynamicFuelModel(unittest.TestCase):
    """Tests for Admiralty formula, cubic speed scaling, and Kwon weather resistance."""

    def setUp(self):
        self.vessel = VesselInfo(
            name="MV Ocean Pioneer",
            vessel_type=VesselType.CARGO_GENERAL.value,
            dwt_tonnes=12000.0,
            max_cargo_capacity_tonnes=10000.0,
            current_cargo_weight_tonnes=8000.0,
            fuel_type=FuelType.VLSFO.value,
            sfoc_g_per_kwh=175.0
        )

    def test_cubic_speed_law(self):
        # Compare power at 10 knots vs 12 knots (should scale roughly as (12/10)^3 = 1.728)
        p_10 = MaritimeFuelModel.calculate_propulsion_power(self.vessel, 10.0)
        p_12 = MaritimeFuelModel.calculate_propulsion_power(self.vessel, 12.0)
        ratio = p_12 / p_10
        expected_ratio = (12.0 / 10.0) ** 3
        self.assertAlmostEqual(ratio, expected_ratio, delta=0.1)

    def test_weather_added_resistance(self):
        # Calm sea factor 1.0 vs Rough sea factor 1.25
        res_calm = MaritimeFuelModel.calculate_voyage_fuel(self.vessel, 1000.0, 12.0, weather_factor=1.0)
        res_rough = MaritimeFuelModel.calculate_voyage_fuel(self.vessel, 1000.0, 12.0, weather_factor=1.25)
        # Main engine fuel burn should be proportionally higher in rough sea
        self.assertGreater(res_rough["main_engine_fuel_tonnes"], res_calm["main_engine_fuel_tonnes"])


class TestEmissionsAndCII(unittest.TestCase):
    """Tests for IMO MEPC carbon conversion and CII calculation."""

    def test_imo_carbon_factors(self):
        # 100 tonnes of VLSFO = 315.1 tonnes CO2
        co2_vlsfo = EmissionsCalculator.calculate_co2(100.0, FuelType.VLSFO.value)
        self.assertAlmostEqual(co2_vlsfo, 315.1, places=1)
        # 100 tonnes of LNG = 275.0 tonnes CO2
        co2_lng = EmissionsCalculator.calculate_co2(100.0, FuelType.LNG.value)
        self.assertAlmostEqual(co2_lng, 275.0, places=1)

    def test_cii_rating_output(self):
        v = VesselInfo(dwt_tonnes=12000.0)
        rating, attained, required, desc = EmissionsCalculator.calculate_cii(v, co2_tonnes=250.0, distance_nm=1580.0)
        self.assertIn(rating, ["A", "B", "C", "D", "E"])
        self.assertGreater(attained, 0.0)
        self.assertGreater(required, 0.0)


class TestOptimizationEngines(unittest.TestCase):
    """Tests for Classical vs Quantum-Inspired simulated annealing fleet solvers."""

    def setUp(self):
        self.vessels = [
            {"name": "Eco Ship", "capacity": 1200.0, "fuel_rate": 2.8},
            {"name": "Cargo Ship", "capacity": 900.0, "fuel_rate": 3.8},
            {"name": "Fast Ship", "capacity": 700.0, "fuel_rate": 5.0}
        ]
        self.shipments = [
            {"name": "Shipment 1", "cargo": 400.0},
            {"name": "Shipment 2", "cargo": 300.0},
            {"name": "Shipment 3", "cargo": 250.0},
            {"name": "Shipment 4", "cargo": 500.0}
        ]
        self.routes = [
            {"name": "Direct Route", "distance": 900.0, "weather": 1.20},
            {"name": "Coastal Route", "distance": 1100.0, "weather": 1.00},
            {"name": "Green Corridor", "distance": 1000.0, "weather": 0.90}
        ]

    def test_classical_optimizer(self):
        res = ClassicalOptimizer.solve_greedy_fleet_assignment(
            self.vessels, self.shipments, self.routes, fuel_price=500.0, carbon_tax=50.0
        )
        self.assertTrue(len(res["assignments"]) == 4)
        self.assertGreater(res["total_fuel_tonnes"], 0.0)

    def test_quantum_optimizer(self):
        res = QuantumInspiredFleetOptimizer.solve(
            self.vessels, self.shipments, self.routes,
            fuel_price=500.0, carbon_tax=50.0, iterations=500, random_seed=42
        )
        self.assertTrue(len(res["assignments"]) == 4)
        self.assertTrue(res["valid_plan"])
        self.assertGreater(res["total_fuel_tonnes"], 0.0)


class TestAISAndVoyagePlanner(unittest.TestCase):
    """Tests for AIS vessel registry and waypoint distance calculations."""

    def test_ais_lookup(self):
        found = AISService.lookup_vessel("Ocean Pioneer")
        self.assertIsNotNone(found)
        self.assertEqual(found["imo"], "9345673")

    def test_chennai_singapore_sailing_distance(self):
        dist, prov = VoyagePlanner.get_sailing_distance("Chennai Port", "Singapore")
        self.assertEqual(dist, 1580.0)
        self.assertIn("Verified", prov)


class TestSectionFExampleWorkflow(unittest.TestCase):
    """
    Tests the exact Section F Example:
    User enters:
    Ship type: Cargo vessel
    Departure: Chennai Port
    Destination: Singapore
    Cargo weight: 8,000 tonnes
    Planned speed: 12 knots
    Fuel price: 650 $/t
    Problem: 'Find a fuel-efficient voyage plan and estimate fuel consumption while keeping the arrival time reasonable.'
    """

    def test_full_section_f_workflow(self):
        vessel = VesselInfo(
            name="MV Ocean Pioneer",
            vessel_type=VesselType.CARGO_GENERAL.value,
            max_cargo_capacity_tonnes=10000.0,
            current_cargo_weight_tonnes=8000.0,
            fuel_type=FuelType.VLSFO.value,
            current_fuel_tonnes=220.0
        )
        voyage = VoyageInfo(
            departure_port="Chennai Port",
            destination_port="Singapore",
            distance_nm=1580.0,
            planned_speed_knots=12.0
        )
        conditions = OperatingConditions(
            fuel_price_per_tonne=650.0,
            weather_condition="Moderate Sea (BF 4)"
        )
        scenario = ScenarioInput(
            vessel=vessel,
            voyage=voyage,
            conditions=conditions,
            problem_statement="Find a fuel-efficient voyage plan and estimate fuel consumption while keeping the arrival time reasonable."
        )

        success, answer, warnings = MaritimeAIEngine.solve_scenario(scenario)
        self.assertTrue(success)
        self.assertIsNotNone(answer)

        # Verify all 10 mandatory sections
        self.assertTrue(len(answer.section_1_problem_understanding) > 10)
        self.assertTrue(len(answer.section_2_input_summary) >= 5)
        self.assertIn("data_quality_assessment", answer.section_3_data_quality_missing_info)
        self.assertTrue("Naval Architecture" in answer.section_4_technical_analysis)
        self.assertGreater(answer.section_5_calculated_results.fuel_consumption_tonnes, 0.0)
        self.assertGreater(answer.section_5_calculated_results.total_cost_usd, 0.0)
        self.assertIsNotNone(answer.section_6_recommended_solution["title"])
        self.assertTrue("Trade-Offs" in answer.section_7_explanation)
        self.assertIn("fuel_savings_tonnes", answer.section_8_expected_impact)
        self.assertIn("confidence_assessment", answer.section_9_confidence_and_limitations)
        self.assertTrue(len(answer.section_10_next_actions) >= 3)

        # Test Follow-up scenario (Section G: What if I increase the ship speed?)
        new_scenario, change_desc = ScenarioEngine.apply_follow_up(scenario, "speed_plus")
        self.assertEqual(new_scenario.voyage.planned_speed_knots, 13.5)
        
        success2, answer2, _ = MaritimeAIEngine.solve_scenario(new_scenario)
        self.assertTrue(success2)
        
        comparison = ScenarioEngine.compare_runs(answer, answer2, change_desc)
        self.assertIn("table", comparison)
        self.assertTrue(comparison["delta_fuel"] > 0)  # Faster speed uses more fuel


if __name__ == "__main__":
    unittest.main()
