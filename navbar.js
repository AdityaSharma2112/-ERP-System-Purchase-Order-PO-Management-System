
const token = localStorage.getItem("token");
const api = "http://127.0.0.1:8000/"

function getNavbarHTML() {
  return `
  <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
    <div class="container">
      <a class="navbar-brand" href="dashboard.html">PO System</a>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarMain">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarMain">
        <ul class="navbar-nav me-auto">
          <li class="nav-item">
            <a class="nav-link" href="index.html">Dashboard</a>
          </li>
        </ul>
        <ul class="navbar-nav" id="authSection"></ul>
      </div>
    </div>
  </nav>
  `;
}

function loadNavbar() {
  document.getElementById("navbarContainer").innerHTML = getNavbarHTML();
  getUser();
}

function showAleart(success,message){
    const toastEl = document.getElementById('poToast');
    toastEl.className = `toast align-items-center border-0 text-white ${
        success? "bg-success" : "bg-danger" 
    }`;
    const toastBody = document.getElementById('toastMessage')
    toastBody.textContent = message
    const toast = new bootstrap.Toast(toastEl);
    toast.show();
}

async function apiFetch(path,opts = {}) {
    try{
        const res = await fetch(api + path, {
        ...opts,
        headers: { 'Content-Type':'application/json', ...(opts.headers||{}) }
        });
        if (res.status === 401) {
            showAleart(false, "Unauthorized. Please login again.");
            return null;
        }
        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
        const data = await res.json();
        return data;
    }catch (err) {
        showAleart(false,"Something Went Wrong")
    }
  }

function handleCredentialResponse(response) {
  fetch(api + "auth/google", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token: response.credential })
  })
    .then(res => res.json())
    .then(data => {
      localStorage.setItem("token", data.token);
      location.reload();
    });
}

function waitForGoogle(callback) {
  if (window.google && google.accounts) callback();
  else setTimeout(() => waitForGoogle(callback), 100);
}

async function getUser() {
  const token = localStorage.getItem("token");
  const authSection = document.getElementById("authSection");

  let user = null;
  try {
    user = await apiFetch("profile", {
      headers: { Authorization: `Bearer ${token}` }
    });
  } catch {}

  if (user) {
    authSection.innerHTML = `
      <li class="nav-item">
        <span class="navbar-text me-3">Hello, ${user.name}</span>
      </li>
      <li class="nav-item">
        <button class="btn btn-outline-light btn-sm" onclick="logout()">Sign Out</button>
      </li>
    `;
  } else {
    authSection.innerHTML = `
      <div id="g_id_onload"
        data-client_id="886045176737-1kmfr9bed4q0uivjbvhe10t7mrpjr8vt.apps.googleusercontent.com"
        data-callback="handleCredentialResponse">
      </div>
      <div id="googleBtn"></div>
    `;

    waitForGoogle(() => {
      google.accounts.id.initialize({
        client_id: "886045176737-1kmfr9bed4q0uivjbvhe10t7mrpjr8vt.apps.googleusercontent.com",
        callback: handleCredentialResponse
      });

      google.accounts.id.renderButton(
        document.getElementById("googleBtn"),
        { theme: "outline", size: "small" }
      );
    });
  }
}

function logout() {
  localStorage.removeItem("token");
  location.reload();
}