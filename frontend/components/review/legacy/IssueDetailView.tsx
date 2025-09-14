"use client";

import { useMemo } from "react";
import type { Issue } from "@/lib/types";
import IssueCard from "@/components/review/legacy/IssueCard";

type Props = {
  reviewId: string;
  issues: Issue[];
  selectedIssueId: string | null;
};

export default function IssueDetailView({ reviewId, issues, selectedIssueId }: Props) {
  const { current, position, total } = useMemo(() => {
    const total = issues.length;
    const idx = selectedIssueId ? issues.findIndex((i) => i.issue_id === selectedIssueId) : -1;
    return { current: idx >= 0 ? issues[idx] : null, position: idx >= 0 ? idx + 1 : 0, total };
  }, [issues, selectedIssueId]);

  if (!issues || issues.length === 0) {
    return (
      <div className="h-full rounded border bg-white p-4 text-sm text-gray-600">
        指摘事項はありませんでした。
      </div>
    );
  }

  if (!current) {
    return (
      <div className="h-full rounded border bg-white p-6 text-sm text-gray-700 space-y-2">
        <p className="font-medium">ハイライトを選択してください</p>
        <p className="text-gray-600">左のPRDテキストでハイライトをクリックすると詳細が表示されます。</p>
      </div>
    );
  }

  return (
    <div className="h-full overflow-auto">
      <IssueCard reviewId={reviewId} issue={current} position={position} total={total} />
    </div>
  );
}
