# Q-Path: Quantum-Inspired Emergency Response Hub - Chennai

## Overview
Q-Path is an emergency response optimization system for Chennai that uses quantum-inspired algorithms (QAOA) to compute optimal routes for disaster response, considering real-time traffic, weather, and resource constraints.

## Features
- 🏠 Dual Interface: Citizen Incident Reporting + Volunteer Dashboard
- 🏥 Chennai & Surrounding Districts Emergency Infrastructure with Real Locations:
  - 15 major hospitals across Chennai, Chengalpattu, Kanchipuram, and Thiruvallur districts (Stanley Medical College, Kilpauk Medical College, Rajiv Gandhi GGH, Apollo Greams Road, Govt Peripheral Hospital Perambur, Royapettah Govt Hospital, Fortis Malar, SIMS, Chengalpattu Medical College, SRM Global, KGM Govt Hospital, Kanchipuram Govt Hospital, Arignar Anna Govt Hospital, Thiruvallur GGH, Thiruvallur District HQ Hospital)
  - 12 fire stations (Tamil Nadu Fire & Rescue Service across Chennai, Thiruvallur, Kanchipuram, and Chengalpattu)
  - 11 police stations (Chennai Police and district police stations)
  - 7 lifeguard stations (Marina Beach, Elliot's Beach, Thiruvanmiyur, Akkarai, Muttukadu, Mahabalipuram)
  - 4 ambulances (108 Emergency Service)
- 🔀 Graph-Based Routing with dynamic edge weights
- 🔬 QAOA Quantum-Inspired Optimization
- 📊 Classical vs Quantum Performance Comparison
- 🔄 Real-Time Re-Optimization
- 🗺️ Interactive Dashboard with Map Visualization
- 👨‍⚕️ Secure Volunteer Portal with Authentication

## Installation

```bash
pip install -r requirements.txt
```

## Running the Application

```bash
python app.py
```

Then open http://localhost:5000 in your browser.

### User Access

**For Citizens (Report Emergency):**
- Click "Report Incident" from home page
- No login required, immediate access

**For Emergency Responders (Volunteer Dashboard):**
- Click "Volunteer Portal" from home page
- Login credentials: `admin` / `admin123`
- Access full optimization dashboard

## Architecture

### Backend (Python)
- `app.py` - Flask API server
- `optimizer/qubo_solver.py` - QUBO formulation and QAOA implementation
- `optimizer/classical_solver.py` - Classical baseline algorithms
- `models/graph_model.py` - Emergency routing graph
- `models/entities.py` - Emergency entity models

### Frontend (HTML/JS)
- `static/home.html` - Landing page with dual options
- `static/incident_report.html` - Citizen incident reporting interface
- `static/login.html` - Volunteer authentication
- `static/index.html` - Volunteer dashboard (main app)
- `static/app.js` - Dashboard logic and API integration
- Interactive map with Leaflet.js
- Real-time metrics comparison

## How It Works

1. **Graph Modeling**: All emergency entities are nodes in a weighted graph
2. **Edge Weights**: Distance × Traffic Multiplier × Weather Severity
3. **QUBO Formulation**: Routing problem reformulated as Quadratic Unconstrained Binary Optimization
4. **QAOA Solving**: Quantum-inspired algorithm finds optimal routes
5. **Real-Time Updates**: Automatic re-optimization on condition changes
` - Home page
- `GET /incident` - Incident reporting page
- `GET /volunteer` - Volunteer login page
- `GET /dashboard` - Volunteer dashboard (requires login)
- `GET /api/entities` - Get all emergency entities
- `POST /api/victims` - Add new victim emergency request
- `POST /api/optimize` - Compute optimal routes
- `POST /api/conditions` - Update traffic/weather
- `POST /api/reset` - Reset system
- `POST /api/demo` - Run demo scenario
- `POST /api/optimize` - Compute optimal routes
- `POST /api/update-conditions` - Update traffic/weather
- `GET /api/metrics` - Get optimization metrics

## Technologies
- **Quantum Computing**: Qiskit, QAOA
- **Optimization**: NetworkX, SciPy
- **Backend**: Flask, Python
- **Frontend**: Leaflet.js, Chart.js
- **APIs**: Simulated traffic/weather data
