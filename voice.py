import speech_recognition as sr
import pyttsx3
import re

class VoiceSystem:
    """
    The 'Ears' and 'Mouth' of JARVIS.
    Handles Speech-to-Text (STT) via sounddevice + SpeechRecognition,
    and Text-to-Speech (TTS) via pyttsx3.
    """
    def __init__(self, voice_id=None, rate=175, volume=1.0):
        # Initialize TTS engine
        self.engine = pyttsx3.init()
        self.voice_id = voice_id
        self.rate = rate
        self.volume = volume

        voices = self.engine.getProperty('voices')
        if voice_id is not None and len(voices) > voice_id:
            self.engine.setProperty('voice', voices[voice_id].id)
        self.engine.setProperty('rate', rate)
        self.engine.setProperty('volume', volume)

        # Initialize STT recognizer
        self.recognizer = sr.Recognizer()

        # Import sounddevice (replaces PyAudio which has no Python 3.14 wheels)
        import sounddevice as sd
        self.sd = sd

        # Audio settings
        self.sample_rate = 16000
        self.channels = 1

        # Quick test to make sure audio device is available
        devices = sd.query_devices()
        input_device = sd.query_devices(kind='input')
        print(f"[System] Microphone detected: {input_device['name']}")
        print("[System] Voice system initialized successfully.")

    def speak(self, text):
        """Converts text to speech and speaks it aloud."""
        if not text:
            return

        # Clean text for TTS (remove tags like <SAVE_FACT> if they leak into the response)
        clean_text = re.sub(r'<.*?>', '', text)

        if not clean_text.strip():
            return

        try:
            self.engine.say(clean_text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"[System] TTS playing error: {e}")
            # Attempt reinitialization
            try:
                self.engine.stop()
            except Exception:
                pass
            try:
                self.engine = pyttsx3.init()
                voices = self.engine.getProperty('voices')
                if self.voice_id is not None and len(voices) > self.voice_id:
                    self.engine.setProperty('voice', voices[self.voice_id].id)
                self.engine.setProperty('rate', self.rate)
                self.engine.setProperty('volume', self.volume)
            except Exception:
                pass

    def listen(self, timeout=5, phrase_time_limit=8):
        """
        Captures audio from the microphone using sounddevice with silence detection.
        Returns the recognized text or an empty string if nothing was heard.
        """
        import numpy as np
        import io
        import wave

        print("\n[Listening... speak now!]")
        
        sample_rate = self.sample_rate
        chunk_size = 1024
        
        audio_frames = []
        
        # Silence detection parameters
        threshold = 500  # Amplitude threshold for speech
        silence_duration_limit = 1.5  # Seconds of silence to trigger stop
        max_duration = phrase_time_limit
        
        speech_detected = False
        silence_chunks_limit = int((silence_duration_limit * sample_rate) / chunk_size)
        max_chunks = int((max_duration * sample_rate) / chunk_size)
        
        silence_counter = 0
        chunks_recorded = 0
        
        try:
            # We open an input stream for recording
            with self.sd.InputStream(samplerate=sample_rate, channels=self.channels, dtype='int16', blocksize=chunk_size) as stream:
                while chunks_recorded < max_chunks:
                    data, overflowed = stream.read(chunk_size)
                    audio_frames.append(data.copy())
                    chunks_recorded += 1
                    
                    # Check amplitude
                    max_amplitude = np.max(np.abs(data))
                    if max_amplitude > threshold:
                        if not speech_detected:
                            # Speech just started
                            speech_detected = True
                        silence_counter = 0
                    else:
                        if speech_detected:
                            silence_counter += 1
                            if silence_counter >= silence_chunks_limit:
                                # Detected silence after speech, stop early
                                break
                        else:
                            # If no speech detected yet, check if we exceeded timeout
                            timeout_chunks = int((timeout * sample_rate) / chunk_size)
                            if chunks_recorded > timeout_chunks:
                                # Timeout exceeded with no speech
                                break
        except Exception as e:
            print(f"[System] Recording error: {e}")
            return ""

        if not audio_frames:
            return ""

        try:
            print("[Processing speech...]")
            # Combine all frames
            recording = np.concatenate(audio_frames, axis=0)

            # Convert numpy array to WAV bytes for SpeechRecognition
            buffer = io.BytesIO()
            with wave.open(buffer, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)  # 16-bit = 2 bytes
                wf.setframerate(self.sample_rate)
                wf.writeframes(recording.tobytes())
            buffer.seek(0)

            # Use SpeechRecognition to process the WAV data
            with sr.AudioFile(buffer) as source:
                audio = self.recognizer.record(source)

            # Using Google Speech Recognition
            text = self.recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text

        except sr.UnknownValueError:
            # Occurs when the audio is just noise or unrecognizable
            print("[System] Couldn't understand. Try again.")
            return ""
        except sr.RequestError as e:
            print(f"[System] Speech service error: {e}")
            return ""
        except Exception as e:
            print(f"[System] Speech processing error: {e}")
            return ""
