"use client";

import { ChevronLeftIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface HeaderProps {
  title: string;
  onBack?: () => void;
  onSummary?: () => void;
  onExport?: () => void;
  className?: string;
}

export default function Header({ title, onBack, onSummary, onExport, className }: HeaderProps) {
  return (
    <header
      className={cn(
        "flex items-center justify-between gap-4 border-b border-slate-200 bg-white px-6 py-3",
        className
      )}
    >
      <div className="flex items-center gap-3 min-w-0">
        {onBack ? (
          <button
            type="button"
            onClick={onBack}
            className="inline-flex items-center gap-1.5 rounded-lg border border-slate-300 bg-white px-3 py-1.5 typ-body-sm font-medium text-slate-700 transition-colors hover:border-slate-400 hover:bg-slate-50 whitespace-nowrap"
          >
            <ChevronLeftIcon className="h-4 w-4" />
            <span>戻る</span>
          </button>
        ) : (
          <div className="w-[88px]" aria-hidden="true" />
        )}
        <div className="min-w-0">
          <p className="truncate typ-heading-xs text-slate-900" title={title}>
            {title || "レビュー"}
          </p>
        </div>
      </div>
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={onSummary}
          className="inline-flex items-center rounded-lg border border-slate-300 bg-white px-4 py-1.5 typ-body-sm font-medium text-slate-700 transition-colors hover:border-slate-400 hover:bg-slate-50 whitespace-nowrap"
        >
          サマリー
        </button>
        <button
          type="button"
          onClick={onExport}
          className="inline-flex items-center rounded-lg border border-slate-300 bg-white px-4 py-1.5 typ-body-sm font-medium text-slate-700 transition-colors hover:border-slate-400 hover:bg-slate-50 whitespace-nowrap"
        >
          エクスポート
        </button>
      </div>
    </header>
  );
}
