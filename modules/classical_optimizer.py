"""
QuantumGreen Fleet AI - Classical Optimizer Module
Provides deterministic baseline solutions and greedy heuristics
for fleet assignment and single-voyage benchmarks.
"""

from typing import List, Dict, Any, Tuple
from modules.fuel_model import MaritimeFuelModel
from modules.emissions_calculator import EmissionsCalculator
from modules.data_models import VesselInfo, OperatingConditions


class ClassicalOptimizer:
    """Deterministic reference solver for benchmarking."""

    @classmethod
    def solve_greedy_fleet_assignment(
        cls,
        vessels: List[Dict[str, Any]],
        shipments: List[Dict[str, Any]],
        routes: List[Dict[str, Any]],
        fuel_price: float = 650.0,
        carbon_tax: float = 60.0
    ) -> Dict[str, Any]:
        """
        Greedy baseline: assigns each shipment to the lowest fuel rate vessel
        with remaining capacity on the shortest route.
        """
        assignments = []
        vessel_loads = {i: 0.0 for i in range(len(vessels))}
        
        # Sort routes by distance
        direct_route_idx = 0
        min_dist = min(r["distance"] for r in routes)
        for idx, r in enumerate(routes):
            if r["distance"] == min_dist:
                direct_route_idx = idx
                break
                
        total_fuel = 0.0
        total_co2 = 0.0
        
        for s_idx, ship in enumerate(shipments):
            cargo = ship["cargo"]
            # Find first vessel with capacity
            assigned_vessel_idx = None
            for v_idx, v in enumerate(vessels):
                if vessel_loads[v_idx] + cargo <= v["capacity"]:
                    assigned_vessel_idx = v_idx
                    break
                    
            if assigned_vessel_idx is None:
                # Force round robin if over capacity
                assigned_vessel_idx = s_idx % len(vessels)
                
            vessel_loads[assigned_vessel_idx] += cargo
            
            v_spec = vessels[assigned_vessel_idx]
            r_spec = routes[direct_route_idx]
            
            load_ratio = cargo / max(1.0, v_spec["capacity"])
            load_factor = 1.0 + 0.20 * load_ratio
            
            trip_fuel = (
                (r_spec["distance"] / 1000.0)
                * v_spec.get("fuel_rate", 3.0)
                * r_spec.get("weather", 1.0)
                * load_factor
            )
            trip_co2 = trip_fuel * 3.151
            
            total_fuel += trip_fuel
            total_co2 += trip_co2
            
            assignments.append({
                "shipment_index": s_idx,
                "shipment_name": ship["name"],
                "cargo_tonnes": cargo,
                "vessel_index": assigned_vessel_idx,
                "vessel_name": v_spec["name"],
                "route_index": direct_route_idx,
                "route_name": r_spec["name"],
                "fuel_tonnes": trip_fuel,
                "co2_tonnes": trip_co2
            })
            
        fuel_cost = total_fuel * fuel_price
        carbon_cost = total_co2 * carbon_tax
        total_cost = fuel_cost + carbon_cost
        
        # Capacity check
        all_capacities_valid = all(
            vessel_loads[i] <= vessels[i]["capacity"] for i in range(len(vessels))
        )
        
        return {
            "solver": "Classical Greedy Direct Assignment",
            "assignments": assignments,
            "total_fuel_tonnes": total_fuel,
            "total_co2_tonnes": total_co2,
            "fuel_cost_usd": fuel_cost,
            "carbon_cost_usd": carbon_cost,
            "total_cost_usd": total_cost,
            "all_capacities_valid": all_capacities_valid,
            "vessel_loads": vessel_loads
        }
