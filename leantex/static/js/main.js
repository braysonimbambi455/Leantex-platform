// Main JavaScript for Leantex Platform

// Initialize tooltips
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Add fade-in class to main content
    var mainContent = document.querySelector('main');
    if (mainContent) {
        mainContent.classList.add('fade-in');
    }
});

// Form validation
function validateForm(formId) {
    var form = document.getElementById(formId);
    if (!form) return true;

    var inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    var isValid = true;

    inputs.forEach(function(input) {
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
        }
    });

    return isValid;
}

// Confirm actions
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-KE', {
        style: 'currency',
        currency: 'KES',
        minimumFractionDigits: 2
    }).format(amount);
}

// Format date
function formatDate(dateString) {
    var options = { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    return new Date(dateString).toLocaleDateString('en-KE', options);
}

// Show loading spinner
function showLoading() {
    var loader = document.createElement('div');
    loader.className = 'spinner';
    loader.id = 'loading-spinner';
    document.body.appendChild(loader);
}

// Hide loading spinner
function hideLoading() {
    var loader = document.getElementById('loading-spinner');
    if (loader) {
        loader.remove();
    }
}

// Handle AJAX errors
function handleAjaxError(error) {
    console.error('AJAX Error:', error);
    alert('An error occurred. Please try again.');
}

// Smooth scroll to element
function smoothScroll(elementId) {
    var element = document.getElementById(elementId);
    if (element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}