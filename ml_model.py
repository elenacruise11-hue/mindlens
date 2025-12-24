"""
ML Model Integration for Health Risk Prediction
This module loads and uses the trained health risk prediction model.
"""

import os
import numpy as np
import joblib
from typing import Dict, Any

# Get the directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))
# Path to the model file
MODEL_PATH = os.path.join(current_dir, 'final_health_model.pkl')


class HealthRiskPredictor:
    """
    Health Risk Prediction Model
    
    TODO: Load and use your trained model here
    """
    
    def __init__(self, model_path=MODEL_PATH):
        """
        Initialize the health risk prediction model
        
        Args:
            model_path: Path to the trained model file (.pkl)
        """
        self.model = None
        self.model_loaded = False
        
        try:
            if model_path and os.path.exists(model_path):
                self.model = joblib.load(model_path)
                self.model_loaded = True
                print("Health risk prediction model loaded successfully!")
            else:
                print(f"Model file not found at {model_path}")
        except Exception as e:
            print(f"Error loading model: {str(e)}")
    
    def prepare_features(self, stress_scans, habits):
        """
        Prepare features from raw data for model input
        
        Args:
            stress_scans: List of stress scan records from database
            habits: List of habit records from database
            
        Returns:
            numpy array of features ready for model prediction
        """
        features = []
        
        # TODO: Extract and engineer features according to your model's training
        
        # Example feature extraction:
        if stress_scans and len(stress_scans) > 0:
            # Stress-related features
            avg_jaw_clench = np.mean([s.get("jaw_clench_score", 0) for s in stress_scans])
            avg_mouth_open = np.mean([s.get("mouth_open", 0) for s in stress_scans])
            avg_slouch = np.mean([s.get("slouch_score", 0) for s in stress_scans])
            avg_head_tilt = np.mean([s.get("head_tilt_angle", 0) for s in stress_scans])
            poor_posture_ratio = sum(1 for s in stress_scans if s.get("posture_quality") == "poor") / len(stress_scans)
            
            features.extend([
                avg_jaw_clench,
                avg_mouth_open,
                avg_slouch,
                avg_head_tilt,
                poor_posture_ratio
            ])
        else:
            # Default values if no stress scans
            features.extend([0, 0, 0, 0, 0])
        
        if habits and len(habits) > 0:
            # Habit-related features
            avg_sleep = np.mean([h.get("sleep_hours", 0) for h in habits])
            avg_work_hours = np.mean([h.get("work_hours", 0) for h in habits])
            avg_screen_time = np.mean([h.get("screen_time", 0) for h in habits])
            avg_water = np.mean([h.get("water_intake", 0) for h in habits])
            exercise_ratio = sum(1 for h in habits if h.get("exercise", False)) / len(habits)
            caffeine_ratio = sum(1 for h in habits if h.get("caffeine_intake", False)) / len(habits)
            
            features.extend([
                avg_sleep,
                avg_work_hours,
                avg_screen_time,
                avg_water,
                exercise_ratio,
                caffeine_ratio
            ])
        else:
            # Default values if no habits
            features.extend([0, 0, 0, 0, 0, 0])
        
        return np.array(features).reshape(1, -1)
    
    def predict(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make predictions using the loaded health risk model
        
        Args:
            input_data: Dictionary containing input features including:
                - stress_level: float (0-100)
                - sleep_quality: float (0-10)
                - exercise_frequency: int (times per week)
                - diet_quality: float (0-10)
                - social_support: float (0-10)
                
        Returns:
            dict: Prediction results with risk level, confidence, and recommendations
        """
        if not self.model_loaded:
            return {
                'error': 'Model not loaded',
                'predictions': None
            }
            
        try:
            # Prepare the feature vector in the correct order expected by the model
            features = [
                input_data.get('stress_level', 50),  # Default to 50 if not provided
                input_data.get('sleep_quality', 5),  # Default to 5 if not provided
                input_data.get('exercise_frequency', 3),  # Default to 3 if not provided
                input_data.get('diet_quality', 5),  # Default to 5 if not provided
                input_data.get('social_support', 5)  # Default to 5 if not provided
            ]
            
            # Make prediction
            prediction = self.model.predict_proba([features])[0]
            
            # Get the predicted class and confidence
            risk_classes = ['low', 'medium', 'high']
            predicted_class_idx = prediction.argmax()
            confidence = float(prediction[predicted_class_idx])
            risk_level = risk_classes[predicted_class_idx]
            
            # Generate recommendations based on risk level
            recommendations = self._generate_recommendations(risk_level, input_data)
            
            return {
                'risk_level': risk_level,
                'confidence': round(confidence, 2),
                'predictions': {
                    'low_risk': float(prediction[0]),
                    'medium_risk': float(prediction[1]),
                    'high_risk': float(prediction[2])
                },
                'recommendations': recommendations
            }
            
        except Exception as e:
            return {
                'error': f'Prediction error: {str(e)}',
                'predictions': None
            }
    
    def _generate_recommendations(self, risk_level: str, input_data: Dict[str, Any]) -> list:
        """Generate personalized recommendations based on risk level and input data"""
        recommendations = []
        
        # General recommendations based on risk level
        if risk_level == 'high':
            recommendations.append("Consider consulting a healthcare professional soon.")
            recommendations.append("Practice stress management techniques daily.")
        elif risk_level == 'medium':
            recommendations.append("Monitor your stress levels regularly.")
            recommendations.append("Maintain a healthy lifestyle balance.")
        else:
            recommendations.append("Keep up with your healthy habits!")
        
        # Specific recommendations based on input data
        if input_data.get('sleep_quality', 5) < 5:
            recommendations.append("Aim for 7-9 hours of quality sleep each night.")
            
        if input_data.get('exercise_frequency', 0) < 3:
            recommendations.append("Try to exercise at least 3 times a week.")
            
        if input_data.get('diet_quality', 5) < 5:
            recommendations.append("Consider improving your diet with more whole foods and vegetables.")
            
        if input_data.get('social_support', 5) < 5:
            recommendations.append("Spend more time with friends and family for better social support.")
            
        return recommendations
    
    def _placeholder_prediction(self, features):
        """
        Placeholder prediction logic
        TODO: Remove this when you integrate your trained model
        """
        # Simple rule-based prediction for demonstration
        avg_jaw = features[0][0]
        avg_slouch = features[0][2]
        avg_sleep = features[0][5]
        
        stress_level = int((avg_jaw * 40 + avg_slouch * 40 + (1 - min(avg_sleep/7, 1)) * 20) * 100)
        
        prediction = {
            "stress_level": min(stress_level, 100),
            "risk_level": "Low",
            "health_risks": {
                "hypertension": min(stress_level, 100),
                "insomnia": max(0, int((7 - avg_sleep) * 15)) if avg_sleep < 7 else 0,
                "anxiety": min(stress_level + 10, 100),
                "depression": min(stress_level - 10, 100) if stress_level > 10 else 0
            },
            "symptoms": [],
            "recommendations": []
        }
        
        # Detect symptoms
        if avg_jaw > 0.3:
            prediction["symptoms"].append("Jaw tension")
        if avg_slouch > 0.4:
            prediction["symptoms"].append("Poor posture")
        if avg_sleep < 6:
            prediction["symptoms"].append("Sleep deprivation")
        
        # Determine risk level
        if stress_level > 70:
            prediction["risk_level"] = "High"
            prediction["recommendations"].append("Consider professional stress management support")
            prediction["recommendations"].append("Prioritize rest and relaxation")
        elif stress_level > 40:
            prediction["risk_level"] = "Medium"
            prediction["recommendations"].append("Practice daily relaxation techniques")
            prediction["recommendations"].append("Maintain regular exercise routine")
        else:
            prediction["risk_level"] = "Low"
            prediction["recommendations"].append("Maintain current healthy habits")
        
        return prediction


# Global model instance
predictor = HealthRiskPredictor()


# Example usage:
"""
# In your app.py, replace the prediction logic with:

from ml_model import predictor

# Get predictions
prediction = predictor.predict(stress_scans, habits)
"""
