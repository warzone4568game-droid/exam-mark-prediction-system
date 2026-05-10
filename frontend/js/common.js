// Common configuration
const API_BASE_URL = '/api';

// Helper function to make API calls
async function apiCall(endpoint, options = {}) {
    try {
        const url = `${API_BASE_URL}${endpoint}`;
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });

        if (!response.ok) {
            throw new Error(`API Error: ${response.statusText}`);
        }

        return await response.json();
    } catch (error) {
        console.error('API Call Error:', error);
        showAlert('Error: ' + error.message, 'error');
        throw error;
    }
}

// Show alert message
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    alertDiv.style.position = 'fixed';
    alertDiv.style.top = '20px';
    alertDiv.style.right = '20px';
    alertDiv.style.zIndex = '1000';
    alertDiv.style.maxWidth = '400px';

    document.body.appendChild(alertDiv);

    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// Format date to readable format
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' };
    return new Date(dateString).toLocaleDateString('en-US', options);
}

// Format number to 2 decimal places
function formatNumber(number) {
    return parseFloat(number).toFixed(2);
}

// Check API health
async function checkHealth() {
    try {
        const response = await apiCall('/health');
        console.log('API Health:', response);
        return response.status === 'healthy';
    } catch (error) {
        console.error('API is not responding');
        return false;
    }
}

// Initialize common elements
document.addEventListener('DOMContentLoaded', () => {
    checkHealth().then(isHealthy => {
        if (!isHealthy) {
            console.warn('Backend API may not be available');
        }
    });
});
