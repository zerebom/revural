export function shortenOriginalText(text: string, limit = 160): string {
  const normalized = text?.trim() ?? "";
  if (normalized.length <= limit) {
    return normalized;
  }
  return `${normalized.slice(0, limit).trimEnd()}...`;
}
