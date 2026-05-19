import os
from pydantic_settings import BaseSettings

class SystemSettings(BaseSettings):
    # Hardware Safety Limits
    MAX_ALLOWED_TEMP_C: float = 85.0
    MIN_COOLANT_FLOW_LPM: float = 10.0
    MAX_PUMP_PRESSURE_PSI: float = 60.0
    
    # API Configurations
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "mock_key_if_testing")
    MODEL_NAME: str = "llama-3.3-70b-specdec"

    class Config:
        env_file = ".env"

settings = SystemSettings()
