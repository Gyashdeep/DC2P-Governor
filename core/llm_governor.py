import json
import logging
from typing import Dict, Any
from pydantic import BaseModel, Field
from groq import Groq
from config.settings import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [GOVERNOR] - %(message)s")

class ActionSchema(BaseModel):
    pump_pressure_psi: float = Field(ge=10.0, le=60.0, description="Target pressure optimization value in PSI.")
    coolant_flow_lpm: float = Field(ge=10.0, le=35.0, description="Target liquid coolant flow rate in LPM.")
    valve_actuation_pct: float = Field(ge=0.0, le=100.0, description="Electronic valve deployment percentage.")
    justification: str = Field(description="Engineering rationale behind the asset adjustment strategy.")

class LlmGovernor:
    """Autonomous AI governor managing optimization calculations via Groq Cloud with 429 Fallback Routing."""
    def __init__(self):
        api_key = settings.GROQ_API_KEY if settings.GROQ_API_KEY else import_streamlit_secrets()
        self.client = Groq(api_key=api_key)
        self.active_model = settings.MODEL_NAME

    def compute_optimization_strategy(self, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""
        [ROLE] Liquid-Cooled GPU Cluster Governor Engine.
        [TASK] Optimize parameters based on operational metrics. Prioritize thermal safety while mitigating power drag.
        [CURRENT TELEMETRY] {json.dumps(telemetry)}
        
        CRITICAL OPERATIONAL BOUNDARIES:
        - pump_pressure_psi: MUST be a float between 10.0 and 60.0
        - coolant_flow_lpm: MUST be a float between 10.0 and 35.0
        - valve_actuation_pct: MUST be a float between 0.0 and 100.0
        - justification: MUST be a string detailing your engineering logic.

        OUTPUT FORMAT REQUIREMENT: You must output a valid json object matching the schema. Include all 4 fields.
        """
        
        try:
            # Attempt execution using primary target model
            return self._execute_inference(self.active_model, prompt)
            
        except Exception as e:
            # Catch Groq Rate Limit (429) and cascade to low-overhead high-speed fallback architecture
            if "429" in str(e) and self.active_model == "openai/gpt-oss-120b":
                logging.warning("PRIMARY MODEL RATE LIMIT EXCEEDED. HOT-SWAPPING TO LLAMA-4-SCOUT...")
                try:
                    fallback_model = "meta-llama/llama-4-scout-17b-16e-instruct"
                    data = self._execute_inference(fallback_model, prompt)
                    # Include architectural status in justification string
                    data["justification"] = f"[FALLBACK ROUTING ACTIVE] {data['justification']}"
                    return data
                except Exception as fallback_err:
                    return self._load_hardcoded_failsafe(f"Cascade failure: {str(fallback_err)}")
            else:
                return self._load_hardcoded_failsafe(str(e))

    def _execute_inference(self, model: str, prompt: str) -> Dict[str, Any]:
        """Handles structural API execution constraints."""
        response = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,  
            response_format={
                "type": "json_object",
                "schema": ActionSchema.model_json_schema()
            }
        )
        raw_output = json.loads(response.choices[0].message.content)
        return ActionSchema(**raw_output).model_dump()

    def _load_hardcoded_failsafe(self, error_msg: str) -> Dict[str, Any]:
        """Deterministic safety parameters deployed on deep gateway connection failures."""
        return {
            "pump_pressure_psi": 30.0,
            "coolant_flow_lpm": 15.0,
            "valve_actuation_pct": 50.0,
            "justification": f"CRITICAL LOOP FAILSAFE: {error_msg}"
        }

def import_streamlit_secrets():
    import streamlit as st
    return st.secrets.get("GROQ_API_KEY", "")
