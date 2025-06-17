document.addEventListener('DOMContentLoaded', function() {
    // Smooth scrolling for navigation links
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');

    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();

            const targetId = this.getAttribute('href').substring(1);
            const targetSection = document.getElementById(targetId);

            if (targetSection) {
                const offsetTop = targetSection.offsetTop - 80; // Account for fixed navbar

                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });

                // Update active nav link
                updateActiveNavLink(this);

                // Close mobile menu if open
                const navbarCollapse = document.querySelector('.navbar-collapse');
                if (navbarCollapse.classList.contains('show')) {
                    bootstrap.Collapse.getInstance(navbarCollapse).hide();
                }
            }
        });
    });

    // Update active nav link based on scroll position
    function updateActiveNavLink(activeLink = null) {
        navLinks.forEach(link => {
            link.classList.remove('active');
        });

        if (activeLink) {
            activeLink.classList.add('active');
        } else {
            // Auto-detect based on scroll position
            const sections = ['home', 'portfolio', 'about', 'contact'];
            const scrollPosition = window.scrollY + 100;

            for (let i = sections.length - 1; i >= 0; i--) {
                const section = document.getElementById(sections[i]);
                if (section && scrollPosition >= section.offsetTop) {
                    const correspondingLink = document.querySelector(`a[href="#${sections[i]}"]`);
                    if (correspondingLink) {
                        correspondingLink.classList.add('active');
                    }
                    break;
                }
            }
        }
    }

    // Navbar background change on scroll
    const navbar = document.querySelector('.navbar');

    function handleNavbarScroll() {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }

        // Update active nav link based on scroll
        updateActiveNavLink();
    }

    window.addEventListener('scroll', handleNavbarScroll);

    // Initial call to set correct navbar state
    handleNavbarScroll();

    // Animate progress bars when they come into view
    const progressBars = document.querySelectorAll('.progress-bar');

    function animateProgressBars() {
        progressBars.forEach(bar => {
            const rect = bar.getBoundingClientRect();
            if (rect.top < window.innerHeight && rect.bottom > 0) {
                const width = bar.style.width;
                bar.style.width = '0%';
                setTimeout(() => {
                    bar.style.width = width;
                }, 100);
            }
        });
    }

    // Enhanced Intersection Observer for animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('loaded');

                // Animate progress bars if they're in the about section
                if (entry.target.closest('#about')) {
                    setTimeout(animateProgressBars, 200);
                }

                // Animate stats counter
                if (entry.target.classList.contains('stat-number')) {
                    animateCounter(entry.target);
                }

                // Stagger portfolio items animation
                if (entry.target.classList.contains('portfolio-item')) {
                    const portfolioItems = document.querySelectorAll('.portfolio-item');
                    portfolioItems.forEach((item, index) => {
                        setTimeout(() => {
                            item.style.transform = 'translateY(0) scale(1)';
                            item.style.opacity = '1';
                        }, index * 100);
                    });
                }

                // Animate section reveals
                if (entry.target.classList.contains('section-reveal')) {
                    entry.target.classList.add('revealed');
                }
            }
        });
    }, observerOptions);

    // Observe elements for animation
    const animatedElements = document.querySelectorAll('.portfolio-item, .about-content, .contact-form, .stat-number');
    animatedElements.forEach(el => {
        el.classList.add('loading');
        observer.observe(el);
    });

    // Add section reveal animations
    const sectionElements = document.querySelectorAll('section');
    sectionElements.forEach(section => {
        section.classList.add('section-reveal');
        observer.observe(section);
    });

    // Enhanced portfolio item interactions
    const portfolioCards = document.querySelectorAll('.portfolio-item');
    portfolioCards.forEach((card, index) => {
        // Add mouse move parallax effect
        card.addEventListener('mousemove', function(e) {
            if (window.innerWidth > 768) {
                const rect = this.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                const centerX = rect.width / 2;
                const centerY = rect.height / 2;

                const rotateX = (y - centerY) / 10;
                const rotateY = (centerX - x) / 10;

                this.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateZ(20px)`;
            }
        });

        card.addEventListener('mouseleave', function() {
            this.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) translateZ(0px)';
        });

        // Add click animation
        card.addEventListener('click', function(e) {
            // Create ripple effect
            const ripple = document.createElement('div');
            ripple.classList.add('click-ripple');

            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;

            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';

            this.appendChild(ripple);

            setTimeout(() => {
                ripple.remove();
            }, 600);
        });

        // Add initial stagger animation
        card.style.animationDelay = `${index * 0.1}s`;
    });

    // Counter animation for stats
    function animateCounter(element) {
        const target = parseInt(element.textContent);
        const increment = target / 100;
        let current = 0;

        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            element.textContent = Math.floor(current) + (element.textContent.includes('+') ? '+' : '');
        }, 20);
    }

    // Form validation and enhancement
    const contactForm = document.querySelector('.contact-form form');

    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            // Add loading state to submit button
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;

            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Sending...';
            submitBtn.disabled = true;

            // Reset button after 3 seconds (form will redirect anyway)
            setTimeout(() => {
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            }, 3000);
        });

        // Real-time form validation
        const inputs = contactForm.querySelectorAll('input, textarea');
        inputs.forEach(input => {
            input.addEventListener('blur', validateField);
            input.addEventListener('input', clearValidation);
        });

        function validateField(e) {
            const field = e.target;
            const value = field.value.trim();

            // Remove existing validation classes
            field.classList.remove('is-valid', 'is-invalid');

            if (field.hasAttribute('required') && !value) {
                field.classList.add('is-invalid');
                return false;
            }

            if (field.type === 'email' && value) {
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(value)) {
                    field.classList.add('is-invalid');
                    return false;
                }
            }

            if (value) {
                field.classList.add('is-valid');
            }

            return true;
        }

        function clearValidation(e) {
            e.target.classList.remove('is-valid', 'is-invalid');
        }
    }

    // Auto-hide flash messages
    const flashMessages = document.querySelectorAll('.flash-messages .alert');
    flashMessages.forEach(message => {
        setTimeout(() => {
            if (message && message.parentNode) {
                const alert = new bootstrap.Alert(message);
                alert.close();
            }
        }, 5000); // Hide after 5 seconds
    });

    // Parallax effect for hero section (subtle)
    const hero = document.querySelector('.hero-section');

    function parallaxEffect() {
        const scrolled = window.pageYOffset;
        const rate = scrolled * -0.5;

        if (hero) {
            hero.style.transform = `translateY(${rate}px)`;
        }
    }

    // Throttle scroll events for better performance
    let ticking = false;

    function requestTick() {
        if (!ticking) {
            requestAnimationFrame(updateScroll);
            ticking = true;
        }
    }

    function updateScroll() {
        parallaxEffect();
        ticking = false;
    }

    window.addEventListener('scroll', requestTick);

    // Lazy loading for images
    const images = document.querySelectorAll('img[src]');

    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.classList.add('loaded');
                observer.unobserve(img);
            }
        });
    });

    images.forEach(img => {
        img.classList.add('loading');
        imageObserver.observe(img);
    });

    // Floating button visibility
    const floatingBtn = document.getElementById('backToTop');

    function toggleFloatingButton() {
        if (window.scrollY > 300) {
            floatingBtn.style.display = 'flex';
        } else {
            floatingBtn.style.display = 'none';
        }
    }

    window.addEventListener('scroll', toggleFloatingButton);
    toggleFloatingButton(); // Initial call

    // Add magnetic effect to buttons
    const magneticButtons = document.querySelectorAll('.btn, .floating-btn');

    magneticButtons.forEach(btn => {
        btn.addEventListener('mouseenter', function(e) {
            this.style.transform = 'translateY(-3px) scale(1.05)';
        });

        btn.addEventListener('mouseleave', function(e) {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });

    // Dynamic typing effect for hero subtitle
    const heroSubtitle = document.querySelector('.hero-subtitle');
    if (heroSubtitle) {
        const originalText = heroSubtitle.textContent;
        heroSubtitle.textContent = '';
        heroSubtitle.classList.add('typewriter');

        let i = 0;
        function typeWriter() {
            if (i < originalText.length) {
                heroSubtitle.textContent += originalText.charAt(i);
                i++;
                setTimeout(typeWriter, 100);
            } else {
                heroSubtitle.classList.remove('typewriter');
            }
        }

        setTimeout(typeWriter, 1000);
    }

    // Cursor trail effect
    let trail = [];
    const maxTrail = 20;

    function createTrailDot(x, y) {
        const dot = document.createElement('div');
        dot.className = 'cursor-trail';
        dot.style.left = x + 'px';
        dot.style.top = y + 'px';
        document.body.appendChild(dot);

        trail.push(dot);

        if (trail.length > maxTrail) {
            const oldDot = trail.shift();
            oldDot.remove();
        }

        setTimeout(() => {
            dot.style.opacity = '0';
            dot.style.transform = 'scale(0)';
        }, 100);

        setTimeout(() => {
            if (dot.parentNode) {
                dot.remove();
            }
        }, 500);
    }

    document.addEventListener('mousemove', (e) => {
        if (window.innerWidth > 768) { // Only on desktop
            createTrailDot(e.clientX, e.clientY);
        }
    });

    // Random portfolio item animations
    const portfolioItemsMain = document.querySelectorAll('.portfolio-item');
    portfolioItemsMain.forEach((item, index) => {
        item.style.animationDelay = `${index * 0.2}s`;

        // Add glitch effect to project titles occasionally
        const title = item.querySelector('h4');
        if (title && Math.random() > 0.7) {
            title.classList.add('glitch-text');
        }

        // Add stagger animation to portfolio items
        item.style.opacity = '0';
        item.style.transform = 'translateY(30px)';
        setTimeout(() => {
            item.style.transition = 'all 0.8s ease';
            item.style.opacity = '1';
            item.style.transform = 'translateY(0)';
        }, index * 150);
    });

    // Interactive tech stack items
    const techItems = document.querySelectorAll('.tech-item');
    techItems.forEach(item => {
        item.addEventListener('click', function() {
            this.style.transform = 'scale(1.2) rotate(5deg)';
            setTimeout(() => {
                this.style.transform = 'scale(1) rotate(0deg)';
            }, 200);
        });
    });

    console.log('🚀 Unique portfolio loaded with style!');
});

// Utility function to debounce events
function debounce(func, wait, immediate) {
    let timeout;
    return function executedFunction() {
        const context = this;
        const args = arguments;
        const later = function() {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    };
}

// Smooth reveal animation for sections
function revealSection(entries, observer) {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('revealed');
            observer.unobserve(entry.target);
        }
    });
}

// Error handling for external resources
window.addEventListener('error', function(e) {
    if (e.target.tagName === 'IMG') {
        console.warn('Image failed to load:', e.target.src);
        // Could add a placeholder image here
    }
});

// Performance monitoring
if ('performance' in window) {
    window.addEventListener('load', function() {
        setTimeout(function() {
            const perfData = performance.getEntriesByType('navigation')[0];
            console.log('Page load time:', perfData.loadEventEnd - perfData.fetchStart, 'ms');
        }, 0);
    });
}

// Visitor tracking
function trackVisitorData() {
    try {
        const visitorData = {
            screen_resolution: `${screen.width}x${screen.height}`,
            visit_duration: Math.floor((Date.now() - window.pageLoadTime) / 1000)
        };

        fetch('/api/track-visitor', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(visitorData)
        }).catch(console.error);
    } catch (error) {
        console.error('Error tracking visitor data:', error);
    }
}

// Track page load time
window.pageLoadTime = Date.now();

// Track visitor data on page load
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(trackVisitorData, 5000); // Track after 5 seconds
});

// Track when user leaves the page
window.addEventListener('beforeunload', trackVisitorData);

// Fix duplicate declaration error - Remove duplicate portfolioItems declaration
const portfolioElements = document.querySelectorAll('.portfolio-item');

// Portfolio item animations
portfolioElements.forEach((item, index) => {
    item.style.animationDelay = `${index * 0.2}s`;

    // Add glitch effect to project titles occasionally
    const title = item.querySelector('h4');
    if (title && Math.random() > 0.7) {
        title.classList.add('glitch-text');
    }

    // Add stagger animation to portfolio items
    item.style.opacity = '0';
    item.style.transform = 'translateY(30px)';
    setTimeout(() => {
        item.style.transition = 'all 0.8s ease';
        item.style.opacity = '1';
        item.style.transform = 'translateY(0)';
    }, index * 150);
});