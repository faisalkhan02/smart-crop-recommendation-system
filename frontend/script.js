// base URL for the backend API - change this if the backend is hosted elsewhere later
const API_BASE = "http://127.0.0.1:8000";

// grabbing references to all the HTML elements needed
const form = document.getElementById("cropForm");
const submitBtn = document.getElementById("submitBtn");
const resultCard = document.getElementById("resultCard");
const errorCard = document.getElementById("errorCard");
const cropName = document.getElementById("cropName");
const confidenceEl = document.getElementById("confidence");
const top3El = document.getElementById("top3");
const advisoryEl = document.getElementById("advisory");
const downloadBtn = document.getElementById("downloadBtn");

// stores the last prediction result, needed later when downloading the PDF report
let lastPrediction = null;

// runs when the form is submitted (Recommend Crop button clicked)
form.addEventListener("submit", async (e) => {
  e.preventDefault(); // stops the page from refreshing (default form behavior)

  // resetting UI state before making a new request
  errorCard.style.display = "none";
  resultCard.style.display = "none";
  submitBtn.disabled = true;
  submitBtn.textContent = "Analyzing...";

  // collecting all 7 input values from the form and converting them to numbers
  const payload = {
    N: parseFloat(document.getElementById("N").value),
    P: parseFloat(document.getElementById("P").value),
    K: parseFloat(document.getElementById("K").value),
    temperature: parseFloat(document.getElementById("temperature").value),
    humidity: parseFloat(document.getElementById("humidity").value),
    ph: parseFloat(document.getElementById("ph").value),
    rainfall: parseFloat(document.getElementById("rainfall").value),
  };

  try {
    // calling the /predict endpoint with the soil/climate values
    const predictRes = await fetch(`${API_BASE}/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!predictRes.ok) throw new Error("Prediction failed. Check backend is running.");
    const prediction = await predictRes.json();

    // once the recommended crop is known, fetching its advisory info separately
    const infoRes = await fetch(`${API_BASE}/crop-info/${prediction.recommended_crop}`);
    const info = infoRes.ok ? await infoRes.json() : null;

    // saving the combined data - needed later if the PDF report is downloaded
    lastPrediction = { ...payload, ...prediction };

    // updating the page with the results
    renderResult(prediction, info);
  } catch (err) {
    // showing an error message if anything goes wrong (e.g. backend not running)
    errorCard.textContent = `⚠️ ${err.message}`;
    errorCard.style.display = "block";
  } finally {
    // re-enabling the button regardless of success/failure
    submitBtn.disabled = false;
    submitBtn.textContent = "🔍 Recommend Crop";
  }
});

// updates the result card with the prediction and advisory info
function renderResult(prediction, info) {
  cropName.textContent = prediction.recommended_crop;
  confidenceEl.textContent = `${(prediction.confidence * 100).toFixed(1)}% confidence`;

  // building the top-3 crop list (small pill-style boxes)
  top3El.innerHTML = prediction.top_3
    .map(
      (item) =>
        `<div class="top3-item">${item.crop} — ${(item.confidence * 100).toFixed(1)}%</div>`
    )
    .join("");

  // filling in the advisory section if info was found for this crop
  if (info) {
    advisoryEl.innerHTML = `
      <dt>Growing Season</dt><dd>${info.season}</dd>
      <dt>Water Requirement</dt><dd>${info.water}</dd>
      <dt>Suitable Soil</dt><dd>${info.soil}</dd>
      <dt>Harvest Duration</dt><dd>${info.harvest_days} days</dd>
      <dt>Fertilizer Suggestion</dt><dd>${info.fertilizer}</dd>
    `;
  } else {
    advisoryEl.innerHTML = "<dd>No advisory info available for this crop.</dd>";
  }

  // showing the result card and scrolling to it smoothly
  resultCard.style.display = "block";
  resultCard.scrollIntoView({ behavior: "smooth", block: "start" });
}

// runs when the "Download PDF Report" button is clicked
downloadBtn.addEventListener("click", async () => {
  if (!lastPrediction) return; // safety check - nothing to download if no prediction was made yet

  downloadBtn.disabled = true;
  downloadBtn.textContent = "Generating...";

  try {
    // calling the /report endpoint with the full prediction data
    const res = await fetch(`${API_BASE}/report`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(lastPrediction),
    });
    if (!res.ok) throw new Error("Could not generate report.");

    // the response is a PDF file (binary blob) - converting it into a downloadable link
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "crop_recommendation_report.pdf";
    document.body.appendChild(a);
    a.click();   // triggers the actual download
    a.remove();  // cleans up the temporary link element
    window.URL.revokeObjectURL(url); // frees up memory
  } catch (err) {
    errorCard.textContent = `⚠️ ${err.message}`;
    errorCard.style.display = "block";
  } finally {
    downloadBtn.disabled = false;
    downloadBtn.textContent = "📄 Download PDF Report";
  }
});