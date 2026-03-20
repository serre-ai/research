'use client';

import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
} from 'recharts';
import { Card } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import type { CalibrationBucket } from '@/lib/collective-types';

interface CalibrationChartProps {
  buckets: CalibrationBucket[];
  brierScore?: number;
}

export function CalibrationChart({ buckets, brierScore }: CalibrationChartProps) {
  const data = buckets.map((b) => ({
    predicted: b.predicted_avg,
    actual: b.actual_avg,
    count: b.count,
  }));

  return (
    <Card>
      <div className="flex items-center justify-between mb-4">
        <Label>Calibration</Label>
        {brierScore !== undefined && (
          <span className="font-mono text-xs text-text-muted">
            Brier: <span className="text-text-bright">{brierScore.toFixed(3)}</span>
          </span>
        )}
      </div>
      <ResponsiveContainer width="100%" height={240}>
        <ScatterChart margin={{ top: 10, right: 10, bottom: 20, left: 10 }}>
          <XAxis
            dataKey="predicted"
            type="number"
            domain={[0, 1]}
            tick={{ fontSize: 10, fontFamily: 'IBM Plex Mono', fill: '#737373' }}
            label={{ value: 'Predicted', position: 'bottom', fontSize: 10, fontFamily: 'IBM Plex Mono', fill: '#737373' }}
          />
          <YAxis
            dataKey="actual"
            type="number"
            domain={[0, 1]}
            tick={{ fontSize: 10, fontFamily: 'IBM Plex Mono', fill: '#737373' }}
            label={{ value: 'Actual', angle: -90, position: 'insideLeft', fontSize: 10, fontFamily: 'IBM Plex Mono', fill: '#737373' }}
          />
          <ReferenceLine
            segment={[{ x: 0, y: 0 }, { x: 1, y: 1 }]}
            stroke="#404040"
            strokeDasharray="4 4"
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#171717',
              border: '1px solid rgba(255,255,255,0.1)',
              fontFamily: 'IBM Plex Mono',
              fontSize: 11,
            }}
            formatter={(value) => typeof value === 'number' ? value.toFixed(2) : String(value)}
          />
          <Scatter data={data} fill="#3b82f6" />
        </ScatterChart>
      </ResponsiveContainer>
    </Card>
  );
}
