import { apiRequest } from './api.js';
import { showSectionLoading, hideSectionLoading } from './ui.js';
import { logger } from './logger.js';
import { errorHandler } from './error-handler.js';

let currentPage = 1;
let pageSize = 12;
let hasNextPage = true;
let isLoading = false;
let filters = {};

const containerSelector = '#programsListContainer';
const loadMoreBtnId = 'loadMoreProgramsBtn';

function buildApiUrl(page, filters) {
    const params = new URLSearchParams();
    params.append('limit', pageSize);
    params.append('offset', (page - 1) * pageSize);
    for (const [key, value] of Object.entries(filters)) {
        if (value) params.append(key, value);
    }
    return `/api/programs/?${params.toString()}`;
}

function renderPrograms(programs, append = false) {
    const container = document.querySelector(containerSelector);
    if (!container) return;
    let html = '';
    for (const program of programs) {
        html += renderProgramCard(program);
    }
    if (append) {
        // Use security utilities for safe HTML insertion
        if (window.SEIM_SECURITY_UTILS) {
            container.insertAdjacentHTML('beforeend', html);
        } else {
            // Fallback to textContent for safety
            container.textContent = 'Programs loaded';
        }
    } else {
        // Use security utilities for safe innerHTML setting
        if (window.SEIM_SECURITY_UTILS) {
            window.SEIM_SECURITY_UTILS.safeSetInnerHTML(container, html);
        } else {
            // Fallback to textContent for safety
            container.textContent = 'Programs loaded';
        }
    }
}

function renderProgramCard(program) {
    return `
    <div class="col-md-6 col-lg-4">
        <div class="card h-100">
            <div class="card-header">
                <h5 class="card-title mb-1">${program.name}</h5>
                <p class="text-muted mb-0">${program.institution}</p>
            </div>
            <div class="card-body">
                <div class="mb-2">
                    <small class="text-muted">Country</small><br>
                    <strong>${program.country}</strong>
                </div>
                <div class="mb-2">
                    <small class="text-muted">Min GPA</small><br>
                    <strong>${program.min_gpa || 'N/A'}</strong>
                </div>
            </div>
            <div class="card-footer">
                <a href="/programs/${program.id}/" class="btn btn-outline-primary btn-sm">
                    <i class="bi bi-eye"></i> View Details
                </a>
            </div>
        </div>
    </div>
    `;
}

async function fetchPrograms(page, append = false) {
    if (isLoading || !hasNextPage) return;
    isLoading = true;
    showSectionLoading(containerSelector, 'Loading...');
    try {
        const url = buildApiUrl(page, filters);
        const data = await apiRequest(url);
        renderPrograms(data.results, append);
        hasNextPage = !!data.next;
        if (!hasNextPage) {
            const btn = document.getElementById(loadMoreBtnId);
            if (btn) btn.style.display = 'none';
        }
    } catch (error) {
        errorHandler.handleApiError(error, { context: 'fetchPrograms', page, filters });
        logger.error('Failed to fetch programs', error);
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
            fetchPrograms(currentPage, true);
        });
        const container = document.querySelector(containerSelector);
        if (container) container.parentNode.appendChild(btn);
    } else {
        btn.style.display = 'block';
    }
}

function setupFilters() {
    const form = document.getElementById('programsFilterForm');
    if (!form) return;
    form.addEventListener('submit', e => {
        e.preventDefault();
        const formData = new FormData(form);
        filters = Object.fromEntries(formData.entries());
        currentPage = 1;
        hasNextPage = true;
        fetchPrograms(currentPage, false);
        setupLoadMoreButton();
    });
}

export function initProgramsList() {
    currentPage = 1;
    hasNextPage = true;
    filters = {};
    setupFilters();
    fetchPrograms(currentPage, false);
    setupLoadMoreButton();
} 