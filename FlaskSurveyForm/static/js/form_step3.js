document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('training-form');
    const traineesDataInput = document.getElementById('trainees_data');
    const attachmentContainer = document.getElementById('attachment-container');
    const addAttachmentBtn = document.getElementById('add-attachment-btn');

    // Initialize currency inputs if they exist
    if (typeof initializeCurrencyInputs === 'function') {
        initializeCurrencyInputs();
    }

    // Initialize attachments if container exists
    if (attachmentContainer && addAttachmentBtn) {
        addAttachmentBtn.addEventListener('click', function() {
            const attachmentGroup = document.createElement('div');
            attachmentGroup.className = 'attachment-group mb-3';
            attachmentGroup.innerHTML = `
                <div class="input-group">
                    <input type="file" class="form-control" name="attachments" accept=".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx">
                    <input type="text" class="form-control" name="attachment_descriptions[]" placeholder="Description">
                    <button type="button" class="btn btn-danger" onclick="this.parentElement.parentElement.remove()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            `;
            attachmentContainer.appendChild(attachmentGroup);
        });
    }

    // Form validation
    if (form) {
        form.addEventListener('submit', function(event) {
            console.log('[form_step3.js] Form submit event fired');
            // Log all form fields and their values
            Array.from(form.elements).forEach(el => {
                if (el.name) {
                    console.log(`[form_step3.js] Field '${el.name}':`, el.value, 'required:', el.required, 'valid:', el.validity.valid, 'validationMessage:', el.validationMessage);
                }
            });
            // Check if trainees are selected
            if (!traineesDataInput || !traineesDataInput.value) {
                console.warn('[form_step3.js] No trainees data, preventing submit');
                event.preventDefault();
                const message = document.createElement('div');
                message.className = 'alert alert-danger mt-2';
                message.textContent = 'Please add at least one trainee.';
                const traineeSection = document.querySelector('.trainee-section');
                if (traineeSection) {
                    traineeSection.parentNode.insertBefore(message, traineeSection.nextSibling);
                }
                return;
            }

            // Validate required fields
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('is-invalid');
                } else {
                    field.classList.remove('is-invalid');
                }
            });

            if (!isValid) {
                console.warn('[form_step3.js] Required fields missing, preventing submit');
                event.preventDefault();
                const message = document.createElement('div');
                message.className = 'alert alert-danger mt-2';
                message.textContent = 'Please fill in all required fields.';
                form.insertBefore(message, form.firstChild);
                return;
            }
            console.log('[form_step3.js] Form is valid, will submit');
        });
    }
}); 