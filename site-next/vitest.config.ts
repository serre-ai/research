import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import { resolve } from 'node:path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': resolve(__dirname, './src'),
    },
    dedupe: ['react', 'react-dom'],
  },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/test/setup.ts'],
    include: ['src/**/*.test.{ts,tsx}'],
    css: false,
    server: {
      deps: {
        // Inline @tanstack/react-query so Vite resolves its `react` import
        // through our alias/dedupe instead of Node's module resolution
        // (which would pick up the workspace-root React 18).
        inline: ['@tanstack/react-query'],
      },
    },
  },
});
