# Q-Path Emergency Response Hub - Chennai

## Quick Start Guide

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Tests

Verify all components work:

```bash
python test.py
```

### 3. Start the Application

```bash
python app.py
```

### 4. Open Application

Navigate to: http://localhost:5000

## Application Structure

### 🏠 Home Page
The landing page provides two main options:

1. **🆘 Report Incident** - For citizens to report emergencies
2. **👨‍⚕️ Volunteer Portal** - For emergency responders and coordinators

### 📍 Incident Reporting (Citizen View)
Citizens can report emergencies by:
- Clicking on map to mark exact location (or auto-detect location)
- Selecting emergency type (medical, fire, accident, natural disaster)
- Choosing severity level (Critical, High, Medium)
- Providing contact number and description
- Submitting request for immediate assistance

**Access**: Click "Report Incident" from home page or go to `/incident`

### 👥 Volunteer Portal (Emergency Responders)

**Login Credentials** (Demo):
- Username: `admin`
- Password: `admin123`

After login, volunteers access the main dashboard with:
- Emergency infrastructure visualization
- Route optimization tools
- Resource allocation management
- Real-time incident monitoring

**Access**: Click "Volunteer Portal" from home page → Login → Dashboard

## Features Overview

### 🏥 Emergency Infrastructure (Chennai & Surrounding Districts)
**Real Emergency Services with Actual Locations:**

- **15 Major Hospitals**:
  - Rajiv Gandhi Govt General Hospital, Chennai (044-2530 5000)
  - Apollo Hospitals (Greams Road), Chennai (044-2829 3333)
  - Stanley Medical College, Chennai (044-2528 1351)
  - Kilpauk Medical College, Chennai (044-2664 1611)
  - Govt Peripheral Hospital (Perambur), Chennai (044-2662 2111)
  - Royapettah Govt Hospital, Chennai (044-2844 7564)
  - Fortis Malar Hospital, Adyar, Chennai (044-42892222)
  - SIMS Hospital, Vadapalani, Chennai (044-45678900)
  - Chengalpattu Medical College, Chengalpattu (044-2742 6666)
  - SRM Global Hospitals, Chengalpattu (044-4743 2345)
  - KGM Govt Hospital, Chengalpattu (044-2742 2211)
  - Kanchipuram Govt Hospital, Kanchipuram (044-2722 2442)
  - Arignar Anna Govt Hospital, Kanchipuram (044-2722 2234)
  - Thiruvallur Govt General Hospital, Thiruvallur (044-2766 0306)
  - Thiruvallur District HQ Hospital, Thiruvallur (044-2766 2345)

- **12 Fire Stations** (Tamil Nadu Fire and Rescue, Dial: 101):
  - Central Fire Station, Pudupet
  - Kilpauk Fire Station
  - T Nagar Fire Station
  - Anna Nagar Fire Station
  - Adyar Fire Station
  - Teynampet Fire Station
  - Kilpauk Fire Station (North)
  - Avadi Fire Station (Thiruvallur)
  - Ponneri Fire Station (Thiruvallur)
  - Gummidipoondi Fire Station (Thiruvallur)
  - Sriperumbudur Fire Station (Kanchipuram)
  - Kalpakkam Fire Station (Chengalpattu)

- **11 Police Stations** (Dial: 100):
  - Central Crime Branch, Egmore
  - Anna Nagar Police Station
  - T Nagar Police Station
  - Adyar Police Station
  - Mylapore Police Station
  - Flower Bazaar Police Station
  - Poonamallee Police Station (Thiruvallur)
  - Red Hills Police Station (Thiruvallur)
  - Kanchipuram Taluk PS
  - Guduvanchery Police Station (Chengalpattu)
  - Maduranthakam Police Station (Chengalpattu)

- **7 Lifeguard Stations**:
  - Marina Beach Lifeguard Post 1 & 2
  - Elliot's Beach Lifeguard Station, Besant Nagar
  - Thiruvanmiyur Beach Tower
  - Akkarai Beach Point
  - Muttukadu Boat House Area (Chengalpattu)
  - Mahabalipuram Shore Temple Side (Chengalpattu)

- **4 Ambulances**: 
  - 108 Emergency Service (Government) - Dial: 108
  - Private hospital ambulances

All locations, phone numbers, and addresses are real and operational.

### 🗺️ Interactive Map
- **Volunteer Dashboard**: For emergency coordinators
  - Visualize all emergency resources in Chennai
  - Add random victims for testing
  - Control traffic and weather conditions
  - Run optimization algorithms

- **Citizen Incident Report**: For public emergency requests
  - Click map to set emergency location
  - Select emergency type and severity level
  - Submit help request with contact details

### 🔬 Quantum-Inspired Optimization
- **Classical Algorithms**:
  - Greedy TSP
  - Simulated Annealing
  - Multi-start Nearest Neighbor

- **Quantum Algorithms**:
  - QUBO Formulation
  - QAOA (Quantum Approximate Optimization Algorithm)
  - Hybrid approaches for scalability

### 📊 Performance Metrics
- Real-time convergence comparison
- Cost reduction percentage
- Route visualization on map
- Resource allocation optimization

### ⚡ Real-Time Re-Optimization
- Dynamic traffic condition updates
- Weather severity adjustments
- Automatic re-routing when conditions change
- New victim integration

## Usage Examples

### Report an Emergency (Citizen)
1. Navigate to home page
2. Click "Report Incident"
3. Click on map to mark location (or allow auto-detection)
4. Select emergency type and severity
5. Enter contact number
6. Add description
7. Click "Request Emergency Assistance"

### Access Volunteer Dashboard
1. Navigate to home page
2. Click "Volunteer Portal"
3. Login with credentials (admin/admin123)
4. Access full dashboard features

### Run Optimization (Volunteer)
1. Login to volunteer dashboard
2. Add victims (manual or random)
3. Adjust traffic/weather conditions
4. Click "🚀 Optimize Routes"
5. View results in metrics panel

### Compare Classical vs Quantum
1. Add 3-5 victim locations
2. Run optimization with "both" methods
3. View convergence chart
4. Check improvement percentage

### Run Full Demo
1. Click "▶️ Run Demo"
2. System automatically:
   - Adds 3 victim requests
   - Updates conditions
   - Runs both classical and quantum optimization
   - Displays comparative results

## Technical Details

### QUBO Formulation
The routing problem is formulated as:
```
minimize: x^T Q x

where:
- x_i_t = 1 if node i visited at time t
- Q encodes edge weights and constraints
- Constraints ensure valid tours via penalties
```

### QAOA Circuit
- Parameterized quantum circuit
- Cost Hamiltonian: encodes QUBO problem
- Mixer Hamiltonian: explores solution space
- Classical optimization loop for parameters

### Graph Model
- Nodes: Emergency entities
- Edge weights: distance × traffic × weather
- Complete graph for full connectivity
- Dynamic weight updates
13.0654,
  "lon": 80.2491,
  "severity": "critical",
  "emergency_type": "medical",
  "phone": "+91 9876543210",
  "description": "Medical emergency details
### GET /api/entities
Get all emergency entities

### POST /api/victims
Add new victim emergency request
```json
{
  "lat": 28.6120,
  "lon": 77.2100,
  "severity": "critical"
}
```

### POST /api/optimize
Run optimization
```json
{
  "method": "both",  // "classical", "qaoa", or "both"
  "start_node": "H1",
  "target_nodes": ["V1", "V2"],
  "algorithm": "simulated_annealing"
}
```

### POST /api/conditions
Update traffic/weather
```json
{
  "traffic": "high",
  "weather": "storm"
}
```

### POST /api/reset
Reset system and clear victims

### POST /api/demo
Run complete demo scenario

## Performance Notes

- QAOA works best for small problems (< 5 nodes)
- Larger problems use hybrid greedy+QAOA approach
- Classical methods scale better but may find suboptimal routes
- Quantum advantage emerges with complex constraint landscapes

## Troubleshooting

**Issue**: Qiskit import error
```bash
pip install qiskit qiskit-aer qiskit-optimization --upgrade
```

**Issue**: Map not showing
- Check internet connection (needs OpenStreetMap tiles)
- Ensure port 5000 is not blocked

**Issue**: Optimization takes too long
- Reduce max_iterations parameter
- Use fewer victim nodes
- Switch to classical-only optimization

## Future Enhancements
- Integration with real Google Maps API
- Live weather data from Weather API
- Multi-objective optimization (time, cost, resources)
- Real quantum hardware execution (IBM Quantum)
- Mobile app interface
- Historical incident analysis

## Credits
Built with:
- Qiskit (Quantum Computing)
- Flask (Backend)
- Leaflet.js (Maps)
- Chart.js (Visualization)
- NetworkX (Graph Theory)
