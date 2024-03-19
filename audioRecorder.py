import os
import wave
import audioop
from PyQt5.QtCore import QThread, pyqtSignal
import pyaudio
from pydub import AudioSegment
import time
import unittest


class AudioRecorder(QThread):
    """
    A class to record audio in a separate thread and emit signals
    with the recording's timecode and amplitude.
    """
    update_timecode = pyqtSignal(str)
    update_amplitude = pyqtSignal(float)

    def __init__(self):
        super().__init__()
        self.is_recording = False
        self.frames = []

    def run(self):
        """Main method to handle audio recording."""
        self.is_recording = True
        self.frames = []

        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16,
                        channels=2,
                        rate=44100,
                        input=True,
                        frames_per_buffer=1024)

        start_time = time.time()  # Start time of recording

        try:
            while self.is_recording:
                data = stream.read(1024, exception_on_overflow=False)
                self.frames.append(data)
                rms = audioop.rms(data, 2)  # Calculate RMS of the data
                self.update_amplitude.emit(rms)  # Emit the RMS value

                 # Calculate and emit the timecode
                elapsed_time = time.time() - start_time
                time_str = self.format_time(elapsed_time)
                self.update_timecode.emit(time_str)
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()

    def stop(self):
        """Stops the audio recording."""
        self.is_recording = False

    def save(self, filename):
        """
        Saves the recorded audio to a file and converts it to MP3.

        :param filename: The filename for the saved audio.
        """
        wf = wave.open(filename, 'wb')
        wf.setnchannels(2)
        wf.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
        wf.setframerate(44100)
        wf.writeframes(b''.join(self.frames))
        wf.close()

        # Convert to MP3
        try:
            sound = AudioSegment.from_wav(filename)
            sound.export(filename.replace('.wav', '.mp3'), format='mp3')
            os.remove(filename)
        except Exception as e:
            print(f"Error converting to MP3: {e}")

    @staticmethod
    def format_time(seconds):
        """
        Formats elapsed time from seconds to a string format (H:MM:SS).

        :param seconds: The number of seconds to format.
        :return: A string representation of the formatted time.
        """
        hours, remainder = divmod(int(seconds), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f'{hours:02}:{minutes:02}:{seconds:02}'

class TestAudioRecorder(unittest.TestCase):
    def test_format_time(self):
        """Test the format_time method."""
        recorder = AudioRecorder()
        self.assertEqual(recorder.format_time(3661), "01:01:01")
        self.assertEqual(recorder.format_time(60), "00:01:00")
        self.assertEqual(recorder.format_time(1), "00:00:01")


if __name__ == '__main__':
    unittest.main()
