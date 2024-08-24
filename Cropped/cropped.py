import cv2
import os
import glob
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, \
    QLabel, QFileDialog, QGraphicsView, QGraphicsScene, QMenuBar, QAction, QMessageBox
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt


class ImageCropper(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Cropper")
        self.setGeometry(100, 100, 1200, 600)

        self.current_image = None
        self.cropped_images = {}  # Dictionary to store cropped images for each index
        self.log_entries = {}  # Dictionary to store log entries for each image index
        self.image_files = []
        self.current_index = 0

        self.initUI()
        self.create_menu()


    def initUI(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Image display areas
        self.image_layout = QHBoxLayout()
        self.layout.addLayout(self.image_layout)

        # Original image view
        self.original_view = QGraphicsView()
        self.original_scene = QGraphicsScene()
        self.original_view.setScene(self.original_scene)
        self.image_layout.addWidget(self.original_view)

        # Cropped image view
        self.cropped_view = QGraphicsView()
        self.cropped_scene = QGraphicsScene()
        self.cropped_view.setScene(self.cropped_scene)
        self.image_layout.addWidget(self.cropped_view)

        # Input fields for cropping
        self.input_layout = QHBoxLayout()
        self.layout.addLayout(self.input_layout)

        self.start_x_input = QLineEdit(self)
        self.start_x_input.setPlaceholderText("Start X")
        self.input_layout.addWidget(self.start_x_input)

        self.start_y_input = QLineEdit(self)
        self.start_y_input.setPlaceholderText("Start Y")
        self.input_layout.addWidget(self.start_y_input)

        self.end_x_input = QLineEdit(self)
        self.end_x_input.setPlaceholderText("End X")
        self.input_layout.addWidget(self.end_x_input)

        self.end_y_input = QLineEdit(self)
        self.end_y_input.setPlaceholderText("End Y")
        self.input_layout.addWidget(self.end_y_input)

        self.distance_x_input = QLineEdit(self)
        self.distance_x_input.setPlaceholderText("Distance X")
        self.input_layout.addWidget(self.distance_x_input)

        self.distance_y_input = QLineEdit(self)
        self.distance_y_input.setPlaceholderText("Distance Y")
        self.input_layout.addWidget(self.distance_y_input)

        # Control buttons
        self.button_layout = QHBoxLayout()
        self.layout.addLayout(self.button_layout)

        self.load_button = QPushButton("Load Images")
        self.load_button.clicked.connect(self.load_images)
        self.button_layout.addWidget(self.load_button)

        self.prev_button = QPushButton("Previous")
        self.prev_button.clicked.connect(self.prev_image)
        self.button_layout.addWidget(self.prev_button)

        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.next_image)
        self.button_layout.addWidget(self.next_button)

        self.crop_button = QPushButton("Crop and Save All")
        self.crop_button.clicked.connect(self.crop_and_save_all)
        self.button_layout.addWidget(self.crop_button)

        # Log area for status messages
        self.log_label = QLabel("")
        self.layout.addWidget(self.log_label)

    def create_menu(self):
        menubar = self.menuBar()
        about_menu = menubar.addMenu("Info")

        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        about_menu.addAction(about_action)

    def show_about(self):
        about_message = (
            "Person doing the project: Alperen Bahar\n"
            "Communication: alpb721@gmail.com"
        )

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Info")
        msg_box.setText(about_message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.setIcon(QMessageBox.Information)

        # Mesaj kutusunun estetik görünümü için aşağıdaki satırları ekleyebilirsiniz
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #f0f0f0;
                font-size: 14px;
            }
            QPushButton {
                min-width: 80px;
                font-size: 12px;
            }
        """)

        msg_box.exec_()

    def load_images(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Image Folder")
        if folder_path:
            self.image_files = glob.glob(os.path.join(folder_path, '*.*'))
            self.current_index = 0
            self.show_image()

    def show_image(self):
        if self.image_files and 0 <= self.current_index < len(self.image_files):
            image_file = self.image_files[self.current_index]
            self.current_image = cv2.imread(image_file)
            if self.current_image is not None:
                # Display original image
                resized_image = self.resize_image(self.current_image, 800, 600)
                self.display_image(resized_image, self.original_scene)

                # Display cropped image if available
                if self.current_index in self.cropped_images:
                    resized_cropped_image = self.resize_image(self.cropped_images[self.current_index], 600, 400)
                    self.display_image(resized_cropped_image, self.cropped_scene)
                else:
                    self.cropped_scene.clear()

                # Update log
                log_entry = self.log_entries.get(self.current_index, f"Current image: {os.path.basename(image_file)}")
                self.log_label.setText(log_entry)

    def resize_image(self, image, max_width, max_height):
        height, width = image.shape[:2]
        scaling_factor = min(max_width / width, max_height / height)
        new_size = (int(width * scaling_factor), int(height * scaling_factor))
        return cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)

    def display_image(self, image, scene):
        height, width = image.shape[:2]
        qimg = QImage(image.data, width, height, 3 * width, QImage.Format_BGR888)
        pixmap = QPixmap.fromImage(qimg)
        scene.clear()
        scene.addPixmap(pixmap)

    def prev_image(self):
        if self.image_files:
            self.current_index = (self.current_index - 1) % len(self.image_files)
            self.show_image()

    def next_image(self):
        if self.image_files:
            self.current_index = (self.current_index + 1) % len(self.image_files)
            self.show_image()

    def crop_and_save_all(self):
        if not self.image_files:
            self.log_label.setText("No images loaded.")
            return

        start_x = self.get_input_value(self.start_x_input)
        start_y = self.get_input_value(self.start_y_input)
        end_x = self.get_input_value(self.end_x_input)
        end_y = self.get_input_value(self.end_y_input)
        distance_x = self.get_input_value(self.distance_x_input)
        distance_y = self.get_input_value(self.distance_y_input)

        save_folder = QFileDialog.getExistingDirectory(self, "Select Save Folder")
        if not save_folder:
            self.log_label.setText("Save folder not selected.")
            return

        for index, image_file in enumerate(self.image_files):
            try:
                image = cv2.imread(image_file)
                cropped_image = crop_image(image, start_x, start_y, end_x, end_y, distance_x, distance_y)
                if cropped_image.size > 0:
                    file_name = os.path.basename(image_file)
                    save_path = os.path.join(save_folder, f"cropped_{file_name}")
                    cv2.imwrite(save_path, cropped_image)

                    # Update log entries
                    log_entry = f"Cropped photo saved: {save_path} (Original: {image_file})"
                    self.log_entries[index] = log_entry

                    # Store cropped image
                    self.cropped_images[index] = cropped_image

                    # If it's the current image, display the cropped image
                    if index == self.current_index:
                        resized_cropped_image = self.resize_image(cropped_image, 800, 600)
                        self.display_image(resized_cropped_image, self.cropped_scene)
                else:
                    self.log_label.setText(f"No cropped image for {image_file}.")
            except Exception as e:
                self.log_label.setText(f"Error cropping image {image_file}: {e}")

        self.log_label.setText("All images processed.")

    def get_input_value(self, input_widget):
        try:
            return int(input_widget.text()) if input_widget.text() else None
        except ValueError:
            return None



def crop_image(image, start_x=None, start_y=None, end_x=None, end_y=None, distance_x=None, distance_y=None):
    img_height, img_width = image.shape[:2]

    if start_x is not None and start_y is not None and end_x is not None and end_y is not None:
        crop_field = (start_x, start_y, end_x, end_y)

    elif distance_x is not None and distance_y is not None:
        if start_x is None:
            start_x = 0
        if start_y is None:
            start_y = 0

        end_x = start_x + distance_x
        end_y = start_y + distance_y

        crop_field = (start_x, start_y, min(end_x, img_width), min(end_y, img_height))

    else:
        raise ValueError("Invalid coordinates or distances provided")

    x1, y1, x2, y2 = crop_field
    if x1 >= x2 or y1 >= y2:
        raise ValueError("Crop area Invalid")

    cropped_image = image[y1:y2, x1:x2]

    return cropped_image


if __name__ == "__main__":
    app = QApplication([])
    window = ImageCropper()
    window.show()
    app.exec_()