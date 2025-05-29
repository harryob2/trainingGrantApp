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
    const expenseFields = ['course_cost'];
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

    // Unified validation message system
    const ValidationManager = {
        // Show a validation message for a field
        showMessage: function(element, message) {
            const fieldId = element.id || element.name;
            
            // Special handling for expense fields that have dedicated validation message containers
            let targetElement;
            if (fieldId === 'course_cost') {
                targetElement = document.getElementById('course-cost-validation');
            } else if (fieldId === 'invoice_number') {
                targetElement = document.getElementById('invoice-number-validation');
            } else if (fieldId === 'concur_claim') {
                targetElement = document.getElementById('concur-claim-validation');
            }
            
            // Fall back to default behavior for other fields
            if (!targetElement) {
                const container = element.closest('.form-group, .mb-3, .trainee-search-box, #training-type-card-group, .col-md-12');
                targetElement = container || element;
            }

            // Remove any existing validation messages for this field
            this.clearMessage(element);

            // Add red outline to the field
            this.addErrorHighlighting(element);

            const messageElement = document.createElement("div");
            messageElement.className = "validation-message alert alert-danger mt-2";
            messageElement.style.cssText = "padding: 0.5rem; font-size: 0.9rem;";
            messageElement.textContent = message;
            messageElement.setAttribute('data-target', fieldId);

            try {
                // For the special expense fields, append directly to their validation column
                if (fieldId === 'course_cost' || fieldId === 'invoice_number' || fieldId === 'concur_claim') {
                    targetElement.appendChild(messageElement);
                } else {
                    // Default behavior for other fields
                    if (targetElement.parentNode) {
                        if (targetElement.nextSibling) {
                            targetElement.parentNode.insertBefore(messageElement, targetElement.nextSibling);
                        } else {
                            targetElement.parentNode.appendChild(messageElement);
                        }
                    }
                }
            } catch (e) {
                console.error(`Error inserting validation message:`, e);
            }
            return messageElement;
        },

        // Add red outline highlighting to error fields
        addErrorHighlighting: function(element) {
            const fieldId = element.id || element.name;

            // Handle different field types for visual highlighting
            if (fieldId === 'training_type' || element.closest('#training-type-card-group')) {
                // Training type cards
                const cards = document.querySelectorAll('#training-type-card-group .training-type-card');
                cards.forEach(card => card.classList.add('is-invalid'));
            } else if (fieldId === 'location_type' || element.closest('input[name="location_type"]')) {
                // Location type radio buttons
                const radioContainer = document.querySelector('input[name="location_type"]')?.closest('.form-group, .col-md-12');
                if (radioContainer) radioContainer.classList.add('is-invalid');
                
                // Also highlight individual radio buttons
                document.querySelectorAll('input[name="location_type"]').forEach(radio => {
                    const formCheck = radio.closest('.form-check');
                    if (formCheck) formCheck.classList.add('is-invalid');
                });
            } else if (fieldId === 'trainee-search-input' || element.closest('.trainee-search-container')) {
                // Trainee search area
                const traineeContainer = document.getElementById('trainee-search-input');
                if (traineeContainer) traineeContainer.classList.add('is-invalid');
                
                const searchContainer = element.closest('.trainee-search-container');
                if (searchContainer) searchContainer.classList.add('is-invalid');
            } else if (fieldId === 'trainer_name_search') {
                // Trainer search field
                element.classList.add('is-invalid');
            } else {
                // Regular form fields
                element.classList.add('is-invalid');
            }
        },

        // Clear validation message for a specific field
        clearMessage: function(element) {
            const fieldId = element.id || element.name;
            
            // Remove our validation messages
            document.querySelectorAll(`.validation-message[data-target="${fieldId}"]`).forEach(msg => msg.remove());
            
            // Clear red outline highlighting
            this.clearErrorHighlighting(element);
            
            // Also clear any server-side validation messages in the same container
            const container = element.closest('.form-group, .mb-3, .trainee-search-box, .col-md-12');
            if (container) {
                const serverErrors = container.querySelectorAll('.text-danger');
                serverErrors.forEach(error => {
                    if (error.querySelector('small') || 
                        error.textContent.includes('required') || 
                        error.textContent.includes('cannot') || 
                        error.textContent.includes('must')) {
                        error.remove();
                    }
                });
            }
        },

        // Clear red outline highlighting from fields
        clearErrorHighlighting: function(element) {
            const fieldId = element.id || element.name;

            // Handle different field types for clearing highlighting
            if (fieldId === 'training_type' || element.closest('#training-type-card-group')) {
                // Training type cards
                const cards = document.querySelectorAll('#training-type-card-group .training-type-card');
                cards.forEach(card => card.classList.remove('is-invalid'));
            } else if (fieldId === 'location_type' || element.closest('input[name="location_type"]')) {
                // Location type radio buttons
                const radioContainer = document.querySelector('input[name="location_type"]')?.closest('.form-group, .col-md-12');
                if (radioContainer) radioContainer.classList.remove('is-invalid');
                
                // Also clear individual radio buttons
                document.querySelectorAll('input[name="location_type"]').forEach(radio => {
                    const formCheck = radio.closest('.form-check');
                    if (formCheck) formCheck.classList.remove('is-invalid');
                });
            } else if (fieldId === 'trainee-search-input' || element.closest('.trainee-search-container')) {
                // Trainee search area
                const traineeContainer = document.getElementById('trainee-search-input');
                if (traineeContainer) traineeContainer.classList.remove('is-invalid');
                
                const searchContainer = element.closest('.trainee-search-container');
                if (searchContainer) searchContainer.classList.remove('is-invalid');
            } else if (fieldId === 'trainer_name_search') {
                // Trainer search field
                element.classList.remove('is-invalid');
            } else {
                // Regular form fields
                element.classList.remove('is-invalid');
            }
        },

        // Clear all validation messages and highlighting
        clearAllMessages: function() {
            document.querySelectorAll('.validation-message').forEach(msg => msg.remove());
            this.clearAllHighlighting();
        },

        // Clear all error highlighting from the form
        clearAllHighlighting: function() {
            // Clear regular form fields
            document.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
            
            // Clear training type cards
            document.querySelectorAll('#training-type-card-group .training-type-card').forEach(card => {
                card.classList.remove('is-invalid');
            });
            
            // Clear location radio buttons
            document.querySelectorAll('input[name="location_type"]').forEach(radio => {
                const formCheck = radio.closest('.form-check');
                if (formCheck) formCheck.classList.remove('is-invalid');
            });
            
            // Clear trainee search container
            const traineeContainer = document.querySelector('.trainee-search-container');
            if (traineeContainer) traineeContainer.classList.remove('is-invalid');
        },

        // Set up auto-clearing when user starts fixing issues
        setupAutoClearing: function() {
            // Clear errors when users start typing/selecting in regular fields
            document.querySelectorAll('input, textarea, select').forEach(field => {
                field.addEventListener('input', () => this.clearMessage(field));
                field.addEventListener('change', () => this.clearMessage(field));
            });

            // Special handling for file inputs (attachments)
            document.querySelectorAll('input[type="file"]').forEach(fileInput => {
                fileInput.addEventListener('change', () => {
                    if (fileInput.files && fileInput.files.length > 0) {
                        this.clearMessage(fileInput);
                    }
                });
            });

            // Special handling for radio buttons
            document.querySelectorAll('input[type="radio"]').forEach(radio => {
                radio.addEventListener('change', () => {
                    if (radio.checked && radio.value) {
                        // Clear errors for all radio buttons with the same name
                        document.querySelectorAll(`input[name="${radio.name}"]`).forEach(r => {
                            this.clearMessage(r);
                        });
                        
                        // Also clear errors from the radio group container
                        const container = radio.closest('.form-group, .col-md-12');
                        if (container) {
                            this.clearMessage(container);
                        }
                    }
                });
            });

            // Special handling for trainees - clear trainee messages when trainees are added
            const originalHasTrainees = window.hasTrainees || hasTrainees;
            if (originalHasTrainees) {
                const checkTrainees = () => {
                    if (originalHasTrainees()) {
                        const traineeInput = document.getElementById("trainee-search-input");
                        if (traineeInput) this.clearMessage(traineeInput);
                    }
                };
                
                // Listen for trainees updates
                document.addEventListener('traineesUpdated', checkTrainees);
                
                // Also check periodically for trainee changes
                setInterval(checkTrainees, 1000);
            }
        }
    };

    // Helper function to display validation messages (uses unified system)
    function showValidationMessage(element, message) {
        return ValidationManager.showMessage(element, message);
    }

    // Initialize the validation manager
    ValidationManager.setupAutoClearing();

    // Main validation logic
    submitButton.addEventListener("click", function (event) {
        // Clear all previous validation messages using unified system
        ValidationManager.clearAllMessages();
        
        let isValid = true;
        let firstInvalidElement = null;

        // Get form elements
        const trainingType = document.querySelector('input[name="training_type"]:checked');
        const locationType = document.querySelector('input[name="location_type"]:checked');
        const locationDetails = document.getElementById("location_details");
        const trainerName = document.getElementById("trainer_name_search");
        const supplierName = document.getElementById("supplier_name");
        const trainingName = document.getElementById("training_name");
        const startDate = document.getElementById("start_date");
        const endDate = document.getElementById("end_date");
        const trainingDescription = document.getElementById("training_description");
        const idaClass = document.getElementById("ida_class");
        const trainingHours = document.getElementById("training_hours");
        const courseCost = document.getElementById("course_cost");
        const concurClaim = document.getElementById("concur_claim");
        const attachments = document.getElementById("attachments");

        // Validate training type selection
        if (!trainingType) {
            const trainingTypeContainer = document.getElementById("training-type-card-group");
            if (trainingTypeContainer) {
                showValidationMessage(trainingTypeContainer, "Please select a training type.");
                if (!firstInvalidElement) firstInvalidElement = trainingTypeContainer;
            }
            isValid = false;
        }

        // Validate training name (always required)
        if (!trainingName || !trainingName.value.trim()) {
            if (trainingName) {
                showValidationMessage(trainingName, "Training Name is required.");
                if (!firstInvalidElement) firstInvalidElement = trainingName;
            }
            isValid = false;
        }

        // Validate start date (always required)
        if (!startDate || !startDate.value) {
            if (startDate) {
                showValidationMessage(startDate, "Start Date is required.");
                if (!firstInvalidElement) firstInvalidElement = startDate;
            }
            isValid = false;
        }

        // Validate end date (always required)
        if (!endDate || !endDate.value) {
            if (endDate) {
                showValidationMessage(endDate, "End Date is required.");
                if (!firstInvalidElement) firstInvalidElement = endDate;
            }
            isValid = false;
        }

        // Validate that end date is not before start date
        if (startDate && startDate.value && endDate && endDate.value) {
            const startDateValue = new Date(startDate.value);
            const endDateValue = new Date(endDate.value);
            if (endDateValue < startDateValue) {
                showValidationMessage(endDate, "End date cannot be earlier than start date.");
                if (!firstInvalidElement) firstInvalidElement = endDate;
                isValid = false;
            }
        }

        // Validate training description (always required)
        if (!trainingDescription || !trainingDescription.value.trim()) {
            if (trainingDescription) {
                showValidationMessage(trainingDescription, "Training Description is required.");
                if (!firstInvalidElement) firstInvalidElement = trainingDescription;
            }
            isValid = false;
        }

        // Validate IDA class (always required)
        if (!idaClass || !idaClass.value) {
            if (idaClass) {
                showValidationMessage(idaClass, "Training Class is required.");
                if (!firstInvalidElement) firstInvalidElement = idaClass;
            }
            isValid = false;
        }

        // Validate location type selection
        if (!locationType) {
            const locationTypeContainer = document.querySelector('.form-group:has(input[name="location_type"])');
            const fallbackContainer = document.querySelector('input[name="location_type"]')?.closest('.form-group, .col-md-12');
            const container = locationTypeContainer || fallbackContainer;
            
            if (container) {
                showValidationMessage(container, "Please select a location type.");
                if (!firstInvalidElement) firstInvalidElement = container;
            }
            isValid = false;
        } else {
            // Validate location details for Offsite training
            if (locationType.value === "Offsite") {
                if (!locationDetails || !locationDetails.value.trim()) {
                    if (locationDetails) {
                        showValidationMessage(locationDetails, "Location Details is required for offsite training.");
                        if (!firstInvalidElement) firstInvalidElement = locationDetails;
                    }
                    isValid = false;
                }
            }
            
            // Validate attachments for Virtual training
            if (locationType.value === "Virtual") {
                if (!attachments || attachments.files.length === 0) {
                    if (attachments) {
                        showValidationMessage(attachments, "At least one attachment is required for virtual training.");
                        if (!firstInvalidElement) firstInvalidElement = attachments;
                    }
                    isValid = false;
                }
            }
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

                // Validate invoice number for External Training
                const invoiceNumber = document.getElementById("invoice_number");
                if (!invoiceNumber || !invoiceNumber.value.trim()) {
                    if (invoiceNumber) {
                        showValidationMessage(invoiceNumber, "Invoice Number is required for external training.");
                        if (!firstInvalidElement) firstInvalidElement = invoiceNumber;
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
