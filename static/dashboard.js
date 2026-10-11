/**
 * Dashboard JavaScript for Cybersecurity Training Platform
 * Handles interactive elements, data visualization, and user experience enhancements
 */

// Global variables
let refreshInterval;
let notificationTimeout;

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
    setupEventListeners();
    startAutoRefresh();
    initializeTooltips();
});

/**
 * Initialize dashboard components
 */
function initializeDashboard() {
    console.log('Initializing cybersecurity training dashboard...');
    
    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('fade-in');
    });
    
    // Initialize progress bars
    initializeProgressBars();
    
    // Load recent activity
    loadRecentActivity();
    
    // Setup real-time updates
    setupRealTimeUpdates();
}

/**
 * Setup event listeners for interactive elements
 */
function setupEventListeners() {
    // Modal events
    setupModalEvents();
    
    // Button click handlers
    setupButtonHandlers();
    
    // Form submission handlers
    setupFormHandlers();
    
    // Search and filter functionality
    setupSearchAndFilter();
    
    // Keyboard shortcuts
    setupKeyboardShortcuts();
}

/**
 * Setup modal event handlers
 */
function setupModalEvents() {
    // Clear forms when modals are closed
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.addEventListener('hidden.bs.modal', function() {
            const form = this.querySelector('form');
            if (form) {
                form.reset();
                clearFormErrors(form);
            }
        });
        
        modal.addEventListener('shown.bs.modal', function() {
            const firstInput = this.querySelector('input, select, textarea');
            if (firstInput) {
                firstInput.focus();
            }
        });
    });
}

/**
 * Setup button click handlers
 */
function setupButtonHandlers() {
    // Export button
    const exportBtn = document.querySelector('[href*="export"]');
    if (exportBtn) {
        exportBtn.addEventListener('click', function(e) {
            showNotification('Preparing export...', 'info');
            // Add loading state
            this.innerHTML = '<i data-feather="loader" class="me-1"></i>Exporting...';
            this.classList.add('loading');
        });
    }
    
    // Refresh buttons
    const refreshBtns = document.querySelectorAll('[onclick*="refresh"]');
    refreshBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            refreshDashboardData();
        });
    });
    
    // Campaign launch buttons
    const launchBtns = document.querySelectorAll('[onclick*="launch"]');
    launchBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const campaignName = this.closest('tr').querySelector('td strong').textContent;
            showLaunchConfirmation(campaignName, this.closest('form'));
        });
    });
}

/**
 * Setup form submission handlers
 */
function setupFormHandlers() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
                return false;
            }
            
            // Add loading state to submit button
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.innerHTML = '<i data-feather="loader" class="me-1"></i>Processing...';
                submitBtn.disabled = true;
            }
        });
    });
}

/**
 * Initialize progress bars with animation
 */
function initializeProgressBars() {
    const progressBars = document.querySelectorAll('.progress-bar');
    progressBars.forEach(bar => {
        const width = bar.style.width;
        bar.style.width = '0%';
        
        setTimeout(() => {
            bar.style.width = width;
        }, 500);
    });
}

/**
 * Setup search and filter functionality
 */
function setupSearchAndFilter() {
    // Table search functionality
    const searchInputs = document.querySelectorAll('[data-search-target]');
    searchInputs.forEach(input => {
        input.addEventListener('input', function() {
            const target = document.querySelector(this.getAttribute('data-search-target'));
            if (target) {
                filterTable(target, this.value);
            }
        });
    });
    
    // Filter buttons
    const filterBtns = document.querySelectorAll('[data-filter]');
    filterBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const filterValue = this.getAttribute('data-filter');
            const targetTable = this.getAttribute('data-target');
            applyTableFilter(targetTable, filterValue);
            
            // Update button states
            this.parentElement.querySelectorAll('.btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
        });
    });
}

/**
 * Setup keyboard shortcuts
 */
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + R for refresh
        if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
            e.preventDefault();
            refreshDashboardData();
        }
        
        // Ctrl/Cmd + N for new campaign
        if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
            e.preventDefault();
            const newCampaignBtn = document.querySelector('[data-bs-target="#createCampaignModal"]');
            if (newCampaignBtn) {
                newCampaignBtn.click();
            }
        }
        
        // Escape to close modals
        if (e.key === 'Escape') {
            const openModal = document.querySelector('.modal.show');
            if (openModal) {
                const modal = bootstrap.Modal.getInstance(openModal);
                if (modal) {
                    modal.hide();
                }
            }
        }
    });
}

/**
 * Filter table rows based on search term
 */
function filterTable(table, searchTerm) {
    const rows = table.querySelectorAll('tbody tr');
    const term = searchTerm.toLowerCase();
    
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        const shouldShow = text.includes(term);
        row.style.display = shouldShow ? '' : 'none';
    });
    
    // Update "no results" message
    updateNoResultsMessage(table, rows, searchTerm);
}

/**
 * Apply filter to table based on criteria
 */
function applyTableFilter(tableSelector, filterValue) {
    const table = document.querySelector(tableSelector);
    if (!table) return;
    
    const rows = table.querySelectorAll('tbody tr');
    
    rows.forEach(row => {
        let shouldShow = true;
        
        if (filterValue !== 'all') {
            // Implement specific filter logic based on your needs
            const statusCell = row.querySelector('[data-status]');
            if (statusCell) {
                shouldShow = statusCell.getAttribute('data-status') === filterValue;
            }
        }
        
        row.style.display = shouldShow ? '' : 'none';
    });
}

/**
 * Update "no results" message for filtered tables
 */
function updateNoResultsMessage(table, rows, searchTerm) {
    const visibleRows = Array.from(rows).filter(row => row.style.display !== 'none');
    let noResultsRow = table.querySelector('.no-results-row');
    
    if (visibleRows.length === 0 && searchTerm) {
        if (!noResultsRow) {
            noResultsRow = document.createElement('tr');
            noResultsRow.className = 'no-results-row';
            noResultsRow.innerHTML = `
                <td colspan="100%" class="text-center py-4 text-muted">
                    <i data-feather="search" class="me-2"></i>
                    No results found for "${searchTerm}"
                </td>
            `;
            table.querySelector('tbody').appendChild(noResultsRow);
            feather.replace();
        }
    } else if (noResultsRow) {
        noResultsRow.remove();
    }
}

/**
 * Start auto-refresh functionality
 */
function startAutoRefresh() {
    // Clear any existing interval before starting a new one
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }

    // Auto-refresh every 2 minutes
    refreshInterval = setInterval(() => {
        refreshDashboardData();
    }, 120000);
}

// Single visibility listener registered once at module level
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        if (refreshInterval) {
            clearInterval(refreshInterval);
            refreshInterval = null;
        }
    } else {
        startAutoRefresh();
    }
});

/**
 * Refresh dashboard data
 */
function refreshDashboardData() {
    console.log('Refreshing dashboard data...');
    
    // Add visual indicator
    const refreshBtn = document.querySelector('[onclick*="refresh"]');
    if (refreshBtn) {
        refreshBtn.innerHTML = '<i data-feather="refresh-cw" class="me-1"></i>Refreshing...';
        refreshBtn.disabled = true;
    }
    
    // In a real implementation, this would fetch new data via AJAX
    // For now, we'll just reload the page after a delay
    setTimeout(() => {
        window.location.reload();
    }, 1000);
}

/**
 * Load recent activity data
 */
function loadRecentActivity() {
    const activityFeed = document.querySelector('.activity-feed');
    if (!activityFeed) return;
    
    // Animate activity items
    const activityItems = activityFeed.querySelectorAll('.activity-item');
    activityItems.forEach((item, index) => {
        item.style.opacity = '0';
        item.style.transform = 'translateX(-20px)';
        
        setTimeout(() => {
            item.style.transition = 'all 0.3s ease';
            item.style.opacity = '1';
            item.style.transform = 'translateX(0)';
        }, index * 100);
    });
}

/**
 * Setup real-time updates
 */
function setupRealTimeUpdates() {
    // In a real implementation, this would use WebSockets or Server-Sent Events
    // For now, we'll simulate real-time updates
    
    // Update timestamps
    updateTimestamps();
    setInterval(updateTimestamps, 60000); // Update every minute
    
    // Simulate new notifications
    setTimeout(() => {
        simulateNewActivity();
    }, 10000);
}

/**
 * Update relative timestamps
 */
function updateTimestamps() {
    const timeElements = document.querySelectorAll('[data-timestamp]');
    timeElements.forEach(element => {
        const timestamp = parseInt(element.getAttribute('data-timestamp'));
        const relative = getRelativeTime(timestamp);
        element.textContent = relative;
    });
}

/**
 * Get relative time string
 */
function getRelativeTime(timestamp) {
    const now = Date.now();
    const diff = now - timestamp;
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);
    
    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    return `${days}d ago`;
}

/**
 * Simulate new activity for demo purposes
 */
function simulateNewActivity() {
    const activityFeed = document.querySelector('.activity-feed');
    if (!activityFeed) return;
    
    const newActivity = document.createElement('div');
    newActivity.className = 'activity-item mb-3 pb-3 border-bottom';
    newActivity.innerHTML = `
        <div class="d-flex align-items-start">
            <div class="flex-shrink-0">
                <div class="badge bg-info rounded-pill">
                    <i data-feather="mail" style="width: 12px; height: 12px;"></i>
                </div>
            </div>
            <div class="flex-grow-1 ms-3">
                <div class="small">
                    <strong>New campaign launched</strong>
                </div>
                <div class="text-muted small">
                    Just now
                </div>
            </div>
        </div>
    `;
    
    // Add with animation
    newActivity.style.opacity = '0';
    newActivity.style.transform = 'translateY(-20px)';
    activityFeed.insertBefore(newActivity, activityFeed.firstChild);
    
    setTimeout(() => {
        newActivity.style.transition = 'all 0.3s ease';
        newActivity.style.opacity = '1';
        newActivity.style.transform = 'translateY(0)';
        feather.replace();
    }, 100);
    
    // Show notification
    showNotification('New campaign activity detected', 'info');
}

/**
 * Show campaign launch confirmation
 */
function showLaunchConfirmation(campaignName, form) {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.innerHTML = `
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">
                        <i data-feather="send" class="me-2"></i>
                        Launch Campaign
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="alert alert-warning">
                        <i data-feather="alert-triangle" class="me-2"></i>
                        <strong>Confirm Campaign Launch</strong>
                    </div>
                    <p>You are about to launch the campaign:</p>
                    <p class="fw-bold">"${campaignName}"</p>
                    <p>This will send phishing training emails to all active users. Are you sure you want to continue?</p>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-success" onclick="confirmLaunch(this)">
                        <i data-feather="send" class="me-1"></i>
                        Launch Campaign
                    </button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    const bootstrapModal = new bootstrap.Modal(modal);
    
    // Store form reference
    modal.formToSubmit = form;
    
    bootstrapModal.show();
    feather.replace();
    
    // Clean up when modal is hidden
    modal.addEventListener('hidden.bs.modal', function() {
        document.body.removeChild(modal);
    });
}

/**
 * Confirm campaign launch
 */
function confirmLaunch(button) {
    const modal = button.closest('.modal');
    const form = modal.formToSubmit;
    
    if (form) {
        form.submit();
    }
    
    const bootstrapModal = bootstrap.Modal.getInstance(modal);
    bootstrapModal.hide();
}

/**
 * Form validation
 */
function validateForm(form) {
    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            showFieldError(field, 'This field is required');
            isValid = false;
        } else {
            clearFieldError(field);
        }
    });
    
    // Email validation
    const emailFields = form.querySelectorAll('input[type="email"]');
    emailFields.forEach(field => {
        if (field.value && !isValidEmail(field.value)) {
            showFieldError(field, 'Please enter a valid email address');
            isValid = false;
        }
    });
    
    return isValid;
}

/**
 * Show field validation error
 */
function showFieldError(field, message) {
    clearFieldError(field);
    
    field.classList.add('is-invalid');
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    
    field.parentNode.appendChild(errorDiv);
}

/**
 * Clear field validation error
 */
function clearFieldError(field) {
    field.classList.remove('is-invalid');
    const errorDiv = field.parentNode.querySelector('.invalid-feedback');
    if (errorDiv) {
        errorDiv.remove();
    }
}

/**
 * Clear all form errors
 */
function clearFormErrors(form) {
    const invalidFields = form.querySelectorAll('.is-invalid');
    invalidFields.forEach(field => {
        clearFieldError(field);
    });
}

/**
 * Email validation
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Show notification
 */
function showNotification(message, type = 'info', duration = 5000) {
    // Clear existing notification
    if (notificationTimeout) {
        clearTimeout(notificationTimeout);
    }
    
    const existingNotification = document.querySelector('.notification-toast');
    if (existingNotification) {
        existingNotification.remove();
    }
    
    // Create notification
    const notification = document.createElement('div');
    notification.className = `notification-toast alert alert-${type} position-fixed`;
    notification.style.cssText = `
        top: 20px;
        right: 20px;
        z-index: 1060;
        min-width: 300px;
        max-width: 400px;
        opacity: 0;
        transform: translateX(100%);
        transition: all 0.3s ease;
    `;
    
    const iconMap = {
        success: 'check-circle',
        warning: 'alert-triangle',
        danger: 'alert-circle',
        info: 'info'
    };
    
    notification.innerHTML = `
        <div class="d-flex align-items-center">
            <i data-feather="${iconMap[type] || 'info'}" class="me-2"></i>
            <span>${message}</span>
            <button type="button" class="btn-close ms-auto" onclick="this.parentElement.parentElement.remove()"></button>
        </div>
    `;
    
    document.body.appendChild(notification);
    feather.replace();
    
    // Animate in
    setTimeout(() => {
        notification.style.opacity = '1';
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Auto remove
    notificationTimeout = setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 300);
    }, duration);
}

/**
 * Initialize tooltips
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Cleanup function for page unload
 */
window.addEventListener('beforeunload', function() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
    if (notificationTimeout) {
        clearTimeout(notificationTimeout);
    }
});

// Export functions for global access
window.dashboardUtils = {
    refreshDashboardData,
    showNotification,
    validateForm,
    filterTable,
    applyTableFilter
};
