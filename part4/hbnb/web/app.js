const API_BASE = "http://127.0.0.1:5000/api/v1";

async function login() {
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();
    const messageEl = document.getElementById("message");

    if (!email || !password) {
        messageEl.textContent = "Email et mot de passe requis.";
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (response.ok) {
            localStorage.setItem("token", data.access_token);
            messageEl.style.color = "green";
            messageEl.textContent = "Connexion réussie, redirection...";
            setTimeout(() => {
                window.location.href = "dashboard.html";
            }, 800);
        } else {
            messageEl.style.color = "#e11d48";
            messageEl.textContent = data.error || "Erreur de connexion.";
        }
    } catch (err) {
        messageEl.style.color = "#e11d48";
        messageEl.textContent = "Erreur réseau.";
    }
}

async function loadProtected() {
    const token = localStorage.getItem("token");
    const infoEl = document.getElementById("user-info");

    if (!token) {
        infoEl.textContent = "Aucun token trouvé. Connecte-toi d’abord.";
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/auth/protected`, {
            headers: {
                "Authorization": "Bearer " + token
            }
        });

        const data = await response.json();
        infoEl.textContent = JSON.stringify(data, null, 2);
    } catch (err) {
        infoEl.textContent = "Erreur lors du chargement des données.";
    }
}

function logout() {
    localStorage.removeItem("token");
    window.location.href = "login.html";
}

