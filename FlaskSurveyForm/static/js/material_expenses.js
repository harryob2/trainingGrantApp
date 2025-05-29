/**
 * Material Expenses Management
 * Handles modal interactions, validation, and data management for material expenses
 * 
 * Field Naming Convention:
 * - material_purchase_date: Purchase date for materials (vs. training dates)
 * - material_supplier_name: Supplier of materials (vs. training course supplier)
 * - material_invoice_number: Invoice number for material purchases (vs. course invoice_number)
 * - material_cost: Cost of materials (vs. course_cost for training)
 */

class MaterialExpensesManager {
    constructor() {
        this.materialExpenses = [];
        this.editingIndex = -1;
        this.modal = null;
        this.form = null;
        
        this.init();
    }

    init() {
        this.modal = document.getElementById('materialExpenseModal');
        this.form = document.getElementById('material-expense-form');
        
        if (!this.modal || !this.form) {
            console.error('Material expense modal or form not found');
            return;
        }

        this.setupEventListeners();
        this.loadExistingData();
        this.updateDisplay();
    }

    setupEventListeners() {
        // Add material expense button
        const addBtn = document.getElementById('add-material-expense-btn');
        if (addBtn) {
            addBtn.addEventListener('click', () => this.openModal());
        }

        // Modal save button
        const saveBtn = document.getElementById('save-material-expense-btn');
        if (saveBtn) {
            saveBtn.addEventListener('click', () => this.saveMaterialExpense());
        }

        // Modal reset on close
        if (this.modal) {
            this.modal.addEventListener('hidden.bs.modal', () => this.resetModal());
        }

        // Form submission handler to include material expenses data
        const mainForm = document.getElementById('training-form');
        if (mainForm) {
            mainForm.addEventListener('submit', () => this.prepareDataForSubmission());
        }

        // Dynamic error clearing for modal fields
        this.setupDynamicErrorClearing();
    }

    setupDynamicErrorClearing() {
        // Add error clearing functionality to all modal input fields
        const modalFields = [
            'material_purchase_date',
            'material_supplier_name', 
            'material_invoice_number',
            'material_cost'
        ];

        modalFields.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field) {
                // Clear errors on input (typing)
                field.addEventListener('input', () => {
                    this.clearFieldErrors(field);
                });
                
                // Clear errors on change (for date fields and when focus leaves)
                field.addEventListener('change', () => {
                    this.clearFieldErrors(field);
                });
            }
        });
    }

    clearFieldErrors(field) {
        // Get the current error container
        const errorContainer = this.modal.querySelector('.validation-error');
        if (!errorContainer) return; // No errors to clear
        
        // Determine which error message to remove based on the field
        const fieldId = field.id;
        let errorTextToRemove = '';
        
        switch(fieldId) {
            case 'material_purchase_date':
                errorTextToRemove = ['Purchase date is required', 'Purchase date cannot be before training start date', 'Purchase date cannot be after training end date'];
                break;
            case 'material_supplier_name':
                errorTextToRemove = ['Supplier name is required'];
                break;
            case 'material_invoice_number':
                errorTextToRemove = ['Invoice number is required'];
                break;
            case 'material_cost':
                errorTextToRemove = ['Material cost is required and must be greater than 0'];
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

    loadExistingData() {
        // Load existing material expenses (for edit mode)
        const existingDataField = document.getElementById('material_expenses_data');
        if (existingDataField && existingDataField.value) {
            try {
                this.materialExpenses = JSON.parse(existingDataField.value) || [];
            } catch (e) {
                console.error('Error parsing existing material expenses:', e);
                this.materialExpenses = [];
            }
        }
    }

    openModal(editIndex = -1) {
        this.editingIndex = editIndex;
        
        if (editIndex >= 0 && this.materialExpenses[editIndex]) {
            this.populateModalForEdit(this.materialExpenses[editIndex]);
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
        document.getElementById('material_purchase_date').value = expense.purchase_date;
        document.getElementById('material_supplier_name').value = expense.supplier_name;
        document.getElementById('material_invoice_number').value = expense.invoice_number;
        document.getElementById('material_cost').value = expense.material_cost;
    }

    resetModal() {
        this.editingIndex = -1;
        this.form.reset();
        
        // Clear any validation messages
        const errorMessages = this.modal.querySelectorAll('.text-danger, .validation-error');
        errorMessages.forEach(msg => msg.remove());

        // Clear any error styling from fields
        const allFields = ['material_purchase_date', 'material_supplier_name', 'material_invoice_number', 'material_cost'];
        allFields.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field) {
                field.classList.remove('is-invalid');
            }
        });
    }

    setDateConstraints() {
        const startDate = document.getElementById('start_date').value;
        const endDate = document.getElementById('end_date').value;
        const purchaseDateField = document.getElementById('material_purchase_date');
        
        if (startDate && endDate && purchaseDateField) {
            // Set min and max dates based on training period
            purchaseDateField.min = startDate;
            purchaseDateField.max = endDate;
        }
    }

    validateForm() {
        const errors = [];
        
        // Purchase date validation
        const purchaseDate = document.getElementById('material_purchase_date').value;
        if (!purchaseDate) {
            errors.push('Purchase date is required');
        } else {
            // Check if date is within training period
            const startDate = document.getElementById('start_date').value;
            const endDate = document.getElementById('end_date').value;
            
            if (startDate && purchaseDate < startDate) {
                errors.push('Purchase date cannot be before training start date');
            }
            if (endDate && purchaseDate > endDate) {
                errors.push('Purchase date cannot be after training end date');
            }
        }

        // Supplier name validation
        const supplierName = document.getElementById('material_supplier_name').value.trim();
        if (!supplierName) {
            errors.push('Supplier name is required');
        }

        // Invoice number validation
        const invoiceNumber = document.getElementById('material_invoice_number').value.trim();
        if (!invoiceNumber) {
            errors.push('Invoice number is required');
        }

        // Material cost validation
        const materialCost = document.getElementById('material_cost').value;
        if (!materialCost || parseFloat(materialCost) <= 0) {
            errors.push('Material cost is required and must be greater than 0');
        }

        return errors;
    }

    saveMaterialExpense() {
        const errors = this.validateForm();
        
        if (errors.length > 0) {
            this.showValidationErrors(errors);
            return;
        }

        const expense = {
            purchase_date: document.getElementById('material_purchase_date').value,
            supplier_name: document.getElementById('material_supplier_name').value.trim(),
            invoice_number: document.getElementById('material_invoice_number').value.trim(),
            material_cost: parseFloat(document.getElementById('material_cost').value)
        };

        // Add or update expense
        if (this.editingIndex >= 0) {
            this.materialExpenses[this.editingIndex] = expense;
        } else {
            this.materialExpenses.push(expense);
        }

        // Update display and close modal
        this.updateDisplay();
        const modalInstance = bootstrap.Modal.getInstance(this.modal);
        modalInstance.hide();
    }

    showValidationErrors(errors) {
        // Clear existing error messages first
        const existingErrors = this.modal.querySelectorAll('.validation-error');
        existingErrors.forEach(error => error.remove());

        // Show new errors at the top of the modal
        const errorContainer = document.createElement('div');
        errorContainer.className = 'validation-error alert alert-danger';
        errorContainer.innerHTML = '<ul class="mb-0">' + 
            errors.map(error => `<li>${error}</li>`).join('') + 
            '</ul>';

        const modalBody = this.modal.querySelector('.modal-body');
        modalBody.insertBefore(errorContainer, modalBody.firstChild);

        // Add error styling to specific fields
        this.highlightErrorFields(errors);
    }

    highlightErrorFields(errors) {
        // Clear all previous error styling first
        const allFields = ['material_purchase_date', 'material_supplier_name', 'material_invoice_number', 'material_cost'];
        allFields.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field) {
                field.classList.remove('is-invalid');
            }
        });

        // Add error styling to fields mentioned in current error messages
        errors.forEach(error => {
            if (error.includes('Purchase date')) {
                const field = document.getElementById('material_purchase_date');
                if (field) field.classList.add('is-invalid');
            }
            if (error.includes('Supplier name')) {
                const field = document.getElementById('material_supplier_name');
                if (field) field.classList.add('is-invalid');
            }
            if (error.includes('Invoice number')) {
                const field = document.getElementById('material_invoice_number');
                if (field) field.classList.add('is-invalid');
            }
            if (error.includes('Material cost')) {
                const field = document.getElementById('material_cost');
                if (field) field.classList.add('is-invalid');
            }
        });
    }

    updateErrorHighlighting() {
        // Get current error messages from the error container
        const errorContainer = this.modal.querySelector('.validation-error');
        if (!errorContainer) {
            // No errors, clear all highlighting
            const allFields = ['material_purchase_date', 'material_supplier_name', 'material_invoice_number', 'material_cost'];
            allFields.forEach(fieldId => {
                const field = document.getElementById(fieldId);
                if (field) field.classList.remove('is-invalid');
            });
            return;
        }

        const errorList = errorContainer.querySelector('ul');
        if (!errorList) return;

        const errorItems = errorList.querySelectorAll('li');
        const currentErrors = Array.from(errorItems).map(item => item.textContent.trim());
        
        // Update highlighting based on current errors
        this.highlightErrorFields(currentErrors);
    }

    deleteMaterialExpense(index) {
        if (confirm('Are you sure you want to delete this material expense?')) {
            this.materialExpenses.splice(index, 1);
            this.updateDisplay();
        }
    }

    updateDisplay() {
        const container = document.getElementById('material-expenses-list');
        const emptyMessage = document.getElementById('no-material-expenses-message');
        
        if (!container) return;

        if (this.materialExpenses.length === 0) {
            container.innerHTML = '';
            if (emptyMessage) emptyMessage.style.display = 'block';
        } else {
            if (emptyMessage) emptyMessage.style.display = 'none';
            container.innerHTML = this.generateExpensesTable();
        }

        // Dispatch event to notify other components that material expenses have been updated
        document.dispatchEvent(new CustomEvent('materialExpensesUpdated'));
    }

    generateExpensesTable() {
        const table = `
            <div class="table-responsive">
                <table class="table table-bordered table-hover">
                    <thead class="table-light">
                        <tr>
                            <th>Purchase Date</th>
                            <th>Supplier</th>
                            <th>Invoice Number</th>
                            <th>Cost (excl. VAT)</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${this.materialExpenses.map((expense, index) => this.generateExpenseRow(expense, index)).join('')}
                    </tbody>
                </table>
            </div>
        `;
        return table;
    }

    generateExpenseRow(expense, index) {
        const formattedDate = new Date(expense.purchase_date).toLocaleDateString();

        return `
            <tr>
                <td>${formattedDate}</td>
                <td>${expense.supplier_name}</td>
                <td>${expense.invoice_number}</td>
                <td>€${expense.material_cost.toFixed(2)}</td>
                <td>
                    <button type="button" class="btn btn-sm btn-outline-primary me-1" 
                            onclick="materialExpensesManager.openModal(${index})" title="Edit">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button type="button" class="btn btn-sm btn-outline-danger" 
                            onclick="materialExpensesManager.deleteMaterialExpense(${index})" title="Delete">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    }

    prepareDataForSubmission() {
        // Create or update hidden field with material expenses data
        let hiddenField = document.getElementById('material_expenses_data');
        if (!hiddenField) {
            hiddenField = document.createElement('input');
            hiddenField.type = 'hidden';
            hiddenField.id = 'material_expenses_data';
            hiddenField.name = 'material_expenses_data';
            document.getElementById('training-form').appendChild(hiddenField);
        }
        
        hiddenField.value = JSON.stringify(this.materialExpenses);
    }

    refreshData() {
        this.loadExistingData();
        this.updateDisplay();
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize if we're on a page with the material expenses section
    if (document.getElementById('material-expenses-section')) {
        window.materialExpensesManager = new MaterialExpensesManager();
    }
}); 