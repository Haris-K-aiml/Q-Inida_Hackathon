"""
QuantumGreen Fleet AI - Scheduling and Deadline Feasibility Engine
Evaluates voyage durations, ETA, strict delivery deadlines, slack time,
and speed recommendations for demurrage avoidance and fuel reduction.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from modules.data_models import VoyageInfo, OperatingConditions


class SchedulingEngine:
    """Evaluates voyage calendar constraints and speed trade-offs."""

    @classmethod
    def analyze_schedule_feasibility(
        cls,
        voyage: VoyageInfo,
        conditions: OperatingConditions,
        port_turnaround_hours: float = 2.0
    ) -> Dict[str, Any]:
        """
        Determines if the planned voyage can meet the delivery deadline.
        """
        dep_time = voyage.departure_time or datetime.now()
        speed = voyage.planned_speed_knots
        dist = voyage.distance_nm
        
        # Sailing duration
        sailing_hours = dist / max(1.0, speed)
        total_trip_hours = sailing_hours + port_turnaround_hours
        
        estimated_eta = dep_time + timedelta(hours=total_trip_hours)
        
        # If no deadline specified
        if voyage.delivery_deadline is None:
            return {
                "has_deadline": False,
                "is_feasible": True,
                "sailing_hours": sailing_hours,
                "total_trip_hours": total_trip_hours,
                "estimated_eta": estimated_eta,
                "required_speed_knots": speed,
                "slack_hours": None,
                "recommendation": (
                    f"Estimated voyage duration: {sailing_hours:.1f} hours ({sailing_hours/24:.1f} days). "
                    f"Expected arrival: {estimated_eta.strftime('%Y-%m-%d %H:%M UTC')}."
                )
            }
            
        deadline = voyage.delivery_deadline
        available_hours = (deadline - dep_time).total_seconds() / 3600.0
        
        if available_hours <= 0:
            return {
                "has_deadline": True,
                "is_feasible": False,
                "sailing_hours": sailing_hours,
                "total_trip_hours": total_trip_hours,
                "estimated_eta": estimated_eta,
                "available_hours": available_hours,
                "slack_hours": available_hours - total_trip_hours,
                "required_speed_knots": 999.0,
                "recommendation": "CRITICAL: Delivery deadline has already passed relative to departure time."
            }
            
        # Available hours for pure sailing
        sailing_avail_hours = max(0.5, available_hours - port_turnaround_hours)
        required_speed = dist / sailing_avail_hours
        
        slack_hours = available_hours - total_trip_hours
        is_feasible = (total_trip_hours <= available_hours) and (required_speed <= conditions.speed_max_knots)
        
        # Recommendations based on slack
        if not is_feasible:
            if required_speed > conditions.speed_max_knots:
                rec = (
                    f"INFEASIBLE: Meeting the deadline requires an average speed of {required_speed:.1f} knots, "
                    f"which exceeds the vessel's maximum operational speed limit of {conditions.speed_max_knots:.1f} knots. "
                    f"Vessel will arrive approximately {-slack_hours:.1f} hours late."
                )
            else:
                rec = (
                    f"DEADLINE AT RISK: At planned speed {speed:.1f} knots, arrival is {-slack_hours:.1f} hours late. "
                    f"Increasing speed to {required_speed:.1f} knots would meet the deadline."
                )
        else:
            if slack_hours > 12.0:
                slow_steam_speed = max(conditions.speed_min_knots, dist / (available_hours - port_turnaround_hours - 2.0))
                rec = (
                    f"FEASIBLE WITH SLACK: Arrival is {slack_hours:.1f} hours ahead of deadline. "
                    f"Slow steaming at {slow_steam_speed:.1f} knots would save fuel and CO2 while still arriving on schedule."
                )
            else:
                rec = (
                    f"FEASIBLE: Tight schedule with {slack_hours:.1f} hours buffer. "
                    f"Maintain current speed of {speed:.1f} knots."
                )
                
        return {
            "has_deadline": True,
            "is_feasible": is_feasible,
            "sailing_hours": sailing_hours,
            "total_trip_hours": total_trip_hours,
            "available_hours": available_hours,
            "slack_hours": slack_hours,
            "required_speed_knots": round(required_speed, 1),
            "estimated_eta": estimated_eta,
            "deadline": deadline,
            "recommendation": rec
        }
