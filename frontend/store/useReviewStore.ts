import { create } from "zustand";
import type { Issue, AgentRole } from "@/lib/types";

interface ReviewState {
  reviewId: string | null;
  prdText: string;
  issues: Issue[];
  expandedIssueId: string | null;
  viewMode: 'list' | 'detail';

  // Agent information
  agents: AgentRole[];

  // Agent selection state
  selectedRoles: string[];
  selectedPreset: string | null;

  setReviewId: (id: string | null) => void;
  setPrdText: (text: string) => void;
  setIssues: (issues: Issue[]) => void;
  setExpandedIssueId: (issueId: string | null) => void;
  setViewMode: (mode: 'list' | 'detail') => void;
  updateIssueStatus: (issueId: string, status: string) => void;

  // Agent methods
  setAgents: (agents: AgentRole[]) => void;
  getAgentByName: (agentName: string) => AgentRole | undefined;

  // Agent selection methods
  setSelectedRoles: (roles: string[]) => void;
  toggleRole: (role: string) => void;
  setSelectedPreset: (preset: string | null) => void;

  reset: () => void;
}

export const useReviewStore = create<ReviewState>((set, get) => ({
  reviewId: null,
  prdText: "",
  issues: [],
  expandedIssueId: null,
  viewMode: 'list',

  // Agent information initial state
  agents: [],

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

  // Agent methods
  setAgents: (agents) => set({ agents }),
  getAgentByName: (agentName) => {
    const state = get();
    // Try matching by display name first (e.g., "Engineer Specialist")
    const byDisplayName = state.agents.find(a => a.display_name === agentName);
    if (byDisplayName) return byDisplayName;

    // Fallback: try matching by role (e.g., "engineer")
    const byRole = state.agents.find(a => a.role === agentName.toLowerCase());
    if (byRole) return byRole;

    // Fallback: partial matching
    return state.agents.find(a =>
      a.display_name.toLowerCase().includes(agentName.toLowerCase()) ||
      agentName.toLowerCase().includes(a.role)
    );
  },

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
    agents: [],
    selectedRoles: [],
    selectedPreset: null,
  }),
}));
