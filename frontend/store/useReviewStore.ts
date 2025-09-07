import { create } from "zustand";
import type { Issue } from "@/lib/types";

type IssueStatus = "pending" | "done" | "later";

interface ReviewState {
  reviewId: string | null;
  prdText: string;
  issues: Issue[];
  currentIssueIndex: number;
  issueStatuses: Record<string, IssueStatus>;

  setReviewId: (id: string | null) => void;
  setPrdText: (text: string) => void;
  setIssues: (issues: Issue[]) => void;
  markStatus: (issueId: string, status: IssueStatus) => void;
  nextIssue: () => void;
  reset: () => void;
}

export const useReviewStore = create<ReviewState>((set, get) => ({
  reviewId: null,
  prdText: "",
  issues: [],
  currentIssueIndex: 0,
  issueStatuses: {},

  setReviewId: (id) => set({ reviewId: id }),
  setPrdText: (text) => set({ prdText: text }),
  setIssues: (issues) =>
    set({
      issues,
      currentIssueIndex: 0,
      issueStatuses: issues.reduce<Record<string, IssueStatus>>((acc, it) => {
        acc[it.issue_id] = acc[it.issue_id] ?? "pending";
        return acc;
      }, {}),
    }),
  markStatus: (issueId, status) =>
    set({ issueStatuses: { ...get().issueStatuses, [issueId]: status } }),
  nextIssue: () => {
    const { currentIssueIndex, issues } = get();
    if (currentIssueIndex < issues.length - 1) {
      set({ currentIssueIndex: currentIssueIndex + 1 });
    }
  },
  reset: () => set({ reviewId: null, prdText: "", issues: [], currentIssueIndex: 0, issueStatuses: {} }),
}));
