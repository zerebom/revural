import SummaryPage from "@/components/SummaryPage";

export default async function ReviewSummaryPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <SummaryPage reviewId={id} />;
}
