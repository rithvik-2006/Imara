"use client";
import * as React from "react";
import { cn } from "@/lib/utils";
import { motion } from "framer-motion";

export interface ProgressProps extends React.HTMLAttributes<HTMLDivElement> {
  value?: number;
  indicatorColor?: string;
}

const Progress = React.forwardRef<HTMLDivElement, ProgressProps>(({ className, value, indicatorColor, ...props }, ref) => {
  return (
    <div
      ref={ref}
      className={cn("relative h-2 w-full overflow-hidden rounded-full bg-zinc-800", className)}
      {...props}
    >
      <motion.div
        className={cn("h-full w-full flex-1 bg-zinc-50 transition-all", indicatorColor)}
        initial={{ x: "-100%" }}
        animate={{ x: `-${100 - (value || 0)}%` }}
        transition={{ duration: 0.5, ease: "easeInOut" }}
      />
    </div>
  );
});
Progress.displayName = "Progress";

export { Progress };
