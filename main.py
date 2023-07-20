import time
import numpy as np
import cv2
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QLabel
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QSize
from PyQt5.QtGui import QImage, QPixmap, QMouseEvent
from PyQt5 import uic, QtCore
import sys


class VideoFeed(QThread):
    # Define a signal for updating the image in the UI
    img_update = pyqtSignal(np.ndarray)
    def __init__(self):
        super().__init__()
        self.is_running = False

    # Define the run method that is called when the thread is started
    def run(self):
        # Initialize the video capture
        cap = cv2.VideoCapture(0)
        # Loop until the thread is stopped
        self.is_running = True
        while self.is_running:
            # Read a frame from the video capture
            ret, frame = cap.read()
            # If a frame is successfully read, emit the signal with the frame data
            if ret:
                self.img_update.emit(frame)
        cap.release()

    # Define a method for stopping the thread
    def stop(self):
        self.is_running = False


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("video-process.ui", self)

        # Thread

        self.tmp = None
        self.video_thread = VideoFeed()
        self.video_thread.img_update.connect(self.set_video_frame)

        # Labels

        self.video_lbl = self.findChild(QLabel, 'label')

        # Buttons

        self.play_btn = self.findChild(QPushButton, 'play_button')
        self.play_btn.clicked.connect(self.start_video)

        self.photo_btn = self.findChild(QPushButton, 'photo_button')
        self.photo_btn.clicked.connect(self.save_photo)
        self.photo_btn.setEnabled(False)

        self.stop_btn = self.findChild(QPushButton, 'stop_button')
        self.stop_btn.clicked.connect(self.stop_video)
        self.stop_btn.setEnabled(False)

    def start_video(self):

        self.video_thread.start()

        self.play_btn.setEnabled(False)
        self.photo_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)

    def stop_video(self):

        self.video_thread.stop()
        self.video_thread.quit()
        self.video_thread.wait()

        self.play_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.photo_btn.setEnabled(True)
        self.video_lbl.clear()

    def set_video_frame(self, frame):

        """
        Updates the displayed video frame with the given frame.

        :param frame: The video fram to display
        :return:
        """
        # Convert to RGB format and flip the image horizontally
        self.tmp = cv2.flip(frame, 1)
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        flipped = cv2.flip(image, 1)

        # Convert to Qt format and display in video_lbl
        qt_image = QImage(flipped.data, flipped.shape[1], flipped.shape[0], QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        self.video_lbl.setPixmap(pixmap)

    def save_photo(self):


        self.file_name = 'Snapshot ' + str(time.strftime("%Y-%b-%d at %H.%M.%S %p")) + '.png'
        cv2.imwrite(self.file_name, self.tmp)
        print('Image saved as:', self.file_name)


# Entry point of the application
if __name__ == '__main__':
    # Create a QApplication instance
    app = QApplication(sys.argv)
    # Create a MainWindow instance and show it
    window = MainWindow()
    window.show()
    # Run the application event loop
    sys.exit(app.exec_())