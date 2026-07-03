"use client";

import { useQuery } from "@tanstack/react-query";
import axios from "axios";
import { motion, AnimatePresence } from "framer-motion";
import { X } from "lucide-react";
import { format } from "date-fns";

const API_BASE = "http://127.0.0.1:5000/api/v1";

export function JobDrawer({ jobId, onClose }: { jobId: string, onClose: () => void }) {
  const { data: job, isLoading } = useQuery({
    queryKey: ['job', jobId],
    queryFn: async () => (await axios.get(`${API_BASE}/alerts/jobs/${jobId}`)).data,
    refetchInterval: (data: any) => (data?.status === 'Completed' || data?.status === 'Failed' ? false : 2000),
  });

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex justify-end">
        <motion.div 
          initial={{ opacity: 0 }} 
          animate={{ opacity: 1 }} 
          exit={{ opacity: 0 }}
          className="absolute inset-0 bg-black/60 backdrop-blur-sm"
          onClick={onClose}
        />
        <motion.div 
          initial={{ x: "100%" }} 
          animate={{ x: 0 }} 
          exit={{ x: "100%" }}
          transition={{ type: "spring", damping: 25, stiffness: 200 }}
          className="relative w-full max-w-md h-full bg-zinc-950 border-l border-zinc-800 shadow-2xl overflow-y-auto"
        >
          <div className="p-6 border-b border-zinc-800 flex justify-between items-center sticky top-0 bg-zinc-950/90 backdrop-blur">
            <h2 className="text-lg font-semibold text-zinc-100">Job Details</h2>
            <button onClick={onClose} className="p-2 hover:bg-zinc-800 rounded-full text-zinc-400 transition-colors">
              <X className="w-5 h-5" />
            </button>
          </div>
          
          <div className="p-6 space-y-8">
            {isLoading ? (
              <div className="text-zinc-500 animate-pulse">Loading job data...</div>
            ) : job ? (
              <>
                <Section title="Overview">
                  <Detail label="Job ID" value={job.id} mono />
                  <Detail label="Status" value={job.status} />
                  <Detail label="Worker" value={job.worker_id || "Unassigned"} />
                </Section>
                
                <Section title="Timings">
                  <Detail label="Created At" value={format(new Date(job.created_at), "PP pp")} />
                  <Detail label="Started At" value={job.started_at ? format(new Date(job.started_at), "PP pp") : "-"} />
                  <Detail label="Completed At" value={job.completed_at ? format(new Date(job.completed_at), "PP pp") : "-"} />
                  <Detail label="Total Processing" value={job.processing_time ? `${job.processing_time.toFixed(2)}s` : "-"} />
                </Section>

                <Section title="Pipeline Latencies">
                  <Detail label="AI Generation" value={job.ai_latency ? `${job.ai_latency.toFixed(2)}s` : "-"} />
                  <Detail label="Translation" value={job.translation_latency ? `${job.translation_latency.toFixed(2)}s` : "-"} />
                  <Detail label="TTS Audio" value={job.tts_latency ? `${job.tts_latency.toFixed(2)}s` : "-"} />
                  <Detail label="SMS Dispatch" value={job.sms_latency ? `${job.sms_latency.toFixed(2)}s` : "-"} />
                  <Detail label="Voice Dispatch" value={job.voice_latency ? `${job.voice_latency.toFixed(2)}s` : "-"} />
                </Section>

                {job.error_message && (
                  <Section title="Errors">
                    <div className="p-3 bg-red-900/20 border border-red-900/50 rounded-lg text-red-400 text-sm font-mono break-words">
                      {job.error_message}
                    </div>
                  </Section>
                )}
              </>
            ) : (
              <div className="text-red-400">Job not found</div>
            )}
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}

function Section({ title, children }: { title: string, children: React.ReactNode }) {
  return (
    <div className="space-y-3">
      <h3 className="text-xs font-semibold uppercase tracking-wider text-zinc-500">{title}</h3>
      <div className="space-y-2 bg-zinc-900/50 p-4 rounded-xl border border-zinc-800/50">
        {children}
      </div>
    </div>
  );
}

function Detail({ label, value, mono = false }: { label: string, value: string | React.ReactNode, mono?: boolean }) {
  return (
    <div className="flex justify-between items-start text-sm">
      <span className="text-zinc-400">{label}</span>
      <span className={`text-zinc-100 text-right ${mono ? 'font-mono text-xs' : ''}`}>{value}</span>
    </div>
  );
}
