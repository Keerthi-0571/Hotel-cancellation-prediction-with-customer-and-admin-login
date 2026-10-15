/* =========================================================
   auth_pages.js  -  login.html, register.html, admin_login.html
   Requires common.js
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    const errorBox = document.getElementById("formError");
    const submitBtn = document.getElementById("submitBtn");

    function showError(message) {
        errorBox.textContent = message;
        errorBox.classList.remove("d-none");
    }

    function hideError() {
        errorBox.classList.add("d-none");
    }

    /* Runs `action` with the button disabled; shows any error it throws. */
    async function submitWith(action) {
        hideError();
        const label = submitBtn.textContent;
        submitBtn.disabled = true;
        submitBtn.textContent = "Please wait...";

        try {
            await action();
        } catch (error) {
            showError(error.message);
            submitBtn.disabled = false;
            submitBtn.textContent = label;
        }
    }

    function value(id) {
        return document.getElementById(id).value;
    }


    /* ---------------- CUSTOMER LOGIN ---------------- */

    const loginForm = document.getElementById("loginForm");

    if (loginForm) {
        loginForm.addEventListener("submit", function (event) {
            event.preventDefault();

            submitWith(async function () {

                if (!value("email").trim() || !value("password")) {
                    throw new Error("Please enter your email and password.");
                }

                const data = await api("/api/login", {
                    method: "POST",
                    auth: false,
                    body: { email: value("email"), password: value("password") }
                });

                Auth.set(data.token, data.user);
                location.replace(Auth.homeFor(data.user.role));
            });
        });
    }


    /* ---------------- REGISTER ---------------- */

    const registerForm = document.getElementById("registerForm");

    if (registerForm) {
        registerForm.addEventListener("submit", function (event) {
            event.preventDefault();

            submitWith(async function () {

                if (value("name").trim().length < 2) {
                    throw new Error("Please enter your full name.");
                }

                if (!value("email").trim()) {
                    throw new Error("Please enter your email address.");
                }

                if (value("password").length < 8) {
                    throw new Error("Password must be at least 8 characters.");
                }

                if (value("password") !== value("confirm")) {
                    throw new Error("The two passwords do not match.");
                }

                const data = await api("/api/register", {
                    method: "POST",
                    auth: false,
                    body: {
                        name: value("name"),
                        email: value("email"),
                        password: value("password")
                    }
                });

                Auth.set(data.token, data.user);
                location.replace(Auth.homeFor(data.user.role));
            });
        });
    }


    /* ---------------- ADMIN LOGIN ---------------- */

    const adminForm = document.getElementById("adminLoginForm");

    if (adminForm) {
        adminForm.addEventListener("submit", function (event) {
            event.preventDefault();

            submitWith(async function () {

                if (!value("email").trim() || !value("password")) {
                    throw new Error("Please enter your email and password.");
                }

                const data = await api("/api/admin/login", {
                    method: "POST",
                    auth: false,
                    body: { email: value("email"), password: value("password") }
                });

                Auth.set(data.token, data.user);
                location.replace(Auth.homeFor(data.user.role));
            });
        });
    }

});
