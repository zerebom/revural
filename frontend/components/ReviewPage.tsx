"use client";

import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
  type CSSProperties,
  type PointerEvent as ReactPointerEvent,
} from "react";
import { useRouter } from "next/navigation";
import { useReviewStore } from "@/store/useReviewStore";
import PrdTextView from "@/components/PrdTextView";
import IssueListView from "@/components/review/IssueListView";
import IssueDetailView from "@/components/review/IssueDetailView";
import { AnimatePresence, motion } from "framer-motion";
import Header from "@/components/layout/Header";
import type { Issue } from "@/lib/types";

export default function ReviewPage() {
  const prdText = useReviewStore((s) => s.prdText);
  const issues = useReviewStore((s) => s.issues);
  const reviewId = useReviewStore((s) => s.reviewId) || "";
  const expandedIssueId = useReviewStore((s) => s.expandedIssueId);
  const setExpandedIssueId = useReviewStore((s) => s.setExpandedIssueId);
  const viewMode = useReviewStore((s) => s.viewMode);
  const router = useRouter();

  const onSelect = useCallback(
    (id: string) => {
      setExpandedIssueId(id);
    },
    [setExpandedIssueId]
  );

  const documentTitle = useMemo(() => {
    const text = (prdText || "").trim();
    if (!text) return "レビュー";
    const firstMeaningfulLine = text
      .split(/\r?\n/)
      .map((line) => line.trim())
      .find((line) => line.length > 0);
    if (!firstMeaningfulLine) return "レビュー";
    return firstMeaningfulLine.replace(/^#+\s*/, "");
  }, [prdText]);

  const handleSummary = useCallback(() => {
    if (!reviewId) return;
    router.push(`/reviews/${reviewId}/summary`);
  }, [reviewId, router]);

  const handleExport = useCallback(() => {
    console.warn("エクスポート機能は未実装です");
  }, []);

  const handleBack = useCallback(() => {
    router.back();
  }, [router]);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <div className="flex min-h-screen flex-col">
        <Header
          title={documentTitle}
          onBack={handleBack}
          onSummary={handleSummary}
          onExport={handleExport}
          className="sticky top-0 z-30 border-b border-slate-200/80 bg-white/90 px-6 py-4 backdrop-blur"
        />
        <main className="flex-1 px-6 pb-8 pt-4">
          <div className="flex h-full min-h-[520px] flex-col gap-4">
            <div className="flex items-center justify-between px-2 typ-caption text-slate-500">
              <span>PRDと指摘を並べて確認できます。ドラッグで幅を調整してください。</span>
              <span>{issues.length} 件の指摘</span>
            </div>
            <ResizableWorkspace
              viewMode={viewMode}
              expandedIssueId={expandedIssueId}
              reviewId={reviewId}
              issues={issues}
              prdText={prdText}
              onSelect={onSelect}
            />
          </div>
        </main>
      </div>
    </div>
  );
}

interface ResizableWorkspaceProps {
  viewMode: 'list' | 'detail';
  expandedIssueId: string | null;
  reviewId: string;
  issues: Issue[];
  prdText: string;
  onSelect: (id: string) => void;
}

function ResizableWorkspace({ viewMode, expandedIssueId, reviewId, issues, prdText, onSelect }: ResizableWorkspaceProps) {
  const [ratio, setRatio] = useState(0.62);
  const [isResizing, setIsResizing] = useState(false);
  const [isStacked, setIsStacked] = useState(false);
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const updateLayout = () => {
      if (typeof window === "undefined") return;
      setIsStacked(window.innerWidth < 1024);
    };

    updateLayout();
    window.addEventListener("resize", updateLayout);
    return () => window.removeEventListener("resize", updateLayout);
  }, []);

  useEffect(() => {
    if (!isResizing || isStacked) return;

    const handlePointerMove = (event: PointerEvent) => {
      if (!containerRef.current) return;
      const rect = containerRef.current.getBoundingClientRect();
      const next = (event.clientX - rect.left) / rect.width;
      if (Number.isNaN(next)) return;
      const clamped = Math.min(Math.max(next, 0.3), 0.78);
      setRatio(clamped);
    };

    const stop = () => setIsResizing(false);

    window.addEventListener("pointermove", handlePointerMove);
    window.addEventListener("pointerup", stop);
    window.addEventListener("pointercancel", stop);

    return () => {
      window.removeEventListener("pointermove", handlePointerMove);
      window.removeEventListener("pointerup", stop);
      window.removeEventListener("pointercancel", stop);
    };
  }, [isResizing, isStacked]);

  const startResize = useCallback((event: ReactPointerEvent<HTMLDivElement>) => {
    if (isStacked) return;
    event.preventDefault();
    setIsResizing(true);
  }, [isStacked]);

  const resetRatio = useCallback(() => {
    setRatio(0.62);
  }, []);

  const leftWidth = `${Math.round(ratio * 1000) / 10}%`;
  const leftPaneStyle = useMemo<CSSProperties | undefined>(() => {
    if (isStacked) return undefined;
    return { width: leftWidth };
  }, [isStacked, leftWidth]);

  const containerClasses = `relative flex flex-1 min-h-0 gap-4 rounded-2xl border border-slate-200/40 bg-white/80 p-4 ${
    isStacked ? "flex-col" : "flex-row"
  }`;

  return (
    <div ref={containerRef} className={containerClasses}>
      <section className="flex min-h-0 min-w-[280px] flex-col rounded-xl bg-white px-5 pb-5 pt-4" style={leftPaneStyle}>
        <header className="mb-3 flex items-center justify-between gap-3">
          <h2 className="typ-heading-xs text-slate-900">PRD ドキュメント</h2>
          <button
            type="button"
            onClick={resetRatio}
            className="hidden typ-caption text-slate-400 transition-colors hover:text-slate-600 sm:inline-flex"
          >
            幅をリセット
          </button>
        </header>
        <div className="flex-1 min-h-0">
          <PrdTextView
            prdText={prdText}
            issues={issues}
            expandedIssueId={expandedIssueId}
            onSelect={onSelect}
          />
        </div>
      </section>
      {!isStacked && (
        <div
          role="separator"
          aria-orientation="vertical"
          aria-label="パネル幅を調整"
          tabIndex={0}
          onPointerDown={startResize}
          className="group relative w-3 cursor-col-resize select-none"
        >
          <div
            className={`absolute inset-y-1 inset-x-1/3 rounded-full transition-colors ${
              isResizing ? "bg-slate-300/70" : "group-hover:bg-slate-300/50"
            }`}
          />
          <div className="absolute inset-y-2 left-1/2 w-px -translate-x-1/2 bg-slate-300/80" />
        </div>
      )}
      <section className="flex min-h-0 min-w-[260px] flex-1 flex-col rounded-xl bg-white px-5 pb-5 pt-4">
        <AnimatePresence mode="popLayout" initial={false}>
          {viewMode === 'list' ? (
            <motion.div
              key="list"
              initial={{ x: 24, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: -24, opacity: 0 }}
              transition={{ type: "tween", duration: 0.18 }}
              className="flex h-full min-h-0 flex-col"
            >
              <div className="mb-3 flex items-center justify-between">
                <h2 className="typ-heading-xs text-slate-900">指摘一覧</h2>
              </div>
              <div className="flex-1 min-h-0">
                <IssueListView issues={issues} />
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="detail"
              initial={{ x: 24, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: -24, opacity: 0 }}
              transition={{ type: "tween", duration: 0.18 }}
              className="flex h-full min-h-0 flex-col"
            >
              <div className="flex-1 min-h-0">
                {expandedIssueId && (
                  <IssueDetailView
                    reviewId={reviewId}
                    issue={issues.find((i) => i.issue_id === expandedIssueId) || issues[0]}
                  />
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </section>
    </div>
  );
}
