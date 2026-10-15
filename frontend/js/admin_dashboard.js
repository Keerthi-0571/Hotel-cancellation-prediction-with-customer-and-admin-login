/* =========================================================
   admin_dashboard.js  -  ADMIN ONLY
   Loads every customer's prediction history from the server.
   The server rejects these calls unless the login belongs
   to an admin account.
   ========================================================= */

document.addEventListener("DOMContentLoaded", async function () {

    if (!Auth.user()) return;           // Auth.require() is already redirecting

    const MAX_ROWS = 500;               // keep the table fast on large histories

    const body = document.getElementById("historyBody");
    const countEl = document.getElementById("resultCount");
    const pageError = document.getElementById("pageError");

    const searchBox = document.getElementById("searchBox");
    const riskFilter = document.getElementById("riskFilter");
    const predFilter = document.getElementById("predFilter");

    let allRows = [];


    function showPageError(message) {
        pageError.textContent = message;
        pageError.classList.remove("d-none");
    }


    /* ---------- load stats + history ---------- */

    try {

        const [stats, hist] = await Promise.all([
            api("/api/admin/stats"),
            api("/api/admin/history")
        ]);

        setText("totalCustomers", stats.total_customers);
        setText("totalPredictions", stats.total_predictions);
        setText("cancelledBookings", stats.cancelled);
        setText("notCancelledBookings", stats.not_cancelled);
        setText("cancellationRate", stats.cancellation_rate + "%");
        setText("highRisk", stats.high_risk);
        setText("mediumRisk", stats.medium_risk);
        setText("lowRisk", stats.low_risk);

        drawCharts({
            cancelled: stats.cancelled,
            notCancelled: stats.not_cancelled,
            high: stats.high_risk,
            medium: stats.medium_risk,
            low: stats.low_risk
        });

        allRows = hist.history;

    } catch (error) {

        showPageError(error.message);
        countEl.textContent = "Could not load history.";
        return;
    }


    /* ---------- render the table (applies the filters) ---------- */

    function render() {

        const q = searchBox.value.trim().toLowerCase();
        const risk = riskFilter.value;
        const pred = predFilter.value;

        const rows = allRows.filter(function (p) {

            if (risk && String(p.risk_level).toLowerCase() !== risk) return false;
            if (pred !== "" && String(p.prediction) !== pred) return false;

            if (q) {
                const haystack = (
                    p.customer_name + " " + p.customer_email + " " + p.hotel
                ).toLowerCase();
                if (haystack.indexOf(q) === -1) return false;
            }

            return true;
        });

        if (allRows.length === 0) {
            countEl.textContent = "No predictions have been made yet.";
            body.innerHTML =
                '<tr><td colspan="8" class="text-center text-muted py-5">' +
                "No customer predictions yet.</td></tr>";
            return;
        }

        if (rows.length === 0) {
            countEl.textContent = "Showing 0 of " + allRows.length + " predictions";
            body.innerHTML =
                '<tr><td colspan="8" class="text-center text-muted py-5">' +
                "No predictions match your filters.</td></tr>";
            return;
        }

        const shown = rows.slice(0, MAX_ROWS);

        countEl.textContent =
            "Showing " + shown.length + " of " + allRows.length + " predictions" +
            (rows.length > MAX_ROWS
                ? " (first " + MAX_ROWS + " matches - narrow the search to see more)"
                : "");

        body.innerHTML = shown.map(function (p) {
            return (
                "<tr>" +
                '<td class="nowrap">' + esc(p.id) + "</td>" +
                '<td class="customer"><strong>' + esc(p.customer_name) + "</strong>" +
                    '<div class="text-muted">' + esc(p.customer_email) + "</div></td>" +
                '<td class="nowrap">' + esc(p.hotel) + "</td>" +
                '<td class="details">' + bookingDetails(p) + "</td>" +
                '<td class="nowrap">' + predictionBadge(p) + "</td>" +
                '<td class="nowrap"><strong>' +
                    Number(p.cancellation_probability).toFixed(2) + "%</strong></td>" +
                '<td class="nowrap">' + riskBadge(p.risk_level) + "</td>" +
                '<td class="nowrap">' + esc(fmtDate(p.created_at)) + "</td>" +
                "</tr>"
            );
        }).join("");
    }


    searchBox.addEventListener("input", render);
    riskFilter.addEventListener("change", render);
    predFilter.addEventListener("change", render);

    render();
});
