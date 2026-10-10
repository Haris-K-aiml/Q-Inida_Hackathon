"""
QuantumGreen Fleet AI - Data Models
Typed data structures for maritime vessels, voyages, operating conditions,
data provenance, and analysis results.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime, timezone


class DataProvenance(str, Enum):
    """Identifies the origin and verification level of a data point."""
    USER_ENTERED = "User Entered"
    VERIFIED_AIS = "Verified AIS / Registry"
    SYSTEM_ESTIMATED = "System Estimated / Calibrated"
    HISTORICAL_BENCHMARK = "Historical Benchmark"
    SIMULATED_PREDICTION = "Simulated / Predicted"
    NOT_PROVIDED = "Not Provided (Blank)"


class VesselType(str, Enum):
    CARGO_GENERAL = "Cargo Vessel (General)"
    CONTAINER = "Container Ship"
    BULK_CARRIER = "Bulk Carrier"
    OIL_TANKER = "Oil / Chemical Tanker"
    LNG_CARRIER = "LNG Carrier"
    RO_RO = "Ro-Ro Cargo"
    FEEDER = "Feeder Vessel"


class FuelType(str, Enum):
    VLSFO = "Very Low Sulfur Fuel Oil (VLSFO)"
    HFO = "Heavy Fuel Oil (HFO)"
    MGO = "Marine Gas Oil (MGO)"
    LNG = "Liquefied Natural Gas (LNG)"
    METHANOL = "Green Methanol"
    BIOFUEL = "Bio-Bunkers (B30)"


class VoyageStatus(str, Enum):
    UNDERWAY = "Underway Using Engine"
    AT_ANCHOR = "At Anchor"
    IN_PORT = "Moored / In Port"
    MANEUVERING = "Maneuvering"
    DRIFTING = "Drifting"


@dataclass
class VesselInfo:
    """Maritime vessel specifications and state."""
    name: str = "MV Ocean Pioneer"
    imo: Optional[str] = None
    mmsi: Optional[str] = None
    vessel_type: str = VesselType.CARGO_GENERAL.value
    length_m: Optional[float] = 145.0
    beam_m: Optional[float] = 22.0
    draft_m: Optional[float] = 7.5
    dwt_tonnes: Optional[float] = 12000.0
    max_cargo_capacity_tonnes: float = 10000.0
    current_cargo_weight_tonnes: float = 8000.0
    fuel_type: str = FuelType.VLSFO.value
    sfoc_g_per_kwh: Optional[float] = 175.0  # Specific Fuel Oil Consumption
    engine_power_kw: Optional[float] = 5200.0
    base_fuel_rate_tonnes_per_day: Optional[float] = 16.5
    current_fuel_tonnes: Optional[float] = 220.0
    
    # Provenance tags for each field: {field_name: DataProvenance}
    provenance: Dict[str, DataProvenance] = field(default_factory=dict)

    def get_provenance(self, field_name: str) -> DataProvenance:
        return self.provenance.get(field_name, DataProvenance.USER_ENTERED)


@dataclass
class VoyageInfo:
    """Maritime voyage itinerary and navigational status."""
    departure_port: str = "Chennai Port"
    destination_port: str = "Singapore"
    current_lat: Optional[float] = 13.0827
    current_lon: Optional[float] = 80.2707
    planned_route: str = "Direct Malacca Strait"
    waypoints: List[Dict[str, Any]] = field(default_factory=list)
    current_speed_knots: Optional[float] = 12.0
    planned_speed_knots: float = 12.0
    distance_nm: float = 1580.0  # Nautical miles
    departure_time: Optional[datetime] = None
    expected_arrival_time: Optional[datetime] = None
    delivery_deadline: Optional[datetime] = None
    status: str = VoyageStatus.UNDERWAY.value
    
    # Provenance tags
    provenance: Dict[str, DataProvenance] = field(default_factory=dict)

    def get_provenance(self, field_name: str) -> DataProvenance:
        return self.provenance.get(field_name, DataProvenance.USER_ENTERED)


@dataclass
class OperatingConditions:
    """Environmental, financial, and operational constraints."""
    weather_condition: str = "Moderate Sea (BF 4)"
    wind_speed_knots: Optional[float] = 15.0
    wave_height_m: Optional[float] = 1.8
    current_drift_knots: Optional[float] = 0.5
    fuel_price_per_tonne: float = 650.0  # USD / tonne
    historical_daily_fuel: Optional[float] = 16.2
    historical_avg_speed: Optional[float] = 12.5
    speed_min_knots: float = 9.0
    speed_max_knots: float = 16.5
    max_draft_limit_m: Optional[float] = 12.0
    is_seca_compliant_required: bool = False
    carbon_emission_budget_tonnes: Optional[float] = 250.0
    carbon_tax_per_tonne_co2: float = 60.0  # USD / tCO2
    
    # Provenance tags
    provenance: Dict[str, DataProvenance] = field(default_factory=dict)

    def get_provenance(self, field_name: str) -> DataProvenance:
        return self.provenance.get(field_name, DataProvenance.USER_ENTERED)


@dataclass
class ScenarioInput:
    """Full snapshot of an input scenario submitted to the AI engine."""
    vessel: VesselInfo
    voyage: VoyageInfo
    conditions: OperatingConditions
    problem_statement: str
    selected_unit_distance: str = "NM"  # 'NM' or 'km'
    selected_unit_speed: str = "knots"  # 'knots' or 'km/h'
    selected_unit_weight: str = "tonnes"  # 'tonnes' or 'DWT'


@dataclass
class CalculatedMetrics:
    """Core numerical outputs computed by verified backend modules."""
    fuel_consumption_tonnes: float
    fuel_cost_usd: float
    co2_emissions_tonnes: float
    carbon_cost_usd: float
    total_cost_usd: float
    voyage_duration_hours: float
    voyage_duration_days: float
    estimated_eta: Optional[datetime]
    deadline_feasible: bool
    deadline_slack_hours: Optional[float]
    fuel_remaining_at_dest_tonnes: Optional[float]
    fuel_shortage: bool
    cii_rating: str  # A, B, C, D, E
    cii_grams_per_dwt_nm: float
    weather_resistance_penalty_pct: float
    hydrodynamic_power_kw: float


@dataclass
class RouteAlternative:
    """Comparison candidate for alternative maritime routing."""
    route_name: str
    distance_nm: float
    weather_factor: float
    weather_desc: str
    speed_knots: float
    duration_hours: float
    fuel_tonnes: float
    co2_tonnes: float
    fuel_cost_usd: float
    feasible: bool
    recommendation_reason: str


@dataclass
class StructuredAIAnswer:
    """Comprehensive 10-section structured AI maritime response."""
    problem_type: str
    section_1_problem_understanding: str
    section_2_input_summary: List[Dict[str, Any]]
    section_3_data_quality_missing_info: Dict[str, Any]
    section_4_technical_analysis: str
    section_5_calculated_results: CalculatedMetrics
    section_6_recommended_solution: Dict[str, Any]
    section_7_explanation: str
    section_8_expected_impact: Dict[str, Any]
    section_9_confidence_and_limitations: Dict[str, Any]
    section_10_next_actions: List[str]
    
    # Scenario comparisons (baseline vs optimized, alternative routes)
    baseline_metrics: Optional[CalculatedMetrics] = None
    route_comparisons: List[RouteAlternative] = field(default_factory=list)
    speed_curve_data: List[Dict[str, Any]] = field(default_factory=list)
    
    # Metadata
    engine_mode: str = "Rule & Physics-Based Maritime Engine (Calibrated)"
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
