"""
QuantumGreen Fleet AI - Interactive Follow-up and Scenario Engine
Preserves verified scenario parameters, mutates designated operational variables,
reruns backend calculations, and produces detailed Before-and-After comparative deltas.
"""

import copy
from typing import Dict, Any, Tuple, Optional, List
from modules.data_models import ScenarioInput, StructuredAIAnswer
from modules.ai_engine import MaritimeAIEngine
from modules.ais_service import AISService


class ScenarioEngine:
    """Manages iterative scenario follow-ups and sensitivity evaluations."""

    SUPPORTED_FOLLOW_UPS = [
        {"id": "speed_plus", "label": "⚡ What if I increase the ship speed (+1.5 kn)?", "param": "speed"},
        {"id": "fuel_plus_10", "label": "📈 What if fuel prices rise by 10%?", "param": "fuel_price"},
        {"id": "cargo_plus_15", "label": "📦 What if cargo weight increases by 15%?", "param": "cargo"},
        {"id": "cost_vs_emission", "label": "⚖️ Compare lowest-cost vs lowest-emission route", "param": "comparison"},
        {"id": "another_vessel", "label": "🚢 Can another vessel complete this shipment faster?", "param": "vessel"},
        {"id": "weather_worsen", "label": "🌊 What happens to the voyage if weather worsens?", "param": "weather"},
        {"id": "carbon_cap", "label": "🌱 How can I stay within my carbon budget?", "param": "carbon"}
    ]

    @classmethod
    def apply_follow_up(
        cls,
        base_scenario: ScenarioInput,
        follow_up_action: str
    ) -> Tuple[ScenarioInput, str]:
        """
        Clones base scenario and mutates specified parameter.
        Returns:
            (new_scenario, change_description)
        """
        new_scenario = copy.deepcopy(base_scenario)
        action = follow_up_action.lower().strip()
        change_desc = ""

        if "increase" in action and "speed" in action or action == "speed_plus":
            old_speed = new_scenario.voyage.planned_speed_knots
            new_speed = min(new_scenario.conditions.speed_max_knots, old_speed + 1.5)
            new_scenario.voyage.planned_speed_knots = new_speed
            new_scenario.problem_statement = "Follow-up: Evaluated impact of increasing ship speed by +1.5 knots."
            change_desc = f"Planned speed increased from {old_speed:.1f} knots to {new_speed:.1f} knots (+1.5 kn)."

        elif "fuel price" in action or "10%" in action or action == "fuel_plus_10":
            old_price = new_scenario.conditions.fuel_price_per_tonne
            new_price = round(old_price * 1.10, 2)
            new_scenario.conditions.fuel_price_per_tonne = new_price
            new_scenario.problem_statement = "Follow-up: Evaluated sensitivity to a 10% fuel price escalation."
            change_desc = f"Fuel price increased by 10% from ${old_price:.2f}/t to ${new_price:.2f}/tonne."

        elif "cargo" in action or action == "cargo_plus_15":
            old_cargo = new_scenario.vessel.current_cargo_weight_tonnes
            new_cargo = min(new_scenario.vessel.max_cargo_capacity_tonnes, old_cargo * 1.15)
            new_scenario.vessel.current_cargo_weight_tonnes = new_cargo
            new_scenario.problem_statement = "Follow-up: Evaluated impact of a 15% cargo weight surge."
            change_desc = f"Cargo weight increased from {old_cargo:,.0f} tonnes to {new_cargo:,.0f} tonnes (+15%)."

        elif "weather" in action or action == "weather_worsen":
            old_wave = new_scenario.conditions.wave_height_m or 1.8
            old_wind = new_scenario.conditions.wind_speed_knots or 15.0
            new_wave = old_wave + 1.5
            new_wind = old_wind + 12.0
            new_scenario.conditions.wave_height_m = new_wave
            new_scenario.conditions.wind_speed_knots = new_wind
            new_scenario.conditions.weather_condition = "Rough Sea (Beaufort 6, Hs 3.3m, 27 kn)"
            new_scenario.problem_statement = "Follow-up: Assessed consequence of weather worsening to Rough Sea."
            change_desc = f"Weather conditions worsened: Wave height increased to {new_wave:.1f}m, wind to {new_wind:.0f} kn."

        elif "another vessel" in action or action == "another_vessel":
            # Swap to a faster modern container vessel from registry
            alt_vessel_dict = AISService.lookup_vessel("MV Chennai Express") or AISService.lookup_vessel("MV Eco Carrier")
            old_name = new_scenario.vessel.name
            if alt_vessel_dict:
                AISService.populate_vessel_info_from_registry(new_scenario.vessel, alt_vessel_dict)
                new_scenario.voyage.planned_speed_knots = 14.5  # Faster transit speed
            change_desc = f"Swapped vessel from '{old_name}' to '{new_scenario.vessel.name}' ({new_scenario.vessel.vessel_type}) at 14.5 knots."
            new_scenario.problem_statement = f"Follow-up: Testing performance of alternative vessel {new_scenario.vessel.name}."

        elif "carbon budget" in action or "stay within" in action or action == "carbon_cap":
            # Calculate speed needed to save ~20% fuel/CO2
            old_speed = new_scenario.voyage.planned_speed_knots
            new_speed = max(new_scenario.conditions.speed_min_knots, old_speed - 1.8)
            new_scenario.voyage.planned_speed_knots = new_speed
            new_scenario.conditions.carbon_emission_budget_tonnes = 180.0
            change_desc = f"Applied slow steaming ({new_speed:.1f} kn) and set carbon cap to 180 t CO2."
            new_scenario.problem_statement = "Follow-up: Investigating speed reduction to strictly comply with carbon budget."

        else:
            # Generic follow-up
            new_scenario.problem_statement = f"Follow-up Query: {follow_up_action}"
            change_desc = f"Custom scenario follow-up: '{follow_up_action}'."

        return new_scenario, change_desc

    @classmethod
    def compare_runs(
        cls,
        before_answer: StructuredAIAnswer,
        after_answer: StructuredAIAnswer,
        change_desc: str
    ) -> Dict[str, Any]:
        """
        Constructs a structured side-by-side comparison table and delta analysis.
        """
        b_m = before_answer.section_5_calculated_results
        a_m = after_answer.section_5_calculated_results

        delta_fuel = a_m.fuel_consumption_tonnes - b_m.fuel_consumption_tonnes
        delta_fuel_pct = (delta_fuel / b_m.fuel_consumption_tonnes * 100.0) if b_m.fuel_consumption_tonnes > 0 else 0.0

        delta_co2 = a_m.co2_emissions_tonnes - b_m.co2_emissions_tonnes
        delta_co2_pct = (delta_co2 / b_m.co2_emissions_tonnes * 100.0) if b_m.co2_emissions_tonnes > 0 else 0.0

        delta_cost = a_m.total_cost_usd - b_m.total_cost_usd
        delta_hours = a_m.voyage_duration_hours - b_m.voyage_duration_hours

        return {
            "change_description": change_desc,
            "table": [
                {
                    "Metric": "Voyage Fuel (tonnes)",
                    "Before": round(b_m.fuel_consumption_tonnes, 2),
                    "After": round(a_m.fuel_consumption_tonnes, 2),
                    "Delta": f"{'+' if delta_fuel > 0 else ''}{delta_fuel:.2f} t ({delta_fuel_pct:+.1f}%)"
                },
                {
                    "Metric": "CO2 Emissions (tonnes)",
                    "Before": round(b_m.co2_emissions_tonnes, 2),
                    "After": round(a_m.co2_emissions_tonnes, 2),
                    "Delta": f"{'+' if delta_co2 > 0 else ''}{delta_co2:.2f} t ({delta_co2_pct:+.1f}%)"
                },
                {
                    "Metric": "Total Cost (USD)",
                    "Before": f"${b_m.total_cost_usd:,.2f}",
                    "After": f"${a_m.total_cost_usd:,.2f}",
                    "Delta": f"{'+' if delta_cost > 0 else ''}${delta_cost:,.2f}"
                },
                {
                    "Metric": "Voyage Duration (hours / days)",
                    "Before": f"{b_m.voyage_duration_hours:.1f} h ({b_m.voyage_duration_days:.1f} d)",
                    "After": f"{a_m.voyage_duration_hours:.1f} h ({a_m.voyage_duration_days:.1f} d)",
                    "Delta": f"{'+' if delta_hours > 0 else ''}{delta_hours:.1f} hours"
                },
                {
                    "Metric": "IMO CII Rating",
                    "Before": b_m.cii_rating,
                    "After": a_m.cii_rating,
                    "Delta": "Maintained" if b_m.cii_rating == a_m.cii_rating else f"{b_m.cii_rating} -> {a_m.cii_rating}"
                },
                {
                    "Metric": "Schedule Feasibility",
                    "Before": "Feasible" if b_m.deadline_feasible else "Infeasible",
                    "After": "Feasible" if a_m.deadline_feasible else "Infeasible",
                    "Delta": "Consistent" if b_m.deadline_feasible == a_m.deadline_feasible else "Status Changed"
                }
            ],
            "delta_fuel": delta_fuel,
            "delta_co2": delta_co2,
            "delta_cost": delta_cost,
            "delta_hours": delta_hours
        }
