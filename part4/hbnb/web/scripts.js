const PLACE_ICONS = ['🏡','🏰','🌊','🏔️','🌴','🏙️','🌿','🏛️'];
const PLACE_COLORS = [
    'linear-gradient(135deg,#1a1a2e,#16213e)',
    'linear-gradient(135deg,#1a2a1a,#0d1f0d)',
    'linear-gradient(135deg,#1a1a30,#0d0d26)',
    'linear-gradient(135deg,#2a1a1a,#1f0d0d)',
    'linear-gradient(135deg,#1a2a2a,#0d1f1f)',
    'linear-gradient(135deg,#2a2a1a,#1f1f0d)',
];

const DEMO_PLACES = [
    { id: 'demo-1', title: 'Appartement Bellecour', description: 'Magnifique appartement en plein cœur de Lyon, vue sur la place Bellecour.', price: 85 },
    { id: 'demo-2', title: 'Studio Croix-Rousse', description: 'Studio cosy dans le quartier des Canuts, idéal pour un séjour solo.', price: 48 },
    { id: 'demo-3', title: 'Loft Vieux-Lyon', description: 'Superbe loft dans une traboule rénovée du Vieux-Lyon, cachet unique.', price: 110 },
    { id: 'demo-4', title: 'Maison avec jardin', description: 'Grande maison avec jardin privé, parfaite pour les familles.', price: 120 },
    { id: 'demo-5', title: 'Villa Beaujolais', description: 'Villa de charme au cœur des vignes du Beaujolais, calme et nature.', price: 200 },
    { id: 'demo-6', title: 'Appartement Part-Dieu', description: 'Appartement moderne proche de la gare Part-Dieu, idéal pour les voyageurs.', price: 70 },
    { id: 'demo-7', title: 'Chalet Montagne', description: 'Chalet authentique avec vue panoramique sur les Alpes.', price: 150 },
    { id: 'demo-8', title: 'Studio Confluence', description: 'Studio design dans le nouveau quartier Confluence, vue sur le Rhône.', price: 60 },
];

document.addEventListener('DOMContentLoaded', () => {

    // ── Login page ──
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            await loginUser(email, password);
        });
    }

    // ── Index page ──
    if (document.getElementById('places-list')) {
        checkAuthentication();
        document.getElementById('price-filter').addEventListener('change', (e) => {
            const max = e.target.value;
            document.querySelectorAll('.place-card').forEach(card => {
                card.style.display = (max === 'all' || parseFloat(card.dataset.price) <= parseFloat(max))
                    ? 'block' : 'none';
            });
        });
    }

    // ── Place details page ──
    if (document.getElementById('place-details')) {
        const placeId = getPlaceIdFromURL();
        const token = getCookie('token');
        setLoginVisibility(token);
        const addReview = document.getElementById('add-review');
        if (addReview) {
            addReview.style.display = token ? 'block' : 'none';
            const link = addReview.querySelector('a');
            if (link && placeId) link.href = `add_review.html?id=${placeId}`;
        }
        if (placeId) fetchPlaceDetails(token, placeId);
    }

    // ── Add review page ──
    const reviewForm = document.getElementById('review-form');
    if (reviewForm) {
        const token = getCookie('token');
        if (!token) { window.location.href = 'index.html'; return; }
        setLoginVisibility(token);
        const placeId = getPlaceIdFromURL();
        reviewForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const rating = parseInt(document.getElementById('rating').value);
            const comment = document.getElementById('comment').value;
            await submitReview(token, placeId, rating, comment);
        });
    }
});

function setLoginVisibility(token) {
    const loginLink = document.getElementById('login-link');
    if (loginLink) loginLink.style.display = token ? 'none' : 'block';
    const navLoginLink = document.getElementById('nav-login-link');
    if (navLoginLink) navLoginLink.style.display = token ? 'none' : 'block';
}

async function loginUser(email, password) {
    const response = await fetch('http://127.0.0.1:5000/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
    });
    if (response.ok) {
        const data = await response.json();
        document.cookie = `token=${data.access_token}; path=/`;
        window.location.href = 'index.html';
    } else {
        alert('Login failed: ' + response.statusText);
    }
}

function getCookie(name) {
    return document.cookie.split(';').reduce((acc, c) => {
        const [k, v] = c.trim().split('=');
        return k === name ? decodeURIComponent(v) : acc;
    }, null);
}

function checkAuthentication() {
    const token = getCookie('token');
    setLoginVisibility(token);
    if (token) fetchPlaces(token);
    else displayPlaces(DEMO_PLACES); // affiche les démos si non connecté
}

async function fetchPlaces(token) {
    try {
        const response = await fetch('http://127.0.0.1:5000/api/v1/places/', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const places = await response.json();
        // Si l'API renvoie une liste vide, on affiche les démos
        displayPlaces(places.length ? places : DEMO_PLACES);
    } catch (e) {
        // Si l'API est hors ligne, on affiche les démos
        displayPlaces(DEMO_PLACES);
    }
}

function displayPlaces(places) {
    const list = document.getElementById('places-list');
    list.innerHTML = '';
    if (!places.length) {
        list.innerHTML = `<div class="empty-state"><p>No places available yet.</p></div>`;
        return;
    }
    places.forEach((place, i) => {
        const card = document.createElement('div');
        card.classList.add('place-card');
        card.dataset.price = place.price ?? 0;
        const icon = PLACE_ICONS[i % PLACE_ICONS.length];
        const bg = PLACE_COLORS[i % PLACE_COLORS.length];
        card.innerHTML = `
            <div class="place-card-img-placeholder" style="background:${bg}">${icon}</div>
            <div class="place-card-body">
                <h3>${place.title}</h3>
                <p>${place.description || 'A wonderful place to stay.'}</p>
            </div>
            <div class="place-card-footer">
                <div class="place-price">$${place.price ?? 'N/A'} <span>/ night</span></div>
                <a href="place.html?id=${place.id}" class="details-button">View →</a>
            </div>
        `;
        list.appendChild(card);
    });
}

function getPlaceIdFromURL() {
    return new URLSearchParams(window.location.search).get('id');
}

async function fetchPlaceDetails(token, placeId) {
    // Vérifie d'abord si c'est un lieu de démo
    if (placeId.startsWith('demo-')) {
        const place = DEMO_PLACES.find(p => p.id === placeId);
        if (place) { displayPlaceDetails(place); return; }
    }
    const headers = {};
    if (token) headers['Authorization'] = `Bearer ${token}`;
    const response = await fetch(`http://127.0.0.1:5000/api/v1/places/${placeId}`, { headers });
    if (!response.ok) return;
    const place = await response.json();
    displayPlaceDetails(place);
}

function displayPlaceDetails(place) {
    const section = document.getElementById('place-details');
    const stars = (r) => '★'.repeat(r) + '☆'.repeat(5 - r);
    section.innerHTML = `
        <div class="place-info">
            <h1>${place.title}</h1>
            <p><strong>Price per night</strong> — $${place.price ?? 'N/A'}</p>
            <p><strong>Description</strong> — ${place.description || 'No description available.'}</p>
            <p><strong>Amenities</strong> — ${
                place.amenities && place.amenities.length
                    ? place.amenities.map(a => a.name).join(' · ')
                    : 'None listed'
            }</p>
            <div class="reviews-section">
                <h2>Guest Reviews</h2>
                ${place.reviews && place.reviews.length
                    ? place.reviews.map(r => `
                        <div class="review-card">
                            <p><strong>${r.user_name || 'Anonymous'}</strong> &nbsp;${stars(r.rating)}</p>
                            <p>${r.text}</p>
                        </div>`).join('')
                    : '<p>No reviews yet. Be the first!</p>'
                }
            </div>
        </div>
    `;
}

async function submitReview(token, placeId, rating, text) {
    const response = await fetch('http://127.0.0.1:5000/api/v1/reviews/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ place_id: placeId, rating, text })
    });
    if (response.ok) {
        alert('Review submitted successfully!');
        document.getElementById('review-form').reset();
        if (placeId) window.location.href = `place.html?id=${placeId}`;
    } else {
        alert('Failed to submit review. Please try again.');
    }
}
