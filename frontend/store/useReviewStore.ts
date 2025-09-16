import { create } from "zustand";
import type { Issue } from "@/lib/types";

interface ReviewState {
  reviewId: string | null;
  prdText: string;
  issues: Issue[];
  expandedIssueId: string | null;
  viewMode: 'list' | 'detail';

  setReviewId: (id: string | null) => void;
  setPrdText: (text: string) => void;
  setIssues: (issues: Issue[]) => void;
  setExpandedIssueId: (issueId: string | null) => void;
  setViewMode: (mode: 'list' | 'detail') => void;
  updateIssueStatus: (issueId: string, status: string) => void;
  reset: () => void;
}

export const useReviewStore = create<ReviewState>((set) => ({
  reviewId: null,
  prdText: "",
  issues: [],
  expandedIssueId: null,
  viewMode: 'list',

  setReviewId: (id) => set({ reviewId: id }),
  setPrdText: (text) => set({ prdText: text }),
  setIssues: (issues) => set({ issues }),
  setExpandedIssueId: (issueId) => set({ expandedIssueId: issueId }),
  setViewMode: (mode) => set({ viewMode: mode }),
  updateIssueStatus: (issueId, status) =>
    set((state) => ({
      issues: state.issues.map((i) => (i.issue_id === issueId ? { ...i, status } : i)),
    })),
  reset: () => set({ reviewId: null, prdText: "", issues: [], expandedIssueId: null, viewMode: 'list' }),
}));
