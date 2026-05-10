# Exam Mark Prediction System - Installation & Setup Guide

## Quick Start

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install Tesseract OCR

**Windows:**
- Download from: https://github.com/UB-Mannheim/tesseract/wiki
- Default installation path: `C:\Program Files\Tesseract-OCR`
- Update path in `backend/ocr_handler.py` if installed elsewhere

**macOS:**
```bash
brew install tesseract
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

### 3. Run the Application

```bash
python backend/app.py
```

### 4. Access the Application

Open browser and go to: `http://localhost:5000`

## Features Available

✅ Student form for data input
✅ Image upload with OCR processing
✅ Predictions using Linear Regression
✅ Performance metrics display
✅ Student dashboard
✅ Data visualization with charts
✅ Student record storage
✅ Model retraining capability

## API Endpoints

The backend runs on `http://localhost:5000` and provides these endpoints:

- `GET /api/health` - Health check
- `POST /api/predict` - Make prediction
- `POST /api/upload-image` - Upload and process image
- `GET /api/statistics` - Get system statistics
- `GET /api/student-records` - Get all predictions
- `GET /api/model-info` - Get model information
- `POST /api/retrain-model` - Retrain the model

## Project Structure

```
backend/          - Flask application & ML model
frontend/         - HTML, CSS, JavaScript UI
ml_model/         - Linear Regression model
database/         - SQLite database handler
uploads/          - Uploaded image storage
```

## Troubleshooting

**Issue: Tesseract not found**
- Solution: Install Tesseract-OCR and update path in ocr_handler.py

**Issue: CORS errors**
- Solution: Ensure Flask-CORS is installed (pip install Flask-CORS)

**Issue: Port already in use**
- Solution: Change port in app.py or kill process on port 5000

**Issue: Database errors**
- Solution: Delete exam_marks.db file - it will be recreated

## Next Steps

1. Make your first prediction
2. Upload result images for OCR testing
3. View predictions on dashboard
4. Export data as CSV
5. Retrain model with more data

Enjoy using the Exam Mark Prediction System!
