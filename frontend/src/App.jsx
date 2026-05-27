import { useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMapEvents, Polyline } from 'react-leaflet';

function MapClickHandler({ startPoint, setStartPoint, endPoint, setEndPoint }) {
  useMapEvents({
    click(e) {
      if (!startPoint) {
        setStartPoint([e.latlng.lat, e.latlng.lng]);
      } else if (!endPoint) {
        setEndPoint([e.latlng.lat, e.latlng.lng]);
      } else {
        setStartPoint([e.latlng.lat, e.latlng.lng]);
        setEndPoint(null);
      }
    },
  });
  return null;
}

function App() {
  const hanoiPosition = [21.0035, 105.8490];
  const [startPoint, setStartPoint] = useState(null);
  const [endPoint, setEndPoint] = useState(null);
  const [mode, setMode] = useState('drive'); 
  
  // NEW: State to hold the array of path coordinates returned by Python
  const [pathCoords, setPathCoords] = useState([]); 

  const handleFindRoute = async () => {
    if (!startPoint || !endPoint) return;

    try {
      const response = await fetch("http://127.0.0.1:8000/api/find-path", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          startLat: startPoint[0],
          startLng: startPoint[1],
          endLat: endPoint[0],
          endLng: endPoint[1],
          mode: mode, 
        }),
      });

      const data = await response.json();
      
      if (data.status === "success") {
        // NEW: Save the path coordinates to state so React draws them!
        setPathCoords(data.path);
        alert(`Path found! Total distance: ${data.distance.toFixed(2)} meters`); 
      } else {
        alert(`Error: ${data.message}`);
      }

    } catch (error) {
      console.error("Error connecting to backend:", error);
      alert("Failed to connect. Make sure your FastAPI server is running!");
    }
  };

  return (
    <div style={{ position: 'relative' }}>
      
      <div style={{
        position: 'absolute',
        top: '20px',
        right: '20px',
        zIndex: 1000,
        backgroundColor: 'white',
        padding: '20px',
        borderRadius: '8px',
        boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
        width: '220px'
      }}>
        <h3 style={{ margin: '0 0 10px 0' }}>Pathfinder</h3>
        <p style={{ fontSize: '14px', color: '#555', marginBottom: '10px' }}>
          1. Click map for Start<br/>
          2. Click map for End
        </p>

        {/* NEW: Walking / Driving Toggle */}
        <div style={{ display: 'flex', gap: '10px', marginBottom: '15px' }}>
          <button 
            onClick={() => setMode('drive')}
            style={{
              flex: 1,
              padding: '8px',
              backgroundColor: mode === 'drive' ? '#333' : '#eee',
              color: mode === 'drive' ? 'white' : 'black',
              border: '1px solid #ccc',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            🚗 Drive
          </button>
          <button 
            onClick={() => setMode('walk')}
            style={{
              flex: 1,
              padding: '8px',
              backgroundColor: mode === 'walk' ? '#333' : '#eee',
              color: mode === 'walk' ? 'white' : 'black',
              border: '1px solid #ccc',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            🚶 Walk
          </button>
        </div>
        
        <button 
          onClick={handleFindRoute}
          disabled={!startPoint || !endPoint}
          style={{ 
            padding: '10px', 
            width: '100%',
            cursor: (!startPoint || !endPoint) ? 'not-allowed' : 'pointer',
            backgroundColor: (!startPoint || !endPoint) ? '#ccc' : '#007BFF',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            fontWeight: 'bold'
          }}
        >
          Find Route
        </button>
      </div>

      <MapContainer 
        center={hanoiPosition} 
        zoom={14} 
        style={{ height: '100vh', width: '100vw' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        <MapClickHandler 
          startPoint={startPoint} 
          setStartPoint={setStartPoint} 
          endPoint={endPoint} 
          setEndPoint={setEndPoint} 
        />

        {startPoint && <Marker position={startPoint}><Popup>Start</Popup></Marker>}
        {endPoint && <Marker position={endPoint}><Popup>End</Popup></Marker>}

        {/* NEW: Draw the blue route line following project specs! */}
        {pathCoords.length > 0 && (
          <Polyline 
            positions={pathCoords} 
            color="blue" 
            weight={5} 
            opacity={0.8} 
          />
        )}
      </MapContainer>
    </div>
  );
}

export default App;