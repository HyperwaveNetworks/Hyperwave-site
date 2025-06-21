/**
 * Mobile Menu Functionality for Hyperwave Networks
 * Handles mobile navigation, dropdowns, and responsive interactions
 */

document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu elements
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const navLinks = document.querySelector('.nav-links');
    const dropdownToggles = document.querySelectorAll('.has-dropdown > a');
    const body = document.body;
    
    // Create mobile menu overlay
    const overlay = document.createElement('div');
    overlay.className = 'mobile-menu-overlay';
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.5);
        z-index: 999;
        opacity: 0;
        visibility: hidden;
        transition: all 0.3s ease;
    `;
    document.body.appendChild(overlay);
    
    // Toggle mobile menu
    if (mobileMenuToggle && navLinks) {
        mobileMenuToggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const isActive = navLinks.classList.contains('active');
            
            if (isActive) {
                closeMobileMenu();
            } else {
                openMobileMenu();
            }
        });
    }
    
    // Open mobile menu
    function openMobileMenu() {
        navLinks.classList.add('active');
        overlay.style.opacity = '1';
        overlay.style.visibility = 'visible';
        body.style.overflow = 'hidden';
        
        // Add hamburger animation
        if (mobileMenuToggle) {
            mobileMenuToggle.classList.add('active');
        }
    }
    
    // Close mobile menu
    function closeMobileMenu() {
        navLinks.classList.remove('active');
        overlay.style.opacity = '0';
        overlay.style.visibility = 'hidden';
        body.style.overflow = '';
        
        // Remove hamburger animation
        if (mobileMenuToggle) {
            mobileMenuToggle.classList.remove('active');
        }
        
        // Close all dropdowns
        dropdownToggles.forEach(toggle => {
            toggle.parentElement.classList.remove('active');
        });
    }
    
    // Close menu when clicking overlay
    overlay.addEventListener('click', closeMobileMenu);
    
    // Handle dropdown toggles in mobile
    dropdownToggles.forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            // Only prevent default on mobile
            if (window.innerWidth <= 768) {
                e.preventDefault();
                e.stopPropagation();
                
                const parentLi = this.parentElement;
                const isActive = parentLi.classList.contains('active');
                
                // Close all other dropdowns
                dropdownToggles.forEach(otherToggle => {
                    if (otherToggle !== this) {
                        otherToggle.parentElement.classList.remove('active');
                    }
                });
                
                // Toggle current dropdown
                if (isActive) {
                    parentLi.classList.remove('active');
                } else {
                    parentLi.classList.add('active');
                }
            }
        });
    });
    
    // Close mobile menu on window resize
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            closeMobileMenu();
        }
    });
    
    // Close mobile menu when clicking on nav links
    const navLinkItems = document.querySelectorAll('.nav-links a:not(.has-dropdown > a)');
    navLinkItems.forEach(link => {
        link.addEventListener('click', function() {
            if (window.innerWidth <= 768) {
                closeMobileMenu();
            }
        });
    });
    
    // Improve touch interactions on mobile
    if ('ontouchstart' in window) {
        document.documentElement.classList.add('touch-device');
        
        // Add touch feedback to buttons
        const buttons = document.querySelectorAll('button, .btn, .nav-links a');
        buttons.forEach(button => {
            button.addEventListener('touchstart', function() {
                this.style.transform = 'scale(0.98)';
                this.style.transition = 'transform 0.1s ease';
            });
            
            button.addEventListener('touchend', function() {
                setTimeout(() => {
                    this.style.transform = '';
                }, 100);
            });
        });
    }
    
    // Smooth scrolling for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            const target = document.querySelector(href);
            
            if (target) {
                e.preventDefault();
                
                // Close mobile menu first
                if (window.innerWidth <= 768) {
                    closeMobileMenu();
                    
                    // Wait for menu to close before scrolling
                    setTimeout(() => {
                        target.scrollIntoView({
                            behavior: 'smooth',
                            block: 'start'
                        });
                    }, 300);
                } else {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });
    
    // Handle form responsiveness
    const contactForms = document.querySelectorAll('.contact-form');
    contactForms.forEach(form => {
        const formGroups = form.querySelectorAll('.form-group');
        
        function adjustFormLayout() {
            if (window.innerWidth <= 768) {
                formGroups.forEach(group => {
                    group.style.width = '100%';
                    group.style.marginBottom = '1.5rem';
                });
            }
        }
        
        adjustFormLayout();
        window.addEventListener('resize', adjustFormLayout);
    });
    
    // Optimize images for mobile
    const images = document.querySelectorAll('img');
    images.forEach(img => {
        // Add loading="lazy" for better performance
        if (!img.hasAttribute('loading')) {
            img.setAttribute('loading', 'lazy');
        }
        
        // Handle image load errors
        img.addEventListener('error', function() {
            this.style.display = 'none';
        });
    });
    
    // Handle service cards responsive layout
    function adjustServiceCards() {
        const serviceCards = document.querySelectorAll('.service-card');
        const serviceGrid = document.querySelector('.services-grid');
        
        if (window.innerWidth <= 768 && serviceGrid) {
            serviceGrid.style.gridTemplateColumns = '1fr';
            serviceGrid.style.gap = '1.5rem';
        }
    }
    
    adjustServiceCards();
    window.addEventListener('resize', adjustServiceCards);
});

// Utility function to check if device is mobile
function isMobileDevice() {
    return window.innerWidth <= 768;
}

// Add mobile-specific styles dynamically
if (isMobileDevice()) {
    document.documentElement.classList.add('mobile-device');
    
    // Disable hover effects on mobile
    const style = document.createElement('style');
    style.textContent = `
        .mobile-device *:hover {
            /* Reset hover styles on mobile */
        }
    `;
    document.head.appendChild(style);
} 