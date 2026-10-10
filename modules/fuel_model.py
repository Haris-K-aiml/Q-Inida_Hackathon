"""
QuantumGreen Fleet AI - Maritime Hydrodynamic Fuel Model
Naval architecture propulsion power model based on the Admiralty coefficient,
Kwon weather added resistance, hull displacement loading, and engine SFOC.
"""

import math
from typing import Dict, Any, List, Tuple, Optional
from modules.data_models import VesselInfo


class MaritimeFuelModel:
    """Calibrated hydrodynamic and empirical fuel consumption engine."""

    # Reference Admiralty coefficients for merchant hull types
    ADMIRALTY_COEFFICIENTS = {
        "Cargo Vessel (General)": 520.0,
        "Container Ship": 580.0,
        "Bulk Carrier": 540.0,
        "Oil / Chemical Tanker": 530.0,
        "LNG Carrier": 600.0,
        "Ro-Ro Cargo": 500.0,
        "Feeder Vessel": 460.0
    }

    # Reference SFOC (grams per kilowatt-hour)
    DEFAULT_SFOC = {
        "Very Low Sulfur Fuel Oil (VLSFO)": 175.0,
        "Heavy Fuel Oil (HFO)": 180.0,
        "Marine Gas Oil (MGO)": 170.0,
        "Liquefied Natural Gas (LNG)": 150.0,
        "Green Methanol": 320.0,  # Lower energy density requires higher mass flow
        "Bio-Bunkers (B30)": 185.0
    }

    # Auxiliary engine consumption (tonnes/day)
    DEFAULT_AUX_CONSUMPTION = {
        "Container Ship": 3.0,
        "Reefer / Ro-Ro": 3.8,
        "Bulk Carrier": 1.5,
        "Oil / Chemical Tanker": 2.2,
        "Cargo Vessel (General)": 1.6,
        "LNG Carrier": 4.0,
        "Feeder Vessel": 1.2
    }

    @classmethod
    def estimate_displacement(cls, vessel: VesselInfo) -> float:
        """
        Calculates vessel displacement (delta) in metric tonnes.
        Displacement = Lightweight + Deadweight (Cargo + Bunkers + Ballast).
        """
        max_cap = max(100.0, vessel.max_cargo_capacity_tonnes)
        current_cargo = min(max_cap, max(0.0, vessel.current_cargo_weight_tonnes))
        
        # Deadweight Tonnage baseline
        dwt = vessel.dwt_tonnes if vessel.dwt_tonnes and vessel.dwt_tonnes > 0 else (max_cap * 1.2)
        
        # Lightweight (empty ship structure) is typically ~25-30% of DWT
        lightweight = dwt * 0.28
        
        # Ballast / consumables allowance
        consumables = min(500.0, max_cap * 0.05)
        
        displacement = lightweight + current_cargo + consumables
        return max(500.0, displacement)

    @classmethod
    def calculate_propulsion_power(
        cls,
        vessel: VesselInfo,
        speed_knots: float,
        weather_factor: float = 1.0,
        fouling_factor: float = 1.0
    ) -> float:
        """
        Calculates main engine shaft power (kW) using the Admiralty formula:
        Power (kW) = (Displacement^(2/3) * Speed^3) / C_adm * weather_factor * fouling_factor
        """
        displacement = cls.estimate_displacement(vessel)
        c_adm = cls.ADMIRALTY_COEFFICIENTS.get(vessel.vessel_type, 520.0)
        
        # Safe positive speed
        v_knots = max(1.0, speed_knots)
        
        # Admiralty power in metric horsepower (HP), converted to kW (1 HP = 0.7355 kW)
        power_hp = (math.pow(displacement, 2.0 / 3.0) * math.pow(v_knots, 3.0)) / c_adm
        power_kw = power_hp * 0.7355 * weather_factor * fouling_factor
        
        # If user specified rated engine power, cap at 105% MCR (Maximum Continuous Rating)
        if vessel.engine_power_kw and vessel.engine_power_kw > 0:
            mcr_cap = vessel.engine_power_kw * 1.05
            power_kw = min(power_kw, mcr_cap)
            
        return max(50.0, power_kw)

    @classmethod
    def calculate_fuel_rate_hourly(
        cls,
        vessel: VesselInfo,
        speed_knots: float,
        weather_factor: float = 1.0,
        fouling_factor: float = 1.0
    ) -> Tuple[float, float, float]:
        """
        Returns:
            (total_tonnes_per_hour, main_engine_tonnes_per_hour, aux_engine_tonnes_per_hour)
        """
        power_kw = cls.calculate_propulsion_power(vessel, speed_knots, weather_factor, fouling_factor)
        
        # Specific Fuel Oil Consumption
        sfoc = vessel.sfoc_g_per_kwh or cls.DEFAULT_SFOC.get(vessel.fuel_type, 175.0)
        
        # Main engine fuel burn: Power * SFOC * 1e-6 (t/hr)
        me_t_per_hr = power_kw * sfoc * 1e-6
        
        # Auxiliary engine fuel burn
        aux_daily = cls.DEFAULT_AUX_CONSUMPTION.get(vessel.vessel_type, 1.6)
        aux_t_per_hr = aux_daily / 24.0
        
        total_t_per_hr = me_t_per_hr + aux_t_per_hr
        return total_t_per_hr, me_t_per_hr, aux_t_per_hr

    @classmethod
    def calculate_voyage_fuel(
        cls,
        vessel: VesselInfo,
        distance_nm: float,
        speed_knots: float,
        weather_factor: float = 1.0,
        fouling_factor: float = 1.0
    ) -> Dict[str, Any]:
        """
        Calculates total fuel consumption for a given voyage segment or route.
        """
        safe_speed = max(3.0, speed_knots)
        duration_hours = distance_nm / safe_speed
        duration_days = duration_hours / 24.0
        
        rate_hr, me_hr, aux_hr = cls.calculate_fuel_rate_hourly(
            vessel, safe_speed, weather_factor, fouling_factor
        )
        
        total_fuel_tonnes = rate_hr * duration_hours
        me_fuel_tonnes = me_hr * duration_hours
        aux_fuel_tonnes = aux_hr * duration_hours
        
        daily_fuel_burn = rate_hr * 24.0
        power_kw = cls.calculate_propulsion_power(vessel, safe_speed, weather_factor, fouling_factor)
        
        return {
            "total_fuel_tonnes": total_fuel_tonnes,
            "main_engine_fuel_tonnes": me_fuel_tonnes,
            "aux_engine_fuel_tonnes": aux_fuel_tonnes,
            "hourly_fuel_rate_tonnes": rate_hr,
            "daily_fuel_rate_tonnes": daily_fuel_burn,
            "propulsion_power_kw": power_kw,
            "duration_hours": duration_hours,
            "duration_days": duration_days,
            "weather_penalty_factor": weather_factor,
            "fouling_factor": fouling_factor
        }

    @classmethod
    def generate_speed_consumption_curve(
        cls,
        vessel: VesselInfo,
        distance_nm: float,
        weather_factor: float = 1.0,
        fouling_factor: float = 1.0,
        min_speed: float = 9.0,
        max_speed: float = 18.0,
        steps: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Generates speed vs fuel consumption points for graphical analysis.
        Demonstrates the cubic relationship between speed and fuel consumption.
        """
        curve = []
        step_size = (max_speed - min_speed) / max(1, steps - 1)
        
        for i in range(steps):
            spd = min_speed + i * step_size
            res = cls.calculate_voyage_fuel(
                vessel, distance_nm, spd, weather_factor, fouling_factor
            )
            curve.append({
                "Speed (knots)": round(spd, 1),
                "Voyage Fuel (tonnes)": round(res["total_fuel_tonnes"], 2),
                "Daily Fuel (tonnes/day)": round(res["daily_fuel_rate_tonnes"], 2),
                "Duration (days)": round(res["duration_days"], 2),
                "Power (kW)": round(res["propulsion_power_kw"], 0)
            })
        return curve
