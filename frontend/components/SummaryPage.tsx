"use client";

import { useCallback, useMemo, useState } from "react";
import useSWR from "swr";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Bar, BarChart, CartesianGrid, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis, Cell } from "recharts";
import Header from "@/components/layout/Header";
import LoadingSpinner from "@/components/LoadingSpinner";
import { api } from "@/lib/api";
import { AgentCount, ReviewSummaryResponse, StatusCount } from "@/lib/types";
import { cn } from "@/lib/utils";
import { ChartContainer, ChartTooltipContent, ChartEmptyState, ChartConfig } from "@/components/ui/chart";

const STATUS_COLORS: Record<string, string> = {
  done: "hsl(152, 76%, 40%)", // emerald-500
  pending: "hsl(215, 16%, 47%)", // slate-500
  later: "hsl(43, 96%, 56%)", // amber-400
};

const AGENT_COLOR_PALETTE = [
  "hsl(221, 83%, 53%)", // blue-500
  "hsl(262, 83%, 58%)", // violet-500
  "hsl(158, 64%, 52%)", // emerald-400
  "hsl(12, 86%, 53%)", // orange-500
  "hsl(200, 89%, 53%)", // sky-500
  "hsl(340, 82%, 52%)", // fuchsia-500
];

function statusLabel(count: StatusCount): string {
  return count.label || count.key;
}

function formatStatusKey(key: string): string {
  return key in STATUS_COLORS ? key : "pending";
}

function buildMarkdown(reviewId: string, data: ReviewSummaryResponse): string {
  const lines: string[] = [];
  lines.push(`# レビューサマリー (${reviewId})`);
  lines.push("");
  lines.push(`ステータス: ${data.status}`);
  lines.push("");
  lines.push("## 概要統計");
  lines.push("");
  lines.push(`- 指摘総数: ${data.statistics.total_issues}`);
  if (data.statistics.status_counts.length > 0) {
    lines.push("- ステータス内訳:");
    for (const count of data.statistics.status_counts) {
      lines.push(`  - ${count.label}: ${count.count}`);
    }
  }
  if (data.statistics.agent_counts.length > 0) {
    lines.push("- 担当エージェントごとの件数:");
    for (const agent of data.statistics.agent_counts) {
      lines.push(`  - ${agent.agent_name}: ${agent.count}`);
    }
  }
  lines.push("");
  lines.push("## 指摘一覧");
  lines.push("");
  data.issues.forEach((issue, index) => {
    const heading = issue.summary || issue.comment.split("\n")[0] || `指摘 ${index + 1}`;
    lines.push(`### ${index + 1}. ${heading}`);
    lines.push("");
    lines.push(`- エージェント: ${issue.agent_name}`);
    lines.push(`- 優先度: ${issue.priority}`);
    lines.push(`- ステータス: ${issue.status ?? "pending"}`);
    lines.push("");
    lines.push(issue.comment);
    lines.push("");
    if (issue.original_text) {
      lines.push("> 元テキスト:");
      lines.push(
        issue.original_text
          .split("\n")
          .map((line) => `> ${line}`)
          .join("\n")
      );
      lines.push("");
    }
  });
  return lines.join("\n");
}

export default function SummaryPage({ reviewId }: { reviewId: string }) {
  const router = useRouter();
  const { data, error, isLoading } = useSWR<ReviewSummaryResponse>(
    reviewId ? ["summary", reviewId] : null,
    () => api.getReviewSummary(reviewId)
  );
  const [exporting, setExporting] = useState(false);

  const totalIssues = data?.statistics.total_issues ?? 0;
  const onBack = useCallback(() => {
    router.push(`/reviews/${reviewId}`);
  }, [reviewId, router]);

  const handleExport = useCallback(() => {
    if (!data) return;
    try {
      setExporting(true);
      const markdown = buildMarkdown(reviewId, data);
      const blob = new Blob([markdown], { type: "text/markdown" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `review-${reviewId}-summary.md`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } finally {
      setExporting(false);
    }
  }, [data, reviewId]);

  const statusChartData = useMemo(() => {
    if (!data) return [] as { key: string; name: string; count: number }[];
    return data.statistics.status_counts.map((count) => {
      const key = formatStatusKey(count.key);
      return {
        key,
        name: statusLabel(count),
        count: count.count,
      };
    });
  }, [data]);

  const statusChartConfig: ChartConfig = useMemo(() => {
    const config: ChartConfig = {};
    statusChartData.forEach((item) => {
      config[item.key] = {
        label: item.name,
        color: STATUS_COLORS[item.key] ?? "hsl(215, 16%, 47%)",
      };
    });
    return config;
  }, [statusChartData]);

  const agentChartData = useMemo(() => {
    if (!data) return [] as { key: string; name: string; value: number; color: string }[];
    return data.statistics.agent_counts.map((count, index) => {
      const color = AGENT_COLOR_PALETTE[index % AGENT_COLOR_PALETTE.length];
      return {
        key: `agent-${index}`,
        name: count.agent_name,
        value: count.count,
        color,
      };
    });
  }, [data]);

  const agentChartConfig: ChartConfig = useMemo(() => {
    const config: ChartConfig = {};
    agentChartData.forEach((item) => {
      config[item.key] = { label: item.name, color: item.color };
    });
    return config;
  }, [agentChartData]);

  let content: JSX.Element;
  if (isLoading) {
    content = (
      <div className="flex items-center justify-center py-24">
        <LoadingSpinner />
      </div>
    );
  } else if (error) {
    content = <p className="typ-body text-red-600">サマリーの取得に失敗しました: {String(error)}</p>;
  } else if (!data) {
    content = <p className="typ-body text-slate-600">サマリーがまだ生成されていません。</p>;
  } else {
    const hasIssues = data.issues.length > 0;
    content = (
      <div className="space-y-8">
        <section className="space-y-4">
          <div className="space-y-1">
            <h1 className="typ-heading-md text-slate-900">レビューサマリー</h1>
            <p className="typ-body text-slate-600">レビューID: {reviewId}</p>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <ChartContainer config={statusChartConfig}>
              <div className="space-y-4">
                <div>
                  <h2 className="typ-heading-xs text-slate-900">ステータスの内訳</h2>
                  <p className="typ-caption text-slate-500">対応状況をカテゴリ別に可視化します。</p>
                </div>
                {statusChartData.length === 0 ? (
                  <ChartEmptyState message="ステータス情報はまだありません。" />
                ) : (
                  <ResponsiveContainer width="100%" height={260}>
                    <BarChart data={statusChartData} barSize={32}>
                      <CartesianGrid vertical={false} strokeDasharray="3 3" className="stroke-slate-200" />
                      <XAxis dataKey="name" tickLine={false} axisLine={false} className="typ-caption text-slate-500" />
                      <YAxis hide />
                      <Tooltip cursor={{ fill: "rgba(100,116,139,0.08)" }} content={<ChartTooltipContent />} />
                      <Bar dataKey="count" radius={[8, 8, 4, 4]}>
                        {statusChartData.map((item) => (
                          <Cell key={item.key} fill={`var(--chart-${item.key})`} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                )}
              </div>
            </ChartContainer>

            <ChartContainer config={agentChartConfig}>
              <div className="space-y-4">
                <div>
                  <h2 className="typ-heading-xs text-slate-900">エージェント別の件数</h2>
                  <p className="typ-caption text-slate-500">どの専門家が多く指摘したのかを俯瞰できます。</p>
                </div>
                {agentChartData.length === 0 ? (
                  <ChartEmptyState message="エージェント情報はまだありません。" />
                ) : (
                  <ResponsiveContainer width="100%" height={260}>
                    <PieChart>
                      <Pie
                        data={agentChartData}
                        dataKey="value"
                        nameKey="name"
                        innerRadius={60}
                        outerRadius={90}
                        paddingAngle={6}
                        stroke="#fff"
                        strokeWidth={2}
                      >
                        {agentChartData.map((entry) => (
                          <Cell key={entry.key} fill={`var(--chart-${entry.key})`} />
                        ))}
                      </Pie>
                      <Tooltip content={<ChartTooltipContent />} />
                    </PieChart>
                  </ResponsiveContainer>
                )}
              </div>
            </ChartContainer>
          </div>
        </section>

        <section className="space-y-4">
          <div className="space-y-1">
            <h2 className="typ-heading-sm text-slate-900">指摘事項一覧</h2>
            <p className="typ-caption text-slate-500">
              初回コメントと元テキストを確認できます。必要に応じてレビュー画面で深掘りを行ってください。
            </p>
          </div>

          {!hasIssues ? (
            <div className="rounded-xl border border-slate-200/60 bg-white p-6 text-center typ-body text-slate-600">
              指摘事項はまだありません。
            </div>
          ) : (
            <motion.div
              className="space-y-4"
              initial="hidden"
              animate="visible"
              variants={{
                hidden: {},
                visible: {
                  transition: {
                    staggerChildren: 0.08,
                  },
                },
              }}
            >
              {data.issues.map((issue) => (
                <motion.article
                  key={issue.issue_id}
                  variants={{ hidden: { opacity: 0, y: 8 }, visible: { opacity: 1, y: 0 } }}
                  className="space-y-4 rounded-xl border border-slate-200/60 bg-white p-6"
                >
                  <div className="flex flex-col gap-2 md:flex-row md:items-start md:justify-between">
                    <div className="space-y-1">
                      <p className="typ-caption uppercase text-slate-500">{issue.agent_name}</p>
                      <h3 className="typ-heading-xs text-slate-900">{issue.summary || "指摘"}</h3>
                    </div>
                    <div className="flex items-center gap-2 text-slate-600">
                      <span className="typ-caption">優先度: {issue.priority}</span>
                      <span className="typ-caption">ステータス: {issue.status ?? "未対応"}</span>
                    </div>
                  </div>

                  <p className="typ-body whitespace-pre-wrap text-slate-800">{issue.comment}</p>

                  {issue.original_text && (
                    <div className="space-y-2">
                      <p className="typ-caption text-slate-500">元テキスト</p>
                      <blockquote className="typ-body-sm whitespace-pre-wrap border-l-4 border-slate-200 bg-slate-50 p-3 pl-4 text-slate-800">
                        {issue.original_text}
                      </blockquote>
                    </div>
                  )}

                  <div>
                    <button
                      type="button"
                      onClick={() => router.push(`/reviews/${reviewId}`)}
                      className="typ-body inline-flex items-center gap-2 rounded-md bg-slate-900 px-3.5 py-2 text-white transition-colors hover:bg-slate-800"
                    >
                      レビュー画面で深掘りする
                    </button>
                  </div>
                </motion.article>
              ))}
            </motion.div>
          )}
        </section>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <div className="flex min-h-screen flex-col">
        <Header
          title="レビューサマリー"
          onBack={onBack}
          onExport={data ? handleExport : undefined}
          className="sticky top-0 z-30 border-b border-slate-200/80 bg-white/90 px-6 py-4 backdrop-blur"
          showSummaryButton={false}
          showExportButton={Boolean(data)}
        />
        <main className="mx-auto w-full max-w-5xl flex-1 px-6 pb-12 pt-6">
          {exporting && (
            <p className="typ-caption mb-3 text-slate-500">Markdownを生成中...</p>
          )}
          {content}
        </main>
      </div>
    </div>
  );
}
