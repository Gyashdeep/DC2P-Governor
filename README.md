# Autonomous DC2P Governor 🌊

### The Project
**DC2P (Data-Center-to-Potable)** is an AI-driven energy governor designed to solve the 2027 water scarcity crisis. It utilizes the waste heat from high-density AI data centers to power local water purification systems.

### Features
*   **Thermodynamic Agent:** Powered by Groq (GPT-OSS 120B) for real-time physics reasoning.
*   **Dynamic Load Balancing:** Automatically spikes compute load to increase heat output when local water reservoirs are low.
*   **Water-Positive Infrastructure:** Aims for a Water Usage Effectiveness (WUE) of < 0.2 L/kWh.

### Setup
1. Clone the repo.
2. Create `.streamlit/secrets.toml` with your `GROQ_API_KEY`.
3. Run `pip install -r requirements.txt`.
4. Run `streamlit run app.py`.
