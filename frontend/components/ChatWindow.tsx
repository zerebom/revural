"use client";

import { api } from "@/lib/api";
import { useState } from "react";

export default function ChatWindow({ reviewId, issueId }: { reviewId: string; issueId: string }) {
  const [question, setQuestion] = useState("");
  const [history, setHistory] = useState<{ role: "user" | "ai"; text: string }[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const ask = async () => {
    const q = question.trim();
    if (!q) return;
    setError(null);
    setLoading(true);
    setHistory((h) => [...h, { role: "user", text: q }]);
    setQuestion("");
    try {
      const res = await api.dialog(reviewId, issueId, q);
      setHistory((h) => [...h, { role: "ai", text: res.response_text }]);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : String(e);
      setError(msg || "対話の送信に失敗しました");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="border rounded p-3 space-y-3 dark:border-gray-700">
      <div className="max-h-56 overflow-y-auto space-y-2 text-sm">
        {history.length === 0 && <p className="text-gray-500">この指摘についてAIに質問できます。</p>}
        {history.map((m, idx) => (
          <div key={idx} className={m.role === "user" ? "text-right" : "text-left"}>
            <span className={
              m.role === "user"
                ? "inline-block bg-blue-50 dark:bg-blue-900/40 text-blue-900 dark:text-blue-100 px-2 py-1 rounded"
                : "inline-block bg-gray-100 dark:bg-gray-900 text-gray-900 dark:text-gray-100 px-2 py-1 rounded"
            }>
              {m.text}
            </span>
          </div>
        ))}
      </div>
      {error && <p className="text-red-600 text-xs">{error}</p>}
      <div className="flex gap-2">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="質問を入力..."
          className="flex-1 border rounded px-2 py-1 outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-800 dark:border-gray-700"
        />
        <button onClick={ask} disabled={loading} className="rounded bg-blue-600 text-white px-3 py-1 hover:bg-blue-700 disabled:opacity-60">
          送信
        </button>
      </div>
    </div>
  );
}
