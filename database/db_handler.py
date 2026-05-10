import sqlite3
import json
import os
from datetime import datetime

class DatabaseHandler:
    def __init__(self, db_path='database/exam_marks.db'):
        """Initialize database handler"""
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else '.', exist_ok=True)
    
    def init_db(self):
        """Initialize database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create students table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT UNIQUE NOT NULL,
                student_name TEXT NOT NULL,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create predictions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                attendance REAL NOT NULL,
                internal_marks REAL NOT NULL,
                study_hours REAL NOT NULL,
                previous_semester_marks REAL NOT NULL,
                predicted_marks REAL NOT NULL,
                prediction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(student_id)
            )
        ''')
        
        # Create model metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS model_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mse REAL,
                rmse REAL,
                r2_score REAL,
                mae REAL,
                training_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_student_record(self, record):
        """
        Add or update student prediction record
        
        Args:
            record: Dictionary with student data
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if student exists
            cursor.execute('SELECT id FROM students WHERE student_id = ?', (record['student_id'],))
            student_exists = cursor.fetchone()
            
            # Insert or update student
            if not student_exists:
                cursor.execute('''
                    INSERT INTO students (student_id, student_name)
                    VALUES (?, ?)
                ''', (record['student_id'], record['student_name']))
            
            # Insert prediction record
            cursor.execute('''
                INSERT INTO predictions 
                (student_id, attendance, internal_marks, study_hours, previous_semester_marks, predicted_marks, prediction_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                record['student_id'],
                record['attendance'],
                record['internal_marks'],
                record['study_hours'],
                record['previous_semester_marks'],
                record['predicted_marks'],
                record.get('prediction_date', datetime.now().isoformat())
            ))
            
            conn.commit()
            conn.close()
            return True
        
        except Exception as e:
            print(f"Error adding student record: {str(e)}")
            return False
    
    def get_all_records(self):
        """Get all prediction records"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT p.*, s.student_name FROM predictions p
                JOIN students s ON p.student_id = s.student_id
                ORDER BY p.prediction_date DESC
            ''')
            
            records = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return records
        
        except Exception as e:
            print(f"Error getting records: {str(e)}")
            return []
    
    def get_records_by_student(self, student_id):
        """Get records for a specific student"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT p.*, s.student_name FROM predictions p
                JOIN students s ON p.student_id = s.student_id
                WHERE p.student_id = ?
                ORDER BY p.prediction_date DESC
            ''', (student_id,))
            
            records = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return records
        
        except Exception as e:
            print(f"Error getting student records: {str(e)}")
            return []
    
    def get_statistics(self):
        """Get overall statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total students
            cursor.execute('SELECT COUNT(DISTINCT student_id) as total FROM students')
            total_students = cursor.fetchone()[0]
            
            # Total predictions
            cursor.execute('SELECT COUNT(*) as total FROM predictions')
            total_predictions = cursor.fetchone()[0]
            
            # Average predicted marks
            cursor.execute('SELECT AVG(predicted_marks) as avg_predicted FROM predictions')
            avg_predicted = cursor.fetchone()[0]
            
            # Average previous semester marks
            cursor.execute('SELECT AVG(previous_semester_marks) as avg_previous FROM predictions')
            avg_previous = cursor.fetchone()[0]
            
            # Average attendance
            cursor.execute('SELECT AVG(attendance) as avg_attendance FROM predictions')
            avg_attendance = cursor.fetchone()[0]
            
            # Average study hours
            cursor.execute('SELECT AVG(study_hours) as avg_study_hours FROM predictions')
            avg_study_hours = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_students': total_students or 0,
                'total_predictions': total_predictions or 0,
                'average_predicted_marks': round(avg_predicted, 2) if avg_predicted else 0,
                'average_previous_marks': round(avg_previous, 2) if avg_previous else 0,
                'average_attendance': round(avg_attendance, 2) if avg_attendance else 0,
                'average_study_hours': round(avg_study_hours, 2) if avg_study_hours else 0
            }
        
        except Exception as e:
            print(f"Error getting statistics: {str(e)}")
            return {}
    
    def save_model_metrics(self, metrics):
        """Save model performance metrics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO model_metrics (mse, rmse, r2_score, mae)
                VALUES (?, ?, ?, ?)
            ''', (metrics['mse'], metrics['rmse'], metrics['r2_score'], metrics['mae']))
            
            conn.commit()
            conn.close()
            return True
        
        except Exception as e:
            print(f"Error saving metrics: {str(e)}")
            return False
    
    def get_latest_metrics(self):
        """Get latest model metrics"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM model_metrics
                ORDER BY training_date DESC
                LIMIT 1
            ''')
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return dict(row)
            return None
        
        except Exception as e:
            print(f"Error getting metrics: {str(e)}")
            return None
