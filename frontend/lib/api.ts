import { ReviewStatusResponse, ReviewStartResponse, ReviewSummaryResponse } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

async function http<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
    cache: "no-store",
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`API error ${res.status}: ${text}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  startReview: (prd_text: string, panel_type?: string | null) =>
    http<ReviewStartResponse>("/reviews", {
      method: "POST",
      body: JSON.stringify({ prd_text, panel_type: panel_type ?? null }),
    }),

  getReview: (review_id: string) => http<ReviewStatusResponse>(`/reviews/${review_id}`),

  dialog: (review_id: string, issue_id: string, question_text: string) =>
    http<{ response_text: string }>(`/reviews/${review_id}/issues/${issue_id}/dialog`, {
      method: "POST",
      body: JSON.stringify({ question_text }),
    }),

  suggest: (review_id: string, issue_id: string) =>
    http<{ suggested_text: string; target_text: string }>(
      `/reviews/${review_id}/issues/${issue_id}/suggest`,
      { method: "POST" }
    ),

  applySuggestion: (review_id: string, issue_id: string) =>
    http<{ status: "success" | "failed" }>(
      `/reviews/${review_id}/issues/${issue_id}/apply_suggestion`,
      { method: "POST" }
    ),

  updateIssueStatus: (review_id: string, issue_id: string, status: string) =>
    http<{ status: "success" | "failed" }>(
      `/reviews/${review_id}/issues/${issue_id}/status`,
      { method: "PATCH", body: JSON.stringify({ status }) }
    ),

  getReviewSummary: (review_id: string) => http<ReviewSummaryResponse>(`/reviews/${review_id}/summary`),
};
