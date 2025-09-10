"use client";

import useSWR from "swr";
import { api } from "@/lib/api";
import { useEffect } from "react";
import { useReviewStore } from "@/store/useReviewStore";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
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
  const markStatus = useReviewStore((s) => s.markStatus);
  const nextIssue = useReviewStore((s) => s.nextIssue);
  const router = useRouter();

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

  const handleDone = () => {
    markStatus(current.issue_id, "done");
    if (currentIssueIndex >= issues.length - 1) {
      router.push(`/reviews/${reviewId}/summary`);
    } else {
      nextIssue();
    }
  };

  const handleLater = () => {
    markStatus(current.issue_id, "later");
    if (currentIssueIndex >= issues.length - 1) {
      router.push(`/reviews/${reviewId}/summary`);
    } else {
      nextIssue();
    }
  };

  return (
    <div className="max-w-3xl mx-auto w-full space-y-4 pb-24">
      <h2 className="text-xl font-semibold">指摘事項の確認</h2>
      <p className="text-sm text-gray-600">AIからの提案を一つずつ確認していきましょう。</p>
      <IssueCard reviewId={reviewId} issue={current} position={currentIssueIndex + 1} total={issues.length} />
      <p className="text-xs text-gray-600 text-right">{currentIssueIndex + 1} / {issues.length}</p>

      {/* Sticky action bar */}
      <div className="fixed inset-x-0 bottom-0 z-50 pointer-events-none">
        <div className="mx-auto max-w-3xl px-4 pb-[env(safe-area-inset-bottom)]">
          <div className="pointer-events-auto rounded-t-md border border-b-0 bg-white/90 backdrop-blur supports-[backdrop-filter]:bg-white/80 shadow-sm">
            <div className="flex items-center justify-between gap-3 p-3">
              <span className="text-xs text-gray-600">
                {currentIssueIndex + 1} / {issues.length}
              </span>
              <div className="flex gap-2">
                <Button variant="outline" onClick={handleLater} className="border px-4 py-2 bg-white hover:bg-gray-50">
                  あとで対応
                </Button>
                <Button onClick={handleDone} className="bg-green-600 hover:bg-green-700">対応済みにする</Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
