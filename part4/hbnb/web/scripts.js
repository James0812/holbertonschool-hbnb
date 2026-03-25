const PLACE_ICONS = ['🏡','🏰','🌊','🏔️','🌴','🏙️','🌿','🏛️'];
const PLACE_COLORS = [
  'linear-gradient(135deg,#1a1a2e,#16213e)',
  'linear-gradient(135deg,#1a2a1a,#0d1f0d)',
  'linear-gradient(135deg,#1a1a30,#0d0d26)',
  'linear-gradient(135deg,#2a1a1a,#1f0d0d)',
  'linear-gradient(135deg,#1a2a2a,#0d1f1f)',
  'linear-gradient(135deg,#2a2a1a,#1f1f0d)',
];

document.addEventListener('DOMContentLoaded', () => {

  const token = getCookie('token');
  updateUserUI(token);

  // LOGIN PAGE
  const loginForm = document.getElementById('login-form');
  if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const email    = document.getElementById('email').value;
      const password = document.getElementById('password').value;
      await loginUser(email, password);
    });
  }

  // INDEX PAGE
  if (document.getElementById('places-list')) {
    checkAuthentication();
    document.getElementById('price-filter').addEventListener('change', (e) => {
      const max = e.target.value;
      document.querySelectorAll('.place-card').forEach(card => {
        card.style.display =
          (max === 'all' || parseFloat(card.dataset.price) <= parseFloat(max))
            ? 'block' : 'none';
      });
    });
  }

  // PLACE DETAILS PAGE
  if (document.getElementById('place-details')) {
    const placeId = getPlaceIdFromURL();
    const token   = getCookie('token');
    setLoginVisibility(token);
    const addReview = document.getElementById('add-review');
    if (addReview) {
      addReview.style.display = token ? 'block' : 'none';
      const link = addReview.querySelector('a');
      if (link && placeId) link.href = `add_review.html?id=${placeId}`;
    }
    if (placeId) fetchPlaceDetails(token, placeId);
  }

  // ADD REVIEW PAGE
  const reviewForm = document.getElementById('review-form');
  if (reviewForm) {
    const token = getCookie('token');
    if (!token) { window.location.href = 'index.html'; return; }
    setLoginVisibility(token);
    const placeId = getPlaceIdFromURL();
    reviewForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const rating  = parseInt(document.getElementById('rating').value);
      const comment = document.getElementById('comment').value;
      await submitReview(token, placeId, rating, comment);
    });
  }
});

// ── USER UI + LOGOUT ──────────────────────────────
function updateUserUI(token) {
  const loginLink      = document.getElementById('login-link');
  const userInfo       = document.getElementById('user-info');
  const usernameDisplay = document.getElementById('username-display');
  const logoutBtn      = document.getElementById('logout-btn');

  if (!loginLink || !userInfo) return;

  if (!token) {
    loginLink.style.display = 'block';
    userInfo.style.display  = 'none';
    return;
  }

  try {
    const payload  = JSON.parse(atob(token.split('.')[1]));
    const username = payload.username || payload.name || payload.first_name || payload.email || 'User';
    usernameDisplay.textContent = username;
  } catch (e) {
    usernameDisplay.textContent = 'User';
  }

  loginLink.style.display = 'none';
  userInfo.style.display  = 'flex';

  logoutBtn.addEventListener('click', () => {
    document.cookie = 'token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
    window.location.href = 'index.html';
  });
}

// ── AUTH ──────────────────────────────────────────
function setLoginVisibility(token) {
  const loginLink = document.getElementById('login-link');
  if (loginLink) loginLink.style.display = token ? 'none' : 'block';
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
    alert('Connexion échouée : ' + response.statusText);
  }
}

function getCookie(name) {
  return document.cookie.split(';').reduce((acc, c) => {
    const [k, v] = c.trim().split('=');
    return k === name ? decodeURIComponent(v) : acc;
  }, null);
}

// ── PLACES ───────────────────────────────────────
function checkAuthentication() {
  const token = getCookie('token');
  setLoginVisibility(token);
  fetchPlaces(token);
}

async function fetchPlaces(token) {
  try {
    const response = await fetch('http://127.0.0.1:5000/api/v1/places/', {
      headers: token ? { 'Authorization': `Bearer ${token}` } : {}
    });
    const places = await response.json();
    displayPlaces(places);
  } catch (e) {
    displayPlaces([]);
  }
}

function displayPlaces(places) {
  const list = document.getElementById('places-list');
  list.innerHTML = '';
  if (!places.length) {
    list.innerHTML = `<div class="empty-state"><p>🏚️ Aucun logement disponible pour le moment.</p></div>`;
    return;
  }
  places.forEach((place, i) => {
    const card = document.createElement('div');
    card.classList.add('place-card');
    card.dataset.price = place.price ?? 0;
    const icon = PLACE_ICONS[i % PLACE_ICONS.length];
    const bg   = PLACE_COLORS[i % PLACE_COLORS.length];
    card.innerHTML = `
      <div class="place-card-img-placeholder" style="background:${bg}">${icon}</div>
      <div class="place-card-body">
        <h3>${place.title}</h3>
        <p>${place.description || 'Un endroit merveilleux pour séjourner.'}</p>
      </div>
      <div class="place-card-footer">
        <div class="place-price">$${place.price ?? 'N/A'} <span>/ nuit</span></div>
        <a href="place.html?id=${place.id}" class="details-button">Voir →</a>
      </div>
    `;
    list.appendChild(card);
  });
}

// ── PLACE DETAILS ─────────────────────────────────
function getPlaceIdFromURL() {
  return new URLSearchParams(window.location.search).get('id');
}

async function fetchPlaceDetails(token, placeId) {
  const headers  = token ? { 'Authorization': `Bearer ${token}` } : {};
  const response = await fetch(`http://127.0.0.1:5000/api/v1/places/${placeId}`, { headers });
  if (!response.ok) return;
  const place = await response.json();
  displayPlaceDetails(place);
}

function displayPlaceDetails(place) {
  // Update hero
  const titleEl = document.getElementById('place-title');
  const metaEl  = document.getElementById('place-meta');
  if (titleEl) titleEl.textContent = place.title;
  if (metaEl) {
    metaEl.innerHTML = `
      <div class="place-meta-item">📍 ${place.location || 'Emplacement non précisé'}</div>
      <div class="place-meta-item">💰 $${place.price ?? 'N/A'} / nuit</div>
      <div class="place-meta-item">⭐ ${place.reviews?.length || 0} avis</div>
    `;
  }

  const section = document.getElementById('place-details');
  const stars = (r) => '★'.repeat(r) + '☆'.repeat(5 - r);

  section.innerHTML = `
    <div class="place-info-grid">
      <div class="info-card">
        <div class="info-label">Prix par nuit</div>
        <div class="info-value price">$${place.price ?? 'N/A'}</div>
      </div>
      <div class="info-card">
        <div class="info-label">Avis clients</div>
        <div class="info-value">${place.reviews?.length || 0} avis</div>
      </div>
    </div>

    <div class="desc-card">
      <div class="info-label">Description</div>
      <p>${place.description || 'Aucune description disponible.'}</p>
    </div>

    ${place.amenities && place.amenities.length ? `
    <div class="desc-card">
      <div class="info-label">Équipements</div>
      <div class="amenities-list">
        ${place.amenities.map(a => `<span class="amenity-tag">✓ ${a.name}</span>`).join('')}
      </div>
    </div>` : ''}

    <h2 class="section-title">Avis des voyageurs</h2>
    ${place.reviews && place.reviews.length
      ? place.reviews.map(r => `
        <div class="review-card">
          <div class="reviewer">${r.user_name || 'Anonyme'}</div>
          <div class="stars">${stars(r.rating)}</div>
          <p>${r.text}</p>
        </div>`).join('')
      : '<p style="color:var(--mid);font-size:15px;">Aucun avis pour l\'instant. Soyez le premier !</p>'
    }
  `;
}

// ── REVIEWS ───────────────────────────────────────
async function submitReview(token, placeId, rating, text) {
  let userId = null;
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    userId = payload.sub;
  } catch (e) {}

  const response = await fetch('http://127.0.0.1:5000/api/v1/reviews/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ place_id: placeId, user_id: userId, rating, text })
  });

  if (response.ok) {
    alert('Avis publié avec succès !');
    window.location.href = `place.html?id=${placeId}`;
  } else {
    const err = await response.json().catch(() => null);
    console.error('Review error:', err);
    alert('Échec de la publication. Veuillez réessayer.');
  }
}
