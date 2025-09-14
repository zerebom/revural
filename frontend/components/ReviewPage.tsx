"use client";

import { useCallback } from "react";
import { useReviewStore } from "@/store/useReviewStore";
import PrdTextView from "@/components/PrdTextView";
import IssueListView from "@/components/review/IssueListView";
import IssueDetailView from "@/components/review/IssueDetailView";
import { AnimatePresence, motion } from "framer-motion";

export default function ReviewPage() {
  const prdText = useReviewStore((s) => s.prdText);
  const issues = useReviewStore((s) => s.issues);
  const reviewId = useReviewStore((s) => s.reviewId) || "";
  const expandedIssueId = useReviewStore((s) => s.expandedIssueId);
  const setExpandedIssueId = useReviewStore((s) => s.setExpandedIssueId);
  const viewMode = useReviewStore((s) => s.viewMode);

  const onSelect = useCallback(
    (id: string) => {
      setExpandedIssueId(id);
    },
    [setExpandedIssueId]
  );

  return (
    <div className="min-h-[calc(100vh-4rem)] grid grid-cols-12 gap-4">
      <section className="col-span-12 lg:col-span-7 xl:col-span-8 flex flex-col">
        <h2 className="text-lg font-semibold mb-2">PRD</h2>
        <div className="flex-1">
          <PrdTextView prdText={prdText} issues={issues} expandedIssueId={expandedIssueId} onSelect={onSelect} />
      </div>
    </section>
    <section className="col-span-12 lg:col-span-5 xl:col-span-4 flex flex-col overflow-hidden">
      <AnimatePresence mode="popLayout" initial={false}>
        {viewMode === 'list' ? (
          <motion.div
            key="list"
            initial={{ x: 40, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: -40, opacity: 0 }}
            transition={{ type: "tween", duration: 0.2 }}
            className="flex-1 flex flex-col"
          >
            <h2 className="text-lg font-semibold mb-2">指摘一覧</h2>
            <div className="flex-1">
              <IssueListView reviewId={reviewId} issues={issues} />
            </div>
          </motion.div>
        ) : (
          <motion.div
            key="detail"
            initial={{ x: 40, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: -40, opacity: 0 }}
            transition={{ type: "tween", duration: 0.2 }}
            className="flex-1 flex flex-col"
          >
            <h2 className="text-lg font-semibold mb-2">論点の深掘り</h2>
            <div className="flex-1">
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
