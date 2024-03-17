import os
import unittest
from openai import OpenAI

class AudioTranscriber:
    """
    A class for transcribing audio files to text using OpenAI's audio API.

    Attributes:
        client (OpenAI): The OpenAI client configured with an API key.
    """

    def __init__(self, api_key):
        """
        Initializes the AudioTranscriber with the provided OpenAI API key.

        Parameters:
            api_key (str): The OpenAI API key.

        Raises:
            ValueError: If no API key is provided.
        """
        if not api_key:
            raise ValueError("API key must be provided")
        self.client = OpenAI(api_key=api_key)

    def transcribe(self, filename):
        """
        Transcribes the given audio file to text using the OpenAI audio API.

        Parameters:
            filename (str): The path to the audio file to be transcribed.

        Returns:
            str: The transcribed text.

        Raises:
            FileNotFoundError: If the specified file does not exist.
            Exception: For any other issues during the transcription process.
        """
        try:
            with open(filename, "rb") as audio_file:
                transcription = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
                return transcription.text
        except FileNotFoundError:
            raise FileNotFoundError(f"The file {filename} was not found.")
        except Exception as e:
            raise Exception(f"An error occurred during transcription: {e}")

# Unit tests for the AudioTranscriber class
class TestAudioTranscriber(unittest.TestCase):

    def test_api_key_missing(self):
        """Test initializing AudioTranscriber without an API key raises ValueError."""
        with self.assertRaises(ValueError):
            AudioTranscriber(api_key=None)

    # Additional tests can be added here to mock OpenAI's response and test the transcribe method.

if __name__ == "__main__":
    # Perform environment check for OPENAI_API_KEY
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY environment variable not set.")

    # Example usage with safety check for demonstration
    transcriber = AudioTranscriber(api_key)
    try:
        transcription = transcriber.transcribe('recording.mp3')
        print(f"Transcription: {transcription}")
    except Exception as e:
        print(f"Error: {e}")

    # Run unit tests
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
