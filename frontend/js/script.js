document.addEventListener("DOMContentLoaded", function () {

    console.log("======================================");
    console.log("HOTEL PREDICTION SCRIPT LOADED");
    console.log("======================================");

    // =========================================================
    // GET ELEMENTS
    // =========================================================

    const form = document.getElementById("predictionForm");

    const hotel = document.getElementById("hotel");
    const leadTime = document.getElementById("lead_time");
    const arrivalMonth = document.getElementById("arrival_date_month");
    const totalNights = document.getElementById("total_nights");
    const adults = document.getElementById("adults");
    const children = document.getElementById("children");
    const marketSegment = document.getElementById("market_segment");
    const depositType = document.getElementById("deposit_type");

    const predictBtn = document.getElementById("predictBtn");
    const loading = document.getElementById("loading");
    const result = document.getElementById("result");
    const hotelMessage = document.getElementById("hotelMessage");


    // =========================================================
    // CHECK ELEMENTS
    // =========================================================

    if (!form) {
        console.error("predictionForm not found.");
        return;
    }

    if (!hotel) {
        console.error("hotel select not found.");
        return;
    }

    console.log("All form elements loaded successfully.");


    // =========================================================
    // HOTEL CHANGE
    // =========================================================

    hotel.addEventListener("change", function () {

        console.log("Selected hotel:", hotel.value);

        if (hotel.value === "Resort Hotel") {

            hotelMessage.textContent =
                "Selected: Resort Hotel";

            hotelMessage.className =
                "form-text text-success fw-bold";

        } else if (hotel.value === "City Hotel") {

            hotelMessage.textContent =
                "Selected: City Hotel";

            hotelMessage.className =
                "form-text text-success fw-bold";

        } else {

            hotelMessage.textContent =
                "Please select the hotel.";

            hotelMessage.className =
                "form-text text-muted";
        }

    });


    // =========================================================
    // FORM SUBMIT
    // =========================================================

    form.addEventListener("submit", async function (event) {

        // VERY IMPORTANT
        // Prevent page refresh
        event.preventDefault();

        console.log("======================================");
        console.log("PREDICT BUTTON CLICKED");
        console.log("======================================");


        // =====================================================
        // GET VALUES
        // =====================================================

        const selectedHotel = hotel.value;

        const leadTimeValue =
            Number(leadTime.value);

        const arrivalMonthValue =
            arrivalMonth.value;

        const totalNightsValue =
            Number(totalNights.value);

        const adultsValue =
            Number(adults.value);

        const childrenValue =
            Number(children.value || 0);

        const marketSegmentValue =
            marketSegment.value;

        const depositTypeValue =
            depositType.value;


        // =====================================================
        // VALIDATION
        // =====================================================

        if (!selectedHotel) {

            alert("Please select a hotel.");

            hotel.focus();

            return;
        }


        if (!arrivalMonthValue) {

            alert("Please select arrival month.");

            arrivalMonth.focus();

            return;
        }


        if (
            !Number.isFinite(leadTimeValue) ||
            leadTimeValue < 0
        ) {

            alert("Please enter a valid lead time.");

            leadTime.focus();

            return;
        }


        if (
            !Number.isFinite(totalNightsValue) ||
            totalNightsValue < 1
        ) {

            alert("Please enter valid total nights.");

            totalNights.focus();

            return;
        }


        if (
            !Number.isFinite(adultsValue) ||
            adultsValue < 1
        ) {

            alert("Please enter valid number of adults.");

            adults.focus();

            return;
        }


        if (!marketSegmentValue) {

            alert("Please select market segment.");

            marketSegment.focus();

            return;
        }


        if (!depositTypeValue) {

            alert("Please select deposit type.");

            depositType.focus();

            return;
        }


        // =====================================================
        // CALCULATE NIGHTS
        // =====================================================

        const weekendNights =
            Math.min(totalNightsValue, 2);

        const weekNights =
            Math.max(
                totalNightsValue - weekendNights,
                0
            );


        // =====================================================
        // CREATE REQUEST DATA
        // =====================================================

        const data = {

            hotel: selectedHotel,

            lead_time: leadTimeValue,

            arrival_date_month:
                arrivalMonthValue,

            stays_in_weekend_nights:
                weekendNights,

            stays_in_week_nights:
                weekNights,

            adults:
                adultsValue,

            children:
                childrenValue,

            market_segment:
                marketSegmentValue,

            deposit_type:
                depositTypeValue

        };


        // =====================================================
        // SHOW DATA IN CONSOLE
        // =====================================================

        console.log("DATA SENT TO FLASK:");

        console.table(data);


        // =====================================================
        // BUTTON LOADING
        // =====================================================

        predictBtn.disabled = true;

        predictBtn.innerHTML =
            "⏳ Predicting...";


        if (loading) {

            loading.classList.remove("d-none");

        }


        if (result) {

            result.innerHTML = `

                <div class="text-center p-4">

                    <div
                        class="spinner-border text-primary"
                        role="status">
                    </div>

                    <h5 class="mt-3">
                        Analyzing booking...
                    </h5>

                    <p class="text-muted">
                        Please wait.
                    </p>

                </div>

            `;

        }


        // =====================================================
        // SEND TO FLASK
        // =====================================================

        try {

            console.log(
                "Sending POST request to Flask..."
            );


            const response =
                await fetch(
                    API_BASE + "/predict",
                    {

                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json",
                            "Authorization":
                                "Bearer " + Auth.token()
                        },

                        body:
                            JSON.stringify(data)

                    }
                );


            console.log(
                "Flask HTTP status:",
                response.status
            );


            // =================================================
            // GET RESPONSE
            // =================================================

            const responseText =
                await response.text();


            console.log(
                "Flask response:",
                responseText
            );


            let prediction;


            try {

                prediction =
                    JSON.parse(responseText);

            } catch (jsonError) {

                throw new Error(
                    "Flask did not return valid JSON. " +
                    "Check the Flask terminal."
                );

            }


            // =================================================
            // BACKEND ERROR
            // =================================================

            if (response.status === 401) {

                Auth.logout();

                return;

            }


            if (!response.ok) {

                throw new Error(
                    prediction.error ||
                    "Prediction failed."
                );

            }


            // =================================================
            // READ PREDICTION
            // =================================================

            const predictionValue =
                Number(
                    prediction.prediction
                );


            const probability =
                Number(
                    prediction.cancellation_probability
                );


            const predictionLabel =
                prediction.prediction_label ||
                (
                    predictionValue === 1
                        ? "Cancelled"
                        : "Not Cancelled"
                );


            const riskLevel =
                prediction.risk_level ||
                "Low";


            // =================================================
            // CHECK RESULT
            // =================================================

            if (
                !Number.isFinite(predictionValue)
            ) {

                throw new Error(
                    "Invalid prediction returned by Flask."
                );

            }


            if (
                !Number.isFinite(probability)
            ) {

                throw new Error(
                    "Invalid cancellation probability returned by Flask."
                );

            }


            // =================================================
            // SAFE PROBABILITY
            // =================================================

            const safeProbability =
                Math.min(
                    Math.max(
                        probability,
                        0
                    ),
                    100
                );


            // =================================================
            // CSS CLASSES
            // =================================================

            let riskClass =
                "risk-low";


            if (riskLevel === "High") {

                riskClass =
                    "risk-high";

            } else if (riskLevel === "Medium") {

                riskClass =
                    "risk-medium";

            }


            let predictionClass =
                "prediction-not-cancelled";


            if (predictionValue === 1) {

                predictionClass =
                    "prediction-cancelled";

            }


            // =================================================
            // DISPLAY RESULT
            // =================================================

            result.innerHTML = `

                <div>

                    <h4 class="fw-bold mb-4">
                        📊 Prediction Result
                    </h4>

                    <hr>


                    <div class="mb-3">

                        <small class="text-muted">
                            Selected Hotel
                        </small>

                        <div class="fw-bold fs-5">
                            🏨 ${selectedHotel}
                        </div>

                    </div>


                    <div class="mb-4">

                        <small class="text-muted">
                            Prediction
                        </small>

                        <div
                            class="prediction-success
                            ${predictionClass}">

                            ${predictionLabel}

                        </div>

                    </div>


                    <div class="mb-3">

                        <small class="text-muted">
                            Cancellation Probability
                        </small>

                        <div class="probability">

                            ${safeProbability.toFixed(2)}%

                        </div>

                    </div>


                    <div
                        class="progress mb-4"
                        style="height:14px;">

                        <div
                            class="progress-bar"
                            role="progressbar"
                            style="
                                width:${safeProbability}%;
                            ">

                        </div>

                    </div>


                    <div>

                        <small class="text-muted">
                            Risk Level
                        </small>

                        <br>

                        <span
                            class="risk-badge ${riskClass}">

                            ${riskLevel}

                        </span>

                    </div>

                </div>

            `;


            // =================================================
            // HISTORY IS SAVED BY THE SERVER (linked to your account)
            // =================================================

            result.insertAdjacentHTML(
                "beforeend",
                '<p class="text-muted small mt-4 mb-0">' +
                '✅ Saved to <a href="dashboard.html">My History</a></p>'
            );


        } catch (error) {

            // =================================================
            // ERROR
            // =================================================

            console.error(
                "PREDICTION ERROR:",
                error
            );


            result.innerHTML = `

                <div class="alert alert-danger">

                    <h5>
                        ❌ Prediction Failed
                    </h5>

                    <p class="mb-2">
                        ${error.message}
                    </p>

                    <hr>

                    <strong>
                        Check:
                    </strong>

                    <ul class="mb-0">

                        <li>
                            Flask is running on
                            <b>127.0.0.1:5000</b>
                        </li>

                        <li>
                            Open
                            <b>http://127.0.0.1:5000/health</b>
                            in your browser
                        </li>

                        <li>
                            Check the Flask terminal
                            for the actual error
                        </li>

                    </ul>

                </div>

            `;

        }


        // =====================================================
        // FINALLY
        // =====================================================

        finally {

            predictBtn.disabled = false;

            predictBtn.innerHTML =
                "🔍 Predict Cancellation";


            if (loading) {

                loading.classList.add(
                    "d-none"
                );

            }

        }

    });

});