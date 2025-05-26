import { initAutocomplete } from './autocomplete.js';

document.addEventListener("DOMContentLoaded", function () {
    console.log("[FormSetup] DOMContentLoaded, initializing components...");

    // Initialize Training Catalog Search
    const trainingCatalogSearchInput = document.getElementById("training_catalog_search_input");
    const trainingCatalogSearchResultsDivId = "training_catalog_search_results";
    const trainingFormDetails = document.getElementById("training-form-details");
    const addManuallyBtn = document.getElementById("add-manually-btn");
    
    if (trainingCatalogSearchInput && document.getElementById(trainingCatalogSearchResultsDivId)) {
        console.log("[FormSetup] Setting up Training Catalog Search.");
        initAutocomplete({
            inputId: "training_catalog_search_input",
            resultsId: trainingCatalogSearchResultsDivId,
            lookupUrl: "/api/lookup/trainings",
            fuseKeys: ['name', 'area', 'course_code'], // searchable fields from catalog
            renderItem: (training) => {
                if (training.id === 0 && training.name === "Other (Manual Entry)") { // Special rendering for "Other"
                    return `<div class="fw-bold p-2">${training.name}</div>`;
                }
                return `
                    <div class="fw-medium">${training.name}</div>
                    <div class="text-muted small">${training.area || ''} ${training.course_code ? `(${training.course_code})` : ''}</div>
                `;
            },
            onSelect: (training) => {
                console.log('[DEBUG] Selected training:', training);
                const trainingDescField = document.getElementById('training_description');
                const trainingIdField = document.getElementById('training_catalog_id');
                const trainingTypeRadios = document.querySelectorAll('input[name="training_type"]');
                const trainingTypeCards = document.querySelectorAll('.training-type-card');
                const supplierNameField = document.getElementById('supplier_name');
                const trainingHoursField = document.getElementById('training_hours');
                console.log('[DEBUG] Found trainingTypeRadios:', trainingTypeRadios);
                console.log('[DEBUG] Found trainingTypeCards:', trainingTypeCards);

                if (trainingIdField) {
                    trainingIdField.value = training.id;
                }

                if (trainingDescField) {
                    trainingDescField.value = training.id === 0 ? "" : training.name;
                    trainingDescField.placeholder = training.id === 0 ? 
                        "Please describe the training (course title, area, etc.)" : "";
                }

                // Set training type based on catalog data
                if (training.id !== 0 && training.training_type) {
                    let found = false;
                    trainingTypeRadios.forEach(radio => {
                        console.log('[DEBUG] Checking radio value:', radio.value, 'against', training.training_type);
                        if (radio.value === training.training_type) {
                            radio.checked = true;
                            found = true;
                            
                            // Update card selection - Remove active-card from all cards first
                            trainingTypeCards.forEach(card => {
                                card.classList.remove('selected');
                            });
                            
                            // Then add active-card to the matching card
                            trainingTypeCards.forEach(card => {
                                if (card.dataset.value === training.training_type) {
                                    card.classList.add('selected');
                                    console.log('[DEBUG] Activated card for type:', card.dataset.value);
                                }
                            });

                            // Trigger change event
                            radio.dispatchEvent(new Event('change', { bubbles: true }));
                            console.log('[DEBUG] Set training type to:', radio.value);
                        }
                    });
                    if (!found) {
                        console.warn('[DEBUG] No matching radio found for training_type:', training.training_type);
                    }
                } else {
                    if (training.id !== 0) {
                        console.warn('[DEBUG] training.training_type missing in selected training:', training);
                    }
                }

                // Populate supplier name if External Training
                if (training.training_type === 'External Training' && supplierNameField && training.supplier_name) {
                    supplierNameField.value = training.supplier_name;
                }

                // Populate training hours regardless of type
                if (trainingHoursField && training.training_hours) {
                    trainingHoursField.value = training.training_hours;
                }

                // Show the form details section
                if (trainingFormDetails) {
                    trainingFormDetails.classList.remove('d-none');
                }

                console.log(`[TrainingCatalogSearch] Selected: ID=${training.id}, Name=${training.name}`);
            },
            clearInputOnSelect: true, 
            showOtherOptionOnNoResults: true,
            noResultsText: "No matching trainings. Select 'Other' to enter manually.",
            otherOptionText: "Other (Manually Enter Training Details)",
            otherOptionValue: { id: 0, name: "Other (Manual Entry)" }
        });
    } else {
        console.warn("[FormSetup] Training Catalog Search input or results container not found. Skipping init.");
    }

    // Handle Add Manually button click
    if (addManuallyBtn) {
        addManuallyBtn.addEventListener('click', function() {
            if (trainingFormDetails) {
                trainingFormDetails.classList.remove('d-none');
                // Clear any selected training
                const trainingIdField = document.getElementById('training_catalog_id');
                if (trainingIdField) {
                    trainingIdField.value = '';
                }
                const trainingDescField = document.getElementById('training_description');
                if (trainingDescField) {
                    trainingDescField.value = '';
                    trainingDescField.placeholder = "Please describe the training (course title, area, etc.)";
                }
            }
        });
    }

    // Future: Other form-wide component initializations can go here.
    // For example, if you had a general date picker setup not specific to one form element.
}); 