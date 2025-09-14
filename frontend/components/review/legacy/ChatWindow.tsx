"use client";

import { api } from "@/lib/api";
import { toErrorMessage } from "@/lib/errors";
import { useEffect, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import ReactMarkdown from "react-markdown";

export default function ChatWindow({ reviewId, issueId }: { reviewId: string; issueId: string }) {
  const [question, setQuestion] = useState("");
  const [history, setHistory] = useState<{ role: "user" | "ai"; text: string }[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const endRef = useRef<HTMLDivElement | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);

  const ask = async () => {
    const q = question.trim();
    if (!q) return;
    setError(null);
    setLoading(true);
    setHistory((h) => [...h, { role: "user", text: q }]);
    setQuestion("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
    try {
      const res = await api.dialog(reviewId, issueId, q);
      setHistory((h) => [...h, { role: "ai", text: res.response_text }]);
    } catch (e: unknown) {
      setError(toErrorMessage(e, "対話の送信に失敗しました"));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [history.length]);

  const onInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setQuestion(e.target.value);
    // auto-grow
    e.currentTarget.style.height = "auto";
    e.currentTarget.style.height = `${e.currentTarget.scrollHeight}px`;
  };

  const onKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      if (!loading) void ask();
    }
  };

  return (
    <div className="border rounded p-3 space-y-3">
      <div className="max-h-72 overflow-y-auto space-y-2 text-sm">
        {history.length === 0 && <p className="text-gray-500">この指摘についてAIに質問できます。</p>}
        {history.map((m, idx) => (
          <div key={idx} className={m.role === "user" ? "text-right" : "text-left"}>
            <div
              className={
                m.role === "user"
                  ? "inline-block bg-blue-50 text-blue-900 px-3 py-2 rounded text-left"
                  : "inline-block bg-gray-100 text-gray-900 px-3 py-2 rounded text-left"
              }
            >
              <div className="prose prose-sm max-w-none [&_p]:m-0 [&_ul]:my-1 [&_ol]:my-1 [&_li]:my-0.5 [&_code]:text-[85%]">
                <ReactMarkdown
                  components={{
                    a: ({ node, ...props }) => (
                      <a {...props} target="_blank" rel="noreferrer noopener" />
                    ),
                  }}
                >
                  {m.text}
                </ReactMarkdown>
              </div>
            </div>
          </div>
        ))}
        <div ref={endRef} />
      </div>
      {error && <p className="text-red-600 text-xs">{error}</p>}
      <div className="flex items-end gap-2">
        <div className="flex-1">
          <Textarea
            ref={textareaRef}
            value={question}
            onChange={onInput}
            onKeyDown={onKeyDown}
            placeholder="質問を入力..."
            rows={2}
          />
          <p className="mt-1 text-[11px] text-gray-500">⌘/Ctrl + Enter で送信、Enter で改行</p>
        </div>
        <Button onClick={ask} disabled={loading} className="bg-blue-600 hover:bg-blue-700 text-white">
          送信
        </Button>
      </div>
    </div>
  );
}
