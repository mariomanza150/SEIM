// Application Actions Module
// Handles application submission, withdrawal, and comment management

import { apiRequest } from './api.js';
import { showConfirmDialog, showSuccessAlert, showErrorAlert } from './notifications.js';
import { logger } from './logger.js';
import { errorHandler } from './error-handler.js';

// Simple toast function since it doesn't exist in the codebase
function showToast(message, type = 'info') {
    // Create a simple toast notification
    const toast = document.createElement('div');
    toast.className = `alert alert-${type === 'success' ? 'success' : type === 'error' ? 'danger' : 'info'} alert-dismissible fade show position-fixed`;
    toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    // Use security utilities for safe innerHTML setting
    if (window.SEIM_SECURITY_UTILS) {
        window.SEIM_SECURITY_UTILS.safeSetInnerHTML(toast, `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `);
    } else {
        // Fallback to textContent for safety
        toast.textContent = message;
    }
    document.body.appendChild(toast);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 3000);
}

/**
 * Submit an application
 * @param {number} applicationId - The application ID to submit
 */
export async function submitApplication(applicationId) {
    const result = await showConfirmDialog(
        'Submit Application',
        'Are you sure you want to submit this application? You won\'t be able to edit it after submission.',
        'Yes, Submit'
    );
    
    if (result.isConfirmed) {
        try {
            await apiRequest(`/api/applications/${applicationId}/submit/`, {
                method: 'POST'
            });
            showSuccessAlert('Application Submitted!', 'Your application has been submitted successfully.');
            // Refresh the page to show updated status
            location.reload();
        } catch (error) {
            errorHandler.handleApiError(error, { context: 'submitApplication', applicationId });
            showErrorAlert('Error', 'Failed to submit application. Please try again.');
        }
    }
}

/**
 * Withdraw an application
 * @param {number} applicationId - The application ID to withdraw
 */
export async function withdrawApplication(applicationId) {
    const result = await showConfirmDialog(
        'Withdraw Application',
        'Are you sure you want to withdraw this application? This action cannot be undone.',
        'Yes, Withdraw'
    );
    
    if (result.isConfirmed) {
        try {
            await apiRequest(`/api/applications/${applicationId}/withdraw/`, {
                method: 'POST'
            });
            showSuccessAlert('Application Withdrawn', 'Your application has been withdrawn successfully.');
            // Refresh the page to show updated status
            location.reload();
        } catch (error) {
            errorHandler.handleApiError(error, { context: 'withdrawApplication', applicationId });
            showErrorAlert('Error', 'Failed to withdraw application. Please try again.');
        }
    }
}

/**
 * Delete a comment
 * @param {number} commentId - The comment ID to delete
 */
export async function deleteComment(commentId) {
    const result = await showConfirmDialog(
        'Delete Comment',
        'Are you sure you want to delete this comment? This action cannot be undone.',
        'Yes, Delete'
    );
    
    if (result.isConfirmed) {
        try {
            await apiRequest(`/api/comments/${commentId}/`, {
                method: 'DELETE'
            });
            showSuccessAlert('Comment Deleted', 'Comment has been deleted successfully.');
            // Remove the comment element from the DOM
            const commentElement = document.querySelector(`[data-comment-id="${commentId}"]`);
            if (commentElement) {
                commentElement.remove();
            }
        } catch (error) {
            errorHandler.handleApiError(error, { context: 'deleteComment', commentId });
            showErrorAlert('Error', 'Failed to delete comment. Please try again.');
        }
    }
}

/**
 * Add a comment to an application
 * @param {number} applicationId - The application ID
 * @param {string} text - The comment text
 * @param {string} containerSelector - CSS selector for the comments container
 */
export async function addComment(applicationId, text, containerSelector = '#commentsContainer') {
    try {
        const data = await apiRequest('/api/comments/', {
            method: 'POST',
            body: JSON.stringify({
                application: applicationId,
                text: text
            })
        });
        
        // Add new comment to the container
        const commentsContainer = document.querySelector(containerSelector);
        if (commentsContainer) {
            // Use security utilities for safe HTML creation
            if (window.SEIM_SECURITY_UTILS) {
                const commentHtml = window.SEIM_SECURITY_UTILS.createSafeHTML(`
                    <div class="comment mb-3 p-3 border rounded" data-comment-id="{{commentId}}">
                        <div class="d-flex justify-content-between align-items-start">
                            <div>
                                <strong>{{userName}}</strong>
                                <small class="text-muted ms-2">Just now</small>
                            </div>
                            <button class="btn btn-sm btn-outline-danger" onclick="deleteComment({{commentId}})">
                                <i class="bi bi-trash"></i>
                            </button>
                        </div>
                        <p class="mb-0 mt-2">{{commentText}}</p>
                    </div>
                `, {
                    commentId: data.id,
                    userName: data.user_name || 'You',
                    commentText: text.replace(/\n/g, '<br>')
                });
                
                // Remove "No comments yet" message if it exists
                const noCommentsMsg = commentsContainer.querySelector('p.text-muted');
                if (noCommentsMsg && noCommentsMsg.textContent === 'No comments yet.') {
                    noCommentsMsg.remove();
                }
                
                commentsContainer.insertAdjacentHTML('afterbegin', commentHtml);
            } else {
                // Fallback to simple text content
                const commentDiv = document.createElement('div');
                commentDiv.className = 'comment mb-3 p-3 border rounded';
                commentDiv.setAttribute('data-comment-id', data.id);
                commentDiv.textContent = `${data.user_name || 'You'}: ${text}`;
                commentsContainer.insertBefore(commentDiv, commentsContainer.firstChild);
            }
        }
        
        showToast('Comment posted successfully!', 'success');
        return data;
    } catch (error) {
        errorHandler.handleApiError(error, { context: 'addComment', applicationId, text });
        showErrorAlert('Error', 'Failed to post comment. Please try again.');
        throw error;
    }
}

/**
 * Escape HTML to prevent XSS
 * @param {string} text - Text to escape
 * @returns {string} Escaped text
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Make functions available globally for onclick handlers
window.submitApplication = submitApplication;
window.withdrawApplication = withdrawApplication;
window.deleteComment = deleteComment; 