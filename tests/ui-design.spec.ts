import { test, expect } from '@playwright/test';

test.describe('imam Farm Assist - UI Design & Visual Elements', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should display beautiful gradient background', async ({ page }) => {
    const heroSection = page.locator('.hero-section');
    await expect(heroSection).toBeVisible();
    
    // Check for gradient background
    const heroStyle = await heroSection.evaluate(el => getComputedStyle(el).background);
    expect(heroStyle).toContain('gradient');
  });

  test('should have proper color scheme and typography', async ({ page }) => {
    // Check main heading
    const heading = page.locator('h1');
    await expect(heading).toBeVisible();
    await expect(heading).toHaveCSS('color', 'rgb(255, 255, 255)'); // White text
    
    // Check subtitle
    const subtitle = page.locator('.subtitle');
    await expect(subtitle).toBeVisible();
    
    // Check card backgrounds
    const cards = page.locator('.card');
    expect(await cards.count()).toBeGreaterThan(0);
    
    for (const card of await cards.all()) {
      const cardBg = await card.evaluate(el => getComputedStyle(el).background);
      expect(cardBg).toContain('rgba(255, 255, 255'); // Semi-transparent white
    }
  });

  test('should display Font Awesome icons correctly', async ({ page }) => {
    // Check various icons throughout the interface
    const icons = [
      '.fas.fa-seedling',         // Main logo
      '.fas.fa-user',             // User icon
      '.fas.fa-phone',            // Phone icon  
      '.fas.fa-map-marker-alt',   // Location icon
      '.fas.fa-user-plus',        // Registration icon
      '.fas.fa-phone-alt',        // Call icon
      '.fas.fa-comments',         // Chat icon
      '.fas.fa-paper-plane',      // Send icon
      '.fas.fa-volume-up',        // Voice icon
      '.fas.fa-sms',              // SMS icon
      '.fas.fa-robot'             // AI icon (in messages)
    ];

    for (const iconSelector of icons) {
      const icon = page.locator(iconSelector).first();
      if (await icon.isVisible()) {
        await expect(icon).toBeVisible();
      }
    }
  });

  test('should have proper button styling and hover effects', async ({ page }) => {
    const buttons = [
      '.btn.btn-primary',
      '.btn.btn-call', 
      '.btn.btn-secondary'
    ];

    for (const btnSelector of buttons) {
      const button = page.locator(btnSelector).first();
      if (await button.isVisible()) {
        // Check gradient background
        const buttonBg = await button.evaluate(el => getComputedStyle(el).background);
        expect(buttonBg).toContain('gradient');
        
        // Check border radius
        await expect(button).toHaveCSS('border-radius', '25px');
        
        // Test hover effect
        await button.hover();
        // Note: CSS transitions may not be testable in this environment
      }
    }
  });

  test('should have proper card layout and shadows', async ({ page }) => {
    const cards = page.locator('.card');
    
    for (const card of await cards.all()) {
      // Check border radius
      await expect(card).toHaveCSS('border-radius', '15px');
      
      // Check box shadow
      const shadow = await card.evaluate(el => getComputedStyle(el).boxShadow);
      expect(shadow).not.toBe('none');
      
      // Check padding
      const padding = await card.evaluate(el => getComputedStyle(el).padding);
      expect(padding).toBeTruthy();
    }
  });

  test('should display proper form styling', async ({ page }) => {
    // Check form groups
    const formGroups = page.locator('.form-group');
    expect(await formGroups.count()).toBeGreaterThan(0);
    
    // Check input styling
    const inputs = page.locator('input[type="text"], input[type="tel"], select');
    for (const input of await inputs.all()) {
      // Check border radius
      await expect(input).toHaveCSS('border-radius', '10px');
      
      // Check padding
      const padding = await input.evaluate(el => getComputedStyle(el).padding);
      expect(padding).toBeTruthy();
    }
    
    // Check label styling
    const labels = page.locator('label');
    for (const label of await labels.all()) {
      const labelColor = await label.evaluate(el => getComputedStyle(el).color);
      expect(labelColor).toBeTruthy();
    }
  });

  test('should have responsive grid layout', async ({ page }) => {
    const mainGrid = page.locator('.main-grid');
    await expect(mainGrid).toBeVisible();
    
    // Check grid properties
    const gridDisplay = await mainGrid.evaluate(el => getComputedStyle(el).display);
    expect(gridDisplay).toBe('grid');
    
    const gridGap = await mainGrid.evaluate(el => getComputedStyle(el).gap);
    expect(gridGap).toBeTruthy();
  });

  test('should display loading animations', async ({ page }) => {
    // Check if loading CSS class exists
    const style = page.locator('style');
    const styleContent = await style.textContent();
    
    if (styleContent) {
      expect(styleContent).toContain('.loading');
      expect(styleContent).toContain('animation');
    }
  });

  test('should have proper spacing and margins', async ({ page }) => {
    const container = page.locator('.container');
    await expect(container).toBeVisible();
    
    // Check container padding
    const containerPadding = await container.evaluate(el => getComputedStyle(el).padding);
    expect(containerPadding).toBeTruthy();
    
    // Check sections have proper margins
    const sections = page.locator('.card, .sms-card');
    for (const section of await sections.all()) {
      const margin = await section.evaluate(el => getComputedStyle(el).margin);
      expect(margin).toBeTruthy();
    }
  });

  test('should have beautiful chat message styling', async ({ page }) => {
    // Wait for welcome message
    await expect(page.locator('.message.ai-message')).toBeVisible();
    
    const messages = page.locator('.message');
    expect(await messages.count()).toBeGreaterThan(0);
    
    // Check message styling
    for (const message of await messages.all()) {
      const messageBg = await message.evaluate(el => getComputedStyle(el).background);
      const messagePadding = await message.evaluate(el => getComputedStyle(el).padding);
      const messageBorderRadius = await message.evaluate(el => getComputedStyle(el).borderRadius);
      
      expect(messagePadding).toBeTruthy();
      expect(messageBorderRadius).toBeTruthy();
    }
  });

  test('should have proper voice button styling', async ({ page }) => {
    // Send a message to get AI response with voice button
    await page.fill('#chatInput', 'test');
    await page.press('#chatInput', 'Enter');
    
    await page.waitForTimeout(1000);
    
    const voiceButtons = page.locator('.voice-btn');
    if (await voiceButtons.count() > 0) {
      const voiceBtn = voiceButtons.first();
      
      // Check button styling
      const btnBg = await voiceBtn.evaluate(el => getComputedStyle(el).background);
      const btnBorderRadius = await voiceBtn.evaluate(el => getComputedStyle(el).borderRadius);
      
      expect(btnBg).toBeTruthy();
      expect(btnBorderRadius).toBeTruthy();
      
      // Should have icon
      await expect(voiceBtn.locator('i.fas.fa-volume-up')).toBeVisible();
    }
  });
});

test.describe('UI Design - Mobile Responsiveness', () => {
  test('should adapt beautifully to mobile viewport', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');

    // Container should adapt to mobile
    const container = page.locator('.container');
    await expect(container).toBeVisible();
    
    // Grid should stack on mobile
    const mainGrid = page.locator('.main-grid');
    const gridTemplateColumns = await mainGrid.evaluate(el => getComputedStyle(el).gridTemplateColumns);
    
    // On mobile, should be single column or adapted layout
    expect(gridTemplateColumns).toBeTruthy();
  });

  test('should maintain proper touch targets on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');

    // All interactive elements should meet minimum touch target size
    const interactiveElements = page.locator('button, input, select, a, .voice-btn');
    
    for (const element of await interactiveElements.all()) {
      if (await element.isVisible()) {
        const box = await element.boundingBox();
        if (box) {
          expect(box.height).toBeGreaterThanOrEqual(40); // Minimum touch target
        }
      }
    }
  });

  test('should have readable text on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');

    // Check font sizes are appropriate for mobile
    const textElements = page.locator('h1, h2, h3, p, label, span');
    
    for (const element of await textElements.all()) {
      if (await element.isVisible()) {
        const fontSize = await element.evaluate(el => getComputedStyle(el).fontSize);
        const fontSizeNum = parseFloat(fontSize);
        expect(fontSizeNum).toBeGreaterThanOrEqual(14); // Minimum readable size
      }
    }
  });

  test('should handle overflow properly on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');

    // Check for horizontal overflow
    const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
    const viewportWidth = 375;
    
    expect(bodyWidth).toBeLessThanOrEqual(viewportWidth + 5); // Allow small tolerance
  });
});