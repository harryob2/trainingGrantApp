/**
 * Helper functions and UI initialization for the main training form.
 */

document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("training-form");
    if (!form) {
        console.warn("Form #training-form not found. Cannot initialize form helpers.");
        return;
    }

    // --- Initialize Date Pickers ---
    try {
        if (typeof flatpickr !== 'undefined') {
            flatpickr(".date-picker", { dateFormat: "Y-m-d", allowInput: true });
             console.log("Flatpickr date pickers initialized.");
        } else {
            console.warn("Flatpickr library not found.");
        }
    } catch (e) {
        console.error("Error initializing Flatpickr:", e);
    }


    // --- Initialize Auto-Resize Textareas ---
    try {
        document.querySelectorAll(".auto-resize-textarea").forEach((textarea) => {
            textarea.addEventListener("input", function () {
                this.style.height = "auto";
                const maxHeight = 300; // Max height in px
                this.style.height = Math.min(this.scrollHeight, maxHeight) + "px";
                this.style.overflowY = this.scrollHeight > maxHeight ? "auto" : "hidden";
            });
            // Initialize on page load
            if (textarea.value) {
                textarea.dispatchEvent(new Event("input"));
            }
        });
        console.log("Auto-resize textareas initialized.");
    } catch(e) {
         console.error("Error initializing auto-resize textareas:", e);
    }


    // --- Initialize Card Selection Logic ---
    try {
        const cardGroup = document.getElementById("training-type-card-group");
        if (cardGroup) {
            const cards = cardGroup.querySelectorAll(".training-type-card");
            const radios = form.elements["training_type"]; // Use form reference

            if (cards.length > 0 && radios) {
                function updateCardSelection() {
                    let selectedValue = Array.from(radios).find(r => r.checked)?.value;
                    cards.forEach(card => {
                        card.classList.toggle("selected", card.dataset.value === selectedValue);
                    });
                }

                cards.forEach(card => {
                    card.addEventListener("click", function () {
                        radios.forEach(radio => {
                            radio.checked = (radio.value === this.dataset.value);
                        });
                        updateCardSelection();
                        const checkedRadio = Array.from(radios).find(r => r.checked);
                        if (checkedRadio) {
                            checkedRadio.dispatchEvent(new Event("change", { bubbles: true }));
                        }
                    });
                    card.addEventListener("keydown", function (e) {
                        if (e.key === "Enter" || e.key === " ") {
                            e.preventDefault();
                            this.click();
                        }
                    });
                });
                updateCardSelection(); // Initial state
                console.log("Card selection logic initialized.");
            } else {
                console.warn("Training type cards or radios not found for card selection init.");
            }
        } else {
            console.warn("Card group #training-type-card-group not found for card selection init.");
        }
    } catch (e) {
         console.error("Error initializing card selection:", e);
    }

    // --- Initialize Form Visibility Logic ---
    try {
        const trainingTypeRadios = form.elements["training_type"];
        const locationTypeRadios = form.elements["location_type"];
        const trainingDetailsSection = document.getElementById("training-details-section");
        const internalTrainerContainer = document.getElementById("internal-trainer-container");
        const externalSupplierContainer = document.getElementById("external-supplier-container");
        const trainerHoursContainer = document.getElementById("trainer-Hours-container");
        const trainingClassContainer = document.getElementById("training-class-container");
        const courseCostContainer = document.getElementById("course-cost-container");
        const invoiceNumberContainer = document.getElementById("invoice-number-container");
        const concurClaimContainer = document.getElementById("concur-claim-container");
        const locationDetailsContainer = document.getElementById("location-details-container");
        const virtualTrainingNote = document.getElementById("virtual-training-attachment-note");

        // Basic check for essential elements
        if (!trainingTypeRadios || !locationTypeRadios || !trainingDetailsSection) {
            console.warn("Essential elements missing for form visibility logic.");
            return; // Exit if core elements are missing
        }

        function handleTrainingTypeChange() {
            const selectedTrainingType = form.elements["training_type"]?.value;
            
            // Check if there are any validation errors in the training details section
            const hasValidationErrors = trainingDetailsSection.querySelector('.text-danger');
            
            // Show the section if training type is selected OR if there are validation errors
            trainingDetailsSection.classList.toggle("d-none", !selectedTrainingType && !hasValidationErrors);

            if (selectedTrainingType) {
                internalTrainerContainer?.classList.toggle("d-none", selectedTrainingType !== "Internal Training");
                externalSupplierContainer?.classList.toggle("d-none", selectedTrainingType !== "External Training");
                // Always show training hours and training class since they're now always required
                trainerHoursContainer?.classList.remove("d-none");
                trainingClassContainer?.classList.remove("d-none");
                // Show course cost and invoice number only for External Training
                courseCostContainer?.classList.toggle("d-none", selectedTrainingType !== "External Training");
                invoiceNumberContainer?.classList.toggle("d-none", selectedTrainingType !== "External Training");
                concurClaimContainer?.classList.toggle("d-none", selectedTrainingType !== "External Training");
                
                // Clear course cost when switching to internal training to prevent client-side validation issues
                if (selectedTrainingType === "Internal Training") {
                    const courseCostField = document.getElementById("course_cost");
                    if (courseCostField && courseCostField.value) {
                        // Use currency function if available, otherwise clear directly
                        if (window.setCurrencyValue) {
                            window.setCurrencyValue(courseCostField, "");
                        } else {
                            courseCostField.value = "";
                        }
                    }
                }
            }
        }

        function handleLocationTypeChange() {
            const selectedLocationType = form.elements["location_type"]?.value;
            locationDetailsContainer?.classList.toggle("d-none", selectedLocationType !== "Offsite");
            virtualTrainingNote?.classList.toggle("d-none", selectedLocationType !== "Virtual");
        }

        Array.from(trainingTypeRadios).forEach((radio) => {
            radio.addEventListener("change", handleTrainingTypeChange);
        });
        Array.from(locationTypeRadios).forEach((radio) => {
            radio.addEventListener("change", handleLocationTypeChange);
        });

        handleTrainingTypeChange(); // Initial state
        handleLocationTypeChange(); // Initial state
        console.log("Form visibility logic initialized.");

    } catch (e) {
        console.error("Error initializing form visibility:", e);
    }

    console.log("Form helpers initialized successfully.");
}); 