"""
Speech recognition module for voice command application.
"""
import speech_recognition as sr
import time

class SpeechRecognizer:
    """Class to handle speech recognition functionality."""
    
    def __init__(
        self,
        energy_threshold=300,
        dynamic_energy_threshold=True,
        dynamic_energy_adjustment_damping=0.15,
        dynamic_energy_ratio=1.5,
        pause_threshold=0.2,
        phrase_threshold=0.2,
        non_speaking_duration=0.2,
        operation_timeout=None
    ):
        """Initialize the speech recognizer with configurable parameters.
        
        Args:
            energy_threshold: Energy level for the microphone to detect (higher = less sensitive)
            dynamic_energy_threshold: Whether to dynamically adjust the energy threshold
            dynamic_energy_adjustment_damping: Damping factor for dynamic energy adjustment
            dynamic_energy_ratio: Ratio for dynamic energy adjustment
            pause_threshold: Seconds of non-speaking audio before a phrase is considered complete
            phrase_threshold: Minimum seconds of speaking audio before we consider the audio a phrase
            non_speaking_duration: Seconds of non-speaking audio to keep before and after recording
            operation_timeout: Seconds after an internal operation (e.g., API request) times out
        """
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = energy_threshold
        self.recognizer.dynamic_energy_threshold = dynamic_energy_threshold
        self.recognizer.dynamic_energy_adjustment_damping = dynamic_energy_adjustment_damping
        self.recognizer.dynamic_energy_ratio = dynamic_energy_ratio
        self.recognizer.pause_threshold = pause_threshold
        self.recognizer.operation_timeout = operation_timeout
        self.recognizer.phrase_threshold = phrase_threshold
        self.recognizer.non_speaking_duration = non_speaking_duration
        self.microphone = None
        
    def calibrate(self, duration=2):
        """Calibrate the recognizer for ambient noise."""
        try:
            with sr.Microphone() as source:
                self.microphone = source
                print("Calibrating for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=duration)
                print("Calibration complete")
                return True
        except Exception as e:
            print(f"Error during calibration: {e}")
            return False
            
    def listen(self, timeout=5):
        """Listen for audio and return it.
        
        Args:
            timeout: Maximum number of seconds to wait for audio
            
        Returns:
            Audio data or None if an error occurred
        """
        if not self.microphone:
            try:
                self.microphone = sr.Microphone()
            except Exception as e:
                print(f"Error initializing microphone: {e}")
                return None
                
        try:
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=timeout)
                return audio
        except Exception as e:
            print(f"Error listening: {e}")
            return None
    
    def recognize_google(self, audio):
        """Recognize speech using Google Speech Recognition.
        
        Args:
            audio: Audio data to recognize
            
        Returns:
            Recognized text or None if an error occurred
        """
        if not audio:
            return None
            
        try:
            text = self.recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            # Could not understand audio
            return None
        except sr.RequestError as e:
            print(f"Google Speech Recognition service error: {e}")
            return None
        except Exception as e:
            print(f"Error recognizing speech: {e}")
            return None
            
    def listen_and_recognize(self, timeout=5):
        """Listen for audio and recognize it in one step.
        
        Args:
            timeout: Maximum number of seconds to wait for audio
            
        Returns:
            Recognized text or None if an error occurred
        """
        audio = self.listen(timeout)
        if audio:
            return self.recognize_google(audio)
        return None 