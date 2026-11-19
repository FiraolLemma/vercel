document.addEventListener('DOMContentLoaded', () => {
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
    const carousel = document.querySelector('.slider-container');

    if (carousel) {
        const slides = Array.from(carousel.querySelectorAll('.slide'));
        const dots = Array.from(carousel.querySelectorAll('.dot'));
        const previousButton = carousel.querySelector('.prev-slide');
        const nextButton = carousel.querySelector('.next-slide');
        let activeIndex = Math.max(0, slides.findIndex(slide => slide.classList.contains('active')));
        if (window.matchMedia('(max-width: 384px)').matches) {
            const poultrySlideIndex = slides.findIndex(slide =>
                slide.querySelector('.hero-highlight')?.textContent.toLowerCase().includes('poultry')
            );
            if (poultrySlideIndex >= 0) activeIndex = poultrySlideIndex;
        }
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

    const categoryCards = Array.from(document.querySelectorAll('.category-section .category-card'));
    const initiallyOpenCategories = categoryCards.map(card => card.open);
    const smallScreen = window.matchMedia('(max-width: 384px)');

    function updateCategoryCards() {
        categoryCards.forEach((card, index) => {
            card.open = smallScreen.matches ? false : initiallyOpenCategories[index];
        });
    }

    if (categoryCards.length) {
        updateCategoryCards();
        if (smallScreen.addEventListener) {
            smallScreen.addEventListener('change', updateCategoryCards);
        } else {
            smallScreen.addListener(updateCategoryCards);
        }
    }

    const productGrid = document.getElementById('featured-products-grid');
    if (productGrid) {
        let productDots = null;
        let productDotButtons = [];
        let productScrollListenerAdded = false;

        function getVisibleCards() {
            return Array.from(productGrid.querySelectorAll('.product-card:not([hidden])'));
        }

        function setActiveProductDot(index) {
            productDotButtons.forEach((button, buttonIndex) => {
                if (buttonIndex === index) button.setAttribute('aria-current', 'true');
                else button.removeAttribute('aria-current');
            });
        }

        function updateProductDots() {
            const cards = getVisibleCards();
            if (!smallScreen.matches || cards.length < 2) {
                productDots?.remove();
                productDots = null;
                productDotButtons = [];
                return;
            }

            if (productDots && productDotButtons.length === cards.length) return;
            productDots?.remove();

            productDots = document.createElement('div');
            productDots.className = 'mobile-product-dots';
            productDots.setAttribute('role', 'group');
            productDots.setAttribute('aria-label', 'Choose a featured listing');
            productDotButtons = cards.map((card, index) => {
                const button = document.createElement('button');
                button.type = 'button';
                button.setAttribute('aria-label', `Show listing ${index + 1}`);
                button.addEventListener('click', () => {
                    productGrid.scrollTo({
                        left: card.offsetLeft - productGrid.offsetLeft,
                        behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth',
                    });
                    setActiveProductDot(index);
                });
                productDots.append(button);
                return button;
            });
            productGrid.insertAdjacentElement('afterend', productDots);

            if (!productScrollListenerAdded) {
                productGrid.addEventListener('scroll', () => {
                    const visibleCards = getVisibleCards();
                    if (!visibleCards.length || !productDotButtons.length) return;

                    const gridLeft = productGrid.getBoundingClientRect().left;
                    const activeIndex = visibleCards.reduce((closestIndex, card, index) => {
                        const closestCard = visibleCards[closestIndex];
                        return Math.abs(card.getBoundingClientRect().left - gridLeft)
                            < Math.abs(closestCard.getBoundingClientRect().left - gridLeft)
                            ? index
                            : closestIndex;
                    }, 0);
                    setActiveProductDot(activeIndex);
                }, { passive: true });
                productScrollListenerAdded = true;
            }

            setActiveProductDot(0);
        }

        updateProductDots();
        if (smallScreen.addEventListener) {
            smallScreen.addEventListener('change', updateProductDots);
        } else {
            smallScreen.addListener(updateProductDots);
        }

        new MutationObserver(updateProductDots).observe(productGrid, {
            attributes: true,
            attributeFilter: ['hidden'],
            childList: true,
            subtree: true,
        });
    }
});
