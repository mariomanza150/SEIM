// Loading spinner/overlay utilities for SEIM frontend

export function setLoadingState(element, isLoading, loadingText = 'Loading...') {
    if (!element) return;
    if (isLoading) {
        element.disabled = true;
        element.dataset.originalText = element.textContent;
        element.textContent = loadingText;
    } else {
        element.disabled = false;
        if (element.dataset.originalText) {
            element.textContent = element.dataset.originalText;
            delete element.dataset.originalText;
        }
    }
}

export function setLoadingStates(elements, isLoading, loadingText = 'Loading...') {
    elements.forEach(el => setLoadingState(el, isLoading, loadingText));
}

export function showPageLoading(message = 'Loading...') {
    let overlay = document.getElementById('page-loading-overlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'page-loading-overlay';
        overlay.innerHTML = `<div class=\"spinner-border text-primary\" role=\"status\"></div><span class=\"ms-2\">${message}</span>`;
        overlay.style.position = 'fixed';
        overlay.style.top = 0;
        overlay.style.left = 0;
        overlay.style.width = '100vw';
        overlay.style.height = '100vh';
        overlay.style.background = 'rgba(255,255,255,0.7)';
        overlay.style.display = 'flex';
        overlay.style.alignItems = 'center';
        overlay.style.justifyContent = 'center';
        overlay.style.zIndex = 2000;
        document.body.appendChild(overlay);
    } else {
        overlay.style.display = 'flex';
    }
}

export function hidePageLoading() {
    const overlay = document.getElementById('page-loading-overlay');
    if (overlay) {
        overlay.style.display = 'none';
    }
}

export function showSectionLoading(selector, message = 'Loading...') {
    const section = document.querySelector(selector);
    if (!section) return;
    let spinner = section.querySelector('.section-loading-spinner');
    if (!spinner) {
        spinner = document.createElement('div');
        spinner.className = 'section-loading-spinner';
        spinner.innerHTML = `<div class=\"spinner-border text-primary\" role=\"status\"></div><span class=\"ms-2\">${message}</span>`;
        spinner.style.display = 'flex';
        spinner.style.alignItems = 'center';
        spinner.style.justifyContent = 'center';
        section.appendChild(spinner);
    } else {
        spinner.style.display = 'flex';
    }
}

export function hideSectionLoading(selector) {
    const section = document.querySelector(selector);
    if (!section) return;
    const spinner = section.querySelector('.section-loading-spinner');
    if (spinner) {
        spinner.style.display = 'none';
    }
} 