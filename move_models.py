import shutil
import os

def move_models():
    models = ["health_model.pkl", "stress_scan_model_bundle.pkl"]
    target_dir = "models"
    
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        print(f"Created directory: {target_dir}")
        
    for model in models:
        if os.path.exists(model):
            try:
                shutil.move(model, os.path.join(target_dir, model))
                print(f"Moved {model} to {target_dir}/")
            except Exception as e:
                print(f"Error moving {model}: {e}")
        else:
            print(f"File {model} not found in current directory.")

if __name__ == "__main__":
    move_models()
