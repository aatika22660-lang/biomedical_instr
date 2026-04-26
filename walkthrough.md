# CAR-MuSC Project Walkthrough

This guide provides a simple, step-by-step walkthrough for setting up and running the CAR-MuSC (Chimeric Antigen Receptor - Muscle Stem Cell) agent-based simulation.

---

## 1. Prerequisites
- **Python 3.12+** (recommended)
- **Git**

## 2. Installation
Clone the repository and install the required dependencies:

```bash
# Clone the repository
git clone https://github.com/aatika22660-lang/CAR_MuSC.git
cd CAR_MuSC

# Install dependencies
pip install -r requirements.txt
```

---

## 3. Core Simulation & Analysis
The primary tool for scientific validation is the **Sensitivity Analysis**. This script sweeps through different noise parameters ($\sigma_{CAR}$) to prove the robustness of the CAR-MuSC navigational advantage.

```bash
# Run the sensitivity analysis
python simulation/sensitivity.py
```
**Output:** A summary table will print to your terminal, and a visualization (`sensitivity_output.png`) will be saved in the `simulation/` directory.

---

## 4. Interactive Dashboard
To explore the simulation in real-time with a graphical interface, run the Streamlit dashboard:

```bash
streamlit run app/dashboard.py
```
**Output:** This will open a browser window where you can adjust parameters and watch the agents navigate the HGF gradient live.

---

## 5. Testing & Validation
The project includes a suite of validation tests to ensure the mathematical and biological models are functioning correctly.

```bash
# Run all validation tests
python tests/test_01_gradient.py
python tests/test_02_single_agent.py
python tests/test_03_car_boost.py
python tests/test_04_engraftment.py
python tests/test_05_repair.py
python tests/test_06_swarm.py
python tests/test_07_metrics.py
```
**Output:** Each test will report a `PASSED` status if the criteria are met and generate relevant plots in the `tests/` directory.

---

## Project Structure
- `simulation/`: Core logic (Agent behavior, Environment, Orchestrator).
- `app/`: Streamlit dashboard for interactive exploration.
- `tests/`: Integration tests and statistical validation.
- `requirements.txt`: Python package dependencies.
