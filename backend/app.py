import os
import sys
import json
import traceback
from datetime import datetime

# Absolute path resolution
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
sys.path.append(os.path.join(BASE_DIR, 'backend'))

try:
    from flask import Flask, request, jsonify, send_from_directory
    from flask_cors import CORS
    from werkzeug.utils import secure_filename
    import numpy as np
    from ml_model.model import MarksPredictor
    from database.db_handler import DatabaseHandler
    # Import ocr_handler with fallback
    try:
        from ocr_handler import OCRHandler
    except ImportError:
        from backend.ocr_handler import OCRHandler
except ImportError as e:
    print(f"CRITICAL ERROR: Missing dependency: {e}")
    sys.exit(1)

# Directories
FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')

# Initialize Flask app
app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')
CORS(app)

# Configuration
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Initialize components with error handling
try:
    db_handler = DatabaseHandler(db_path=os.path.join(BASE_DIR, 'database', 'exam_marks.db'))
    marks_predictor = MarksPredictor(
        model_path=os.path.join(BASE_DIR, 'ml_model', 'trained_model.pkl'),
        scaler_path=os.path.join(BASE_DIR, 'ml_model', 'scaler.pkl')
    )
    ocr_handler = OCRHandler()
except Exception as e:
    print(f"CRITICAL ERROR during component initialization: {e}")
    traceback.print_exc()
    sys.exit(1)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Exam Mark Prediction System is running'}), 200

@app.route('/api/predict', methods=['POST'])
def predict_marks():
    """
    Predict marks based on student input
    Expected JSON: {
        "attendance": float,
        "internal_marks": float,
        "study_hours": float,
        "previous_semester_marks": float,
        "student_name": string,
        "student_id": string
    }
    """
    try:
        data = request.get_json()
        
        # Validate input
        required_fields = ['attendance', 'internal_marks', 'study_hours', 'previous_semester_marks']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Extract features
        features = np.array([[
            float(data['attendance']),
            float(data['internal_marks']),
            float(data['study_hours']),
            float(data['previous_semester_marks'])
        ]])
        
        # Make prediction
        predicted_marks, accuracy_metrics = marks_predictor.predict(features)
        
        # Prepare response
        response = {
            'predicted_marks': float(predicted_marks[0]),
            'accuracy_metrics': {
                'mse': float(accuracy_metrics['mse']),
                'rmse': float(accuracy_metrics['rmse']),
                'r2_score': float(accuracy_metrics['r2_score']),
                'mae': float(accuracy_metrics['mae'])
            },
            'timestamp': datetime.now().isoformat()
        }
        
        # Store in database if student info is provided
        if 'student_name' in data and 'student_id' in data:
            student_record = {
                'student_id': data['student_id'],
                'student_name': data['student_name'],
                'attendance': float(data['attendance']),
                'internal_marks': float(data['internal_marks']),
                'study_hours': float(data['study_hours']),
                'previous_semester_marks': float(data['previous_semester_marks']),
                'predicted_marks': float(predicted_marks[0]),
                'prediction_date': datetime.now().isoformat()
            }
            db_handler.add_student_record(student_record)
        
        return jsonify(response), 200
    
    except Exception as e:
        print(f"Error in predict_marks: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload-image', methods=['POST'])
def upload_image():
    """
    Upload and process image using OCR
    Returns extracted marks from the image
    """
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Allowed: ' + ', '.join(ALLOWED_EXTENSIONS)}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Create upload folder if it doesn't exist
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        file.save(filepath)
        
        # Extract text using OCR
        extracted_text = ocr_handler.extract_text(filepath)
        
        # Parse marks from extracted text
        parsed_marks = ocr_handler.parse_marks(extracted_text)
        
        response = {
            'filename': filename,
            'extracted_text': extracted_text,
            'parsed_marks': parsed_marks,
            'message': 'Image processed successfully'
        }
        
        return jsonify(response), 200
    
    except Exception as e:
        print(f"Error in upload_image: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/api/student-records', methods=['GET'])
def get_student_records():
    """Get all student prediction records"""
    try:
        records = db_handler.get_all_records()
        return jsonify({'records': records, 'total': len(records)}), 200
    except Exception as e:
        print(f"Error in get_student_records: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/student-records/<student_id>', methods=['GET'])
def get_student_record(student_id):
    """Get specific student records"""
    try:
        records = db_handler.get_records_by_student(student_id)
        return jsonify({'records': records}), 200
    except Exception as e:
        print(f"Error in get_student_record: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get prediction statistics"""
    try:
        stats = db_handler.get_statistics()
        return jsonify(stats), 200
    except Exception as e:
        print(f"Error in get_statistics: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/model-info', methods=['GET'])
def get_model_info():
    """Get model information and training metrics"""
    try:
        model_info = marks_predictor.get_model_info()
        return jsonify(model_info), 200
    except Exception as e:
        print(f"Error in get_model_info: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/retrain-model', methods=['POST'])
def retrain_model():
    """Retrain the model with current database records"""
    try:
        records = db_handler.get_all_records()
        if len(records) < 5:
            return jsonify({'error': 'Insufficient data to retrain (minimum 5 records required)'}), 400
        
        # Prepare data for training
        X = []
        y = []
        for record in records:
            X.append([
                record['attendance'],
                record['internal_marks'],
                record['study_hours'],
                record['previous_semester_marks']
            ])
            y.append(record['predicted_marks'])
        
        # Retrain model
        metrics = marks_predictor.retrain(np.array(X), np.array(y))
        
        return jsonify({
            'message': 'Model retrained successfully',
            'metrics': metrics
        }), 200
    
    except Exception as e:
        print(f"Error in retrain_model: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/comparison-data', methods=['GET'])
def get_comparison_data():
    """Get data for comparison graph (actual vs predicted)"""
    try:
        records = db_handler.get_all_records()
        
        # Prepare comparison data
        student_names = []
        predictions = []
        
        for record in records:
            student_names.append(record['student_name'][:10])  # Truncate long names
            predictions.append({
                'previous': record['previous_semester_marks'],
                'predicted': record['predicted_marks']
            })
        
        return jsonify({
            'student_names': student_names,
            'predictions': predictions
        }), 200
    
    except Exception as e:
        print(f"Error in get_comparison_data: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Serve frontend
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

# Error handlers
@app.errorhandler(404)
def not_found(error):
    # For any 404, if it's not an API call, try to serve from static folder
    if not request.path.startswith('/api/'):
        return send_from_directory(app.static_folder, 'index.html')
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("\n" + "="*40)
    print("Exam Mark Prediction System Starting...")
    print("="*40)
    
    # Initialize database
    print("Initializing database...")
    try:
        db_handler.init_db()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"CRITICAL ERROR: Failed to initialize database: {e}")
        sys.exit(1)
    
    # Load or train model
    print("Loading machine learning model...")
    try:
        marks_predictor.load_model()
        print("Model ready for predictions.")
    except Exception as e:
        print(f"ERROR: Failed to load model: {e}")
        # Not exiting as the model might train itself on first request
    
    print(f"\nServer is starting at http://127.0.0.1:5000")
    print("Press CTRL+C to stop the server.")
    print("="*40 + "\n")
    
    # Run Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
