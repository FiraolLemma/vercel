document.addEventListener('DOMContentLoaded', function() {
    initClock();
    initCurrentYear();
    initUnreadCount();
    initFormSubmissions();
    initButtonEffects();
    initMobileNavigation();
    initAccountDropdown();
    initSearch();
    initCategoryNavDropdowns(); // Added this line
});

function initClock() {
    const timeZone = 'Africa/Addis_Ababa';
    const formatter = new Intl.DateTimeFormat('en-CA', {
        timeZone,
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        hourCycle: 'h23'
    });

    function updateClock() {
        const clockElements = document.querySelectorAll('.live-clock');
        if (clockElements.length > 0) {
            const now = new Date();
            const parts = Object.fromEntries(
                formatter.formatToParts(now).map(({ type, value }) => [type, value])
            );
            const formattedDateTime = `${parts.year}-${parts.month}-${parts.day} ${parts.hour}:${parts.minute}`;

            clockElements.forEach(el => {
                el.textContent = formattedDateTime;
                el.dateTime = now.toISOString();
            });
        }
    }

    updateClock();
    setInterval(updateClock, 60000);
}

function initCurrentYear() {
    const currentYear = document.getElementById('current-year');
    if (currentYear) {
        currentYear.textContent = new Date().getFullYear();
    }
}

function initUnreadCount() {
    function fetchUnreadCount() {
        if (!window.UNREAD_COUNT_API_URL) return;

        fetch(window.UNREAD_COUNT_API_URL, {
            credentials: 'include'
        })
            .then(response => {
                if (!response.ok) throw new Error('Network response was not ok');
                return response.json();
            })
            .then(data => {
                const unreadBadge = document.getElementById('navbarUnread');
                if (unreadBadge) {
                    if (data.total_unread > 0) {
                        unreadBadge.textContent = data.total_unread > 9 ? '9+' : data.total_unread;
                        unreadBadge.style.display = 'flex';
                        unreadBadge.classList.add('pulse');
                    } else {
                        unreadBadge.style.display = 'none';
                        unreadBadge.classList.remove('pulse');
                    }
                }
            })
            .catch(error => {
                console.error('Error fetching unread count:', error);
            });
    }

    fetchUnreadCount();
    setInterval(fetchUnreadCount, 30000);
}

function initFormSubmissions() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.classList.add('loading');
                
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = `
                    <span class="spinner">
                        <i class="fas fa-spinner fa-spin"></i>
                    </span>
                    <span class="text">...</span>
                `;
                if (form.dataset.ajax === "true") {
                    e.preventDefault();
                    handleAjaxForm(form, submitBtn, originalText);
                }
            }
        });
    });
}

function handleAjaxForm(form, submitBtn, originalText) {
    const formData = new FormData(form);
    
    fetch(form.action, {
        method: form.method,
        body: formData,
        credentials: 'include'
    })
    .then(response => {
        if (!response.ok) throw new Error('Network response was not ok');
        return response.json();
    })
    .then(data => {
        if (data.redirect) {
            window.location.href = data.redirect;
        } else if (data.success) {
            showToast('Success!', data.message || 'Operation completed successfully', 'success');
            form.reset();
        }
    })
    .catch(error => {
        showToast('Error', error.message || 'Something went wrong', 'error');
    })
    .finally(() => {
        submitBtn.disabled = false;
        submitBtn.classList.remove('loading');
        submitBtn.innerHTML = originalText;
    });
}

function initButtonEffects() {
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('mousedown', () => {
            button.style.transform = 'translateY(1px) scale(0.98)';
        });
        
        button.addEventListener('mouseup', () => {
            button.style.transform = 'translateY(0) scale(1)';
        });
        
        button.addEventListener('mouseleave', () => {
            button.style.transform = 'translateY(0) scale(1)';
        });
    });
}

function initMobileNavigation() {
    const navToggle = document.getElementById('navToggle');
    const categoryNav = document.getElementById('categoryNav');
    if (!categoryNav) return;

    let navOverlay = document.querySelector('.nav-overlay');
    if (!navOverlay) {
        navOverlay = document.createElement('div');
        navOverlay.className = 'nav-overlay';
        navOverlay.setAttribute('aria-hidden', 'true');
        document.body.appendChild(navOverlay);
    }

    function setNavigationOpen(isOpen) {
        categoryNav.classList.toggle('active', isOpen);
        navOverlay.classList.toggle('active', isOpen);
        document.body.classList.toggle('no-scroll');
        navOverlay.setAttribute('aria-hidden', String(!isOpen));
        if (navToggle) {
            navToggle.setAttribute('aria-expanded', String(isOpen));
            const icon = navToggle.querySelector('.nav-toggle-icon');
            if (icon) icon.innerHTML = `<i class="fas fa-${isOpen ? 'times' : 'bars'}"></i>`;
        }
    }

    if (navToggle) {
        navToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            setNavigationOpen(!categoryNav.classList.contains('active'));
        });
    }

    const navCloseBtn = document.getElementById('navCloseBtn');
    if (navCloseBtn) navCloseBtn.addEventListener('click', () => setNavigationOpen(false));
    navOverlay.addEventListener('click', () => setNavigationOpen(false));

    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && categoryNav.classList.contains('active')) setNavigationOpen(false);
    });
}

function initAccountDropdown() {
    const dropdown = document.querySelector('.account-dropdown');
    const toggle = document.getElementById('accountDropdownToggle');
    const menu = document.getElementById('accountDropdown');
    if (!dropdown || !toggle || !menu) return;

    function setOpen(isOpen, returnFocus = false) {
        menu.hidden = !isOpen;
        toggle.setAttribute('aria-expanded', String(isOpen));
        if (returnFocus) toggle.focus();
    }

    toggle.addEventListener('click', function() {
        setOpen(menu.hidden);
    });

    menu.addEventListener('click', function(event) {
        if (event.target instanceof Element && event.target.closest('a, button[type="submit"]')) {
            setOpen(false);
        }
    });

    document.addEventListener('click', function(event) {
        if (!dropdown.contains(event.target)) setOpen(false);
    });

    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape' && !menu.hidden) setOpen(false, true);
    });
}

function initCategoryNavDropdowns() {
    // Toggle dropdowns
    const dropdownToggles = document.querySelectorAll('.dropdown-toggle');
    
    dropdownToggles.forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const parentItem = this.closest('.category-nav-item');
            const dropdown = this.nextElementSibling;
            if (!parentItem || !dropdown || !dropdown.classList.contains('category-nav-dropdown')) return;
            
            // Close other dropdowns
            document.querySelectorAll('.category-nav-dropdown.active').forEach(openDropdown => {
                if (openDropdown !== dropdown) {
                    openDropdown.classList.remove('active');
                    openDropdown.closest('.category-nav-item')?.classList.remove('active');
                    openDropdown.previousElementSibling?.setAttribute('aria-expanded', 'false');
                }
            });
            
            // Toggle current dropdown
            parentItem.classList.toggle('active');
            dropdown.classList.toggle('active');
            
            // Update aria attributes
            const isExpanded = dropdown.classList.contains('active');
            this.setAttribute('aria-expanded', isExpanded);
        });
    });
    
    // Close dropdowns when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.category-nav-item.has-dropdown')) {
            document.querySelectorAll('.category-nav-dropdown.active').forEach(dropdown => {
                dropdown.classList.remove('active');
                dropdown.closest('.category-nav-item')?.classList.remove('active');
                dropdown.previousElementSibling?.setAttribute('aria-expanded', 'false');
            });
        }
    });
    
    // Close dropdowns with Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            document.querySelectorAll('.category-nav-dropdown.active').forEach(dropdown => {
                dropdown.classList.remove('active');
                dropdown.closest('.category-nav-item')?.classList.remove('active');
                dropdown.previousElementSibling?.setAttribute('aria-expanded', 'false');
            });
        }
    });
    
    // Close navigation when a non-dropdown link is clicked
    const navLinks = document.querySelectorAll('.category-nav-link:not(.dropdown-toggle)');
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            const categoryNav = document.getElementById('categoryNav');
            const navOverlay = document.querySelector('.nav-overlay');
            
            if (categoryNav && navOverlay) {
                categoryNav.classList.remove('active');
                navOverlay.classList.remove('active');
                document.body.classList.remove('no-scroll');
                
                // Also close any open dropdowns
                document.querySelectorAll('.category-nav-dropdown.active').forEach(dropdown => {
                    dropdown.classList.remove('active');
                    dropdown.closest('.category-nav-item').classList.remove('active');
                });
                
                // Reset nav toggle
                const navToggle = document.getElementById('navToggle');
                if (navToggle) {
                    navToggle.setAttribute('aria-expanded', 'false');
                    const icon = navToggle.querySelector('.nav-toggle-icon');
                    if (icon) icon.innerHTML = '<i class="fas fa-bars"></i>';
                }
            }
        });
    });
}

function showToast(title, message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <div class="toast-header">
            <strong>${title}</strong>
            <button class="toast-close">&times;</button>
        </div>
        <div class="toast-body">${message}</div>
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('show');
    }, 10);
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, 5000);
    
    toast.querySelector('.toast-close').addEventListener('click', () => {
        toast.classList.remove('show');
        setTimeout(() => {
            toast.remove();
        }, 300);
    });
}

function addPulseAnimation() {
    const style = document.createElement('style');
    style.textContent = `
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); }
        }
        .pulse {
            animation: pulse 1s infinite;
        }
    `;
    document.head.appendChild(style);
}

addPulseAnimation();

function initSearch() {
    const searchField = document.getElementById('search-input');
    if (!searchField) return;

    document.addEventListener('keydown', function(e) {
        if (e.key === '/' && !['INPUT', 'TEXTAREA'].includes(document.activeElement?.tagName || '')) {
            e.preventDefault();
            searchField.focus();
        }
    });
}
