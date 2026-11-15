import { test, expect } from '@playwright/test';

test('AC-2 shows another title', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveTitle('Not the title');
});
