# ──────────────────────────────────────────────────────────────
#  Prometheus File Compressor
#  Version: 0.1.0
#  License: MIT (see LICENSE file for details)
#
#  Author: Yashwant Singh
#  GitHub: https://github.com/yashwantsingh0/Prometheus
#
#  Description:
#      Compress JPG, PNG, and PDF files with full user control.
#      Features drag & drop, save-as, image quality tuning, and PDF DPI reduction.
#
#  ⚠️ This file is part of the Prometheus Project.
#     Do not remove or modify attribution headers in redistributed versions.
# ──────────────────────────────────────────────────────────────
# gui/interface.py

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton,
    QFileDialog, QMenuBar, QAction, QMessageBox, QStyleFactory,
    QApplication, QScrollArea, QGridLayout, QHBoxLayout, QSpinBox,
    QComboBox, QGroupBox, QFormLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPalette, QColor, QPixmap
import os

from compression.image_compressor import compress_image
from compression.pdf_compressor import compress_pdf

SUPPORTED_FORMATS = (".jpg", ".jpeg", ".png", ".pdf")

class PrometheusApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Prometheus - File Compressor")
        self.setMinimumSize(900, 700)
        self.setAcceptDrops(True)
        self.theme = "light"
        self.preview_files = []
        self.preview_widgets = {}

        self.init_ui()

    def init_ui(self):
        self.create_menu()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.layout = QVBoxLayout(central_widget)
        self.layout.setAlignment(Qt.AlignTop)

        self.drop_label = QLabel("\n\n⬇️  Drag & Drop files here  ⬇️\n\n")
        self.drop_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                padding: 40px;
                font-size: 18px;
                color: #666;
            }
        """)
        self.drop_label.setAlignment(Qt.AlignCenter)

        self.button = QPushButton("📁 Choose Files...")
        self.button.setStyleSheet("padding: 10px 20px; font-size: 16px;")
        self.button.clicked.connect(self.open_file_dialog)

        self.compress_button = QPushButton("🔧 Compress All")
        self.compress_button.setStyleSheet("padding: 10px 20px; font-size: 16px;")
        self.compress_button.clicked.connect(self.compress_all_files)

        # Compression options UI
        self.options_group = QGroupBox("Compression Settings")
        options_layout = QFormLayout()

        self.quality_spin = QSpinBox()
        self.quality_spin.setRange(10, 100)
        self.quality_spin.setValue(85)
        options_layout.addRow("Image Quality (%)", self.quality_spin)

        self.resize_spin = QSpinBox()
        self.resize_spin.setRange(10, 100)
        self.resize_spin.setValue(100)
        options_layout.addRow("Resize Percent (For IMGs/PDFs)", self.resize_spin)

        self.dpi_spin = QSpinBox()
        self.dpi_spin.setRange(50, 300)
        self.dpi_spin.setValue(120)
        options_layout.addRow("DPI (Only for PDF)", self.dpi_spin)

        self.options_group.setLayout(options_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.preview_container = QWidget()
        self.preview_layout = QGridLayout(self.preview_container)
        self.scroll_area.setWidget(self.preview_container)

        self.layout.addWidget(self.drop_label)
        self.layout.addWidget(self.button)
        self.layout.addWidget(self.options_group)
        self.layout.addWidget(self.compress_button)
        self.layout.addWidget(self.scroll_area)

        self.apply_theme()

    def create_menu(self):
        menubar = QMenuBar(self)
        self.setMenuBar(menubar)

        file_menu = menubar.addMenu("File")
        open_action = QAction("Open Files", self)
        open_action.triggered.connect(self.open_file_dialog)
        file_menu.addAction(open_action)

        file_menu.addSeparator()
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        theme_menu = menubar.addMenu("Theme")
        toggle_theme = QAction("Dark/Light", self)
        toggle_theme.triggered.connect(self.toggle_theme)
        theme_menu.addAction(toggle_theme)

        about_menu = menubar.addMenu("Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        about_menu.addAction(about_action)

    def open_file_dialog(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select files", "",
            "Images and PDFs (*.jpg *.jpeg *.png *.pdf)"
        )
        if files:
            self.handle_files(files)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        self.handle_files(files)

    def handle_files(self, files):
        valid_files = [f for f in files if f.lower().endswith(SUPPORTED_FORMATS)]
        if not valid_files:
            QMessageBox.warning(self, "Unsupported", "No supported files selected.")
            return

        for file_path in valid_files:
            if file_path not in self.preview_files:
                self.preview_files.append(file_path)
                self.add_preview(file_path)

        self.refresh_preview_grid()

    def add_preview(self, file_path):
        base_name = os.path.basename(file_path)
        container = QWidget()
        layout = QVBoxLayout(container)

        if file_path.lower().endswith((".jpg", ".jpeg", ".png")):
            pixmap = QPixmap(file_path).scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        else:
            pixmap = QPixmap(100, 100)
            pixmap.fill(Qt.gray)
        thumb = QLabel()
        thumb.setPixmap(pixmap)
        thumb.setAlignment(Qt.AlignCenter)

        name = QLabel(base_name)
        name.setAlignment(Qt.AlignCenter)
        name.setWordWrap(True)

        remove_btn = QPushButton("🗑️")
        remove_btn.setFixedSize(28, 28)
        remove_btn.clicked.connect(lambda: self.remove_preview(file_path))

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(remove_btn)

        layout.addLayout(btn_layout)
        layout.addWidget(thumb)
        layout.addWidget(name)

        self.preview_widgets[file_path] = container

    def refresh_preview_grid(self):
        for i in reversed(range(self.preview_layout.count())):
            widget = self.preview_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        for i, file_path in enumerate(self.preview_files):
            widget = self.preview_widgets[file_path]
            row = i // 4
            col = i % 4
            self.preview_layout.addWidget(widget, row, col)

    def remove_preview(self, file_path):
        if file_path in self.preview_files:
            self.preview_files.remove(file_path)
        widget = self.preview_widgets.pop(file_path, None)
        if widget:
            widget.setParent(None)
        self.refresh_preview_grid()


    def compress_all_files(self):
        if not self.preview_files:
            QMessageBox.information(self, "No files", "Please add files to compress.")
            return

        quality = self.quality_spin.value()
        resize = self.resize_spin.value()
        dpi = self.dpi_spin.value()

        for path in self.preview_files:
            suggested_name = os.path.splitext(os.path.basename(path))[0] + "_compressed"
            if path.lower().endswith((".jpg", ".jpeg")):
                extension = ".jpg"
            elif path.lower().endswith(".png"):
                extension = ".png"
            elif path.lower().endswith(".pdf"):
                extension = ".pdf"
            else:
                continue

            save_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Compressed File As",
                suggested_name + extension,
                f"*{extension}"
            )

            if not save_path:
                continue

            try:
                if path.lower().endswith((".jpg", ".jpeg", ".png")):
                    compressed = compress_image(path, output_path=save_path, quality=quality, resize_percent=resize)
                elif path.lower().endswith(".pdf"):
                    compressed = compress_pdf(path, output_path=save_path, dpi=dpi)

                if compressed:
                    print(f"Compressed and saved: {compressed}")
                else:
                    raise Exception("Compression returned None")

            except Exception as e:
                print(f"PDF compression failed: {e}")
                traceback.print_exc()
                QMessageBox.critical(self, "Compression Error", f"Failed to compress file:\n{path}\n\n{str(e)}")

        QMessageBox.information(self, "Done", "Compression completed.")


    def toggle_theme(self):
        self.theme = "dark" if self.theme == "light" else "light"
        self.apply_theme()

    def apply_theme(self):
        if self.theme == "dark":
            palette = QPalette()
            palette.setColor(QPalette.Window, QColor(45, 45, 45))
            palette.setColor(QPalette.WindowText, Qt.white)
            palette.setColor(QPalette.Base, QColor(25, 25, 25))
            palette.setColor(QPalette.Text, Qt.white)
            palette.setColor(QPalette.Button, QColor(60, 60, 60))
            palette.setColor(QPalette.ButtonText, Qt.white)
            self.setPalette(palette)
            self.setStyle(QStyleFactory.create("Fusion"))
        else:
            self.setPalette(QApplication.style().standardPalette())
            self.setStyle(QStyleFactory.create("Fusion"))

    def show_about(self):
        text = (
            "<b>Prometheus File Compressor</b><br>"
            "User-driven file size optimization for Linux desktops.<br>"
            "Built with Python 3.13, PyQt5, and the following technologies:<br><br>"
            "<ul>"
            "<li><b>Image Compression:</b> Pillow (resize, quality, DPI)</li>"
            "<li><b>PDF Compression:</b> PyMuPDF (rasterize pages to images)</li>"
            "<li><b>GUI Framework:</b> PyQt5 (cross-platform native look)</li>"
            "<li><b>File I/O:</b> Drag & drop, batch handling</li>"
            "<li><b>Theming:</b> Dark/Light switch with Fusion palette</li>"
            "</ul><br><br>"
            "<center>Crafted with ❤️ by <a href='https://yashwantsingh0.github.io'>Yashwant Singh</a></center>"
        )
        msg = QMessageBox(self)
        msg.setWindowTitle("About Prometheus")
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(text)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.exec()


