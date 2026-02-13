"""
Classical optimization solvers for emergency routing.
Includes Greedy TSP and Simulated Annealing baselines.
"""

import numpy as np
import networkx as nx
from typing import List, Tuple, Dict
import random
import math
from models.graph_model import EmergencyGraph

class ClassicalSolver:
    """Classical optimization methods for routing."""
    
    def __init__(self, graph: EmergencyGraph):
        self.graph = graph
    
    def greedy_tsp(self, start_node: str, nodes_to_visit: List[str]) -> Tuple[List[str], float]:
        """
        Greedy TSP: Always visit the nearest unvisited node.
        
        Args:
            start_node: Starting node ID
            nodes_to_visit: List of node IDs to visit
        
        Returns:
            Tuple of (route, total_cost)
        """
        if not nodes_to_visit:
            return [start_node], 0.0
        
        route = [start_node]
        unvisited = set(nodes_to_visit)
        current = start_node
        total_cost = 0.0
        
        while unvisited:
            # Find nearest unvisited node
            nearest = None
            min_dist = float('inf')
            
            for node in unvisited:
                dist = self.graph.get_edge_weight(current, node)
                if dist < min_dist:
                    min_dist = dist
                    nearest = node
            
            if nearest is None:
                break
            
            route.append(nearest)
            total_cost += min_dist
            unvisited.remove(nearest)
            current = nearest
        
        return route, total_cost
    
    def simulated_annealing(self, start_node: str, nodes_to_visit: List[str], 
                           max_iterations: int = 1000, 
                           initial_temp: float = 100.0,
                           cooling_rate: float = 0.995) -> Tuple[List[str], float, Dict]:
        """
        Simulated Annealing for TSP optimization.
        
        Args:
            start_node: Starting node ID
            nodes_to_visit: List of node IDs to visit
            max_iterations: Maximum number of iterations
            initial_temp: Initial temperature
            cooling_rate: Temperature cooling rate
        
        Returns:
            Tuple of (best_route, best_cost, metrics)
        """
        if not nodes_to_visit:
            return [start_node], 0.0, {'iterations': 0, 'convergence': []}
        
        # Initialize with random route
        current_route = [start_node] + random.sample(nodes_to_visit, len(nodes_to_visit))
        current_cost = self._calculate_route_cost(current_route)
        
        best_route = current_route.copy()
        best_cost = current_cost
        
        temperature = initial_temp
        convergence = [current_cost]
        
        for iteration in range(max_iterations):
            # Generate neighbor solution by swapping two nodes (excluding start)
            new_route = current_route.copy()
            if len(new_route) > 2:
                i, j = random.sample(range(1, len(new_route)), 2)
                new_route[i], new_route[j] = new_route[j], new_route[i]
            
            new_cost = self._calculate_route_cost(new_route)
            
            # Accept or reject new solution
            delta = new_cost - current_cost
            if delta < 0 or random.random() < math.exp(-delta / temperature):
                current_route = new_route
                current_cost = new_cost
                
                if current_cost < best_cost:
                    best_route = current_route.copy()
                    best_cost = current_cost
            
            # Cool down
            temperature *= cooling_rate
            convergence.append(best_cost)
            
            # Early stopping if temperature is very low
            if temperature < 0.1:
                break
        
        metrics = {
            'iterations': iteration + 1,
            'final_temperature': temperature,
            'convergence': convergence
        }
        
        return best_route, best_cost, metrics
    
    def nearest_neighbor_multistart(self, nodes: List[str], num_starts: int = 5) -> Tuple[List[str], float]:
        """
        Nearest Neighbor with multiple starting points.
        
        Args:
            nodes: All nodes to visit
            num_starts: Number of different starting points to try
        
        Returns:
            Tuple of (best_route, best_cost)
        """
        if not nodes:
            return [], 0.0
        
        best_route = None
        best_cost = float('inf')
        
        # Try different starting points
        start_nodes = random.sample(nodes, min(num_starts, len(nodes)))
        
        for start in start_nodes:
            other_nodes = [n for n in nodes if n != start]
            route, cost = self.greedy_tsp(start, other_nodes)
            
            if cost < best_cost:
                best_cost = cost
                best_route = route
        
        return best_route, best_cost
    
    def _calculate_route_cost(self, route: List[str]) -> float:
        """Calculate total cost of a route."""
        if len(route) < 2:
            return 0.0
        
        total_cost = 0.0
        for i in range(len(route) - 1):
            cost = self.graph.get_edge_weight(route[i], route[i+1])
            if cost == float('inf'):
                return float('inf')
            total_cost += cost
        
        return total_cost
    
    def optimize_resource_allocation(self, victims: List[str], resources: List[str]) -> Dict:
        """
        Optimize allocation of resources to victims using greedy assignment.
        
        Args:
            victims: List of victim node IDs
            resources: List of resource node IDs (ambulances, hospitals, etc.)
        
        Returns:
            Dictionary mapping resource to assigned victims
        """
        allocation = {resource: [] for resource in resources}
        unassigned = set(victims)
        
        # Greedy assignment: each resource takes nearest victim
        for resource in resources:
            if not unassigned:
                break
            
            nearest = min(unassigned, 
                         key=lambda v: self.graph.get_edge_weight(resource, v))
            allocation[resource].append(nearest)
            unassigned.remove(nearest)
        
        # Assign remaining victims to nearest resource
        for victim in unassigned:
            nearest_resource = min(resources,
                                  key=lambda r: self.graph.get_edge_weight(r, victim))
            allocation[nearest_resource].append(victim)
        
        return allocation
