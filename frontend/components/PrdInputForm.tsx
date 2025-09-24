"use client";

import { useForm } from "react-hook-form";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { toErrorMessage } from "@/lib/errors";
import { useState, useEffect } from "react";
import { useReviewStore } from "@/store/useReviewStore";
import { MemberSelectGrid } from "@/components/team/MemberSelectGrid";
import { TeamPresetSelect } from "@/components/team/TeamPresetSelect";
import { TEAM_PRESETS } from "@/lib/presets";
import type { AgentRole } from "@/lib/types";

type FormValues = { prdText: string };

export default function PrdInputForm() {
  const { register, handleSubmit, formState } = useForm<FormValues>({
    defaultValues: { prdText: "" },
  });
  const [error, setError] = useState<string | null>(null);
  const [agents, setAgents] = useState<AgentRole[]>([]);
  const [loading, setLoading] = useState(false);

  const router = useRouter();
  const setPrdText = useReviewStore((s) => s.setPrdText);
  const setReviewId = useReviewStore((s) => s.setReviewId);
  const selectedRoles = useReviewStore((s) => s.selectedRoles);
  const selectedPreset = useReviewStore((s) => s.selectedPreset);
  const toggleRole = useReviewStore((s) => s.toggleRole);
  const setSelectedRoles = useReviewStore((s) => s.setSelectedRoles);
  const setSelectedPreset = useReviewStore((s) => s.setSelectedPreset);
  const setStoreAgents = useReviewStore((s) => s.setAgents);

  // Fetch agent roles on component mount
  useEffect(() => {
    const fetchAgents = async () => {
      try {
        setLoading(true);
        const agentData = await api.getAgentRoles();
        setAgents(agentData);
        setStoreAgents(agentData); // Store agent info globally
      } catch (e) {
        setError(toErrorMessage(e, "エージェント情報の取得に失敗しました"));
      } finally {
        setLoading(false);
      }
    };

    fetchAgents();
  }, [setStoreAgents]);

  // プリセット選択時の自動適用処理
  const handlePresetChange = (presetKey: string) => {
    setSelectedPreset(presetKey);
    const preset = TEAM_PRESETS.find(p => p.key === presetKey);
    if (preset) {
      setSelectedRoles(preset.roles);
    }
  };

  // プリセット適用時の処理（ボタン用 - 廃止予定）
  const handlePresetApply = (roles: string[]) => {
    setSelectedRoles(roles);
  };

  // 個別選択変更時のプリセット解除処理
  const handleToggleRole = (role: string) => {
    toggleRole(role);
    // 個別変更があった場合はプリセット選択を解除
    setSelectedPreset(null);
  };

  const onSubmit = async (values: FormValues) => {
    setError(null);
    try {
      // Pass selected agent roles to the API
      const res = await api.startReview(
        values.prdText,
        null, // panel_type
        selectedRoles.length > 0 ? selectedRoles : undefined
      );
      setPrdText(values.prdText);
      setReviewId(res.review_id);
      router.push(`/reviews/${res.review_id}`);
    } catch (e: unknown) {
      setError(toErrorMessage(e, "レビューの開始に失敗しました"));
    }
  };

  const selectedCount = selectedRoles.length;
  const buttonText = selectedCount > 0
    ? `選択した${selectedCount}人でレビューを開始`
    : "専門家レビューを開始";

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="w-full max-w-5xl mx-auto space-y-6">
      {/* PRD Text Input */}
      <div>
        <label htmlFor="prdText" className="block text-sm font-medium text-gray-700 mb-2">
          レビュー対象のドキュメント
        </label>
        <textarea
          {...register("prdText", { required: true })}
          rows={10}
          placeholder="仕様書・企画書・要件定義など、レビュー対象のドキュメントを入力してください。"
          className="w-full rounded border border-gray-300 p-3 outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Agent Selection */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-4">
          レビューメンバーを選択（任意）
        </label>

        {/* Team Preset Selection */}
        <div className="mb-32">
          <TeamPresetSelect
            presets={TEAM_PRESETS}
            value={selectedPreset}
            onChange={handlePresetChange}
            onApply={handlePresetApply}
            className="mb-4"
          />
        </div>

        {loading && (
          <div className="text-center py-8 text-gray-600">
            エージェント情報を読み込み中...
          </div>
        )}

        {!loading && agents.length > 0 && (
          <div>
            <div className="text-sm font-medium text-gray-700 mb-3">
              個別選択・調整
            </div>
            <MemberSelectGrid
              agents={agents}
              selectedRoles={selectedRoles}
              onToggleRole={handleToggleRole}
            />
          </div>
        )}

        {selectedCount > 0 && (
          <p className="text-sm text-gray-600 mt-4">
            {selectedCount}人のメンバーが選択されています
          </p>
        )}
      </div>

      {/* Error Display */}
      {error && <p className="text-red-600 text-sm">{error}</p>}

      {/* Submit Button */}
      <div className="flex justify-end">
        <button
          type="submit"
          disabled={formState.isSubmitting || loading}
          className="inline-flex items-center gap-2 rounded bg-blue-600 text-white px-6 py-3 hover:bg-blue-700 disabled:opacity-60 font-medium"
        >
          {formState.isSubmitting ? "開始中..." : buttonText}
        </button>
      </div>
    </form>
  );
}
