document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            await loginUser(email, password);
        });
    }

    if (document.getElementById('places-list')) {
        checkAuthentication();
    }
});

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
    document.getElementById('login-link').style.display = token ? 'none' : 'block';
    if (token) fetchPlaces(token);
}

async function fetchPlaces(token) {
    const response = await fetch('http://127.0.0.1:5000/api/v1/places/', {
        headers: { 'Authorization': `Bearer ${token}` }
    });
    const places = await response.json();
    displayPlaces(places);

    document.getElementById('price-filter').addEventListener('change', (e) => {
        const max = e.target.value;
        document.querySelectorAll('.place-card').forEach(card => {
            card.style.display = (max === 'all' || parseFloat(card.dataset.price) <= parseFloat(max))
                ? 'block' : 'none';
        });
    });
}

function displayPlaces(places) {
    const list = document.getElementById('places-list');
    list.innerHTML = '';
    places.forEach(place => {
        const card = document.createElement('div');
        card.classList.add('place-card');
        card.dataset.price = place.price ?? 0;
        card.innerHTML = `
            <h3>${place.title}</h3>
            <p>${place.description || ''}</p>
            <p><strong>Price per night:</strong> $${place.price ?? 'N/A'}</p>
            <a href="place.html?id=${place.id}" class="details-button">View Details</a>
        `;
        list.appendChild(card);
    });
}
