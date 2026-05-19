import os
from pydantic_settings import BaseSettings

class SystemSettings(BaseSettings):
    # Hardware Safety Limits
    MAX_ALLOWED_TEMP_C: float = 85.0
    MIN_COOLANT_FLOW_LPM: float = 10.0
    MAX_PUMP_PRESSURE_PSI: float = 60.0
    
    # API Configurations
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    
    # High-Performance Production Models Target Matrix
    # Options: "openai/gpt-oss-120b" (Deep Reasoning) or "meta-llama/llama-4-scout-17b-16e-instruct" (Next-Gen Native)
    MODEL_NAME: str = "openai/gpt-oss-120b" 

    class Config:
        env_file = ".env"

settings = SystemSettings()
