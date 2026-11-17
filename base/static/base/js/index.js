document.addEventListener('DOMContentLoaded', () => {
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
    const carousel = document.querySelector('.slider-container');

    if (carousel) {
        const slides = Array.from(carousel.querySelectorAll('.slide'));
        const dots = Array.from(carousel.querySelectorAll('.dot'));
        const previousButton = carousel.querySelector('.prev-slide');
        const nextButton = carousel.querySelector('.next-slide');
        let activeIndex = Math.max(0, slides.findIndex(slide => slide.classList.contains('active')));
        let timerId;

        function showSlide(index) {
            activeIndex = (index + slides.length) % slides.length;
            slides.forEach((slide, slideIndex) => {
                const isActive = slideIndex === activeIndex;
                slide.classList.toggle('active', isActive);
                slide.setAttribute('aria-hidden', String(!isActive));
            });
            const heroActions = carousel.querySelector('.hero-actions');
            const activeContent = slides[activeIndex]?.querySelector('.slide-content');
            if (heroActions && activeContent && heroActions.parentElement !== activeContent) {
                activeContent.append(heroActions);
            }
            dots.forEach((dot, dotIndex) => {
                const isActive = dotIndex === activeIndex;
                dot.classList.toggle('active', isActive);
                if (isActive) dot.setAttribute('aria-current', 'true');
                else dot.removeAttribute('aria-current');
            });
        }

        function stopSlideshow() {
            window.clearInterval(timerId);
            timerId = undefined;
        }

        function startSlideshow() {
            stopSlideshow();
            if (slides.length > 1 && !reducedMotion.matches && !document.hidden) {
                timerId = window.setInterval(() => showSlide(activeIndex + 1), 6000);
            }
        }

        if (slides.length) {
            previousButton?.addEventListener('click', () => {
                showSlide(activeIndex - 1);
                startSlideshow();
            });
            nextButton?.addEventListener('click', () => {
                showSlide(activeIndex + 1);
                startSlideshow();
            });
            dots.forEach((dot, index) => {
                dot.addEventListener('click', () => {
                    showSlide(index);
                    startSlideshow();
                });
            });

            carousel.addEventListener('mouseenter', stopSlideshow);
            carousel.addEventListener('mouseleave', startSlideshow);
            carousel.addEventListener('focusin', stopSlideshow);
            carousel.addEventListener('focusout', event => {
                if (!carousel.contains(event.relatedTarget)) startSlideshow();
            });
            document.addEventListener('visibilitychange', () => {
                if (document.hidden) stopSlideshow();
                else startSlideshow();
            });
            reducedMotion.addEventListener?.('change', startSlideshow);

            let touchStartX = null;
            carousel.addEventListener('touchstart', event => {
                touchStartX = event.changedTouches[0]?.clientX ?? null;
            }, { passive: true });
            carousel.addEventListener('touchend', event => {
                const touchEndX = event.changedTouches[0]?.clientX;
                if (touchStartX === null || touchEndX === undefined) return;
                const swipeDistance = touchEndX - touchStartX;
                touchStartX = null;
                if (Math.abs(swipeDistance) < 50) return;
                showSlide(activeIndex + (swipeDistance < 0 ? 1 : -1));
                startSlideshow();
            }, { passive: true });

            showSlide(activeIndex);
            startSlideshow();
        }
    }

    const loadMoreButton = document.getElementById('load-more-btn');
    const featuredGrid = document.getElementById('featured-products-grid');
    if (loadMoreButton && featuredGrid) {
        loadMoreButton.addEventListener('click', () => {
            const hiddenCards = Array.from(featuredGrid.querySelectorAll('.product-card[hidden]'));
            hiddenCards.forEach(card => card.removeAttribute('hidden'));
            loadMoreButton.remove();

            if (hiddenCards[0]) {
                hiddenCards[0].focus({ preventScroll: true });
                hiddenCards[0].scrollIntoView({
                    behavior: reducedMotion.matches ? 'auto' : 'smooth',
                    block: 'center',
                });
            }
        });
    }

    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', event => {
            const targetSelector = anchor.getAttribute('href');
            if (!targetSelector || targetSelector === '#') return;

            const target = document.querySelector(targetSelector);
            if (!target) return;

            event.preventDefault();
            target.scrollIntoView({
                behavior: reducedMotion.matches ? 'auto' : 'smooth',
            });
        });
    });
});
