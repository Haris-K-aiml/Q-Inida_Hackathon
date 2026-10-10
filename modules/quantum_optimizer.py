"""
QuantumGreen Fleet AI - Quantum-Inspired Simulated Annealing Optimizer
Solves multi-vessel multi-route combinatorial optimization using
quantum-inspired simulated annealing with simulated transverse field tunneling.
"""

import math
import random
from typing import List, Dict, Any, Tuple


class QuantumInspiredFleetOptimizer:
    """Quantum-inspired simulated annealing heuristic for constrained fleet logistics."""

    @staticmethod
    def evaluate_solution(
        solution: List[Tuple[int, int]],
        vessels: List[Dict[str, Any]],
        shipments: List[Dict[str, Any]],
        routes: List[Dict[str, Any]],
        fuel_price: float,
        carbon_tax: float
    ) -> Tuple[float, float, float, float, float, List[float]]:
        """
        Calculates Hamiltonian energy (objective cost) of an assignment state:
        E = FuelCost + CarbonCost + CapacityPenalty
        """
        vessel_loads = [0.0] * len(vessels)
        total_fuel = 0.0
        total_co2 = 0.0
        
        for i, (v_idx, r_idx) in enumerate(solution):
            cargo = shipments[i]["cargo"]
            vessel_loads[v_idx] += cargo
            
            v_spec = vessels[v_idx]
            r_spec = routes[r_idx]
            
            load_ratio = cargo / max(1.0, v_spec["capacity"])
            load_factor = 1.0 + 0.20 * load_ratio
            
            # Fuel model formula
            trip_fuel = (
                (r_spec["distance"] / 1000.0)
                * v_spec.get("fuel_rate", 3.0)
                * r_spec.get("weather", 1.0)
                * load_factor
            )
            # CO2 factor (approx 3.151 for VLSFO)
            trip_co2 = trip_fuel * 3.151
            
            total_fuel += trip_fuel
            total_co2 += trip_co2
            
        fuel_cost = total_fuel * fuel_price
        carbon_cost = total_co2 * carbon_tax
        
        # Severe quadratic penalty for capacity overload
        capacity_penalty = 0.0
        for v_idx, load in enumerate(vessel_loads):
            excess = max(0.0, load - vessels[v_idx]["capacity"])
            if excess > 0:
                capacity_penalty += (excess ** 2) * 5000.0 + (excess * 20000.0)
                
        energy = fuel_cost + carbon_cost + capacity_penalty
        return energy, total_fuel, total_co2, fuel_cost, carbon_cost, vessel_loads

    @classmethod
    def solve(
        cls,
        vessels: List[Dict[str, Any]],
        shipments: List[Dict[str, Any]],
        routes: List[Dict[str, Any]],
        fuel_price: float = 650.0,
        carbon_tax: float = 60.0,
        iterations: int = 2500,
        initial_temperature: float = 5000.0,
        random_seed: int = 42
    ) -> Dict[str, Any]:
        """
        Executes Quantum-Inspired Annealing with transverse field tunneling heuristics.
        """
        rng = random.Random(random_seed)
        num_shipments = len(shipments)
        num_vessels = len(vessels)
        num_routes = len(routes)
        
        # Initial random assignment state
        current = [
            (rng.randrange(num_vessels), rng.randrange(num_routes))
            for _ in range(num_shipments)
        ]
        
        current_energy = cls.evaluate_solution(
            current, vessels, shipments, routes, fuel_price, carbon_tax
        )[0]
        
        best = list(current)
        best_energy = current_energy
        
        temperature = initial_temperature
        cooling_rate = 0.996
        
        # Transverse magnetic field strength for quantum tunneling emulation
        gamma_0 = 1000.0
        
        history: List[Dict[str, Any]] = []
        
        for step in range(iterations):
            # Transverse field decreases over time
            gamma_t = gamma_0 * (1.0 - (step / max(1, iterations)))
            
            candidate = list(current)
            
            # Multi-qubit flip / perturbation (quantum spin flip)
            flip_idx = rng.randrange(num_shipments)
            
            # Simulated quantum tunneling: occasionally flip both vessel and route or swap
            if rng.random() < 0.25 and num_shipments > 1:
                # Pair swap
                other_idx = rng.randrange(num_shipments)
                candidate[flip_idx], candidate[other_idx] = candidate[other_idx], candidate[flip_idx]
            else:
                candidate[flip_idx] = (
                    rng.randrange(num_vessels),
                    rng.randrange(num_routes)
                )
                
            candidate_energy = cls.evaluate_solution(
                candidate, vessels, shipments, routes, fuel_price, carbon_tax
            )[0]
            
            delta_e = candidate_energy - current_energy
            
            # Acceptance probability with simulated quantum tunneling term
            tunneling_prob = math.exp(-max(0.0, delta_e) / max(temperature, 0.001))
            # Transverse field tunneling bonus for escaping local barriers
            quantum_fluctuation = 0.05 * (gamma_t / gamma_0)
            
            if delta_e < 0 or rng.random() < (tunneling_prob + quantum_fluctuation):
                current = candidate
                current_energy = candidate_energy
                
            if current_energy < best_energy:
                best = list(current)
                best_energy = current_energy
                
            temperature = max(0.001, temperature * cooling_rate)
            
            if step % max(1, iterations // 20) == 0:
                history.append({
                    "step": step,
                    "energy": best_energy,
                    "temperature": temperature
                })
                
        # Final evaluation
        final_energy, final_fuel, final_co2, final_fuel_cost, final_carbon_cost, final_loads = (
            cls.evaluate_solution(best, vessels, shipments, routes, fuel_price, carbon_tax)
        )
        
        valid_plan = all(
            final_loads[i] <= vessels[i]["capacity"] for i in range(num_vessels)
        )
        
        assignments = []
        for i, (v_idx, r_idx) in enumerate(best):
            v_spec = vessels[v_idx]
            r_spec = routes[r_idx]
            load_ratio = shipments[i]["cargo"] / max(1.0, v_spec["capacity"])
            load_factor = 1.0 + 0.20 * load_ratio
            trip_fuel = (
                (r_spec["distance"] / 1000.0)
                * v_spec.get("fuel_rate", 3.0)
                * r_spec.get("weather", 1.0)
                * load_factor
            )
            trip_co2 = trip_fuel * 3.151
            assignments.append({
                "shipment_index": i,
                "shipment_name": shipments[i]["name"],
                "cargo_tonnes": shipments[i]["cargo"],
                "vessel_index": v_idx,
                "vessel_name": v_spec["name"],
                "route_index": r_idx,
                "route_name": r_spec["name"],
                "distance_km": r_spec["distance"],
                "fuel_tonnes": trip_fuel,
                "co2_tonnes": trip_co2
            })
            
        return {
            "solver": "Quantum-Inspired Simulated Annealing (QUBO / Transverse Field)",
            "iterations": iterations,
            "best_energy": best_energy,
            "assignments": assignments,
            "total_fuel_tonnes": final_fuel,
            "total_co2_tonnes": final_co2,
            "fuel_cost_usd": final_fuel_cost,
            "carbon_cost_usd": final_carbon_cost,
            "total_cost_usd": final_fuel_cost + final_carbon_cost,
            "valid_plan": valid_plan,
            "vessel_loads": final_loads,
            "history": history
        }
