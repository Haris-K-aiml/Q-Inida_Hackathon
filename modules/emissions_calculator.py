"""
QuantumGreen Fleet AI - Emissions and IMO CII Calculator
Calculates CO2 emissions according to IMO MEPC 281(70), carbon tax costs,
and Carbon Intensity Indicator (CII) ratings (A to E).
"""

from typing import Dict, Any, Tuple
from modules.data_models import VesselInfo, FuelType


class EmissionsCalculator:
    """Standard maritime emissions and decarbonization calculation engine."""

    # IMO MEPC 281(70) Carbon Conversion Factors (C_F) in tonnes CO2 / tonne fuel
    IMO_CARBON_FACTORS = {
        FuelType.VLSFO.value: 3.151,
        FuelType.HFO.value: 3.114,
        FuelType.MGO.value: 3.206,
        FuelType.LNG.value: 2.750,
        FuelType.METHANOL.value: 1.375,
        FuelType.BIOFUEL.value: 2.205
    }

    # Reference parameters for IMO CII calculation (MEPC.337(76))
    # a and c coefficients for reference line: CII_ref = a * (DWT)^(-c)
    CII_REFERENCE_COEFFICIENTS = {
        "Cargo Vessel (General)": {"a": 3405.0, "c": 0.352, "d1": 0.83, "d2": 0.94, "d3": 1.06, "d4": 1.19},
        "Container Ship": {"a": 1984.0, "c": 0.489, "d1": 0.82, "d2": 0.93, "d3": 1.08, "d4": 1.19},
        "Bulk Carrier": {"a": 4745.0, "c": 0.322, "d1": 0.86, "d2": 0.94, "d3": 1.06, "d4": 1.18},
        "Oil / Chemical Tanker": {"a": 5247.0, "c": 0.357, "d1": 0.82, "d2": 0.93, "d3": 1.08, "d4": 1.20},
        "LNG Carrier": {"a": 9827.0, "c": 0.400, "d1": 0.89, "d2": 0.95, "d3": 1.06, "d4": 1.13},
        "Ro-Ro Cargo": {"a": 5762.0, "c": 0.381, "d1": 0.78, "d2": 0.92, "d3": 1.10, "d4": 1.25},
        "Feeder Vessel": {"a": 2500.0, "c": 0.450, "d1": 0.83, "d2": 0.94, "d3": 1.06, "d4": 1.19}
    }

    @classmethod
    def get_carbon_factor(cls, fuel_type: str) -> float:
        """Returns IMO carbon conversion factor C_F."""
        return cls.IMO_CARBON_FACTORS.get(fuel_type, 3.151)

    @classmethod
    def calculate_co2(cls, fuel_tonnes: float, fuel_type: str) -> float:
        """Calculates total metric tonnes of CO2 emitted."""
        cf = cls.get_carbon_factor(fuel_type)
        return fuel_tonnes * cf

    @classmethod
    def calculate_carbon_tax(cls, co2_tonnes: float, tax_per_tonne_usd: float = 60.0) -> float:
        """Calculates carbon tax or EU ETS / IMO compliance cost."""
        return co2_tonnes * max(0.0, tax_per_tonne_usd)

    @classmethod
    def calculate_cii(
        cls,
        vessel: VesselInfo,
        co2_tonnes: float,
        distance_nm: float
    ) -> Tuple[str, float, float, str]:
        """
        Calculates IMO Carbon Intensity Indicator (CII).
        Returns:
            (rating, attained_cii, required_cii, description)
        """
        dwt = vessel.dwt_tonnes if vessel.dwt_tonnes and vessel.dwt_tonnes > 0 else (vessel.max_cargo_capacity_tonnes * 1.2)
        dist = max(1.0, distance_nm)
        
        # Attained CII in g CO2 / (dwt * nautical mile)
        attained_cii = (co2_tonnes * 1e6) / (dwt * dist)
        
        coeffs = cls.CII_REFERENCE_COEFFICIENTS.get(
            vessel.vessel_type,
            cls.CII_REFERENCE_COEFFICIENTS["Cargo Vessel (General)"]
        )
        
        # Reference CII line
        required_cii = coeffs["a"] * (dwt ** (-coeffs["c"]))
        ratio = attained_cii / max(0.001, required_cii)
        
        # Determine rating A to E
        if ratio <= coeffs["d1"]:
            rating = "A"
            desc = "Rating A (Major Superior) - Exceptionally energy-efficient voyage"
        elif ratio <= coeffs["d2"]:
            rating = "B"
            desc = "Rating B (Minor Superior) - Well within IMO decarbonization benchmarks"
        elif ratio <= coeffs["d3"]:
            rating = "C"
            desc = "Rating C (Moderate) - Fully compliant with baseline IMO requirements"
        elif ratio <= coeffs["d4"]:
            rating = "D"
            desc = "Rating D (Inferior) - High emissions; repeated D rating requires corrective plan"
        else:
            rating = "E"
            desc = "Rating E (Major Inferior) - Fails IMO CII threshold; requires speed reduction or routing adjustment"
            
        return rating, attained_cii, required_cii, desc

    @classmethod
    def evaluate_carbon_budget(
        cls,
        co2_tonnes: float,
        budget_tonnes: float
    ) -> Dict[str, Any]:
        """Checks if voyage CO2 emissions remain within specified carbon cap."""
        exceeded = co2_tonnes > budget_tonnes
        variance = co2_tonnes - budget_tonnes
        variance_pct = (variance / budget_tonnes * 100.0) if budget_tonnes > 0 else 0.0
        
        return {
            "budget_tonnes": budget_tonnes,
            "actual_co2_tonnes": co2_tonnes,
            "within_budget": not exceeded,
            "variance_tonnes": variance,
            "variance_pct": variance_pct,
            "compliance_status": "COMPLIANT" if not exceeded else "OVER_BUDGET"
        }
