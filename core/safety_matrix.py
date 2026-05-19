import logging
from typing import Dict, Any, Tuple
from config.settings import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [SAFETY] - %(message)s")

class ActuationSafetyMatrix:
    """Deterministic validation layer enforcing thermodynamic laws."""
    
    @staticmethod
    def verify_action(proposed_actions: Dict[str, Any], current_temp: float) -> Tuple[Dict[str, Any], bool]:
        """Validates LLM commands against hardcoded physical constraints."""
        sanitized = proposed_actions.copy()
        override_triggered = False

        # Constraint 1: Prevent Pump Over-pressurization
        if sanitized.get("pump_pressure_psi", 0) > settings.MAX_PUMP_PRESSURE_PSI:
            logging.warning(f"LLM requested dangerous pressure: {sanitized['pump_pressure_psi']} PSI. Throttling to max limit.")
            sanitized["pump_pressure_psi"] = settings.MAX_PUMP_PRESSURE_PSI
            override_triggered = True

        # Constraint 2: Verify Flow Rate meets Minimum/Maximum Critical Thresholds
        if sanitized.get("coolant_flow_lpm", 0) < settings.MIN_COOLANT_FLOW_LPM:
            logging.warning(f"LLM requested sub-nominal flow: {sanitized['coolant_flow_lpm']} LPM. Overriding to safe minimum.")
            sanitized["coolant_flow_lpm"] = settings.MIN_COOLANT_FLOW_LPM
            override_triggered = True
        elif sanitized.get("coolant_flow_lpm", 0) > settings.MAX_COOLANT_FLOW_LPM:
            logging.warning(f"LLM requested excessive flow: {sanitized['coolant_flow_lpm']} LPM. Clamping to hydraulic maximum.")
            sanitized["coolant_flow_lpm"] = settings.MAX_COOLANT_FLOW_LPM
            override_triggered = True

        # Constraint 3: Thermal Emergency Override Cascade
        if current_temp >= settings.MAX_ALLOWED_TEMP_C:
            logging.error(f"CRITICAL THERMAL THRESHOLD EXCEEDED: {current_temp}°C! Initiating safety dump.")
            sanitized["pump_pressure_psi"] = settings.MAX_PUMP_PRESSURE_PSI
            sanitized["coolant_flow_lpm"] = settings.MAX_COOLANT_FLOW_LPM
            sanitized["valve_actuation_pct"] = 100.0
            override_triggered = True

        return sanitized, override_triggered
