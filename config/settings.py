import os
from pydantic_settings import BaseSettings

class SystemSettings(BaseSettings):
    # Hardware Safety Limits
    MAX_ALLOWED_TEMP_C: float = 85.0
    MIN_COOLANT_FLOW_LPM: float = 10.0
    MAX_COOLANT_FLOW_LPM: float = 35.0  # Added hard ceiling for flow rate
    MAX_PUMP_PRESSURE_PSI: float = 60.0
    
    # API Configurations
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    MODEL_NAME: str = "openai/gpt-oss-120b" 

    class Config:
        env_file = ".env"

settings = SystemSettings()
