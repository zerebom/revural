import { create } from "zustand";
import type { Issue } from "@/lib/types";

interface ReviewState {
  reviewId: string | null;
  prdText: string;
  issues: Issue[];
  expandedIssueId: string | null;
  viewMode: 'list' | 'detail';

  // Agent selection state
  selectedRoles: string[];
  selectedPreset: string | null;

  setReviewId: (id: string | null) => void;
  setPrdText: (text: string) => void;
  setIssues: (issues: Issue[]) => void;
  setExpandedIssueId: (issueId: string | null) => void;
  setViewMode: (mode: 'list' | 'detail') => void;
  updateIssueStatus: (issueId: string, status: string) => void;

  // Agent selection methods
  setSelectedRoles: (roles: string[]) => void;
  toggleRole: (role: string) => void;
  setSelectedPreset: (preset: string | null) => void;

  reset: () => void;
}

export const useReviewStore = create<ReviewState>((set) => ({
  reviewId: null,
  prdText: "",
  issues: [],
  expandedIssueId: null,
  viewMode: 'list',

  // Agent selection initial state
  selectedRoles: [],
  selectedPreset: null,

  setReviewId: (id) => set({ reviewId: id }),
  setPrdText: (text) => set({ prdText: text }),
  setIssues: (issues) => set({ issues }),
  setExpandedIssueId: (issueId) => set({ expandedIssueId: issueId }),
  setViewMode: (mode) => set({ viewMode: mode }),
  updateIssueStatus: (issueId, status) =>
    set((state) => ({
      issues: state.issues.map((i) => (i.issue_id === issueId ? { ...i, status } : i)),
    })),

  // Agent selection methods
  setSelectedRoles: (roles) => set({ selectedRoles: roles }),
  toggleRole: (role) =>
    set((state) => ({
      selectedRoles: state.selectedRoles.includes(role)
        ? state.selectedRoles.filter((r) => r !== role)
        : [...state.selectedRoles, role],
    })),
  setSelectedPreset: (preset) => set({ selectedPreset: preset }),

  reset: () => set({
    reviewId: null,
    prdText: "",
    issues: [],
    expandedIssueId: null,
    viewMode: 'list',
    selectedRoles: [],
    selectedPreset: null,
  }),
}));
