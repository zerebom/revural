import type { TeamPreset } from "@/components/team/TeamPresetSelect";

export const TEAM_PRESETS: TeamPreset[] = [
  {
    key: "prd_review",
    name: "PRDレビュー",
    roles: ["engineer", "ux_designer", "pm"],
  },
  {
    key: "technical_review",
    name: "技術レビュー",
    roles: ["engineer", "qa_tester"],
  },
  {
    key: "design_review",
    name: "デザインレビュー",
    roles: ["ux_designer", "pm"],
  },
  {
    key: "full_team",
    name: "フルチーム",
    roles: ["engineer", "ux_designer", "qa_tester", "pm"],
  },
];
