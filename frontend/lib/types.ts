export interface IssueSpan {
  start_index: number;
  end_index: number;
}

export interface Issue {
  issue_id: string;
  priority: number;
  agent_name: string;
  comment: string;
  original_text: string;
  // ハイライト位置情報（バックエンド対応前は未設定の可能性あり）
  span?: IssueSpan;
}

export type ReviewStatus = "processing" | "completed" | "failed" | "not_found";

export interface ReviewStatusResponse {
  status: ReviewStatus;
  issues: Issue[] | null;
}

export interface ReviewStartResponse {
  review_id: string;
}
