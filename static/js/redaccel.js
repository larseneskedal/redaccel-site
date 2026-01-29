// Smooth scroll for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            const offsetTop = target.offsetTop - 72;
            window.scrollTo({
                top: offsetTop,
                behavior: 'smooth'
            });
        }
    });
});

// Navbar scroll effect
const nav = document.getElementById('nav');

window.addEventListener('scroll', () => {
    const currentScroll = window.pageYOffset;
    
    if (currentScroll > 100) {
        nav.style.background = 'rgba(0, 0, 0, 0.95)';
        nav.style.borderBottomColor = 'rgba(26, 26, 26, 0.8)';
    } else {
        nav.style.background = 'rgba(0, 0, 0, 0.8)';
        nav.style.borderBottomColor = 'rgba(26, 26, 26, 1)';
    }
});

// Mobile menu toggle
const navToggle = document.getElementById('navToggle');
const navLinks = document.querySelector('.nav-links');
const navCta = document.querySelector('.nav-cta');

if (navToggle) {
    navToggle.addEventListener('click', () => {
        navLinks.classList.toggle('active');
        navCta.classList.toggle('active');
        navToggle.classList.toggle('active');
    });
}

// Linear-style reveal animations
const revealElements = document.querySelectorAll('.reveal');

const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry, index) => {
        if (entry.isIntersecting) {
            // Stagger animation delays for smooth reveal
            setTimeout(() => {
                entry.target.classList.add('revealed');
            }, index * 100);
            revealObserver.unobserve(entry.target);
        }
    });
}, {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
});

// Observe all reveal elements
revealElements.forEach(el => {
    revealObserver.observe(el);
});

// Booking modal + Calendly integration
const BOOKING_CALENDLY_URL = 'https://calendly.com/redaccel/30min';

const bookingModal = document.getElementById('bookingModal');
const bookingModalClose = document.getElementById('bookingModalClose');
const bookingCloseBtn = document.getElementById('bookingCloseBtn');
const bookingBackBtn = document.getElementById('bookingBackBtn');
const bookingLeadForm = document.getElementById('bookingLeadForm');
const bookingError = document.getElementById('bookingError');
const bookingConfirm = document.getElementById('bookingConfirm');
const calendlyInline = document.getElementById('calendlyInline');
const stepIndicators = document.querySelectorAll('[data-step-indicator]');

let bookingLeadData = null;
let bookingCalendlyInitialized = false;
let bookingSubmitInFlight = false;

function setBookingStep(step) {
    if (!bookingModal) return;
    const step1 = bookingModal.querySelector('.booking-step[data-step="1"]');
    const step2 = bookingModal.querySelector('.booking-step[data-step="2"]');
    if (step1 && step2) {
        step1.hidden = step !== 1;
        step2.hidden = step !== 2;
    }
    stepIndicators.forEach(el => {
        const elStep = parseInt(el.getAttribute('data-step-indicator'), 10);
        el.classList.toggle('modal-step-active', elStep === step);
    });
}

function openBookingModal() {
    if (!bookingModal) return;
    bookingModal.classList.add('is-open');
    bookingModal.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
    bookingSubmitInFlight = false;
    bookingCalendlyInitialized = false;
    if (bookingConfirm) bookingConfirm.hidden = true;
    if (bookingError) bookingError.textContent = '';
    setBookingStep(1);

    // Focus first input
    const firstInput = bookingModal.querySelector('#booking_name');
    if (firstInput) setTimeout(() => firstInput.focus(), 50);
}

function closeBookingModal() {
    if (!bookingModal) return;
    bookingModal.classList.remove('is-open');
    bookingModal.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
    setBookingStep(1);
}

async function ensureCalendlyLoaded() {
    if (window.Calendly) return;
    await new Promise((resolve, reject) => {
        const existing = document.querySelector('script[data-calendly-widget="true"]');
        if (existing) {
            existing.addEventListener('load', () => resolve(), { once: true });
            existing.addEventListener('error', () => reject(new Error('Failed to load Calendly')), { once: true });
            return;
        }
        const script = document.createElement('script');
        script.src = 'https://assets.calendly.com/assets/external/widget.js';
        script.async = true;
        script.setAttribute('data-calendly-widget', 'true');
        script.onload = () => resolve();
        script.onerror = () => reject(new Error('Failed to load Calendly'));
        document.head.appendChild(script);
    });
}

async function initCalendlyInline() {
    if (!calendlyInline) return;
    if (bookingCalendlyInitialized) return;
    await ensureCalendlyLoaded();

    // Reset container (Calendly writes into it)
    calendlyInline.innerHTML = '';

    window.Calendly.initInlineWidget({
        url: BOOKING_CALENDLY_URL,
        parentElement: calendlyInline,
        prefill: {
            name: bookingLeadData?.name || '',
            email: bookingLeadData?.email || '',
        },
        utm: {
            utmCampaign: 'website_booking',
            utmSource: bookingLeadData?.found_us || 'website',
        }
    });

    bookingCalendlyInitialized = true;
}

function extractCalendlyUris(messageData) {
    const payload = messageData?.payload || {};
    const eventUri = payload?.event?.uri || payload?.event_uri || null;
    const inviteeUri = payload?.invitee?.uri || payload?.invitee_uri || null;
    return { eventUri, inviteeUri };
}

async function notifyBookingToServer({ eventUri, inviteeUri }) {
    if (bookingSubmitInFlight) return;
    bookingSubmitInFlight = true;

    try {
        const res = await fetch('/api/booking', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                lead: bookingLeadData,
                calendly: { event_uri: eventUri, invitee_uri: inviteeUri },
                page_url: window.location.href,
            }),
        });
        const json = await res.json().catch(() => ({}));
        if (!res.ok || !json.success) {
            throw new Error(json.error || 'Failed to record booking');
        }

        if (bookingConfirm) bookingConfirm.hidden = false;
    } catch (err) {
        console.error('Booking notify error:', err);
        if (bookingError) bookingError.textContent = 'Booked successfully, but we couldn’t notify our team automatically. Please email contact@redaccel.com.';
    }
}

// Open modal from any button/link with data-open-booking
document.querySelectorAll('[data-open-booking]').forEach(el => {
    el.addEventListener('click', (e) => {
        e.preventDefault();
        openBookingModal();
    });
});

// Close behaviors
if (bookingModalClose) bookingModalClose.addEventListener('click', closeBookingModal);
if (bookingCloseBtn) bookingCloseBtn.addEventListener('click', closeBookingModal);
if (bookingBackBtn) bookingBackBtn.addEventListener('click', () => {
    setBookingStep(1);
});

// Click outside dialog closes
if (bookingModal) {
    bookingModal.addEventListener('click', (e) => {
        if (e.target === bookingModal) closeBookingModal();
    });
}

// Esc closes
window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && bookingModal?.classList.contains('is-open')) {
        closeBookingModal();
    }
});

// Lead intake → Calendly
if (bookingLeadForm) {
    bookingLeadForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        if (!bookingLeadForm.checkValidity()) {
            bookingLeadForm.reportValidity();
            return;
        }

        const formData = new FormData(bookingLeadForm);
        bookingLeadData = {
            name: String(formData.get('name') || '').trim(),
            email: String(formData.get('email') || '').trim(),
            business: String(formData.get('business') || '').trim(),
            found_us: String(formData.get('found_us') || '').trim(),
            goals: String(formData.get('goals') || '').trim(),
        };

        if (bookingError) bookingError.textContent = '';
        setBookingStep(2);

        try {
            await initCalendlyInline();
        } catch (err) {
            console.error(err);
            if (bookingError) bookingError.textContent = 'Failed to load scheduling. Please refresh or email contact@redaccel.com.';
            setBookingStep(1);
        }
    });
}

// Calendly postMessage events (booking completed)
window.addEventListener('message', (e) => {
    const data = e.data;
    if (!data || typeof data !== 'object') return;
    if (!data.event || typeof data.event !== 'string') return;
    if (!data.event.startsWith('calendly.')) return;

    if (data.event === 'calendly.event_scheduled') {
        const { eventUri, inviteeUri } = extractCalendlyUris(data);
        if (eventUri || inviteeUri) {
            notifyBookingToServer({ eventUri, inviteeUri });
        }
    }
});

// Add active state to nav links based on scroll position
const sections = document.querySelectorAll('section[id]');
const navLinksAll = document.querySelectorAll('.nav-link');

window.addEventListener('scroll', () => {
    let current = '';
    
    sections.forEach(section => {
        const sectionTop = section.offsetTop - 150;
        const sectionHeight = section.clientHeight;
        
        if (window.pageYOffset >= sectionTop && window.pageYOffset < sectionTop + sectionHeight) {
            current = section.getAttribute('id');
        }
    });
    
    navLinksAll.forEach(link => {
        link.classList.remove('active');
        const href = link.getAttribute('href');
        if (href === `#${current}` || (current === '' && href === '#')) {
            link.classList.add('active');
        }
    });
});

// NOTE: Intentionally disabled the "fade on scroll" effect for the hero.
// Keeping the rest of the scroll behaviors (nav + active link highlighting) intact.
