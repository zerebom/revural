"use client";

import { Accordion } from "@/components/ui/accordion";
import IssueAccordionItem from "@/components/review/IssueAccordionItem";
import type { Issue } from "@/lib/types";
import { useReviewStore } from "@/store/useReviewStore";

export default function IssueListView({ reviewId, issues }: { reviewId: string; issues: Issue[] }) {
  const expandedIssueId = useReviewStore((s) => s.expandedIssueId);
  const setExpandedIssueId = useReviewStore((s) => s.setExpandedIssueId);

  if (!issues || issues.length === 0) {
    return (
      <div className="h-full rounded border bg-white p-4 text-sm text-gray-600">指摘事項はありませんでした。</div>
    );
  }

  return (
    <div className="h-full overflow-auto rounded border bg-white p-2">
      <Accordion
        type="single"
        collapsible
        value={expandedIssueId ?? undefined}
        onValueChange={(v) => setExpandedIssueId((v as string) || null)}
      >
        {issues.map((issue) => (
          <IssueAccordionItem
            key={issue.issue_id}
            issue={issue}
            reviewId={reviewId}
            isSelected={issue.issue_id === expandedIssueId}
          />
        ))}
      </Accordion>
    </div>
  );
}
