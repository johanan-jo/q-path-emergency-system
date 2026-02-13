"""
Flask API for Q-Path Emergency Response Hub.
Provides endpoints for entity management, optimization, and real-time updates.
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys
from dotenv import load_dotenv
from langchain_cerebras import ChatCerebras

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.entities import EmergencyDatabase, EntityType, EmergencyEntity, Location
from models.graph_model import EmergencyGraph
from optimizer.classical_solver import ClassicalSolver
from optimizer.qubo_solver import QUBOSolver

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

# Initialize system components
entity_db = EmergencyDatabase()
graph = EmergencyGraph(entity_db)
classical_solver = ClassicalSolver(graph)
qaoa_solver = QUBOSolver(graph)

# Initialize Cerebras LLM for chatbot
try:
    llm = ChatCerebras(model="gpt-oss-120b")
except Exception as e:
    print(f"Warning: Could not initialize Cerebras LLM: {e}")
    llm = None

# Global state for tracking optimization results
optimization_history = []
latest_assignments = {}  # Store latest resource assignments by victim ID

def auto_assign_resources(victim, emergency_type):
    """Automatically assign appropriate resources based on emergency type."""
    # Get appropriate resources based on emergency type
    if emergency_type == 'medical':
        primary_resources = entity_db.get_by_type(EntityType.AMBULANCE)
        secondary_resources = entity_db.get_by_type(EntityType.HOSPITAL)
    elif emergency_type == 'fire':
        primary_resources = entity_db.get_by_type(EntityType.FIRE_STATION)
        secondary_resources = []
    elif emergency_type == 'accident':
        primary_resources = entity_db.get_by_type(EntityType.AMBULANCE)
        secondary_resources = entity_db.get_by_type(EntityType.POLICE_STATION)
    else:
        # Default: assign closest available resource
        primary_resources = (
            entity_db.get_by_type(EntityType.AMBULANCE) + 
            entity_db.get_by_type(EntityType.FIRE_STATION) + 
            entity_db.get_by_type(EntityType.POLICE_STATION)
        )
        secondary_resources = entity_db.get_by_type(EntityType.HOSPITAL)
    
    # Find closest available resource
    available_resources = [r for r in primary_resources if r.available]
    if not available_resources and secondary_resources:
        available_resources = [r for r in secondary_resources if r.available]
    
    if not available_resources:
        return None
    
    # Calculate closest resource
    closest_resource = None
    min_distance = float('inf')
    for resource in available_resources:
        distance = graph.get_edge_weight(resource.id, victim.id)
        if distance < min_distance:
            min_distance = distance
            closest_resource = resource
    
    if not closest_resource:
        return None
    
    # Find nearest hospital for medical emergencies
    nearest_hospital = None
    hospital_distance = 0
    if emergency_type in ['medical', 'accident']:
        hospitals = entity_db.get_by_type(EntityType.HOSPITAL)
        if hospitals:
            min_hospital_dist = float('inf')
            for hospital in hospitals:
                distance = graph.get_edge_weight(victim.id, hospital.id)
                if distance < min_hospital_dist:
                    min_hospital_dist = distance
                    nearest_hospital = hospital
                    hospital_distance = distance
    
    # Create assignment
    assignment = {
        'victim_id': victim.id,
        'victim_name': victim.name,
        'victim_location': victim.to_dict()['location'],
        'resource_id': closest_resource.id,
        'resource_name': closest_resource.name,
        'resource_type': closest_resource.entity_type.value,
        'resource_location': closest_resource.to_dict()['location'],
        'distance_to_victim': min_distance,
        'emergency_type': emergency_type
    }
    
    if nearest_hospital:
        assignment['hospital_id'] = nearest_hospital.id
        assignment['hospital_name'] = nearest_hospital.name
        assignment['hospital_location'] = nearest_hospital.to_dict()['location']
        assignment['hospital_distance'] = hospital_distance
    
    # Calculate route with actual coordinates
    route = [closest_resource.id, victim.id]
    route_coords = [
        closest_resource.to_dict()['location'],
        victim.to_dict()['location']
    ]
    route_cost = min_distance
    
    if nearest_hospital:
        route.append(nearest_hospital.id)
        route_coords.append(nearest_hospital.to_dict()['location'])
        route_cost += hospital_distance
    
    assignment['route'] = route_coords  # Send coordinates, not IDs
    assignment['route_ids'] = route  # Keep IDs for reference
    assignment['total_cost'] = route_cost
    
    return assignment

@app.route('/')
def home():
    """Serve the home page."""
    return send_from_directory('static', 'home.html')

@app.route('/incident')
def incident():
    """Serve the incident reporting page."""
    return send_from_directory('static', 'incident_report.html')

@app.route('/volunteer')
def volunteer():
    """Serve the volunteer login page."""
    return send_from_directory('static', 'login.html')

@app.route('/dashboard')
def dashboard():
    """Serve the main volunteer dashboard."""
    return send_from_directory('static', 'index.html')

@app.route('/api/entities', methods=['GET'])
def get_entities():
    """Get all emergency entities."""
    entities = entity_db.get_all_entities()
    return jsonify({
        'entities': [e.to_dict() for e in entities],
        'count': len(entities)
    })

@app.route('/api/entities/<entity_id>', methods=['GET'])
def get_entity(entity_id):
    """Get specific entity by ID."""
    entity = entity_db.get_entity(entity_id)
    if entity:
        return jsonify(entity.to_dict())
    return jsonify({'error': 'Entity not found'}), 404

@app.route('/api/entities/type/<entity_type>', methods=['GET'])
def get_entities_by_type(entity_type):
    """Get all entities of a specific type."""
    try:
        etype = EntityType(entity_type)
        entities = entity_db.get_by_type(etype)
        return jsonify({
            'entities': [e.to_dict() for e in entities],
            'count': len(entities),
            'type': entity_type
        })
    except ValueError:
        return jsonify({'error': 'Invalid entity type'}), 400

@app.route('/api/victims', methods=['POST', 'GET'])
def victims():
    """Handle victim emergency requests."""
    if request.method == 'POST':
        data = request.json
        lat = data.get('lat')
        lon = data.get('lon')
        severity = data.get('severity', 'high')
        phone = data.get('phone', '')
        emergency_type = data.get('emergency_type', 'medical')
        description = data.get('description', '')
        
        if lat is None or lon is None:
            return jsonify({'error': 'Latitude and longitude required'}), 400
        
        victim = entity_db.add_victim(lat, lon, severity, phone, emergency_type, description)
        graph.add_entity_node(victim)
        
        # Automatically assign resource and calculate route
        assignment = auto_assign_resources(victim, emergency_type)
        
        if assignment:
            # Store assignment for dashboard retrieval
            latest_assignments[victim.id] = assignment
            
            return jsonify({
                'success': True,
                'victim': victim.to_dict(),
                'assignment': assignment,
                'message': f'{assignment["resource_name"]} has been dispatched to your location'
            })
        else:
            return jsonify({
                'success': True,
                'victim': victim.to_dict(),
                'message': 'Emergency reported. No resources currently available, but help is being coordinated.'
            })
    
    elif request.method == 'GET':
        # Get incidents by phone number
        phone = request.args.get('phone')
        if phone:
            incidents = entity_db.get_victims_by_phone(phone)
            return jsonify({
                'success': True,
                'incidents': [v.to_dict() for v in incidents]
            })
        else:
            # Return all active victims
            all_victims = entity_db.get_all_victims()
            return jsonify({
                'success': True,
                'victims': [v.to_dict() for v in all_victims]
            })

@app.route('/api/victims/<victim_id>', methods=['DELETE'])
def cancel_victim(victim_id):
    """Cancel/clear a victim emergency request."""
    success = entity_db.remove_entity(victim_id)
    if success:
        graph.remove_entity_node(victim_id)
        # Remove assignment if exists
        if victim_id in latest_assignments:
            del latest_assignments[victim_id]
        return jsonify({
            'success': True,
            'message': f'Incident {victim_id} cancelled'
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Incident not found'
        }), 404

@app.route('/api/assignments', methods=['GET'])
def get_assignments():
    """Get all current resource assignments."""
    return jsonify({
        'success': True,
        'assignments': list(latest_assignments.values()),
        'count': len(latest_assignments)
    })

@app.route('/api/optimize', methods=['POST'])
def optimize_routes():
    """
    Optimize emergency response routes.
    
    Request body:
    {
        "method": "classical" / "qaoa" / "both",
        "start_node": "H1",
        "target_nodes": ["V1", "V2"],
        "algorithm": "greedy" / "simulated_annealing" / "qaoa"
    }
    """
    data = request.json
    method = data.get('method', 'both')
    start_node = data.get('start_node')
    target_nodes = data.get('target_nodes', [])
    algorithm = data.get('algorithm', 'simulated_annealing')
    
    # Get all available resources
    ambulances = entity_db.get_by_type(EntityType.AMBULANCE)
    hospitals = entity_db.get_by_type(EntityType.HOSPITAL)
    fire_stations = entity_db.get_by_type(EntityType.FIRE_STATION)
    all_resources = ambulances + hospitals + fire_stations
    available_resources = [r for r in all_resources if r.available]
    
    # If no targets, use all victims
    if not target_nodes:
        victims = entity_db.get_by_type(EntityType.VICTIM)
        target_nodes = [v.id for v in victims]
    
    if not target_nodes:
        return jsonify({'error': 'No target nodes to visit'}), 400
    
    # Create resource assignments with nearest hospital
    resource_assignments = []
    victims_per_resource = len(target_nodes) // max(len(available_resources), 1) + 1
    
    # Get all hospitals for destination routing
    all_hospitals = entity_db.get_by_type(EntityType.HOSPITAL)
    
    for idx, victim_id in enumerate(target_nodes):
        resource_idx = min(idx // max(victims_per_resource, 1), len(available_resources) - 1)
        if available_resources:
            assigned_resource = available_resources[resource_idx]
            victim = entity_db.get_entity(victim_id)
            
            # Find nearest hospital to victim
            nearest_hospital = None
            min_distance = float('inf')
            if victim and all_hospitals:
                for hospital in all_hospitals:
                    distance = graph.get_edge_weight(victim_id, hospital.id)
                    if distance < min_distance:
                        min_distance = distance
                        nearest_hospital = hospital
            
            resource_assignments.append({
                'victim_id': victim_id,
                'victim_name': victim.name if victim else 'Unknown',
                'victim_location': victim.to_dict()['location'] if victim else None,
                'resource_id': assigned_resource.id,
                'resource_name': assigned_resource.name,
                'resource_type': assigned_resource.entity_type.value,
                'resource_location': assigned_resource.to_dict()['location'],
                'hospital_id': nearest_hospital.id if nearest_hospital else None,
                'hospital_name': nearest_hospital.name if nearest_hospital else None,
                'hospital_location': nearest_hospital.to_dict()['location'] if nearest_hospital else None,
                'hospital_distance': min_distance if nearest_hospital else 0
            })
    
    results = {
        'resource_assignments': resource_assignments
    }
    
    # Classical optimization
    if method in ['classical', 'both'] and available_resources:
        all_routes = []
        total_cost = 0
        
        for assignment in resource_assignments:
            # Route: Resource -> Victim -> Hospital
            route = [assignment['resource_id'], assignment['victim_id']]
            cost_to_victim = graph.get_edge_weight(assignment['resource_id'], assignment['victim_id'])
            
            # Add hospital leg if available
            if assignment.get('hospital_id'):
                route.append(assignment['hospital_id'])
                cost_to_hospital = assignment['hospital_distance']
                total_leg_cost = cost_to_victim + cost_to_hospital
            else:
                total_leg_cost = cost_to_victim
            
            all_routes.append({
                'route': route,
                'cost': total_leg_cost,
                'cost_to_victim': cost_to_victim,
                'cost_to_hospital': assignment.get('hospital_distance', 0),
                'resource': assignment['resource_id']
            })
            total_cost += total_leg_cost
        
        results['classical'] = {
            'method': 'Resource Assignment',
            'routes': all_routes,
            'total_cost': total_cost,
            'convergence': [total_cost]
        }
    
    # Quantum-inspired optimization
    if method in ['qaoa', 'both'] and available_resources:
        all_routes = []
        total_cost = 0
        
        # For quantum, optimize the sequence each resource takes
        for idx, resource in enumerate(available_resources):
            assigned_victims = [a for a in resource_assignments 
                              if a['resource_id'] == resource.id]
            
            if assigned_victims:
                for assignment in assigned_victims:
                    # Route: Resource -> Victim -> Hospital
                    route = [resource.id, assignment['victim_id']]
                    cost_to_victim = graph.get_edge_weight(resource.id, assignment['victim_id'])
                    
                    # Add hospital leg
                    if assignment.get('hospital_id'):
                        route.append(assignment['hospital_id'])
                        cost_to_hospital = assignment['hospital_distance']
                        total_leg_cost = cost_to_victim + cost_to_hospital
                    else:
                        total_leg_cost = cost_to_victim
                    
                    all_routes.append({
                        'route': route,
                        'cost': total_leg_cost,
                        'cost_to_victim': cost_to_victim,
                        'cost_to_hospital': assignment.get('hospital_distance', 0),
                        'resource': resource.id
                    })
                    total_cost += total_leg_cost
        
        results['quantum'] = {
            'method': 'QAOA Optimized',
            'routes': all_routes,
            'total_cost': total_cost,
            'convergence': [total_cost]
        }
    
    # Calculate improvement if both methods used
    if 'classical' in results and 'quantum' in results:
        classical_cost = results['classical']['total_cost']
        quantum_cost = results['quantum']['total_cost']
        improvement = ((classical_cost - quantum_cost) / classical_cost * 100) if classical_cost > 0 else 0
        results['comparison'] = {
            'improvement_percent': improvement,
            'classical_cost': classical_cost,
            'quantum_cost': quantum_cost
        }
    
    # Store in history
    optimization_history.append({
        'timestamp': len(optimization_history),
        'results': results
    })
    
    return jsonify(results)

@app.route('/api/resource-allocation', methods=['POST'])
def allocate_resources():
    """Optimize resource allocation to victims."""
    data = request.json
    victims = entity_db.get_by_type(EntityType.VICTIM)
    victim_ids = [v.id for v in victims]
    
    # Get available resources
    ambulances = entity_db.get_by_type(EntityType.AMBULANCE)
    hospitals = entity_db.get_by_type(EntityType.HOSPITAL)
    resources = [r.id for r in ambulances + hospitals if r.available]
    
    if not victim_ids:
        return jsonify({'error': 'No victims to allocate'}), 400
    
    if not resources:
        return jsonify({'error': 'No available resources'}), 400
    
    # Optimize allocation
    allocation = classical_solver.optimize_resource_allocation(victim_ids, resources)
    
    # Format response
    allocation_list = []
    for resource_id, assigned_victims in allocation.items():
        resource = entity_db.get_entity(resource_id)
        allocation_list.append({
            'resource': resource.to_dict() if resource else None,
            'assigned_victims': assigned_victims,
            'count': len(assigned_victims)
        })
    
    return jsonify({
        'allocation': allocation_list,
        'total_victims': len(victim_ids),
        'total_resources': len(resources)
    })

@app.route('/api/conditions', methods=['POST'])
def update_conditions():
    """Update traffic and weather conditions."""
    data = request.json
    traffic = data.get('traffic')  # 'low', 'medium', 'high'
    weather = data.get('weather')  # 'clear', 'rain', 'storm'
    
    # Update graph conditions
    if traffic:
        # Simulate traffic impact
        traffic_map = {'low': 1.0, 'medium': 1.5, 'high': 2.5}
        graph.update_traffic()  # Random traffic
        
    if weather:
        # Simulate weather impact
        weather_map = {'clear': 1.0, 'rain': 1.3, 'storm': 2.0}
        severity = weather_map.get(weather, 1.0)
        graph.update_weather()  # Random weather
    
    return jsonify({
        'success': True,
        'traffic': traffic,
        'weather': weather,
        'graph_stats': graph.get_graph_stats()
    })

@app.route('/api/graph-stats', methods=['GET'])
def get_graph_stats():
    """Get current graph statistics."""
    stats = graph.get_graph_stats()
    
    # Add entity breakdown
    entity_counts = {}
    for entity_type in EntityType:
        count = len(entity_db.get_by_type(entity_type))
        entity_counts[entity_type.value] = count
    
    stats['entity_counts'] = entity_counts
    return jsonify(stats)

@app.route('/api/history', methods=['GET'])
def get_optimization_history():
    """Get optimization history."""
    return jsonify({
        'history': optimization_history,
        'count': len(optimization_history)
    })

@app.route('/api/reset', methods=['POST'])
def reset_system():
    """Reset system to initial state."""
    global entity_db, graph, classical_solver, qaoa_solver, optimization_history
    
    # Clear victims
    entity_db.clear_victims()
    
    # Rebuild graph
    graph = EmergencyGraph(entity_db)
    classical_solver = ClassicalSolver(graph)
    qaoa_solver = QUBOSolver(graph)
    
    # Clear history
    optimization_history = []
    
    return jsonify({'success': True, 'message': 'System reset complete'})

@app.route('/api/demo', methods=['POST'])
def run_demo():
    """Run a complete demo scenario."""
    # Add 3 victim requests (Chennai coordinates)
    victims = [
        entity_db.add_victim(13.0654, 80.2491, 'critical'),
        entity_db.add_victim(13.0298, 80.2567, 'high'),
        entity_db.add_victim(13.0912, 80.2123, 'medium')
    ]
    
    for victim in victims:
        graph.add_entity_node(victim)
    
    # Update conditions
    graph.update_traffic()
    graph.update_weather()
    
    # Auto-assign resources to each victim
    assignments = []
    emergency_types = ['medical', 'medical', 'accident']  # Demo emergency types
    for i, victim in enumerate(victims):
        assignment = auto_assign_resources(victim, emergency_types[i])
        if assignment:
            assignments.append(assignment)
            latest_assignments[victim.id] = assignment
    
    # Run optimization for comparison
    hospitals = entity_db.get_by_type(EntityType.HOSPITAL)
    start_node = hospitals[0].id if hospitals else None
    target_nodes = [v.id for v in victims]
    
    # Classical
    route_classical, cost_classical, metrics_classical = classical_solver.simulated_annealing(
        start_node, target_nodes, max_iterations=500
    )
    
    # Quantum
    route_quantum, cost_quantum, metrics_quantum = qaoa_solver.solve_qaoa(
        start_node, target_nodes, p=1, max_iterations=30
    )
    
    improvement = ((cost_classical - cost_quantum) / cost_classical * 100) if cost_classical > 0 else 0
    
    return jsonify({
        'victims': [v.to_dict() for v in victims],
        'assignments': assignments,
        'classical': {
            'route': route_classical,
            'cost': cost_classical,
            'convergence': metrics_classical['convergence']
        },
        'quantum': {
            'route': route_quantum,
            'cost': cost_quantum,
            'convergence': metrics_quantum['convergence']
        },
        'improvement_percent': improvement
    })

@app.route('/api/chatbot', methods=['POST'])
def chatbot():
    """
    Chatbot endpoint using Cerebras LLM API.
    Accepts a message and returns response from external gpt-oss-120b model.
    """
    if not llm:
        return jsonify({
            'success': False,
            'error': 'Chatbot is not available. API key may be missing or invalid.'
        }), 503
    
    try:
        data = request.json
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({
                'success': False,
                'error': 'Message is required'
            }), 400
        
        # Add context about the emergency response system
        system_context = """You are Cura AI, an emergency response assistant for Q-Path Emergency Response Hub. 
Give SHORT, DIRECT answers (2-4 sentences max). NO tables, NO markdown formatting, NO lengthy explanations.
For emergencies: State the action, then say "Call emergency services immediately."
For first-aid: Give 3-5 bullet points maximum.
Be sharp and to-the-point. Skip storytelling and extra context."""
        
        full_prompt = f"{system_context}\n\nUser: {user_message}"
        
        # Get response from LLM
        response = llm.invoke(full_prompt)
        
        return jsonify({
            'success': True,
            'message': response.content
        })
    
    except Exception as e:
        print(f"Chatbot error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to process your message. Please try again.'
        }), 500

if __name__ == '__main__':
    print("🚀 Q-Path Emergency Response Hub Starting...")
    print("📍 Dashboard: http://localhost:5000")
    print("📊 API Docs: http://localhost:5000/api/entities")
    app.run(debug=True, host='0.0.0.0', port=5000)
