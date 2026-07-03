"use client";

import { useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { useQuery } from "@tanstack/react-query";
import axios from "axios";
import { format } from "date-fns";
import { JobDrawer } from "./JobDrawer";

const API_BASE = "http://127.0.0.1:5000/api/v1";

export function JobTable() {
  const [selectedJob, setSelectedJob] = useState<string | null>(null);

  const { data: jobs } = useQuery({
    queryKey: ['alertsJobs'],
    queryFn: async () => (await axios.get(`${API_BASE}/alerts/jobs`)).data,
    refetchInterval: 2000,
  });

  return (
    <>
      <Card className="col-span-full">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm uppercase text-zinc-400 tracking-wider">Live Job Queue</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="text-xs text-zinc-400 uppercase bg-zinc-900/50 border-b border-zinc-800">
                <tr>
                  <th className="px-4 py-3">Job ID</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Created At</th>
                  <th className="px-4 py-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody>
                {jobs?.map((job: any) => (
                  <tr key={job.id} className="border-b border-zinc-800 hover:bg-zinc-800/30 transition-colors">
                    <td className="px-4 py-3 font-mono text-xs text-zinc-300">{job.id.substring(0, 8)}...</td>
                    <td className="px-4 py-3">
                      <StatusBadge status={job.status} />
                    </td>
                    <td className="px-4 py-3 text-zinc-400">
                      {format(new Date(job.created_at), "HH:mm:ss")}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <button 
                        onClick={() => setSelectedJob(job.id)}
                        className="text-blue-400 hover:text-blue-300 text-xs font-medium"
                      >
                        Details
                      </button>
                    </td>
                  </tr>
                ))}
                {!jobs || jobs.length === 0 ? (
                  <tr>
                    <td colSpan={4} className="px-4 py-8 text-center text-zinc-500">
                      No jobs in queue
                    </td>
                  </tr>
                ) : null}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
      
      {selectedJob && (
        <JobDrawer jobId={selectedJob} onClose={() => setSelectedJob(null)} />
      )}
    </>
  );
}

function StatusBadge({ status }: { status: string }) {
  switch(status) {
    case 'Completed': return <Badge variant="success">Completed</Badge>;
    case 'Failed': return <Badge variant="destructive">Failed</Badge>;
    case 'Processing': return <Badge variant="warning">Processing</Badge>;
    case 'Queued': return <Badge variant="secondary">Queued</Badge>;
    default: return <Badge variant="outline">{status}</Badge>;
  }
}
