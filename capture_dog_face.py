from picamera2 import Picamera2
import cv2
import os

# Folder to save images
save_dir = "dog_images"
os.makedirs(save_dir, exist_ok=True)

# Helper to get the next index for filename
def get_next_index(dog_name):
    files = [f for f in os.listdir(save_dir) if f.startswith(dog_name) and f.endswith(".jpg")]
    indices = [int(f.split("_")[1].split(".")[0]) for f in files if "_" in f]
    return max(indices + [0]) + 1

# Initialize camera
picam2 = Picamera2()
picam2.preview_configuration.main.size = (640, 480)
picam2.preview_configuration.main.format = "RGB888"
picam2.configure("preview")
picam2.set_controls({"AfMode": 1})  # Enable continuous autofocus
picam2.start()

# Dog name toggle
current_dog = "gomi"
print("🐶 Press [SPACE] to capture")
print("🔁 Press [D] to switch between 'gomi' and 'millie'")
print("❌ Press [ESC] to quit")

while True:
    frame = picam2.capture_array()
    cv2.imshow("Dog Cam - Press SPACE to capture", frame)

    key = cv2.waitKey(1)
    if key == 27:  # ESC
        break
    elif key == 32:  # SPACE
        idx = get_next_index(current_dog)
        filename = f"{current_dog}_{idx}.jpg"
        filepath = os.path.join(save_dir, filename)
        # default is ~95 on OpenCV, but you can make it configurable.
        cv2.imwrite("img.jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
        print(f"📸 Saved: {filepath}")
    elif key == ord("d"):
        current_dog = "millie" if current_dog == "gomi" else "gomi"
        print(f"🔁 Switched to: {current_dog}")

cv2.destroyAllWindows()