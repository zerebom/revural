"use client";

import { useCallback, useMemo } from "react";
import type { Issue } from "@/lib/types";

type Props = {
  prdText: string;
  issues: Issue[];
  selectedIssueId: string | null;
  onSelect: (issueId: string) => void;
};

export default function PrdTextView({ prdText, issues, selectedIssueId, onSelect }: Props) {
  const highlights = useMemo(() => {
    if (!prdText) return [{ type: "text" as const, key: "t-0", text: "" }];
    const length = prdText.length;
    const spans = issues
      .map((i) => ({
        issue_id: i.issue_id,
        start: i.span?.start_index ?? -1,
        end: i.span?.end_index ?? -1,
      }))
      .filter((s) => s.start >= 0 && s.end > s.start && s.start < length)
      .map((s) => ({ ...s, end: Math.min(s.end, length) }))
      .sort((a, b) => a.start - b.start);

    const parts: Array<
      | { type: "text"; key: string; text: string }
      | { type: "mark"; key: string; text: string; issue_id: string }
    > = [];
    let cursor = 0;
    spans.forEach((s, idx) => {
      if (s.start > cursor) {
        parts.push({ type: "text", key: `t-${idx}-${cursor}`, text: prdText.slice(cursor, s.start) });
      }
      const text = prdText.slice(s.start, s.end);
      parts.push({ type: "mark", key: `m-${idx}-${s.start}-${s.end}`, text, issue_id: s.issue_id });
      cursor = s.end;
    });
    if (cursor < length) {
      parts.push({ type: "text", key: `t-end-${cursor}`, text: prdText.slice(cursor) });
    }
    return parts;
  }, [prdText, issues]);

  const handleClick = useCallback((issueId: string) => onSelect(issueId), [onSelect]);

  return (
    <div className="h-full overflow-auto rounded border bg-white p-4 text-sm leading-6">
      {highlights.length === 1 && highlights[0].type === "text" && !highlights[0].text && (
        <p className="text-gray-500">PRDテキストが未設定です。</p>
      )}
      <div className="whitespace-pre-wrap break-words">
        {highlights.map((p) => {
          if (p.type === "text") return <span key={p.key}>{p.text}</span>;
          const isSelected = p.issue_id === selectedIssueId;
          return (
            <mark
              key={p.key}
              onClick={() => handleClick(p.issue_id)}
              className={
                "cursor-pointer rounded px-0.5 " +
                (isSelected
                  ? "bg-yellow-300 ring-2 ring-yellow-500/60"
                  : "bg-yellow-200 hover:bg-yellow-300")
              }
            >
              {p.text}
            </mark>
          );
        })}
      </div>
    </div>
  );
}
