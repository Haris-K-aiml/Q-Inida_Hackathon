"""
QuantumGreen Fleet AI - Weather and Environmental Conditions Service
Calculates hydrodynamic wave resistance penalties based on Kwon's formula
and ISO 15016 standard maritime added resistance factors.
"""

from typing import Dict, Any, Tuple


class WeatherService:
    """Environmental condition modeling and weather penalty engine."""

    # Standard Beaufort scale mappings
    BEAUFORT_TABLE = {
        "Calm (BF 0-2)": {"hs_m": 0.3, "wind_kn": 5.0, "factor": 1.00, "desc": "Mirror smooth to rippled sea."},
        "Slight Sea (BF 3)": {"hs_m": 0.9, "wind_kn": 10.0, "factor": 1.03, "desc": "Small wavelets; crests do not break."},
        "Moderate Sea (BF 4)": {"hs_m": 1.8, "wind_kn": 15.0, "factor": 1.07, "desc": "Small waves becoming longer; fairly frequent white horses."},
        "Moderate-Rough (BF 5)": {"hs_m": 2.5, "wind_kn": 20.0, "factor": 1.14, "desc": "Moderate waves taking pronounced long form; many white horses."},
        "Rough Sea (BF 6)": {"hs_m": 3.5, "wind_kn": 25.0, "factor": 1.24, "desc": "Large waves begin to form; extensive white foam crests."},
        "High / Storm Sea (BF 8)": {"hs_m": 5.5, "wind_kn": 38.0, "factor": 1.50, "desc": "Moderately high waves of greater length; foam blown in dense streaks."}
    }

    @classmethod
    def calculate_weather_factor(
        cls,
        wave_height_m: float = 1.8,
        wind_speed_knots: float = 15.0,
        relative_angle_deg: float = 180.0  # 180 = head sea, 0 = following sea
    ) -> Tuple[float, float, str]:
        """
        Calculates weather added power multiplier using Kwon's empirical formulation:
        f_weather = 1.0 + (wave_factor * angle_factor) + (wind_factor * angle_factor)
        
        Returns:
            (weather_multiplier, penalty_percentage, description)
        """
        hs = max(0.0, wave_height_m)
        v_w = max(0.0, wind_speed_knots)
        
        # Directional impact factor (head sea has maximum resistance, following sea assists)
        # 180 deg (head sea) -> 1.0, 90 deg (beam sea) -> 0.65, 0 deg (following) -> 0.15
        import math
        angle_rad = math.radians(relative_angle_deg)
        dir_factor = 0.5 * (1.0 - math.cos(angle_rad))  # 0 at 0 deg, 1 at 180 deg
        dir_factor = max(0.2, dir_factor)
        
        # Added wave resistance factor
        delta_wave = 0.038 * (hs ** 1.35) * dir_factor
        
        # Added aerodynamic wind resistance factor
        delta_wind = 0.0016 * v_w * dir_factor
        
        total_factor = 1.0 + delta_wave + delta_wind
        penalty_pct = (total_factor - 1.0) * 100.0
        
        desc = (
            f"Wave Height Hs={hs:.1f}m, Wind={v_w:.0f} kn. "
            f"Hydrodynamic added resistance increases fuel consumption by {penalty_pct:.1f}%."
        )
        return round(total_factor, 3), round(penalty_pct, 1), desc

    @classmethod
    def simulate_weather_deterioration(
        cls,
        base_factor: float,
        deterioration_severity: str = "moderate"
    ) -> Dict[str, Any]:
        """
        Simulates what happens to the voyage if the weather worsens (Section B question).
        """
        if deterioration_severity == "severe":
            new_factor = base_factor * 1.30
            new_desc = "Severe Deterioration: Sea state escalates to Beaufort 7-8 (Hs 4.8m, 35 kn headwinds)."
            speed_loss_knots = 2.4
        else:
            new_factor = base_factor * 1.15
            new_desc = "Moderate Deterioration: Sea state escalates to Beaufort 5-6 (Hs 2.8m, 22 kn headwinds)."
            speed_loss_knots = 1.2
            
        added_fuel_pct = ((new_factor - base_factor) / base_factor) * 100.0
        return {
            "new_weather_factor": round(new_factor, 3),
            "added_fuel_percentage": round(added_fuel_pct, 1),
            "estimated_speed_loss_knots": speed_loss_knots,
            "description": new_desc
        }
