// Import security utilities first to ensure they're available
import './modules/security.js';
import { initializeTooltips, initializeModals, showPageLoading, hidePageLoading } from './modules/ui.js';
import { logger } from './modules/logger.js';
import { errorHandler } from './modules/error-handler.js';

// Dashboard-specific initialization and utilities

document.addEventListener('DOMContentLoaded', async () => {
    showPageLoading();
    initializeTooltips();
    initializeModals();
    
    // Initialize dashboard-specific features
    await initializeDashboardFeatures();
    
    hidePageLoading();
});

async function initializeDashboardFeatures() {
    // Initialize any dashboard-specific features
    // This could include charts, real-time updates, etc.
    
    // Setup auto-refresh for dashboard data (every 5 minutes)
    setInterval(async () => {
        if (window.location.pathname === '/dashboard/') {
            await refreshDashboardData();
        }
    }, 300000); // 5 minutes
    
    // Initialize any dashboard widgets
    initializeDashboardWidgets();
}

async function refreshDashboardData() {
    try {
        // This function can be called to refresh dashboard data
        // It will be implemented in the template
        if (typeof window.refreshDashboard === 'function') {
            await window.refreshDashboard();
        }
    } catch (error) {
        errorHandler.handleApiError(error, { context: 'refreshDashboardData' });
        logger.error('Failed to refresh dashboard data:', error);
    }
}

function initializeDashboardWidgets() {
    // Initialize any dashboard widgets or charts
    // This is a placeholder for future dashboard enhancements
    
    // Example: Initialize charts if Chart.js is available
    if (typeof Chart !== 'undefined') {
        initializeDashboardCharts();
    }
}

function initializeDashboardCharts() {
    // Initialize dashboard charts
    // This would be implemented when charts are added to the dashboard
    
    const chartElements = document.querySelectorAll('[data-chart]');
    chartElements.forEach(element => {
        const chartType = element.dataset.chart;
        const chartData = JSON.parse(element.dataset.chartData || '{}');
        
        switch (chartType) {
            case 'applications-timeline':
                createApplicationsTimelineChart(element, chartData);
                break;
            case 'status-distribution':
                createStatusDistributionChart(element, chartData);
                break;
            // Add more chart types as needed
        }
    });
}

function createApplicationsTimelineChart(element, data) {
    // Create applications timeline chart
    // Implementation would depend on the data structure
    logger.info('Creating applications timeline chart', data);
}

function createStatusDistributionChart(element, data) {
    // Create status distribution chart
    // Implementation would depend on the data structure
    logger.info('Creating status distribution chart', data);
}

// Export functions for use in templates
window.dashboardUtils = {
    refreshDashboardData,
    initializeDashboardWidgets,
    initializeDashboardCharts
}; 