import { create } from "zustand";
import type { Issue } from "@/lib/types";

interface ReviewState {
  reviewId: string | null;
  prdText: string;
  issues: Issue[];
  expandedIssueId: string | null;

  setReviewId: (id: string | null) => void;
  setPrdText: (text: string) => void;
  setIssues: (issues: Issue[]) => void;
  setExpandedIssueId: (issueId: string | null) => void;
  reset: () => void;
}

export const useReviewStore = create<ReviewState>((set) => ({
  reviewId: null,
  prdText: "",
  issues: [],
  expandedIssueId: null,

  setReviewId: (id) => set({ reviewId: id }),
  setPrdText: (text) => set({ prdText: text }),
  setIssues: (issues) => set({ issues }),
  setExpandedIssueId: (issueId) => set({ expandedIssueId: issueId }),
  reset: () => set({ reviewId: null, prdText: "", issues: [], expandedIssueId: null }),
}));
