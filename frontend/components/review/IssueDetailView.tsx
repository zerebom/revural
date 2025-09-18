"use client";

import { useEffect, useRef, useState } from "react";
import type { Issue } from "@/lib/types";
import SuggestionBox from "@/components/review/legacy/SuggestionBox";
import { useReviewStore } from "@/store/useReviewStore";
import { api } from "@/lib/api";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { PromptInput, PromptInputBody, PromptInputTextarea, PromptInputToolbar, PromptInputSubmit } from "@/components/ai-elements/prompt-input";
import { Streamdown } from "streamdown";
import { StickToBottom, useStickToBottomContext } from "use-stick-to-bottom";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { toErrorMessage } from "@/lib/errors";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

export default function IssueDetailView({ reviewId, issue }: { reviewId: string; issue: Issue }) {
  const setViewMode = useReviewStore((s) => s.setViewMode);
  const updateIssueStatus = useReviewStore((s) => s.updateIssueStatus);
  const [saving, setSaving] = useState<string | null>(null);
  const currentStatus = issue.status ?? "pending";

  const setStatus = async (status: string) => {
    if (saving) return;
    setSaving(status);
    try {
      await api.updateIssueStatus(reviewId, issue.issue_id, status);
      updateIssueStatus(issue.issue_id, status);
    } catch {
      // 軽微なUI: 失敗してもサイレント、将来はToast等に
    } finally {
      setSaving(null);
    }
  };

  // stylingは親（JSX側）で決める方針に変更

  return (
    <div className="flex h-full min-h-0 flex-col">
      <div className="flex items-center gap-3 border-b px-4 py-3 shrink-0">
        <button
          onClick={() => setViewMode("list")}
          className="typ-body-sm inline-flex items-center rounded-lg border border-gray-300 px-2.5 py-1.5 text-gray-700 transition-colors hover:border-gray-400 hover:bg-gray-50 whitespace-nowrap"
        >
          ← 戻る
        </button>
        <h3 className="typ-heading-sm">論点の深掘り</h3>
      </div>

      {/* Context accordion (closed by default) */}
      <div className="px-4 pt-3 shrink-0">
        <Accordion type="single" collapsible>
          <AccordionItem value="context">
            <AccordionTrigger className="px-3">
              <div className="typ-body text-gray-900 truncate">
                {issue.summary || issue.comment || "(no summary)"}
              </div>
            </AccordionTrigger>
            <AccordionContent className="px-3 border-b-0">
              <div className="space-y-2">
                <div>
                  <p className="typ-caption text-gray-600 mb-1">対象テキスト</p>
                  <blockquote className="typ-body-sm whitespace-pre-wrap bg-gray-50/80 border-l-4 border-gray-200 rounded-md p-3.5 text-gray-800">
                    {issue.original_text}
                  </blockquote>
                </div>
                <div>
                  <p className="typ-caption text-gray-600 mb-1">コメント</p>
                  <p className="typ-body whitespace-pre-wrap text-gray-800">{issue.comment}</p>
                </div>
              </div>
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      </div>

      {/* Status controls (Zone 2: 意思決定) */}
      <div className="px-4 py-3 flex items-center gap-2 shrink-0 bg-slate-50">
        <span className="typ-caption text-gray-600">ステータス:</span>
        {(["pending", "later", "done"] as const).map((value) => {
          const isActive = currentStatus === value;
          const isPrimary = value === "done";
          const base = "typ-body-sm px-3 py-1 rounded border whitespace-nowrap transition-colors";
          const cls = isPrimary
            ? isActive
              ? `${base} bg-emerald-600 text-white border-emerald-600`
              : `${base} bg-white text-gray-800 border-gray-300 hover:bg-emerald-50`
            : isActive
              ? `${base} bg-slate-50 text-slate-900 border-slate-400`
              : `${base} bg-white text-gray-800 border-gray-300 hover:bg-gray-50`;
          const label = value === "pending" ? "未対応" : value === "later" ? "あとで" : "対応済み";
          return (
            <button
              key={value}
              onClick={() => void setStatus(value)}
              disabled={saving !== null}
              className={cls}
            >
              {label}
            </button>
          );
        })}
      </div>

      {/* Chat + Actions main area (Zone 3: インタラクション) */}
      <div className="flex-1 min-h-0 px-4 pb-4 flex flex-col">
        <Tabs defaultValue="chat" className="flex-1 min-h-0 flex flex-col">
          <TabsList className="grid w-full grid-cols-2 shrink-0">
            <TabsTrigger value="chat">チャット</TabsTrigger>
            <TabsTrigger value="suggestion">修正案</TabsTrigger>
          </TabsList>
          <TabsContent value="chat" className="flex-1 min-h-0 mt-4 rounded-lg bg-white p-4">
            <ChatPane reviewId={reviewId} issueId={issue.issue_id} />
          </TabsContent>
          <TabsContent value="suggestion" className="flex-1 min-h-0 mt-4 rounded-lg bg-white p-4">
            <SuggestionBox reviewId={reviewId} issueId={issue.issue_id} />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}

function ChatPane({ reviewId, issueId }: { reviewId: string; issueId: string }) {
  const [history, setHistory] = useState<{ role: "user" | "ai"; text: string }[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const endRef = useRef<HTMLDivElement | null>(null);
  const [input, setInput] = useState("");

  const ask = async (q: string) => {
    q = (q || "").trim();
    if (!q) return;
    setInput("");
    setError(null);
    setLoading(true);
    setHistory((h) => [...h, { role: "user", text: q }]);
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

  return (
    <div className="flex h-full min-h-0 flex-col">
      <StickToBottom className="flex-1 min-h-0 relative overflow-y-auto">
        <StickToBottom.Content className="space-y-3 typ-body">
          {history.length === 0 && <p className="typ-body text-gray-500">この指摘についてAIに質問できます。</p>}
          {history.map((m, idx) => (
            <MessageBubble key={idx} role={m.role}>
              <Streamdown className="prose prose-sm max-w-none [&_p]:m-0 [&_ul]:my-1 [&_ol]:my-1 [&_li]:my-0.5 [&_code]:text-[85%]">
                {m.text}
              </Streamdown>
            </MessageBubble>
          ))}
          <div ref={endRef} />
        </StickToBottom.Content>
        <ScrollToBottomButton />
      </StickToBottom>
      {error && <p className="typ-caption text-red-600 mt-2">{error}</p>}
      <PromptInput
        className="mt-3 shrink-0"
        onSubmit={(_, e) => {
          e.preventDefault();
          if (!loading) void ask(input);
        }}
      >
        <PromptInputBody>
          <PromptInputTextarea
            placeholder="質問を入力..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            className="resize-none max-h-32 overflow-y-auto"
          />
          <PromptInputToolbar>
            <div />
            <PromptInputSubmit status={loading ? "submitted" : undefined} />
          </PromptInputToolbar>
        </PromptInputBody>
      </PromptInput>
    </div>
  );
}

function MessageBubble({ role, children }: { role: "user" | "ai"; children: React.ReactNode }) {
  const isUser = role === "user";
  return (
    <div className={`flex items-start gap-2 ${isUser ? "flex-row-reverse" : ""}`}>
      <Avatar className="h-7 w-7 select-none">
        <AvatarFallback className={isUser ? "bg-blue-600 text-white" : "bg-gray-200 text-gray-700"}>
          {isUser ? "U" : "AI"}
        </AvatarFallback>
      </Avatar>
      <div
        className={
          isUser
            ? "max-w-[85%] rounded border border-blue-200 bg-blue-50 text-blue-900 px-3 py-2"
            : "max-w-[85%] rounded border border-gray-200 bg-gray-50 text-gray-900 px-3 py-2"
        }
      >
        {children}
      </div>
    </div>
  );
}

function ScrollToBottomButton() {
  const { isAtBottom, scrollToBottom } = useStickToBottomContext();
  if (isAtBottom) return null;
  return (
    <button
      onClick={() => void scrollToBottom()}
      className="typ-caption absolute left-1/2 -translate-x-1/2 bottom-1 rounded border border-slate-200 bg-white/90 px-2 py-1 text-slate-600 transition-colors hover:border-slate-300"
    >
      最新メッセージへ
    </button>
  );
}
