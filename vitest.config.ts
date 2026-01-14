import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./campaign_master/web/react/__tests__/setup.ts'],
    include: ['./campaign_master/web/react/**/*.test.{ts,tsx}'],
    css: true,
  },
});
