"""
QuantumGreen Fleet AI - Validation Module
Rigorous maritime input validation, unit conversions, contradiction detection,
and data provenance tracking.
"""

import re
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
from modules.data_models import (
    VesselInfo, VoyageInfo, OperatingConditions, ScenarioInput, DataProvenance
)


def validate_imo(imo_str: Optional[str]) -> Tuple[bool, str]:
    """
    Validates an IMO number (7 digits, last digit is checksum).
    Formula: sum(d_i * (8 - i) for i in 1..6) % 10 == d_7
    """
    if not imo_str:
        return True, ""  # Optional field
    
    clean = re.sub(r"[^\d]", "", str(imo_str))
    if len(clean) != 7:
        return False, f"IMO number must be exactly 7 digits (got '{imo_str}')."
    
    digits = [int(c) for c in clean]
    checksum = sum(digits[i] * (7 - i) for i in range(6)) % 10
    if checksum != digits[6]:
        return False, (
            f"IMO checksum validation failed for '{clean}'. "
            f"Calculated check digit is {checksum}, but provided {digits[6]}."
        )
    return True, ""


def validate_mmsi(mmsi_str: Optional[str]) -> Tuple[bool, str]:
    """Validates an MMSI number (exactly 9 digits)."""
    if not mmsi_str:
        return True, ""
    clean = re.sub(r"[^\d]", "", str(mmsi_str))
    if len(clean) != 9:
        return False, f"MMSI must be exactly 9 digits (got '{mmsi_str}')."
    return True, ""


def convert_distance(val: float, from_unit: str, to_unit: str = "NM") -> float:
    """Converts distance between Nautical Miles (NM) and Kilometers (km)."""
    if from_unit.upper() == to_unit.upper():
        return val
    if from_unit.upper() == "KM" and to_unit.upper() == "NM":
        return val / 1.852
    if from_unit.upper() == "NM" and to_unit.upper() == "KM":
        return val * 1.852
    return val


def convert_speed(val: float, from_unit: str, to_unit: str = "knots") -> float:
    """Converts speed between knots and km/h."""
    if from_unit.lower() == to_unit.lower():
        return val
    if from_unit.lower() in ("km/h", "kmh") and to_unit.lower() == "knots":
        return val / 1.852
    if from_unit.lower() == "knots" and to_unit.lower() in ("km/h", "kmh"):
        return val * 1.852
    return val


class MaritimeValidator:
    """Comprehensive validator checking physical bounds and operational consistency."""

    @staticmethod
    def validate_scenario(scenario: ScenarioInput) -> Tuple[bool, List[str], List[str]]:
        """
        Validates the scenario.
        Returns:
            (is_valid, error_messages, warning_messages)
        """
        errors: List[str] = []
        warnings: List[str] = []
        
        v = scenario.vessel
        voy = scenario.voyage
        c = scenario.conditions

        # 1. Vessel Validation
        if not v.name or not v.name.strip():
            warnings.append("Ship name was not specified; defaulting to 'MV Ocean Pioneer'.")

        if v.imo:
            valid_imo, msg = validate_imo(v.imo)
            if not valid_imo:
                errors.append(f"Vessel Specification Error: {msg}")

        if v.mmsi:
            valid_mmsi, msg = validate_mmsi(v.mmsi)
            if not valid_mmsi:
                errors.append(f"Vessel AIS Error: {msg}")

        if v.max_cargo_capacity_tonnes <= 0:
            errors.append("Vessel Capacity Error: Maximum cargo capacity must be greater than 0 tonnes.")

        if v.current_cargo_weight_tonnes < 0:
            errors.append("Cargo Load Error: Current cargo weight cannot be negative.")

        if v.current_cargo_weight_tonnes > v.max_cargo_capacity_tonnes:
            errors.append(
                f"Contradictory Cargo Input: Current cargo ({v.current_cargo_weight_tonnes:,.0f} t) "
                f"exceeds vessel maximum cargo capacity ({v.max_cargo_capacity_tonnes:,.0f} t)."
            )

        if v.current_fuel_tonnes is not None and v.current_fuel_tonnes < 0:
            errors.append("Fuel Level Error: Current fuel quantity cannot be negative.")

        if v.length_m is not None and v.length_m <= 0:
            errors.append("Vessel Dimension Error: Vessel length must be positive.")

        if v.draft_m is not None and v.draft_m <= 0:
            errors.append("Vessel Dimension Error: Vessel draft must be positive.")

        # Draft vs limit check
        if v.draft_m is not None and c.max_draft_limit_m is not None:
            if v.draft_m > c.max_draft_limit_m:
                errors.append(
                    f"Operational Constraint Violation: Vessel draft ({v.draft_m:.1f} m) "
                    f"exceeds fairway/port draft constraint ({c.max_draft_limit_m:.1f} m)."
                )

        # 2. Voyage Validation
        if not voy.departure_port or not voy.departure_port.strip():
            errors.append("Voyage Routing Error: Departure port cannot be empty.")

        if not voy.destination_port or not voy.destination_port.strip():
            errors.append("Voyage Routing Error: Destination port cannot be empty.")

        if voy.departure_port.strip().lower() == voy.destination_port.strip().lower():
            errors.append("Voyage Routing Error: Departure port and destination port cannot be identical.")

        if voy.distance_nm <= 0:
            errors.append("Voyage Distance Error: Voyage sailing distance must be greater than 0.")

        if voy.planned_speed_knots <= 0:
            errors.append("Voyage Speed Error: Planned speed must be greater than 0 knots.")
        elif voy.planned_speed_knots > 32.0:
            errors.append(
                f"Physical Feasibility Error: Planned speed {voy.planned_speed_knots:.1f} knots "
                "exceeds standard commercial maritime design limits (> 32 knots)."
            )
        elif voy.planned_speed_knots < 5.0:
            warnings.append(
                f"Warning: Planned speed {voy.planned_speed_knots:.1f} knots is below steerage threshold (< 5 knots)."
            )

        # Speed bounds check
        if c.speed_min_knots >= c.speed_max_knots:
            errors.append(
                f"Constraint Error: Minimum speed limit ({c.speed_min_knots:.1f} kn) "
                f"must be strictly less than maximum speed limit ({c.speed_max_knots:.1f} kn)."
            )

        if voy.planned_speed_knots < c.speed_min_knots:
            warnings.append(
                f"Planned speed ({voy.planned_speed_knots:.1f} kn) is below the minimum operational constraint ({c.speed_min_knots:.1f} kn)."
            )
        elif voy.planned_speed_knots > c.speed_max_knots:
            errors.append(
                f"Operational Constraint Violation: Planned speed ({voy.planned_speed_knots:.1f} kn) "
                f"exceeds maximum allowed engine speed limit ({c.speed_max_knots:.1f} kn)."
            )

        # Coordinate check if given
        if voy.current_lat is not None and not (-90.0 <= voy.current_lat <= 90.0):
            errors.append(f"AIS Position Error: Latitude must be between -90 and +90 (got {voy.current_lat}).")
        if voy.current_lon is not None and not (-180.0 <= voy.current_lon <= 180.0):
            errors.append(f"AIS Position Error: Longitude must be between -180 and +180 (got {voy.current_lon}).")

        # Time constraints check
        if voy.departure_time and voy.delivery_deadline:
            if voy.departure_time >= voy.delivery_deadline:
                errors.append(
                    f"Contradictory Schedule: Departure time ({voy.departure_time.strftime('%Y-%m-%d %H:%M')}) "
                    f"is equal to or after delivery deadline ({voy.delivery_deadline.strftime('%Y-%m-%d %H:%M')})."
                )

        if voy.departure_time and voy.expected_arrival_time:
            if voy.departure_time >= voy.expected_arrival_time:
                errors.append(
                    f"Contradictory Schedule: Departure time is after expected arrival time."
                )

        # 3. Operating Conditions Validation
        if c.fuel_price_per_tonne < 0:
            errors.append("Financial Input Error: Fuel price cannot be negative.")

        if c.wind_speed_knots is not None and c.wind_speed_knots < 0:
            errors.append("Environmental Input Error: Wind speed cannot be negative.")

        if c.wave_height_m is not None and c.wave_height_m < 0:
            errors.append("Environmental Input Error: Significant wave height cannot be negative.")

        if c.carbon_emission_budget_tonnes is not None and c.carbon_emission_budget_tonnes < 0:
            errors.append("Environmental Input Error: Carbon budget cannot be negative.")

        # 4. Problem Statement Check
        if not scenario.problem_statement or not scenario.problem_statement.strip():
            errors.append("Problem Statement Error: Please describe your ship or fleet problem.")

        is_valid = len(errors) == 0
        return is_valid, errors, warnings

    @staticmethod
    def identify_missing_information(scenario: ScenarioInput) -> Dict[str, Any]:
        """
        Classifies fields into Critical Missing, Optional Missing (using verified defaults),
        and Available fields with provenance attribution.
        """
        v = scenario.vessel
        voy = scenario.voyage
        c = scenario.conditions

        missing_critical: List[str] = []
        missing_optional_using_benchmark: List[Dict[str, str]] = []
        provenance_breakdown: List[Dict[str, str]] = []

        # Check vessel
        if v.current_fuel_tonnes is None:
            missing_optional_using_benchmark.append({
                "field": "Current Fuel Level / Remaining Fuel",
                "impact": "Cannot verify bunker reserve margin at destination without fuel tank level.",
                "action": "Assuming adequate bunker capacity based on standard Handysize tank capacity (500 t)."
            })
        if v.sfoc_g_per_kwh is None and v.base_fuel_rate_tonnes_per_day is None:
            missing_optional_using_benchmark.append({
                "field": "Engine SFOC or Fuel Rate",
                "impact": "Engine thermal efficiency is uncalibrated.",
                "action": "Using standard IMO Two-Stroke Diesel SFOC benchmark (175.0 g/kWh)."
            })
        if v.length_m is None or v.draft_m is None:
            missing_optional_using_benchmark.append({
                "field": "Vessel Dimensions (Length/Draft)",
                "impact": "Hydrodynamic wetted surface area is estimated from Deadweight Tonnage.",
                "action": "Calibrating displacement using vessel type standard block coefficient (Cb = 0.78)."
            })

        # Check voyage
        if voy.delivery_deadline is None:
            missing_optional_using_benchmark.append({
                "field": "Delivery Deadline",
                "impact": "Cannot strictly check contract demurrage or delivery feasibility.",
                "action": "Evaluating fuel-optimized speed profile without strict calendar constraint."
            })
        if voy.current_lat is None or voy.current_lon is None:
            missing_optional_using_benchmark.append({
                "field": "Live AIS Coordinates (Lat/Lon)",
                "impact": "Live GPS telemetry not provided.",
                "action": "Routing from port waypoint origin."
            })

        # Check conditions
        if c.wind_speed_knots is None or c.wave_height_m is None:
            missing_optional_using_benchmark.append({
                "field": "Real-time Wave & Wind Telemetry",
                "impact": "Weather resistance penalty computed from descriptive sea state rather than buoy sensor.",
                "action": "Using Beaufort Scale 4 climatological average (Hs = 1.8m, Vw = 15 kn)."
            })
        if c.carbon_emission_budget_tonnes is None:
            missing_optional_using_benchmark.append({
                "field": "Carbon Emission Budget",
                "impact": "CO2 cap is unconstrained.",
                "action": "Calculating IMO MEPC baseline CII and carbon tax impact without a hard threshold."
            })

        # Categorize provenance
        def tag(cat: str, name: str, val: Any, prov: DataProvenance):
            provenance_breakdown.append({
                "category": cat,
                "parameter": name,
                "value": str(val) if val is not None else "Blank / Unspecified",
                "provenance": prov.value
            })

        tag("Vessel", "Ship Name", v.name, v.get_provenance("name"))
        tag("Vessel", "IMO / MMSI", f"IMO: {v.imo or 'N/A'}, MMSI: {v.mmsi or 'N/A'}", v.get_provenance("imo"))
        tag("Vessel", "Vessel Type", v.vessel_type, v.get_provenance("vessel_type"))
        tag("Vessel", "Max Cargo Capacity", f"{v.max_cargo_capacity_tonnes:,.0f} tonnes", v.get_provenance("max_cargo_capacity_tonnes"))
        tag("Vessel", "Current Cargo Weight", f"{v.current_cargo_weight_tonnes:,.0f} tonnes", v.get_provenance("current_cargo_weight_tonnes"))
        tag("Vessel", "Fuel Type", v.fuel_type, v.get_provenance("fuel_type"))
        tag("Vessel", "Current Fuel Reserve", f"{v.current_fuel_tonnes or 'Unknown'} tonnes", v.get_provenance("current_fuel_tonnes"))
        tag("Voyage", "Departure Port", voy.departure_port, voy.get_provenance("departure_port"))
        tag("Voyage", "Destination Port", voy.destination_port, voy.get_provenance("destination_port"))
        tag("Voyage", "Planned Route", voy.planned_route, voy.get_provenance("planned_route"))
        tag("Voyage", "Planned Speed", f"{voy.planned_speed_knots:.1f} knots", voy.get_provenance("planned_speed_knots"))
        tag("Voyage", "Voyage Distance", f"{voy.distance_nm:,.0f} NM", voy.get_provenance("distance_nm"))
        tag("Conditions", "Weather Sea State", c.weather_condition, c.get_provenance("weather_condition"))
        tag("Conditions", "Fuel Price", f"${c.fuel_price_per_tonne:.2f} / tonne", c.get_provenance("fuel_price_per_tonne"))

        return {
            "missing_critical": missing_critical,
            "missing_optional": missing_optional_using_benchmark,
            "provenance_breakdown": provenance_breakdown
        }
