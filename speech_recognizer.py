"""
Speech recognition module for voice command application.
"""
import speech_recognition as sr
import time
import threading
import queue

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
        self.stop_continuous = False
        self.audio_queue = queue.Queue()
        self.listening_thread = None
        self.processor_thread = None
        
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

    def _continuous_listening_thread(self):
        """Thread function that continuously listens for audio and adds to queue."""
        print("Continuous listening thread started")
        
        # Create a dedicated microphone for this thread
        mic = sr.Microphone()
        
        try:
            with mic as source:
                # Initial ambient noise adjustment
                print("Adjusting for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                print("Continuous listening active")
                while not self.stop_continuous:
                    try:
                        print("Listening for speech...")
                        audio = self.recognizer.listen(source, phrase_time_limit=5)
                        print("Speech detected, sending to queue")
                        self.audio_queue.put(audio)
                    except Exception as e:
                        print(f"Error in continuous listening: {e}")
                        time.sleep(0.1)  # Prevent tight loops if errors occur
                        if self.stop_continuous:  # Check again in case the error was due to stopping
                            break
        except Exception as e:
            print(f"Critical error in listening thread: {e}")
        finally:
            print("Continuous listening thread stopped")
        
    def _audio_processor_thread(self):
        """Process audio chunks from the queue and recognize speech."""
        print("Audio processor thread started")
        
        while not self.stop_continuous:
            try:
                # Get the audio data from the queue with a timeout
                audio = self.audio_queue.get(timeout=2)
                
                try:
                    # Recognize the speech
                    text = self.recognize_google(audio)
                    
                    # If we have text and a callback, send it to the callback
                    if text and self.text_callback:
                        self.text_callback(text)
                except Exception as e:
                    print(f"Error processing audio chunk: {e}")
                finally:
                    # Always mark the task as done to prevent queue from filling up
                    self.audio_queue.task_done()
                    
            except queue.Empty:
                # Queue timeout, just continue
                continue
            except Exception as e:
                print(f"Error in audio processor thread: {e}")
                time.sleep(0.1)  # Prevent tight loops if errors occur consistently
                
        print("Audio processor thread stopped")
    
    def start_continuous_recognition(self, text_callback):
        """Start continuous speech recognition with a callback for text chunks.
        
        Args:
            text_callback: Function to call with recognized text chunks
        """
        self.stop_continuous = False
        self.text_callback = text_callback
        
        # Start the audio processor thread
        self.processor_thread = threading.Thread(target=self._audio_processor_thread)
        self.processor_thread.daemon = True
        self.processor_thread.start()
        
        # Start the continuous listening thread
        self.listening_thread = threading.Thread(target=self._continuous_listening_thread)
        self.listening_thread.daemon = True
        self.listening_thread.start()
        
        return True
    
    def stop_continuous_recognition(self):
        """Stop the continuous speech recognition."""
        print("Stopping continuous speech recognition...")
        
        # Set the stop flag first
        self.stop_continuous = True
        
        # Clear the audio queue to prevent processor thread from blocking
        try:
            while not self.audio_queue.empty():
                self.audio_queue.get_nowait()
                self.audio_queue.task_done()
        except Exception:
            pass
            
        # Wait for the threads to finish
        if hasattr(self, 'processor_thread') and self.processor_thread and self.processor_thread.is_alive():
            try:
                self.processor_thread.join(timeout=2)
            except Exception as e:
                print(f"Error joining processor thread: {e}")
                
        if hasattr(self, 'listening_thread') and self.listening_thread and self.listening_thread.is_alive():
            try:
                self.listening_thread.join(timeout=2)
            except Exception as e:
                print(f"Error joining listening thread: {e}")
                
        print("Continuous speech recognition stopped")
        return True 