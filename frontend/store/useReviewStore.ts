import { create } from "zustand";
import type { Issue } from "@/lib/types";

interface ReviewState {
  reviewId: string | null;
  prdText: string;
  issues: Issue[];
  selectedIssueId: string | null;

  setReviewId: (id: string | null) => void;
  setPrdText: (text: string) => void;
  setIssues: (issues: Issue[]) => void;
  setSelectedIssueId: (issueId: string | null) => void;
  reset: () => void;
}

export const useReviewStore = create<ReviewState>((set) => ({
  reviewId: null,
  prdText: "",
  issues: [],
  selectedIssueId: null,

  setReviewId: (id) => set({ reviewId: id }),
  setPrdText: (text) => set({ prdText: text }),
  setIssues: (issues) => set({ issues }),
  setSelectedIssueId: (issueId) => set({ selectedIssueId: issueId }),
  reset: () => set({ reviewId: null, prdText: "", issues: [], selectedIssueId: null }),
}));
