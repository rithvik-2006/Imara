import * as React from "react";
import { cn } from "@/lib/utils";

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "secondary" | "destructive" | "outline" | "success" | "warning";
}

function Badge({ className, variant = "default", ...props }: BadgeProps) {
  const variants = {
    default: "border-transparent bg-zinc-100 text-zinc-900",
    secondary: "border-transparent bg-zinc-800 text-zinc-100",
    destructive: "border-transparent bg-red-900/50 text-red-300",
    success: "border-transparent bg-green-900/50 text-green-300",
    warning: "border-transparent bg-yellow-900/50 text-yellow-300",
    outline: "text-zinc-100",
  };

  return (
    <div
      className={cn(
        "inline-flex items-center rounded-md border border-zinc-800 px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-zinc-400 focus:ring-offset-2",
        variants[variant],
        className
      )}
      {...props}
    />
  );
}

export { Badge };
