"use client";

import PrdInputForm from "@/components/PrdInputForm";

export default function Home() {
  return (
    <main className="min-h-screen p-6 sm:p-10 bg-gray-50">
      <section className="w-full max-w-3xl mx-auto mb-6">
        <h1 className="text-3xl font-bold tracking-tight">SpecCheck</h1>
        <h2 className="mt-2 text-lg text-gray-900">そのPRD、専門家チームが瞬時にレビューします。</h2>
        <p className="mt-2 text-sm text-gray-600">
          開発、UX、QA、ビジネスの専門的な視点から仕様をレビューし、潜在的なリスクや曖昧な点を明確にすることで、開発の手戻りを防ぎます。
        </p>
      </section>
      <PrdInputForm />
    </main>
  );
}
