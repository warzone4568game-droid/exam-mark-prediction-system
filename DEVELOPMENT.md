# Exam Mark Prediction System - Development Configuration

## Environment Setup

### Python Version
Recommended: Python 3.8 or higher

### Development Environment Variables
Create a `.env` file in the project root:

```
FLASK_ENV=development
FLASK_DEBUG=True
API_HOST=0.0.0.0
API_PORT=5000
DATABASE_PATH=database/exam_marks.db
UPLOAD_FOLDER=uploads
MAX_UPLOAD_SIZE=16777216
```

### Tesseract Configuration
For Windows, add to `backend/ocr_handler.py`:
```python
import pytesseract
pytesseract.pytesseract.pytesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

## Development Server

To run in development mode with auto-reload:

```bash
python backend/app.py
```

The server will start at `http://localhost:5000`

## Database

SQLite database is automatically created at:
- `database/exam_marks.db`

To reset the database:
1. Delete `database/exam_marks.db`
2. Restart the application
3. Database will be recreated with empty tables

## File Uploads

Uploaded images are stored in the `uploads/` directory.
Maximum file size: 16MB

## API Testing

Use any of these tools:
- **Postman**: Import API endpoints
- **cURL**: Command line testing
- **Thunder Client**: VS Code extension
- **Browser DevTools**: Network tab

Example cURL request:
```bash
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "student_name": "John Doe",
    "student_id": "STU001",
    "attendance": 85,
    "internal_marks": 70,
    "study_hours": 3,
    "previous_semester_marks": 75
  }'
```

## Frontend Development

### Live Reload
For automatic page refresh during development, use:
- Live Server extension in VS Code
- Or any local HTTP server

```bash
# Using Python
python -m http.server 8000

# Using Node (if installed)
npx http-server
```

## Performance Optimization

### Database Optimization
- Index frequently queried columns
- Archive old records periodically
- Use VACUUM command for cleanup

### Frontend Optimization
- Minify CSS and JavaScript
- Compress images
- Use CDN for libraries

### Backend Optimization
- Cache model predictions
- Optimize OCR processing
- Use connection pooling

## Testing

### Manual Testing Checklist
- [ ] Create new prediction
- [ ] Upload and process image
- [ ] View dashboard
- [ ] Export data
- [ ] Retrain model
- [ ] Test on different browsers
- [ ] Test on mobile devices

### Common Test Cases

1. **Valid Prediction**
   - Input: Valid student data
   - Expected: Prediction displayed with metrics

2. **Image Upload**
   - Input: Image file
   - Expected: OCR results displayed

3. **Dashboard**
   - Action: Navigate to dashboard
   - Expected: All statistics loaded and displayed

4. **Data Export**
   - Action: Click export
   - Expected: CSV file downloaded

## Troubleshooting Development

### Issue: Module not found
```bash
pip install -r requirements.txt
```

### Issue: Port 5000 in use
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/macOS
lsof -i :5000
kill -9 <PID>
```

### Issue: Database locked
- Stop the application
- Delete database if corrupted
- Restart application

### Issue: OCR not working
- Verify Tesseract installation
- Check path in ocr_handler.py
- Test with simple image first

## Deployment

### Production Deployment

1. Use Gunicorn instead of Flask dev server:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 backend.app:app
```

2. Configure reverse proxy (Nginx/Apache)
3. Use SSL certificates
4. Set up proper logging
5. Configure database backup

### Cloud Deployment

Suitable platforms:
- Heroku
- AWS EC2
- Google Cloud
- Azure App Service

## Logging

Add logging to track issues:

```python
import logging

logging.basicConfig(
    filename='app.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## Security Considerations

- Validate all user inputs
- Sanitize file uploads
- Use HTTPS in production
- Implement authentication for admin features
- Regularly update dependencies
- Backup database regularly

## Performance Monitoring

Key metrics to track:
- Average prediction time
- OCR processing time
- API response times
- Database query times
- Server memory usage
- Error rates

## Maintenance

### Regular Tasks
- Monitor error logs
- Update dependencies
- Backup database
- Clean up uploaded files
- Archive old data
- Review performance metrics

### Monthly
- Database optimization
- Security updates
- Performance analysis

### Quarterly
- Full system audit
- Capacity planning
- Feature updates

---

For more information, see README.md
