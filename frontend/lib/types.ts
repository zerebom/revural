export interface IssueSpan {
  start_index: number;
  end_index: number;
}

export interface Issue {
  issue_id: string;
  priority: number;
  agent_name: string;
  summary: string;
  comment: string;
  original_text: string;
  status?: string;
  // ハイライト位置情報（バックエンド対応前は未設定の可能性あり）
  span?: IssueSpan;
}

export type ReviewStatus = "processing" | "completed" | "failed" | "not_found";

export interface ReviewStatusResponse {
  status: ReviewStatus;
  issues: Issue[] | null;
  prd_text?: string | null;
  progress?: number | null;
  phase?: string | null;
  phase_message?: string | null;
  eta_seconds?: number | null;
  expected_agents?: string[] | null;
  completed_agents?: string[] | null;
}

export interface ReviewStartResponse {
  review_id: string;
}

export interface StatusCount {
  key: string;
  label: string;
  count: number;
}

export interface AgentCount {
  agent_name: string;
  count: number;
}

export interface SummaryStatistics {
  total_issues: number;
  status_counts: StatusCount[];
  agent_counts: AgentCount[];
}

export interface ReviewSummaryResponse {
  status: ReviewStatus;
  statistics: SummaryStatistics;
  issues: Issue[];
}
