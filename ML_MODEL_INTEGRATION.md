# ML Model Integration Guide

This guide explains how to integrate your trained ML model for health risk prediction.

## Current Status

✅ **Placeholder prediction logic is working**
- Dashboard shows predictions based on simple rules
- All data collection is working (stress scans, habits)
- API endpoint `/api/predict` is ready

🔄 **Ready for your ML model**
- Structure prepared in `ml_model.py`
- Easy to swap placeholder with your trained model

---

## How to Integrate Your Trained Model

### Step 1: Train Your Model

Train your model using the data from your database:

**Features you can use:**
- `jaw_clench_score` (float 0-1)
- `mouth_open` (float 0-1)
- `eyebrow_raise` (float 0-1)
- `slouch_score` (float 0-1)
- `head_tilt_angle` (float)
- `shoulder_alignment_diff` (float 0-1)
- `spine_curve_ratio` (float 0-1)
- `pose_confidence` (float 0-1)
- `sleep_hours` (float)
- `work_hours` (float)
- `screen_time` (float)
- `water_intake` (float)
- `exercise` (boolean)
- `caffeine_intake` (boolean)
- `social_interaction` (string: None/Low/Medium/High)

**Target variables (what to predict):**
- Stress level (0-100)
- Health risks: hypertension, insomnia, anxiety, depression
- Risk level: Low/Medium/High

### Step 2: Save Your Model

Save your trained model to a file:

```python
# For scikit-learn
import joblib
joblib.dump(model, 'models/health_risk_model.pkl')

# For TensorFlow/Keras
model.save('models/health_risk_model.h5')

# For PyTorch
torch.save(model.state_dict(), 'models/health_risk_model.pt')
```

### Step 3: Update `ml_model.py`

1. **Import your libraries** (top of file):
```python
import joblib  # or tensorflow, torch, etc.
```

2. **Load your model** (in `__init__` method):
```python
def __init__(self, model_path='models/health_risk_model.pkl'):
    if model_path:
        self.model = joblib.load(model_path)
        self.model_loaded = True
```

3. **Update feature preparation** (in `prepare_features` method):
```python
# Make sure features match your training data
features = [
    avg_jaw_clench,
    avg_mouth_open,
    avg_slouch,
    # ... add all features in same order as training
]
```

4. **Update prediction** (in `predict` method):
```python
def predict(self, stress_scans, habits):
    features = self.prepare_features(stress_scans, habits)
    
    # Use your model
    stress_level = self.model.predict(features)[0]
    probabilities = self.model.predict_proba(features)[0]
    
    return {
        "stress_level": int(stress_level),
        "risk_level": self._determine_risk(stress_level),
        "health_risks": {
            "hypertension": probabilities[0] * 100,
            "insomnia": probabilities[1] * 100,
            # ... your model's outputs
        }
    }
```

### Step 4: Update `app.py`

Replace the placeholder in `/api/predict` endpoint:

```python
from ml_model import predictor

@app.post("/api/predict")
async def predict_health_risk(request: Request):
    # ... existing code ...
    
    # Replace placeholder with:
    prediction = predictor.predict(stress_scans, habits)
    
    return JSONResponse(content={
        "success": True,
        "prediction": prediction,
        "model_version": "your_model_v1.0"
    })
```

---

## Model Training Tips

### Recommended Approach

1. **Collect Data**: Use your app to collect real user data
2. **Label Data**: Get ground truth labels (actual health outcomes)
3. **Train Model**: Use scikit-learn, TensorFlow, or PyTorch
4. **Validate**: Test on holdout data
5. **Deploy**: Follow steps above to integrate

### Suggested Models

**For Classification (Risk Level: Low/Medium/High):**
- Random Forest Classifier
- Gradient Boosting (XGBoost, LightGBM)
- Neural Network

**For Regression (Stress Level: 0-100):**
- Linear Regression
- Random Forest Regressor
- Neural Network

### Example Training Code

```python
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib

# Load your data from database
# df = pd.read_csv('user_data.csv')

# Features
X = df[['jaw_clench_score', 'slouch_score', 'sleep_hours', ...]]

# Target
y = df['risk_level']  # or stress_level

# Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Train
model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)

# Evaluate
accuracy = model.score(X_test, y_test)
print(f"Accuracy: {accuracy}")

# Save
joblib.dump(model, 'models/health_risk_model.pkl')
```

---

## Testing Your Model

1. **Test locally**:
```python
from ml_model import predictor

# Test with sample data
prediction = predictor.predict(sample_scans, sample_habits)
print(prediction)
```

2. **Test via API**:
```bash
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"user_id": "your-user-id"}'
```

3. **Test in dashboard**: Predictions will automatically update

---

## Current Placeholder Logic

The current system uses simple rules:
- Stress = 40% jaw tension + 40% slouch + 20% posture
- Risk = High if >70%, Medium if 40-70%, Low if <40%

**This works for demonstration but should be replaced with your trained model for accurate predictions.**

---

## File Structure

```
mindlens/
├── app.py                    # Main API (has /api/predict endpoint)
├── ml_model.py              # Your model integration (UPDATE THIS)
├── models/                  # Create this folder for model files
│   └── health_risk_model.pkl  # Your trained model
├── database.py              # Data fetching (already done)
└── templates/
    └── dashboard.html       # Shows predictions (already done)
```

---

## Questions?

The structure is ready. When you have your trained model:
1. Save it to `models/` folder
2. Update `ml_model.py` with your model loading code
3. Test and deploy!

**Everything else is already working and waiting for your model!** 🚀
