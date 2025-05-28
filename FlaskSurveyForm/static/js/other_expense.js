/**
 * Other Expense and Concur Claim Logic
 * Handles visibility of other expense description field and concur claim requirements
 */

document.addEventListener("DOMContentLoaded", function () {
  // Get references to the relevant elements
  const otherCostField = document.getElementById("other_cost");
  const otherDescriptionDiv = document.getElementById("other-expense-description-container");
  const otherDescriptionField = document.getElementById("other_expense_description");
  const otherDescriptionWarning = document.querySelector(".other-expense-required-text");
  const concurClaimInput = document.getElementById("concur_claim");
  const concurRequiredMessageDiv = document.getElementById("concur-required-message");

  // Expense inputs
  const expenseInputs = [
    document.getElementById("materials_cost"),
    document.getElementById("other_cost"),
  ].filter(Boolean); // Remove null elements

  if (!otherCostField || !otherDescriptionDiv) {
    console.warn("Other expense elements not found. Skipping other expense logic.");
    return;
  }

  // --- Other Expense Description Visibility Logic ---
  function checkOtherExpensesVisibility() {
    const isVisible =
      otherCostField.value && parseCurrency(otherCostField.value) > 0;
    otherDescriptionDiv.classList.toggle("d-none", !isVisible);
  }

  // --- Other Expense Description Warning Logic ---
  function updateOtherExpenseWarningVisibility() {
    if (otherDescriptionWarning && otherDescriptionField) {
      const otherCostVal = parseCurrency(otherCostField.value);
      const hasOtherCost = !isNaN(otherCostVal) && otherCostVal > 0;
      const hasDescription = otherDescriptionField.value.trim() !== "";
      
      // Show warning only if there's an other cost but no description
      const shouldShowWarning = hasOtherCost && !hasDescription;
      otherDescriptionWarning.classList.toggle("d-none", !shouldShowWarning);
    }
  }

  // --- Concur Claim Required Message Logic ---
  function updateConcurMessageVisibility() {
      let hasAnyExpense = false;
      
      // Check materials and other costs
      expenseInputs.forEach((input) => {
          const value = parseCurrency(input.value);
          if (!isNaN(value) && value > 0) {
              hasAnyExpense = true;
          }
      });

      // Check for travel expenses
      if (window.travelExpensesManager && window.travelExpensesManager.travelExpenses) {
          if (window.travelExpensesManager.travelExpenses.length > 0) {
              hasAnyExpense = true;
          }
      }

      // Check if it's external training (always requires Concur claim)
      const trainingTypeRadio = document.querySelector('input[name="training_type"]:checked');
      const isExternalTraining = trainingTypeRadio && trainingTypeRadio.value === "External Training";

      // Check if concur claim number is filled
      const hasConcurClaim = concurClaimInput && concurClaimInput.value.trim() !== "";

      if (concurRequiredMessageDiv) { // Check if element exists
          // Show message if:
          // 1. There are expenses AND no concur claim number, OR
          // 2. It's external training AND no concur claim number
          const shouldShowMessage = (hasAnyExpense || isExternalTraining) && !hasConcurClaim;
          concurRequiredMessageDiv.classList.toggle("d-none", !shouldShowMessage);
      }
  }

  // Add event listeners to the Other Expenses field to check visibility
  if (otherCostField) {
    otherCostField.addEventListener("input", checkOtherExpensesVisibility);
    otherCostField.addEventListener("change", checkOtherExpensesVisibility);
    // Also update concur message when other cost changes
    otherCostField.addEventListener("input", updateConcurMessageVisibility);
    // Update other expense warning when other cost changes
    otherCostField.addEventListener("input", updateOtherExpenseWarningVisibility);
  }

  // Add event listener to other expense description field
  if (otherDescriptionField) {
    otherDescriptionField.addEventListener("input", updateOtherExpenseWarningVisibility);
  }

  // Add Concur Logic Listeners
  expenseInputs.forEach((input) => {
      input.addEventListener("input", updateConcurMessageVisibility);
  });
  
  // Add listener to concur claim input to hide message when filled
  if (concurClaimInput) {
      concurClaimInput.addEventListener("input", updateConcurMessageVisibility);
  }

  // Listen for training type changes
  const trainingTypeRadios = document.querySelectorAll('input[name="training_type"]');
  trainingTypeRadios.forEach(radio => {
      radio.addEventListener("change", updateConcurMessageVisibility);
  });

  // Listen for travel expenses updates
  document.addEventListener('travelExpensesUpdated', updateConcurMessageVisibility);

  // Initial check when the page loads
  checkOtherExpensesVisibility();
  updateOtherExpenseWarningVisibility();
  updateConcurMessageVisibility(); // Also run Concur check on load

  console.log("Other Expense and Concur Message Logic Initialized.");

  // Make the updateConcurMessageVisibility function globally available
  window.checkOtherExpenses = updateConcurMessageVisibility;
});
