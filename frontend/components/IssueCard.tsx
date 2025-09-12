"use client";

import type { Issue } from "@/lib/types";
import ChatWindow from "./ChatWindow";
import SuggestionBox from "./SuggestionBox";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useMemo } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

export default function IssueCard({
  reviewId,
  issue,
  position,
  total,
}: {
  reviewId: string;
  issue: Issue;
  position: number; // 1-based index
  total: number;
}) {
  const priorityVariant = useMemo(() => {
    if (issue.priority >= 3) return "destructive" as const; // high
    if (issue.priority === 2) return "warning" as const; // mid
    return "secondary" as const; // low/default
  }, [issue.priority]);

  const avatarInitial = issue.agent_name?.[0]?.toUpperCase() ?? "A";

  return (
    <Card className="space-y-0">
      <CardHeader className="flex items-start justify-between gap-4 bg-white">
        <div className="flex items-center gap-3">
          <div className="h-8 w-8 rounded-full bg-slate-200 dark:bg-slate-700 flex items-center justify-center text-sm font-semibold text-slate-700 dark:text-slate-100">
            {avatarInitial}
          </div>
          <div>
            <CardTitle className="leading-tight text-gray-900">指摘事項 {position} / {total}</CardTitle>
            <p className="text-xs text-gray-600">{issue.agent_name} の指摘</p>
          </div>
        </div>
        <Badge variant={priorityVariant}>優先度 {issue.priority}</Badge>
      </CardHeader>

      <CardContent className="space-y-3">
        <p className="text-sm text-gray-800 whitespace-pre-wrap">{issue.comment}</p>

        <div>
          <p className="text-xs text-gray-600 mb-1">元テキスト</p>
          <blockquote className="whitespace-pre-wrap text-sm bg-gray-50 border-l-4 border-gray-300 rounded p-3 text-gray-800">
            {issue.original_text}
          </blockquote>
        </div>
      </CardContent>

      <CardFooter>
        <Tabs defaultValue="chat" className="w-full">
          <TabsList>
            <TabsTrigger value="chat">AIと対話する</TabsTrigger>
            <TabsTrigger value="suggest">修正案</TabsTrigger>
          </TabsList>
          <TabsContent value="chat">
            <ChatWindow reviewId={reviewId} issueId={issue.issue_id} />
          </TabsContent>
          <TabsContent value="suggest">
            <SuggestionBox reviewId={reviewId} issueId={issue.issue_id} />
          </TabsContent>
        </Tabs>
      </CardFooter>
    </Card>
  );
}
