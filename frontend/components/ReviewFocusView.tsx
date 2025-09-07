"use client";

import useSWR from "swr";
import { api } from "@/lib/api";
import { useEffect } from "react";
import { useReviewStore } from "@/store/useReviewStore";
import LoadingSpinner from "./LoadingSpinner";
import IssueCard from "./IssueCard";

export default function ReviewFocusView({ reviewId }: { reviewId: string }) {
  const { data, error, isLoading } = useSWR(["review", reviewId], () => api.getReview(reviewId), {
    refreshInterval: (latestData) => (latestData?.status === "processing" ? 1500 : 0),
    revalidateOnFocus: false,
  });

  const setIssues = useReviewStore((s) => s.setIssues);
  const currentIssueIndex = useReviewStore((s) => s.currentIssueIndex);
  const issues = useReviewStore((s) => s.issues);

  useEffect(() => {
    if (data?.status === "completed" && data.issues && data.issues.length > 0) {
      setIssues(data.issues);
    }
  }, [data, setIssues]);

  if (error) return <p className="text-red-600">読み込みに失敗しました: {String(error)}</p>;
  if (isLoading || data?.status === "processing") return <LoadingSpinner />;
  if (data?.status === "failed") return <p className="text-red-600">レビューの実行に失敗しました。</p>;
  if (data?.status === "not_found") return <p className="text-gray-600">レビューが見つかりません。</p>;

  if (!issues || issues.length === 0) {
    return <p className="text-gray-700">指摘事項はありませんでした。</p>;
  }

  const current = issues[currentIssueIndex];
  return (
    <div className="max-w-3xl mx-auto w-full space-y-4">
      <h2 className="text-xl font-semibold">フォーカスモード</h2>
      <IssueCard reviewId={reviewId} issue={current} />
      <p className="text-xs text-gray-600 text-right">{currentIssueIndex + 1} / {issues.length}</p>
    </div>
  );
}
