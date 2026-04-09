/**
 * Enhanced Form Builder
 * Custom form builder UI for django-dynforms
 */

class FormBuilder {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.options = {
            apiUrl: options.apiUrl || '/api/application-forms/',
            saveUrl: options.saveUrl || '/api/application-forms/form-types/',
            ...options
        };
        
        this.fields = [];
        this.selectedField = null;
        this.sortableInstance = null;
        
        this.init();
    }
    
    init() {
        if (!this.container) {
            console.error('FormBuilder: Container not found');
            return;
        }
        
        // Ensure DOM is ready before rendering
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                this.render();
                this.attachEventListeners();
                this.initializeSortable();
            });
        } else {
            // DOM already ready
            this.render();
            // Use setTimeout to ensure render() completes before attaching listeners
            setTimeout(() => {
                this.attachEventListeners();
                this.initializeSortable();
            }, 50);
        }
    }
    
    render() {
        this.container.innerHTML = `
            <div class="form-builder-container">
                <div class="field-palette" id="field-palette">
                    <h3><i class="bi bi-grid-3x3-gap"></i> Field Types</h3>
                    <div id="field-types-list"></div>
                </div>
                
                <div class="builder-canvas">
                    <div class="builder-toolbar">
                        <h2><i class="bi bi-file-earmark-text"></i> Form Builder</h2>
                        <div class="builder-actions">
                            <button type="button" class="btn btn-outline-secondary btn-sm" id="btn-apply-step-template" title="Merge a reusable step template into this form">
                                <i class="bi bi-layers"></i> Step template
                            </button>
                            <button class="btn btn-outline-secondary btn-sm" id="btn-preview">
                                <i class="bi bi-eye"></i> Preview
                            </button>
                            <button class="btn btn-outline-primary btn-sm" id="btn-save">
                                <i class="bi bi-save"></i> Save Form
                            </button>
                        </div>
                    </div>
                    
                    <div class="form-fields-area" id="form-fields-area">
                        <div class="empty-form-state" id="empty-state">
                            <i class="bi bi-inbox"></i>
                            <p>No fields yet</p>
                            <small>Drag fields from the sidebar to start building</small>
                        </div>
                    </div>
                </div>
                
                <div class="preview-panel" id="preview-panel" style="display: none;">
                    <h3><i class="bi bi-eye"></i> Preview</h3>
                    <div class="preview-form" id="preview-form"></div>
                </div>
            </div>
        `;
        
        this.renderFieldTypes();
    }
    
    renderFieldTypes() {
        const fieldTypes = [
            { type: 'text', name: 'Text Input', icon: 'bi-textarea-resize', desc: 'Single line text' },
            { type: 'textarea', name: 'Textarea', icon: 'bi-textarea-t', desc: 'Multi-line text' },
            { type: 'email', name: 'Email', icon: 'bi-envelope', desc: 'Email address' },
            { type: 'number', name: 'Number', icon: 'bi-123', desc: 'Numeric input' },
            { type: 'date', name: 'Date', icon: 'bi-calendar', desc: 'Date picker' },
            { type: 'select', name: 'Select', icon: 'bi-list-ul', desc: 'Dropdown menu' },
            { type: 'checkbox', name: 'Checkbox', icon: 'bi-check-square', desc: 'Checkbox' },
            { type: 'radio', name: 'Radio', icon: 'bi-circle', desc: 'Radio buttons' },
            { type: 'file', name: 'File Upload', icon: 'bi-upload', desc: 'File upload' },
        ];
        
        const list = document.getElementById('field-types-list');
        list.innerHTML = fieldTypes.map(field => `
            <div class="field-type-item" data-type="${field.type}" draggable="true">
                <i class="bi ${field.icon}"></i>
                <div>
                    <div class="field-name">${field.name}</div>
                    <div class="field-desc">${field.desc}</div>
                </div>
            </div>
        `).join('');
    }
    
    attachEventListeners() {
        // Use setTimeout to ensure DOM is ready
        setTimeout(() => {
            // Field type drag
            const fieldItems = document.querySelectorAll('.field-type-item');
            if (fieldItems.length === 0) {
                console.warn('FormBuilder: No field type items found');
                return;
            }
            
            fieldItems.forEach(item => {
                item.addEventListener('dragstart', (e) => {
                    e.dataTransfer.setData('text/plain', e.currentTarget.dataset.type);
                });
            });
            
            // Form area drop
            const formArea = document.getElementById('form-fields-area');
            if (!formArea) {
                console.error('FormBuilder: form-fields-area not found');
                return;
            }
            
            formArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                formArea.classList.add('drag-over');
            });
            
            formArea.addEventListener('dragleave', () => {
                formArea.classList.remove('drag-over');
            });
            
            formArea.addEventListener('drop', (e) => {
                e.preventDefault();
                formArea.classList.remove('drag-over');
                
                const fieldType = e.dataTransfer.getData('text/plain');
                if (fieldType) {
                    this.addField(fieldType);
                }
            });
            
            // Buttons
            const btnSave = document.getElementById('btn-save');
            const btnPreview = document.getElementById('btn-preview');
            const btnSaveFieldConfig = document.getElementById('btnSaveFieldConfig');
            const btnAddOption = document.getElementById('btnAddOption');
            const fieldConfigModal = document.getElementById('fieldConfigModal');
            
            if (btnSave) {
                btnSave.addEventListener('click', () => this.saveForm());
            } else {
                console.error('FormBuilder: btn-save not found');
            }
            
            if (btnPreview) {
                btnPreview.addEventListener('click', () => this.togglePreview());
            } else {
                console.error('FormBuilder: btn-preview not found');
            }

            const btnApplyTpl = document.getElementById('btn-apply-step-template');
            if (btnApplyTpl) {
                btnApplyTpl.addEventListener('click', () => this.openStepTemplateModal());
            }

            const btnConfirmApplyTpl = document.getElementById('btnConfirmApplyStepTemplate');
            if (btnConfirmApplyTpl) {
                btnConfirmApplyTpl.addEventListener('click', () => this.applyStepTemplateFromModal());
            }
            
            if (btnSaveFieldConfig) {
                btnSaveFieldConfig.addEventListener('click', () => this.saveFieldConfig());
            } else {
                console.error('FormBuilder: btnSaveFieldConfig not found');
            }
            
            if (btnAddOption) {
                btnAddOption.addEventListener('click', () => this.addFieldOption());
            } else {
                console.error('FormBuilder: btnAddOption not found');
            }
            
            // Modal cleanup
            if (fieldConfigModal) {
                fieldConfigModal.addEventListener('hidden.bs.modal', () => {
                    this.selectedField = null;
                });
            } else {
                console.error('FormBuilder: fieldConfigModal not found');
            }
        }, 50);
    }
    
    addFieldOption() {
        const container = document.getElementById('fieldOptionsList');
        const index = container.children.length;
        const optionHtml = `
            <div class="input-group mb-2 option-item" data-option-index="${index}">
                <input type="text" class="form-control option-value" placeholder="Option value">
                <input type="text" class="form-control option-label" placeholder="Option label">
                <button type="button" class="btn btn-outline-danger btn-remove-option">
                    <i class="bi bi-trash"></i>
                </button>
            </div>
        `;
        container.insertAdjacentHTML('beforeend', optionHtml);
        
        // Add remove handler
        const newItem = container.lastElementChild;
        newItem.querySelector('.btn-remove-option').addEventListener('click', (e) => {
            e.currentTarget.closest('.option-item').remove();
        });
    }
    
    initializeSortable() {
        const formArea = document.getElementById('form-fields-area');
        
        if (typeof Sortable !== 'undefined') {
            this.sortableInstance = new Sortable(formArea, {
                animation: 150,
                handle: '.field-header',
                ghostClass: 'dragging',
                dragClass: 'drag-over',
                onEnd: (evt) => {
                    // Reorder fields array based on new DOM order
                    const newOrder = Array.from(formArea.querySelectorAll('.form-field-item'))
                        .map(item => item.dataset.fieldId);
                    
                    this.fields.sort((a, b) => {
                        const aIndex = newOrder.indexOf(a.id);
                        const bIndex = newOrder.indexOf(b.id);
                        return aIndex - bIndex;
                    });
                }
            });
        } else {
            console.warn('SortableJS not loaded, field reordering disabled');
        }
    }
    
    addField(type) {
        // Ensure DOM elements exist before proceeding
        const area = document.getElementById('form-fields-area');
        if (!area) {
            console.error('FormBuilder: form-fields-area not found, cannot add field');
            return;
        }
        
        const field = {
            id: 'field_' + Date.now(),
            type: type,
            label: this.getDefaultLabel(type),
            required: false,
            placeholder: '',
            helpText: '',
            options: (type === 'select' || type === 'radio') ? [{ value: 'option1', label: 'Option 1' }] : null
        };
        
        this.fields.push(field);
        this.renderFields();
        this.hideEmptyState();
        
        // Auto-open config modal for new fields
        setTimeout(() => {
            this.editField(field.id);
        }, 100);
    }
    
    getDefaultLabel(type) {
        const labels = {
            'text': 'Text Field',
            'textarea': 'Textarea',
            'email': 'Email Address',
            'number': 'Number',
            'date': 'Date',
            'select': 'Select Option',
            'checkbox': 'Checkbox',
            'radio': 'Radio Buttons',
            'file': 'File Upload'
        };
        return labels[type] || 'Field';
    }
    
    renderFields() {
        const area = document.getElementById('form-fields-area');
        const emptyState = document.getElementById('empty-state');
        
        if (!area) {
            console.error('FormBuilder: form-fields-area not found');
            return;
        }
        
        if (this.fields.length === 0) {
            if (emptyState) {
                emptyState.style.display = 'block';
            }
            return;
        }
        
        if (emptyState) {
            emptyState.style.display = 'none';
        }
        
        area.innerHTML = this.fields.map((field, index) => `
            <div class="form-field-item" data-field-id="${field.id}">
                <div class="field-header">
                    <span class="field-label">${field.label || 'Untitled Field'}</span>
                    <div class="field-actions">
                        <button class="btn-edit" data-field-id="${field.id}">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn-delete" data-field-id="${field.id}">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </div>
                <div class="field-preview">
                    ${this.renderFieldPreview(field)}
                </div>
            </div>
        `).join('');
        
        // Attach edit/delete handlers
        area.querySelectorAll('.btn-edit').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const fieldId = e.currentTarget.dataset.fieldId;
                this.editField(fieldId);
            });
        });
        
        area.querySelectorAll('.btn-delete').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const fieldId = e.currentTarget.dataset.fieldId;
                this.deleteField(fieldId);
            });
        });
        
        // Update preview if visible
        if (document.getElementById('preview-panel').style.display !== 'none') {
            this.renderPreview();
        }
    }
    
    renderFieldPreview(field) {
        const previews = {
            'text': `<input type="text" class="form-control" placeholder="${field.placeholder || ''}" disabled>`,
            'textarea': `<textarea class="form-control" placeholder="${field.placeholder || ''}" disabled></textarea>`,
            'email': `<input type="email" class="form-control" placeholder="${field.placeholder || ''}" disabled>`,
            'number': `<input type="number" class="form-control" placeholder="${field.placeholder || ''}" disabled>`,
            'date': `<input type="date" class="form-control" disabled>`,
            'select': `<select class="form-select" disabled><option>Select option...</option></select>`,
            'checkbox': `<div class="form-check"><input type="checkbox" class="form-check-input" disabled><label class="form-check-label">Option</label></div>`,
            'radio': `<div class="form-check"><input type="radio" class="form-check-input" disabled><label class="form-check-label">Option</label></div>`,
            'file': `<input type="file" class="form-control" disabled>`
        };
        return previews[field.type] || previews['text'];
    }
    
    editField(fieldId) {
        const field = this.fields.find(f => f.id === fieldId);
        if (!field) return;
        
        // Open field configuration modal
        this.showFieldConfigModal(field);
    }
    
    deleteField(fieldId) {
        if (confirm('Are you sure you want to delete this field?')) {
            this.fields = this.fields.filter(f => f.id !== fieldId);
            this.renderFields();
            if (this.fields.length === 0) {
                this.showEmptyState();
            }
        }
    }
    
    showFieldConfigModal(field) {
        this.selectedField = field;
        const modalEl = document.getElementById('fieldConfigModal');
        
        if (!modalEl) {
            console.error('FormBuilder: fieldConfigModal element not found');
            return;
        }
        
        // Check if Bootstrap is available
        if (typeof bootstrap === 'undefined') {
            console.error('FormBuilder: Bootstrap is not loaded');
            // Fallback: show modal manually
            modalEl.style.display = 'block';
            modalEl.classList.add('show');
            document.body.classList.add('modal-open');
            return;
        }
        
        const modal = new bootstrap.Modal(modalEl);
        
        // Populate form with field data
        const fieldLabel = document.getElementById('fieldLabel');
        const fieldName = document.getElementById('fieldName');
        const fieldPlaceholder = document.getElementById('fieldPlaceholder');
        const fieldRequired = document.getElementById('fieldRequired');
        const fieldHelpText = document.getElementById('fieldHelpText');
        
        if (fieldLabel) fieldLabel.value = field.label || '';
        if (fieldName) fieldName.value = field.id || '';
        if (fieldPlaceholder) fieldPlaceholder.value = field.placeholder || '';
        if (fieldRequired) fieldRequired.checked = field.required || false;
        if (fieldHelpText) fieldHelpText.value = field.helpText || '';
        
        // Show options container for select/radio types
        const optionsContainer = document.getElementById('fieldOptionsContainer');
        if (field.type === 'select' || field.type === 'radio') {
            if (optionsContainer) {
                optionsContainer.style.display = 'block';
                this.renderFieldOptions(field.options || []);
            }
        } else {
            if (optionsContainer) optionsContainer.style.display = 'none';
        }
        
        // Disable field name editing if field already exists
        if (fieldName) {
            fieldName.disabled = !!field.id && field.id.startsWith('field_');
        }
        
        modal.show();
    }
    
    renderFieldOptions(options) {
        const container = document.getElementById('fieldOptionsList');
        container.innerHTML = options.map((option, index) => `
            <div class="input-group mb-2 option-item" data-option-index="${index}">
                <input type="text" class="form-control option-value" value="${option.value || option}" placeholder="Option value">
                <input type="text" class="form-control option-label" value="${option.label || option}" placeholder="Option label">
                <button type="button" class="btn btn-outline-danger btn-remove-option">
                    <i class="bi bi-trash"></i>
                </button>
            </div>
        `).join('');
        
        // Add remove handlers
        container.querySelectorAll('.btn-remove-option').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.currentTarget.closest('.option-item').remove();
            });
        });
    }
    
    saveFieldConfig() {
        if (!this.selectedField) return;
        
        const label = document.getElementById('fieldLabel').value;
        const name = document.getElementById('fieldName').value;
        const placeholder = document.getElementById('fieldPlaceholder').value;
        const required = document.getElementById('fieldRequired').checked;
        const helpText = document.getElementById('fieldHelpText').value;
        
        if (!label || !name) {
            alert('Field label and name are required');
            return;
        }
        
        // Update field
        this.selectedField.label = label;
        if (!this.selectedField.id.startsWith('field_')) {
            this.selectedField.id = name;
        }
        this.selectedField.placeholder = placeholder;
        this.selectedField.required = required;
        this.selectedField.helpText = helpText;
        
        // Get options if applicable
        if (this.selectedField.type === 'select' || this.selectedField.type === 'radio') {
            const optionItems = document.querySelectorAll('.option-item');
            this.selectedField.options = Array.from(optionItems).map(item => {
                const value = item.querySelector('.option-value').value;
                const label = item.querySelector('.option-label').value;
                return { value, label: label || value };
            }).filter(opt => opt.value);
        }
        
        // Close modal
        const modalEl = document.getElementById('fieldConfigModal');
        if (modalEl) {
            if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
                const modal = bootstrap.Modal.getInstance(modalEl);
                if (modal) {
                    modal.hide();
                } else {
                    // Fallback: hide manually
                    modalEl.style.display = 'none';
                    modalEl.classList.remove('show');
                    document.body.classList.remove('modal-open');
                }
            } else {
                // Fallback: hide manually
                modalEl.style.display = 'none';
                modalEl.classList.remove('show');
                document.body.classList.remove('modal-open');
            }
        }
        
        // Re-render fields
        this.renderFields();
        this.renderPreview();
        
        this.selectedField = null;
    }
    
    togglePreview() {
        const panel = document.getElementById('preview-panel');
        const btn = document.getElementById('btn-preview');
        
        if (panel.style.display === 'none') {
            panel.style.display = 'block';
            this.renderPreview();
            btn.innerHTML = '<i class="bi bi-eye-slash"></i> Hide Preview';
        } else {
            panel.style.display = 'none';
            btn.innerHTML = '<i class="bi bi-eye"></i> Preview';
        }
    }
    
    renderPreview() {
        const preview = document.getElementById('preview-form');
        
        if (this.fields.length === 0) {
            preview.innerHTML = '<p class="text-muted">No fields to preview</p>';
            return;
        }
        
        const formHtml = this.fields.map(field => this.renderFieldForPreview(field)).join('');
        preview.innerHTML = `<form class="needs-validation" novalidate>${formHtml}</form>`;
    }
    
    renderFieldForPreview(field) {
        const requiredAttr = field.required ? 'required' : '';
        const requiredClass = field.required ? 'required' : '';
        const helpText = field.helpText ? `<small class="form-text text-muted">${field.helpText}</small>` : '';
        
        let fieldHtml = '';
        
        switch(field.type) {
            case 'text':
            case 'email':
            case 'number':
                fieldHtml = `
                    <div class="mb-3">
                        <label class="form-label ${requiredClass}">${field.label}</label>
                        <input type="${field.type}" class="form-control" 
                               placeholder="${field.placeholder || ''}" 
                               ${requiredAttr} disabled>
                        ${helpText}
                    </div>
                `;
                break;
            case 'textarea':
                fieldHtml = `
                    <div class="mb-3">
                        <label class="form-label ${requiredClass}">${field.label}</label>
                        <textarea class="form-control" 
                                  placeholder="${field.placeholder || ''}" 
                                  rows="3" ${requiredAttr} disabled></textarea>
                        ${helpText}
                    </div>
                `;
                break;
            case 'date':
                fieldHtml = `
                    <div class="mb-3">
                        <label class="form-label ${requiredClass}">${field.label}</label>
                        <input type="date" class="form-control" ${requiredAttr} disabled>
                        ${helpText}
                    </div>
                `;
                break;
            case 'select':
                const selectOptions = (field.options || []).map(opt => 
                    `<option value="${opt.value || opt}">${opt.label || opt.value || opt}</option>`
                ).join('');
                fieldHtml = `
                    <div class="mb-3">
                        <label class="form-label ${requiredClass}">${field.label}</label>
                        <select class="form-select" ${requiredAttr} disabled>
                            <option value="">Select...</option>
                            ${selectOptions}
                        </select>
                        ${helpText}
                    </div>
                `;
                break;
            case 'checkbox':
                fieldHtml = `
                    <div class="mb-3">
                        <div class="form-check">
                            <input type="checkbox" class="form-check-input" 
                                   id="preview_${field.id}" ${requiredAttr} disabled>
                            <label class="form-check-label ${requiredClass}" for="preview_${field.id}">
                                ${field.label}
                            </label>
                        </div>
                        ${helpText}
                    </div>
                `;
                break;
            case 'radio':
                const radioOptions = (field.options || []).map((opt, idx) => {
                    const value = opt.value || opt;
                    const label = opt.label || opt.value || opt;
                    return `
                        <div class="form-check">
                            <input type="radio" class="form-check-input" 
                                   name="preview_${field.id}" id="preview_${field.id}_${idx}"
                                   value="${value}" ${requiredAttr} disabled>
                            <label class="form-check-label" for="preview_${field.id}_${idx}">
                                ${label}
                            </label>
                        </div>
                    `;
                }).join('');
                fieldHtml = `
                    <div class="mb-3">
                        <label class="form-label ${requiredClass}">${field.label}</label>
                        ${radioOptions}
                        ${helpText}
                    </div>
                `;
                break;
            case 'file':
                fieldHtml = `
                    <div class="mb-3">
                        <label class="form-label ${requiredClass}">${field.label}</label>
                        <input type="file" class="form-control" ${requiredAttr} disabled>
                        ${helpText}
                    </div>
                `;
                break;
            default:
                fieldHtml = `<div class="mb-3"><p class="text-muted">Unknown field type: ${field.type}</p></div>`;
        }
        
        return fieldHtml;
    }
    
    hideEmptyState() {
        const emptyState = document.getElementById('empty-state');
        if (emptyState) {
            emptyState.style.display = 'none';
        }
    }
    
    showEmptyState() {
        const emptyState = document.getElementById('empty-state');
        if (emptyState) {
            emptyState.style.display = 'block';
        }
    }
    
    async saveForm() {
        if (this.fields.length === 0) {
            alert('Please add at least one field before saving');
            return;
        }
        
        // Get form name
        const formName = prompt('Enter form name:', 'Untitled Form');
        if (!formName) return;
        
        // Convert fields to JSON schema format
        const schema = this.generateSchema();
        const uiSchema = this.generateUISchema();
        
        // Determine if we're editing or creating
        const isEdit = this.options.formId;
        const url = isEdit ? `${this.options.saveUrl}${this.options.formId}/` : this.options.saveUrl;
        const method = isEdit ? 'PUT' : 'POST';
        
        const formData = {
            name: formName,
            description: '',
            form_type: 'application',
            schema: schema,
            ui_schema: uiSchema,
            is_active: true
        };
        
        try {
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                credentials: 'include',
                body: JSON.stringify(formData)
            });
            
            if (response.ok) {
                const data = await response.json();
                this.showMessage('Form saved successfully!', 'success');
                console.log('Form saved:', data);
                
                // If editing existing form, stay on page; if new, redirect to list
                if (this.options.formId) {
                    // Editing - stay on page
                } else {
                    // New form - redirect to list after 2 seconds
                    setTimeout(() => {
                        window.location.href = '/api/application-forms/list/';
                    }, 2000);
                }
            } else {
                const error = await response.json();
                this.showMessage(`Error saving form: ${error.detail || 'Unknown error'}`, 'error');
            }
        } catch (error) {
            console.error('Error saving form:', error);
            this.showMessage('Network error while saving form', 'error');
        }
    }
    
    generateUISchema() {
        const uiSchema = {};
        
        this.fields.forEach(field => {
            uiSchema[field.id] = {
                'ui:placeholder': field.placeholder || '',
                'ui:help': field.helpText || ''
            };
        });
        
        return uiSchema;
    }
    
    getCSRFToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }
        return '';
    }

    escapeHtml(str) {
        if (str === null || str === undefined) return '';
        const d = document.createElement('div');
        d.textContent = String(str);
        return d.innerHTML;
    }

    openStepTemplateModal() {
        if (!this.options.formId) {
            this.showMessage('Save the form first, then you can apply a step template.', 'error');
            return;
        }
        const errEl = document.getElementById('stepTemplateApplyError');
        if (errEl) {
            errEl.classList.add('d-none');
            errEl.textContent = '';
        }
        const keyInput = document.getElementById('stepTemplateKeyOverride');
        if (keyInput) keyInput.value = '';
        this.refreshStepTemplateOptions().then(() => {
            const el = document.getElementById('stepTemplateModal');
            if (!el || typeof bootstrap === 'undefined') return;
            const modal = bootstrap.Modal.getOrCreateInstance(el);
            modal.show();
        });
    }

    async refreshStepTemplateOptions() {
        const sel = document.getElementById('stepTemplateSelect');
        if (!sel) return;
        sel.innerHTML = '<option value="">Loading…</option>';
        try {
            let url = `${this.options.apiUrl}step-templates/`;
            const items = [];
            while (url) {
                const response = await fetch(url, { credentials: 'include' });
                if (!response.ok) {
                    sel.innerHTML = '<option value="">Could not load templates</option>';
                    return;
                }
                const data = await response.json();
                const chunk = Array.isArray(data) ? data : data.results || [];
                items.push(...chunk);
                url = data.next || null;
            }
            const active = items.filter((t) => t.is_active === true);
            if (active.length === 0) {
                sel.innerHTML = '<option value="">No active templates</option>';
                return;
            }
            sel.innerHTML =
                '<option value="">— Select template —</option>' +
                active
                    .map(
                        (t) =>
                            `<option value="${t.id}">${this.escapeHtml(t.name)} (${this.escapeHtml(t.default_step_key || '')})</option>`
                    )
                    .join('');
        } catch (e) {
            console.error(e);
            sel.innerHTML = '<option value="">Error loading templates</option>';
        }
    }

    async applyStepTemplateFromModal() {
        const errEl = document.getElementById('stepTemplateApplyError');
        if (errEl) {
            errEl.classList.add('d-none');
            errEl.textContent = '';
        }
        if (!this.options.formId) {
            this.showMessage('Save the form first.', 'error');
            return;
        }
        const sel = document.getElementById('stepTemplateSelect');
        const tid = sel && sel.value ? parseInt(sel.value, 10) : NaN;
        if (!tid) {
            if (errEl) {
                errEl.textContent = 'Choose a template.';
                errEl.classList.remove('d-none');
            }
            return;
        }
        const keyInput = document.getElementById('stepTemplateKeyOverride');
        const stepKey = keyInput && keyInput.value ? keyInput.value.trim() : '';
        const body = { template_id: tid };
        if (stepKey) body.step_key = stepKey;

        try {
            const response = await fetch(
                `${this.options.apiUrl}form-types/${this.options.formId}/apply-step-template/`,
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCSRFToken(),
                    },
                    credentials: 'include',
                    body: JSON.stringify(body),
                }
            );
            const modalEl = document.getElementById('stepTemplateModal');
            if (response.ok) {
                if (modalEl && typeof bootstrap !== 'undefined') {
                    bootstrap.Modal.getInstance(modalEl)?.hide();
                }
                this.showMessage('Step template applied. Reloading form…', 'success');
                this.loadForm(this.options.formId);
                return;
            }
            let msg = 'Could not apply template.';
            try {
                const err = await response.json();
                if (typeof err.detail === 'string') msg = err.detail;
                else if (Array.isArray(err.detail)) msg = err.detail.join(' ');
                else if (err.detail && typeof err.detail === 'object') {
                    msg = Object.entries(err.detail)
                        .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : v}`)
                        .join('; ');
                } else if (typeof err === 'object') {
                    const parts = [];
                    for (const [k, v] of Object.entries(err)) {
                        if (Array.isArray(v)) parts.push(`${k}: ${v.join(', ')}`);
                        else if (typeof v === 'string') parts.push(v);
                    }
                    if (parts.length) msg = parts.join('; ');
                }
            } catch (_) {
                /* use default msg */
            }
            if (errEl) {
                errEl.textContent = msg;
                errEl.classList.remove('d-none');
            } else {
                this.showMessage(msg, 'error');
            }
        } catch (error) {
            console.error(error);
            this.showMessage('Network error while applying template', 'error');
        }
    }
    
    showMessage(message, type = 'info') {
        // Remove existing messages
        const existing = document.querySelector('.builder-message');
        if (existing) existing.remove();
        
        const messageEl = document.createElement('div');
        messageEl.className = `builder-message ${type}`;
        messageEl.innerHTML = `
            <i class="bi bi-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        `;
        
        const toolbar = document.querySelector('.builder-toolbar');
        toolbar.insertAdjacentElement('afterend', messageEl);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            messageEl.remove();
        }, 5000);
    }
    
    generateSchema() {
        const properties = {};
        const required = [];
        
        this.fields.forEach(field => {
            const fieldName = field.id.startsWith('field_') ? field.id : field.id;
            const fieldType = this.mapFieldTypeToSchemaType(field.type);
            
            const fieldSchema = {
                type: fieldType,
                title: field.label
            };
            
            // Add format for email
            if (field.type === 'email') {
                fieldSchema.format = 'email';
            }
            
            // Add enum for select/radio
            if ((field.type === 'select' || field.type === 'radio') && field.options && field.options.length > 0) {
                fieldSchema.enum = field.options.map(opt => opt.value || opt);
                fieldSchema.enumNames = field.options.map(opt => opt.label || opt.value || opt);
            }
            
            // Add minimum/maximum for number
            if (field.type === 'number') {
                if (field.min !== undefined) fieldSchema.minimum = field.min;
                if (field.max !== undefined) fieldSchema.maximum = field.max;
            }
            
            properties[fieldName] = fieldSchema;
            
            if (field.required) {
                required.push(fieldName);
            }
        });
        
        return {
            type: 'object',
            properties: properties,
            required: required
        };
    }
    
    mapFieldTypeToSchemaType(type) {
        const mapping = {
            'text': 'string',
            'textarea': 'string',
            'email': 'string',
            'number': 'number',
            'date': 'string',
            'select': 'string',
            'checkbox': 'boolean',
            'radio': 'string',
            'file': 'string'
        };
        return mapping[type] || 'string';
    }
    
    mapSchemaTypeToFieldType(schemaType, format, fieldSchema = {}) {
        // Check format first (email)
        if (format === 'email') return 'email';
        
        // Check schema type
        if (schemaType === 'number') return 'number';
        if (schemaType === 'boolean') return 'checkbox';
        
        // If it has enum, it's likely select or radio - default to select
        if (fieldSchema.enum) {
            return 'select';
        }
        
        // Default to text for string types
        if (schemaType === 'string') {
            return 'text';
        }
        
        // Fallback
        return 'text';
    }
    
    loadForm(formId) {
        // Load existing form from API
        fetch(`${this.options.apiUrl}form-types/${formId}/`, {
            credentials: 'include'
        })
        .then(response => response.json())
        .then(data => {
            this.loadFormFromSchema(data.schema, data.ui_schema);
            this.showMessage('Form loaded successfully', 'success');
        })
        .catch(error => {
            console.error('Error loading form:', error);
            this.showMessage('Error loading form', 'error');
        });
    }
    
    loadFormFromSchema(schema, uiSchema = {}) {
        if (!schema || !schema.properties) {
            this.showMessage('Invalid form schema', 'error');
            return;
        }
        
        this.fields = [];
        
        Object.entries(schema.properties).forEach(([fieldName, fieldSchema]) => {
            const field = {
                id: fieldName,
                type: this.mapSchemaTypeToFieldType(fieldSchema.type, fieldSchema.format, fieldSchema),
                label: fieldSchema.title || fieldName,
                required: schema.required && schema.required.includes(fieldName),
                placeholder: uiSchema[fieldName]?.['ui:placeholder'] || '',
                helpText: uiSchema[fieldName]?.['ui:help'] || ''
            };
            
            // Handle enum (select/radio options)
            if (fieldSchema.enum) {
                field.options = fieldSchema.enum.map((value, idx) => ({
                    value: value,
                    label: fieldSchema.enumNames?.[idx] || value
                }));
            }
            
            this.fields.push(field);
        });
        
        this.renderFields();
        if (this.fields.length > 0) {
            this.hideEmptyState();
        }
        
        // Reinitialize Sortable after rendering
        if (this.sortableInstance) {
            this.sortableInstance.destroy();
        }
        this.initializeSortable();
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('form-builder-container')) {
        window.formBuilder = new FormBuilder('form-builder-container');
    }
});

