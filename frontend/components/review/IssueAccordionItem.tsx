"use client";

import { Badge } from "@/components/ui/badge";
import { AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import type { Issue } from "@/lib/types";
import { getAgentColorClasses } from "@/lib/utils";
import { useReviewStore } from "@/store/useReviewStore";

export default function IssueAccordionItem({
  issue,
  isSelected,
}: {
  issue: Issue;
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
    status === "done" ? "bg-emerald-600" : status === "later" ? "bg-amber-500" : "bg-slate-400";
  const triggerBase =
    "group flex w-full items-start gap-3 rounded-lg border border-transparent bg-white px-4 py-3 text-left transition-colors";
  const triggerSelected = isSelected ? "border-slate-300 bg-slate-50" : "hover:border-slate-200 hover:bg-slate-50";
  return (
    <AccordionItem value={issue.issue_id}>
      <AccordionTrigger className={`${triggerBase} ${triggerSelected}`}>
        <span className={`mt-1 h-2.5 w-2.5 flex-none rounded-full ${colors.bgActive.replace("bg-", "bg-")}`} />
        <div className="flex-1 min-w-0 space-y-1">
          <p className="typ-body truncate text-slate-900">{issue.summary || issue.comment || "(no summary)"}</p>
          <div className="flex items-center gap-2 text-slate-500">
            <span className="typ-caption truncate">{issue.agent_name}</span>
            <span className="h-1.5 w-1.5 rounded-full bg-slate-300" />
            <span className="typ-caption">
              {status === "done" ? "対応済み" : status === "later" ? "あとで" : "未対応"}
            </span>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className={`h-2.5 w-2.5 rounded-full ${statusDot}`} title={`status: ${status}`} />
          <Badge className={badgeClass}>優先度 {issue.priority}</Badge>
        </div>
      </AccordionTrigger>
      <AccordionContent className="px-4 pb-4 pt-1">
        <div className="space-y-3.5">
          <p className="typ-body whitespace-pre-wrap text-slate-800">{issue.comment}</p>
          <div>
            <p className="typ-caption text-slate-500 mb-1">元テキスト</p>
            <blockquote className="typ-body-sm whitespace-pre-wrap rounded-md bg-slate-50 p-3 pl-4 text-slate-800 border-l-4 border-slate-200">
              {issue.original_text}
            </blockquote>
          </div>
          <div>
            <button
              type="button"
              className="typ-body inline-flex items-center gap-2 rounded-md bg-slate-900 px-3.5 py-2 text-white transition-colors hover:bg-slate-800"
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
