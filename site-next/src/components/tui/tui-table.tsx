import { clsx } from 'clsx';

interface TuiTableColumn<T> {
  key: string;
  header: string;
  render?: (row: T) => React.ReactNode;
  className?: string;
}

interface TuiTableProps<T> {
  columns: TuiTableColumn<T>[];
  data: T[];
  rowKey: (row: T) => string;
  onRowClick?: (row: T) => void;
  className?: string;
}

/**
 * Monospace-aligned table with header separator.
 *
 * NAME              STATUS    VENUE
 * ─────────────────────────────────
 * reasoning-gaps    analysis  NeurIPS
 * verification      writing   ICLR
 */
export function TuiTable<T extends Record<string, unknown>>({
  columns,
  data,
  rowKey,
  onRowClick,
  className,
}: TuiTableProps<T>) {
  return (
    <table className={clsx('tui-table', className)}>
      <thead>
        <tr>
          {columns.map((col) => (
            <th key={col.key} className={col.className}>
              {col.header}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {data.map((row) => (
          <tr
            key={rowKey(row)}
            onClick={onRowClick ? () => onRowClick(row) : undefined}
            onKeyDown={onRowClick ? (e) => { if (e.key === 'Enter') onRowClick(row); } : undefined}
            role={onRowClick ? 'link' : undefined}
            tabIndex={onRowClick ? 0 : undefined}
          >
            {columns.map((col) => (
              <td key={col.key} className={col.className}>
                {col.render ? col.render(row) : String(row[col.key] ?? '')}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
