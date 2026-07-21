# 🌱 Smart Crop Recommendation & Farm Advisory System

An AI-powered web app that recommends the best crop to grow based on soil
nutrients (N, P, K) and climate conditions (temperature, humidity, pH,
rainfall). Also shows farm advisory info (season, water need, soil type,
fertilizer tips) and lets you download a PDF report.

**Track**: Agriculture & Intelligent Supply Chains — Major Project

---

## Live Demo

- Frontend: _(link will be added after deployment)_
- Backend API docs: _(link will be added after deployment)_

---

## Features

- 🌱 Crop recommendation using a trained ML model
- 💧 Fertilizer suggestion for the recommended crop
- 🌾 Crop info (season, water need, soil type, harvest duration)
- 📄 Downloadable PDF report

---

## Dataset

**Crop Recommendation Dataset** from Kaggle (by Atharva Ingle) — 2200
records, 22 crop classes.
Link: https://www.kaggle.com/datasets/atharvaingle/crop-recommendation-dataset

---

## Project Structure

crop-recommendation/
├── data/               # dataset (CSV)
├── model/               # model training script
├── backend/              # FastAPI backend + trained model
├── frontend/             # HTML/CSS/JS UI
└── README.md

---

## How to Run Locally

**1. Train the model**
```bash
cd model
pip install -r ../backend/requirements.txt
python train_model.py
```

**2. Start the backend**
```bash
cd backend
uvicorn main:app --reload
```
API docs: `http://127.0.0.1:8000/docs`

**3. Open the frontend**
Open `frontend/index.html` in a browser.

---

## Why This Approach

- **Problem**: Farmers often pick crops based on guesswork, not actual soil/climate data — leading to poor yield.
- **Why AI**: 7 variables (N, P, K, temperature, humidity, pH, rainfall) interact in non-linear ways that simple rules can't capture — a good fit for a classification model.
- **Model**: Compared Logistic Regression, Random Forest, and Gradient Boosting. Random Forest performed best (~99.5% accuracy) and handles feature interactions well without needing feature scaling.
- **Tech stack**: FastAPI (auto-generates API docs, built-in validation) + plain HTML/CSS/JS (lightweight, easy to explain) + ReportLab (simple PDF generation).
- **Architecture**: Frontend → FastAPI backend → trained model (loaded once at startup for fast predictions).

---

## Academic Integrity

## Academic Integrity

Dataset used with attribution (linked above). The project structure, model
training pipeline, backend API, and frontend were built with the help of
AI assistance (Claude) for code generation and guidance, and were reviewed,
tested, and understood before submission. No external code repositories
or notebooks were copied.