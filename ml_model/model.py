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
        """Train model with default synthetic CGPA data"""
        try:
            # Generate synthetic training data
            np.random.seed(42)
            n_samples = 100
            
            # Features: Attendance, Internal Marks (out of 30), Study Hours, Previous CGPA
            X = np.random.randn(n_samples, 4) * [10, 5, 2, 1.5] + [80, 20, 4, 7.5]
            X[:, 0] = np.clip(X[:, 0], 40, 100)  # Attendance: 40-100%
            X[:, 1] = np.clip(X[:, 1], 0, 30)    # Internal: 0-30
            X[:, 2] = np.clip(X[:, 2], 0, 12)    # Study hours: 0-12
            X[:, 3] = np.clip(X[:, 3], 0, 10)    # Previous CGPA: 0-10
            
            # Target: Predicted CGPA with realistic constraints
            # 1. Previous CGPA (45%) - strongest predictor
            # 2. Internal Marks (30%) - highly significant
            # 3. Study Hours (15%) - diminishing returns (log scale)
            # 4. Attendance (10%) - baseline requirement
            
            # Non-linear study impact: studying 12 hours isn't 6x better than 2 hours
            study_impact = np.log1p(X[:, 2]) * 0.8 
            
            # Base calculation
            y = (
                0.008 * X[:, 0] +      # Attendance impact (max 0.8)
                0.08 * X[:, 1] +       # Internal impact (max 2.4)
                study_impact +         # Study impact (max ~2.0)
                0.42 * X[:, 3] +       # Prev CGPA impact (max 4.2)
                np.random.randn(n_samples) * 0.15 # Real-world noise
            )
            
            # Cap and realistic scaling (harder to get 10.0)
            # Apply a slight curve to make high scores harder to reach
            y = np.where(y > 8.5, 8.5 + (y - 8.5) * 0.7, y)
            
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

