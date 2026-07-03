"use client";

import { useState, useEffect } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card";

export function ActivityFeed({ logs }: { logs: string[] }) {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="pb-2 border-b border-zinc-800">
        <CardTitle className="text-sm uppercase text-zinc-400 tracking-wider">Live Activity Feed</CardTitle>
      </CardHeader>
      <CardContent 
        className="flex-1 overflow-y-auto p-4 space-y-3 font-mono text-xs"
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
      >
        {logs.length === 0 ? (
          <div className="text-zinc-600 italic h-full flex items-center justify-center">
            Waiting for pipeline events...
          </div>
        ) : (
          logs.map((log, i) => (
            <div 
              key={i} 
              className={`border-l-2 border-blue-500 pl-3 py-1.5 bg-zinc-900/50 rounded-r text-zinc-300 transition-opacity ${isHovered ? 'opacity-50 hover:opacity-100' : 'opacity-100'}`}
            >
              {log}
            </div>
          ))
        )}
      </CardContent>
    </Card>
  );
}
