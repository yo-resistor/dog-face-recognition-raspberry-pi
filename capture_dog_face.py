import os
import sys
import time
import subprocess
import termios  # For low-level terminal control (e.g., disabling line buffering)
import tty      # For easily enabling raw terminal mode
import csv
from datetime import datetime

# Start with "gomi" as the active dog
current_dog = "gomi"

# Base directory for all dog images and metadata file
base_dir = "dog_images"
metadata_file = os.path.join(base_dir, "metadata.csv")

# Ensure dog-specific directories exist
for dog_name in ["gomi", "millie"]:
    os.makedirs(os.path.join(base_dir, dog_name), exist_ok=True)
    
# Ensure metadata.csv exists with header
if not os.path.exists(metadata_file):
    with open(metadata_file, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["dog_name", "filename", "filepath", "timestamp"])

# Get the next image index for a given dog (e.g., gomi_1.jpg → gomi_2.jpg)
def get_next_index(dog_name):
    dog_dir = os.path.join(base_dir, dog_name)
    files = [f for f in os.listdir(dog_dir) if f.startswith(dog_name) and f.endswith(".jpg")]
    indices = [int(f.split("_")[1].split(".")[0]) for f in files if "_" in f]
    return max(indices + [0]) + 1

# Generate file name for image
def make_filename(dog_name):
    index = get_next_index(dog_name)
    filename = f"{dog_name}_{index}.jpg"
    filepath = os.path.join(base_dir, dog_name, filename)
    print(f"[CAPTURE] Capturing {filepath}")
    return filepath, filename

# Save metadata in csv file
def save_metadata(dog_name, filename, filepath):
    timestamp = datetime.now().isoformat()
    with open(metadata_file, mode="a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([dog_name, filename, filepath, timestamp])

# Capture image using the Raspberry Pi's rpicam-jpeg command-line tool with autofocus
def capture_image(dog_name):
    [filepath, filename] = make_filename(dog_name)

    # Run the rpicam-jpeg command with autofocus and short delay to focus
    result = subprocess.run([
        "rpicam-jpeg",
        "--output", filepath,   # Output file path
        "--timeout", "2000",    # Wait 2 seconds for autofocus                    
        "--width", "1280",      # Width 1280 px
        "--height", "1280"       # Height 960 px
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print("[ERROR] Capture failed!")
        print("stderr:", result.stderr)
    else:
        print(f"[OK] Saved: {filepath}")
        save_metadata(dog_name, filename, filepath)

# Read a single key press without requiring ENTER (Unix only)
def get_key():
    fd = sys.stdin.fileno()                    # Get the file descriptor for stdin (usually 0)
    old_settings = termios.tcgetattr(fd)       # Save current terminal settings

    try:
        tty.setraw(fd)                         # Set terminal to raw mode (immediate key detection)
        ch = sys.stdin.read(1)                 # Read one character
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)  # Restore original terminal settings
    return ch

# Intro instructions
print("[INFO] Press [SPACE] to capture")
print("[INFO] Press [D] to switch dog (gomi/millie)")
print("[INFO] Press [ESC] to quit")
print("[INFO] Press [P] to preview for 5 seconds")

# Main loop to handle key inputs
try:
    while True:    
        key = get_key()

        if key == "\x1b":  # ESC key (ASCII code for escape)
            print("[EXIT] Exiting...")
            break
        elif key == " ":  # SPACE key
            capture_image(current_dog)
        elif key.lower() == "d":  # Toggle between "gomi" and "millie"
            current_dog = "millie" if current_dog == "gomi" else "gomi"
            print(f"[TOGGLE] Switched to: {current_dog}")
        elif key.lower() == "p":
            print("[PREVIEW] Starting preview for 5 seconds...")
            preview_proc = subprocess.Popen([
                "rpicam-hello", "--timeout", "5000"  # 5 seconds
            ])

except KeyboardInterrupt:
    # Graceful shutdown on Ctrl+C
    print("\n[EXIT] Interrupted and exiting...")