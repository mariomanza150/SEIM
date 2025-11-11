// File upload area logic for SEIM frontend
// Modularized from main.js

import { debounce } from './utils.js';
import { escapeHtml } from './validators.js';

export function initializeFileUpload() {
    const uploadAreas = document.querySelectorAll('.file-upload-area');
    uploadAreas.forEach(area => {
        const input = area.querySelector('input[type="file"]');
        if (!input) return;
        const debouncedDragLeave = debounce(function(e) {
            e.preventDefault();
            area.classList.remove('dragover');
        }, 100);
        area.addEventListener('dragover', function(e) {
            e.preventDefault();
            area.classList.add('dragover');
        });
        area.addEventListener('dragleave', debouncedDragLeave);
        area.addEventListener('drop', function(e) {
            e.preventDefault();
            area.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                input.files = files;
                input.dispatchEvent(new Event('change'));
            }
        });
        input.addEventListener('change', function() {
            requestAnimationFrame(() => {
                updateFileUploadDisplay(area, this.files);
            });
        });
    });
}

export function updateFileUploadDisplay(area, files) {
    const display = area.querySelector('.file-display');
    if (!display) return;
    if (files.length === 0) {
        // Use security utilities for safe innerHTML setting
        if (window.SEIM_SECURITY_UTILS) {
            window.SEIM_SECURITY_UTILS.safeSetInnerHTML(display, '<p class="text-muted">No files selected</p>');
        } else {
            display.textContent = 'No files selected';
        }
        return;
    }
    const fragment = document.createDocumentFragment();
    const list = document.createElement('ul');
    list.className = 'list-unstyled';
    for (let file of files) {
        const li = document.createElement('li');
        const safeFileName = escapeHtml(file.name);
        // Use security utilities for safe innerHTML setting
        if (window.SEIM_SECURITY_UTILS) {
            window.SEIM_SECURITY_UTILS.safeSetInnerHTML(li, `<i class="bi bi-file-earmark"></i> ${safeFileName} (${file.size} bytes)`);
        } else {
            li.textContent = `${safeFileName} (${file.size} bytes)`;
        }
        list.appendChild(li);
    }
    fragment.appendChild(list);
    display.innerHTML = '';
    display.appendChild(fragment);
} 