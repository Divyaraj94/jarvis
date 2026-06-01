import speech_recognition as sr
import pyttsx3
import time

class VoiceSystem:
    """
    The 'Ears' and 'Mouth' of JARVIS.
    Handles Speech-to-Text (STT) and Text-to-Speech (TTS).
    """
    def __init__(self, voice_id=None, rate=175, volume=1.0):
        # Initialize TTS engine
        self.engine = pyttsx3.init()

        # Configure Voice
        voices = self.engine.getProperty('voices')
        # Attempt to set a specific voice if provided, else use default
        if voice_id is not None and len(voices) > voice_id:
            self.engine.setProperty('voice', voices[voice_id].id)

        self.engine.setProperty('rate', rate)
        self.engine.setProperty('volume', volume)

        # Initialize STT recognizer
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        # Calibration: Adjust for ambient noise
        with self.microphone as source:
            print("[System] Calibrating microphone for ambient noise...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print("[System] Calibration complete.")

    def speak(self, text):
        """Converts text to speech and speaks it aloud."""
        if not text:
            return

        # Clean text for TTS (remove tags like <SAVE_FACT> if they leak into the response)
        import re
        clean_text = re.sub(r'<.*?>', '', text)

        print(f"[Jarvis Voice] {clean_text}")
        self.engine.say(clean_text)
        self.engine.runAndWait()

    def listen(self):
        """
        Captures audio from the microphone and converts it to text.
        Returns the recognized text or an empty string if nothing was heard.
        """
        with self.microphone as source:
            print("\n[Listening...]")
            try:
                # Timeout: stop listening after 5 seconds of silence
                # Phrase time limit: stop listening after 10 seconds of speaking
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            except sr.WaitTimeoutError:
                return ""
            except Exception as e:
                print(f"[System] Listening error: {e}")
                return ""

        try:
            print("[Processing speech...]")
            # Using Google Speech Recognition for MVP (can be swapped for Whisper local)
            text = self.recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            # Occurs when the audio is just noise or unrecognizable
            return ""
        except sr.RequestError as e:
            print(f"[System] Speech service error: {e}")
            return ""

# Global instance for easy integration
voice = VoiceSystem()
