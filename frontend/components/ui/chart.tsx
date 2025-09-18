"use client";

import * as React from "react";
import type { TooltipProps } from "recharts";
import { cn } from "@/lib/utils";

type ChartConfigEntry = {
  label?: string;
  color?: string;
};

export type ChartConfig = Record<string, ChartConfigEntry>;

type ChartContainerProps = React.HTMLAttributes<HTMLDivElement> & {
  config?: ChartConfig;
};

export function ChartContainer({ config, className, children, ...props }: ChartContainerProps) {
  const style = React.useMemo(() => {
    const cssVars: Record<string, string> = {};
    if (config) {
      Object.entries(config).forEach(([key, value]) => {
        if (value?.color) {
          const safeKey = key.replace(/[^a-z0-9-]/gi, "-").toLowerCase();
          cssVars[`--chart-${safeKey}`] = value.color;
        }
      });
    }
    return cssVars;
  }, [config]);

  return (
    <div
      className={cn("rounded-2xl border border-slate-200/60 bg-white p-6", className)}
      style={style as React.CSSProperties}
      {...props}
    >
      {children}
    </div>
  );
}

export function ChartTooltipContent({ active, payload, label }: TooltipProps<number, string>) {
  if (!active || !payload || payload.length === 0) return null;
  const { value, payload: datum } = payload[0];
  const name = (datum?.name as string) ?? label;
  return (
    <div className="rounded-lg border border-slate-200 bg-white/95 px-3 py-2 text-slate-900 shadow-sm">
      {name && <p className="typ-caption text-slate-500">{name}</p>}
      <p className="typ-body font-semibold">{value ?? 0}件</p>
    </div>
  );
}

export function ChartEmptyState({ message }: { message: string }) {
  return (
    <div className="flex h-52 items-center justify-center rounded-xl border border-dashed border-slate-200 bg-slate-50/80">
      <p className="typ-caption text-slate-500">{message}</p>
    </div>
  );
}
