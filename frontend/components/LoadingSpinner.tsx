interface LoadingSpinnerProps {
  progress?: number | null;
  phaseMessage?: string | null;
  expectedAgents?: string[] | null;
  completedAgents?: string[] | null;
}

const SPINNER_ICON = (
  <svg className="h-6 w-6 animate-spin text-slate-400" viewBox="0 0 24 24" role="presentation">
    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
  </svg>
);

const CHECK_ICON = (
  <svg
    className="h-4 w-4"
    viewBox="0 0 20 20"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <path
      d="M16.704 5.293a1 1 0 00-1.408 0L8.5 12.086 5.704 9.293a1 1 0 10-1.408 1.414l3.5 3.5a1 1 0 001.408 0l7.5-7.5a1 1 0 000-1.414z"
      fill="currentColor"
    />
  </svg>
);

function toDisplayName(label: string) {
  return label
    .split(/[_\s]+/)
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

export default function LoadingSpinner({
  progress = 0,
  phaseMessage,
  expectedAgents,
  completedAgents,
}: LoadingSpinnerProps) {
  const pct = Math.max(0, Math.min(100, Math.round((progress ?? 0) * 100)));
  const agents = expectedAgents ?? [];
  const completedSet = new Set(completedAgents ?? []);

  return (
    <div className="flex min-h-[340px] flex-col items-center justify-center gap-6 px-6 py-8" role="status" aria-label="レビュー進行中">
      <div className="flex items-center gap-3 text-slate-600">
        {SPINNER_ICON}
        <span className="typ-body">レビューを実行しています…</span>
      </div>
      <div className="w-full max-w-md space-y-4">
        <div className="h-2.5 rounded-full bg-slate-200/80">
          <div
            className="h-2.5 rounded-full bg-indigo-400 transition-[width] duration-500 ease-out"
            style={{ width: `${pct}%` }}
            role="presentation"
          />
        </div>
        <div className="flex items-center justify-between typ-caption text-slate-500">
          <span>{phaseMessage || "専門家がPRDを解析しています"}</span>
          <span>{pct}%</span>
        </div>
        {agents.length > 0 && (
          <div className="rounded-lg border border-slate-200/70 bg-white/80 p-3">
            <p className="typ-caption mb-2 text-slate-500">参加中のエージェント</p>
            <ul className="space-y-1">
              {agents.map((name) => {
                const finished = completedSet.has(name);
                return (
                  <li key={name} className="flex items-center justify-between rounded-md px-2 py-1 text-sm text-slate-600">
                    <span>{toDisplayName(name)}</span>
                    <span className={finished ? "text-emerald-500" : "text-slate-400"}>
                      {finished ? CHECK_ICON : "…"}
                    </span>
                  </li>
                );
              })}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
