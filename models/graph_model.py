"""
Graph model for emergency routing.
Weighted graph with distance, traffic, and weather factors.
"""

import networkx as nx
import numpy as np
from typing import List, Dict, Tuple, Optional
from geopy.distance import geodesic
from models.entities import EmergencyEntity, EmergencyDatabase
import random

class EmergencyGraph:
    """Graph representation of emergency response network."""
    
    def __init__(self, entity_db: EmergencyDatabase):
        self.entity_db = entity_db
        self.graph = nx.Graph()
        self.traffic_multipliers = {}  # Edge -> traffic multiplier
        self.weather_multipliers = {}  # Edge -> weather severity multiplier
        self.base_distances = {}  # Edge -> base distance in km
        self._build_graph()
    
    def _build_graph(self):
        """Build complete graph from all entities."""
        entities = self.entity_db.get_all_entities()
        
        # Add all entities as nodes
        for entity in entities:
            self.graph.add_node(
                entity.id,
                entity=entity,
                pos=(entity.location.lat, entity.location.lon)
            )
        
        # Add edges between all pairs (complete graph)
        for i, entity1 in enumerate(entities):
            for entity2 in entities[i+1:]:
                distance = self._calculate_distance(entity1, entity2)
                edge = tuple(sorted([entity1.id, entity2.id]))
                
                self.base_distances[edge] = distance
                self.traffic_multipliers[edge] = 1.0  # Default no traffic
                self.weather_multipliers[edge] = 1.0  # Default good weather
                
                weight = self._calculate_edge_weight(edge)
                self.graph.add_edge(entity1.id, entity2.id, weight=weight, distance=distance)
    
    def _calculate_distance(self, entity1: EmergencyEntity, entity2: EmergencyEntity) -> float:
        """Calculate geodesic distance between two entities in km."""
        coord1 = (entity1.location.lat, entity1.location.lon)
        coord2 = (entity2.location.lat, entity2.location.lon)
        return geodesic(coord1, coord2).kilometers
    
    def _calculate_edge_weight(self, edge: Tuple[str, str]) -> float:
        """Calculate edge weight: distance × traffic × weather."""
        base_dist = self.base_distances.get(edge, 1.0)
        traffic = self.traffic_multipliers.get(edge, 1.0)
        weather = self.weather_multipliers.get(edge, 1.0)
        return base_dist * traffic * weather
    
    def update_traffic(self, traffic_data: Optional[Dict] = None):
        """Update traffic multipliers (1.0 = no traffic, 3.0 = heavy traffic)."""
        if traffic_data:
            # Use provided traffic data
            for edge, multiplier in traffic_data.items():
                edge_tuple = tuple(sorted(edge)) if isinstance(edge, (list, tuple)) else edge
                if edge_tuple in self.traffic_multipliers:
                    self.traffic_multipliers[edge_tuple] = multiplier
        else:
            # Simulate random traffic conditions
            for edge in self.base_distances.keys():
                # Random traffic: 1.0 to 2.5
                self.traffic_multipliers[edge] = random.uniform(1.0, 2.5)
        
        self._update_edge_weights()
    
    def update_weather(self, weather_data: Optional[Dict] = None):
        """Update weather severity multipliers (1.0 = clear, 2.0 = severe)."""
        if weather_data:
            # Use provided weather data
            for edge, multiplier in weather_data.items():
                edge_tuple = tuple(sorted(edge)) if isinstance(edge, (list, tuple)) else edge
                if edge_tuple in self.weather_multipliers:
                    self.weather_multipliers[edge_tuple] = multiplier
        else:
            # Simulate weather conditions
            severity = random.choice([1.0, 1.2, 1.5, 1.8])  # Uniform weather for all edges
            for edge in self.base_distances.keys():
                self.weather_multipliers[edge] = severity
        
        self._update_edge_weights()
    
    def _update_edge_weights(self):
        """Recalculate all edge weights after traffic/weather update."""
        for edge in self.base_distances.keys():
            weight = self._calculate_edge_weight(edge)
            node1, node2 = edge
            if self.graph.has_edge(node1, node2):
                self.graph[node1][node2]['weight'] = weight
    
    def add_entity_node(self, entity: EmergencyEntity):
        """Add new entity as a node and connect to all existing nodes."""
        # Add node
        self.graph.add_node(
            entity.id,
            entity=entity,
            pos=(entity.location.lat, entity.location.lon)
        )
        
        # Connect to all existing nodes
        for other_id in self.graph.nodes():
            if other_id != entity.id:
                other_entity = self.entity_db.get_entity(other_id)
                if other_entity:
                    distance = self._calculate_distance(entity, other_entity)
                    edge = tuple(sorted([entity.id, other_id]))
                    
                    self.base_distances[edge] = distance
                    self.traffic_multipliers[edge] = 1.0
                    self.weather_multipliers[edge] = 1.0
                    
                    weight = self._calculate_edge_weight(edge)
                    self.graph.add_edge(entity.id, other_id, weight=weight, distance=distance)
    
    def remove_entity_node(self, entity_id: str):
        """Remove entity node and all its edges."""
        if entity_id in self.graph:
            # Remove associated edges from tracking dicts
            edges_to_remove = []
            for edge in list(self.base_distances.keys()):
                if entity_id in edge:
                    edges_to_remove.append(edge)
            
            for edge in edges_to_remove:
                self.base_distances.pop(edge, None)
                self.traffic_multipliers.pop(edge, None)
                self.weather_multipliers.pop(edge, None)
            
            # Remove node from graph
            self.graph.remove_node(entity_id)
    
    def get_shortest_path(self, source: str, target: str) -> Tuple[List[str], float]:
        """Get shortest path between two nodes using current weights."""
        try:
            path = nx.shortest_path(self.graph, source, target, weight='weight')
            length = nx.shortest_path_length(self.graph, source, target, weight='weight')
            return path, length
        except nx.NetworkXNoPath:
            return [], float('inf')
    
    def get_neighbors(self, node_id: str) -> List[str]:
        """Get all neighbors of a node."""
        return list(self.graph.neighbors(node_id))
    
    def get_edge_weight(self, node1: str, node2: str) -> float:
        """Get weight of edge between two nodes."""
        if self.graph.has_edge(node1, node2):
            return self.graph[node1][node2]['weight']
        return float('inf')
    
    def get_all_nodes(self) -> List[str]:
        """Get all node IDs."""
        return list(self.graph.nodes())
    
    def get_graph_stats(self) -> Dict:
        """Get graph statistics."""
        return {
            'num_nodes': self.graph.number_of_nodes(),
            'num_edges': self.graph.number_of_edges(),
            'avg_degree': sum(dict(self.graph.degree()).values()) / self.graph.number_of_nodes() if self.graph.number_of_nodes() > 0 else 0,
            'density': nx.density(self.graph)
        }
