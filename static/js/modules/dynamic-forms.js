/**
 * Dynamic Forms Client-Side Handler
 * Handles form validation and submission for dynamic form fields
 */

class DynamicFormHandler {
    constructor(formElement) {
        this.form = formElement;
        this.dynamicFields = {};
        this.init();
    }
    
    init() {
        this.collectDynamicFields();
        this.attachValidation();
        console.log('Dynamic Form Handler initialized with', Object.keys(this.dynamicFields).length, 'fields');
    }
    
    collectDynamicFields() {
        // Collect all fields with df_ prefix
        const inputs = this.form.querySelectorAll('[name^="df_"]');
        inputs.forEach(input => {
            this.dynamicFields[input.name] = input;
        });
    }
    
    attachValidation() {
        Object.values(this.dynamicFields).forEach(field => {
            field.addEventListener('blur', () => this.validateField(field));
            field.addEventListener('input', () => this.clearError(field));
        });
    }
    
    validateField(field) {
        // Client-side validation logic
        const isRequired = field.hasAttribute('required');
        const value = this.getFieldValue(field);
        
        if (isRequired && !value) {
            this.showError(field, 'This field is required');
            return false;
        }
        
        // Type-specific validation
        const fieldType = field.type;
        
        if (fieldType === 'email' && value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                this.showError(field, 'Please enter a valid email address');
                return false;
            }
        }
        
        if (fieldType === 'url' && value) {
            try {
                new URL(value);
            } catch {
                this.showError(field, 'Please enter a valid URL');
                return false;
            }
        }
        
        if (fieldType === 'number' && value) {
            const min = field.getAttribute('min');
            const max = field.getAttribute('max');
            const numValue = parseFloat(value);
            
            if (min !== null && numValue < parseFloat(min)) {
                this.showError(field, `Value must be at least ${min}`);
                return false;
            }
            
            if (max !== null && numValue > parseFloat(max)) {
                this.showError(field, `Value must be at most ${max}`);
                return false;
            }
        }
        
        if (field.hasAttribute('maxlength') && value.length > parseInt(field.getAttribute('maxlength'))) {
            this.showError(field, `Maximum length is ${field.getAttribute('maxlength')} characters`);
            return false;
        }
        
        this.clearError(field);
        return true;
    }
    
    getFieldValue(field) {
        if (field.type === 'checkbox') {
            return field.checked;
        } else if (field.type === 'select-multiple') {
            return Array.from(field.selectedOptions).map(opt => opt.value);
        } else {
            return field.value.trim();
        }
    }
    
    showError(field, message) {
        const errorEl = document.getElementById(`${field.id}_error`);
        if (errorEl) {
            errorEl.textContent = message;
            errorEl.style.display = 'block';
        }
        field.classList.add('is-invalid');
    }
    
    clearError(field) {
        const errorEl = document.getElementById(`${field.id}_error`);
        if (errorEl) {
            errorEl.textContent = '';
            errorEl.style.display = 'none';
        }
        field.classList.remove('is-invalid');
    }
    
    validateAll() {
        let isValid = true;
        let firstInvalidField = null;
        
        Object.values(this.dynamicFields).forEach(field => {
            if (!this.validateField(field)) {
                isValid = false;
                if (!firstInvalidField) {
                    firstInvalidField = field;
                }
            }
        });
        
        // Scroll to first invalid field
        if (firstInvalidField) {
            firstInvalidField.scrollIntoView({ behavior: 'smooth', block: 'center' });
            firstInvalidField.focus();
        }
        
        return isValid;
    }
    
    getFormData() {
        const data = {};
        Object.entries(this.dynamicFields).forEach(([name, field]) => {
            data[name] = this.getFieldValue(field);
        });
        return data;
    }
    
    clearAll() {
        Object.values(this.dynamicFields).forEach(field => {
            if (field.type === 'checkbox') {
                field.checked = false;
            } else if (field.type === 'select-multiple') {
                Array.from(field.options).forEach(opt => opt.selected = false);
            } else {
                field.value = '';
            }
            this.clearError(field);
        });
    }
    
    setFormData(data) {
        Object.entries(data).forEach(([key, value]) => {
            const fieldName = key.startsWith('df_') ? key : `df_${key}`;
            const field = this.dynamicFields[fieldName];
            
            if (!field) return;
            
            if (field.type === 'checkbox') {
                field.checked = !!value;
            } else if (field.type === 'select-multiple') {
                const values = Array.isArray(value) ? value : [value];
                Array.from(field.options).forEach(opt => {
                    opt.selected = values.includes(opt.value);
                });
            } else {
                field.value = value;
            }
        });
    }
}

// Auto-initialize if form exists on page
document.addEventListener('DOMContentLoaded', function() {
    const applicationForm = document.getElementById('applicationForm');
    if (applicationForm) {
        // Check if dynamic fields exist
        const hasDynamicFields = applicationForm.querySelector('[name^="df_"]');
        
        if (hasDynamicFields) {
            window.dynamicFormHandler = new DynamicFormHandler(applicationForm);
            console.log('✅ Dynamic Form Handler ready');
            
            // Add validation to form submission
            applicationForm.addEventListener('submit', function(e) {
                if (window.dynamicFormHandler && !window.dynamicFormHandler.validateAll()) {
                    e.preventDefault();
                    console.warn('Dynamic form validation failed');
                    return false;
                }
            });
        }
    }
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DynamicFormHandler;
}

