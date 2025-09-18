"use client";

import { Accordion } from "@/components/ui/accordion";
import IssueAccordionItem from "@/components/review/IssueAccordionItem";
import type { Issue } from "@/lib/types";
import { useReviewStore } from "@/store/useReviewStore";

export default function IssueListView({ issues }: { issues: Issue[] }) {
  const expandedIssueId = useReviewStore((s) => s.expandedIssueId);
  const setExpandedIssueId = useReviewStore((s) => s.setExpandedIssueId);

  if (!issues || issues.length === 0) {
    return (
      <div className="typ-body flex h-full items-center justify-center rounded-lg bg-slate-50 text-slate-500">
        指摘事項はありませんでした。
      </div>
    );
  }

  return (
    <div className="h-full overflow-auto">
      <Accordion
        type="single"
        collapsible
        value={expandedIssueId ?? undefined}
        onValueChange={(v) => setExpandedIssueId((v as string) || null)}
        className="flex flex-col gap-2"
      >
        {issues.map((issue) => (
          <IssueAccordionItem key={issue.issue_id} issue={issue} isSelected={issue.issue_id === expandedIssueId} />
        ))}
      </Accordion>
    </div>
  );
}
