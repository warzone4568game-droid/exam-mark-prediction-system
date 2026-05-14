import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import pickle
import os
from datetime import datetime

class MarksPredictor:
    def __init__(self, model_path='ml_model/trained_model.pkl', scaler_path='ml_model/scaler.pkl'):
        """Initialize the CGPA predictor"""
        self.model_path = model_path
        self.scaler_path = scaler_path
        self.model = None
        self.scaler = None
        self.feature_names = ['Attendance %', 'Internal Marks (scaled to 30)', 'Study Hours', 'Previous Semester CGPA']
        self.metrics = {
            'mse': 0.0,
            'rmse': 0.0,
            'r2_score': 0.0,
            'mae': 0.0
        }
    
    def load_model(self):
        """Load trained model or create new one"""
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
                with open(self.scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
                
                # Try to load metrics if they exist
                metrics_path = self.model_path.replace('.pkl', '_metrics.pkl')
                if os.path.exists(metrics_path):
                    with open(metrics_path, 'rb') as f:
                        self.metrics = pickle.load(f)
                
                print("Model and metrics loaded successfully")
            else:
                # Create default model with synthetic data
                self._train_default_model()
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            self._train_default_model()
    
    def _train_default_model(self):
        """Train model with realistic synthetic CGPA data.
        
        Key principle: When a student has good attendance (85%+), good internals (22+/30),
        decent study hours (4+), and a reasonable previous CGPA, the predicted CGPA should
        be HIGHER than or at least close to the previous CGPA - never drastically lower.
        """
        try:
            np.random.seed(42)
            n_samples = 500
            
            # Generate diverse student profiles
            # Features: Attendance(0-100), Internal Marks(0-30), Study Hours(0-12), Previous CGPA(0-10)
            
            attendance = np.concatenate([
                np.random.uniform(90, 100, n_samples // 4),   # High attendance students
                np.random.uniform(80, 95, n_samples // 4),    # Good attendance
                np.random.uniform(70, 85, n_samples // 4),    # Average attendance
                np.random.uniform(40, 75, n_samples // 4),    # Low attendance
            ])
            
            internal_marks = np.concatenate([
                np.random.uniform(24, 30, n_samples // 4),    # Excellent internals
                np.random.uniform(18, 27, n_samples // 4),    # Good internals
                np.random.uniform(12, 20, n_samples // 4),    # Average internals
                np.random.uniform(3, 15, n_samples // 4),     # Weak internals
            ])
            
            study_hours = np.concatenate([
                np.random.uniform(5, 10, n_samples // 4),     # Dedicated studiers
                np.random.uniform(3, 7, n_samples // 4),      # Moderate study
                np.random.uniform(1, 4, n_samples // 4),      # Light study
                np.random.uniform(0, 3, n_samples // 4),      # Minimal study
            ])
            
            prev_cgpa = np.concatenate([
                np.random.uniform(8.0, 9.8, n_samples // 4),  # High performers
                np.random.uniform(6.5, 8.5, n_samples // 4),  # Good performers
                np.random.uniform(5.0, 7.0, n_samples // 4),  # Average performers
                np.random.uniform(3.0, 6.0, n_samples // 4),  # Struggling students
            ])
            
            # Shuffle all arrays together
            indices = np.random.permutation(n_samples)
            attendance = attendance[indices]
            internal_marks = internal_marks[indices]
            study_hours = study_hours[indices]
            prev_cgpa = prev_cgpa[indices]
            
            X = np.column_stack([attendance, internal_marks, study_hours, prev_cgpa])
            
            # Target CGPA calculation - designed so good inputs = good output
            # The formula ensures predicted CGPA is proportional to effort
            
            # Normalize each feature to 0-1 scale
            att_norm = attendance / 100.0          # 0 to 1
            int_norm = internal_marks / 30.0       # 0 to 1
            study_norm = np.minimum(study_hours, 10) / 10.0  # 0 to 1 (cap at 10)
            prev_norm = prev_cgpa / 10.0           # 0 to 1
            
            # Weighted combination (total weight = 1.0)
            # Previous CGPA has highest weight - it's the best predictor
            # Internal marks are very important - direct academic performance
            # Study hours and attendance support the score
            combined_score = (
                0.35 * prev_norm +       # Previous CGPA: 35% weight
                0.30 * int_norm +        # Internal Marks: 30% weight
                0.20 * study_norm +      # Study Hours: 20% weight
                0.15 * att_norm          # Attendance: 15% weight
            )
            
            # Scale to CGPA range (0-10)
            # A combined_score of 1.0 should give ~9.5-10.0
            # A combined_score of 0.5 should give ~5.0-6.0
            y = combined_score * 10.0
            
            # Add slight positive bias for good students (reward consistency)
            # If current effort (internal + study + attendance) is high, give a small boost
            current_effort = (att_norm + int_norm + study_norm) / 3.0
            boost = np.where(current_effort > 0.7, (current_effort - 0.7) * 1.5, 0)
            y = y + boost
            
            # Add small realistic noise
            noise = np.random.randn(n_samples) * 0.15
            y = y + noise
            
            # Ensure predicted CGPA is never unreasonably lower than previous CGPA
            # when the student is performing well currently
            for i in range(n_samples):
                if att_norm[i] > 0.75 and int_norm[i] > 0.6 and study_norm[i] > 0.3:
                    # Good student - prediction should be at least close to previous CGPA
                    y[i] = max(y[i], prev_cgpa[i] - 0.3)
            
            # Final clip to valid range
            y = np.clip(y, 0, 10)
            
            self._train_model(X, y)
        
        except Exception as e:
            print(f"Error training default model: {str(e)}")
    
    def _train_model(self, X, y):
        """Train the linear regression model"""
        try:
            # Initialize scaler
            self.scaler = StandardScaler()
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train model
            self.model = LinearRegression()
            self.model.fit(X_scaled, y)
            
            # Calculate metrics on training data
            y_pred = self.model.predict(X_scaled)
            self.metrics['mse'] = float(mean_squared_error(y, y_pred))
            self.metrics['rmse'] = float(np.sqrt(self.metrics['mse']))
            self.metrics['r2_score'] = float(r2_score(y, y_pred))
            self.metrics['mae'] = float(mean_absolute_error(y, y_pred))
            
            # Save model
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            with open(self.model_path, 'wb') as f:
                pickle.dump(self.model, f)
            with open(self.scaler_path, 'wb') as f:
                pickle.dump(self.scaler, f)
            
            # Save metrics
            metrics_path = self.model_path.replace('.pkl', '_metrics.pkl')
            with open(metrics_path, 'wb') as f:
                pickle.dump(self.metrics, f)
            
            print(f"Model trained successfully. R^2 Score: {self.metrics['r2_score']:.4f}")
        
        except Exception as e:
            print(f"Error training model: {str(e)}")
    
    def predict(self, X):
        """
        Make prediction using the trained model
        
        Args:
            X: Feature array (n_samples, 4)
                [attendance, internal_marks(out of 30), study_hours, previous_cgpa]
        
        Returns:
            predictions: Predicted CGPA
            metrics: Model metrics
        """
        try:
            if self.model is None or self.scaler is None:
                self.load_model()
            
            # Scale features
            X_scaled = self.scaler.transform(X)
            
            # Make prediction
            predictions = self.model.predict(X_scaled)
            
            # Post-processing: ensure prediction makes sense
            for i in range(len(predictions)):
                attendance = X[i][0]
                internal = X[i][1]
                study_hrs = X[i][2]
                prev_cgpa = X[i][3]
                
                # If student has good current performance, prediction should not be
                # drastically lower than previous CGPA
                if attendance >= 75 and internal >= 18 and study_hrs >= 3:
                    predictions[i] = max(predictions[i], prev_cgpa - 0.2)
                
                # If student has excellent current performance, give a slight boost
                if attendance >= 90 and internal >= 25 and study_hrs >= 5:
                    predictions[i] = max(predictions[i], prev_cgpa + 0.1)
            
            # Clip predictions to reasonable range (0-10 CGPA)
            predictions = np.clip(predictions, 0, 10)
            
            return predictions, self.metrics
        
        except Exception as e:
            print(f"Error in prediction: {str(e)}")
            return np.array([0]), self.metrics
    
    def retrain(self, X, y):
        """
        Retrain model with new data
        
        Args:
            X: Feature array
            y: Target array
        
        Returns:
            Updated metrics
        """
        try:
            if len(X) < 5:
                print("Insufficient data for retraining")
                return self.metrics
            
            self._train_model(X, y)
            return self.metrics
        
        except Exception as e:
            print(f"Error retraining model: {str(e)}")
            return self.metrics
    
    def get_model_info(self):
        """Get model information"""
        try:
            if self.model is None:
                self.load_model()
            
            coefficients = self.model.coef_ if self.model else [0, 0, 0, 0]
            intercept = self.model.intercept_ if self.model else 0
            
            return {
                'model_type': 'Linear Regression (CGPA)',
                'features': self.feature_names,
                'coefficients': [float(c) for c in coefficients],
                'intercept': float(intercept),
                'metrics': {
                    'mse': float(self.metrics['mse']),
                    'rmse': float(self.metrics['rmse']),
                    'r2_score': float(self.metrics['r2_score']),
                    'mae': float(self.metrics['mae'])
                },
                'last_updated': datetime.now().isoformat()
            }
        
        except Exception as e:
            print(f"Error getting model info: {str(e)}")
            return {}
    
    def get_feature_importance(self):
        """Get feature importance (coefficients for linear regression)"""
        try:
            if self.model is None:
                self.load_model()
            
            coefficients = np.abs(self.model.coef_)
            normalized = coefficients / np.sum(coefficients)
            
            importance = {}
            for name, value in zip(self.feature_names, normalized):
                importance[name] = float(value)
            
            return importance
        
        except Exception as e:
            print(f"Error getting feature importance: {str(e)}")
            return {}
