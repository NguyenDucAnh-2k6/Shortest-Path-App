from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import osmnx as ox
from pathlib import Path
import heapq
SCRIPT_DIR = Path(__file__).resolve()
DRIVE_DIR = SCRIPT_DIR.parent / 'graphml' / 'hbt_drive_network.graphml'
WALK_DIR = SCRIPT_DIR.parent / 'graphml' / 'hbt_drive_network.graphml'
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Load the OpenStreetMap data into memory on startup
print("Loading graphs into memory. This might take a few seconds...")
G_drive = ox.load_graphml(DRIVE_DIR)
G_walk = ox.load_graphml(WALK_DIR)
print("Graphs loaded successfully!")

# 2. Update our data model to include 'mode'
class RouteRequest(BaseModel):
    startLat: float
    startLng: float
    endLat: float
    endLng: float
    mode: str  # Will receive 'drive' or 'walk' from React

@app.post("/api/find-path")
def find_shortest_path(request: RouteRequest):
    # 1. Select the correct graph based on the user's choice
    G = G_drive if request.mode == "drive" else G_walk
    
    # 2. SNAP COORDINATES TO THE NEAREST GRAPH NODES
    # Note: OSMnx expects X=longitude, Y=latitude
    try:
        start_node = ox.distance.nearest_nodes(G, X=request.startLng, Y=request.startLat)
        end_node = ox.distance.nearest_nodes(G, X=request.endLng, Y=request.endLat)
        print(f"Snapped Start Node ID: {start_node}")
        print(f"Snapped End Node ID: {end_node}")
    except Exception as e:
        return {"status": "error", "message": "Failed to snap coordinates to graph."}

    # 3. RUN YOUR CUSTOM DIJKSTRA ALGORITHM
    # I have set up the function call here. You will write the actual logic below!
    path_nodes, total_distance = run_custom_dijkstra(G, start_node, end_node)

    if not path_nodes:
        return {"status": "error", "message": "No path found between these points."}

    # 4. RECONSTRUCT THE PATH FOR THE FRONTEND
    # We need to turn the list of Node IDs back into Lat/Lng coordinates so React can draw it
    route_coords = []
    for node in path_nodes:
        lat = G.nodes[node]['y']
        lng = G.nodes[node]['x']
        route_coords.append([lat, lng])

    return {
        "status": "success",
        "message": f"Successfully found a {request.mode} route!",
        "path": route_coords,
        "distance": total_distance
    }

# --- YOUR DIJKSTRA IMPLEMENTATION ---
def run_custom_dijkstra(G, start_node, end_node):
    """
    Custom implementation of Dijkstra's Algorithm using a Priority Queue.
    """
    print("Starting custom Dijkstra algorithm...")
    
    # 1. Initialization
    # Set all distances to infinity, except the start node which is 0
    distances = {node: float('infinity') for node in G.nodes}
    distances[start_node] = 0
    
    # Keep track of the best previous node to reconstruct the path later
    previous_nodes = {node: None for node in G.nodes}
    
    # Priority Queue: stores tuples of (distance_from_start, current_node)
    pq = [(0, start_node)]
    
    # 2. Process the Graph
    while pq:
        # Pop the node with the absolute shortest distance from the queue
        current_distance, current_node = heapq.heappop(pq)
        
        # Optimization: If we reached the destination, we can stop searching!
        if current_node == end_node:
            break
            
        # If we pulled a stale, longer distance from the queue, ignore it
        if current_distance > distances[current_node]:
            continue
            
        # Check all connected neighbor intersections
        for neighbor in G.neighbors(current_node):
            # OSMnx uses MultiDiGraphs (multiple possible roads between 2 nodes)
            # We grab the first edge data (index 0)
            edge_data = G.get_edge_data(current_node, neighbor)[0]
            
            # Get the length of this specific street (default to 1.0 if missing)
            weight = edge_data.get('length', 1.0)
            
            # Calculate the total distance to this neighbor
            distance = current_distance + weight
            
            # 3. Relaxation: If we found a faster way to this neighbor, update it
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous_nodes[neighbor] = current_node
                # Push the newly found shorter distance into the priority queue
                heapq.heappush(pq, (distance, neighbor))
                
    # 4. Path Reconstruction
    # If the end_node's distance is still infinity, no path exists
    if distances[end_node] == float('infinity'):
        print("No path found!")
        return [], 0
        
    # Backtrack from the end node to the start node
    path = []
    current = end_node
    while current is not None:
        path.append(current)
        current = previous_nodes[current]
        
    # Reverse the path so it goes from Start -> End
    path.reverse()
    
    print(f"Path found! It takes {len(path)} steps and is {distances[end_node]:.2f} meters long.")
    return path, distances[end_node]