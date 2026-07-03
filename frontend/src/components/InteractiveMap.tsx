"use client";

import { MapContainer, TileLayer, Marker, Popup, Polygon } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";

// Fix Leaflet's default icon path issues in Next.js
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png",
  iconUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png",
  shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png",
});

const safeIcon = new L.Icon({
  iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png",
  shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

const riskIcon = new L.Icon({
  iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png",
  shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

const alertedIcon = new L.Icon({
  iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-orange.png",
  shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

export default function InteractiveMap({ data }: { data: any }) {
  if (!data || !data.features) return <div className="p-4">Loading Map...</div>;

  const communities = data.features.filter((f: any) => f.properties.type === 'community');
  const hazards = data.features.filter((f: any) => f.properties.type === 'hazard');

  // Default to Eldoret / Nakuru center roughly
  const center: [number, number] = [-0.1, 35.8];

  return (
    <div className="h-full w-full rounded-xl overflow-hidden relative z-0">
      <MapContainer center={center} zoom={7} scrollWheelZoom={true} className="h-full w-full" style={{ height: "100%", width: "100%" }}>
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        {/* Render Hazards */}
        {hazards.map((hazard: any) => {
          // GeoJSON polygon structure: [[[lng, lat], ...]] -> leaflet expects [[lat, lng], ...]
          const coords = hazard.geometry.coordinates[0].map((coord: number[]) => [coord[1], coord[0]]);
          const color = hazard.properties.severity === 'High' ? 'red' : 'orange';
          return (
            <Polygon 
              key={hazard.properties.id} 
              positions={coords} 
              pathOptions={{ color, fillColor: color, fillOpacity: 0.4 }}
            >
              <Popup>
                <strong>{hazard.properties.hazard_type}</strong><br/>
                Severity: {hazard.properties.severity}
              </Popup>
            </Polygon>
          );
        })}

        {/* Render Communities */}
        {communities.map((comm: any) => {
          const [lng, lat] = comm.geometry.coordinates;
          const status = comm.properties.status;
          let icon = safeIcon;
          if (status === 'At Risk') icon = riskIcon;
          if (status === 'Alerted') icon = alertedIcon;

          return (
            <Marker key={comm.properties.id} position={[lat, lng]} icon={icon}>
              <Popup>
                <strong>{comm.properties.name}</strong><br/>
                Status: {status}
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>
    </div>
  );
}
