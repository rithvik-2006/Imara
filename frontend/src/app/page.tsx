"use client";

import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import { Header } from "@/components/dashboard/Header";
import { StatCards } from "@/components/dashboard/StatCards";
import { PipelineStatus } from "@/components/dashboard/PipelineStatus";
import { QueueMonitor } from "@/components/dashboard/QueueMonitor";
import { JobTable } from "@/components/dashboard/JobTable";
import { ActivityFeed } from "@/components/dashboard/ActivityFeed";
import { AnalyticsCharts } from "@/components/dashboard/AnalyticsCharts";
import { SystemHealth } from "@/components/dashboard/SystemHealth";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card";
import { RefreshCw, ShieldAlert } from "lucide-react";
import axios from "axios";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

const InteractiveMap = dynamic(() => import("@/components/InteractiveMap"), { ssr: false });
const API_BASE = "http://127.0.0.1:5000/api/v1";

export default function Dashboard() {
  const queryClient = useQueryClient();
  const [simulating, setSimulating] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);

  // Dynamically adjust map polling
  const { data: jobsStats } = useQuery({
    queryKey: ['dashboardJobs'],
    queryFn: async () => (await axios.get(`${API_BASE}/dashboard/jobs`)).data,
    refetchInterval: 2000,
  });

  const isPipelineActive = jobsStats?.queued > 0 || jobsStats?.running > 0;

  const { data: mapData } = useQuery({
    queryKey: ['dashboardMap'],
    queryFn: async () => (await axios.get(`${API_BASE}/dashboard/map`)).data,
    refetchInterval: isPipelineActive ? 2000 : 10000, // Fast polling if active
  });

  const handleSimulate = async () => {
    setSimulating(true);
    addLog("Initiating AI Orchestration Pipeline...");
    const toastId = toast.loading("Executing spatial join...");
    
    try {
      addLog("Executing PostGIS ST_Intersects spatial join...");
      const res = await axios.post(`${API_BASE}/alerts/process`);
      
      const { jobs_created, status } = res.data;
      addLog(`Queued ${jobs_created} jobs successfully. Status: ${status}`);
      toast.success(`Queued ${jobs_created} jobs successfully!`, { id: toastId });
      
      // Force immediate refresh
      queryClient.invalidateQueries({ queryKey: ['dashboardJobs'] });
      queryClient.invalidateQueries({ queryKey: ['alertsJobs'] });
      
    } catch (error) {
      addLog("Error running pipeline. Backend might be down.");
      toast.error("Failed to trigger pipeline.", { id: toastId });
    } finally {
      setSimulating(false);
    }
  };

  const addLog = (msg: string) => {
    setLogs((prev) => [`[${new Date().toLocaleTimeString()}] ${msg}`, ...prev].slice(0, 50));
  };

  // Listen for job completion to add to logs
  useEffect(() => {
    if (jobsStats) {
      const prevCompleted = Number(localStorage.getItem('prevCompleted') || 0);
      if (jobsStats.completed > prevCompleted) {
        addLog(`Processed ${jobsStats.completed - prevCompleted} new jobs.`);
        toast.success("New alerts dispatched successfully!");
      }
      localStorage.setItem('prevCompleted', jobsStats.completed.toString());
    }
  }, [jobsStats]);

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-50 font-sans flex flex-col">
      <Header />

      <main className="flex-1 p-6 space-y-6">
        <div className="flex justify-between items-center">
          <h2 className="text-xl font-bold">Live Operations Center</h2>
          <button 
            onClick={handleSimulate}
            disabled={simulating || isPipelineActive}
            className="flex items-center space-x-2 bg-red-600 hover:bg-red-700 text-white px-5 py-2 rounded-lg font-semibold transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm shadow-[0_0_15px_rgba(220,38,38,0.5)]"
          >
            {simulating || isPipelineActive ? <RefreshCw className="h-4 w-4 animate-spin" /> : <ShieldAlert className="h-4 w-4" />}
            <span>{isPipelineActive ? "Pipeline Active..." : "Trigger Alerts"}</span>
          </button>
        </div>

        <StatCards />

        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
          <div className="xl:col-span-2 space-y-6 flex flex-col h-[700px]">
            <PipelineStatus />
            <Card className="flex-1 overflow-hidden border-zinc-800 relative z-0">
              <CardHeader className="pb-2 absolute top-0 left-0 right-0 z-10 bg-gradient-to-b from-zinc-950/80 to-transparent pointer-events-none">
                <CardTitle className="text-sm uppercase text-zinc-100 tracking-wider shadow-black drop-shadow-md">Geospatial Intelligence</CardTitle>
              </CardHeader>
              <CardContent className="p-0 h-full">
                <InteractiveMap data={mapData} />
              </CardContent>
            </Card>
          </div>

          <div className="space-y-6 flex flex-col h-[700px]">
            <QueueMonitor />
            <div className="flex-1 overflow-hidden">
              <ActivityFeed logs={logs} />
            </div>
          </div>
        </div>

        <JobTable />

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <AnalyticsCharts />
          <SystemHealth />
        </div>
      </main>
    </div>
  );
}
