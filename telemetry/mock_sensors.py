import random
import time
from typing import Dict, Any

class RealTimeTelemetryEngine:
    """Simulates real-world dynamic industrial GPU clusters under load constraints."""
    def __init__(self):
        self.rack_temp = 55.0
        self.coolant_inlet_temp = 22.0
        self.ambient_temp = 28.0

    def read_sensors(self, current_actuation: Dict[str, Any]) -> Dict[str, Any]:
        flow_factor = current_actuation.get("coolant_flow_lpm", 15.0) / 15.0
        pressure_factor = current_actuation.get("pump_pressure_psi", 30.0) / 30.0
        
        load_spike = random.uniform(5.0, 18.0) if random.random() > 0.7 else random.uniform(-2.0, 4.0)
        
        cooling_effect = (flow_factor * 4.2) + (pressure_factor * 1.5)
        self.rack_temp += (load_spike - cooling_effect)
        self.rack_temp = max(35.0, min(self.rack_temp, 92.0))
        
        return {
            "timestamp": time.time(),
            "gpu_rack_temperature_c": round(self.rack_temp, 2),
            "coolant_inlet_temp_c": round(self.coolant_inlet_temp + (self.rack_temp * 0.1), 2),
            "ambient_facility_temp_c": round(self.ambient_temp + random.uniform(-0.5, 0.5), 2),
            "fluid_return_pressure_psi": round(current_actuation.get("pump_pressure_psi", 30.0) * random.uniform(0.96, 1.02), 2)
        }
