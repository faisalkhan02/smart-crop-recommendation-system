"""
main.py — FastAPI backend for the Crop Recommendation & Farm Advisory System

3 API endpoints defined here:
  POST /predict          -> takes soil/climate values, returns the best crop
  GET  /crop-info/{crop}  -> returns advisory info for a given crop
  POST /report            -> generates a downloadable PDF report of a prediction

"""

# FastAPI - the framework used to build this API
# HTTPException - used to return proper error responses (like 404)
from fastapi import FastAPI, HTTPException

# CORSMiddleware - needed so the frontend (a separate HTML file) can call
# this backend without the browser blocking it
from fastapi.middleware.cors import CORSMiddleware

# FileResponse - used to send the generated PDF back to the client
from fastapi.responses import FileResponse

# BaseModel - defines the structure expected for incoming request data
# Field - adds validation rules (min/max values) to each field
from pydantic import BaseModel, Field

# joblib - for loading the trained model and label encoder from disk
import joblib

# numpy - to format input data into the array shape the model expects
import numpy as np

# os - for handling file paths
import os

# uuid - to generate a unique filename for each PDF report
import uuid

# datetime - to timestamp each generated report
from datetime import datetime

# reportlab - library used to generate PDFs
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# helper function that looks up crop advisory info
from crop_info import get_crop_info

# ------------------- setting up the app -------------------
app = FastAPI(
    title="Smart Crop Recommendation & Farm Advisory API",
    description="Predicts the best crop for given soil/climate conditions and provides farm advisory info.",
    version="1.0.0",
)

# ------------------- enabling CORS -------------------
# without this, the browser blocks the frontend from calling this API
# since they're on different origins. allow_origins=["*"] is fine for
# this project - a real production app would restrict this properly.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------- loading the trained model -------------------
# building the full path to model.pkl and label_encoder.pkl
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")
ENCODER_PATH = os.path.join(os.path.dirname(__file__), "label_encoder.pkl")

# loaded once at startup, not on every request - keeps things fast
model = joblib.load(MODEL_PATH)
label_encoder = joblib.load(ENCODER_PATH)

# folder where generated PDF reports are saved
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)  # create it if it doesn't exist yet


# ------------------- request/response schemas -------------------

# expected structure for the /predict endpoint.
# FastAPI validates incoming requests against this automatically -
# e.g. if N is sent as -50, it gets rejected since ge=0 (must be >= 0)
class SoilInput(BaseModel):
    N: float = Field(..., ge=0, le=200, description="Nitrogen content in soil")
    P: float = Field(..., ge=0, le=200, description="Phosphorus content in soil")
    K: float = Field(..., ge=0, le=250, description="Potassium content in soil")
    temperature: float = Field(..., ge=-10, le=55, description="Temperature in Celsius")
    humidity: float = Field(..., ge=0, le=100, description="Relative humidity in %")
    ph: float = Field(..., ge=0, le=14, description="Soil pH value")
    rainfall: float = Field(..., ge=0, le=500, description="Rainfall in mm")


# shape of the response sent back from /predict
class PredictionResponse(BaseModel):
    recommended_crop: str
    confidence: float
    top_3: list


# ------------------- root endpoint (basic health check) -------------------
@app.get("/")
def root():
    return {"message": "Smart Crop Recommendation API is running. Visit /docs for API documentation."}


# ------------------- predict endpoint -------------------
@app.post("/predict", response_model=PredictionResponse)
def predict_crop(data: SoilInput):
    # converting the incoming data into the 2D array shape the model expects
    # (predict expects a list of samples, even for a single prediction)
    features = np.array([[data.N, data.P, data.K, data.temperature,
                           data.humidity, data.ph, data.rainfall]])

    # predict_proba gives the probability for EVERY crop class, not just the top one
    probs = model.predict_proba(features)[0]

    # sorting probabilities highest to lowest, taking the top 3
    top_idx = np.argsort(probs)[::-1][:3]

    # converting those top 3 indices back into actual crop names with their confidence
    top_3 = [
        {"crop": label_encoder.inverse_transform([i])[0], "confidence": round(float(probs[i]), 4)}
        for i in top_idx
    ]

    # the #1 ranked crop is the main recommendation
    best_crop = top_3[0]["crop"]
    best_confidence = top_3[0]["confidence"]

    return PredictionResponse(
        recommended_crop=best_crop,
        confidence=best_confidence,
        top_3=top_3,
    )


# ------------------- crop info endpoint -------------------
# {crop_name} in the path is a variable, e.g. /crop-info/rice, /crop-info/maize
@app.get("/crop-info/{crop_name}")
def crop_info(crop_name: str):
    info = get_crop_info(crop_name)

    # if no info exists for this crop in the lookup dictionary, return a 404
    if info is None:
        raise HTTPException(status_code=404, detail=f"No info found for crop '{crop_name}'")

    return {"crop": crop_name.lower(), **info}


# ------------------- report request schema -------------------
# same soil inputs plus the prediction result, so everything needed
# for the PDF is available in one place
class ReportRequest(BaseModel):
    N: float
    P: float
    K: float
    temperature: float
    humidity: float
    ph: float
    rainfall: float
    recommended_crop: str
    confidence: float


# ------------------- report (PDF) endpoint -------------------
@app.post("/report")
def generate_report(data: ReportRequest):
    # generating a unique filename so reports don't overwrite each other
    filename = f"report_{uuid.uuid4().hex[:8]}.pdf"
    filepath = os.path.join(REPORTS_DIR, filename)

    # creating a new PDF canvas, A4 size
    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4

    # ---- title ----
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, height - 60, "Smart Crop Recommendation Report")

    # ---- timestamp ----
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 85, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    # ---- input values section ----
    c.setFont("Helvetica-Bold", 13)
    c.drawString(50, height - 130, "Input Soil & Climate Conditions")
    c.setFont("Helvetica", 11)
    y = height - 155  # vertical position tracker, moved down after each line

    for label, val in [
        ("Nitrogen (N)", data.N), ("Phosphorus (P)", data.P), ("Potassium (K)", data.K),
        ("Temperature (C)", data.temperature), ("Humidity (%)", data.humidity),
        ("Soil pH", data.ph), ("Rainfall (mm)", data.rainfall),
    ]:
        c.drawString(60, y, f"{label}: {val}")
        y -= 18  # move down for the next line

    # ---- recommendation section ----
    y -= 15
    c.setFont("Helvetica-Bold", 13)
    c.drawString(50, y, "Recommendation")
    y -= 22
    c.setFont("Helvetica", 12)
    c.drawString(60, y, f"Recommended Crop: {data.recommended_crop.title()}")
    y -= 18
    c.drawString(60, y, f"Confidence: {data.confidence * 100:.1f}%")

    # ---- farm advisory section, only if info exists for this crop ----
    info = get_crop_info(data.recommended_crop)
    if info:
        y -= 30
        c.setFont("Helvetica-Bold", 13)
        c.drawString(50, y, "Farm Advisory")
        y -= 22
        c.setFont("Helvetica", 11)
        for label, key in [
            ("Growing Season", "season"), ("Water Requirement", "water"),
            ("Suitable Soil", "soil"), ("Harvest Duration (days)", "harvest_days"),
            ("Fertilizer Suggestion", "fertilizer"),
        ]:
            c.drawString(60, y, f"{label}: {info[key]}")
            y -= 18

    # saving the PDF to disk
    c.save()

    # sending the generated PDF file back as the response
    return FileResponse(filepath, media_type="application/pdf", filename="crop_report.pdf")