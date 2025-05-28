/**
 * Form validation logic for the training form.
 * 
 * This module handles client-side validation for the training form,
 * including dynamic field requirements based on training type.
 */

/**
 * Validates that the end date is not before the start date.
 * Sets custom validity message on the endDateInput if invalid.
 * @param {HTMLInputElement} startDateInput - The start date input element.
 * @param {HTMLInputElement} endDateInput - The end date input element.
 */
function validateDates(startDateInput, endDateInput) {
  if (
    !startDateInput ||
    !endDateInput ||
    !startDateInput.value ||
    !endDateInput.value
  ) {
     endDateInput?.setCustomValidity(""); // Clear previous error if inputs cleared
    return; // Not enough info to validate or fields empty (let 'required' handle empty)
  }

  const startDate = new Date(startDateInput.value);
  const endDate = new Date(endDateInput.value);

  // Basic check if dates are valid objects
  if (isNaN(startDate.getTime()) || isNaN(endDate.getTime())) {
     endDateInput.setCustomValidity(""); // Clear validity if format is wrong (let type=date handle)
    return;
  }

  if (endDate < startDate) {
    endDateInput.setCustomValidity(
      "End date cannot be earlier than start date.",
    );
  } else {
    endDateInput.setCustomValidity(""); // Clear custom validity if valid
  }
}

/**
 * Validates that the file size is within the allowed limit (16MB).
 * This seems related to an invoice form, not the main training form?
 * Kept for now, but might be unused in the current context.
 * @returns {boolean} - True if file size is valid or no file, false otherwise
 */
function validateFileSize() {
  const fileInput = document.getElementById("invoice_attachment");

  if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
    return true; // No file selected, validation passes
  }

  const maxSize = 16 * 1024 * 1024; // 16MB in bytes
  const fileSize = fileInput.files[0].size;

  if (fileSize > maxSize) {
    alert("File size exceeds the maximum allowed size of 16MB.");
    fileInput.value = ""; // Clear the input
    return false;
  }

  return true;
}

// Helper function to check if an element is really visible
function isReallyVisible(element) {
    if (!element) return false;
    const style = window.getComputedStyle(element);
    return style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0';
}

// Helper function to parse currency values
function parseCurrency(val) {
    if (!val) return 0;
    return parseFloat(val.replace(/[^0-9.-]+/g, ""));
}

// --- Validation Helper Functions ---

/**
 * Check if a field should be required based on training type
 */
function isFieldRequired(fieldName, trainingType) {
    const internalRequiredFields = ['trainer_name'];
    const externalRequiredFields = ['supplier_name', 'course_cost'];
    const alwaysRequiredFields = ['training_hours'];
    
    if (alwaysRequiredFields.includes(fieldName)) {
        return true;
    }
    
    if (trainingType === 'Internal Training') {
        return internalRequiredFields.includes(fieldName);
    } else if (trainingType === 'External Training') {
        return externalRequiredFields.includes(fieldName);
    }
    return false;
}

/**
 * Validate email format
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email.trim());
}

/**
 * Check if trainees have been added
 */
function hasTrainees() {
    const traineesData = document.getElementById('trainees_data');
    if (!traineesData || !traineesData.value) return false;
    
    try {
        const trainees = JSON.parse(traineesData.value);
        return Array.isArray(trainees) && trainees.length > 0;
    } catch (e) {
        return false;
    }
}

/**
 * Check if any expense fields have values
 */
function hasExpenses() {
    const expenseFields = ['travel_cost', 'food_cost', 'materials_cost', 'other_cost'];
    return expenseFields.some(fieldId => {
        const field = document.getElementById(fieldId);
        if (!field) return false;
        const value = parseCurrency(field.value);
        return !isNaN(value) && value > 0;
    });
}

// --- Main Validation Driver Logic ---
document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("training-form");
    const submitButton = document.getElementById("submit-training-form-btn");

    if (!form || !submitButton) {
        console.error("Form or Submit Button not found for validation initialization.");
        return;
    }

    // Helper function to display validation messages
    function showValidationMessage(element, message) {
        const container = element.closest('.form-group, .mb-3, .trainee-search-box, #training-type-card-group');
        const targetElement = container || element;

        // Remove existing message within the container first
        const existingMsg = targetElement.parentNode?.querySelector('.validation-message[data-target="' + (element.id || element.name) + '"]');
        if (existingMsg) {
            existingMsg.remove();
        }

        const messageElement = document.createElement("div");
        messageElement.className = "validation-message alert alert-danger mt-2";
        messageElement.style.cssText = "padding: 0.5rem; font-size: 0.9rem;";
        messageElement.textContent = message;
        messageElement.setAttribute('data-target', (element.id || element.name)); // Link message to field

        try {
             if (targetElement.parentNode) {
                 if (targetElement.nextSibling) {
                    targetElement.parentNode.insertBefore(messageElement, targetElement.nextSibling);
                 } else {
                    targetElement.parentNode.appendChild(messageElement);
                 }
            } else {
                 console.error("Could not find parent node to insert validation message for:", element);
            }
        } catch (e) {
            console.error(`Error inserting validation message for element:`, element, e);
        }
        return messageElement;
    }

    // Main validation logic
    submitButton.addEventListener("click", function (event) {
        // Clear previous validation messages
        document.querySelectorAll('.validation-message').forEach(msg => msg.remove());
        
        let isValid = true;
        let firstInvalidElement = null;

        // Get form elements
        const trainingType = document.querySelector('input[name="training_type"]:checked');
        const trainerName = document.getElementById("trainer_name_search");
        const supplierName = document.getElementById("supplier_name");
        const trainingHours = document.getElementById("training_hours");
        const courseCost = document.getElementById("course_cost");
        const concurClaim = document.getElementById("concur_claim");
        const otherCost = document.getElementById("other_cost");
        const otherDesc = document.getElementById("other_expense_description");

        // Validate training type selection
        if (!trainingType) {
            const trainingTypeContainer = document.getElementById("training-type-card-group");
            if (trainingTypeContainer) {
                showValidationMessage(trainingTypeContainer, "Please select a training type.");
                if (!firstInvalidElement) firstInvalidElement = trainingTypeContainer;
            }
            isValid = false;
        }

        // Validate trainees
        if (!hasTrainees()) {
            const traineesContainer = document.getElementById("trainee-search-input");
            if (traineesContainer) {
                showValidationMessage(traineesContainer, "At least one trainee must be added.");
                if (!firstInvalidElement) firstInvalidElement = traineesContainer;
            }
            isValid = false;
        }

        // Always validate training hours (now required for all training types)
        if (!trainingHours || !trainingHours.value || parseFloat(trainingHours.value) <= 0) {
            if (trainingHours) {
                showValidationMessage(trainingHours, "Training Hours is required and must be greater than 0.");
                if (!firstInvalidElement) firstInvalidElement = trainingHours;
            }
            isValid = false;
        }

        // Dynamic validation based on training type
        if (trainingType) {
            const typeValue = trainingType.value;

            // Internal Training validations
            if (typeValue === "Internal Training") {
                if (!trainerName || !trainerName.value.trim()) {
                    if (trainerName) {
                        showValidationMessage(trainerName, "Trainer Name is required for internal training.");
                        if (!firstInvalidElement) firstInvalidElement = trainerName;
                    }
                    isValid = false;
                }
            }

            // External Training validations
            if (typeValue === "External Training") {
                if (!supplierName || !supplierName.value.trim()) {
                    if (supplierName) {
                        showValidationMessage(supplierName, "Supplier Name is required for external training.");
                        if (!firstInvalidElement) firstInvalidElement = supplierName;
                    }
                    isValid = false;
                }

                if (!courseCost || !courseCost.value || parseCurrency(courseCost.value) < 0) {
                    if (courseCost) {
                        showValidationMessage(courseCost, "Course Cost is required for external training and cannot be negative.");
                        if (!firstInvalidElement) firstInvalidElement = courseCost;
                    }
                    isValid = false;
                }
            }
        }

        // Expense validations
        if (hasExpenses() && (!concurClaim || !concurClaim.value.trim())) {
            if (concurClaim) {
                showValidationMessage(concurClaim, "Concur Claim Number is required when expenses are entered.");
                if (!firstInvalidElement) firstInvalidElement = concurClaim;
            }
            isValid = false;
        }

        // Other expense description validation
        if (otherCost && otherDesc) {
            const otherCostVal = parseCurrency(otherCost.value);
            if (!isNaN(otherCostVal) && otherCostVal > 0 && !otherDesc.value.trim()) {
                showValidationMessage(otherDesc, "Description is required when other expenses are entered.");
                if (!firstInvalidElement) firstInvalidElement = otherDesc;
                isValid = false;
            }
        }

        // If validation failed, prevent submission and focus first invalid element
        if (!isValid) {
            event.preventDefault();
            if (firstInvalidElement) {
                firstInvalidElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
                if (firstInvalidElement.focus) {
                    setTimeout(() => firstInvalidElement.focus(), 100);
                }
            }
            return false;
        }

        return true;
    });

    console.log("Form validation initialized.");
});
