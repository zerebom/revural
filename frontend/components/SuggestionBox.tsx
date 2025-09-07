"use client";

import { useState } from "react";
import { api } from "@/lib/api";

export default function SuggestionBox({ reviewId, issueId }: { reviewId: string; issueId: string }) {
  const [suggestion, setSuggestion] = useState<string | null>(null);
  const [target, setTarget] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchSuggestion = async () => {
    setError(null);
    setLoading(true);
    try {
      const res = await api.suggest(reviewId, issueId);
      setSuggestion(res.suggested_text);
      setTarget(res.target_text);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : String(e);
      setError(msg || "修正案の取得に失敗しました");
    } finally {
      setLoading(false);
    }
  };

  const apply = async () => {
    setError(null);
    setMsg(null);
    try {
      const res = await api.applySuggestion(reviewId, issueId);
      if (res.status === "success") setMsg("PRDを更新しました");
      else setError("適用に失敗しました");
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : String(e);
      setError(msg || "適用に失敗しました");
    }
  };

  return (
    <div className="border rounded p-3 space-y-3 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h4 className="font-medium">修正案</h4>
        <button onClick={fetchSuggestion} disabled={loading} className="rounded bg-gray-800 text-white px-3 py-1 hover:bg-black disabled:opacity-60">
          {loading ? "読込中..." : "修正案を提案して"}
        </button>
      </div>
      {error && <p className="text-red-600 text-sm">{error}</p>}
      {msg && <p className="text-green-700 text-sm">{msg}</p>}
      {target && (
        <div>
          <p className="text-xs text-gray-600 mb-1">対象テキスト</p>
          <pre className="whitespace-pre-wrap text-sm bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded p-2 text-gray-800 dark:text-gray-100">{target}</pre>
        </div>
      )}
      {suggestion && (
        <div className="space-y-2">
          <pre className="whitespace-pre-wrap text-sm bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-800 rounded p-2 text-blue-950 dark:text-blue-100">
            {suggestion}
          </pre>
          <button onClick={apply} className="rounded bg-blue-600 text-white px-3 py-1 hover:bg-blue-700">適用する</button>
        </div>
      )}
    </div>
  );
}
