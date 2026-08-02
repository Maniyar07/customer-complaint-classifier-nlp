document.addEventListener("DOMContentLoaded", () => {
    const apiStatus = document.getElementById("apiStatus");

    const accuracy = document.getElementById("accuracy");
    const macroF1 = document.getElementById("macroF1");
    const weightedF1 = document.getElementById("weightedF1");
    const trainingRows = document.getElementById("trainingRows");

    const complaintText = document.getElementById("complaintText");
    const predictBtn = document.getElementById("predictBtn");
    const clearBtn = document.getElementById("clearBtn");
    const errorBox = document.getElementById("errorBox");

    const predictionResult = document.getElementById("predictionResult");
    const predictedCategory = document.getElementById("predictedCategory");
    const confidenceList = document.getElementById("confidenceList");

    const sampleSelect = document.getElementById("sampleSelect");
    const useSampleBtn = document.getElementById("useSampleBtn");

    const tabButtons = document.querySelectorAll(".tab-btn");
    const tabContents = document.querySelectorAll(".tab-content");

    function showError(message) {
        errorBox.textContent = message;
        errorBox.classList.remove("hidden");
    }

    function hideError() {
        errorBox.textContent = "";
        errorBox.classList.add("hidden");
    }

    function formatPercent(value) {
        if (value === undefined || value === null || value === "") {
            return "--";
        }

        let number = Number(value);

        if (Number.isNaN(number)) {
            return "--";
        }

        if (number <= 1) {
            number = number * 100;
        }

        return `${number.toFixed(2)}%`;
    }

    function getMetric(data, possibleKeys, defaultValue = "--") {
        for (const key of possibleKeys) {
            if (data[key] !== undefined && data[key] !== null) {
                return data[key];
            }
        }
        return defaultValue;
    }

    async function checkBackendStatus() {
        try {
            const response = await fetch("/health");
            const data = await response.json();

            if (data.model_loaded) {
                apiStatus.textContent = "Connected";
                apiStatus.style.color = "#86efac";
            } else {
                apiStatus.textContent = "Model Not Loaded";
                apiStatus.style.color = "#fca5a5";
            }
        } catch (error) {
            apiStatus.textContent = "Disconnected";
            apiStatus.style.color = "#fca5a5";
        }
    }

    async function loadMetrics() {
        try {
            const response = await fetch("/metrics");
            const data = await response.json();

            const acc = getMetric(data, ["accuracy", "test_accuracy", "best_accuracy"]);
            const macro = getMetric(data, ["macro_f1", "macro avg_f1-score", "macro_f1_score"]);
            const weighted = getMetric(data, ["weighted_f1", "weighted avg_f1-score", "weighted_f1_score"]);
            const rows = getMetric(data, ["num_rows", "training_rows", "total_rows"], "--");

            accuracy.textContent = formatPercent(acc);
            macroF1.textContent = formatPercent(macro);
            weightedF1.textContent = formatPercent(weighted);
            trainingRows.textContent = rows;
        } catch (error) {
            accuracy.textContent = "--";
            macroF1.textContent = "--";
            weightedF1.textContent = "--";
            trainingRows.textContent = "--";
            console.error("Metrics loading error:", error);
        }
    }

    function renderConfidenceScores(scores) {
        if (!scores || scores.length === 0) {
            confidenceList.innerHTML = `<p class="muted">No confidence scores available.</p>`;
            return;
        }

        const topScores = scores.slice(0, 5);

        confidenceList.innerHTML = topScores.map(item => {
            const percent = Number(item.confidence_percent || 0).toFixed(2);

            return `
                <div class="confidence-item">
                    <div class="confidence-top">
                        <span>${item.category}</span>
                        <span>${percent}%</span>
                    </div>
                    <div class="progress">
                        <div class="progress-fill" style="width: ${percent}%"></div>
                    </div>
                </div>
            `;
        }).join("");
    }

    async function predictComplaint() {
        hideError();

        const text = complaintText.value.trim();

        if (!text) {
            showError("Please enter a complaint text first.");
            return;
        }

        predictBtn.disabled = true;
        predictBtn.textContent = "Predicting...";

        try {
            const response = await fetch("/predict", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    complaint_text: text
                })
            });

            const data = await response.json();

            if (!response.ok || data.status !== "success") {
                showError(data.message || "Prediction failed.");
                predictionResult.classList.add("hidden");
                return;
            }

            predictedCategory.textContent = data.predicted_category;
            predictionResult.classList.remove("hidden");

            renderConfidenceScores(data.confidence_scores);
        } catch (error) {
            console.error("Prediction error:", error);
            showError("Could not connect to Flask API. Please check if app.py is running.");
        } finally {
            predictBtn.disabled = false;
            predictBtn.textContent = "Predict Category";
        }
    }

    function clearPrediction() {
        complaintText.value = "";
        predictedCategory.textContent = "--";
        predictionResult.classList.add("hidden");
        confidenceList.innerHTML = `<p class="muted">Prediction confidence will appear here.</p>`;
        hideError();
    }

    function useSampleComplaint() {
        const selectedText = sampleSelect.value;

        if (!selectedText) {
            showError("Please choose a sample complaint first.");
            return;
        }

        complaintText.value = selectedText;
        hideError();
    }

    function renderTable(tableId, data) {
        const table = document.getElementById(tableId);
        const thead = table.querySelector("thead");
        const tbody = table.querySelector("tbody");

        if (!data || data.status !== "success" || !data.columns || data.columns.length === 0) {
            thead.innerHTML = "";
            tbody.innerHTML = `
                <tr>
                    <td>No report data found. Please check your reports folder files.</td>
                </tr>
            `;
            return;
        }

        thead.innerHTML = `
            <tr>
                ${data.columns.map(column => `<th>${column}</th>`).join("")}
            </tr>
        `;

        tbody.innerHTML = data.rows.map(row => {
            return `
                <tr>
                    ${data.columns.map(column => `<td>${row[column] ?? ""}</td>`).join("")}
                </tr>
            `;
        }).join("");
    }

    async function loadClassificationReport() {
        try {
            const response = await fetch("/reports/classification");
            const data = await response.json();
            renderTable("classificationTable", data);
        } catch (error) {
            console.error("Classification report loading error:", error);
        }
    }

    async function loadExperimentReport() {
        try {
            const response = await fetch("/reports/experiments");
            const data = await response.json();
            renderTable("experimentTable", data);
        } catch (error) {
            console.error("Experiment report loading error:", error);
        }
    }

    function setupTabs() {
        tabButtons.forEach(button => {
            button.addEventListener("click", () => {
                const targetTab = button.dataset.tab;

                tabButtons.forEach(btn => btn.classList.remove("active"));
                tabContents.forEach(content => content.classList.remove("active"));

                button.classList.add("active");
                document.getElementById(targetTab).classList.add("active");
            });
        });
    }

    predictBtn.addEventListener("click", predictComplaint);
    clearBtn.addEventListener("click", clearPrediction);
    useSampleBtn.addEventListener("click", useSampleComplaint);

    complaintText.addEventListener("keydown", event => {
        if (event.ctrlKey && event.key === "Enter") {
            predictComplaint();
        }
    });

    setupTabs();
    checkBackendStatus();
    loadMetrics();
    loadClassificationReport();
    loadExperimentReport();
});