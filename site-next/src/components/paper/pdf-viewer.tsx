'use client';

import { FileOutput } from 'lucide-react';
import { EmptyState } from '@/components/ui/empty-state';
import { Button } from '@/components/ui/button';

interface PdfViewerProps {
  available?: boolean;
}

export function PdfViewer({ available }: PdfViewerProps) {
  if (!available) {
    return (
      <EmptyState
        icon={FileOutput}
        message="No PDF available"
        description="Run a paper build to generate the PDF"
      />
    );
  }

  return (
    <div className="space-y-4">
      <iframe
        src="/proxy/paper/pdf"
        className="w-full h-[600px] border border-border"
        title="Paper PDF Preview"
      />
      <a href="/proxy/paper/download" download>
        <Button variant="secondary" size="sm">
          Download PDF
        </Button>
      </a>
    </div>
  );
}
