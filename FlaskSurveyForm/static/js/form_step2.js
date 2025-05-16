document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    const trainerNameInput = document.getElementById('trainer_name');
    const supplierNameInput = document.getElementById('supplier_name');
    const startDateInput = document.getElementById('start_date');
    const endDateInput = document.getElementById('end_date');
    const expenseInputs = document.querySelectorAll('.expense-input');
    const concurClaimInput = document.getElementById('concur_claim');
    const concurClaimGroup = document.getElementById('concur_claim_group');

    // Initialize date pickers
    if (startDateInput && endDateInput) {
        flatpickr(startDateInput, {
            dateFormat: "Y-m-d",
            maxDate: "today",
            onChange: function(selectedDates) {
                endDateInput._flatpickr.set('minDate', selectedDates[0]);
            }
        });

        flatpickr(endDateInput, {
            dateFormat: "Y-m-d",
            maxDate: "today"
        });
    }

    // Handle expense inputs
    expenseInputs.forEach(input => {
        input.addEventListener('input', function() {
            const hasExpenses = Array.from(expenseInputs).some(input => input.value && parseFloat(input.value) > 0);
            if (hasExpenses) {
                concurClaimGroup.classList.remove('d-none');
                concurClaimInput.required = true;
            } else {
                concurClaimGroup.classList.add('d-none');
                concurClaimInput.required = false;
            }
        });
    });

    // Form validation
    form.addEventListener('submit', function(event) {
        if (!form.checkValidity()) {
            event.preventDefault();
            event.stopPropagation();
        }

        // Validate dates
        const startDate = new Date(startDateInput.value);
        const endDate = new Date(endDateInput.value);
        if (endDate < startDate) {
            event.preventDefault();
            endDateInput.setCustomValidity('End date must be after start date');
        } else {
            endDateInput.setCustomValidity('');
        }

        form.classList.add('was-validated');
    });

    // Clear validation on input
    form.querySelectorAll('input').forEach(input => {
        input.addEventListener('input', function() {
            input.setCustomValidity('');
        });
    });
}); 