import os

# Path to your project root and header file
PROJECT_DIR = "./"
HEADER_FILE = "header.txt"

# File types to apply header to
TARGET_EXTENSIONS = [".py"]

# Read header contents
with open(HEADER_FILE, "r") as f:
    header = f.read().rstrip() + "\n\n"

# Walk through project files
for folder, _, files in os.walk(PROJECT_DIR):
    for file in files:
        if file.endswith(tuple(TARGET_EXTENSIONS)):
            full_path = os.path.join(folder, file)

            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Skip files that already have header
            if header.strip() in content:
                continue

            # Skip this script to avoid recursion
            if file == os.path.basename(__file__):
                continue

            with open(full_path, "w", encoding="utf-8") as f:
                f.write(header + content)

            print(f"✅ Header added to: {full_path}")
