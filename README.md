# Customer Complaint Classifier NLP

An NLP-based Machine Learning application that automatically classifies customer complaints into predefined categories using Natural Language Processing and Machine Learning techniques.

The project provides a Flask web application where users can enter complaint text and get:
- Predicted complaint category
- Confidence scores
- Model performance metrics
- Classification reports
- Data analysis visualizations


## Project Overview

Customer service teams receive thousands of complaints daily. Manually categorizing these complaints is time-consuming.

This project uses NLP and Machine Learning to automatically classify complaints and assist customer support teams in faster routing and analysis.


## Features

✅ Text preprocessing and cleaning  
✅ TF-IDF based feature extraction  
✅ Machine Learning classification  
✅ Complaint category prediction  
✅ Confidence score generation  
✅ Flask REST API  
✅ Web-based user interface  
✅ Model evaluation reports  
✅ Docker deployment support  


# Tech Stack

## Programming Language
- Python

## Machine Learning
- Scikit-learn
- Logistic Regression
- TF-IDF Vectorizer

## NLP
- Text preprocessing
- Feature engineering
- Label encoding

## Backend
- Flask
- Flask-CORS

## Deployment
- Docker
- Gunicorn
- AWS EC2


# Project Structure

```
customer-complaint-classifier-nlp/

│
├── app.py
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── .gitignore
│
├── models/
│   ├── best_complaint_classifier_pipeline.pkl
│   └── best_label_encoder.pkl
│
├── data/
│   └── complaints_copy.xlsx
│
├── notebooks/
│   ├── 01_EDA_AND_DATA_UNDERSTANDING.ipynb
│   ├── 02_TEXT_PREPROCESSING_AND_FEATURE_ENGINEERING.ipynb
│   └── 03_MODEL_TRAINING_EVALUATION_AND_EXPORT.ipynb
│
├── reports/
│   ├── classification reports
│   ├── model metrics
│   └── experiment results
│
├── static/
│   ├── css/
│   └── js/
│
└── templates/
    └── index.html

```


# Machine Learning Pipeline

```
Customer Complaint Text

        ↓

Text Cleaning & Preprocessing

        ↓

TF-IDF Feature Extraction

        ↓

Logistic Regression Classifier

        ↓

Complaint Category Prediction

        ↓

Confidence Score Output
```


# Model Details

## Best Model

Algorithm:

```
TF-IDF + Logistic Regression
```

The model pipeline includes:

- Text vectorization
- Feature extraction
- Classification


## Evaluation Metrics

The model is evaluated using:

- Accuracy
- Precision
- Recall
- F1-score
- Classification Report


# Installation and Setup


## 1. Clone Repository

```bash
git clone https://github.com/Maniyar07/customer-complaint-classifier-nlp.git
```

Move into project directory:

```bash
cd customer-complaint-classifier-nlp
```


## 2. Create Virtual Environment

```bash
python -m venv .venv
```


Activate environment:

Windows:

```bash
.venv\Scripts\activate
```


## 3. Install Dependencies

```bash
pip install -r requirements.txt
```


# Run Application

Start Flask server:

```bash
python app.py
```


Application will run on:

```
http://127.0.0.1:5000
```


# API Endpoints


## Health Check

GET:

```
/health
```

Example response:

```json
{
 "status":"healthy",
 "model_loaded":true
}
```


## Prediction API

POST:

```
/predict
```


Request:

```json
{
 "complaint_text":"I have an issue with my credit card payment"
}
```


Response:

```json
{
 "status":"success",
 "predicted_category":"Credit Card",
 "confidence_scores":[]
}
```


# Docker Deployment


Build Docker image:

```bash
docker build -t complaint-classifier .
```


Run container:

```bash
docker run -p 5000:5000 complaint-classifier
```


Open:

```
http://localhost:5000
```


# Future Improvements

- Deploy using AWS EC2
- Add deep learning based NLP models
- Add authentication system
- Add database integration
- Improve classification accuracy


# Author

**Sohel Maniyar**

B.Tech Computer Science Engineering

GitHub:
https://github.com/Maniyar07


# License

This project is created for learning and demonstration purposes.