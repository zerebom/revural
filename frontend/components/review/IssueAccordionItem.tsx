"use client";

import { Badge } from "@/components/ui/badge";
import { AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import type { Issue } from "@/lib/types";
import { getAgentColorClasses } from "@/lib/utils";

export default function IssueAccordionItem({
  issue,
  reviewId,
  isSelected,
}: {
  issue: Issue;
  reviewId: string;
  isSelected?: boolean;
}) {
  const priorityVariant = issue.priority === 1 ? "destructive" : issue.priority === 2 ? "warning" : "secondary";
  const colors = getAgentColorClasses(issue.agent_name);
  return (
    <AccordionItem value={issue.issue_id}>
      <AccordionTrigger className={`px-3 ${isSelected ? `${colors.bgActive} ring-1 ${colors.ring}` : ""}`}>
        <div className="flex w-full items-center gap-3 min-w-0">
          <span className={`h-2.5 w-2.5 rounded-full flex-none ${colors.bgActive.replace("bg-", "bg-")}`} />
          <div className="flex-1 min-w-0">
            <p className="truncate text-gray-900">{issue.summary || issue.comment || "(no summary)"}</p>
            <p className="text-xs text-gray-600 truncate">{issue.agent_name}</p>
          </div>
          <Badge variant={priorityVariant}>優先度 {issue.priority}</Badge>
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
              // NOTE: 実装はマイルストーン2で行う
              onClick={(e) => e.preventDefault()}
            >
              AIに質問する（準備中）
            </button>
          </div>
        </div>
      </AccordionContent>
    </AccordionItem>
  );
}
