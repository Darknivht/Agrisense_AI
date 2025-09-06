import { test, expect } from '@playwright/test';

test.describe('imam Farm Assist - SMS Functionality', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should display SMS interface with beautiful styling', async ({ page }) => {
    // Check SMS card
    await expect(page.locator('.sms-card')).toBeVisible();
    await expect(page.locator('.sms-card h3')).toContainText('Send SMS to imam Farm Assist');
    
    // Check SMS icon
    await expect(page.locator('.sms-card h3 i')).toHaveClass(/fas fa-sms/);
    
    // Check input field
    const smsInput = page.locator('#smsInput');
    await expect(smsInput).toBeVisible();
    await expect(smsInput).toHaveAttribute('placeholder', /Type SMS message in Hausa or English/);
    
    // Check send button
    const smsBtn = page.locator('.sms-card .btn-secondary');
    await expect(smsBtn).toBeVisible();
    await expect(smsBtn.locator('i')).toHaveClass(/fas fa-paper-plane/);
  });

  test('should send SMS and receive reply', async ({ page }) => {
    const smsInput = page.locator('#smsInput');
    const smsBtn = page.locator('.sms-card .btn-secondary');
    const smsReply = page.locator('#smsReply');

    // Send SMS about water
    await smsInput.fill('Need help with water for crops');
    await smsBtn.click();

    // Wait for reply
    await expect(smsReply).toContainText('SMS Reply:', { timeout: 5000 });
    await expect(smsReply).toContainText('Ka tabbata ka shayar da shinkafa');
    
    // Input should be cleared
    await expect(smsInput).toHaveValue('');

    // Check reply formatting
    await expect(smsReply.locator('i.fas.fa-reply')).toBeVisible();
    await expect(smsReply.locator('.voice-btn')).toBeVisible();
  });

  test('should handle fertilizer SMS requests', async ({ page }) => {
    const smsInput = page.locator('#smsInput');
    const smsBtn = page.locator('.sms-card .btn-secondary');

    // Send SMS about fertilizer
    await smsInput.fill('fertilizer advice needed');
    await smsBtn.click();

    // Should receive fertilizer advice
    await expect(page.locator('#smsReply')).toContainText('taki mai kyau', { timeout: 5000 });
  });

  test('should display loading state during SMS sending', async ({ page }) => {
    const smsInput = page.locator('#smsInput');
    const smsBtn = page.locator('.sms-card .btn-secondary');

    // Send SMS
    await smsInput.fill('test sms message');
    await smsBtn.click();

    // Button should show loading state
    await expect(smsBtn).toContainText('Sending...');
    await expect(smsBtn).toBeDisabled();
    
    // Should return to normal state
    await expect(smsBtn).not.toBeDisabled({ timeout: 5000 });
    await expect(smsBtn).not.toContainText('Sending...');
  });

  test('should handle empty SMS messages', async ({ page }) => {
    const smsInput = page.locator('#smsInput');
    const smsBtn = page.locator('.sms-card .btn-secondary');

    // Try to send empty SMS
    await smsInput.fill('   '); // Just spaces
    await smsBtn.click();

    // Should not process empty message
    await expect(smsInput).toHaveValue('');
    
    // Try with completely empty
    await smsBtn.click();
    
    // Should not show loading or send anything
    await expect(smsBtn).not.toContainText('Sending...');
  });

  test('should include voice button in SMS replies', async ({ page }) => {
    await page.fill('#smsInput', 'water crops');
    await page.click('.sms-card .btn-secondary');

    // Wait for reply
    await expect(page.locator('#smsReply')).toContainText('SMS Reply:', { timeout: 5000 });
    
    // Check voice button
    const voiceBtn = page.locator('#smsReply .voice-btn');
    await expect(voiceBtn).toBeVisible();
    await expect(voiceBtn.locator('i')).toHaveClass(/fas fa-volume-up/);
    await expect(voiceBtn).toContainText('Play Reply');
  });

  test('should handle multiple SMS exchanges', async ({ page }) => {
    const smsInput = page.locator('#smsInput');
    const smsBtn = page.locator('.sms-card .btn-secondary');

    // Send first SMS
    await smsInput.fill('water advice');
    await smsBtn.click();
    await page.waitForTimeout(1000);

    // Send second SMS
    await smsInput.fill('fertilizer help');
    await smsBtn.click();
    
    // Should replace previous reply with new one
    await expect(page.locator('#smsReply')).toContainText('taki mai kyau', { timeout: 5000 });
  });

  test('should display beautiful SMS reply styling', async ({ page }) => {
    await page.fill('#smsInput', 'farming help');
    await page.click('.sms-card .btn-secondary');

    // Wait for reply
    await page.waitForTimeout(2000);
    
    const smsReply = page.locator('#smsReply');
    
    // Check styling elements
    await expect(smsReply.locator('i.fas.fa-reply')).toBeVisible();
    await expect(smsReply).toContainText('SMS Reply:');
    
    // Check white background for reply content
    const replyContent = smsReply.locator('div[style*="background: white"]');
    await expect(replyContent).toBeVisible();
  });

  test('should handle error states gracefully', async ({ page }) => {
    // Mock a network error by intercepting the request
    await page.route('/sms-reply', route => {
      route.abort();
    });

    await page.fill('#smsInput', 'test message');
    await page.click('.sms-card .btn-secondary');

    // Should show error message
    await expect(page.locator('#smsReply')).toContainText('Error sending SMS', { timeout: 5000 });
    await expect(page.locator('#smsReply i.fas.fa-exclamation-triangle')).toBeVisible();
  });
});

test.describe('SMS Interface - Mobile Responsiveness', () => {
  test('should display SMS interface correctly on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');

    // Check SMS card on mobile
    await expect(page.locator('.sms-card')).toBeVisible();
    
    // Input should be full width on mobile
    const smsInput = page.locator('#smsInput');
    await expect(smsInput).toBeVisible();
    
    // Button should be touch-friendly
    const smsBtn = page.locator('.sms-card .btn-secondary');
    const buttonBox = await smsBtn.boundingBox();
    expect(buttonBox?.height).toBeGreaterThanOrEqual(44);
  });

  test('should handle SMS replies on mobile viewport', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');

    await page.fill('#smsInput', 'mobile test');
    await page.click('.sms-card .btn-secondary');

    // Reply should display properly on mobile
    await expect(page.locator('#smsReply')).toBeVisible({ timeout: 5000 });
    
    // Voice button should be touch-friendly
    const voiceBtn = page.locator('#smsReply .voice-btn');
    await expect(voiceBtn).toBeVisible();
    
    const voiceBtnBox = await voiceBtn.boundingBox();
    expect(voiceBtnBox?.height).toBeGreaterThanOrEqual(40);
  });
});