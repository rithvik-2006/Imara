"use client";

import { Card, CardContent } from "@/components/ui/Card";
import { Activity, AlertTriangle, CheckCircle2, Clock, Map, XCircle, Zap } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import axios from "axios";

const API_BASE = "http://127.0.0.1:5000/api/v1";

export function StatCards() {
  const { data: stats } = useQuery({
    queryKey: ['dashboardStats'],
    queryFn: async () => (await axios.get(`${API_BASE}/dashboard/stats`)).data,
    refetchInterval: 5000,
  });

  const { data: jobs } = useQuery({
    queryKey: ['dashboardJobs'],
    queryFn: async () => (await axios.get(`${API_BASE}/dashboard/jobs`)).data,
    refetchInterval: 2000,
  });

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4">
      <MetricCard title="Total Communities" value={stats?.total_communities || 0} icon={<Map className="text-zinc-400" />} />
      <MetricCard title="Active Hazards" value={stats?.active_hazards || 0} icon={<AlertTriangle className="text-yellow-500" />} />
      <MetricCard title="Queued Jobs" value={jobs?.queued || 0} icon={<Clock className="text-blue-400" />} />
      <MetricCard title="Running Jobs" value={jobs?.running || 0} icon={<Activity className="text-orange-400" />} />
      <MetricCard title="Completed Jobs" value={jobs?.completed || 0} icon={<CheckCircle2 className="text-green-500" />} />
      <MetricCard title="Failed Jobs" value={jobs?.failed || 0} icon={<XCircle className="text-red-500" />} />
      <MetricCard title="Delivery Success" value={`${stats?.delivery_success_rate || 0}%`} icon={<CheckCircle2 className="text-green-500" />} />
      <MetricCard title="Avg Processing Time" value={`${jobs?.avg_processing_time || 0}s`} icon={<Zap className="text-purple-400" />} />
    </div>
  );
}

function MetricCard({ title, value, icon }: { title: string, value: string | number, icon: React.ReactNode }) {
  return (
    <Card className="bg-zinc-900 border-zinc-800">
      <CardContent className="p-4 flex items-center justify-between">
        <div>
          <div className="text-xs text-zinc-400 font-medium uppercase tracking-wider mb-1">{title}</div>
          <div className="text-2xl font-bold text-zinc-100">{value}</div>
        </div>
        <div className="p-2 bg-zinc-800/50 rounded-lg">
          {icon}
        </div>
      </CardContent>
    </Card>
  );
}
