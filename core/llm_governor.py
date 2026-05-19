import json
from typing import Dict, Any
from pydantic import BaseModel, Field
from groq import Groq
from config.settings import settings

class ActionSchema(BaseModel):
    pump_pressure_psi: float = Field(
        ge=10.0, le=60.0, 
        description="Target pressure optimization value in PSI. Must be between 10.0 and 60.0."
    )
    coolant_flow_lpm: float = Field(
        ge=10.0, le=35.0, 
        description="Target liquid coolant flow rate in Liters Per Minute. Must be between 10.0 and 35.0."
    )
    valve_actuation_pct: float = Field(
        ge=0.0, le=100.0, 
        description="Electronic valve deployment percentage (0.0 - 100.0)."
    )
    justification: str = Field(
        description="Engineering rationale behind the asset adjustment strategy. This text field is MANDATORY."
    )

class LlmGovernor:
    """Autonomous AI governor managing optimization calculations via Groq Cloud."""
    def __init__(self):
        api_key = settings.GROQ_API_KEY if settings.GROQ_API_KEY else import_streamlit_secrets()
        self.client = Groq(api_key=api_key)

    def compute_optimization_strategy(self, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""
        [ROLE] Liquid-Cooled GPU Cluster Governor Engine.
        [TASK] Optimize parameters based on operational metrics. Prioritize thermal safety while mitigating power drag.
        [CURRENT TELEMETRY] {json.dumps(telemetry)}
        
        CRITICAL OPERATIONAL BOUNDARIES:
        - pump_pressure_psi: MUST be a float between 10.0 and 60.0
        - coolant_flow_lpm: MUST be a float between 10.0 and 35.0
        - valve_actuation_pct: MUST be a float between 0.0 and 100.0
        - justification: MUST be a string detailing your engineering logic. Do not leave this empty.

        OUTPUT FORMAT REQUIREMENT: You must output a valid json object matching the schema. Include all 4 fields.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=settings.MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,  # Set to 0.1 to allow fluid text generation for the justification string
                response_format={
                    "type": "json_object",
                    "schema": ActionSchema.model_json_schema()
                }
            )
            
            raw_output = json.loads(response.choices[0].message.content)
            validated_data = ActionSchema(**raw_output)
            return validated_data.model_dump()
            
        except Exception as e:
            return {
                "pump_pressure_psi": 30.0,
                "coolant_flow_lpm": 15.0,
                "valve_actuation_pct": 50.0,
                "justification": f"FAILSAFE INITIATED: Schema Validation/API Error: {str(e)}"
            }

def import_streamlit_secrets():
    import streamlit as st
    return st.secrets.get("GROQ_API_KEY", "")
