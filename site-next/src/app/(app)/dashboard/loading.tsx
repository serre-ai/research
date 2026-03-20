import { Skeleton } from '@/components/ui/skeleton';

function MetricSkeleton() {
  return (
    <div className="border border-border bg-bg-elevated p-6 flex flex-col gap-2">
      <div className="flex items-center justify-between">
        <Skeleton className="h-3 w-16" />
        <Skeleton className="h-4 w-4" />
      </div>
      <Skeleton className="h-8 w-20" />
    </div>
  );
}

function ProjectCardSkeleton() {
  return (
    <div className="border border-border bg-bg-elevated p-6 flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <Skeleton className="h-4 w-32" />
        <Skeleton className="h-5 w-16" />
      </div>
      <Skeleton className="h-3 w-48" />
      <Skeleton className="h-3 w-24" />
    </div>
  );
}

export default function DashboardLoading() {
  return (
    <div>
      {/* Page header */}
      <div className="mb-8">
        <Skeleton className="h-7 w-32" />
        <Skeleton className="mt-2 h-4 w-64" />
      </div>

      {/* Metric cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <MetricSkeleton />
        <MetricSkeleton />
        <MetricSkeleton />
        <MetricSkeleton />
      </div>

      {/* Projects section */}
      <div className="mt-8">
        <Skeleton className="mb-4 h-4 w-16" />
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          <ProjectCardSkeleton />
          <ProjectCardSkeleton />
        </div>
      </div>

      {/* Bottom row: Decisions + Health */}
      <div className="mt-8 grid grid-cols-1 gap-4 lg:grid-cols-3">
        {/* Decisions skeleton */}
        <div className="border border-border bg-bg-elevated p-6 lg:col-span-2">
          <Skeleton className="mb-4 h-4 w-32" />
          <div className="space-y-3">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="space-y-1.5">
                <Skeleton className="h-3 w-3/4" />
                <Skeleton className="h-3 w-1/2" />
              </div>
            ))}
          </div>
        </div>

        {/* Health skeleton */}
        <div className="border border-border bg-bg-elevated p-6">
          <Skeleton className="mb-4 h-4 w-24" />
          <div className="space-y-3">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="flex items-center gap-3">
                <Skeleton className="h-2 w-2 rounded-full" />
                <Skeleton className="h-3 w-24" />
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
