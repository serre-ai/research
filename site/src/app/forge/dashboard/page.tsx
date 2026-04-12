import { Card, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-lg font-semibold text-foreground">Dashboard</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Research platform overview
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardDescription>Projects</CardDescription>
            <CardTitle className="text-2xl">4</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader>
            <CardDescription>Active Agents</CardDescription>
            <CardTitle className="text-2xl">0</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader>
            <CardDescription>Monthly Spend</CardDescription>
            <CardTitle className="text-2xl">$0</CardTitle>
          </CardHeader>
        </Card>
      </div>

      <Card className="border-dashed">
        <CardHeader>
          <CardDescription className="text-center">
            Dashboard pages are being migrated. Connect the data layer in Phase 3.
          </CardDescription>
        </CardHeader>
      </Card>
    </div>
  );
}
