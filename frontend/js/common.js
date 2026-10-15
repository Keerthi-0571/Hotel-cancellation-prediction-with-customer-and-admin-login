/* =========================================================
   common.js  -  shared by every page

   - API base URL
   - login state (kept in sessionStorage: cleared when the tab closes)
   - api() fetch wrapper that adds the login token
   - small helpers: HTML escaping, date format, badges, statistics
   ========================================================= */

const API_BASE = "http://127.0.0.1:5000";


/* ---------------------------------------------------------
   AUTH STATE
--------------------------------------------------------- */

const Auth = {

    KEY: "hotelAuth",

    get() {
        try {
            return JSON.parse(sessionStorage.getItem(this.KEY));
        } catch (e) {
            return null;
        }
    },

    set(token, user) {
        sessionStorage.setItem(this.KEY, JSON.stringify({ token: token, user: user }));
    },

    clear() {
        sessionStorage.removeItem(this.KEY);
    },

    token() {
        const a = this.get();
        return a ? a.token : null;
    },

    user() {
        const a = this.get();
        return a ? a.user : null;
    },

    homeFor(role) {
        return role === "admin" ? "admin_dashboard.html" : "index.html";
    },

    loginFor(role) {
        return role === "admin" ? "admin_login.html" : "login.html";
    },

    /* Call at the top of a protected page.
       Sends the visitor away unless they are logged in with the right role. */
    require(role) {
        const user = this.user();

        if (!user || !this.token()) {
            location.replace(this.loginFor(role));
            return null;
        }

        if (user.role !== role) {
            location.replace(this.homeFor(user.role));
            return null;
        }

        return user;
    },

    /* Call on login / register pages: already logged in? go to your home. */
    skipIfLoggedIn() {
        const user = this.user();
        if (user && this.token()) {
            location.replace(this.homeFor(user.role));
        }
    },

    logout() {
        const user = this.user();
        this.clear();
        location.replace(this.loginFor(user ? user.role : "customer"));
    }
};


/* ---------------------------------------------------------
   API WRAPPER
--------------------------------------------------------- */

let sessionRedirecting = false;   // several requests can fail 401 at once: redirect only once

async function api(path, options) {

    const opts = options || {};
    const headers = { "Content-Type": "application/json" };

    /* Remember who we were BEFORE the request, so an expired admin session
       is sent to the admin login page (not the customer one). */
    const roleAtStart = Auth.user() ? Auth.user().role : "customer";

    if (opts.auth !== false && Auth.token()) {
        headers["Authorization"] = "Bearer " + Auth.token();
    }

    let response;

    try {
        response = await fetch(API_BASE + path, {
            method: opts.method || "GET",
            headers: headers,
            body: opts.body ? JSON.stringify(opts.body) : undefined
        });
    } catch (networkError) {
        throw new Error(
            "Cannot reach the server. Make sure Flask is running on 127.0.0.1:5000."
        );
    }

    let data = {};

    try {
        data = await response.json();
    } catch (e) {
        /* non-JSON response */
    }

    /* Session expired / token rejected on a protected call */
    if (response.status === 401 && opts.auth !== false) {
        if (!sessionRedirecting) {
            sessionRedirecting = true;
            Auth.clear();
            location.replace(Auth.loginFor(roleAtStart));
        }
        throw new Error("Your session has expired. Please log in again.");
    }

    if (!response.ok) {
        throw new Error(data.error || "Request failed (" + response.status + ").");
    }

    return data;
}


/* ---------------------------------------------------------
   HELPERS
--------------------------------------------------------- */

/* Always escape anything that came from a user (names, emails). */
function esc(value) {
    return String(value === null || value === undefined ? "" : value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
}

function fmtDate(iso) {
    const d = new Date(iso);
    return isNaN(d.getTime()) ? "-" : d.toLocaleString();
}

function predictionBadge(p) {
    const cancelled = Number(p.prediction) === 1;
    return '<span class="badge ' +
        (cancelled ? "badge-cancelled" : "badge-not-cancelled") + '">' +
        esc(p.prediction_label) + "</span>";
}

function riskBadge(level) {
    const l = String(level || "").toLowerCase();
    const cls = l === "high" ? "badge-high" : l === "medium" ? "badge-medium" : "badge-low";
    return '<span class="badge ' + cls + '">' + esc(level || "-") + "</span>";
}

function bookingDetails(p) {
    const nights = Number(p.total_nights);
    return (
        '<div>Arrival ' + esc(p.arrival_date_month) + ", " +
        esc(nights) + (nights === 1 ? " night" : " nights") +
        ", lead time " + esc(p.lead_time) + " days</div>" +
        '<div class="text-muted">' +
        esc(p.adults) + (Number(p.adults) === 1 ? " adult" : " adults") + ", " +
        esc(p.children) + (Number(p.children) === 1 ? " child" : " children") + ", " +
        esc(p.market_segment) + ", " + esc(p.deposit_type) + "</div>"
    );
}

function computeStats(list) {
    const total = list.length;
    const cancelled = list.filter(p => Number(p.prediction) === 1).length;
    const count = lvl => list.filter(
        p => String(p.risk_level).toLowerCase() === lvl).length;

    return {
        total: total,
        cancelled: cancelled,
        notCancelled: total - cancelled,
        rate: total ? ((cancelled / total) * 100).toFixed(1) : "0.0",
        high: count("high"),
        medium: count("medium"),
        low: count("low")
    };
}

function setText(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
}

/* Doughnut (cancelled / not) + bar (risk) charts shared by both dashboards */
function drawCharts(s) {

    if (typeof Chart === "undefined") return;

    const canvasA = document.getElementById("cancellationChart");
    const canvasB = document.getElementById("riskChart");

    if (canvasA) {
        new Chart(canvasA, {
            type: "doughnut",
            data: {
                labels: ["Cancelled", "Not Cancelled"],
                datasets: [{
                    data: [s.cancelled, s.notCancelled],
                    backgroundColor: ["#dc3545", "#198754"]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: "bottom" } }
            }
        });
    }

    if (canvasB) {
        new Chart(canvasB, {
            type: "bar",
            data: {
                labels: ["High", "Medium", "Low"],
                datasets: [{
                    label: "Predictions",
                    data: [s.high, s.medium, s.low],
                    backgroundColor: ["#dc3545", "#ffc107", "#198754"]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: { y: { beginAtZero: true, ticks: { precision: 0 } } }
            }
        });
    }
}

/* Navbar widget:  "Name  [role]  Logout" */
function renderUserNav(containerId, extraLinksHtml) {
    const user = Auth.user();
    const el = document.getElementById(containerId);
    if (!user || !el) return;

    el.innerHTML =
        (extraLinksHtml || "") +
        '<span class="text-white-50 small d-none d-md-inline">' +
        esc(user.name) + "</span>" +
        '<button type="button" class="btn btn-outline-light btn-sm" id="logoutBtn">' +
        "Logout</button>";

    document.getElementById("logoutBtn").addEventListener("click", () => Auth.logout());
}
