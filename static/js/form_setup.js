import { initAutocomplete } from './autocomplete.js';

document.addEventListener("DOMContentLoaded", function () {
    console.log("[FormSetup] DOMContentLoaded, initializing components...");

    // Helper function to set currency value with retry logic
    function setCurrencyValueWithRetry(field, value, retryCount = 0) {
        const maxRetries = 5;
        const retryDelay = 50; // ms
        
        // Try to use the global setCurrencyValue function first
        if (window.setCurrencyValue && window.setCurrencyValue(field, value)) {
            return true;
        }
        
        // If that didn't work and we haven't exhausted retries, try again
        if (retryCount < maxRetries) {
            console.log(`[FormSetup] Currency value setting failed, retrying in ${retryDelay}ms (attempt ${retryCount + 1}/${maxRetries})`);
            setTimeout(() => setCurrencyValueWithRetry(field, value, retryCount + 1), retryDelay);
            return true;
        }
        
        // Fallback to setting raw value
        console.warn('[FormSetup] All currency setting attempts failed, using raw value');
        field.value = value;
        return false;
    }

    // Check if we're in edit mode
    const isEditMode = document.querySelector('form[action*="/edit/"]') !== null;
    console.log('[FormSetup] Edit mode detected:', isEditMode);

    // Initialize Training Catalog Search
    const trainingCatalogSearchInput = document.getElementById("training_catalog_search_input");
    const trainingCatalogSearchResultsDivId = "training_catalog_search_results";
    const trainingFormDetails = document.getElementById("training-form-details");
    const addManuallyBtn = document.getElementById("add-manually-btn");

    // Show form details immediately if in edit mode or if form has validation errors
    if (trainingFormDetails && (isEditMode || !trainingFormDetails.classList.contains('d-none'))) {
        trainingFormDetails.classList.remove('d-none');
        console.log('[FormSetup] Form details visible immediately (edit mode or validation errors)');
    }

    if (trainingCatalogSearchInput && document.getElementById(trainingCatalogSearchResultsDivId)) {
        console.log("[FormSetup] Setting up Training Catalog Search.");
        initAutocomplete({
            inputId: "training_catalog_search_input",
            resultsId: trainingCatalogSearchResultsDivId,
            lookupUrl: "/api/lookup/trainings",
            fuseKeys: ["training_name", "area", "training_desc"],
            renderItem: (training) => {
                return `
                    <div class="fw-medium">${training.training_name}</div>
                    ${training.area ? `<div class="text-muted small">${training.area}</div>` : ''}
                    ${training.training_desc ? `<div class="text-muted small">${training.training_desc}</div>` : ''}
                `;
            },
            onSelect: (training) => {
                console.log('[DEBUG] Selected training:', training);
                const trainingNameField = document.getElementById('training_name');
                const trainingDescField = document.getElementById('training_description');
                const idaClassField = document.getElementById('ida_class');
                const trainingTypeRadios = document.querySelectorAll('input[name="training_type"]');
                const trainingTypeCards = document.querySelectorAll('.training-type-card');
                const supplierNameField = document.getElementById('supplier_name');
                const trainingHoursField = document.getElementById('training_hours');
                const courseCostField = document.getElementById('course_cost');
                console.log('[DEBUG] Found trainingTypeRadios:', trainingTypeRadios);
                console.log('[DEBUG] Found trainingTypeCards:', trainingTypeCards);

                // Populate training name field
                if (trainingNameField) {
                    trainingNameField.value = training.id === 0 ? "" : training.training_name;
                    trainingNameField.placeholder = training.id === 0 ? 
                        "Enter the training name/title" : "";
                }

                if (trainingDescField) {
                    trainingDescField.value = training.id === 0 ? "" : training.training_desc || "";
                    trainingDescField.placeholder = training.id === 0 ? 
                        "Please describe the training (course title, area, etc.)" : "";
                }

                // Populate IDA class if available
                if (idaClassField && training.ida_class && training.id !== 0) {
                    idaClassField.value = training.ida_class;
                }

                // Handle training type selection
                if (training.training_type && training.id !== 0) {
                    // Clear existing selections
                    trainingTypeRadios.forEach(radio => {
                        radio.checked = false;
                    });
                    trainingTypeCards.forEach(card => {
                        card.classList.remove('selected');
                    });

                    // Set the appropriate training type
                    const targetRadio = Array.from(trainingTypeRadios).find(radio => 
                        radio.value === training.training_type
                    );
                    const targetCard = Array.from(trainingTypeCards).find(card => 
                        card.getAttribute('data-value') === training.training_type
                    );

                    if (targetRadio && targetCard) {
                        targetRadio.checked = true;
                        targetCard.classList.add('selected');
                        
                        // Trigger change event to update form visibility
                        targetRadio.dispatchEvent(new Event('change', { bubbles: true }));

                        console.log(`[TrainingCatalogSearch] Selected training type: ${training.training_type}`);
                    } else {
                        console.warn('[TrainingCatalogSearch] Could not find matching radio/card for training type:', training.training_type);
                    }
                }

                // Populate supplier name and course cost if External Training
                if (training.training_type === 'External Training' && supplierNameField && training.supplier_name) {
                    supplierNameField.value = training.supplier_name;
                    
                    // Handle course cost with AutoNumeric formatting
                    if (courseCostField && training.course_cost) {
                        setCurrencyValueWithRetry(courseCostField, training.course_cost);
                    }
                }

                // Populate training hours regardless of type
                if (trainingHoursField && training.training_hours) {
                    trainingHoursField.value = training.training_hours;
                }

                // Show the form details section
                if (trainingFormDetails) {
                    trainingFormDetails.classList.remove('d-none');
                }

                console.log(`[TrainingCatalogSearch] Selected: ID=${training.id}, Name=${training.training_name}`);
            },
            clearInputOnSelect: true, 
            showOtherOptionOnNoResults: true,
            noResultsText: "No matching trainings. Select 'Other' to enter manually.",
            otherOptionText: "Other (Manually Enter Training Details)",
            otherOptionValue: { id: 0, training_name: "Other (Manual Entry)" }
        });
    } else {
        console.warn("[FormSetup] Training Catalog Search input or results container not found. Skipping init.");
    }

    // Handle Add Manually button click
    if (addManuallyBtn) {
        addManuallyBtn.addEventListener('click', function() {
            if (trainingFormDetails) {
                trainingFormDetails.classList.remove('d-none');
                
                // Only clear fields if NOT in edit mode
                if (!isEditMode) {
                    // Clear any selected training
                    const trainingNameField = document.getElementById('training_name');
                    const trainingDescField = document.getElementById('training_description');
                    
                    if (trainingNameField) {
                        trainingNameField.value = '';
                        trainingNameField.placeholder = "Enter the training name/title";
                    }
                    
                    if (trainingDescField) {
                        trainingDescField.value = '';
                        trainingDescField.placeholder = "Please describe the training (course title, area, etc.)";
                    }
                } else {
                    console.log('[FormSetup] Edit mode: preserving existing training name and description');
                }
            }
        });
    }

    // Future: Other form-wide component initializations can go here.
    // For example, if you had a general date picker setup not specific to one form element.
}); 