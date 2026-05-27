import osmnx as ox

def download_maps():
    place = "Hai Bà Trưng District, Hanoi, Vietnam"
    print(f"Fetching data for {place}...")

    # 1. Download and save the Driving Network
    print("Downloading driving network... (This might take a minute)")
    G_drive = ox.graph_from_place(
        place, 
        network_type="drive", 
        simplify=True
    )
    ox.save_graphml(G_drive, "hbt_drive_network.graphml")
    print("Saved hbt_drive_network.graphml!")

    # 2. Download and save the Walking Network
    print("Downloading walking network...")
    G_walk = ox.graph_from_place(
        place, 
        network_type="walk", 
        simplify=True
    )
    ox.save_graphml(G_walk, "hbt_walk_network.graphml")
    print("Saved hbt_walk_network.graphml!")

    print("All map data downloaded successfully!")

if __name__ == "__main__":
    download_maps()