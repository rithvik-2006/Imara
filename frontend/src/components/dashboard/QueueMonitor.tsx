"use client";

import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card";
import { Progress } from "@/components/ui/Progress";
import { useQuery } from "@tanstack/react-query";
import axios from "axios";

const API_BASE = "http://127.0.0.1:5000/api/v1";

export function QueueMonitor() {
  const { data: jobs } = useQuery({
    queryKey: ['dashboardJobs'],
    queryFn: async () => (await axios.get(`${API_BASE}/dashboard/jobs`)).data,
    refetchInterval: 2000,
  });

  const total = (jobs?.queued || 0) + (jobs?.running || 0) + (jobs?.completed || 0) + (jobs?.failed || 0);
  const queuedPct = total ? (jobs?.queued / total) * 100 : 0;
  const runningPct = total ? (jobs?.running / total) * 100 : 0;
  const completedPct = total ? (jobs?.completed / total) * 100 : 0;
  const failedPct = total ? (jobs?.failed / total) * 100 : 0;

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm uppercase text-zinc-400 tracking-wider">Queue Monitor</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <QueueBar label="Queued" value={jobs?.queued || 0} pct={queuedPct} color="bg-blue-500" />
        <QueueBar label="Running" value={jobs?.running || 0} pct={runningPct} color="bg-yellow-500" />
        <QueueBar label="Completed" value={jobs?.completed || 0} pct={completedPct} color="bg-green-500" />
        <QueueBar label="Failed" value={jobs?.failed || 0} pct={failedPct} color="bg-red-500" />
        
        <div className="pt-4 mt-4 border-t border-zinc-800 grid grid-cols-2 gap-4 text-xs">
          <div>
            <div className="text-zinc-500">Overall Progress</div>
            <div className="text-lg font-mono text-zinc-100">{jobs?.progress_percentage || 0}%</div>
          </div>
          <div>
            <div className="text-zinc-500">Avg Processing Speed</div>
            <div className="text-lg font-mono text-zinc-100">{jobs?.avg_processing_time || 0}s / job</div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function QueueBar({ label, value, pct, color }: { label: string, value: number, pct: number, color: string }) {
  return (
    <div className="space-y-1.5">
      <div className="flex justify-between text-xs">
        <span className="text-zinc-300 font-medium">{label}</span>
        <span className="font-mono text-zinc-400">{value} ({pct.toFixed(0)}%)</span>
      </div>
      <Progress value={pct} indicatorColor={color} className="h-1.5 bg-zinc-800" />
    </div>
  );
}
