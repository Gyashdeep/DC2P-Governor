import json
from typing import Dict, Any
from pydantic import BaseModel, Field
from groq import Groq
from config.settings import settings

class ActionSchema(BaseModel):
    pump_pressure_psi: float = Field(description="Target pressure optimization value.")
    coolant_flow_lpm: float = Field(description="Target liquid coolant flow rate in Liters Per Minute.")
    valve_actuation_pct: float = Field(description="Electronic valve deployment percentage (0-100).")
    justification: str = Field(description="Engineering rationale behind the asset adjustment strategy.")

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
        
        CRITICAL: You MUST respond with a JSON object that contains exactly these keys and no others:
        - pump_pressure_psi
        - coolant_flow_lpm
        - valve_actuation_pct
        - justification
        """
        
        try:
            # Enforcing strict Pydantic JSON schema format directly at the Groq API level
            response = self.client.chat.completions.create(
                model=settings.MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,  # Dropped to 0 for maximum deterministic consistency
                response_format={
                    "type": "json_object",
                    "schema": ActionSchema.model_json_schema() # Forces the model to adhere to the schema keys
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
