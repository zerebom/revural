"use client";

import { useForm } from "react-hook-form";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { toErrorMessage } from "@/lib/errors";
import { useState } from "react";
import { useReviewStore } from "@/store/useReviewStore";

type FormValues = { prdText: string };

export default function PrdInputForm() {
  const { register, handleSubmit, formState } = useForm<FormValues>({
    defaultValues: { prdText: "" },
  });
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  const setPrdText = useReviewStore((s) => s.setPrdText);
  const setReviewId = useReviewStore((s) => s.setReviewId);

  const onSubmit = async (values: FormValues) => {
    setError(null);
    try {
      const res = await api.startReview(values.prdText);
      setPrdText(values.prdText);
      setReviewId(res.review_id);
      router.push(`/reviews/${res.review_id}`);
    } catch (e: unknown) {
      setError(toErrorMessage(e, "レビューの開始に失敗しました"));
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="w-full max-w-3xl mx-auto">
      <textarea
        {...register("prdText", { required: true })}
        rows={14}
        placeholder="レビュー対象の製品要求仕様書（PRD）をこちらに貼り付けてください。"
        className="w-full rounded border border-gray-300 p-3 outline-none focus:ring-2 focus:ring-blue-500"
      />
      {error && <p className="text-red-600 text-sm mt-2">{error}</p>}
      <div className="flex justify-end mt-4">
        <button
          type="submit"
          disabled={formState.isSubmitting}
          className="inline-flex items-center gap-2 rounded bg-blue-600 text-white px-4 py-2 hover:bg-blue-700 disabled:opacity-60"
        >
          {formState.isSubmitting ? "開始中..." : "専門家レビューを開始"}
        </button>
      </div>
    </form>
  );
}
