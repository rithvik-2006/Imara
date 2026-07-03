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

const createIcon = (color: string) => new L.Icon({
  iconUrl: `https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-${color}.png`,
  shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

const icons: Record<string, L.Icon> = {
  'Safe': createIcon('green'),
  'Queued': createIcon('yellow'),
  'Processing': createIcon('blue'),
  'SMS Sent': createIcon('orange'),
  'Voice Sent': createIcon('violet'),
  'Failed': createIcon('red'),
  'At Risk': createIcon('red')
};

export default function InteractiveMap({ data }: { data: any }) {
  if (!data || !data.features) return <div className="h-full flex items-center justify-center text-zinc-500">Loading Map Data...</div>;

  const communities = data.features.filter((f: any) => f.properties.type === 'community');
  const hazards = data.features.filter((f: any) => f.properties.type === 'hazard');

  const center: [number, number] = [-0.1, 35.8];

  return (
    <div className="h-full w-full rounded-xl overflow-hidden relative z-0 border border-zinc-800">
      <MapContainer center={center} zoom={7} scrollWheelZoom={true} className="h-full w-full bg-zinc-900" style={{ height: "100%", width: "100%" }}>
        {/* Dark Mode CartoDB Positron TileLayer */}
        <TileLayer
          attribution='&copy; <a href="https://carto.com/">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />
        
        {/* Render Hazards */}
        {hazards.map((hazard: any) => {
          const coords = hazard.geometry.coordinates[0].map((coord: number[]) => [coord[1], coord[0]]);
          const hazardColors: Record<string, string> = {
            'Flood': '#3b82f6', // Blue
            'Drought': '#a16207', // Brown
            'Locust': '#f97316', // Orange
            'Cyclone': '#a855f7', // Purple
            'Fire': '#ef4444' // Red
          };
          const color = hazardColors[hazard.properties.hazard_type] || '#ef4444';
          
          return (
            <Polygon 
              key={hazard.properties.id} 
              positions={coords} 
              pathOptions={{ color, fillColor: color, fillOpacity: 0.3, weight: 2 }}
            >
              <Popup className="dark-popup">
                <div className="text-zinc-900">
                  <strong className="text-lg">{hazard.properties.hazard_type}</strong>
                  <div className="text-sm mt-1">Severity: {hazard.properties.severity}</div>
                </div>
              </Popup>
            </Polygon>
          );
        })}

        {/* Render Communities */}
        {communities.map((comm: any) => {
          const [lng, lat] = comm.geometry.coordinates;
          const status = comm.properties.status;
          const icon = icons[status] || icons['Safe'];

          return (
            <Marker key={comm.properties.id} position={[lat, lng]} icon={icon}>
              <Popup>
                <div className="text-zinc-900 min-w-[150px]">
                  <strong className="text-base border-b pb-1 mb-1 block">{comm.properties.name}</strong>
                  <div className="text-xs space-y-1">
                    <div>Status: <span className="font-semibold">{status}</span></div>
                    <div>Risk: {comm.properties.risk_level}</div>
                    <div>Lang: {comm.properties.preferred_language}</div>
                    <div>Pop: {comm.properties.population}</div>
                  </div>
                </div>
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>
    </div>
  );
}
