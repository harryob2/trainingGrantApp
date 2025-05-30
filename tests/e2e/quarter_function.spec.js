const { test, expect } = require("@playwright/test");
const { loginAsAdmin } = require("./utils/test-utils");

test.describe("Quarter Function Tests", () => {
  test("export claim5 options should return correct quarters", async ({ page }) => {
    await loginAsAdmin(page);

    // Navigate to the list page to access export functionality
    await page.goto("http://127.0.0.1:5000/list");

    // Make API call to get export options
    const response = await page.request.get("http://127.0.0.1:5000/api/export_claim5_options");
    expect(response.ok()).toBeTruthy();

    const data = await response.json();
    
    // Verify the response structure
    expect(data).toHaveProperty("quarters");
    expect(data).toHaveProperty("min_date");
    expect(data).toHaveProperty("max_date");
    
    // Verify quarters are in correct format (Q1 2024, Q2 2024, etc.)
    if (data.quarters && data.quarters.length > 0) {
      for (const quarter of data.quarters) {
        expect(quarter).toMatch(/^Q[1-4] \d{4}$/);
      }
    }
  });

  test("export claim5 with quarter filtering should work", async ({ page }) => {
    await loginAsAdmin(page);

    // Navigate to list page
    await page.goto("http://127.0.0.1:5000/list");

    // First get available quarters
    const optionsResponse = await page.request.get("http://127.0.0.1:5000/api/export_claim5_options");
    const optionsData = await optionsResponse.json();

    if (optionsData.quarters && optionsData.quarters.length > 0) {
      // Test export with quarter filtering
      const exportResponse = await page.request.post("http://127.0.0.1:5000/export_claim5", {
        data: {
          quarters: [optionsData.quarters[0]], // Use first available quarter
          start_date: null,
          end_date: null
        }
      });

      // Should return Excel file or redirect (both are valid responses)
      expect([200, 302]).toContain(exportResponse.status());
    }
  });
}); 