"use client";

import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card";
import { Database, Server, Cpu, Globe, MessageCircle } from "lucide-react";
import { Badge } from "@/components/ui/Badge";

export function SystemHealth() {
  // Mock health data - in a real app, this would come from a /health endpoint
  const services = [
    { name: "PostgreSQL Database", icon: <Database />, status: "Healthy", ping: "14ms" },
    { name: "Redis Message Broker", icon: <Server />, status: "Healthy", ping: "2ms" },
    { name: "Celery Worker Pool", icon: <Cpu />, status: "Healthy", ping: "0ms" },
    { name: "NVIDIA NIM API", icon: <Globe />, status: "Healthy", ping: "450ms" },
    { name: "Africa's Talking API", icon: <MessageCircle />, status: "Healthy", ping: "210ms" },
  ];

  return (
    <Card className="col-span-full md:col-span-1">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm uppercase text-zinc-400 tracking-wider">System Health</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4 mt-2">
        {services.map((svc, i) => (
          <div key={i} className="flex items-center justify-between">
            <div className="flex items-center space-x-3 text-zinc-300 text-sm">
              <div className="text-zinc-500 w-4 h-4 [&>svg]:w-4 [&>svg]:h-4">{svc.icon}</div>
              <span>{svc.name}</span>
            </div>
            <div className="flex items-center space-x-3">
              <span className="text-xs font-mono text-zinc-500">{svc.ping}</span>
              <Badge variant="success" className="h-5">{svc.status}</Badge>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
