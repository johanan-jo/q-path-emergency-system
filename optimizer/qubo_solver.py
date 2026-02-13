"""
QUBO formulation and QAOA solver for emergency routing.
Quantum-inspired optimization using Qiskit.
"""

import numpy as np
from typing import List, Tuple, Dict, Optional
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
from qiskit_aer import AerSimulator
from qiskit.primitives import Sampler
from scipy.optimize import minimize
from models.graph_model import EmergencyGraph
import time

class QUBOSolver:
    """QUBO formulation and QAOA solver for routing optimization."""
    
    def __init__(self, graph: EmergencyGraph):
        self.graph = graph
        self.simulator = AerSimulator()
    
    def formulate_qubo(self, start_node: str, nodes_to_visit: List[str], 
                       penalty: float = 100.0) -> Tuple[np.ndarray, Dict]:
        """
        Formulate routing problem as QUBO.
        
        Variables: x_i_t = 1 if node i is visited at time t
        
        Objective:
        - Minimize sum of edge weights in tour
        - Constraints via penalties:
          * Each node visited exactly once
          * Each time step has exactly one node
          * Valid tour connectivity
        
        Args:
            start_node: Starting node ID
            nodes_to_visit: Nodes that must be visited
            penalty: Constraint penalty weight
        
        Returns:
            Tuple of (QUBO matrix, variable mapping)
        """
        all_nodes = [start_node] + nodes_to_visit
        n = len(all_nodes)
        
        # Variable mapping: (node_idx, time_step) -> variable_idx
        var_map = {}
        idx = 0
        for i in range(n):
            for t in range(n):
                var_map[(i, t)] = idx
                idx += 1
        
        # Initialize QUBO matrix (symmetric)
        num_vars = n * n
        Q = np.zeros((num_vars, num_vars))
        
        # 1. Objective: minimize tour length
        for t in range(n - 1):
            for i in range(n):
                for j in range(n):
                    if i != j:
                        weight = self.graph.get_edge_weight(all_nodes[i], all_nodes[j])
                        if weight != float('inf'):
                            var_i_t = var_map[(i, t)]
                            var_j_t1 = var_map[(j, t + 1)]
                            Q[var_i_t, var_j_t1] += weight / 2
                            Q[var_j_t1, var_i_t] += weight / 2
        
        # 2. Constraint: Each node visited exactly once
        for i in range(n):
            for t1 in range(n):
                var1 = var_map[(i, t1)]
                Q[var1, var1] += -penalty  # Linear term
                
                for t2 in range(t1 + 1, n):
                    var2 = var_map[(i, t2)]
                    Q[var1, var2] += penalty
                    Q[var2, var1] += penalty
        
        # 3. Constraint: Each time step has exactly one node
        for t in range(n):
            for i1 in range(n):
                var1 = var_map[(i1, t)]
                Q[var1, var1] += -penalty  # Linear term
                
                for i2 in range(i1 + 1, n):
                    var2 = var_map[(i2, t)]
                    Q[var1, var2] += penalty
                    Q[var2, var1] += penalty
        
        # 4. Fix start node at time 0
        start_var = var_map[(0, 0)]
        Q[start_var, start_var] += -1000 * penalty  # Strong bias to be 1
        
        return Q, var_map
    
    def qaoa_circuit(self, Q: np.ndarray, gamma: float, beta: float) -> QuantumCircuit:
        """
        Build QAOA circuit for QUBO problem.
        
        Args:
            Q: QUBO matrix
            gamma: Cost Hamiltonian rotation angle
            beta: Mixer Hamiltonian rotation angle
        
        Returns:
            QAOA quantum circuit
        """
        num_qubits = Q.shape[0]
        qc = QuantumCircuit(num_qubits)
        
        # Initialize in superposition
        qc.h(range(num_qubits))
        
        # Cost Hamiltonian: exp(-i * gamma * H_C)
        for i in range(num_qubits):
            # Diagonal terms
            if Q[i, i] != 0:
                qc.rz(2 * gamma * Q[i, i], i)
            
            # Off-diagonal terms (interactions)
            for j in range(i + 1, num_qubits):
                if Q[i, j] != 0:
                    qc.cx(i, j)
                    qc.rz(2 * gamma * Q[i, j], j)
                    qc.cx(i, j)
        
        # Mixer Hamiltonian: exp(-i * beta * H_M)
        for i in range(num_qubits):
            qc.rx(2 * beta, i)
        
        # Measurement
        qc.measure_all()
        
        return qc
    
    def solve_qaoa(self, start_node: str, nodes_to_visit: List[str],
                   p: int = 1, max_iterations: int = 100) -> Tuple[List[str], float, Dict]:
        """
        Solve routing problem using QAOA.
        
        Args:
            start_node: Starting node
            nodes_to_visit: Nodes to visit
            p: Number of QAOA layers
            max_iterations: Max optimization iterations
        
        Returns:
            Tuple of (route, cost, metrics)
        """
        start_time = time.time()
        
        # Formulate QUBO
        Q, var_map = self.formulate_qubo(start_node, nodes_to_visit)
        all_nodes = [start_node] + nodes_to_visit
        n = len(all_nodes)
        
        # For small problems, use exact solver
        if Q.shape[0] <= 15:
            route, cost = self._solve_qubo_exact(Q, var_map, all_nodes)
            metrics = {
                'method': 'exact',
                'time': time.time() - start_time,
                'qubits': Q.shape[0],
                'convergence': [cost]
            }
            return route, cost, metrics
        
        # For larger problems, use QAOA with limited qubits
        # Reduce problem size by selecting subset
        if len(nodes_to_visit) > 4:
            # Use greedy + QAOA hybrid approach
            return self._solve_hybrid_qaoa(start_node, nodes_to_visit, max_iterations)
        
        # QAOA optimization
        best_route = None
        best_cost = float('inf')
        convergence = []
        
        def objective(params):
            """Objective function for QAOA parameter optimization."""
            gamma_list = params[:p]
            beta_list = params[p:]
            
            # Build QAOA circuit
            qc = QuantumCircuit(Q.shape[0])
            qc.h(range(Q.shape[0]))
            
            for layer in range(p):
                # Apply cost Hamiltonian
                for i in range(Q.shape[0]):
                    if Q[i, i] != 0:
                        qc.rz(2 * gamma_list[layer] * Q[i, i], i)
                    for j in range(i + 1, Q.shape[0]):
                        if Q[i, j] != 0:
                            qc.cx(i, j)
                            qc.rz(2 * gamma_list[layer] * Q[i, j], j)
                            qc.cx(i, j)
                
                # Apply mixer Hamiltonian
                for i in range(Q.shape[0]):
                    qc.rx(2 * beta_list[layer], i)
            
            qc.measure_all()
            
            # Execute circuit
            job = self.simulator.run(qc, shots=1024)
            result = job.result()
            counts = result.get_counts()
            
            # Calculate expectation value
            expectation = 0
            for bitstring, count in counts.items():
                x = np.array([int(b) for b in bitstring[::-1]])
                energy = x @ Q @ x
                expectation += energy * count / 1024
            
            convergence.append(expectation)
            return expectation
        
        # Optimize QAOA parameters
        initial_params = np.random.uniform(0, 2 * np.pi, 2 * p)
        result = minimize(objective, initial_params, method='COBYLA',
                         options={'maxiter': max_iterations})
        
        # Get best solution from final measurement
        optimal_params = result.x
        gamma_opt = optimal_params[:p]
        beta_opt = optimal_params[p:]
        
        qc = QuantumCircuit(Q.shape[0])
        qc.h(range(Q.shape[0]))
        for layer in range(p):
            for i in range(Q.shape[0]):
                if Q[i, i] != 0:
                    qc.rz(2 * gamma_opt[layer] * Q[i, i], i)
                for j in range(i + 1, Q.shape[0]):
                    if Q[i, j] != 0:
                        qc.cx(i, j)
                        qc.rz(2 * gamma_opt[layer] * Q[i, j], j)
                        qc.cx(i, j)
            for i in range(Q.shape[0]):
                qc.rx(2 * beta_opt[layer], i)
        qc.measure_all()
        
        job = self.simulator.run(qc, shots=2048)
        result = job.result()
        counts = result.get_counts()
        
        # Extract best valid route
        best_route, best_cost = self._extract_route_from_counts(counts, Q, var_map, all_nodes)
        
        metrics = {
            'method': 'QAOA',
            'time': time.time() - start_time,
            'qubits': Q.shape[0],
            'layers': p,
            'iterations': len(convergence),
            'convergence': convergence
        }
        
        return best_route, best_cost, metrics
    
    def _solve_qubo_exact(self, Q: np.ndarray, var_map: Dict, 
                          all_nodes: List[str]) -> Tuple[List[str], float]:
        """Solve QUBO exactly by enumerating all valid tours."""
        n = len(all_nodes)
        best_cost = float('inf')
        best_route = None
        
        from itertools import permutations
        
        # Try all permutations (starting with first node fixed)
        for perm in permutations(range(1, n)):
            route_indices = [0] + list(perm)
            
            # Build binary vector
            x = np.zeros(n * n)
            for t, node_idx in enumerate(route_indices):
                var_idx = var_map[(node_idx, t)]
                x[var_idx] = 1
            
            # Calculate cost
            cost = x @ Q @ x
            
            if cost < best_cost:
                best_cost = cost
                best_route = [all_nodes[i] for i in route_indices]
        
        return best_route, best_cost
    
    def _solve_hybrid_qaoa(self, start_node: str, nodes_to_visit: List[str],
                           max_iterations: int) -> Tuple[List[str], float, Dict]:
        """Hybrid approach: use greedy clustering + QAOA for small clusters."""
        # For now, fall back to greedy for large problems
        # In production, would implement hierarchical QAOA
        from optimizer.classical_solver import ClassicalSolver
        solver = ClassicalSolver(self.graph)
        route, cost = solver.greedy_tsp(start_node, nodes_to_visit)
        
        metrics = {
            'method': 'Hybrid (Greedy)',
            'time': 0.0,
            'qubits': 0,
            'convergence': [cost]
        }
        
        return route, cost, metrics
    
    def _extract_route_from_counts(self, counts: Dict, Q: np.ndarray,
                                   var_map: Dict, all_nodes: List[str]) -> Tuple[List[str], float]:
        """Extract best valid route from measurement counts."""
        n = len(all_nodes)
        best_route = None
        best_cost = float('inf')
        
        for bitstring, count in counts.items():
            x = np.array([int(b) for b in bitstring[::-1]])
            
            # Try to reconstruct route
            route_indices = []
            for t in range(n):
                for i in range(n):
                    if x[var_map[(i, t)]] == 1:
                        route_indices.append(i)
                        break
            
            if len(route_indices) == n and len(set(route_indices)) == n:
                # Valid route
                route = [all_nodes[i] for i in route_indices]
                cost = x @ Q @ x
                
                if cost < best_cost:
                    best_cost = cost
                    best_route = route
        
        # If no valid route found, use greedy
        if best_route is None:
            from optimizer.classical_solver import ClassicalSolver
            solver = ClassicalSolver(self.graph)
            best_route, _ = solver.greedy_tsp(start_node, [n for n in all_nodes if n != start_node])
            best_cost = self._calculate_route_cost(best_route)
        
        return best_route, best_cost
    
    def _calculate_route_cost(self, route: List[str]) -> float:
        """Calculate actual route cost using graph weights."""
        if len(route) < 2:
            return 0.0
        
        total = 0.0
        for i in range(len(route) - 1):
            total += self.graph.get_edge_weight(route[i], route[i + 1])
        return total
