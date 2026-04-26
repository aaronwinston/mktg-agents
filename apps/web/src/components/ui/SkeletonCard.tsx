export function SkeletonCard() {
  return (
    <div className="border border-border rounded-xl p-4 bg-bg-secondary overflow-hidden">
      <div className="flex items-center gap-2 mb-3">
        <div className="h-4 w-16 rounded bg-gradient-to-r from-bg-tertiary via-border to-bg-tertiary bg-[length:200%_100%] animate-shimmer" />
        <div className="h-3 w-8 rounded bg-gradient-to-r from-bg-tertiary via-border to-bg-tertiary bg-[length:200%_100%] animate-shimmer" />
      </div>
      <div className="space-y-2 mb-3">
        <div className="h-4 w-full rounded bg-gradient-to-r from-bg-tertiary via-border to-bg-tertiary bg-[length:200%_100%] animate-shimmer" />
        <div className="h-4 w-3/4 rounded bg-gradient-to-r from-bg-tertiary via-border to-bg-tertiary bg-[length:200%_100%] animate-shimmer" />
      </div>
      <div className="h-3 w-full rounded bg-gradient-to-r from-bg-tertiary via-border to-bg-tertiary bg-[length:200%_100%] animate-shimmer mb-2" />
      <div className="h-3 w-2/3 rounded bg-gradient-to-r from-bg-tertiary via-border to-bg-tertiary bg-[length:200%_100%] animate-shimmer" />
    </div>
  );
}
