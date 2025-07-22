# 🗜️ Prometheus File Compressor

**Prometheus** is a powerful, modern file compression tool for images and PDFs. Built with Python 3.13 and PyQt5, it provides users full control over file size optimization without compromising usability or file integrity.

---

## ✨ Features

- ✅ Drag & Drop interface
- 📁 Batch processing of:
  - `.jpg`, `.jpeg`, `.png`, `.pdf`
- 📸 Image Compression Options:
  - Resize by % or dimensions
  - Adjustable quality
  - Format and background control (e.g., PNG transparency)
- 📄 PDF Compression:
  - User-defined DPI
  - Optional metadata removal
  - Same layout, reduced size
- 🌗 Dark/Light theme toggle
- 💾 Save-as dialog with rename + path control
- 🛠 Built with:
  - `PyQt5`, `Pillow`, `PyMuPDF`

---

## 🧑‍💻 Built With

- Python 3.13
- PyQt5
- Pillow
- PyMuPDF (fitz)

---

## 🖥️ Run Locally

```bash
git clone https://github.com/YOUR_USERNAME/Prometheus.git
cd Prometheus
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
