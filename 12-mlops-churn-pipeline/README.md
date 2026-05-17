# Project 12: MLOps Pipeline for Churn Prediction

## 🚀 Overview
Një platformë e plotë **MLOps** që automatizon trajnimin, validimin dhe regjistrimin e modeleve të Churn Prediction. Përfshin detektim automatik të **Data Drift** dhe integrim me **MLflow** për gjurmueshmëri të plotë.

## 🏗️ Arkitektura
- **MLflow Server**: Menaxhon eksperimentet, artifact-et dhe regjistrimin e modeleve.
- **Pipeline Runner**: Ekzekuton logjikën e trajnimit dhe kontrollit të drift-it.
- **Drift Detector**: Përdor librarinë `Evidently` (ose logjikë statistikore) për të krahasuar të dhënat.
- **PostgreSQL**: Ruan metadata e eksperimenteve.

## 🛠️ Si ta Ekzekutoni

1. **Nisja e Infrastrukturës:**
   ```bash
   docker-compose up -d --build