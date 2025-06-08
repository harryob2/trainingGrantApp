const { expect } = require("@playwright/test");

// Base URL for the application - define once and export
const BASE_URL = "http://127.0.0.1:5000";

// Admin user credentials - used for all tests
const ADMIN_EMAIL = "harry@test.com";
const ADMIN_PASSWORD = "cork4liam";

/**
 * Common utilities for e2e tests to reduce code duplication and
 * standardize test patterns
 */

/**
 * Login as the admin user
 * @param {import('@playwright/test').Page} page - Playwright page
 */
async function loginAsAdmin(page) {
  console.log("--- Logging in as admin user ---");

  // Navigate to home (will redirect to login)
  await page.goto(BASE_URL + "/new");

  // Check if already logged in
  const currentUrl = page.url();
  if (!currentUrl.includes("/login")) {
    console.log("--- Already logged in, skipping login ---");
    return;
  }

  // Fill login form
  await page.locator('input[name="username"]').fill(ADMIN_EMAIL);
  await page.locator('input[name="password"]').fill(ADMIN_PASSWORD);

  // Submit login form
  await page.locator('input[type="submit"]').click();

  // Wait for redirect after login
  await page.waitForURL("**/");

  // Verify we are logged in by checking we're not on the login page anymore
  await expect(page).not.toHaveURL(/.*\/login/);

  console.log("--- Successfully logged in as admin ---");
}

/**
 * Go to the application's home page and ensure we're logged in
 * @param {import('@playwright/test').Page} page - Playwright page
 */
async function gotoHome(page) {
  await page.goto(BASE_URL + "/new");

  // Check if we need to login
  if (page.url().includes("/login")) {
    await loginAsAdmin(page);
  }
}

/**
 * Click the "Add Training Manually" button to show the form details
 * @param {import('@playwright/test').Page} page - Playwright page
 */
async function clickAddTrainingManually(page) {
  console.log("--- Clicking Add Training Manually button ---");
  
  const addManuallyBtn = page.locator("#add-manually-btn");
  await expect(addManuallyBtn).toBeVisible();
  await addManuallyBtn.click();
  
  // Wait for the form details to become visible
  await expect(page.locator("#training-form-details")).toBeVisible();
  
  console.log("--- Form details now visible ---");
}

/**
 * Add a trainee to the form by searching and selecting the first match
 * @param {import('@playwright/test').Page} page - Playwright page
 * @param {string} searchTerm - Search term for trainee (default 'gre')
 * @param {Object} options - Optional parameters
 */
async function addTrainee(page, searchTerm = "gre", options = {}) {
  const defaults = {
    timeout: 10000, // 10 second timeout by default
    retries: 2 // Number of retries if search fails
  };

  const settings = { ...defaults, ...options };

  // Fill the search input
  await page.locator("input#trainee-search-input").fill(searchTerm);

  // Try to find and click the first search result with retry logic
  let attempt = 0;

  while (attempt <= settings.retries) {
    try {
      // Wait for suggestions to appear and click the first one
      await page
        .locator("div#trainee-search-results div.autocomplete-item:first-child")
        .waitFor({ state: "visible", timeout: settings.timeout });

      await page
        .locator("div#trainee-search-results div.autocomplete-item:first-child")
        .click();

      // Success! Return early
      return;
    } catch (error) {
      attempt++;
      console.log(
        `Attempt ${attempt} failed for trainee search '${searchTerm}'. ${settings.retries - attempt + 1} retries left.`
      );

      if (attempt > settings.retries) {
        throw error; // All retries failed, rethrow the error
      }

      // Clear and refill the search input for next attempt
      await page.locator("input#trainee-search-input").fill("");
      await page.waitForTimeout(500); // Small delay before trying again
      await page.locator("input#trainee-search-input").fill(searchTerm);
    }
  }
}

/**
 * Set a trainer name in both visible search field and hidden field
 * @param {import('@playwright/test').Page} page - Playwright page
 * @param {string} trainerName - Name of the trainer to set
 */
async function setTrainerName(page, trainerName) {
  await page.locator("input#trainer_name_search").fill(trainerName);

  // Also set the hidden field that stores the actual value
  await page.evaluate((name) => {
    const hiddenInput = document.getElementById("trainer_name_hidden");
    if (hiddenInput) {
      hiddenInput.value = name;
    }
  }, trainerName);

  // Wait for the dropdown to potentially appear and then dismiss it by clicking elsewhere
  await page.waitForTimeout(500);
  
  // Click somewhere else to dismiss any open dropdowns
  await page.locator("h3").first().click();
  
  // Wait for UI to stabilize
  await page.waitForTimeout(300);
}

/**
 * Fill the basic required fields for an internal training submission
 * @param {import('@playwright/test').Page} page - Playwright page
 * @param {Object} options - Optional parameters to customize the form
 */
async function fillBasicInternalTrainingForm(page, options = {}) {
  const defaults = {
    trainingName: "Test Training Course",
    trainerName: "Test Trainer",
    trainerHours: "1",
    traineeHours: "1",
    startDate: "2024-01-01",
    endDate: "2024-01-01",
    description: "Test training description",
    idaClass: "Class A - QQI Certified L1-10",
    includeTrainer: true,
    includeTrainee: true,
    locationType: "Onsite", // Allow setting location type
    locationDetails: null, // Optional location details for Offsite
    skipBaseSetup: false // Allow skipping basic setup
  };

  const settings = { ...defaults, ...options };

  // First, show the form by clicking "Add Training Manually"
  await clickAddTrainingManually(page);

  // Set training name
  await page.locator('input[name="training_name"]').fill(settings.trainingName);

  // Select training type and location
  await page
    .locator(".training-type-card")
    .filter({ hasText: "Internal Training" })
    .click();

  // Set location if not skipping basic setup
  if (!settings.skipBaseSetup) {
    await page
      .locator("label")
      .filter({ hasText: settings.locationType })
      .click({ force: true });

    // Fill location details if Offsite
    if (settings.locationType === "Offsite") {
      await expect(page.locator("#location-details-container")).toBeVisible();
      if (settings.locationDetails) {
        await page
          .locator('input[name="location_details"]')
          .fill(settings.locationDetails);
      }
    }
  }

  // Set trainer info if included
  if (settings.includeTrainer) {
    await setTrainerName(page, settings.trainerName);
  }

  // Set training hours (always required)
  await page
    .locator('input[name="training_hours"]')
    .fill(settings.trainerHours);

  // Set IDA class (always required)
  await page.locator('select[name="ida_class"]').selectOption(settings.idaClass);

  // Set dates
  await page.locator('input[name="start_date"]').fill(settings.startDate);
  await page.locator('input[name="end_date"]').fill(settings.endDate);

  // Set description
  await page
    .locator('textarea[name="training_description"]')
    .fill(settings.description);

  // Add trainee if included
  if (settings.includeTrainee) {
    await addTrainee(page);
  }
}

/**
 * Fill an external training form with basic required fields
 * @param {import('@playwright/test').Page} page - Playwright page
 * @param {Object} options - Optional parameters to customize the form
 */
async function fillBasicExternalTrainingForm(page, options = {}) {
  const defaults = {
    trainingName: "External Test Training Course",
    supplierName: "External Test Supplier",
    courseCost: "1000.00",
    invoiceNumber: "INV-2024-001",
    concurClaim: "CONCUR-2024-001",
    traineeHours: "1",
    startDate: "2024-07-01",
    endDate: "2024-07-01",
    description: "External training description",
    idaClass: "Class B - Nat/International Industry Cert",
    includeTrainee: true
  };

  const settings = { ...defaults, ...options };

  // First, show the form by clicking "Add Training Manually"
  await clickAddTrainingManually(page);

  // Set training name
  await page.locator('input[name="training_name"]').fill(settings.trainingName);

  // Select external training type
  await page
    .locator(".training-type-card")
    .filter({ hasText: "External Training" })
    .click();
  await expect(page.locator("#external-supplier-container")).toBeVisible();

  // Wait for the external training specific containers to become visible
  await expect(page.locator("#course-cost-container")).toBeVisible();
  await expect(page.locator("#invoice-number-container")).toBeVisible();

  // Set supplier
  await page.locator('input[name="supplier_name"]').fill(settings.supplierName);

  // Set location (default: Onsite)
  await page.locator("label").filter({ hasText: "Onsite" }).click({ force: true });

  // Set training hours (always required)
  await page.locator('input[name="training_hours"]').fill(settings.traineeHours);

  // Fill external training specific fields (they should now be visible)
  await page.locator('input[name="course_cost"]').clear();
  await page.locator('input[name="course_cost"]').fill(settings.courseCost);

  await page.locator('input[name="invoice_number"]').clear();
  await page.locator('input[name="invoice_number"]').fill(settings.invoiceNumber);

  await page.locator('input[name="concur_claim"]').clear();
  await page.locator('input[name="concur_claim"]').fill(settings.concurClaim);

  // Set IDA class (always required)
  await page.locator('select[name="ida_class"]').selectOption(settings.idaClass);

  // Set dates
  await page.locator('input[name="start_date"]').fill(settings.startDate);
  await page.locator('input[name="end_date"]').fill(settings.endDate);

  // Set description
  await page
    .locator('textarea[name="training_description"]')
    .fill(settings.description);

  // Add trainee if included
  if (settings.includeTrainee) {
    await addTrainee(page);
  }
}

/**
 * Submit the form
 * @param {import('@playwright/test').Page} page - Playwright page
 */
async function submitForm(page) {
  await page.locator("#submit-training-form-btn").click();
}

/**
 * Verify the form submission was successful
 * @param {import('@playwright/test').Page} page - Playwright page
 */
async function expectSuccessfulSubmission(page) {
  try {
    await page.waitForURL("**/success", { timeout: 10000 });
    await expect(page).toHaveURL(BASE_URL + "/success");
  } catch (error) {
    // If we didn't get to success page, let's see what happened
    const currentUrl = page.url();
    console.log(`Expected success page but got: ${currentUrl}`);
    
    // Check for validation errors or other issues on the page
    const pageContent = await page.textContent('body');
    if (pageContent.includes('required') || pageContent.includes('error') || pageContent.includes('invalid')) {
      console.log('Page content suggests validation errors');
      
      // Look for visible error messages
      const errorElements = await page.locator('.text-danger, .alert-danger, .is-invalid').all();
      for (let i = 0; i < errorElements.length; i++) {
        const errorText = await errorElements[i].textContent();
        if (errorText && errorText.trim()) {
          console.log(`Error ${i + 1}: ${errorText.trim()}`);
        }
      }
    }
    
    // Re-throw the original error
    throw error;
  }
}

/**
 * Verify the form update was successful
 * @param {import('@playwright/test').Page} page - Playwright page
 */
async function expectSuccessfulUpdate(page) {
  // Wait for the success flash message to appear
  const successFlash = page.locator(".alert-success");
  await expect(successFlash).toBeVisible();

  // Verify the success message contains the expected text
  const successMessage = await successFlash.textContent();
  expect(successMessage).toContain("updated successfully");
}

/**
 * Verify a validation error for the specified field
 * @param {import('@playwright/test').Page} page - Playwright page
 * @param {string} selector - Selector for the field with error
 * @param {string} expectedMessage - Expected validation message
 */
async function expectValidationError(page, selector, expectedMessage) {
  // First, verify we're still on the form page (not redirected to success)
  await expect(page).not.toHaveURL(BASE_URL + "/success");

  // Check for server-side validation messages in the page content
  // Look for flash messages, error containers, or general page content
  const pageContent = await page.textContent('body');
  
  // First try to find the error in common error containers
  const errorContainers = [
    '.alert-danger',
    '.alert-error', 
    '.text-danger',
    '.invalid-feedback',
    '.error-message',
    '.flash-error'
  ];
  
  let foundError = false;
  
  for (const container of errorContainers) {
    try {
      const errorElement = page.locator(container);
      if (await errorElement.isVisible()) {
        const errorText = await errorElement.textContent();
        if (errorText && errorText.includes(expectedMessage)) {
          foundError = true;
          break;
        }
      }
    } catch {
      // Continue to next container
    }
  }
  
  // If not found in containers, check if it's in the general page content
  if (!foundError) {
    expect(pageContent).toContain(expectedMessage);
  }
}

module.exports = {
  BASE_URL,
  loginAsAdmin,
  gotoHome,
  clickAddTrainingManually,
  addTrainee,
  setTrainerName,
  fillBasicInternalTrainingForm,
  fillBasicExternalTrainingForm,
  submitForm,
  expectSuccessfulSubmission,
  expectValidationError,
  expectSuccessfulUpdate
};
