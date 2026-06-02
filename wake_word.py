import numpy as np
import collections

class WakeWordSystem:
    """
    The 'Intuition' of JARVIS.
    Listens for a specific keyword to activate the assistant.
    Uses sounddevice instead of PyAudio (no Python 3.14 wheels for PyAudio).
    """
    def __init__(self, wake_word="hey_jarvis_v0.1"):
        import sounddevice as sd
        from openwakeword.model import Model

        print("[System] Loading Wake Word engine...")

        # Load the model with ONNX inference framework
        self.oww_model = Model(
            wakeword_models=[wake_word],
            inference_framework="onnx"
        )
        self.wake_word = wake_word

        # Audio stream setup using sounddevice
        self.sd = sd
        self.sample_rate = 16000
        self.chunk_size = 1280  # openwakeword expects 1280 samples (80ms at 16kHz)

        # Start an input stream
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype='int16',
            blocksize=self.chunk_size
        )
        self.stream.start()

        print(f"[System] Wake Word system active. Listening for '{wake_word}'...")

    def listen(self):
        """
        Reads one chunk of audio and checks for wake word.
        Returns True if wake word is detected.
        """
        try:
            # Read audio from the sounddevice stream
            data, overflowed = self.stream.read(self.chunk_size)

            # Convert to the format openwakeword expects (flat int16 numpy array)
            audio_data = data.flatten()

            # Run prediction
            prediction = self.oww_model.predict(audio_data)

            # Check all model predictions
            for model_name, score in prediction.items():
                if score > 0.5:
                    # Reset the model after detection to avoid repeated triggers
                    self.oww_model.reset()
                    return True

        except Exception as e:
            # Silently handle audio read errors to keep the loop alive
            pass

        return False

    def pause(self):
        """Pause the audio stream."""
        try:
            if self.stream.active:
                self.stream.stop()
        except Exception:
            pass

    def resume(self):
        """Resume the audio stream."""
        try:
            if not self.stream.active:
                self.oww_model.reset()
                self.stream.start()
        except Exception:
            pass

    def stop(self):
        """Clean up audio streams."""
        try:
            self.stream.stop()
            self.stream.close()
        except Exception:
            pass


# NOTE: No global instance here. Instantiated in main.py with error handling.
