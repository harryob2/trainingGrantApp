/**
 * Other Expense and Concur Claim Logic
 * Handles visibility of other expense description field and concur claim requirements
 */

document.addEventListener("DOMContentLoaded", function () {
  // Get references to the relevant elements
  const otherCostField = document.getElementById("other_cost");
  const otherDescriptionDiv = document.getElementById("other-expense-description");
  const concurClaimInput = document.getElementById("concur_claim");
  const concurRequiredMessageDiv = document.getElementById("concur-required-message");

  // Get all expense input fields for concur logic
  const expenseInputs = [
    document.getElementById("travel_cost"),
    document.getElementById("food_cost"),
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

  // --- Concur Claim Required Message Logic ---
  function updateConcurMessageVisibility() {
      let hasAnyExpense = false;
      expenseInputs.forEach((input) => {
          const value = parseCurrency(input.value);
          if (!isNaN(value) && value > 0) {
              hasAnyExpense = true;
          }
      });

      // Check if concur claim number is filled
      const hasConcurClaim = concurClaimInput && concurClaimInput.value.trim() !== "";

      if (concurRequiredMessageDiv) { // Check if element exists
          // Show message only if there are expenses AND no concur claim number
          concurRequiredMessageDiv.classList.toggle("d-none", !hasAnyExpense || hasConcurClaim);
      }
  }

  // Add event listeners to the Other Expenses field to check visibility
  if (otherCostField) {
    otherCostField.addEventListener("input", checkOtherExpensesVisibility);
    otherCostField.addEventListener("change", checkOtherExpensesVisibility);
  }

  // Add Concur Logic Listeners
  expenseInputs.forEach((input) => {
      input.addEventListener("input", updateConcurMessageVisibility);
  });
  
  // Add listener to concur claim input to hide message when filled
  if (concurClaimInput) {
      concurClaimInput.addEventListener("input", updateConcurMessageVisibility);
  }

  // Initial check when the page loads
  checkOtherExpensesVisibility();
  updateConcurMessageVisibility(); // Also run Concur check on load

  console.log("Other Expense and Concur Message Logic Initialized.");
});
