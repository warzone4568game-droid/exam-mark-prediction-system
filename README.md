# Exam Mark Prediction System

A full-stack web application that uses Machine Learning to predict college students' semester marks based on their academic performance and study habits.

## 📋 Features

- **Smart Predictions**: Uses Linear Regression model to predict next semester marks
- **OCR Processing**: Automatically extract marks from uploaded result images
- **Comprehensive Analytics**: Detailed performance metrics (R² Score, RMSE, MSE, MAE)
- **Student Dashboard**: View all predictions and performance trends
- **Data Storage**: SQLite database to store student records
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Beautiful UI**: Modern and user-friendly interface

## 🏗️ Project Structure

```
finial_pro/
├── backend/
│   ├── app.py                 # Flask application
│   └── ocr_handler.py         # OCR image processing
├── frontend/
│   ├── index.html             # Home page
│   ├── css/
│   │   └── style.css          # Styles
│   ├── js/
│   │   ├── common.js          # Common functions
│   │   ├── form.js            # Form handling
│   │   └── dashboard.js       # Dashboard functions
│   └── pages/
│       ├── form.html          # Prediction form
│       ├── dashboard.html     # Analytics dashboard
│       └── about.html         # About page
├── ml_model/
│   └── model.py               # Linear Regression model
├── database/
│   ├── db_handler.py          # Database operations
│   └── exam_marks.db          # SQLite database
├── uploads/                   # Uploaded images
├── requirements.txt           # Python dependencies
└── README.md                  # Documentation
```

## 🔧 Technology Stack

### Frontend
- HTML5
- CSS3
- JavaScript (Vanilla)
- Chart.js (for visualizations)

### Backend
- Python 3.8+
- Flask 2.3.2
- Flask-CORS

### Machine Learning
- Scikit-learn (Linear Regression)
- NumPy
- Pandas
- Matplotlib & Seaborn

### Image Processing
- Tesseract OCR
- Pillow
- OpenCV

### Database
- SQLite3

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Tesseract-OCR installed on your system

### Install Tesseract OCR

**Windows:**
1. Download the installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Run the installer (default path: `C:\Program Files\Tesseract-OCR`)
3. Update the pytesseract path in `backend/ocr_handler.py` if needed

**macOS:**
```bash
brew install tesseract
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install tesseract-ocr
```

### Setup Instructions

1. **Clone or navigate to the project directory:**
```bash
cd finial_pro
```

2. **Create a virtual environment:**
```bash
python -m venv venv
```

3. **Activate virtual environment:**
   - Windows:
   ```bash
   venv\Scripts\activate
   ```
   - macOS/Linux:
   ```bash
   source venv/bin/activate
   ```

4. **Install dependencies:**
```bash
pip install -r requirements.txt
```

5. **Run the Flask application:**
```bash
python backend/app.py
```

6. **Open your browser and navigate to:**
```
http://localhost:5000
```

## 🚀 Usage

### Making a Prediction

1. Go to "Predict Marks" page
2. Enter your student information:
   - Student Name
   - Student ID
   - Current Attendance Percentage (0-100)
   - Internal Assessment Marks (0-100)
   - Daily Study Hours (0-24)
   - Previous Semester Marks (0-100)

3. (Optional) Upload an image of your previous semester result
4. Click "Get Prediction"
5. View your predicted marks and performance metrics

### Viewing the Dashboard

- Navigate to "Dashboard" to see:
  - System statistics
  - All student predictions
  - Performance comparison graphs
  - Model metrics and feature importance
  - Option to export data as CSV

## 📊 Machine Learning Model

### Algorithm
- **Type**: Linear Regression
- **Features**: 
  - Attendance Percentage
  - Internal Assessment Marks
  - Daily Study Hours
  - Previous Semester Marks

### Model Metrics

- **R² Score**: Coefficient of determination (0-1, higher is better)
- **RMSE**: Root Mean Square Error (lower is better)
- **MSE**: Mean Square Error (lower is better)
- **MAE**: Mean Absolute Error (lower is better)

### Data Preprocessing
- Missing value handling
- Feature scaling and normalization
- Data validation

## 📁 API Endpoints

### Health Check
```
GET /api/health
```

### Make Prediction
```
POST /api/predict
Body: {
    "student_name": "string",
    "student_id": "string",
    "attendance": float,
    "internal_marks": float,
    "study_hours": float,
    "previous_semester_marks": float
}
```

### Upload Image
```
POST /api/upload-image
Body: Form data with 'image' file
```

### Get All Records
```
GET /api/student-records
```

### Get Student Records
```
GET /api/student-records/<student_id>
```

### Get Statistics
```
GET /api/statistics
```

### Get Model Info
```
GET /api/model-info
```

### Retrain Model
```
POST /api/retrain-model
```

## 🎯 How It Works

1. **Data Collection**: User inputs academic data
2. **Image Processing**: OCR extracts marks from uploaded images
3. **Preprocessing**: Data is normalized and scaled
4. **Prediction**: Linear Regression model generates prediction
5. **Storage**: Results are saved in database
6. **Analytics**: Dashboard displays trends and metrics

## 📈 Performance Analysis

The system provides detailed performance metrics:

| Metric | Explanation |
|--------|-------------|
| R² Score | How well the model explains variance (0-1) |
| RMSE | Average prediction error in marks |
| MSE | Squared average prediction error |
| MAE | Mean absolute prediction error |

## 🔒 Data Privacy

- All data is stored locally in SQLite
- No data is shared with external services
- Students' personal information is used only for prediction
- Database can be backed up and secured

## ⚙️ Configuration

### Modify OCR Tesseract Path (if needed)

In `backend/ocr_handler.py`:
```python
pytesseract.pytesseract.pytesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

### Change Flask Port

In `backend/app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

### Update API URL in Frontend

In `frontend/js/common.js`:
```javascript
const API_BASE_URL = 'http://localhost:5000/api';
```

## 🐛 Troubleshooting

### Tesseract not found error
- Ensure Tesseract-OCR is installed
- Update the path in `ocr_handler.py`

### CORS errors
- Ensure Flask-CORS is installed
- Check that API URL in frontend matches backend URL

### Database errors
- Delete `database/exam_marks.db` to reset
- Database will be recreated on next run

### Port already in use
- Change port in `app.py`
- Or kill process using port 5000

## 📝 Example Workflow

```
1. Student enters details (attendance: 85%, internal: 70, study hours: 3, previous: 75)
2. System normalizes data
3. Linear Regression model predicts marks: 78
4. Results displayed with R² Score: 0.85, RMSE: 3.5
5. Comparison shows improvement from previous semester
6. Recommendations provided for improvement
7. Data stored in database for future analysis
```

## 🎓 Educational Use

This system is designed for:
- Educational institutions
- Student self-assessment
- Academic planning
- Performance analysis
- Research purposes

## ⚠️ Limitations

- Predictions based on historical patterns
- May vary with curriculum changes
- Should not be considered guaranteed
- Requires minimum 5 records for retraining

## 🤝 Contributing

Feel free to improve the system by:
- Adding more features
- Improving ML model
- Enhancing UI/UX
- Fixing bugs

## 📄 License

This project is open source and available for educational purposes.

## 👨‍💻 Developer Notes

### Adding New Features

1. Backend: Add endpoints in `app.py`
2. Frontend: Add corresponding UI in HTML
3. ML: Improve model in `ml_model/model.py`
4. Database: Update schema in `db_handler.py`

### Testing

Test endpoints using:
- Postman
- cURL
- Browser DevTools

### Performance Optimization

- Cache prediction results
- Optimize database queries
- Minimize OCR processing time
- Compress static assets

## 📞 Support

For issues or questions:
1. Check documentation
2. Review troubleshooting section
3. Check console for error messages
4. Verify all dependencies are installed

---

**Built with ❤️ using Flask, Machine Learning & JavaScript**

Last Updated: 2024
