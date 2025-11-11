// Notification and dialog utilities for SEIM frontend
// Modularized from main.js

import Swal from 'sweetalert2';
import { logger } from './logger.js';
import { errorHandler } from './error-handler.js';

/**
 * Show a generic alert
 */
export function showAlert(message, icon = 'info', title = null) {
    logger.info(`Showing alert: ${icon} - ${title || ''} - ${message}`);
    return Swal.fire({
        title: title || '',
        text: message,
        icon: icon,
        confirmButtonText: 'OK',
        customClass: {
            confirmButton: 'btn btn-primary'
        },
        buttonsStyling: false
    });
}

/**
 * Show a success alert
 */
export function showSuccessAlert(title, message) {
    return showAlert(message, 'success', title);
}

/**
 * Show an error alert
 */
export function showErrorAlert(title, message) {
    errorHandler.handleApiError(new Error(message), { title });
    logger.error(`Showing error alert: ${title} - ${message}`);
    return showAlert(message, 'error', title);
}

/**
 * Show a warning alert
 */
export function showWarningAlert(title, message) {
    return showAlert(message, 'warning', title);
}

/**
 * Show a confirmation dialog (returns a Promise)
 */
export function showConfirmDialog(title, text, confirmButtonText = 'Yes, proceed') {
    return Swal.fire({
        title: title,
        text: text,
        icon: 'question',
        showCancelButton: true,
        confirmButtonText: confirmButtonText,
        cancelButtonText: 'Cancel',
        customClass: {
            confirmButton: 'btn btn-primary',
            cancelButton: 'btn btn-secondary'
        },
        buttonsStyling: false
    });
}

/**
 * Show a loading alert
 */
export function showLoadingAlert(title = 'Loading...') {
    return Swal.fire({
        title: title,
        allowOutsideClick: false,
        didOpen: () => {
            Swal.showLoading();
        }
    });
}

/**
 * Close any open alert
 */
export function closeAlert() {
    Swal.close();
} 