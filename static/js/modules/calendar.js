/**
 * Calendar Manager Module
 * 
 * Integrates FullCalendar.js with the backend calendar API
 * Features: Multiple views, event filtering, mobile responsiveness
 */

class CalendarManager {
    constructor(options = {}) {
        this.options = {
            containerEl: null,
            apiEndpoint: '/api/calendar/events/',
            initialView: 'dayGridMonth',
            ...options
        };
        
        this.calendar = null;
        this.eventFilters = {
            program: true,
            application: true,
            deadline: true
        };
        
        this.init();
    }
    
    /**
     * Initialize calendar
     */
    init() {
        if (!this.options.containerEl) {
            console.error('Calendar: Container element not provided');
            return;
        }
        
        this.initCalendar();
        this.attachEventListeners();
    }
    
    /**
     * Initialize FullCalendar
     */
    initCalendar() {
        const self = this;
        
        this.calendar = new FullCalendar.Calendar(this.options.containerEl, {
            initialView: this.getInitialView(),
            headerToolbar: {
                left: 'prev,next today',
                center: 'title',
                right: 'dayGridMonth,timeGridWeek,timeGridDay,listMonth'
            },
            buttonText: {
                today: 'Today',
                month: 'Month',
                week: 'Week',
                day: 'Day',
                list: 'List'
            },
            height: 'auto',
            navLinks: true,
            editable: false,
            dayMaxEvents: true,
            events: function(info, successCallback, failureCallback) {
                self.fetchEvents(info.start, info.end, successCallback, failureCallback);
            },
            eventClick: function(info) {
                self.handleEventClick(info);
            },
            eventDidMount: function(info) {
                self.handleEventMount(info);
            },
            datesSet: function(info) {
                self.handleDatesSet(info);
            },
            loading: function(isLoading) {
                self.handleLoading(isLoading);
            },
            // Mobile responsiveness
            windowResize: function(view) {
                self.handleResize(view);
            },
            // Accessibility
            eventKeyBindings: {
                enter: function(e) {
                    self.handleEventClick(e);
                }
            }
        });
        
        this.calendar.render();
    }
    
    /**
     * Get initial view based on screen size
     */
    getInitialView() {
        if (window.innerWidth < 768) {
            return 'listMonth';
        }
        return this.options.initialView;
    }
    
    /**
     * Fetch events from API
     */
    async fetchEvents(start, end, successCallback, failureCallback) {
        try {
            const token = localStorage.getItem('seim_access_token');
            const params = new URLSearchParams({
                start: start.toISOString(),
                end: end.toISOString()
            });
            
            // Add filter parameters
            const types = [];
            if (this.eventFilters.program) types.push('program');
            if (this.eventFilters.application) types.push('application');
            if (this.eventFilters.deadline) types.push('deadline');
            
            if (types.length > 0 && types.length < 3) {
                params.append('type', types.join(','));
            }
            
            const response = await fetch(`${this.options.apiEndpoint}?${params}`, {
                headers: token ? {
                    'Authorization': `Bearer ${token}`
                } : {}
            });
            
            if (!response.ok) {
                throw new Error('Failed to fetch calendar events');
            }
            
            const events = await response.json();
            successCallback(events);
            
        } catch (error) {
            console.error('Calendar: Error fetching events', error);
            failureCallback(error);
            this.showError('Failed to load calendar events');
        }
    }
    
    /**
     * Handle event click
     */
    handleEventClick(info) {
        info.jsEvent.preventDefault();
        
        const event = info.event;
        
        // Navigate to event URL if available
        if (event.url) {
            window.location.href = event.url;
        } else {
            // Show event details modal
            this.showEventDetails(event);
        }
    }
    
    /**
     * Handle event mount (for styling)
     */
    handleEventMount(info) {
        const event = info.event;
        const el = info.el;
        
        // Add custom class name if provided
        if (event.extendedProps.className) {
            el.classList.add(event.extendedProps.className);
        }
        
        // Add tooltip
        el.title = event.title;
        el.setAttribute('aria-label', event.title);
    }
    
    /**
     * Handle dates change
     */
    handleDatesSet(info) {
        // Store view state
        localStorage.setItem('calendar_view', info.view.type);
    }
    
    /**
     * Handle loading state
     */
    handleLoading(isLoading) {
        const loader = document.getElementById('calendarLoading');
        if (loader) {
            if (isLoading) {
                loader.classList.remove('d-none');
            } else {
                loader.classList.add('d-none');
            }
        }
    }
    
    /**
     * Handle window resize
     */
    handleResize(view) {
        // Switch to list view on mobile
        if (window.innerWidth < 768 && this.calendar.view.type !== 'listMonth') {
            this.calendar.changeView('listMonth');
        } else if (window.innerWidth >= 768 && this.calendar.view.type === 'listMonth') {
            this.calendar.changeView('dayGridMonth');
        }
    }
    
    /**
     * Attach event listeners
     */
    attachEventListeners() {
        // Today button
        const todayBtn = document.getElementById('todayBtn');
        if (todayBtn) {
            todayBtn.addEventListener('click', () => {
                this.calendar.today();
            });
        }
        
        // Event filter checkboxes
        document.querySelectorAll('.event-filter').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                this.eventFilters[e.target.value] = e.target.checked;
                this.refreshEvents();
            });
        });
    }
    
    /**
     * Refresh calendar events
     */
    refreshEvents() {
        if (this.calendar) {
            this.calendar.refetchEvents();
        }
    }
    
    /**
     * Navigate to specific date
     */
    gotoDate(date) {
        if (this.calendar) {
            this.calendar.gotoDate(date);
        }
    }
    
    /**
     * Change calendar view
     */
    changeView(viewName) {
        if (this.calendar) {
            this.calendar.changeView(viewName);
        }
    }
    
    /**
     * Show event details modal
     */
    showEventDetails(event) {
        const modalHtml = `
            <div class="modal fade" id="eventDetailsModal" tabindex="-1" aria-labelledby="eventDetailsModalLabel" aria-hidden="true">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="eventDetailsModalLabel">${this.escapeHtml(event.title)}</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            <dl class="row">
                                <dt class="col-sm-3">Date:</dt>
                                <dd class="col-sm-9">${this.formatDate(event.start)}</dd>
                                
                                ${event.end ? `
                                    <dt class="col-sm-3">End:</dt>
                                    <dd class="col-sm-9">${this.formatDate(event.end)}</dd>
                                ` : ''}
                                
                                ${event.extendedProps.description ? `
                                    <dt class="col-sm-3">Description:</dt>
                                    <dd class="col-sm-9">${this.escapeHtml(event.extendedProps.description)}</dd>
                                ` : ''}
                            </dl>
                        </div>
                        <div class="modal-footer">
                            ${event.url ? `
                                <a href="${event.url}" class="btn btn-primary">View Details</a>
                            ` : ''}
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Remove existing modal
        const existing = document.getElementById('eventDetailsModal');
        if (existing) {
            existing.remove();
        }
        
        // Add and show modal
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        const modal = new bootstrap.Modal(document.getElementById('eventDetailsModal'));
        modal.show();
    }
    
    /**
     * Format date
     */
    formatDate(date) {
        return date.toLocaleDateString('en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }
    
    /**
     * Escape HTML
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    /**
     * Show error message
     */
    showError(message) {
        if (window.toastNotifications) {
            window.toastNotifications.error('Error', message);
        }
    }
    
    /**
     * Destroy calendar
     */
    destroy() {
        if (this.calendar) {
            this.calendar.destroy();
            this.calendar = null;
        }
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CalendarManager;
}

// Make available globally
window.CalendarManager = CalendarManager;

