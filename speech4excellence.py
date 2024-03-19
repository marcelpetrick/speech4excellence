import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLineEdit, QLabel, QTextEdit, QFrame
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from audioRecorder import AudioRecorder
from audioTranscriber import AudioTranscriber
from excelWriter import ExcelWriter


class MainWindow(QWidget):
    def __init__(self, transcriber):
        super().__init__()
        self.transcriber = transcriber  # The AudioTranscriber instance
        self.recorder = AudioRecorder()
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()

        self.timecodeLabel = QLabel('00:00:00')
        self.layout.addWidget(self.timecodeLabel)

        self.amplitudeLabel = QLabel('Amplitude: 0')
        self.layout.addWidget(self.amplitudeLabel)

        self.filenameLineEdit = QLineEdit('recording.mp3')
        self.layout.addWidget(self.filenameLineEdit)

        self.recordButton = QPushButton('Record')
        self.recordButton.clicked.connect(self.toggleRecording)
        self.layout.addWidget(self.recordButton)

        self.divider0 = QFrame()
        self.divider0.setFrameShape(QFrame.HLine)
        self.divider0.setFrameShadow(QFrame.Sunken)
        self.layout.addWidget(self.divider0)
        self.divider0.setObjectName("line")

        self.transcribeButton = QPushButton('Transcribe')
        self.transcribeButton.clicked.connect(self.transcribeAudio)
        self.layout.addWidget(self.transcribeButton)

        self.transcriptionPreview = QTextEdit()
        self.transcriptionPreview.setReadOnly(False)
        self.layout.addWidget(self.transcriptionPreview)

        self.divider1 = QFrame()
        self.divider1.setFrameShape(QFrame.HLine)
        self.divider1.setFrameShadow(QFrame.Sunken)
        self.layout.addWidget(self.divider1)
        self.divider1.setObjectName("line")

        self.excelFilenameLineEdit = QLineEdit('transcription.xlsx')
        self.layout.addWidget(self.excelFilenameLineEdit)

        self.writeExcelButton = QPushButton('Write to Excel')
        self.writeExcelButton.clicked.connect(self.writeToExcel)
        self.layout.addWidget(self.writeExcelButton)

        self.recorder.update_amplitude.connect(self.updateAmplitude)
        self.recorder.update_timecode.connect(self.updateTimecode)

        self.setLayout(self.layout)
        self.setWindowTitle('speech4excellence')

        # Set the window to be half-transparent
        self.setWindowOpacity(0.8)

        # Apply a violet color palette tint to the window
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(148, 0, 211, 0.4); /* Violet background with slight transparency */
                color: #FFFFFF; /* White text color */
            }
            QPushButton {
                background-color: rgba(138, 43, 226, 0.6); /* Button background color */
                color: #FFFFFF; /* White text color */
                border-style: outset;
                border-width: 2px;
                border-radius: 10px;
                border-color: rgba(255, 255, 255, 0.8); /* Slightly transparent white border */
                padding: 4px;
            }
            QPushButton:hover {
                background-color: rgba(138, 43, 226, 0.8); /* Darker on hover */
            }
            QPushButton:pressed {
                background-color: rgba(138, 43, 226, 1.0); /* Even darker when pressed */
            }
            QLineEdit, QTextEdit {
                border-radius: 5px;
                background-color: gray;
            }
            QFrame#line {
                background-color: cyan; /* Cyan color for the divider */
            }
        """)

        self.setAttribute(Qt.WA_TranslucentBackground)  # Enable background transparency
        #self.setWindowFlag(Qt.FramelessWindowHint)  # Remove title bar

        # Set the window icon
        self.setWindowIcon(QIcon('icon.png'))

        self.show()

    def writeToExcel(self):
        """Writes the content of the transcription preview to the specified Excel file."""
        excel_filename = self.excelFilenameLineEdit.text()
        transcription_text = self.transcriptionPreview.toPlainText()
        if not excel_filename.endswith('.xlsx'):
            excel_filename += '.xlsx'  # Ensure the filename has the correct extension

        # Assume the ExcelWriter class has an `insert_text` method
        try:
            excel_writer = ExcelWriter(excel_filename)
            print(f"Writing transcription to {excel_filename}")
            print(f"transcription_text: {transcription_text}")
            excel_writer.insert_text(transcription_text)
            print(f"Transcription written to {excel_filename}")
        except Exception as e:
            print(f"Error writing to Excel: {e}")

    def updateAmplitude(self, rms):
        self.amplitudeLabel.setText(f'Amplitude: {rms}')

    def toggleRecording(self):
        if self.recorder.is_recording:
            self.recorder.stop()
            self.recorder.wait()  # Wait for the recording thread to finish
            filename = self.filenameLineEdit.text()
            if not filename.endswith('.mp3'):
                filename += '.mp3'
            self.recorder.save('temp.wav')
            if os.path.exists(filename):
                os.remove(filename)
            os.rename('temp.mp3', filename)
            self.recordButton.setText('Record')
        else:
            self.recorder.start()
            self.recordButton.setText('Stop')

    def updateTimecode(self, timecode):
        self.timecodeLabel.setText(timecode)

    def transcribeAudio(self):
        """Transcribe the recorded audio and display the text."""
        filename = self.filenameLineEdit.text()
        if not os.path.exists(filename):
            self.transcriptionPreview.setText("File not found. Please record something first.")
            return
        try:
            transcription = self.transcriber.transcribe(filename)
            self.transcriptionPreview.setText(transcription)
        except Exception as e:
            self.transcriptionPreview.setText(f"Error during transcription: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key is None:
        raise EnvironmentError("OPENAI_API_KEY environment variable not set.")
    transcriber = AudioTranscriber(api_key)
    ex = MainWindow(transcriber)
    sys.exit(app.exec_())
