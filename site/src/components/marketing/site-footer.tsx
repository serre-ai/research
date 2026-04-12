import { Separator } from '@/components/ui/separator';

export function SiteFooter() {
  return (
    <footer className="mx-auto max-w-3xl px-6 pb-12 pt-16">
      <Separator className="mb-6" />
      <div className="flex items-center justify-between text-xs text-muted-foreground">
        <span>Reykjavik</span>
        <span>oddur@serre.ai</span>
      </div>
    </footer>
  );
}
