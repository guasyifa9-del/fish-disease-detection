/**
 * Fish Disease Detection - Main JavaScript
 * Fungsi utilitas dan interaksi UI
 */

document.addEventListener('DOMContentLoaded', function () {

    // ===========================
    // Auto-dismiss flash alerts
    // ===========================
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        }, 5000); // 5 detik
    });

    // ===========================
    // Active nav link highlight
    // ===========================
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');

    navLinks.forEach(function (link) {
        const href = link.getAttribute('href');
        if (href === currentPath) {
            link.classList.add('active');
        } else if (currentPath === '/' && href === '/') {
            link.classList.add('active');
        }
    });

    // ===========================
    // Tooltip initialization
    // ===========================
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipTriggerList.forEach(function (el) {
        new bootstrap.Tooltip(el);
    });

    // ===========================
    // Smooth scroll for anchors
    // ===========================
    document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });

    // ===========================
    // Image lazy loading fallback
    // ===========================
    const images = document.querySelectorAll('img[loading="lazy"]');
    if ('loading' in HTMLImageElement.prototype) {
        // Browser supports native lazy loading
    } else {
        // Fallback: load images immediately
        images.forEach(function (img) {
            img.src = img.dataset.src || img.src;
        });
    }

    console.log('Fish Disease Detection - App loaded successfully.');
});
