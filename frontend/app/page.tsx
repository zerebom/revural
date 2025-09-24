"use client";

import PrdInputForm from "@/components/PrdInputForm";

export default function Home() {
  return (
    <main className="min-h-screen p-6 sm:p-10 bg-gray-50">
      <section className="w-full max-w-5xl mx-auto mb-6">
        <h1 className="text-3xl font-bold tracking-tight">RevuRal</h1>
        <h2 className="mt-2 text-lg text-gray-900">そのドキュメント、専門家チームが即時レビューします。</h2>
        <p className="mt-2 text-sm text-gray-600">
          開発、UX、QA、ビジネスなど多様な視点からドキュメントをレビューし、潜在的なリスクや不明点を明確化。手戻りや認識の齟齬を防ぎます。
        </p>
      </section>
      <PrdInputForm />
    </main>
  );
}
