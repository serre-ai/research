import { TuiBox, TuiTable, TuiBadge, TuiProgress } from '@/components/tui';

interface Project {
  name: string;
  title: string;
  venue?: string;
  phase?: string;
  status: string;
  confidence?: number;
}

export function ProjectsTable({ projects }: { projects: Project[] }) {
  return (
    <TuiBox title="PROJECTS">
      {projects.length > 0 ? (
        <TuiTable<Project>
          columns={[
            {
              key: 'name',
              header: 'Name',
              render: (row) => (
                <span className="text-text-bright">{row.name}</span>
              ),
            },
            {
              key: 'venue',
              header: 'Venue',
              className: 'text-text-muted',
              render: (row) => row.venue ?? '—',
            },
            {
              key: 'phase',
              header: 'Phase',
              render: (row) => (
                <TuiBadge color="accent">{row.phase ?? row.status}</TuiBadge>
              ),
            },
            {
              key: 'confidence',
              header: 'Conf',
              render: (row) => {
                const conf = row.confidence ?? 0;
                return (
                  <TuiProgress
                    value={Math.round(conf * 100)}
                    width={8}
                    showPercent={false}
                    color={conf > 0.7 ? 'ok' : conf > 0.3 ? 'warn' : 'error'}
                  />
                );
              },
            },
          ]}
          data={projects}
          rowKey={(r) => r.name}
        />
      ) : (
        <span className="font-mono text-xs text-text-muted">no projects</span>
      )}
    </TuiBox>
  );
}
