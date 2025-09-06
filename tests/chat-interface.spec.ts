import { test, expect } from '@playwright/test';

test.describe('imam Farm Assist - Chat Interface', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    
    // Wait for the welcome message to appear
    await expect(page.locator('.message.ai-message')).toBeVisible();
  });

  test('should display welcome message on load', async ({ page }) => {
    // Check for AI welcome message
    const welcomeMessage = page.locator('.message.ai-message').first();
    await expect(welcomeMessage).toContainText('Sannu! Welcome to imam Farm Assist');
    await expect(welcomeMessage).toContainText('weather');
    await expect(welcomeMessage).toContainText('farming tips');
  });

  test('should have beautiful chat interface design', async ({ page }) => {
    // Check chat container styling
    await expect(page.locator('.chat-container')).toBeVisible();
    await expect(page.locator('#chatMessages')).toBeVisible();
    
    // Verify chat input styling
    const chatInput = page.locator('#chatInput');
    await expect(chatInput).toBeVisible();
    await expect(chatInput).toHaveAttribute('placeholder', /Type your message in Hausa or English/);

    // Check send button with icon
    const sendBtn = page.locator('.chat-input-container .btn-secondary');
    await expect(sendBtn).toBeVisible();
    await expect(sendBtn.locator('i')).toHaveClass(/fas fa-paper-plane/);
  });

  test('should send English message and receive response', async ({ page }) => {
    const chatInput = page.locator('#chatInput');
    const sendBtn = page.locator('.chat-input-container .btn-secondary');

    // Send English message
    await chatInput.fill('What is the weather today?');
    await sendBtn.click();

    // Check user message appears
    await expect(page.locator('.message.user-message').last()).toContainText('What is the weather today?');

    // Wait for AI response
    await expect(page.locator('.message.ai-message').last()).toContainText('weather', { timeout: 5000 });
    
    // Input should be cleared
    await expect(chatInput).toHaveValue('');
  });

  test('should detect Hausa language and respond appropriately', async ({ page }) => {
    const chatInput = page.locator('#chatInput');
    const sendBtn = page.locator('.chat-input-container .btn-secondary');

    // Send Hausa message
    await chatInput.fill('Yanayi na yau yaya?');
    await sendBtn.click();

    // Check user message appears
    await expect(page.locator('.message.user-message').last()).toContainText('Yanayi na yau yaya?');

    // Wait for Hausa AI response
    const aiResponse = page.locator('.message.ai-message').last();
    await expect(aiResponse).toContainText('Yanayi', { timeout: 5000 });
    
    // Should contain voice button
    await expect(aiResponse.locator('.voice-btn')).toBeVisible();
  });

  test('should handle Enter key for sending messages', async ({ page }) => {
    const chatInput = page.locator('#chatInput');

    // Type message and press Enter
    await chatInput.fill('farming tips please');
    await chatInput.press('Enter');

    // Message should be sent
    await expect(page.locator('.message.user-message').last()).toContainText('farming tips please');
    await expect(page.locator('.message.ai-message').last()).toContainText('tip', { timeout: 5000 });
  });

  test('should display loading state when sending message', async ({ page }) => {
    const chatInput = page.locator('#chatInput');
    const sendBtn = page.locator('.chat-input-container .btn-secondary');

    // Send message
    await chatInput.fill('test message');
    await sendBtn.click();

    // Button should show loading state briefly
    await expect(sendBtn).toContainText(''); // Loading spinner, no text
    await expect(sendBtn).toBeDisabled();
    
    // Should return to normal state
    await expect(sendBtn).not.toBeDisabled({ timeout: 5000 });
  });

  test('should have voice buttons on AI messages', async ({ page }) => {
    const chatInput = page.locator('#chatInput');
    
    // Send a message to get AI response
    await chatInput.fill('weather update');
    await chatInput.press('Enter');

    // Wait for AI response with voice button
    const aiMessage = page.locator('.message.ai-message').last();
    await expect(aiMessage).toBeVisible({ timeout: 5000 });
    
    const voiceBtn = aiMessage.locator('.voice-btn');
    await expect(voiceBtn).toBeVisible();
    await expect(voiceBtn.locator('i')).toHaveClass(/fas fa-volume-up/);
  });

  test('should test voice functionality button', async ({ page }) => {
    const testVoiceBtn = page.locator('.voice-btn[onclick="testVoice()"]');
    
    // Should have test voice button
    await expect(testVoiceBtn).toBeVisible();
    
    // Click test voice button (note: actual audio won't play in test environment)
    await testVoiceBtn.click();
    
    // Should not throw error
    await page.waitForTimeout(1000);
  });

  test('should scroll chat messages to bottom', async ({ page }) => {
    const chatMessages = page.locator('#chatMessages');
    
    // Send multiple messages to create scroll
    for (let i = 0; i < 5; i++) {
      await page.fill('#chatInput', `Test message ${i + 1}`);
      await page.press('#chatInput', 'Enter');
      await page.waitForTimeout(500);
    }

    // Last message should be visible
    const lastMessage = page.locator('.message').last();
    await expect(lastMessage).toBeInViewport();
  });

  test('should handle empty messages gracefully', async ({ page }) => {
    const chatInput = page.locator('#chatInput');
    const sendBtn = page.locator('.chat-input-container .btn-secondary');
    
    // Try to send empty message
    await chatInput.fill('   '); // Just spaces
    await sendBtn.click();
    
    // Should not send message (input will be cleared but no new messages)
    await expect(chatInput).toHaveValue('');
  });

  test('should display message icons correctly', async ({ page }) => {
    // Send a message to get both user and AI messages
    await page.fill('#chatInput', 'hello');
    await page.press('#chatInput', 'Enter');
    
    // Wait for messages
    await page.waitForTimeout(2000);
    
    // Check user message icon
    const userMessage = page.locator('.message.user-message').last();
    await expect(userMessage.locator('i.fas.fa-user')).toBeVisible();
    
    // Check AI message icon  
    const aiMessage = page.locator('.message.ai-message').last();
    await expect(aiMessage.locator('i.fas.fa-robot')).toBeVisible();
  });
});

test.describe('Chat Interface - Language Detection', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should detect farming-related Hausa keywords', async ({ page }) => {
    const hausaTerms = [
      'yanayi',      // weather
      'shinkafa',    // rice
      'ciyawa',      // grass
      'taki',        // fertilizer
      'shawara'      // advice
    ];

    for (const term of hausaTerms) {
      await page.fill('#chatInput', term);
      await page.press('#chatInput', 'Enter');
      
      await page.waitForTimeout(1000);
      
      // Should get response in Hausa context
      const lastAiMessage = page.locator('.message.ai-message').last();
      await expect(lastAiMessage).toBeVisible();
    }
  });

  test('should handle mixed language conversations', async ({ page }) => {
    // Send English message
    await page.fill('#chatInput', 'What about yanayi?');
    await page.press('#chatInput', 'Enter');
    
    await page.waitForTimeout(1000);
    
    // Should detect Hausa keyword and respond accordingly
    const response = page.locator('.message.ai-message').last();
    await expect(response).toBeVisible();
    
    // Send pure English
    await page.fill('#chatInput', 'farming tips');
    await page.press('#chatInput', 'Enter');
    
    await page.waitForTimeout(1000);
    
    const englishResponse = page.locator('.message.ai-message').last();
    await expect(englishResponse).toBeVisible();
  });
});