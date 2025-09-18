"use client";

import useSWR from "swr";
import { api } from "@/lib/api";
import React, { useEffect } from "react";
import { useReviewStore } from "@/store/useReviewStore";
import LoadingSpinner from "@/components/LoadingSpinner";
import ReviewPage from "@/components/ReviewPage";

export default function ReviewDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = React.use(params);
  const setIssues = useReviewStore((s) => s.setIssues);
  const setReviewId = useReviewStore((s) => s.setReviewId);
  const expandedIssueId = useReviewStore((s) => s.expandedIssueId);
  const setExpandedIssueId = useReviewStore((s) => s.setExpandedIssueId);
  const setPrdText = useReviewStore((s) => s.setPrdText);

  const { data, error, isLoading } = useSWR(["review", id], () => api.getReview(id), {
    refreshInterval: (latestData) => (latestData?.status === "processing" ? 1500 : 0),
    revalidateOnFocus: false,
  });

  useEffect(() => {
    setReviewId(id);
  }, [id, setReviewId]);

  useEffect(() => {
    // Hydrate PRD text if present in response (supports reload/deep-link)
    if (typeof data?.prd_text === "string") {
      setPrdText(data.prd_text);
    }
    if (data?.status === "completed" && data.issues && data.issues.length > 0) {
      setIssues(data.issues);
      if (!expandedIssueId) {
        setExpandedIssueId(data.issues[0].issue_id);
      }
    }
  }, [data, setIssues, expandedIssueId, setExpandedIssueId, setPrdText]);

  if (error) return <p className="text-red-600 p-6">読み込みに失敗しました: {String(error)}</p>;
  if (isLoading || data?.status === "processing") return <LoadingSpinner />;
  if (data?.status === "failed") return <p className="text-red-600 p-6">レビューの実行に失敗しました。</p>;
  if (data?.status === "not_found") return <p className="text-gray-600 p-6">レビューが見つかりません。</p>;

  return <ReviewPage />;
}
