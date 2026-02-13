// Q-Path Emergency Response Hub - Frontend JavaScript

const API_BASE = 'http://localhost:5000/api';

// Global state
let map;
let markers = {};
let routeLayer;
let routingControls = [];
let currentViewMode = 'infrastructure';
let clickedLocation = null;

// Initialize application
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOMContentLoaded - Starting initialization'); // Debug
    try {
        initializeMap();
        console.log('Map initialized'); // Debug
        loadEntities();
        console.log('Loading entities'); // Debug
        updateGraphStats();
        console.log('Updating graph stats'); // Debug
        loadAndDisplayAssignments(); // Load assignments on init
        console.log('Loading assignments'); // Debug
        setInterval(updateGraphStats, 5000); // Update stats every 5 seconds
        setInterval(loadAndDisplayAssignments, 10000); // Check for new assignments every 10 seconds
        console.log('Initialization complete'); // Debug
    } catch(error) {
        console.error('Initialization error:', error); // Debug
    }
});

// Initialize Leaflet map
function initializeMap() {
    console.log('initializeMap() called'); // Debug
    try {
        // Initialize map centered on Chennai
        map = L.map('map').setView([13.0827, 80.2707], 12);
        console.log('Leaflet map created'); // Debug
        
        // Add OpenStreetMap tiles
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 19
        }).addTo(map);
        console.log('Map tiles added'); // Debug
        
        // Create custom pane for routes to ensure they appear above markers
        map.createPane('routePane');
        map.getPane('routePane').style.zIndex = 450; // Above markers (400) but below popups (600)
        console.log('Route pane created'); // Debug
        
        // Route layer for displaying optimal routes
        routeLayer = L.layerGroup().addTo(map);
        console.log('Route layer added'); // Debug
        
        // Map click handler for adding victims
        map.on('click', (e) => {
            if (currentViewMode === 'citizen') {
                clickedLocation = e.latlng;
                // Visual feedback
                L.marker([e.latlng.lat, e.latlng.lng], {
                    icon: L.divIcon({
                        className: 'temp-marker',
                        html: '📍',
                        iconSize: [30, 30]
                    })
                }).addTo(map);
            }
        });
        console.log('Map initialization complete'); // Debug
    } catch(error) {
        console.error('Map initialization error:', error); // Debug
    }
}

// Load and display assignments (routes from resources to victims)
let assignmentLayers = {}; // Track assignment polylines by victim ID

async function loadAndDisplayAssignments() {
    try {
        const response = await fetch(`${API_BASE}/assignments`);
        const data = await response.json();
        
        console.log('Assignments loaded:', data); // Debug log
        
        if (data.success) {
            // Clear old assignment layers that no longer exist
            const currentAssignmentIds = new Set(data.assignments.map(a => a.victim_id));
            Object.keys(assignmentLayers).forEach(victimId => {
                if (!currentAssignmentIds.has(victimId)) {
                    assignmentLayers[victimId].forEach(layer => routeLayer.removeLayer(layer));
                    delete assignmentLayers[victimId];
                }
            });
            
            // Add or update assignments
            for (const assignment of data.assignments) {
                console.log('Processing assignment:', assignment); // Debug log
                
                // Skip if this assignment is already displayed
                if (assignmentLayers[assignment.victim_id]) {
                    console.log('Assignment already displayed, skipping:', assignment.victim_id); // Debug log
                    continue;
                }
                
                // Draw real road routes
                await drawRealRoutes(assignment);
            }
            
            // Update status if there are active assignments
            if (data.count > 0) {
                console.log(`${data.count} active assignment(s) displayed`);
            }
        }
    } catch (error) {
        console.error('Failed to load assignments:', error);
    }
}

// Draw actual road routes using OSRM API
async function drawRealRoutes(assignment) {
    const layers = [];
    
    try {
        // Resource location → Victim location (ORANGE)
        const resourceToVictim = await fetchOSRMRoute(
            assignment.resource_location,
            assignment.victim_location
        );
        
        if (resourceToVictim && resourceToVictim.coordinates) {
            const orangeLine = L.polyline(resourceToVictim.coordinates, {
                color: '#ff6600',
                weight: 6,
                opacity: 0.8,
                pane: 'routePane',
                className: 'animated-route-line'
            });
            
            const popupContent = `
                <div class="popup-content">
                    <h4>🚨 Resource → Incident</h4>
                    <p><strong>Resource:</strong> ${assignment.resource_name}</p>
                    <p><strong>Type:</strong> ${formatEntityType(assignment.resource_type)}</p>
                    <p><strong>Distance:</strong> ${resourceToVictim.distance.toFixed(2)} km</p>
                    <p><strong>Duration:</strong> ${resourceToVictim.duration.toFixed(1)} min</p>
                </div>
            `;
            orangeLine.bindPopup(popupContent);
            orangeLine.addTo(routeLayer);
            layers.push(orangeLine);
        }
        
        // Victim location → Hospital location (GREEN) - if hospital exists
        if (assignment.hospital_location) {
            const victimToHospital = await fetchOSRMRoute(
                assignment.victim_location,
                assignment.hospital_location
            );
            
            if (victimToHospital && victimToHospital.coordinates) {
                const greenLine = L.polyline(victimToHospital.coordinates, {
                    color: '#00ff00',
                    weight: 6,
                    opacity: 0.8,
                    pane: 'routePane',
                    className: 'animated-route-line'
                });
                
                const popupContent = `
                    <div class="popup-content">
                        <h4>🏥 Incident → Hospital</h4>
                        <p><strong>Hospital:</strong> ${assignment.hospital_name}</p>
                        <p><strong>Distance:</strong> ${victimToHospital.distance.toFixed(2)} km</p>
                        <p><strong>Duration:</strong> ${victimToHospital.duration.toFixed(1)} min</p>
                    </div>
                `;
                greenLine.bindPopup(popupContent);
                greenLine.addTo(routeLayer);
                layers.push(greenLine);
            }
        }
        
        // Store layers for this assignment
        assignmentLayers[assignment.victim_id] = layers;
        
    } catch (error) {
        console.error('Error drawing real routes:', error);
    }
}

// Fetch actual road route from OSRM
async function fetchOSRMRoute(startLocation, endLocation) {
    try {
        const url = `https://router.project-osrm.org/route/v1/driving/${startLocation.lon},${startLocation.lat};${endLocation.lon},${endLocation.lat}?overview=full&geometries=geojson`;
        
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.code === 'Ok' && data.routes && data.routes.length > 0) {
            const route = data.routes[0];
            const coordinates = route.geometry.coordinates.map(coord => [coord[1], coord[0]]); // [lon, lat] to [lat, lon]
            
            return {
                coordinates: coordinates,
                distance: route.distance / 1000, // Convert to km
                duration: route.duration / 60 // Convert to minutes
            };
        }
        
        return null;
    } catch (error) {
        console.error('OSRM routing error:', error);
        return null;
    }
}


// Load all entities from backend
async function loadEntities() {
    console.log('loadEntities() called'); // Debug
    try {
        console.log('Fetching from:', `${API_BASE}/entities`); // Debug
        const response = await fetch(`${API_BASE}/entities`);
        console.log('Response status:', response.status); // Debug
        const data = await response.json();
        console.log('Entities data received:', data); // Debug
        
        // Clear existing markers
        Object.values(markers).forEach(marker => map.removeLayer(marker));
        markers = {};
        
        // Add markers for each entity
        data.entities.forEach(entity => {
            addEntityMarker(entity);
        });
        
        // Update entity counts
        updateEntityCounts(data.entities);
        
        updateStatus('Entities loaded successfully');
    } catch (error) {
        console.error('Failed to load entities:', error);
        console.error('Error details:', error.message, error.stack); // Debug
        updateStatus('Error loading entities', 'error');
    }
}

// Add marker for entity
function addEntityMarker(entity) {
    const icon = getEntityIcon(entity.type);
    const marker = L.marker([entity.location.lat, entity.location.lon], {
        icon: L.divIcon({
            className: 'entity-marker',
            html: icon,
            iconSize: [30, 30]
        })
    });
    
    // Popup with entity details
    const popupContent = `
        <div class="popup-content">
            <h4>${entity.name}</h4>
            <p><strong>Type:</strong> ${formatEntityType(entity.type)}</p>
            <p><strong>ID:</strong> ${entity.id}</p>
            <p><strong>Capacity:</strong> ${entity.capacity}</p>
            ${entity.metadata ? formatMetadata(entity.metadata) : ''}
        </div>
    `;
    marker.bindPopup(popupContent);
    marker.addTo(map);
    
    markers[entity.id] = marker;
}

// Get icon for entity type
function getEntityIcon(type) {
    const icons = {
        'hospital': '🏥',
        'fire_station': '🚒',
        'police_station': '👮',
        'lifeguard': '🏊',
        'ngo': '🏢',
        'ambulance': '🚑',
        'victim': '🆘'
    };
    return icons[type.toLowerCase()] || '📍';
}

// Format entity type
function formatEntityType(type) {
    return type.split('_').map(word => 
        word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
}

// Format metadata
function formatMetadata(metadata) {
    return Object.entries(metadata).map(([key, value]) => 
        `<p><strong>${key}:</strong> ${value}</p>`
    ).join('');
}

// Update entity counts
function updateEntityCounts(entities) {
    const counts = {
        hospital: 0,
        fire_station: 0,
        police_station: 0,
        lifeguard: 0,
        ngo: 0,
        ambulance: 0,
        victim: 0
    };
    
    entities.forEach(entity => {
        if (counts.hasOwnProperty(entity.type)) {
            counts[entity.type]++;
        }
    });
    
    document.getElementById('hospitalCount').textContent = counts.hospital;
    document.getElementById('fireCount').textContent = counts.fire_station;
    document.getElementById('ngoCount').textContent = counts.ngo;
    document.getElementById('ambulanceCount').textContent = counts.ambulance;
    document.getElementById('victimCount').textContent = counts.victim;
}

// Update view mode
function updateViewMode() {
    const viewMode = document.getElementById('viewMode').value;
    currentViewMode = viewMode;
    
    if (viewMode === 'citizen') {
        document.getElementById('emergencyPanel').style.display = 'block';
        document.getElementById('infrastructurePanel').style.display = 'none';
    } else {
        document.getElementById('emergencyPanel').style.display = 'none';
        document.getElementById('infrastructurePanel').style.display = 'block';
    }
}

// Request emergency help (citizen view)
async function requestHelp() {
    if (!clickedLocation) {
        alert('Please click on the map to select your location first');
        return;
    }
    
    const severity = document.getElementById('severity').value;
    
    try {
        const response = await fetch(`${API_BASE}/victims`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                lat: clickedLocation.lat,
                lon: clickedLocation.lng,
                severity: severity
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            addEntityMarker(data.victim);
            updateStatus('Emergency request submitted successfully!');
            clickedLocation = null;
            
            // Remove temp markers
            map.eachLayer(layer => {
                if (layer.options && layer.options.icon && 
                    layer.options.icon.options.className === 'temp-marker') {
                    map.removeLayer(layer);
                }
            });
            
            // Reload entities
            await loadEntities();
        }
    } catch (error) {
        console.error('Failed to submit emergency request:', error);
        updateStatus('Error submitting request', 'error');
    }
}

// Add random victim for testing
async function addRandomVictim() {
    const center = map.getCenter();
    const lat = center.lat + (Math.random() - 0.5) * 0.05;
    const lon = center.lng + (Math.random() - 0.5) * 0.05;
    
    try {
        const response = await fetch(`${API_BASE}/victims`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                lat: lat,
                lon: lon,
                severity: ['critical', 'high', 'medium'][Math.floor(Math.random() * 3)]
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            addEntityMarker(data.victim);
            await loadEntities();
            updateStatus('Random victim added');
        }
    } catch (error) {
        console.error('Failed to add victim:', error);
    }
}

// Update traffic and weather conditions
async function updateConditions() {
    const traffic = document.getElementById('traffic').value;
    const weather = document.getElementById('weather').value;
    
    try {
        const response = await fetch(`${API_BASE}/conditions`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ traffic, weather })
        });
        
        const data = await response.json();
        
        if (data.success) {
            updateStatus(`Conditions updated: ${traffic} traffic, ${weather} weather`);
        }
    } catch (error) {
        console.error('Failed to update conditions:', error);
    }
}

// Optimize routes
async function optimizeRoutes() {
    updateStatus('Optimizing routes...');
    
    // Show loading
    document.getElementById('optimizationResults').innerHTML = '<div class="spinner"></div>';
    
    try {
        const response = await fetch(`${API_BASE}/optimize`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                method: 'both',
                algorithm: 'simulated_annealing'
            })
        });
        
        const data = await response.json();
        
        // Display results
        displayOptimizationResults(data);
        
        // Draw routes on map with actual paths
        if (data.quantum && data.quantum.routes) {
            await drawRoutedPaths(data.quantum.routes, data.resource_assignments);
        } else if (data.classical && data.classical.routes) {
            await drawRoutedPaths(data.classical.routes, data.resource_assignments);
        }
        
        // Show comparison
        if (data.comparison) {
            displayComparison(data.comparison);
        }
        
        // Display resource assignments
        if (data.resource_assignments) {
            displayResourceAssignments(data.resource_assignments);
        }
        
        updateStatus('Optimization complete!');
    } catch (error) {
        console.error('Optimization failed:', error);
        document.getElementById('optimizationResults').innerHTML = 
            `<p class="placeholder" style="color: red;">Optimization failed: ${error.message}</p>`;
        updateStatus('Optimization failed', 'error');
    }
}

// Display optimization results
function displayOptimizationResults(data) {
    let html = '';
    
    // Show comparison if both methods available
    if (data.classical && data.quantum && data.comparison) {
        const improving = data.comparison.improvement_percent > 0;
        html += `
            <div class="result-comparison">
                <div class="comparison-badge ${improving ? 'improving' : 'degrading'}">
                    ${improving ? '✓' : '⚠'} Quantum ${improving ? 'Improvement' : 'Performance'}: ${Math.abs(data.comparison.improvement_percent).toFixed(1)}%
                </div>
            </div>
        `;
    }
    
    if (data.classical) {
        const routeCount = data.classical.routes ? data.classical.routes.length : 1;
        html += `
            <div class="result-card">
                <h4>🔵 Classical: ${data.classical.method}</h4>
                <div class="result-metric">
                    <span class="label">Total Route Cost:</span>
                    <span class="value">${data.classical.total_cost ? data.classical.total_cost.toFixed(2) : data.classical.cost.toFixed(2)} km</span>
                </div>
                <div class="result-metric">
                    <span class="label">Active Routes:</span>
                    <span class="value">${routeCount}</span>
                </div>
            </div>
        `;
    }
    
    if (data.quantum) {
        const routeCount = data.quantum.routes ? data.quantum.routes.length : 1;
        html += `
            <div class="result-card quantum">
                <h4>🔮 Quantum: ${data.quantum.method}</h4>
                <div class="result-metric">
                    <span class="label">Total Route Cost:</span>
                    <span class="value">${data.quantum.total_cost ? data.quantum.total_cost.toFixed(2) : data.quantum.cost.toFixed(2)} km</span>
                </div>
                <div class="result-metric">
                    <span class="label">Active Routes:</span>
                    <span class="value">${routeCount}</span>
                </div>
            </div>
        `;
    }
    
    document.getElementById('optimizationResults').innerHTML = html;
}

// Display comparison metrics
function displayComparison(comparison) {
    // Comparison is now shown inline with optimization results
    // This function kept for backwards compatibility
    console.log('Comparison:', comparison);
}

// Draw route on map
function drawRoute(route, color) {
    // Clear existing routes
    routeLayer.clearLayers();
    
    // Get coordinates for route nodes
    const coordinates = [];
    route.forEach(nodeId => {
        if (markers[nodeId]) {
            const latlng = markers[nodeId].getLatLng();
            coordinates.push([latlng.lat, latlng.lng]);
        }
    });
    
    if (coordinates.length > 1) {
        const polyline = L.polyline(coordinates, {
            color: color,
            weight: 4,
            opacity: 0.7,
            dashArray: '10, 10'
        });
        polyline.addTo(routeLayer);
        
        // Add direction arrows
        for (let i = 0; i < coordinates.length - 1; i++) {
            const midpoint = [
                (coordinates[i][0] + coordinates[i+1][0]) / 2,
                (coordinates[i][1] + coordinates[i+1][1]) / 2
            ];
            
            L.marker(midpoint, {
                icon: L.divIcon({
                    className: 'arrow-marker',
                    html: '➤',
                    iconSize: [20, 20]
                })
            }).addTo(routeLayer);
        }
    }
}

// Draw routed paths with actual routing
async function drawRoutedPaths(routes, assignments) {
    // Clear existing routes
    routeLayer.clearLayers();
    routingControls.forEach(control => {
        try {
            map.removeControl(control);
        } catch (e) {
            console.log('Error removing control:', e);
        }
    });
    routingControls = [];
    
    const colors = ['#ff6b00', '#00d9ff', '#ff8c00', '#c9b8a0', '#10b981'];
    const hospitalColor = '#10b981'; // Green for hospital leg
    
    // Process each route
    for (let index = 0; index < routes.length; index++) {
        const routeData = routes[index];
        const route = routeData.route;
        const color = colors[index % colors.length];
        
        if (route.length < 2) continue;
        
        // Split route into two segments: Resource->Victim and Victim->Hospital
        const hasHospital = route.length >= 3;
        
        // SEGMENT 1: Resource to Victim
        const segment1 = [route[0], route[1]];
        await drawSingleRouteSegment(segment1, color, index, 'to-victim', assignments);
        
        // SEGMENT 2: Victim to Hospital (if exists)
        if (hasHospital) {
            const segment2 = [route[1], route[2]];
            await drawSingleRouteSegment(segment2, hospitalColor, index, 'to-hospital', assignments);
        }
    }
    
    updateStatus(`${routes.length} complete route(s) visualized (pickup → hospital)`);
}

// Draw a single route segment
async function drawSingleRouteSegment(routeNodes, color, index, segmentType, assignments) {
    if (routeNodes.length < 2) return;
    
    // Get waypoints
    const waypoints = [];
    routeNodes.forEach(nodeId => {
        if (markers[nodeId]) {
            const latlng = markers[nodeId].getLatLng();
            waypoints.push([latlng.lng, latlng.lat]); // lon, lat for OSRM
        }
    });
    
    if (waypoints.length < 2) return;
    
    try {
        // Call OSRM API directly for better control
        const coords = waypoints.map(w => `${w[0]},${w[1]}`).join(';');
        const url = `https://router.project-osrm.org/route/v1/driving/${coords}?overview=full&geometries=geojson`;
        
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.code === 'Ok' && data.routes && data.routes.length > 0) {
            const geometry = data.routes[0].geometry;
            
            // Convert GeoJSON coordinates to Leaflet format
            const latlngs = geometry.coordinates.map(coord => [coord[1], coord[0]]);
            
            // Draw the route with different style for hospital leg
            const lineStyle = {
                color: color,
                weight: 6,
                opacity: 0.9,
                smoothFactor: 1,
                className: 'animated-route'
            };
            
            if (segmentType === 'to-hospital') {
                lineStyle.dashArray = '15, 10';
                lineStyle.weight = 5;
            } else {
                lineStyle.dashArray = '20, 15';
            }
            
            const polyline = L.polyline(latlngs, lineStyle);
            polyline.addTo(routeLayer);
            
            // Add ONE prominent arrow at the midpoint for direction
            const midIdx = Math.floor(latlngs.length / 2);
            if (midIdx + 10 < latlngs.length) {
                const start = latlngs[midIdx];
                const end = latlngs[midIdx + 10];
                
                // Calculate bearing for arrow direction
                const lat1 = start[0] * Math.PI / 180;
                const lat2 = end[0] * Math.PI / 180;
                const dLon = (end[1] - start[1]) * Math.PI / 180;
                
                const y = Math.sin(dLon) * Math.cos(lat2);
                const x = Math.cos(lat1) * Math.sin(lat2) - Math.sin(lat1) * Math.cos(lat2) * Math.cos(dLon);
                const bearing = Math.atan2(y, x) * 180 / Math.PI;
                
                L.marker(start, {
                    icon: L.divIcon({
                        className: 'direction-arrow',
                        html: `<div style="
                            transform: rotate(${bearing}deg);
                            font-size: ${segmentType === 'to-hospital' ? '28px' : '32px'};
                            filter: drop-shadow(0 2px 4px rgba(0,0,0,0.5));
                            color: ${color};
                        ">▶</div>`,
                        iconSize: [32, 32]
                    }),
                    zIndexOffset: 500
                }).addTo(routeLayer);
            }
            
            // Add labels
            if (segmentType === 'to-victim') {
                // START marker at resource
                const startPos = latlngs[0];
                const resourceId = routeNodes[0];
                const victimId = routeNodes[1];
                const assignment = assignments.find(a => 
                    a.resource_id === resourceId && a.victim_id === victimId
                );
                
                if (assignment) {
                    L.marker(startPos, {
                        icon: L.divIcon({
                            className: 'route-label-start',
                            html: `<div style="background: ${color}; color: white; padding: 6px 10px; border-radius: 6px; font-size: 11px; font-weight: bold; white-space: nowrap; box-shadow: 0 2px 4px rgba(0,0,0,0.3);">
                                🚦 ${getEntityIcon(assignment.resource_type)} START
                            </div>`,
                            iconSize: [120, 35]
                        }),
                        zIndexOffset: 1000
                    }).addTo(routeLayer);
                    
                    // PICKUP marker at victim
                    const endPos = latlngs[latlngs.length - 1];
                    L.marker(endPos, {
                        icon: L.divIcon({
                            className: 'route-label-end',
                            html: `<div style="background: ${color}; color: white; padding: 6px 10px; border-radius: 6px; font-size: 11px; font-weight: bold; white-space: nowrap; box-shadow: 0 2px 4px rgba(0,0,0,0.3);">
                                🆘 PICKUP
                            </div>`,
                            iconSize: [100, 35]
                        }),
                        zIndexOffset: 1000
                    }).addTo(routeLayer);
                }
            } else if (segmentType === 'to-hospital') {
                // HOSPITAL marker at destination
                const endPos = latlngs[latlngs.length - 1];
                L.marker(endPos, {
                    icon: L.divIcon({
                        className: 'route-label-hospital',
                        html: `<div style="background: ${color}; color: white; padding: 6px 10px; border-radius: 6px; font-size: 11px; font-weight: bold; white-space: nowrap; box-shadow: 0 2px 4px rgba(0,0,0,0.3);">
                            🏥 HOSPITAL
                        </div>`,
                        iconSize: [100, 35]
                    }),
                    zIndexOffset: 1000
                }).addTo(routeLayer);
            }
            
            const segmentLabel = segmentType === 'to-hospital' ? 'to hospital' : 'to victim';
            console.log(`✓ Route ${index + 1} ${segmentLabel}: ${data.routes[0].distance.toFixed(0)}m, ${(data.routes[0].duration / 60).toFixed(1)} min`);
        }
    } catch (error) {
        console.error('Routing error:', error);
        // Fallback to straight line if routing fails
        const latlngs = waypoints.map(w => [w[1], w[0]]);
        L.polyline(latlngs, {
            color: color,
            weight: 4,
            opacity: 0.6,
            dashArray: '10, 10'
        }).addTo(routeLayer);
    }
}

// Display resource assignments
function displayResourceAssignments(assignments) {
    if (!assignments || assignments.length === 0) {
        document.getElementById('resourceAllocation').innerHTML = 
            '<p class="placeholder">No assignments available</p>';
        return;
    }
    
    // Calculate summary statistics
    const totalCost = assignments.reduce((sum, a) => sum + (a.cost_to_victim || 0) + (a.cost_to_hospital || 0), 0);
    const totalVictims = assignments.length;
    const avgCost = totalCost / totalVictims;
    const totalToVictim = assignments.reduce((sum, a) => sum + (a.distance_to_victim || 0), 0);
    const totalToHospital = assignments.reduce((sum, a) => sum + (a.hospital_distance || 0), 0);
    
    // Resource type breakdown
    const resourceTypes = {};
    assignments.forEach(a => {
        resourceTypes[a.resource_type] = (resourceTypes[a.resource_type] || 0) + 1;
    });
    
    let html = `
        <div class="allocation-summary">
            <div class="summary-grid">
                <div class="summary-card">
                    <div class="summary-value">${totalVictims}</div>
                    <div class="summary-label">🆘 Total Assignments</div>
                </div>
                <div class="summary-card">
                    <div class="summary-value">${avgCost.toFixed(1)}</div>
                    <div class="summary-label">📊 Avg Cost</div>
                </div>
                <div class="summary-card">
                    <div class="summary-value">${totalToVictim.toFixed(1)} km</div>
                    <div class="summary-label">🚑 Distance to Victims</div>
                </div>
                <div class="summary-card">
                    <div class="summary-value">${totalToHospital.toFixed(1)} km</div>
                    <div class="summary-label">🏥 Distance to Hospitals</div>
                </div>
            </div>
            <div class="resource-breakdown">
                <strong>Resource Utilization:</strong> 
                ${Object.entries(resourceTypes).map(([type, count]) => 
                    `${getEntityIcon(type)} ${type}: ${count}`
                ).join(' • ')}
            </div>
        </div>
        <div class="allocation-list">
    `;
    
    assignments.forEach((assignment, idx) => {
        const icon = getEntityIcon(assignment.resource_type);
        const hospitalInfo = assignment.hospital_name 
            ? `🏥 ${assignment.hospital_name}` 
            : 'Hospital';
        const distToVictim = assignment.distance_to_victim 
            ? `${assignment.distance_to_victim.toFixed(1)} km` 
            : 'N/A';
        const distToHospital = assignment.hospital_distance 
            ? `${assignment.hospital_distance.toFixed(1)} km` 
            : 'N/A';
        const totalDist = (assignment.distance_to_victim || 0) + (assignment.hospital_distance || 0);
        const estTime = (totalDist / 40 * 60).toFixed(0); // Assuming 40 km/h avg speed
        
        html += `
            <div class="allocation-item">
                <div class="allocation-header">
                    <span class="allocation-number">#${idx + 1}</span>
                    <span class="allocation-route">
                        ${icon} ${assignment.resource_name} → 🆘 ${assignment.victim_name} → ${hospitalInfo}
                    </span>
                </div>
                <div class="allocation-details">
                    <div class="detail-row">
                        <span>📍 To Victim:</span>
                        <span class="detail-value">${distToVictim}</span>
                    </div>
                    <div class="detail-row">
                        <span>🏥 To Hospital:</span>
                        <span class="detail-value green">${distToHospital}</span>
                    </div>
                    <div class="detail-row">
                        <span>⏱️ Est. Time:</span>
                        <span class="detail-value">${estTime} min</span>
                    </div>
                    <div class="detail-row">
                        <span>💰 Total Cost:</span>
                        <span class="detail-value bold">${((assignment.cost_to_victim || 0) + (assignment.cost_to_hospital || 0)).toFixed(1)}</span>
                    </div>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    document.getElementById('resourceAllocation').innerHTML = html;
}

// Update graph stats
async function updateGraphStats() {
    try {
        const response = await fetch(`${API_BASE}/graph-stats`);
        const data = await response.json();
        
        document.getElementById('graphStats').textContent = 
            `Nodes: ${data.num_nodes} | Edges: ${data.num_edges} | Density: ${data.density.toFixed(3)}`;
    } catch (error) {
        console.error('Failed to update graph stats:', error);
    }
}

// Run demo scenario
async function runDemo() {
    updateStatus('Running demo scenario...');
    
    try {
        const response = await fetch(`${API_BASE}/demo`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        // Reload entities
        await loadEntities();
        
        // Create fake route data for demo
        const demoRoutes = [{
            route: data.quantum.route,
            cost: data.quantum.cost,
            resource: data.quantum.route[0]
        }];
        
        // Get victims for assignments
        const victims = data.victims || [];
        const assignments = victims.map((victim, idx) => ({
            resource_id: data.quantum.route[0],
            resource_name: 'Demo Resource',
            resource_type: 'ambulance',
            victim_id: victim.id,
            victim_name: victim.name,
            resource_location: {lat: 28.6139, lon: 77.2090},
            victim_location: victim.location
        }));
        
        // Display results
        displayOptimizationResults({
            classical: {
                method: 'Simulated Annealing',
                total_cost: data.classical.cost,
                cost: data.classical.cost,
                routes: [{route: data.classical.route, cost: data.classical.cost}]
            },
            quantum: {
                method: data.quantum.method || 'QAOA',
                total_cost: data.quantum.cost,
                cost: data.quantum.cost,
                routes: demoRoutes
            },
            comparison: {
                classical_cost: data.classical.cost,
                quantum_cost: data.quantum.cost,
                improvement_percent: data.improvement_percent
            }
        });
        
        // Draw route with actual road routing
        if (demoRoutes.length > 0) {
            await drawRoutedPaths(demoRoutes, assignments);
        }
        
        // Show comparison
        displayComparison({
            classical_cost: data.classical.cost,
            quantum_cost: data.quantum.cost,
            improvement_percent: data.improvement_percent
        });
        
        updateStatus('Demo complete!');
    } catch (error) {
        console.error('Demo failed:', error);
        updateStatus('Demo failed', 'error');
    }
}

// Reset system
async function resetSystem() {
    if (!confirm('Reset system and clear all victims?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/reset`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Reload entities
            await loadEntities();
            
            // Clear routes
            routeLayer.clearLayers();
            routingControls.forEach(control => map.removeControl(control));
            routingControls = [];
            
            // Clear results
            document.getElementById('optimizationResults').innerHTML = 
                '<p class="placeholder">Run optimization to see results...</p>';
            document.getElementById('resourceAllocation').innerHTML = 
                '<p class="placeholder">No allocation yet...</p>';
            
            updateStatus('System reset complete');
        }
    } catch (error) {
        console.error('Reset failed:', error);
        updateStatus('Reset failed', 'error');
    }
}

// Update status message
function updateStatus(message, type = 'success') {
    const statusEl = document.getElementById('status');
    statusEl.textContent = message;
    statusEl.style.color = type === 'error' ? '#ff6b00' : '#00d9ff';
}

// Logout function
function logout() {
    sessionStorage.removeItem('isLoggedIn');
    sessionStorage.removeItem('username');
    window.location.href = '/';
}

// Check if user is logged in (for dashboard access)
document.addEventListener('DOMContentLoaded', () => {
    const isLoggedIn = sessionStorage.getItem('isLoggedIn');
    if (!isLoggedIn && window.location.pathname === '/dashboard') {
        window.location.href = '/volunteer';
    }
});
