"use client";

import type { Issue } from "@/lib/types";
import { useReviewStore } from "@/store/useReviewStore";
import ChatWindow from "./ChatWindow";
import SuggestionBox from "./SuggestionBox";
import { useRouter } from "next/navigation";

export default function IssueCard({ reviewId, issue }: { reviewId: string; issue: Issue }) {
  const { nextIssue, markStatus } = useReviewStore();
  const currentIndex = useReviewStore((s) => s.currentIssueIndex);
  const issues = useReviewStore((s) => s.issues);
  const router = useRouter();

  const done = () => {
    markStatus(issue.issue_id, "done");
    if (currentIndex >= issues.length - 1) {
      router.push(`/reviews/${reviewId}/summary`);
    } else {
      nextIssue();
    }
  };
  const later = () => {
    markStatus(issue.issue_id, "later");
    if (currentIndex >= issues.length - 1) {
      router.push(`/reviews/${reviewId}/summary`);
    } else {
      nextIssue();
    }
  };

  return (
    <div className="border rounded-md p-4 space-y-4 bg-white dark:bg-gray-800 dark:border-gray-700">
      <div className="flex items-start justify-between gap-4">
        <div className="space-y-1">
          <h3 className="text-lg font-semibold">{issue.agent_name} の指摘</h3>
          <p className="text-sm text-gray-700 dark:text-gray-200 whitespace-pre-wrap">{issue.comment}</p>
        </div>
        <span className="inline-flex items-center text-xs px-2 py-1 rounded bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-100">優先度: {issue.priority}</span>
      </div>

      <div>
        <p className="text-xs text-gray-600 mb-1">元テキスト</p>
        <pre className="whitespace-pre-wrap text-sm bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded p-2 text-gray-800 dark:text-gray-100">{issue.original_text}</pre>
      </div>

      <ChatWindow reviewId={reviewId} issueId={issue.issue_id} />
      <SuggestionBox reviewId={reviewId} issueId={issue.issue_id} />

      <div className="flex justify-end gap-2">
        <button onClick={later} className="rounded border px-3 py-1 hover:bg-gray-50 dark:hover:bg-gray-700">あとで</button>
        <button onClick={done} className="rounded bg-green-600 text-white px-3 py-1 hover:bg-green-700">対応済み</button>
      </div>
    </div>
  );
}
