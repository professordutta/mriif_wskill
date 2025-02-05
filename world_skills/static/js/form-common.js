class FormHandler {
    constructor(formId, config) {
        this.formState = {
            currentStep: 1,
            totalSteps: config.totalSteps || 3,
            form: document.getElementById(formId),
            validationRules: config.validationRules,
            messages: {
                minLength: field => `${field} must be at least ${config.validationRules[field].minLength} characters long`,
                pattern: config.patternMessages,
                required: field => `${field.replace('_', ' ')} is required`,
                min: field => `${field.replace('_', ' ')} must be at least ${config.validationRules[field].min}`,
                max: field => `${field.replace('_', ' ')} must not exceed ${config.validationRules[field].max}`
            },
            stepFields: config.stepFields,
            onUpdate: config.onUpdate || (() => {})
        };
        // Add validation state tracking
        this.validationInProgress = false;
        this.errorMessages = new Set();
        this.initializeForm();
    }

    showCustomAlert(message) {
        const alertEl = document.getElementById('custom-alert');
        const alertBox = alertEl.querySelector('div[class*="bg-white"]');
        const messageEl = document.getElementById('alert-message');
        messageEl.textContent = message;
        alertEl.classList.remove('hidden');
        setTimeout(() => {
            alertBox.classList.remove('scale-95', 'opacity-0');
            alertBox.classList.add('scale-100', 'opacity-100');
        }, 50);
    }

    hideCustomAlert() {
        const alertEl = document.getElementById('custom-alert');
        const alertBox = alertEl.querySelector('div[class*="bg-white"]');
        alertBox.classList.remove('scale-100', 'opacity-100');
        alertBox.classList.add('scale-95', 'opacity-0');
        setTimeout(() => {
            alertEl.classList.add('hidden');
        }, 300);
    }

    validateStep(step) {
        if (this.validationInProgress) return true;
        this.validationInProgress = true;
        
        let isValid = true;
        this.errorMessages.clear();
        this.clearValidationErrors();
        
        const fields = this.formState.stepFields[step];

        for (const fieldName of fields) {
            const input = this.formState.form.querySelector(`[name="${fieldName}"]`);
            if (!input) continue;

            input.setAttribute('tabindex', '0');
            const value = input.type === 'file' ? input.files[0] : input.value.trim();
            const rules = this.formState.validationRules[fieldName];

            if (!this.validateField(input, rules, value)) {
                isValid = false;
                if (!input.getAttribute('data-focused')) {
                    input.focus();
                    input.setAttribute('data-focused', 'true');
                }
            }
        }

        if (!isValid && this.errorMessages.size > 0) {
            // Show only unique error messages
            this.showCustomAlert([...this.errorMessages][0]);
        }

        this.validationInProgress = false;
        return isValid;
    }

    validateField(input, rules, value) {
        if (!rules) return true;

        // Remove existing error for this field
        this.removeFieldError(input);

        if (rules.required && !value) {
            const message = this.formState.messages.required(input.name);
            this.errorMessages.add(message);
            this.showFieldError(input, message);
            return false;
        }

        if (rules.minLength && value.length < rules.minLength) {
            const message = this.formState.messages.minLength(input.name);
            this.errorMessages.add(message);
            this.showFieldError(input, message);
            return false;
        }

        if (rules.pattern && !rules.pattern.test(value)) {
            const message = this.formState.messages.pattern[input.name];
            this.errorMessages.add(message);
            this.showFieldError(input, message);
            return false;
        }

        // Add numeric validation with messages
        if ((rules.min !== undefined || rules.max !== undefined) && value !== '') {
            const numValue = Number(value);
            if (isNaN(numValue)) {
                const message = `${input.name.replace('_', ' ')} must be a number`;
                this.errorMessages.add(message);
                this.showFieldError(input, message);
                return false;
            }
            if (rules.min !== undefined && numValue < rules.min) {
                const message = this.formState.messages.min(input.name);
                this.errorMessages.add(message);
                this.showFieldError(input, message);
                return false;
            }
            if (rules.max !== undefined && numValue > rules.max) {
                const message = this.formState.messages.max(input.name);
                this.errorMessages.add(message);
                this.showFieldError(input, message);
                return false;
            }
        }

        input.classList.remove('border-gray-300', 'border-red-500');
        input.classList.add('border-green-500');
        return true;
    }

    showFieldError(input, message) {
        input.classList.remove('border-gray-300', 'border-green-500');
        input.classList.add('border-red-500');

        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message text-red-500 text-sm mt-1';
        errorDiv.textContent = message;
        input.parentElement.appendChild(errorDiv);
    }

    removeFieldError(input) {
        const errorDiv = input.parentElement.querySelector('.error-message');
        if (errorDiv) {
            errorDiv.remove();
        }
        input.classList.remove('border-red-500');
    }

    clearValidationErrors() {
        document.querySelectorAll('.error-message').forEach(el => el.remove());
        document.querySelectorAll('.border-red-500').forEach(el => {
            el.classList.remove('border-red-500');
            el.classList.add('border-gray-300');
        });
        document.querySelectorAll('[data-focused]').forEach(el => {
            el.removeAttribute('data-focused');
        });
    }

    updateStepIndicators() {
        const steps = document.querySelectorAll('.relative.pl-12');
        const lines = document.querySelectorAll('.absolute.left-4 .bg-green-500');
        
        steps.forEach((step, index) => {
            const circle = step.querySelector('.w-8');
            const number = step.querySelector('.font-semibold');
            const title = step.querySelector('h4');
            const line = lines[index];

            this.updateStepUI(circle, number, title, line, index + 1);
        });

        this.updateNavigationButtons();
    }

    updateStepUI(circle, number, title, line, stepNumber) {
        circle.className = 'w-8 h-8 rounded-full flex items-center justify-center transition-all duration-300';
        number.className = 'font-semibold';
        title.className = 'text-sm font-semibold transition-colors duration-300';

        if (stepNumber === this.formState.currentStep) {
            circle.classList.add('bg-gradient-to-r', 'from-yellow-400', 'to-yellow-600', 'shadow-lg', 'shadow-yellow-200');
            number.classList.add('text-white');
            title.classList.add('text-yellow-600');
            if (line) line.style.height = '0%';
        } else if (stepNumber < this.formState.currentStep) {
            circle.classList.add('bg-gradient-to-r', 'from-green-400', 'to-green-600', 'shadow-lg', 'shadow-green-200');
            number.classList.add('text-white');
            title.classList.add('text-green-600');
            if (line) line.style.height = '100%';
        } else {
            circle.classList.add('bg-gray-200');
            number.classList.add('text-gray-600');
            title.classList.add('text-gray-600');
            if (line) line.style.height = '0%';
        }

        if (line) {
            line.style.transition = 'height 0.3s ease-in-out';
        }
    }

    updateNavigationButtons() {
        const prevButton = document.getElementById('prev-step');
        const nextButton = document.getElementById('next-step');
        const submitSection = document.getElementById('submit-section');

        prevButton.disabled = this.formState.currentStep === 1;
        nextButton.style.display = this.formState.currentStep === this.formState.totalSteps ? 'none' : 'flex';
        submitSection.classList.toggle('hidden', this.formState.currentStep !== this.formState.totalSteps);
    }

    showStep(step) {
        if (step > this.formState.currentStep && !this.validateStep(this.formState.currentStep)) {
            return false;
        }

        document.querySelectorAll('.form-step').forEach(el => {
            el.classList.add('hidden');
        });

        const targetStep = document.getElementById(`step-${step}`);
        targetStep.classList.remove('hidden');
        
        targetStep.classList.add('opacity-0');
        setTimeout(() => {
            targetStep.classList.remove('opacity-0');
        }, 50);

        this.formState.currentStep = step;
        this.updateStepIndicators();
        this.updateProgress();
        
        return true;
    }

    updateProgress() {
        const totalFields = Object.values(this.formState.stepFields).flat().length;
        let completedFields = 0;

        Object.values(this.formState.stepFields).flat().forEach(fieldName => {
            const input = this.formState.form.querySelector(`[name="${fieldName}"]`);
            if (input && this.isFieldComplete(input)) {
                completedFields++;
            }
        });

        const percentage = Math.round((completedFields / totalFields) * 100);
        this.updateProgressUI(percentage, completedFields, totalFields);
    }

    isFieldComplete(input) {
        if (input.type === 'checkbox') return input.checked;
        if (input.type === 'file') return input.files && input.files.length > 0;
        return input.value && input.checkValidity();
    }

    updateProgressUI(percentage, completed, total) {
        document.getElementById('progress-bar').style.width = `${percentage}%`;
        document.getElementById('progress-percentage').textContent = `${percentage}%`;
        document.getElementById('fields-completed').textContent = completed;
        document.getElementById('total-fields').textContent = total;
    }

    initializeForm() {
        this.initializeEventListeners();
        this.showStep(1);
        this.updateProgress();
        this.initializeFileUpload();
    }

    handleInput(e) {
        if (!e.target.matches('input, select, textarea')) return;
        
        const input = e.target;
        const rules = this.formState.validationRules[input.name];
        
        if (rules) {
            // Debounce validation on input
            clearTimeout(input.validateTimeout);
            input.validateTimeout = setTimeout(() => {
                this.validateField(input, rules, input.value.trim());
                this.updateProgress();
            }, 300);
        }
    }

    handleBlur(e) {
        if (!e.target.matches('input, select, textarea')) return;
        
        const input = e.target;
        const rules = this.formState.validationRules[input.name];
        if (rules) {
            // Clear any pending input validation
            clearTimeout(input.validateTimeout);
            this.validateField(input, rules, input.value.trim());
        }
    }

    initializeEventListeners() {
        // Remove any existing listeners first
        const form = this.formState.form;
        const newForm = form.cloneNode(true);
        form.parentNode.replaceChild(newForm, form);
        this.formState.form = newForm;

        // Add listeners
        document.getElementById('close-alert').addEventListener('click', () => this.hideCustomAlert());
        
        document.getElementById('next-step').addEventListener('click', () => {
            if (this.formState.currentStep < this.formState.totalSteps) {
                this.showStep(this.formState.currentStep + 1);
            }
        });

        document.getElementById('prev-step').addEventListener('click', () => {
            if (this.formState.currentStep > 1) {
                this.showStep(this.formState.currentStep - 1);
            }
        });

        // Prevent form submission on Enter key
        this.formState.form.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                // Allow Enter key for textarea elements
                if (e.target.tagName.toLowerCase() !== 'textarea') {
                    return false;
                }
            }
        });

        this.formState.form.addEventListener('submit', (e) => this.handleSubmit(e));
        this.formState.form.addEventListener('input', (e) => this.handleInput(e));
        this.formState.form.addEventListener('blur', (e) => this.handleBlur(e), true);
    }

    handleSubmit(e) {
        e.preventDefault();

        for (let i = 1; i <= this.formState.totalSteps; i++) {
            if (!this.validateStep(i)) {
                this.showStep(i);
                return;
            }
        }

        const submitButton = e.target.querySelector('button[type="submit"]');
        this.updateSubmitButtonState(submitButton, true);
        e.target.submit();
    }

    updateSubmitButtonState(button, disabled) {
        button.disabled = disabled;
        button.innerHTML = disabled ? `
            <svg class="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
            </svg>
            Processing...
        ` : 'Submit';
    }

    initializeFileUpload() {
        const fileInput = document.getElementById('file-upload');
        if (!fileInput) return;

        const dropZone = fileInput.parentElement;
        this.setupFileDragAndDrop(dropZone, fileInput);
        this.setupFileInputAccessibility(fileInput, dropZone);

        // Reset file input on page load
        fileInput.value = '';
        const fileNameDiv = document.getElementById('file-name');
        if (fileNameDiv) {
            fileNameDiv.classList.add('hidden');
        }
    }

    setupFileDragAndDrop(dropZone, fileInput) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
            }, false);
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => {
                dropZone.classList.add('border-yellow-500', 'bg-yellow-50');
                this.showDragHelper(dropZone);
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => {
                dropZone.classList.remove('border-yellow-500', 'bg-yellow-50');
                this.removeDragHelper(dropZone);
            }, false);
        });

        dropZone.addEventListener('drop', (e) => {
            const file = e.dataTransfer.files[0];
            if (file) {
                this.validateAndProcessFile(file, fileInput);
            }
        }, false);

        fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                this.validateAndProcessFile(file, fileInput);
            } else {
                const fileNameDiv = document.getElementById('file-name');
                fileNameDiv.classList.add('hidden');
            }
        });
    }

    showDragHelper(dropZone) {
        // Remove existing helper if any
        this.removeDragHelper(dropZone);
        
        const helperText = document.createElement('div');
        helperText.id = 'drag-helper';
        helperText.className = 'absolute inset-0 flex flex-col items-center justify-center bg-yellow-50/90 text-yellow-700 font-medium';
        helperText.innerHTML = `
            <p class="mb-1">Drop your file here</p>
            <p class="text-xs text-yellow-600">Allowed: PDF, DOC, DOCX (max 5MB)</p>
        `;
        dropZone.appendChild(helperText);
    }

    removeDragHelper(dropZone) {
        const helperText = dropZone.querySelector('#drag-helper');
        if (helperText) {
            helperText.remove();
        }
    }

    validateAndProcessFile(file, fileInput) {
        const validExtensions = ['.pdf', '.doc', '.docx'];
        const maxSize = 5 * 1024 * 1024; // 5MB
        const fileNameDiv = document.getElementById('file-name');
        const fileNameSpan = fileNameDiv.querySelector('span');

        if (!this.validateFileExtension(file, validExtensions)) {
            fileInput.value = '';
            fileNameDiv.classList.add('hidden');
            return false;
        }

        if (!this.validateFileSize(file, maxSize)) {
            fileInput.value = '';
            fileNameDiv.classList.add('hidden');
            return false;
        }

        // Create a new FileList object
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);
        fileInput.files = dataTransfer.files;

        // Update file name display
        fileNameSpan.textContent = file.name;
        fileNameDiv.classList.remove('hidden');
        
        this.updateProgress();
        return true;
    }

    validateFileExtension(file, validExtensions) {
        const fileName = file.name.toLowerCase();
        const isValid = validExtensions.some(ext => fileName.endsWith(ext));
        
        if (!isValid) {
            this.showCustomAlert('Only PDF and Word documents (.pdf, .doc, .docx) are allowed');
        }
        return isValid;
    }

    validateFileSize(file, maxSize) {
        const isValid = file.size <= maxSize;
        
        if (!isValid) {
            this.showCustomAlert(`File size must not exceed 5MB. Current size: ${(file.size / (1024 * 1024)).toFixed(2)}MB`);
        }
        return isValid;
    }

    setupFileInputAccessibility(fileInput, dropZone) {
        fileInput.addEventListener('focus', () => {
            dropZone.classList.add('ring-2', 'ring-yellow-500');
        });

        fileInput.addEventListener('blur', () => {
            dropZone.classList.remove('ring-2', 'ring-yellow-500');
        });

        fileInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                fileInput.click();
            }
        });
    }
}
