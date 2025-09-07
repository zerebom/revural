export default async function ReviewSummaryPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return (
    <main className="min-h-screen p-6 sm:p-10 bg-gray-50">
      <div className="max-w-3xl mx-auto w-full space-y-4">
        <h1 className="text-2xl font-semibold">共有サマリーページ</h1>
        <p className="text-gray-700">レビューID: {id}</p>
        <p className="text-gray-600">このページではレビュー結果のサマリーを共有します。（実装拡張予定）</p>
      </div>
    </main>
  );
}
