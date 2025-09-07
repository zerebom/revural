import ReviewFocusView from "@/components/ReviewFocusView";

export default async function ReviewDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return (
    <main className="min-h-screen p-6 sm:p-10 bg-gray-50">
      <ReviewFocusView reviewId={id} />
    </main>
  );
}
