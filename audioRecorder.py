import os
from PyQt5.QtCore import QThread, pyqtSignal
import pyaudio
import wave
import audioop
from pydub import AudioSegment
import time


class AudioRecorder(QThread):
    update_timecode = pyqtSignal(str)
    update_amplitude = pyqtSignal(float)  # New signal for amplitude

    def __init__(self):
        super().__init__()
        self.is_recording = False
        self.frames = []

    def run(self):
        self.is_recording = True
        self.frames = []

        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16,
                        channels=2,
                        rate=44100,
                        input=True,
                        frames_per_buffer=1024)

        start_time = time.time()  # Start time of recording

        while self.is_recording:
            data = stream.read(1024, exception_on_overflow=False)
            self.frames.append(data)
            rms = audioop.rms(data, 2)  # Calculate RMS of the data
            self.update_amplitude.emit(rms)  # Emit the RMS value

            # Calculate and emit the timecode
            elapsed_time = time.time() - start_time  # Elapsed time in seconds
            time_str = self.format_time(elapsed_time)
            self.update_timecode.emit(time_str)

        stream.stop_stream()
        stream.close()
        p.terminate()

    def stop(self):
        self.is_recording = False

    def save(self, filename):
        wf = wave.open(filename, 'wb')
        wf.setnchannels(2)
        wf.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
        wf.setframerate(44100)
        wf.writeframes(b''.join(self.frames))
        wf.close()

        # Convert to MP3
        sound = AudioSegment.from_wav(filename)
        sound.export(filename.replace('.wav', '.mp3'), format='mp3')
        os.remove(filename)  # Remove the temporary WAV file

    def format_time(self, seconds):
        """Formats elapsed time from seconds to a string format (H:MM:SS)."""
        hours, remainder = divmod(int(seconds), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f'{hours:02}:{minutes:02}:{seconds:02}'