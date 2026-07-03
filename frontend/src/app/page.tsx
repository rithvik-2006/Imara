"use client";

import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import Image from "next/image";
import { ShieldAlert, Users, RadioTower, RefreshCw, Send } from "lucide-react";
import axios from "axios";

// Dynamically import Leaflet map with SSR disabled (Leaflet requires `window`)
const InteractiveMap = dynamic(() => import("@/components/InteractiveMap"), { ssr: false });

const API_BASE = "http://127.0.0.1:5000/api/v1";

export default function Dashboard() {
  const [stats, setStats] = useState<any>(null);
  const [mapData, setMapData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [simulating, setSimulating] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);

  const fetchData = async () => {
    try {
      const statsRes = await axios.get(`${API_BASE}/dashboard/stats`);
      const mapRes = await axios.get(`${API_BASE}/dashboard/map`);
      setStats(statsRes.data);
      setMapData(mapRes.data);
    } catch (err) {
      console.error("Failed to fetch data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    // Poll every 5 seconds for real-time AT DeliveryLog updates
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleSimulate = async () => {
    setSimulating(true);
    addLog("Initiating AI Orchestration Pipeline...");
    
    try {
      addLog("Executing PostGIS ST_Intersects spatial join...");
      const res = await axios.get(`${API_BASE}/check-alerts`);
      
      const { total_alerts, alerts } = res.data;
      addLog(`Identified ${total_alerts} communities currently at risk.`);
      
      alerts.forEach((alert: any) => {
        addLog(`NVIDIA NIM localized alert to ${alert.language} for ${alert.community_name}.`);
        addLog(`AT Webhook: SMS & Voice Call dispatched to ${alert.community_name}.`);
      });
      
      await fetchData(); // Refresh map to show red/orange icons
    } catch (error) {
      addLog("Error running pipeline. Is backend running with CORS?");
    } finally {
      setSimulating(false);
    }
  };

  const addLog = (msg: string) => {
    setLogs((prev) => [`[${new Date().toLocaleTimeString()}] ${msg}`, ...prev].slice(0, 15));
  };

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 font-sans">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-8 py-4 flex justify-between items-center sticky top-0 z-50">
        <div className="flex items-center space-x-3">
          <Image src="/logo.svg" alt="Imara Logo" width={32} height={32} />
          <h1 className="text-2xl font-bold tracking-tight text-gray-800">
            Imara
          </h1>
        </div>
        <button 
          onClick={handleSimulate}
          disabled={simulating}
          className="flex items-center space-x-2 bg-red-600 hover:bg-red-700 text-white px-5 py-2.5 rounded-lg font-semibold transition-colors disabled:opacity-50"
        >
          {simulating ? <RefreshCw className="h-5 w-5 animate-spin" /> : <ShieldAlert className="h-5 w-5" />}
          <span>{simulating ? "Generating AI Alerts..." : "Simulate Trigger"}</span>
        </button>
      </header>

      <main className="p-8 max-w-7xl mx-auto space-y-6">
        
        {/* Metrics Row */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <MetricCard title="Monitored Communities" value={stats?.total_communities || 0} icon={<Users />} />
          <MetricCard title="Active Hazards" value={stats?.active_hazards || 0} icon={<ShieldAlert className="text-red-500" />} />
          <MetricCard title="Alerts Dispatched" value={stats?.total_alerts || 0} icon={<Send className="text-blue-500" />} />
          <MetricCard title="Delivery Success" value={`${stats?.delivery_success_rate || 0}%`} icon={<RefreshCw className="text-green-500" />} />
        </div>

        {/* Content Split */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[650px]">
          <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border border-gray-200 p-2 h-full relative z-0">
            {loading ? <div className="h-full flex items-center justify-center text-gray-400">Loading Map Data...</div> : <InteractiveMap data={mapData} />}
          </div>
          
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 flex flex-col h-full overflow-hidden">
            <div className="p-4 border-b border-gray-100 bg-gray-50 font-bold text-gray-700 uppercase tracking-wide text-xs">
              Live Activity Feed
            </div>
            <div className="p-4 overflow-y-auto flex-1 space-y-4 font-mono text-xs">
              {logs.length === 0 ? (
                <div className="text-gray-400 italic">Waiting for triggers...</div>
              ) : (
                logs.map((log, i) => (
                  <div key={i} className="text-gray-600 border-l-2 border-green-500 pl-3 py-1 bg-gray-50 rounded-r">
                    {log}
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

function MetricCard({ title, value, icon }: { title: string, value: string | number, icon: React.ReactNode }) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 flex items-center space-x-5 transition-transform hover:-translate-y-1 hover:shadow-md duration-200">
      <div className="p-3 bg-gray-100 rounded-xl text-gray-600">
        {icon}
      </div>
      <div>
        <div className="text-sm text-gray-500 font-semibold uppercase tracking-wider">{title}</div>
        <div className="text-3xl font-black text-gray-800">{value}</div>
      </div>
    </div>
  );
}
