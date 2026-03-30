'use client';

interface PdfViewerProps {
  available?: boolean;
}

export function PdfViewer({ available }: PdfViewerProps) {
  if (!available) {
    return <span className="text-text-muted">no PDF available -- run a paper build first</span>;
  }

  return (
    <div className="space-y-2">
      <iframe
        src="/proxy/paper/pdf"
        className="w-full h-[600px] border border-border"
        title="Paper PDF Preview"
      />
      <a
        href="/proxy/paper/download"
        download
        className="border border-border bg-bg-elevated px-2 py-1 font-mono text-xs text-text-secondary hover:text-text-bright inline-block"
      >
        [download pdf]
      </a>
    </div>
  );
}
