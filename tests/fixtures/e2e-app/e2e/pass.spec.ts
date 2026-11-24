import { test, expect } from '@playwright/test';

test('AC-1 shows the title', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveTitle('NIO Demo');
});
