import type { TeamPreset } from "@/components/team/TeamPresetSelect";

export const TEAM_PRESETS: TeamPreset[] = [
  {
    key: "prd_document",
    name: "📋 PRD（プロダクト要求仕様書）",
    roles: ["pm", "engineer", "ux_designer", "data_scientist"],
  },
  {
    key: "technical_spec",
    name: "🔧 技術仕様書・設計書",
    roles: ["engineer", "security_specialist", "qa_tester", "data_scientist"],
  },
  {
    key: "ui_ux_spec",
    name: "🎨 UI/UX仕様書・デザインガイド",
    roles: ["ux_designer", "ux_writer", "pm", "marketing_strategist"],
  },
  {
    key: "business_plan",
    name: "💼 事業計画書・ビジネス要件",
    roles: ["pm", "marketing_strategist", "data_scientist", "legal_advisor"],
  },
  {
    key: "compliance_doc",
    name: "⚖️ 法務・コンプライアンス文書",
    roles: ["legal_advisor", "security_specialist", "pm", "data_scientist"],
  },
];
