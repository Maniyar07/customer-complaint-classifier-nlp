
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import joblib
from pathlib import Path
import json
import csv
import os

# ------------------------------------------------------------
# Flask App Configuration
# ------------------------------------------------------------

app = Flask(__name__)
CORS(app)

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "models" / "best_complaint_classifier_pipeline.pkl"
ENCODER_PATH = BASE_DIR / "models" / "best_label_encoder.pkl"

METRICS_PATH = BASE_DIR / "reports" / "03_best_model_metrics.json"
CLASSIFICATION_REPORT_PATH = BASE_DIR / "reports" / "03_best_classification_report.csv"
EXPERIMENT_FILE = BASE_DIR / "reports" / "03_data_feature_experiment_results.csv"
MISCLASSIFIED_FILE = BASE_DIR / "reports" / "03_misclassified_samples.csv"

# ------------------------------------------------------------
# Safe File Loading
# ------------------------------------------------------------
def load_json_file(path, default=None):
    if default is None:
        default = {}
    try:
        if path.exists():
            with open(path, "r", encoding="utf-8") as file:
                return json.load(file)
    except Exception as error:
        print(f"Could not load JSON file {path}: {error}")
    return default


def load_csv_preview(path, limit=200):
    """
    Reads CSV report files without requiring pandas.
    Returns columns and rows so the frontend can build modern tables.
    """
    if not path.exists():
        return {
            "status": "error",
            "message": f"{path.name} not found.",
            "columns": [],
            "rows": []
        }

    try:
        with open(path, "r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)
            rows = []
            for index, row in enumerate(reader):
                if index >= limit:
                    break
                rows.append(row)

            return {
                "status": "success",
                "columns": reader.fieldnames or [],
                "rows": rows
            }

    except Exception as error:
        return {
            "status": "error",
            "message": str(error),
            "columns": [],
            "rows": []
        }


# ------------------------------------------------------------
# Load Model Files
# ------------------------------------------------------------
try:
    model = joblib.load(MODEL_PATH)
except Exception as error:
    model = None
    print(f"Model loading failed: {error}")

try:
    label_encoder = joblib.load(ENCODER_PATH) if ENCODER_PATH.exists() else None
except Exception as error:
    label_encoder = None
    print(f"Label encoder loading failed: {error}")

metrics = load_json_file(METRICS_PATH, default={})


# ------------------------------------------------------------
# Helper Functions
# ------------------------------------------------------------
def decode_prediction(prediction):
    """
    Converts encoded numeric prediction into original category name.
    """
    if label_encoder is not None:
        try:
            prediction_int = int(prediction)
            return label_encoder.inverse_transform([prediction_int])[0]
        except Exception:
            return str(prediction)

    return str(prediction)


def get_confidence_scores(text):
    """
    Returns model confidence scores with readable category names.
    """
    if model is None or not hasattr(model, "predict_proba"):
        return []

    probabilities = model.predict_proba([text])[0]

    if label_encoder is not None:
        class_names = label_encoder.classes_
    elif hasattr(model, "classes_"):
        class_names = model.classes_
    else:
        class_names = [f"Class {i}" for i in range(len(probabilities))]

    confidence_list = []

    for category, confidence in zip(class_names, probabilities):
        confidence_list.append({
            "category": str(category),
            "confidence": float(confidence),
            "confidence_percent": round(float(confidence) * 100, 2)
        })

    return sorted(confidence_list, key=lambda x: x["confidence"], reverse=True)


def metric_value(key, default=0):
    value = metrics.get(key, default)
    try:
        return float(value)
    except Exception:
        return default


def percentage(value):
    try:
        value = float(value)
        if value <= 1:
            value *= 100
        return round(value, 2)
    except Exception:
        return 0


# ------------------------------------------------------------
# Web UI Route
# ------------------------------------------------------------
@app.route("/", methods=["GET"])
def index():

    ui_metrics = {
        "accuracy": percentage(metric_value("accuracy", 0)),
        "macro_f1": percentage(metric_value("macro_f1", 0)),
        "weighted_f1": percentage(metric_value("weighted_f1", 0)),
        "training_rows": int(metrics.get("num_rows", 20874)),
        "num_classes": int(metrics.get("num_classes", 8)),
        "text_version": metrics.get("text_version", "clean_text"),
        "max_features": metrics.get("max_features", 30000),
        "min_samples_per_class": metrics.get("min_samples_per_class", 50),
        "model_name": metrics.get("model_name", "TF-IDF + Logistic Regression")
    }

    return render_template("index.html", metrics=ui_metrics)


# ------------------------------------------------------------
# API Routes
# ------------------------------------------------------------
@app.route("/api", methods=["GET"])
def api_home():
    return jsonify({
        "message": "Customer Complaint Classification API is running.",
        "model": "TF-IDF + Logistic Regression",
        "status": "success"
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy" if model is not None else "unhealthy",
        "model_loaded": model is not None,
        "label_encoder_loaded": label_encoder is not None,
        "metrics_loaded": bool(metrics)
    })


@app.route("/metrics", methods=["GET"])
def get_metrics():
    return jsonify(metrics)


@app.route("/reports/classification", methods=["GET"])
def classification_report():
    return jsonify(load_csv_preview(CLASSIFICATION_REPORT_PATH))


@app.route("/reports/experiments", methods=["GET"])
def experiment_report():
    return jsonify(load_csv_preview(EXPERIMENT_FILE))


@app.route("/reports/misclassified", methods=["GET"])
def misclassified_report():
    return jsonify(load_csv_preview(MISCLASSIFIED_FILE, limit=100))


@app.route("/reports/image/<path:filename>", methods=["GET"])
def report_image(filename):
    """
    Serves chart images from the reports folder:
    /reports/image/top_15_categories.png
    /reports/image/complaint_word_count_distribution.png
    """
    return send_from_directory(BASE_DIR / "reports", filename)


@app.route("/predict", methods=["POST"])
def predict():
    try:
        if model is None:
            return jsonify({
                "status": "error",
                "message": "Model is not loaded. Check models folder and file names."
            }), 500

        data = request.get_json(silent=True)

        if not data:
            return jsonify({
                "status": "error",
                "message": "No JSON data received."
            }), 400

        complaint_text = data.get("complaint_text", "")

        if complaint_text.strip() == "":
            return jsonify({
                "status": "error",
                "message": "complaint_text cannot be empty."
            }), 400

        prediction = model.predict([complaint_text])[0]
        prediction = decode_prediction(prediction)

        confidence_scores = get_confidence_scores(complaint_text)

        return jsonify({
            "status": "success",
            "input_text": complaint_text,
            "predicted_category": str(prediction),
            "confidence_scores": confidence_scores
        })

    except Exception as error:
        return jsonify({
            "status": "error",
            "message": str(error)
        }), 500


# ------------------------------------------------------------
# Run Flask App
# ------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(
        host="0.0.0.0",
        port=port,
        debug=False,
        use_reloader=False
    )
