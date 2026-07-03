"use client";

import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell } from "recharts";
import { useQuery } from "@tanstack/react-query";
import axios from "axios";

const API_BASE = "http://127.0.0.1:5000/api/v1";

export function AnalyticsCharts() {
  const { data: jobs } = useQuery({
    queryKey: ['dashboardJobs'],
    queryFn: async () => (await axios.get(`${API_BASE}/dashboard/jobs`)).data,
    refetchInterval: 5000,
  });

  const latencyData = [
    { name: "AI", latency: jobs?.avg_ai_latency || 0, color: "#3b82f6" },
    { name: "Trans", latency: jobs?.avg_translation_latency || 0, color: "#8b5cf6" },
    { name: "TTS", latency: jobs?.avg_tts_latency || 0, color: "#ec4899" },
    { name: "SMS", latency: jobs?.avg_sms_latency || 0, color: "#f97316" },
    { name: "Voice", latency: jobs?.avg_voice_latency || 0, color: "#eab308" },
  ];

  return (
    <Card className="col-span-full md:col-span-1">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm uppercase text-zinc-400 tracking-wider">Average Latency (s)</CardTitle>
      </CardHeader>
      <CardContent className="h-[200px] mt-4">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={latencyData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#27272a" vertical={false} />
            <XAxis dataKey="name" stroke="#52525b" fontSize={11} tickLine={false} axisLine={false} />
            <YAxis stroke="#52525b" fontSize={11} tickLine={false} axisLine={false} />
            <Tooltip 
              cursor={{ fill: '#27272a', opacity: 0.4 }}
              contentStyle={{ backgroundColor: '#18181b', border: '1px solid #27272a', borderRadius: '8px' }}
              itemStyle={{ color: '#e4e4e7' }}
            />
            <Bar dataKey="latency" radius={[4, 4, 0, 0]}>
              {latencyData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
