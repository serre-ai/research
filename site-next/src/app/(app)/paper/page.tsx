'use client';

import { PageHeader } from '@/components/ui/page-header';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { BuildStatusCard } from '@/components/paper/build-status-card';
import { BuildLogViewer } from '@/components/paper/build-log-viewer';
import { PdfViewer } from '@/components/paper/pdf-viewer';
import { usePaperStatus } from '@/hooks';

export default function PaperPage() {
  const { data: status } = usePaperStatus();

  return (
    <div>
      <PageHeader title="Paper Build" subtitle="Build and preview the research paper" />

      <div className="flex gap-6">
        {/* Left column */}
        <div className="w-1/3">
          <BuildStatusCard />
        </div>

        {/* Right column */}
        <div className="w-2/3">
          <Tabs defaultValue="pdf">
            <TabsList>
              <TabsTrigger value="pdf">PDF Preview</TabsTrigger>
              <TabsTrigger value="log">Build Log</TabsTrigger>
            </TabsList>
            <TabsContent value="pdf">
              <PdfViewer available={status?.status === 'success'} />
            </TabsContent>
            <TabsContent value="log">
              <BuildLogViewer />
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
}
