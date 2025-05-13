document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('training-form');
    const trainingTypeCards = document.querySelectorAll('.training-type-card');
    const trainingTypeRadios = document.querySelectorAll('.training-type-radio');
    const locationTypeRadios = document.querySelectorAll('.location-type-radio');
    const locationDetailsContainer = document.getElementById('location-details-container');
    const locationDetailsInput = document.getElementById('location_details');

    // Function to update active card
    function updateActiveCard(selectedValue) {
        trainingTypeCards.forEach(card => {
            if (card.getAttribute('data-value') === selectedValue) {
                card.classList.add('active-card');
            } else {
                card.classList.remove('active-card');
            }
        });
    }

    // Set initial active card based on radio button
    const initialTrainingType = document.querySelector('.training-type-radio:checked');
    if (initialTrainingType) {
        updateActiveCard(initialTrainingType.value);
    }

    // Handle training type card selection
    trainingTypeCards.forEach(card => {
        card.addEventListener('click', function() {
            const value = this.getAttribute('data-value');
            const radio = document.querySelector(`.training-type-radio[value="${value}"]`);
            if (radio) {
                radio.checked = true;
                updateActiveCard(value);
            }
        });

        // Add keyboard support
        card.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.click();
            }
        });
    });

    // Handle radio button changes
    trainingTypeRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            updateActiveCard(this.value);
        });
    });

    // Handle location type change
    locationTypeRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            if (this.value === 'Offsite') {
                locationDetailsContainer.classList.remove('d-none');
                locationDetailsInput.required = true;
            } else {
                locationDetailsContainer.classList.add('d-none');
                locationDetailsInput.required = false;
            }
        });
    });

    // Form validation
    form.addEventListener('submit', function(event) {
        // Check if a training type is selected
        const selectedTrainingType = document.querySelector('.training-type-radio:checked');
        if (!selectedTrainingType) {
            event.preventDefault();
            const message = document.createElement('div');
            message.className = 'alert alert-danger mt-2';
            message.textContent = 'Please select a training type.';
            const cardGroup = document.getElementById('training-type-card-group');
            cardGroup.parentNode.insertBefore(message, cardGroup.nextSibling);
            return;
        }

        // Check if a location type is selected
        const selectedLocationType = document.querySelector('.location-type-radio:checked');
        if (!selectedLocationType) {
            event.preventDefault();
            const message = document.createElement('div');
            message.className = 'alert alert-danger mt-2';
            message.textContent = 'Please select a location type.';
            const locationGroup = document.querySelector('.form-group:has(.location-type-radio)');
            locationGroup.parentNode.insertBefore(message, locationGroup.nextSibling);
            return;
        }

        // If location is offsite, check location details
        if (selectedLocationType.value === 'Offsite' && !locationDetailsInput.value.trim()) {
            event.preventDefault();
            const message = document.createElement('div');
            message.className = 'alert alert-danger mt-2';
            message.textContent = 'Please provide location details for offsite training.';
            locationDetailsContainer.parentNode.insertBefore(message, locationDetailsContainer.nextSibling);
            return;
        }

        // If all validations pass, submit the form
        form.submit();
    });
}); 