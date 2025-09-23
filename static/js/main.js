// RekoBuku JavaScript Functions

// Toggle favorite book
async function toggleFavorite(bookId) {
    const button = document.querySelector(`.book-favorite-btn[data-book-id="${bookId}"]`);
    if (!button) return;
    
    // Add loading state
    button.classList.add('btn-loading');
    button.disabled = true;
    
    try {
        const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
        const response = await fetch(`/toggle_favorite/${bookId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Update button appearance
            const icon = button.querySelector('i');
            const text = button.querySelector('.favorite-text');
            
            if (data.is_favorite) {
                button.classList.remove('btn-outline-danger');
                button.classList.add('btn-danger');
                icon.classList.remove('far');
                icon.classList.add('fas');
                if (text) text.textContent = 'Hapus dari Favorit';
            } else {
                button.classList.remove('btn-danger');
                button.classList.add('btn-outline-danger');
                icon.classList.remove('fas');
                icon.classList.add('far');
                if (text) text.textContent = 'Tambahkan ke Favorit';
            }
            
            // Show success message
            showMessage(data.message, 'success');
        } else {
            showMessage(data.error || 'Terjadi kesalahan', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showMessage('Terjadi kesalahan koneksi', 'error');
    } finally {
        // Remove loading state
        button.classList.remove('btn-loading');
        button.disabled = false;
    }
}

// Show temporary message
function showMessage(message, type = 'info') {
    // Remove existing messages
    const existingMessages = document.querySelectorAll('.temp-message');
    existingMessages.forEach(msg => msg.remove());
    
    // Create new message
    const messageDiv = document.createElement('div');
    messageDiv.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show temp-message`;
    messageDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert at top of main content
    const main = document.querySelector('main');
    if (main) {
        const container = document.createElement('div');
        container.className = 'container mt-3';
        container.appendChild(messageDiv);
        main.insertBefore(container, main.firstChild);
    }
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (messageDiv.parentNode) {
            messageDiv.parentNode.remove();
        }
    }, 5000);
}

// Initialize tooltips and other Bootstrap components
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize Bootstrap popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.temp-message)');
    alerts.forEach(alert => {
        if (!alert.classList.contains('alert-danger')) {
            setTimeout(() => {
                const alertInstance = bootstrap.Alert.getOrCreateInstance(alert);
                if (alertInstance) {
                    alertInstance.close();
                }
            }, 5000);
        }
    });
});

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Add loading states to form submissions
document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', function() {
        const submitButton = form.querySelector('button[type="submit"], input[type="submit"]');
        if (submitButton) {
            submitButton.classList.add('btn-loading');
            submitButton.disabled = true;
        }
    });
});