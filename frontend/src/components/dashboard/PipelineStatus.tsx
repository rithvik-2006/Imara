"use client";

import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card";
import { ArrowRight, BrainCircuit, MessageSquare, PhoneCall, Radio, Send, Volume2 } from "lucide-react";

export function PipelineStatus() {
  // In a real implementation, we could fetch exact counts per stage if the backend exposed it.
  // For now, we will just visually map the pipeline.
  
  return (
    <Card className="col-span-full">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm uppercase text-zinc-400 tracking-wider">Alert Pipeline Status</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex items-center justify-between overflow-x-auto py-4 px-2">
          
          <Stage icon={<Radio />} label="Spatial Query" status="active" />
          <Connector />
          <Stage icon={<BrainCircuit />} label="AI Generation" status="active" />
          <Connector />
          <Stage icon={<MessageSquare />} label="Translation" status="active" />
          <Connector />
          <Stage icon={<Volume2 />} label="TTS Audio" status="active" />
          <Connector />
          <Stage icon={<Send />} label="SMS Dispatch" status="active" />
          <Connector />
          <Stage icon={<PhoneCall />} label="Voice Call" status="active" />
          
        </div>
      </CardContent>
    </Card>
  );
}

function Stage({ icon, label, status }: { icon: React.ReactNode, label: string, status: 'active' | 'pending' | 'error' }) {
  const colors = {
    active: "bg-blue-500/20 text-blue-400 border-blue-500/30",
    pending: "bg-zinc-800 text-zinc-400 border-zinc-700",
    error: "bg-red-500/20 text-red-400 border-red-500/30"
  };

  return (
    <div className="flex flex-col items-center space-y-2 min-w-[100px]">
      <div className={`p-4 rounded-full border ${colors[status]}`}>
        {icon}
      </div>
      <span className="text-xs font-medium text-zinc-300 text-center">{label}</span>
    </div>
  );
}

function Connector() {
  return (
    <div className="flex-1 min-w-[30px] flex items-center justify-center">
      <ArrowRight className="text-zinc-700 w-5 h-5" />
    </div>
  );
}
