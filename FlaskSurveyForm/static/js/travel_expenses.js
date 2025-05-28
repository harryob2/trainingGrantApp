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

        // Load existing travel expenses (for edit mode)
        const existingDataField = document.getElementById('travel_expenses_data');
        if (existingDataField && existingDataField.value) {
            try {
                this.travelExpenses = JSON.parse(existingDataField.value) || [];
            } catch (e) {
                console.error('Error parsing existing travel expenses:', e);
                this.travelExpenses = [];
            }
        }

        this.updateTravelerCheckboxes();
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
            checkboxDiv.innerHTML = `
                <input class="form-check-input" type="checkbox" id="traveler_trainer" 
                       value='${JSON.stringify({
                           type: 'trainer',
                           email: this.trainerData.email,
                           name: this.trainerData.name
                       })}'>
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
                checkboxDiv.innerHTML = `
                    <input class="form-check-input" type="checkbox" id="traveler_trainee_${index}" 
                           value='${JSON.stringify({
                               type: 'trainee',
                               email: trainee.email,
                               name: trainee.name
                           })}'>
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
        
        if (editIndex >= 0 && this.travelExpenses[editIndex]) {
            this.populateModalForEdit(this.travelExpenses[editIndex]);
        } else {
            this.resetModal();
        }

        // Update traveler checkboxes with current data
        this.updateTravelerCheckboxes();
        
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
        
        // Set traveler selections (multiple travelers)
        const travelers = expense.travelers || [];
        travelers.forEach(traveler => {
            const travelerValue = JSON.stringify({
                type: traveler.traveler_type,
                email: traveler.traveler_email,
                name: traveler.traveler_name
            });
            
            const checkbox = document.querySelector(`input[type="checkbox"][value='${travelerValue}']`);
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
            document.getElementById('cost').value = expense.cost || '';
        }

        this.handleTravelModeChange();
    }

    resetModal() {
        this.editingIndex = -1;
        this.form.reset();
        
        // Uncheck all traveler checkboxes
        const checkboxes = document.querySelectorAll('#traveler-checkboxes input[type="checkbox"]');
        checkboxes.forEach(checkbox => checkbox.checked = false);
        
        this.handleTravelModeChange();
        
        // Clear any validation messages
        const errorMessages = this.modal.querySelectorAll('.text-danger');
        errorMessages.forEach(msg => msg.remove());
    }

    setDateConstraints() {
        const startDateField = document.getElementById('start_date');
        const endDateField = document.getElementById('end_date');
        const travelDateField = document.getElementById('travel_date');

        if (startDateField && endDateField && travelDateField) {
            const startDate = startDateField.value;
            const endDate = endDateField.value;

            if (startDate) {
                travelDateField.setAttribute('min', startDate);
            }
            if (endDate) {
                travelDateField.setAttribute('max', endDate);
            }
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

    validateForm() {
        const errors = [];
        
        // Travel date validation
        const travelDate = document.getElementById('travel_date').value;
        if (!travelDate) {
            errors.push('Travel date is required');
        } else {
            // Check if date is within training period
            const startDate = document.getElementById('start_date').value;
            const endDate = document.getElementById('end_date').value;
            
            if (startDate && travelDate < startDate) {
                errors.push('Travel date cannot be before training start date');
            }
            if (endDate && travelDate > endDate) {
                errors.push('Travel date cannot be after training end date');
            }
        }

        // Destination validation
        const destination = document.getElementById('destination').value.trim();
        if (!destination) {
            errors.push('Destination is required');
        }

        // Traveler validation (multiple selection)
        const selectedTravelers = document.querySelectorAll('#traveler-checkboxes input[type="checkbox"]:checked');
        if (selectedTravelers.length === 0) {
            errors.push('Please select at least one traveler');
        }

        // Travel mode validation
        const travelMode = document.querySelector('input[name="travel_mode"]:checked');
        if (!travelMode) {
            errors.push('Please select a travel mode');
        } else {
            if (travelMode.value === 'mileage') {
                const distance = document.getElementById('distance_km').value;
                if (!distance || parseFloat(distance) <= 0) {
                    errors.push('Distance in km is required for mileage expenses');
                }
            } else {
                const cost = document.getElementById('cost').value;
                if (!cost || parseFloat(cost) <= 0) {
                    errors.push('Cost is required for rail, bus, and flight expenses');
                }
            }
        }

        return errors;
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
            const travelerData = JSON.parse(checkbox.value);
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
            travelers: selectedTravelers,
            travel_mode: travelMode,
            cost: travelMode === 'mileage' ? null : parseFloat(document.getElementById('cost').value),
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

    showValidationErrors(errors) {
        // Clear existing error messages
        const existingErrors = this.modal.querySelectorAll('.validation-error');
        existingErrors.forEach(error => error.remove());

        // Show new errors
        const errorContainer = document.createElement('div');
        errorContainer.className = 'validation-error alert alert-danger';
        errorContainer.innerHTML = '<ul class="mb-0">' + 
            errors.map(error => `<li>${error}</li>`).join('') + 
            '</ul>';

        const modalBody = this.modal.querySelector('.modal-body');
        modalBody.insertBefore(errorContainer, modalBody.firstChild);
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