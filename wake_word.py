import openwakeword
from openwakeword.model import Model
import pyaudio
import numpy as np
import collections

class WakeWordSystem:
    """
    The 'Intuition' of JARVIS.
    Listens for a specific keyword to activate the assistant.
    """
    def __init__(self, wake_word="alexa"):
        # Note: openWakeWord comes with a few default models like 'alexa', 'hey google', etc.
        # For a custom 'Jarvis' word, we'd typically load a custom .tflite or .onnx model.
        # For this MVP, we will use 'alexa' as a proxy for 'Jarvis' until a custom model is loaded,
        # or we can implement a fallback using simple speech recognition.

        print("[System] Loading Wake Word engine...")
        self.oww_model = Model(wakeword_models=None, inference_framework="onnx")

        # Use the default models provided by the library
        self.model = self.oww_model.get_model(wake_word)

        # Audio stream setup
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=128
        )

        self.buffer = collections.deque(maxlen=128)
        print(f"[System] Wake Word system active. Listening for '{wake_word}'...")

    def listen(self):
        """
        Continuously monitors audio. Returns True if wake word is detected.
        """
        # Read audio from stream
        data = self.stream.read(128, exception_on_overflow=False)
        # Convert to numpy array
        audio_data = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0

        # Add to buffer
        self.buffer.extend(audio_data)

        # If buffer is full, run inference
        if len(self.buffer) == 128:
            input_data = np.array(self.buffer)
            # Run the model
            prediction = self.model.predict(input_data)

            # If prediction probability is high enough (usually > 0.5)
            if prediction > 0.5:
                return True

        return False

    def stop(self):
        """Clean up audio streams."""
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()

# Default instance
wake_word_system = WakeWordSystem()
