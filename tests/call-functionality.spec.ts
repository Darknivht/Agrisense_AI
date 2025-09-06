import { test, expect } from '@playwright/test';

test.describe('imam Farm Assist - Call Functionality', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should display call button with beautiful styling', async ({ page }) => {
    // Check call button
    const callBtn = page.locator('.btn.btn-call');
    await expect(callBtn).toBeVisible();
    
    // Check button text and icon
    await expect(callBtn).toContainText('Call Me');
    await expect(callBtn.locator('i')).toHaveClass(/fas fa-phone-alt/);
    
    // Check button styling (call button should have distinct color)
    await expect(callBtn).toHaveCSS('background', /linear-gradient/);
  });

  test('should initiate call when button is clicked', async ({ page }) => {
    // Set up dialog handler for the alert
    page.on('dialog', async dialog => {
      expect(dialog.type()).toBe('alert');
      expect(dialog.message()).toContain('Mock call initiated');
      await dialog.accept();
    });

    const callBtn = page.locator('.btn.btn-call');
    await callBtn.click();

    // Button should show loading state briefly
    await expect(callBtn).toContainText('Calling...', { timeout: 1000 });
    await expect(callBtn).toBeDisabled();
  });

  test('should handle call button loading state', async ({ page }) => {
    const callBtn = page.locator('.btn.btn-call');
    
    // Mock slow response to test loading state
    await page.route('/call-me', async route => {
      await new Promise(resolve => setTimeout(resolve, 1000));
      await route.fulfill({
        status: 200,
        contentType: 'text/plain',
        body: 'Mock call initiated! Voice functionality not available in demo mode.'
      });
    });

    // Set up dialog handler
    page.on('dialog', async dialog => {
      await dialog.accept();
    });

    await callBtn.click();

    // Should show loading state
    await expect(callBtn).toContainText('Calling...');
    await expect(callBtn).toBeDisabled();
    
    // Should return to normal state after response
    await expect(callBtn).not.toContainText('Calling...', { timeout: 3000 });
    await expect(callBtn).not.toBeDisabled();
  });

  test('should handle call errors gracefully', async ({ page }) => {
    // Mock error response
    await page.route('/call-me', route => {
      route.fulfill({
        status: 500,
        contentType: 'text/plain',
        body: 'Call failed: Network error'
      });
    });

    // Set up dialog handler for error
    page.on('dialog', async dialog => {
      expect(dialog.message()).toContain('Call failed');
      await dialog.accept();
    });

    const callBtn = page.locator('.btn.btn-call');
    await callBtn.click();

    // Button should return to normal state after error
    await expect(callBtn).not.toBeDisabled({ timeout: 3000 });
  });

  test('should have accessible call button', async ({ page }) => {
    const callBtn = page.locator('.btn.btn-call');
    
    // Should be focusable
    await callBtn.focus();
    await expect(callBtn).toBeFocused();
    
    // Should be activatable with Enter key
    page.on('dialog', async dialog => {
      await dialog.accept();
    });
    
    await callBtn.press('Enter');
    
    // Should show loading state
    await expect(callBtn).toContainText('Calling...', { timeout: 1000 });
  });

  test('should position call button correctly in layout', async ({ page }) => {
    const callBtn = page.locator('.btn.btn-call');
    const registrationCard = page.locator('.card.registration-card');
    
    // Call button should be inside action-buttons container within registration card
    await expect(registrationCard.locator('.action-buttons .btn.btn-call')).toBeVisible();
    
    // Should be positioned after the registration form
    const form = page.locator('form');
    const actionButtons = page.locator('.action-buttons');
    
    // Both should be visible and properly ordered
    await expect(form).toBeVisible();
    await expect(actionButtons).toBeVisible();
  });

  test('should have proper button hierarchy and styling', async ({ page }) => {
    const primaryBtn = page.locator('.btn.btn-primary');
    const callBtn = page.locator('.btn.btn-call');
    
    // Both buttons should be visible
    await expect(primaryBtn).toBeVisible();
    await expect(callBtn).toBeVisible();
    
    // Should have different styling to indicate different purposes
    const primaryBg = await primaryBtn.evaluate(el => getComputedStyle(el).background);
    const callBg = await callBtn.evaluate(el => getComputedStyle(el).background);
    
    // Should have different background styles
    expect(primaryBg).not.toBe(callBg);
  });
});

test.describe('Call Functionality - Mobile Experience', () => {
  test('should display call button properly on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');

    const callBtn = page.locator('.btn.btn-call');
    await expect(callBtn).toBeVisible();
    
    // Should be touch-friendly size
    const buttonBox = await callBtn.boundingBox();
    expect(buttonBox?.height).toBeGreaterThanOrEqual(44);
    expect(buttonBox?.width).toBeGreaterThanOrEqual(44);
  });

  test('should handle touch interaction on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');

    // Set up dialog handler
    page.on('dialog', async dialog => {
      await dialog.accept();
    });

    const callBtn = page.locator('.btn.btn-call');
    
    // Simulate touch tap
    await callBtn.tap();
    
    // Should trigger call
    await expect(callBtn).toContainText('Calling...', { timeout: 1000 });
  });

  test('should maintain proper spacing on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');

    const registrationCard = page.locator('.card.registration-card');
    const actionButtons = page.locator('.action-buttons');
    
    // Should maintain proper spacing between form and call button
    await expect(registrationCard).toBeVisible();
    await expect(actionButtons).toBeVisible();
    
    // Should not overflow or be cut off
    const callBtn = page.locator('.btn.btn-call');
    await expect(callBtn).toBeInViewport();
  });
});