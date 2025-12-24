import tkinter as tk
from tkinter import filedialog
from deepface import DeepFace

# Hide the main tkinter window
root = tk.Tk()
root.withdraw()

# Ask the user to pick two images
print("📁 Select first face image...")
img1_path = filedialog.askopenfilename(title="Select first face image", filetypes=[("Image files", "*.jpg *.jpeg *.png")])

print("📁 Select second face image...")
img2_path = filedialog.askopenfilename(title="Select second face image", filetypes=[("Image files", "*.jpg *.jpeg *.png")])

if not img1_path or not img2_path:
    print("⚠️ Image selection cancelled. Exiting...")
else:
    print(f"🔹 Comparing:\n1️⃣ {img1_path}\n2️⃣ {img2_path}\n")

    try:
        result = DeepFace.verify(img1_path=img1_path, img2_path=img2_path, model_name="VGG-Face")

        if result["verified"]:
            print("✅ Same person")
        else:
            print("❌ Different person")

        print("\n📊 Details:")
        print(result)

    except Exception as e:
        print(f"❌ Error: {e}")
