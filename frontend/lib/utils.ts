import { type ClassValue } from "clsx";
import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export type AgentColor = {
  bg: string; // normal background
  bgActive: string; // active/selected background
  ring: string; // ring color class (e.g., ring-blue-400)
  border: string; // border color class (e.g., border-blue-400)
};

// UI計画書の定義に従った色マッピング（9エージェント対応）
export function getAgentColorClasses(agentName: string | undefined | null): AgentColor {
  const name = (agentName || "").toLowerCase();

  // UXデザイナー・UXライター (青系)
  if (name.includes("ux") || name.includes("デザイナー") || name.includes("uxレビュー") || name.includes("designer") || name.includes("writer") || name.includes("ライター")) {
    return { bg: "bg-blue-200", bgActive: "bg-blue-300", ring: "ring-blue-500", border: "border-blue-500" };
  }

  // セキュリティスペシャリスト (赤系)
  if (name.includes("セキュリティ") || name.includes("security")) {
    return { bg: "bg-red-200", bgActive: "bg-red-300", ring: "ring-red-500", border: "border-red-500" };
  }

  // QAテスター (緑系)
  if (name.includes("qa" ) || name.includes("テスター") || name.includes("qaレビュー") || name.includes("tester")) {
    return { bg: "bg-green-200", bgActive: "bg-green-300", ring: "ring-green-500", border: "border-green-500" };
  }

  // エンジニア (黄系)
  if (name.includes("engineer") || name.includes("エンジニア")) {
    return { bg: "bg-amber-200", bgActive: "bg-amber-300", ring: "ring-amber-500", border: "border-amber-500" };
  }

  // PM・マーケティングストラテジスト (紫系)
  if (name.includes("pm") || name.includes("product manager") || name.includes("プロダクト") || name.includes("marketing") || name.includes("マーケティング")) {
    return { bg: "bg-violet-200", bgActive: "bg-violet-300", ring: "ring-violet-500", border: "border-violet-500" };
  }

  // データサイエンティスト (青緑系)
  if (name.includes("data") || name.includes("scientist") || name.includes("データ") || name.includes("サイエンティスト")) {
    return { bg: "bg-teal-200", bgActive: "bg-teal-300", ring: "ring-teal-500", border: "border-teal-500" };
  }

  // リーガルアドバイザー (グレー系)
  if (name.includes("legal") || name.includes("advisor") || name.includes("法務") || name.includes("リーガル")) {
    return { bg: "bg-slate-200", bgActive: "bg-slate-300", ring: "ring-slate-500", border: "border-slate-500" };
  }

  // フォールバック（その他）
  return { bg: "bg-gray-200", bgActive: "bg-gray-300", ring: "ring-gray-500", border: "border-gray-500" };
}

// 互換用（既存呼び出しがあっても壊さない）
export function agentColorClasses(agentName: string | undefined | null) {
  const c = getAgentColorClasses(agentName);
  return {
    mark: `${c.bg.replace("bg-", "bg-")} hover:${c.bgActive}`,
    markSelected: `${c.bgActive} ring-2 ${c.ring}`,
    dotBg: c.bgActive.replace("bg-", "bg-"),
    border: c.border,
  } as unknown as { mark: string; markSelected: string; dotBg: string; border: string };
}
