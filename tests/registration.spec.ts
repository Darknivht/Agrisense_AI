import { test, expect } from '@playwright/test';

test.describe('imam Farm Assist - Registration Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should display beautiful homepage with multicolored design', async ({ page }) => {
    // Check page title and header
    await expect(page).toHaveTitle(/imam Farm Assist/);
    await expect(page.locator('h1')).toContainText('imam Farm Assist');
    await expect(page.locator('.subtitle')).toContainText('Smart Agricultural AI Assistant');

    // Verify multicolored gradient background
    const heroSection = page.locator('.hero-section');
    await expect(heroSection).toBeVisible();
    
    // Check for the beautiful color scheme
    const heroStyle = await heroSection.getAttribute('style');
    expect(heroStyle).toContain('background');
  });

  test('should have responsive design elements', async ({ page }) => {
    // Check main container
    await expect(page.locator('.container')).toBeVisible();
    
    // Verify card-based layout
    await expect(page.locator('.card.registration-card')).toBeVisible();
    await expect(page.locator('.card.chat-card')).toBeVisible();
    await expect(page.locator('.sms-card')).toBeVisible();

    // Test responsive grid
    const mainGrid = page.locator('.main-grid');
    await expect(mainGrid).toBeVisible();
  });

  test('should display registration form with proper styling', async ({ page }) => {
    // Check form elements
    await expect(page.locator('#fullName')).toBeVisible();
    await expect(page.locator('#phone')).toBeVisible();
    await expect(page.locator('#location')).toBeVisible();

    // Verify form styling and icons
    await expect(page.locator('label[for="fullName"] i')).toHaveClass(/fas fa-user/);
    await expect(page.locator('label[for="phone"] i')).toHaveClass(/fas fa-phone/);
    await expect(page.locator('label[for="location"] i')).toHaveClass(/fas fa-map-marker-alt/);
  });

  test('should validate registration form fields', async ({ page }) => {
    const submitBtn = page.locator('.btn.btn-primary');
    
    // Try to submit empty form
    await submitBtn.click();
    
    // Check HTML5 validation
    await expect(page.locator('#fullName:invalid')).toBeVisible();
    await expect(page.locator('#phone:invalid')).toBeVisible();
    await expect(page.locator('#location:invalid')).toBeVisible();
  });

  test('should complete registration successfully', async ({ page }) => {
    // Fill registration form
    await page.fill('#fullName', 'Ahmad Ibrahim');
    await page.fill('#phone', '8012345678');
    await page.selectOption('#location', 'taruni');

    // Submit form
    await page.click('.btn.btn-primary');

    // Wait for success message in chat
    await expect(page.locator('.message.ai-message')).toContainText('Registration successful');
    await expect(page.locator('.message.ai-message')).toContainText('Ahmad Ibrahim');
    await expect(page.locator('.message.ai-message')).toContainText('taruni');

    // Form should be cleared
    await expect(page.locator('#fullName')).toHaveValue('');
    await expect(page.locator('#phone')).toHaveValue('');
    await expect(page.locator('#location')).toHaveValue('');
  });

  test('should validate phone number format', async ({ page }) => {
    await page.fill('#phone', '123'); // Invalid format
    await page.fill('#fullName', 'Test User');
    await page.selectOption('#location', 'hotoro');
    
    await page.click('.btn.btn-primary');
    
    // Should show HTML5 validation error
    await expect(page.locator('#phone:invalid')).toBeVisible();
  });

  test('should display beautiful button states and animations', async ({ page }) => {
    const primaryBtn = page.locator('.btn.btn-primary');
    const callBtn = page.locator('.btn.btn-call');

    // Check button styling
    await expect(primaryBtn).toHaveCSS('background', /linear-gradient/);
    await expect(callBtn).toBeVisible();

    // Test hover states (if possible)
    await primaryBtn.hover();
    await callBtn.hover();
  });
});

test.describe('Mobile Responsiveness', () => {
  test('should display correctly on mobile devices', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');

    // Check mobile layout
    await expect(page.locator('.container')).toBeVisible();
    await expect(page.locator('.main-grid')).toBeVisible();

    // Verify cards stack properly on mobile
    const cards = page.locator('.card');
    expect(await cards.count()).toBeGreaterThanOrEqual(2);
  });

  test('should have touch-friendly buttons on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');

    // Check button sizes are appropriate for touch
    const buttons = page.locator('.btn');
    for (const button of await buttons.all()) {
      const box = await button.boundingBox();
      expect(box?.height).toBeGreaterThanOrEqual(44); // Minimum touch target size
    }
  });
});