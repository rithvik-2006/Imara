"use client";

import Image from "next/image";
import { useEffect, useState } from "react";
import { Badge } from "@/components/ui/Badge";
import { format } from "date-fns";

export function Header() {
  const [mounted, setMounted] = useState(false);
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    setMounted(true);
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <header className="bg-zinc-950 border-b border-zinc-800 px-6 py-3 flex justify-between items-center sticky top-0 z-50">
      <div className="flex items-center space-x-3">
        <Image src="/logo.svg" alt="Imara Logo" width={28} height={28} />
        <h1 className="text-xl font-bold tracking-tight text-zinc-100">
          Imara Operations Center
        </h1>
      </div>
      
      <div className="flex items-center space-x-6 text-sm">
        <div className="flex flex-col items-end">
          <span className="text-zinc-400 text-xs uppercase tracking-wider">Local Time</span>
          <span className="font-mono text-zinc-100">
            {mounted ? format(time, "HH:mm:ss") : "--:--:--"}
          </span>
        </div>
        
        <div className="h-8 w-px bg-zinc-800" />
        
        <div className="flex items-center space-x-4">
          <StatusItem label="Backend" status="Healthy" />
          <StatusItem label="Queue" status="Healthy" />
          <StatusItem label="NVIDIA" status="Connected" />
          <StatusItem label="Africa's Talking" status="Online" />
        </div>
      </div>
    </header>
  );
}

function StatusItem({ label, status }: { label: string, status: string }) {
  return (
    <div className="flex items-center space-x-2">
      <span className="text-zinc-400">{label}</span>
      <Badge variant="success" className="h-5 px-1.5">{status}</Badge>
    </div>
  );
}
