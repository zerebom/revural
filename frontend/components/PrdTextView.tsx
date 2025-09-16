"use client";

import { useCallback, useEffect, useMemo, useRef } from "react";
import ReactMarkdown from "react-markdown";
import rehypeRaw from "rehype-raw";
import rehypeSanitize, { defaultSchema } from "rehype-sanitize";
import type { Issue } from "@/lib/types";
import { cn, getAgentColorClasses } from "@/lib/utils";
import { useReviewStore } from "@/store/useReviewStore";

type Props = {
  prdText: string;
  issues: Issue[];
  expandedIssueId: string | null;
  onSelect: (issueId: string) => void;
};

export default function PrdTextView({ prdText, issues, expandedIssueId, onSelect }: Props) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const setExpandedIssueId = useReviewStore((s) => s.setExpandedIssueId);

  // Build annotated markdown with <mark data-issue-id="..."> wrapped around target spans.
  const annotated = useMemo(() => {
    if (!prdText) return "";
    const length = prdText.length;
    const id2Agent = new Map<string, string>(issues.map((i) => [i.issue_id, i.agent_name]));
    // Prepare spans; fallback to original_text search if span missing
    const rawSpans = issues
      .map((i) => {
        let start = i.span?.start_index ?? -1;
        let end = i.span?.end_index ?? -1;
        if (!(start >= 0 && end > start)) {
          // fallback: find first occurrence of original_text
          const t = (i.original_text || "").trim();
          if (t) {
            const pos = prdText.indexOf(t);
            if (pos >= 0) {
              start = pos;
              end = pos + t.length;
            }
          }
        }
        return { issue_id: i.issue_id, start, end };
      })
      .filter((s) => s.start >= 0 && s.end > s.start && s.start < length)
      .map((s) => ({ ...s, end: Math.min(s.end, length) }))
      .sort((a, b) => a.start - b.start);

    let cursor = 0;
    let out = "";
    rawSpans.forEach((s) => {
      // Clip overlapping spans to avoid duplicate output
      if (s.end <= cursor) {
        return; // this span is fully behind the cursor
      }
      const start = Math.max(s.start, cursor);
      if (start > cursor) {
        out += prdText.slice(cursor, start);
      }
      const inner = prdText.slice(start, s.end);
      const agent = id2Agent.get(s.issue_id) ?? "";
      // Inject raw HTML mark (rendered via rehype-raw). Include agent for color mapping.
      out += `<mark data-issue-id="${escapeAttr(s.issue_id)}" data-agent="${escapeAttr(agent)}">${escapeHtml(inner)}</mark>`;
      cursor = s.end;
    });
    if (cursor < length) out += prdText.slice(cursor);
    return out;
  }, [prdText, issues]);

  // Auto-scroll to current expanded mark
  useEffect(() => {
    if (!containerRef.current || !expandedIssueId) return;
    const el = containerRef.current.querySelector(`mark[data-issue-id="${CSS.escape(expandedIssueId)}"]`);
    if (el && el instanceof HTMLElement) {
      el.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  }, [expandedIssueId]);

  const handleClick = useCallback(
    (issueId: string) => {
      onSelect(issueId);
      // ensure accordion opens even if parent callback changes
      setExpandedIssueId(issueId);
    },
    [onSelect, setExpandedIssueId]
  );

  return (
    <div ref={containerRef} className="h-full overflow-auto rounded border bg-white p-4 text-sm leading-6">
      {!prdText && <p className="text-gray-500">PRDテキストが未設定です。</p>}
      <div className="prose prose-sm max-w-none">
        <ReactMarkdown
          // Allow raw HTML so injected <mark> renders
          rehypePlugins={[
            rehypeRaw,
            [
              rehypeSanitize,
              {
                ...defaultSchema,
                tagNames: [...(defaultSchema.tagNames || []), "mark"],
                attributes: {
                  ...(defaultSchema.attributes || {}),
                  // Allow our custom data attributes on <mark>.
                  // rehype-sanitize matches property names (camel-cased) for data-* attributes.
                  mark: ["data-issue-id", "data-agent", "dataIssueId", "dataAgent"],
                  "*": [
                    ...(((defaultSchema.attributes || {})["*"]) || []),
                    "data-issue-id",
                    "data-agent",
                    "dataIssueId",
                    "dataAgent",
                  ],
                },
              },
            ],
          ]}
          // Attach click handler via component override
          components={{
            mark: ({ node, children, ...props }) => {
              // Try both hyphenated and camel-cased keys depending on how sanitizer mapped them
              const anyProps = props as Record<string, unknown>;
              const nodeProps = ((node as unknown as { properties?: Record<string, unknown> })?.properties) || {};
              const idFromProps = typeof anyProps["data-issue-id"] === "string" ? (anyProps["data-issue-id"] as string) : undefined;
              const idFromNode =
                typeof nodeProps["data-issue-id"] === "string"
                  ? (nodeProps["data-issue-id"] as string)
                  : typeof nodeProps["dataIssueId"] === "string"
                    ? (nodeProps["dataIssueId"] as string)
                    : undefined;
              const id = idFromProps || idFromNode;

              const agentFromProps = typeof anyProps["data-agent"] === "string" ? (anyProps["data-agent"] as string) : undefined;
              const agentFromNode =
                typeof nodeProps["data-agent"] === "string"
                  ? (nodeProps["data-agent"] as string)
                  : typeof nodeProps["dataAgent"] === "string"
                    ? (nodeProps["dataAgent"] as string)
                    : undefined;

              // Prefer attribute value; fallback to store by issue_id
              const agentName = agentFromProps || agentFromNode || (id ? issues.find((i) => i.issue_id === id)?.agent_name : undefined);
              const isSelected = id && id === expandedIssueId;
              const colors = getAgentColorClasses(agentName || "");
              return (
                <mark
                  data-issue-id={id}
                  data-agent={agentFromProps || agentFromNode}
                  onClick={() => id && handleClick(id)}
                  className={cn(
                    "cursor-pointer rounded px-0.5",
                    isSelected ? `${colors.bgActive} ring-2 ${colors.ring}` : colors.bg
                  )}
                >
                  {children}
                </mark>
              );
            },
          }}
        >
          {annotated}
        </ReactMarkdown>
      </div>
    </div>
  );
}

function escapeHtml(s: string): string {
  return s
    .replaceAll(/&/g, "&amp;")
    .replaceAll(/</g, "&lt;")
    .replaceAll(/>/g, "&gt;")
    .replaceAll(/\"/g, "&quot;")
    .replaceAll(/'/g, "&#39;");
}

function escapeAttr(s: string): string {
  return s
    .replaceAll(/&/g, "&amp;")
    .replaceAll(/\"/g, "&quot;")
    .replaceAll(/</g, "&lt;")
    .replaceAll(/>/g, "&gt;")
    .replaceAll(/'/g, "&#39;");
}
