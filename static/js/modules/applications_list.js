import { apiRequest } from './api.js';
import { showSectionLoading, hideSectionLoading } from './ui.js';
import { logger } from './logger.js';
import { errorHandler } from './error-handler.js';

let currentPage = 1;
let pageSize = 12;
let hasNextPage = true;
let isLoading = false;
let filters = {};

const containerSelector = '#applicationsListContainer';
const loadMoreBtnId = 'loadMoreApplicationsBtn';

function buildApiUrl(page, filters) {
    const params = new URLSearchParams();
    params.append('limit', pageSize);
    params.append('offset', (page - 1) * pageSize);
    for (const [key, value] of Object.entries(filters)) {
        if (value) params.append(key, value);
    }
    return `/api/applications/?${params.toString()}`;
}

function renderApplications(applications, append = false) {
    const container = document.querySelector(containerSelector);
    if (!container) return;
    let html = '';
    for (const application of applications) {
        html += renderApplicationCard(application);
    }
    if (append) {
        container.insertAdjacentHTML('beforeend', html);
    } else {
        container.innerHTML = html;
    }
}

function renderApplicationCard(application) {
    // Minimal card rendering; expand as needed
    return `
    <div class="col-md-6 col-lg-4">
        <div class="card h-100">
            <div class="card-header">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <h5 class="card-title mb-1">${application.program.name}</h5>
                        <p class="text-muted mb-0">${application.program.institution}</p>
                    </div>
                    <span class="badge bg-secondary">${application.status}</span>
                </div>
            </div>
            <div class="card-body">
                <div class="row g-2 mb-3">
                    <div class="col-6">
                        <small class="text-muted">Submitted</small><br>
                        <strong>${application.submitted_at || 'Not submitted'}</strong>
                    </div>
                    <div class="col-6">
                        <small class="text-muted">Program</small><br>
                        <strong>${application.program.country}</strong>
                    </div>
                </div>
                <div class="mb-3">
                    <small class="text-muted">Personal Statement</small><br>
                    <p class="mb-0">${application.personal_statement || ''}</p>
                </div>
            </div>
            <div class="card-footer">
                <a href="/applications/${application.id}/" class="btn btn-outline-primary btn-sm">
                    <i class="bi bi-eye"></i> View Details
                </a>
            </div>
        </div>
    </div>
    `;
}

async function fetchApplications(page, append = false) {
    if (isLoading || !hasNextPage) return;
    isLoading = true;
    showSectionLoading(containerSelector, 'Loading...');
    try {
        const url = buildApiUrl(page, filters);
        const data = await apiRequest(url);
        renderApplications(data.results, append);
        hasNextPage = !!data.next;
        if (!hasNextPage) {
            const btn = document.getElementById(loadMoreBtnId);
            if (btn) btn.style.display = 'none';
        }
    } catch (error) {
        errorHandler.handleApiError(error, { context: 'fetchApplications', page, filters });
        logger.error('Failed to fetch applications', error);
    } finally {
        hideSectionLoading(containerSelector);
        isLoading = false;
    }
}

function setupLoadMoreButton() {
    let btn = document.getElementById(loadMoreBtnId);
    if (!btn) {
        btn = document.createElement('button');
        btn.id = loadMoreBtnId;
        btn.className = 'btn btn-primary d-block mx-auto my-4';
        btn.textContent = 'Load More';
        btn.addEventListener('click', () => {
            currentPage++;
            fetchApplications(currentPage, true);
        });
        const container = document.querySelector(containerSelector);
        if (container) container.parentNode.appendChild(btn);
    } else {
        btn.style.display = 'block';
    }
}

function setupFilters() {
    const form = document.getElementById('applicationsFilterForm');
    if (!form) return;
    form.addEventListener('submit', e => {
        e.preventDefault();
        const formData = new FormData(form);
        filters = Object.fromEntries(formData.entries());
        currentPage = 1;
        hasNextPage = true;
        fetchApplications(currentPage, false);
        setupLoadMoreButton();
    });
}

export function initApplicationsList() {
    currentPage = 1;
    hasNextPage = true;
    filters = {};
    setupFilters();
    fetchApplications(currentPage, false);
    setupLoadMoreButton();
} 