"""
Scenario and Acceptance Tests for QuantumGreen Fleet AI.
Validates all Section B questions, Section F baseline interaction,
Section G follow-ups, and Section H safety & infeasibility constraints.
"""

import unittest
from datetime import datetime, timedelta

from modules.data_models import (
    VesselInfo, VoyageInfo, OperatingConditions, ScenarioInput,
    VesselType, FuelType
)
from modules.ai_engine import MaritimeAIEngine
from modules.scenario_engine import ScenarioEngine


class TestSectionBQuestions(unittest.TestCase):
    """Verifies that all 10 maritime questions from Section B are accurately parsed and solved."""

    def setUp(self):
        self.vessel = VesselInfo(
            name="MV Ocean Pioneer",
            imo="9345673",
            vessel_type=VesselType.CARGO_GENERAL.value,
            max_cargo_capacity_tonnes=10000.0,
            current_cargo_weight_tonnes=8000.0,
            current_fuel_tonnes=220.0,
            fuel_type=FuelType.VLSFO.value
        )
        self.voyage = VoyageInfo(
            departure_port="Chennai Port",
            destination_port="Singapore",
            distance_nm=1580.0,
            planned_speed_knots=12.0,
            departure_time=datetime.now(),
            delivery_deadline=datetime.now() + timedelta(days=7)
        )
        self.conditions = OperatingConditions(
            fuel_price_per_tonne=650.0,
            weather_condition="Moderate Sea (BF 4)",
            carbon_emission_budget_tonnes=250.0
        )

    def _run_question(self, question_text: str):
        scenario = ScenarioInput(
            vessel=self.vessel,
            voyage=self.voyage,
            conditions=self.conditions,
            problem_statement=question_text
        )
        success, answer, _ = MaritimeAIEngine.solve_scenario(scenario)
        self.assertTrue(success, f"Failed for question: {question_text}")
        self.assertIsNotNone(answer)
        self.assertIsNotNone(answer.section_1_problem_understanding)
        self.assertIsNotNone(answer.section_6_recommended_solution)
        self.assertIsNotNone(answer.section_5_calculated_results)
        return answer

    def test_q1_excess_fuel(self):
        ans = self._run_question("Why is my ship consuming more fuel than expected?")
        self.assertEqual(ans.problem_type, "EXCESS_FUEL_CONSUMPTION")
        self.assertIn("Fouling", ans.section_6_recommended_solution["title"])

    def test_q2_route_comparison(self):
        ans = self._run_question("Which route is more fuel-efficient for this voyage?")
        self.assertEqual(ans.problem_type, "ROUTE_COMPARISON")
        self.assertTrue(len(ans.route_comparisons) >= 2)

    def test_q3_fuel_needed(self):
        ans = self._run_question("How much fuel might this ship need to reach its destination?")
        self.assertEqual(ans.problem_type, "FUEL_REQUIREMENT_ESTIMATE")
        self.assertGreater(ans.section_5_calculated_results.fuel_consumption_tonnes, 0.0)

    def test_q4_deadline_feasibility(self):
        ans = self._run_question("Can this ship reach the destination before the deadline?")
        self.assertEqual(ans.problem_type, "DEADLINE_FEASIBILITY")
        self.assertTrue(ans.section_5_calculated_results.deadline_feasible)

    def test_q5_vessel_selection(self):
        ans = self._run_question("Which available vessel should carry this shipment?")
        self.assertEqual(ans.problem_type, "VESSEL_SELECTION")

    def test_q6_reduce_costs_without_missing_deadline(self):
        ans = self._run_question("How can I reduce fuel costs without missing the delivery deadline?")
        self.assertEqual(ans.problem_type, "COST_EMISSION_TRADE_OFF")
        self.assertIn("Eco Corridor", ans.section_6_recommended_solution["title"])

    def test_q7_route_deviation(self):
        ans = self._run_question("What should I investigate if the ship deviates from its planned route?")
        self.assertEqual(ans.problem_type, "ROUTE_DEVIATION")

    def test_q8_fleet_assignment(self):
        ans = self._run_question("Which fleet assignment minimizes fuel consumption and estimated CO2 emissions?")
        self.assertEqual(ans.problem_type, "FLEET_ASSIGNMENT_OPTIMIZATION")

    def test_q9_weather_worsens(self):
        ans = self._run_question("What happens to the voyage if the weather worsens?")
        self.assertEqual(ans.problem_type, "WEATHER_IMPACT")

    def test_q10_carbon_budget(self):
        ans = self._run_question("Can this fleet operate within a specified carbon budget?")
        self.assertEqual(ans.problem_type, "CARBON_BUDGET_COMPLIANCE")


class TestSectionGFollowUps(unittest.TestCase):
    """Verifies that all interactive follow-up mutations produce valid Before/After comparisons."""

    def setUp(self):
        self.scenario = ScenarioInput(
            vessel=VesselInfo(max_cargo_capacity_tonnes=10000.0, current_cargo_weight_tonnes=8000.0),
            voyage=VoyageInfo(distance_nm=1580.0, planned_speed_knots=12.0),
            conditions=OperatingConditions(fuel_price_per_tonne=650.0),
            problem_statement="Baseline problem"
        )
        _, self.base_answer, _ = MaritimeAIEngine.solve_scenario(self.scenario)

    def test_followup_speed_increase(self):
        new_scen, desc = ScenarioEngine.apply_follow_up(self.scenario, "speed_plus")
        _, new_ans, _ = MaritimeAIEngine.solve_scenario(new_scen)
        comp = ScenarioEngine.compare_runs(self.base_answer, new_ans, desc)
        self.assertGreater(comp["delta_fuel"], 0)
        self.assertLess(comp["delta_hours"], 0)  # Shorter transit time

    def test_followup_fuel_price_rise(self):
        new_scen, desc = ScenarioEngine.apply_follow_up(self.scenario, "fuel_plus_10")
        _, new_ans, _ = MaritimeAIEngine.solve_scenario(new_scen)
        comp = ScenarioEngine.compare_runs(self.base_answer, new_ans, desc)
        self.assertGreater(comp["delta_cost"], 0)  # Costs rise

    def test_followup_weather_deterioration(self):
        new_scen, desc = ScenarioEngine.apply_follow_up(self.scenario, "weather_worsen")
        _, new_ans, _ = MaritimeAIEngine.solve_scenario(new_scen)
        comp = ScenarioEngine.compare_runs(self.base_answer, new_ans, desc)
        self.assertGreater(comp["delta_fuel"], 0)  # Adverse waves increase fuel burn


class TestSectionHInfeasibleScenarios(unittest.TestCase):
    """Verifies rejection of impossible or contradictory scenarios with clear error messages."""

    def test_impossible_speed_exceeds_physical_limits(self):
        scen = ScenarioInput(
            vessel=VesselInfo(),
            voyage=VoyageInfo(planned_speed_knots=45.0),  # Impossible for cargo ship
            conditions=OperatingConditions(),
            problem_statement="Test speed limit"
        )
        valid, answer, errors = MaritimeAIEngine.solve_scenario(scen)
        self.assertFalse(valid)
        self.assertIsNotNone(errors)
        self.assertTrue(any("design limits" in err for err in errors))

    def test_impossible_negative_distance(self):
        scen = ScenarioInput(
            vessel=VesselInfo(),
            voyage=VoyageInfo(distance_nm=-500.0),
            conditions=OperatingConditions(),
            problem_statement="Test negative distance"
        )
        valid, answer, errors = MaritimeAIEngine.solve_scenario(scen)
        self.assertFalse(valid)
        self.assertIsNotNone(errors)
        self.assertTrue(any("distance" in err.lower() for err in errors))


if __name__ == "__main__":
    unittest.main()
