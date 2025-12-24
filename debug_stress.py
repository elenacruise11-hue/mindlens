import logging
import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

# Mock prediction result
prediction = {"stress_prediction": "low", "stress_confidence": 0.8}

# Logic from app.py
overall_stress = 20.0 if prediction["stress_prediction"] == "low" else 50.0 if prediction["stress_prediction"] == "medium" else 80.0

print(f"Prediction: {prediction}")
print(f"Calculated Overall Stress: {overall_stress}")

# Test with weird values
prediction_weird = {"stress_prediction": 16.53, "stress_confidence": 0.8}
overall_stress_weird = 20.0 if prediction_weird["stress_prediction"] == "low" else 50.0 if prediction_weird["stress_prediction"] == "medium" else 80.0
print(f"Weird Prediction: {prediction_weird}")
print(f"Calculated Overall Stress (Weird): {overall_stress_weird}")
