"use client";

import { Badge } from "@/components/ui/badge";
import { AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import type { Issue } from "@/lib/types";
import { getAgentColorClasses } from "@/lib/utils";
import { useReviewStore } from "@/store/useReviewStore";

export default function IssueAccordionItem({
  issue,
  reviewId,
  isSelected,
}: {
  issue: Issue;
  reviewId: string;
  isSelected?: boolean;
}) {
  // Avoid 'destructive' variant because theme tokens may make it unreadable.
  const badgeClass =
    issue.priority === 1
      ? "bg-red-100 text-red-800 border-red-200"
      : issue.priority === 2
        ? "bg-amber-100 text-amber-800 border-amber-200"
        : "bg-gray-100 text-gray-800 border-gray-200";
  const colors = getAgentColorClasses(issue.agent_name);
  const setViewMode = useReviewStore((s) => s.setViewMode);
  const setExpandedIssueId = useReviewStore((s) => s.setExpandedIssueId);
  const status = issue.status || "pending";
  const statusDot =
    status === "done" ? "bg-emerald-600" : status === "later" ? "bg-amber-500" : "bg-gray-500";
  return (
    <AccordionItem value={issue.issue_id}>
      <AccordionTrigger className={`px-3 ${isSelected ? `${colors.bgActive} ring-1 ${colors.ring}` : ""}`}>
        <div className="flex w-full items-center gap-3 min-w-0">
          <span className={`h-2.5 w-2.5 rounded-full flex-none ${colors.bgActive.replace("bg-", "bg-")}`} />
          <div className="flex-1 min-w-0">
            <p className="truncate text-gray-900">{issue.summary || issue.comment || "(no summary)"}</p>
            <p className="text-xs text-gray-600 truncate">{issue.agent_name}</p>
          </div>
          <div className="flex items-center gap-2">
            <span className={`h-2.5 w-2.5 rounded-full ${statusDot}`} title={`status: ${status}`} />
            <Badge className={badgeClass}>優先度 {issue.priority}</Badge>
          </div>
        </div>
      </AccordionTrigger>
      <AccordionContent className="px-4 py-4">
        <div className="space-y-4">
          <p className="whitespace-pre-wrap text-gray-800 leading-5">{issue.comment}</p>
          <div>
            <p className="text-xs text-gray-600 mb-1 mt-2">元テキスト</p>
            <blockquote className="whitespace-pre-wrap text-sm bg-gray-50/80 border-l-4 border-gray-200 rounded-md p-3.5 text-gray-800">
              {issue.original_text}
            </blockquote>
          </div>
          <div>
            <button
              type="button"
              className="text-sm px-3.5 py-2 rounded border border-gray-300 bg-white hover:bg-gray-50 shadow-sm mt-2"
              onClick={(e) => {
                e.preventDefault();
                setExpandedIssueId(issue.issue_id);
                setViewMode('detail');
              }}
            >
              論点を深掘りする
            </button>
          </div>
        </div>
      </AccordionContent>
    </AccordionItem>
  );
}
