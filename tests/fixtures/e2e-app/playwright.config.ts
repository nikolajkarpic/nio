import { defineConfig } from '@playwright/test';

export default defineConfig({
  timeout: 12345,
  outputDir: 'pw-out',
  webServer: { command: 'python3 -m http.server 4173 # nio-e2e-marker', url: 'http://127.0.0.1:4173' },
  use: { baseURL: 'http://127.0.0.1:4173' },
});
