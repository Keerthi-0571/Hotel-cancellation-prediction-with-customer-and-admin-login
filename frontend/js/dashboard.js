/* =========================================================
   dashboard.js  -  CUSTOMER "My History" page
   Shows ONLY the logged-in customer's own predictions.
   (The server filters by the login token; this page cannot
   ask for anyone else's data.)
   ========================================================= */

document.addEventListener("DOMContentLoaded", async function () {

    if (!Auth.user()) return;           // Auth.require() is already redirecting

    const body = document.getElementById("predictionHistory");

    body.innerHTML =
        '<tr><td colspan="7" class="text-center text-muted py-4">Loading...</td></tr>';

    let history;

    try {
        const data = await api("/api/history");
        history = data.history;
    } catch (error) {
        body.innerHTML =
            '<tr><td colspan="7" class="text-center text-danger py-4">' +
            esc(error.message) + "</td></tr>";
        return;
    }

    /* ---------- statistics + charts ---------- */

    const s = computeStats(history);

    setText("totalPredictions", s.total);
    setText("cancelledBookings", s.cancelled);
    setText("notCancelledBookings", s.notCancelled);
    setText("cancellationRate", s.rate + "%");
    setText("highRisk", s.high);
    setText("mediumRisk", s.medium);
    setText("lowRisk", s.low);

    drawCharts(s);

    /* ---------- history table (newest first) ---------- */

    if (history.length === 0) {
        body.innerHTML =
            '<tr><td colspan="7" class="text-center text-muted py-4">' +
            'No predictions yet. <a href="index.html">Make your first prediction</a>.' +
            "</td></tr>";
        return;
    }

    body.innerHTML = history.map(function (p, i) {
        return (
            "<tr>" +
            "<td>" + (history.length - i) + "</td>" +
            "<td><strong>" + esc(p.hotel) + "</strong></td>" +
            '<td class="details">' + bookingDetails(p) + "</td>" +
            "<td>" + predictionBadge(p) + "</td>" +
            "<td><strong>" + Number(p.cancellation_probability).toFixed(2) + "%</strong></td>" +
            "<td>" + riskBadge(p.risk_level) + "</td>" +
            "<td>" + esc(fmtDate(p.created_at)) + "</td>" +
            "</tr>"
        );
    }).join("");
});
