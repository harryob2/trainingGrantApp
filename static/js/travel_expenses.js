/**
 * Travel Expenses Management
 * Handles modal interactions, validation, and data management for travel expenses
 */

class TravelExpensesManager {
    constructor() {
        this.travelExpenses = [];
        this.editingIndex = -1;
        this.modal = null;
        this.form = null;
        this.traineesData = [];
        this.trainerData = null;
        
        this.init();
    }

    init() {
        this.modal = document.getElementById('travelExpenseModal');
        this.form = document.getElementById('travel-expense-form');
        
        if (!this.modal || !this.form) {
            console.error('Travel expense modal or form not found');
            return;
        }

        this.setupEventListeners();
        this.loadExistingData();
        this.updateDisplay();
    }

    setupEventListeners() {
        // Add travel expense button
        const addBtn = document.getElementById('add-travel-expense-btn');
        if (addBtn) {
            addBtn.addEventListener('click', () => this.openModal());
        }

        // Modal save button
        const saveBtn = document.getElementById('save-travel-expense-btn');
        if (saveBtn) {
            saveBtn.addEventListener('click', () => this.saveTravelExpense());
        }

        // Travel mode change handler
        const travelModeInputs = document.querySelectorAll('input[name="travel_mode"]');
        travelModeInputs.forEach(input => {
            input.addEventListener('change', () => this.handleTravelModeChange());
        });

        // Modal reset on close
        if (this.modal) {
            this.modal.addEventListener('hidden.bs.modal', () => this.resetModal());
        }

        // Form submission handler to include travel expenses data
        const mainForm = document.getElementById('training-form');
        if (mainForm) {
            mainForm.addEventListener('submit', () => this.prepareDataForSubmission());
        }

        // Enhanced dynamic error clearing with visual feedback
        this.setupDynamicErrorClearing();
    }

    setupDynamicErrorClearing() {
        // Travel date field
        const travelDateField = document.getElementById('travel_date');
        if (travelDateField) {
            travelDateField.addEventListener('input', () => this.clearFieldErrors(travelDateField, 'travel_date'));
            travelDateField.addEventListener('change', () => {
                this.clearFieldErrors(travelDateField, 'travel_date');
                this.validateTravelDate(); // Re-validate for date range
            });
        }

        // Destination field
        const destinationField = document.getElementById('destination');
        if (destinationField) {
            destinationField.addEventListener('input', () => {
                if (destinationField.value.trim()) {
                    this.clearFieldErrors(destinationField, 'destination');
                }
            });
        }

        // Concur claim number field
        const concurClaimField = document.getElementById('concur_claim_number');
        if (concurClaimField) {
            concurClaimField.addEventListener('input', () => {
                if (concurClaimField.value.trim()) {
                    this.clearFieldErrors(concurClaimField, 'concur_claim_number');
                }
            });
        }

        // Travel mode radio buttons
        const travelModeInputs = document.querySelectorAll('input[name="travel_mode"]');
        travelModeInputs.forEach(input => {
            input.addEventListener('change', () => {
                this.clearFieldErrors(input, 'travel_mode');
                this.handleTravelModeChange();
            });
        });

        // Cost field
        const costField = document.getElementById('cost');
        if (costField) {
            costField.addEventListener('input', () => {
                if (costField.value && parseFloat(costField.value) > 0) {
                    this.clearFieldErrors(costField, 'cost');
                }
            });
        }

        // Distance field
        const distanceField = document.getElementById('distance_km');
        if (distanceField) {
            distanceField.addEventListener('input', () => {
                if (distanceField.value && parseFloat(distanceField.value) > 0) {
                    this.clearFieldErrors(distanceField, 'distance');
                }
            });
        }

        // Traveler checkboxes - need to handle dynamically as they're populated later
        document.addEventListener('change', (e) => {
            if (e.target.matches('#traveler-checkboxes input[type="checkbox"]')) {
                const checkedBoxes = document.querySelectorAll('#traveler-checkboxes input[type="checkbox"]:checked');
                if (checkedBoxes.length > 0) {
                    this.clearFieldErrors(null, 'travelers');
                }
            }
        });
    }

    clearFieldErrors(field, fieldType) {
        // Get the current error container (check both possible class names for compatibility)
        const errorContainer = this.modal.querySelector('.validation-error') || this.modal.querySelector('.validation-errors-container');
        if (!errorContainer) return; // No errors to clear
        
        // Determine which error messages to remove based on the field type
        let errorTextToRemove = [];
        
        switch(fieldType) {
            case 'travel_date':
                errorTextToRemove = ['Travel date is required', 'Travel date must be within 1 week before training start or 1 week after training end'];
                break;
            case 'destination':
                errorTextToRemove = ['Destination is required'];
                break;
            case 'concur_claim_number':
                errorTextToRemove = ['Concur claim number is required'];
                break;
            case 'travelers':
                errorTextToRemove = ['Please select at least one traveler'];
                break;
            case 'travel_mode':
                errorTextToRemove = ['Please select a travel mode'];
                break;
            case 'cost':
                errorTextToRemove = ['Cost is required for rail, bus, and flight expenses'];
                break;
            case 'distance':
                errorTextToRemove = ['Distance in km is required for mileage expenses'];
                break;
        }
        
        // Get current error list
        const errorList = errorContainer.querySelector('ul');
        if (!errorList) return;
        
        const errorItems = errorList.querySelectorAll('li');
        const remainingErrors = [];
        
        // Filter out the errors that should be removed for this field
        errorItems.forEach(item => {
            const errorText = item.textContent.trim();
            const shouldRemove = errorTextToRemove.some(textToRemove => errorText.includes(textToRemove));
            
            if (!shouldRemove) {
                remainingErrors.push(errorText);
            }
        });
        
        // Update the error container
        if (remainingErrors.length === 0) {
            // No errors left, remove the entire container
            errorContainer.remove();
        } else {
            // Update the error list with remaining errors
            errorList.innerHTML = remainingErrors.map(error => `<li>${error}</li>`).join('');
        }
        
        // Update error highlighting to reflect current state
        this.updateErrorHighlighting();
    }

    calculateAllowedDateRange() {
        const startDate = document.getElementById('start_date').value;
        const endDate = document.getElementById('end_date').value;
        
        let minAllowed = null;
        let maxAllowed = null;
        
        if (startDate) {
            const startDateObj = new Date(startDate);
            startDateObj.setDate(startDateObj.getDate() - 7); // 1 week before
            minAllowed = startDateObj.toISOString().split('T')[0];
        }
        
        if (endDate) {
            const endDateObj = new Date(endDate);
            endDateObj.setDate(endDateObj.getDate() + 7); // 1 week after
            maxAllowed = endDateObj.toISOString().split('T')[0];
        }
        
        return { minAllowed, maxAllowed };
    }

    validateTravelDate() {
        const travelDate = document.getElementById('travel_date').value;
        if (!travelDate) return;

        const { minAllowed, maxAllowed } = this.calculateAllowedDateRange();
        
        if ((minAllowed && travelDate < minAllowed) || (maxAllowed && travelDate > maxAllowed)) {
            this.addSpecificError('travel_date', 'Travel date must be within 1 week before training start or 1 week after training end');
        }
    }

    validateCostOrDistance() {
        const travelMode = document.querySelector('input[name="travel_mode"]:checked');
        if (!travelMode) return;

        if (travelMode.value === 'mileage') {
            const distance = document.getElementById('distance_km').value;
            if (distance && parseFloat(distance) > 0) {
                this.removeSpecificError('distance');
            }
        } else {
            const cost = document.getElementById('cost').value;
            if (cost && parseFloat(cost) > 0) {
                this.removeSpecificError('cost');
            }
        }
    }

    validateForm() {
        const errors = [];
        
        // Travel date validation
        const travelDate = document.getElementById('travel_date').value;
        if (!travelDate) {
            errors.push({ field: 'travel_date', message: 'Travel date is required' });
        } else {
            // Check if date is within allowed range (1 week before start to 1 week after end)
            const { minAllowed, maxAllowed } = this.calculateAllowedDateRange();
            
            if ((minAllowed && travelDate < minAllowed) || (maxAllowed && travelDate > maxAllowed)) {
                errors.push({ field: 'travel_date', message: 'Travel date must be within 1 week before training start or 1 week after training end' });
            }
        }

        // Destination validation
        const destination = document.getElementById('destination').value.trim();
        if (!destination) {
            errors.push({ field: 'destination', message: 'Destination is required' });
        }

        // Concur claim number validation
        const concurClaimNumber = document.getElementById('concur_claim_number').value.trim();
        if (!concurClaimNumber) {
            errors.push({ field: 'concur_claim_number', message: 'Concur claim number is required' });
        }

        // Traveler validation (multiple selection)
        const selectedTravelers = document.querySelectorAll('#traveler-checkboxes input[type="checkbox"]:checked');
        if (selectedTravelers.length === 0) {
            errors.push({ field: 'travelers', message: 'Please select at least one traveler' });
        }

        // Travel mode validation
        const travelMode = document.querySelector('input[name="travel_mode"]:checked');
        if (!travelMode) {
            errors.push({ field: 'travel_mode', message: 'Please select a travel mode' });
        } else {
            if (travelMode.value === 'mileage') {
                const distance = document.getElementById('distance_km').value;
                if (!distance || parseFloat(distance) <= 0) {
                    errors.push({ field: 'distance', message: 'Distance in km is required for mileage expenses' });
                }
            } else {
                const cost = this.getCostValue();
                if (!cost || cost <= 0) {
                    errors.push({ field: 'cost', message: 'Cost is required for rail, bus, and flight expenses' });
                }
            }
        }

        return errors;
    }

    addSpecificError(field, message) {
        // Remove existing error for this field first
        this.removeSpecificError(field);
        
        let errorContainer = this.modal.querySelector('.validation-errors-container');
        if (!errorContainer) {
            errorContainer = document.createElement('div');
            errorContainer.className = 'validation-errors-container alert alert-danger';
            errorContainer.innerHTML = '<ul class="mb-0"></ul>';
            
            const modalBody = this.modal.querySelector('.modal-body');
            modalBody.insertBefore(errorContainer, modalBody.firstChild);
        }

        const errorList = errorContainer.querySelector('ul');
        const errorItem = document.createElement('li');
        errorItem.className = `error-${field}`;
        errorItem.textContent = message;
        errorList.appendChild(errorItem);

        // Show the container
        errorContainer.style.display = 'block';
    }

    removeSpecificError(field) {
        const errorItem = this.modal.querySelector(`.error-${field}`);
        if (errorItem) {
            errorItem.remove();
            
            // Hide container if no errors remain
            const errorContainer = this.modal.querySelector('.validation-errors-container');
            const remainingErrors = errorContainer.querySelectorAll('li');
            if (remainingErrors.length === 0) {
                errorContainer.style.display = 'none';
            }
        }
    }

    showValidationErrors(errors) {
        // Clear existing error messages first
        const existingErrors = this.modal.querySelectorAll('.validation-error, .validation-errors-container');
        existingErrors.forEach(error => error.remove());

        // Show new errors at the top of the modal
        const errorContainer = document.createElement('div');
        errorContainer.className = 'validation-error alert alert-danger';
        errorContainer.innerHTML = '<ul class="mb-0">' + 
            errors.map(error => typeof error === 'object' ? error.message : error).map(msg => `<li>${msg}</li>`).join('') + 
            '</ul>';

        const modalBody = this.modal.querySelector('.modal-body');
        modalBody.insertBefore(errorContainer, modalBody.firstChild);

        // Add error styling to specific fields
        const errorMessages = errors.map(error => typeof error === 'object' ? error.message : error);
        this.highlightErrorFields(errorMessages);
    }

    loadExistingData() {
        // Load trainees data from the main form
        const traineesDataField = document.getElementById('trainees_data');
        if (traineesDataField && traineesDataField.value) {
            try {
                this.traineesData = JSON.parse(traineesDataField.value) || [];
            } catch (e) {
                console.error('Error parsing trainees data:', e);
                this.traineesData = [];
            }
        }

        // Load trainer data
        const trainerNameField = document.getElementById('trainer_name_hidden');
        const trainerEmailField = document.getElementById('trainer_email_hidden');
        if (trainerNameField && trainerEmailField) {
            this.trainerData = {
                name: trainerNameField.value,
                email: trainerEmailField.value
            };
        }

        // Load existing travel expenses (for edit mode) - use script tag approach
        const existingDataScript = document.getElementById('existing-travel-expenses-data');
        if (existingDataScript) {
            try {
                const rawExpenses = JSON.parse(existingDataScript.textContent) || [];
                console.log('[TravelExpenses] Raw expenses from script tag:', rawExpenses);
                
                // Transform the data from database format to JavaScript format
                // Database stores individual records per traveler, but we need grouped records
                this.travelExpenses = this.transformDatabaseExpenses(rawExpenses);
                console.log('[TravelExpenses] Transformed expenses:', this.travelExpenses);
            } catch (e) {
                console.error('Error parsing existing travel expenses from script tag:', e);
                console.error('Script content was:', existingDataScript ? existingDataScript.textContent : 'null');
                this.travelExpenses = [];
            }
        } else {
            console.log('[TravelExpenses] No travel expenses script tag found, checking hidden field as fallback');
            
            // Fallback to hidden field (for backwards compatibility)
            const existingDataField = document.getElementById('travel_expenses_data');
            if (existingDataField && existingDataField.value) {
                console.log('[TravelExpenses] Using hidden field fallback');
                console.log('[TravelExpenses] Raw field value:', existingDataField.value);
                
                const cleanValue = existingDataField.value.trim();
                if (!cleanValue || cleanValue === '' || cleanValue === 'null') {
                    console.log('[TravelExpenses] Empty or null field value, using empty array');
                    this.travelExpenses = [];
                } else {
                    try {
                        const rawExpenses = JSON.parse(cleanValue) || [];
                        console.log('[TravelExpenses] Raw expenses from database:', rawExpenses);
                        this.travelExpenses = this.transformDatabaseExpenses(rawExpenses);
                        console.log('[TravelExpenses] Transformed expenses:', this.travelExpenses);
                    } catch (e) {
                        console.error('Error parsing existing travel expenses:', e);
                        console.error('Problem value was:', cleanValue);
                        this.travelExpenses = [];
                    }
                }
            } else {
                console.log('[TravelExpenses] No travel expenses data found');
                this.travelExpenses = [];
            }
        }

        this.updateTravelerCheckboxes();
    }

    transformDatabaseExpenses(rawExpenses) {
        // Group expenses by travel_date, destination, and travel_mode
        const groupedExpenses = {};
        
        rawExpenses.forEach(expense => {
            // Create a unique key for grouping
            const key = `${expense.travel_date}_${expense.destination}_${expense.travel_mode}_${expense.cost || 0}_${expense.distance_km || 0}`;
            
            if (!groupedExpenses[key]) {
                // Create new grouped expense
                groupedExpenses[key] = {
                    travel_date: expense.travel_date,
                    destination: expense.destination,
                    travel_mode: expense.travel_mode,
                    cost: expense.cost,
                    distance_km: expense.distance_km,
                    concur_claim_number: expense.concur_claim_number,
                    travelers: []
                };
            }
            
            // Add traveler to the group
            groupedExpenses[key].travelers.push({
                traveler_type: expense.traveler_type,
                traveler_email: expense.traveler_email,
                traveler_name: expense.traveler_name
            });
        });
        
        // Convert grouped expenses object to array
        return Object.values(groupedExpenses);
    }

    updateTravelerCheckboxes() {
        const checkboxContainer = document.getElementById('traveler-checkboxes');
        const noTravelersMsg = document.getElementById('no-travelers-available');
        
        if (!checkboxContainer) return;

        // Clear existing checkboxes
        checkboxContainer.innerHTML = '';

        let hasTravalers = false;

        // Add trainer checkbox if available
        if (this.trainerData && this.trainerData.name && this.trainerData.email) {
            hasTravalers = true;
            const checkboxDiv = document.createElement('div');
            checkboxDiv.className = 'form-check mb-2';
            // Use btoa encoding to handle special characters in names/emails
            const trainerDataJson = JSON.stringify({
                type: 'trainer',
                email: this.trainerData.email,
                name: this.trainerData.name
            });
            checkboxDiv.innerHTML = `
                <input class="form-check-input" type="checkbox" id="traveler_trainer" 
                       value="${btoa(trainerDataJson)}">
                <label class="form-check-label" for="traveler_trainer">
                    <strong>${this.trainerData.name}</strong> <span class="badge bg-primary">Trainer</span>
                </label>
            `;
            checkboxContainer.appendChild(checkboxDiv);
        }

        // Add trainee checkboxes
        this.traineesData.forEach((trainee, index) => {
            if (trainee.email && trainee.name) {
                hasTravalers = true;
                const checkboxDiv = document.createElement('div');
                checkboxDiv.className = 'form-check mb-2';
                // Use btoa encoding to handle special characters in names/emails
                const traineeDataJson = JSON.stringify({
                    type: 'trainee',
                    email: trainee.email,
                    name: trainee.name
                });
                checkboxDiv.innerHTML = `
                    <input class="form-check-input" type="checkbox" id="traveler_trainee_${index}" 
                           value="${btoa(traineeDataJson)}">
                    <label class="form-check-label" for="traveler_trainee_${index}">
                        <strong>${trainee.name}</strong> <span class="badge bg-secondary">Trainee</span>
                    </label>
                `;
                checkboxContainer.appendChild(checkboxDiv);
            }
        });

        // Show/hide no travelers message
        if (noTravelersMsg) {
            noTravelersMsg.style.display = hasTravalers ? 'none' : 'block';
        }
    }

    openModal(editIndex = -1) {
        this.editingIndex = editIndex;
        
        // Update traveler checkboxes with current data FIRST
        this.updateTravelerCheckboxes();
        
        if (editIndex >= 0 && this.travelExpenses[editIndex]) {
            this.populateModalForEdit(this.travelExpenses[editIndex]);
        } else {
            this.resetModal();
        }
        
        // Set date constraints based on training dates
        this.setDateConstraints();

        // Show modal
        const modalInstance = new bootstrap.Modal(this.modal);
        modalInstance.show();
    }

    populateModalForEdit(expense) {
        // Populate form fields
        document.getElementById('travel_date').value = expense.travel_date;
        document.getElementById('destination').value = expense.destination;
        document.getElementById('concur_claim_number').value = expense.concur_claim_number || '';
        
        // Set traveler selections (multiple travelers)
        const travelers = expense.travelers || [];
        travelers.forEach(traveler => {
            const travelerDataJson = JSON.stringify({
                type: traveler.traveler_type,
                email: traveler.traveler_email,
                name: traveler.traveler_name
            });
            // Use btoa encoding for comparison
            const travelerValue = btoa(travelerDataJson);
            
            const checkbox = document.querySelector(`input[type="checkbox"][value="${travelerValue}"]`);
            if (checkbox) {
                checkbox.checked = true;
            }
        });

        // Set travel mode
        const travelModeRadio = document.querySelector(`input[name="travel_mode"][value="${expense.travel_mode}"]`);
        if (travelModeRadio) {
            travelModeRadio.checked = true;
        }

        // Set cost or distance based on travel mode
        if (expense.travel_mode === 'mileage') {
            document.getElementById('distance_km').value = expense.distance_km || '';
        } else {
            const costField = document.getElementById('cost');
            if (costField && expense.cost) {
                // Use the global currency function if available
                if (window.setCurrencyValue) {
                    window.setCurrencyValue(costField, expense.cost);
                } else {
                    costField.value = expense.cost || '';
                }
            }
        }

        this.handleTravelModeChange();
    }

    resetModal() {
        this.editingIndex = -1;
        this.form.reset();
        
        // Clear any validation messages
        const errorMessages = this.modal.querySelectorAll('.text-danger, .validation-error, .validation-errors-container');
        errorMessages.forEach(msg => msg.remove());

        // Clear any error styling from fields
        this.clearAllHighlighting();
        
        // Reset travel mode visibility
        this.handleTravelModeChange();
    }

    setDateConstraints() {
        const travelDateField = document.getElementById('travel_date');
        if (!travelDateField) return;

        const { minAllowed, maxAllowed } = this.calculateAllowedDateRange();

        if (minAllowed) {
            travelDateField.setAttribute('min', minAllowed);
        }
        if (maxAllowed) {
            travelDateField.setAttribute('max', maxAllowed);
        }
    }

    handleTravelModeChange() {
        const selectedMode = document.querySelector('input[name="travel_mode"]:checked');
        const costGroup = document.getElementById('cost-group');
        const distanceGroup = document.getElementById('distance-group');
        const costField = document.getElementById('cost');
        const distanceField = document.getElementById('distance_km');

        if (!selectedMode) {
            // Hide both groups if no mode selected
            if (costGroup) costGroup.style.display = 'none';
            if (distanceGroup) distanceGroup.style.display = 'none';
            return;
        }

        if (selectedMode.value === 'mileage') {
            // Show distance, hide cost
            if (costGroup) costGroup.style.display = 'none';
            if (distanceGroup) distanceGroup.style.display = 'block';
            if (costField) costField.value = '';
        } else {
            // Show cost, hide distance (for rail, bus, economy_flight)
            if (costGroup) costGroup.style.display = 'block';
            if (distanceGroup) distanceGroup.style.display = 'none';
            if (distanceField) distanceField.value = '';
        }
    }

    saveTravelExpense() {
        const errors = this.validateForm();
        
        if (errors.length > 0) {
            this.showValidationErrors(errors);
            return;
        }

        // Collect selected travelers
        const selectedTravelers = [];
        const travelerCheckboxes = document.querySelectorAll('#traveler-checkboxes input[type="checkbox"]:checked');
        travelerCheckboxes.forEach(checkbox => {
            // Use atob to decode the base64 encoded value
            const travelerData = JSON.parse(atob(checkbox.value));
            selectedTravelers.push({
                traveler_type: travelerData.type,
                traveler_email: travelerData.email,
                traveler_name: travelerData.name
            });
        });

        const travelMode = document.querySelector('input[name="travel_mode"]:checked').value;
        
        const expense = {
            travel_date: document.getElementById('travel_date').value,
            destination: document.getElementById('destination').value.trim(),
            concur_claim_number: document.getElementById('concur_claim_number').value.trim(),
            travelers: selectedTravelers,
            travel_mode: travelMode,
            cost: travelMode === 'mileage' ? null : this.getCostValue(),
            distance_km: travelMode === 'mileage' ? parseFloat(document.getElementById('distance_km').value) : null
        };

        // Calculate cost for mileage (60 cents per km) - store for backend but don't display
        if (travelMode === 'mileage' && expense.distance_km) {
            expense.cost = expense.distance_km * 0.60;
        }

        // Add or update expense
        if (this.editingIndex >= 0) {
            this.travelExpenses[this.editingIndex] = expense;
        } else {
            this.travelExpenses.push(expense);
        }

        // Update display and close modal
        this.updateDisplay();
        const modalInstance = bootstrap.Modal.getInstance(this.modal);
        modalInstance.hide();
    }

    deleteTravelExpense(index) {
        if (confirm('Are you sure you want to delete this travel expense?')) {
            this.travelExpenses.splice(index, 1);
            this.updateDisplay();
        }
    }

    updateDisplay() {
        const container = document.getElementById('travel-expenses-list');
        const emptyMessage = document.getElementById('no-travel-expenses-message');
        
        if (!container) return;

        if (this.travelExpenses.length === 0) {
            container.innerHTML = '';
            if (emptyMessage) emptyMessage.style.display = 'block';
        } else {
            if (emptyMessage) emptyMessage.style.display = 'none';
            container.innerHTML = this.generateExpensesTable();
        }

        // Dispatch event to notify other components that travel expenses have been updated
        document.dispatchEvent(new CustomEvent('travelExpensesUpdated'));
    }

    generateExpensesTable() {
        const table = `
            <div class="table-responsive">
                <table class="table table-bordered table-hover">
                    <thead class="table-light">
                        <tr>
                            <th>Date</th>
                            <th>Destination</th>                            
                            <th>Travelers</th>
                            <th>Mode</th>
                            <th>Distance/Cost</th>
                            <th>Concur Claim</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${this.travelExpenses.map((expense, index) => this.generateExpenseRow(expense, index)).join('')}
                    </tbody>
                </table>
            </div>
        `;
        return table;
    }

    generateExpenseRow(expense, index) {
        const formattedDate = new Date(expense.travel_date).toLocaleDateString();
        
        // Format travelers list
        const travelersList = expense.travelers.map(traveler => 
            `${traveler.traveler_name} <small class="text-muted">(${traveler.traveler_type})</small>`
        ).join('<br>');
        
        // Format distance/cost display without showing calculated cost
        const distanceDisplay = expense.travel_mode === 'mileage' 
            ? `${expense.distance_km} km`
            : `€${expense.cost.toFixed(2)}`;
        
        const modeDisplay = expense.travel_mode === 'mileage' ? 'Mileage' :
                           expense.travel_mode === 'rail' ? 'Rail' : 
                           expense.travel_mode === 'bus' ? 'Bus' : 'Economy Flight';

        return `
            <tr>
                <td>${formattedDate}</td>
                <td>${expense.destination}</td>
                <td>${travelersList}</td>
                <td>${modeDisplay}</td>
                <td>${distanceDisplay}</td>
                <td>${expense.concur_claim_number || '-'}</td>
                <td>
                    <button type="button" class="btn btn-sm btn-outline-primary me-1" 
                            onclick="travelExpensesManager.openModal(${index})" title="Edit">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button type="button" class="btn btn-sm btn-outline-danger" 
                            onclick="travelExpensesManager.deleteTravelExpense(${index})" title="Delete">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    }

    prepareDataForSubmission() {
        // Create or update hidden field with travel expenses data
        // Convert the format to be compatible with backend processing
        const formattedExpenses = this.travelExpenses.map(expense => {
            // Create separate entries for each traveler
                            return expense.travelers.map(traveler => ({
                    travel_date: expense.travel_date,
                    destination: expense.destination,
                    concur_claim_number: expense.concur_claim_number,
                    traveler_type: traveler.traveler_type,
                    traveler_email: traveler.traveler_email,
                    traveler_name: traveler.traveler_name,
                    travel_mode: expense.travel_mode,
                    cost: expense.cost,
                    distance_km: expense.distance_km
                }));
        }).flat(); // Flatten the array

        let hiddenField = document.getElementById('travel_expenses_data');
        if (!hiddenField) {
            hiddenField = document.createElement('input');
            hiddenField.type = 'hidden';
            hiddenField.id = 'travel_expenses_data';
            hiddenField.name = 'travel_expenses_data';
            document.getElementById('training-form').appendChild(hiddenField);
        }
        
        hiddenField.value = JSON.stringify(formattedExpenses);
    }

    // Method to refresh traveler data when trainees are updated
    refreshTravelerData() {
        this.loadExistingData();
        this.updateTravelerCheckboxes();
    }

    updateErrorHighlighting() {
        // Get current error messages from the error container
        const errorContainer = this.modal.querySelector('.validation-error') || this.modal.querySelector('.validation-errors-container');
        if (!errorContainer) {
            // No errors, clear all highlighting
            this.clearAllHighlighting();
            return;
        }

        const errorList = errorContainer.querySelector('ul');
        if (!errorList) return;

        const errorItems = errorList.querySelectorAll('li');
        const currentErrors = Array.from(errorItems).map(item => item.textContent.trim());
        
        // Update highlighting based on current errors
        this.highlightErrorFields(currentErrors);
    }

    highlightErrorFields(errors) {
        // Clear all previous error styling first
        this.clearAllHighlighting();

        // Add error styling to fields mentioned in current error messages
        errors.forEach(error => {
            if (error.includes('Travel date')) {
                const field = document.getElementById('travel_date');
                if (field) field.classList.add('is-invalid');
            }
            if (error.includes('Destination')) {
                const field = document.getElementById('destination');
                if (field) field.classList.add('is-invalid');
            }
            if (error.includes('Concur claim number')) {
                const field = document.getElementById('concur_claim_number');
                if (field) field.classList.add('is-invalid');
            }
            if (error.includes('select at least one traveler')) {
                const checkboxContainer = document.getElementById('traveler-checkboxes');
                if (checkboxContainer) checkboxContainer.classList.add('is-invalid');
            }
            if (error.includes('select a travel mode')) {
                const radioButtons = document.querySelectorAll('input[name="travel_mode"]');
                radioButtons.forEach(radio => {
                    const label = radio.closest('.form-check');
                    if (label) label.classList.add('is-invalid');
                });
            }
            if (error.includes('Cost is required')) {
                const field = document.getElementById('cost');
                if (field) field.classList.add('is-invalid');
            }
            if (error.includes('Distance in km')) {
                const field = document.getElementById('distance_km');
                if (field) field.classList.add('is-invalid');
            }
        });
    }

    clearAllHighlighting() {
        // Clear highlighting from regular input fields
        const fields = ['travel_date', 'destination', 'concur_claim_number', 'cost', 'distance_km'];
        fields.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field) field.classList.remove('is-invalid');
        });

        // Clear highlighting from traveler checkboxes container
        const checkboxContainer = document.getElementById('traveler-checkboxes');
        if (checkboxContainer) checkboxContainer.classList.remove('is-invalid');

        // Clear highlighting from travel mode radio buttons
        const radioButtons = document.querySelectorAll('input[name="travel_mode"]');
        radioButtons.forEach(radio => {
            const label = radio.closest('.form-check');
            if (label) label.classList.remove('is-invalid');
        });
    }

    getCostValue() {
        const costField = document.getElementById('cost');
        if (!costField) return 0;
        
        // Try to get AutoNumeric value first
        if (typeof AutoNumeric !== 'undefined') {
            try {
                const autoNumericInstance = AutoNumeric.getAutoNumericElement(costField);
                if (autoNumericInstance) {
                    return parseFloat(autoNumericInstance.getNumber()) || 0;
                }
            } catch (e) {
                console.log('[TravelExpenses] AutoNumeric not available on cost field, using raw value');
            }
        }
        
        // Fallback to raw value
        return parseFloat(costField.value) || 0;
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize if we're on a page with the travel expenses section
    if (document.getElementById('travel-expenses-section')) {
        window.travelExpensesManager = new TravelExpensesManager();
        
        // Listen for trainee updates to refresh traveler dropdown
        document.addEventListener('traineesUpdated', function() {
            if (window.travelExpensesManager) {
                window.travelExpensesManager.refreshTravelerData();
            }
        });
    }
}); 