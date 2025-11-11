// Bootstrap helpers for SEIM frontend

export function initializeTooltips() {
    const tooltipObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const element = entry.target;
                if (element.dataset.bsToggle === 'tooltip' && !element._tooltip) {
                    element._tooltip = new bootstrap.Tooltip(element);
                }
            }
        });
    });
    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
        tooltipObserver.observe(el);
    });
}

export function initializeModals() {
    const modalObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const element = entry.target;
                if (element.dataset.bsToggle === 'modal' && !element._modal) {
                    element._modal = new bootstrap.Modal(element);
                }
            }
        });
    });
    document.querySelectorAll('[data-bs-toggle="modal"]').forEach(el => {
        modalObserver.observe(el);
    });
} 