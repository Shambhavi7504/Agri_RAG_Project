"""
Voice Input Module
Handles speech-to-text in multiple languages
"""

import speech_recognition as sr
import tempfile
import os

class VoiceInput:
    """Handles voice input and speech recognition"""
    
    # Language codes for speech recognition
    SPEECH_LANGUAGES = {
        'en': 'en-IN',  # English (India)
        'hi': 'hi-IN',  # Hindi
        'kn': 'kn-IN',  # Kannada
        'te': 'te-IN',  # Telugu
        'ta': 'ta-IN',  # Tamil
        'bn': 'bn-IN',  # Bengali
        'mr': 'mr-IN',  # Marathi
        'pa': 'pa-IN',  # Punjabi
        'gu': 'gu-IN',  # Gujarati
        'ml': 'ml-IN',  # Malayalam
        'ur': 'ur-IN',  # Urdu
    }
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
    
    def recognize_from_microphone(self, language='en', timeout=5):
        """
        Capture audio from microphone and convert to text
        
        Args:
            language: Language code (e.g., 'hi', 'en')
            timeout: Recording timeout in seconds
            
        Returns:
            Recognized text or None
        """
        try:
            # Get language code for speech recognition
            lang_code = self.SPEECH_LANGUAGES.get(language, 'en-IN')
            
            with sr.Microphone() as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                # Listen for audio
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
            
            # Recognize speech using Google Speech Recognition
            text = self.recognizer.recognize_google(audio, language=lang_code)
            
            return text
            
        except sr.WaitTimeoutError:
            return "⚠️ No speech detected. Please try again."
        except sr.UnknownValueError:
            return "⚠️ Could not understand audio. Please speak clearly."
        except sr.RequestError as e:
            return f"⚠️ Speech recognition error: {e}"
        except Exception as e:
            return f"⚠️ Error: {e}"
    
    def recognize_from_audio_file(self, audio_file, language='en'):
        """
        Recognize speech from audio file
        
        Args:
            audio_file: Path to audio file or file-like object
            language: Language code
            
        Returns:
            Recognized text or None
        """
        try:
            lang_code = self.SPEECH_LANGUAGES.get(language, 'en-IN')
            
            # If it's bytes, save to temporary file
            if isinstance(audio_file, bytes):
                with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                    tmp_file.write(audio_file)
                    audio_file_path = tmp_file.name
            else:
                audio_file_path = audio_file
            
            # Load audio file
            with sr.AudioFile(audio_file_path) as source:
                audio = self.recognizer.record(source)
            
            # Recognize
            text = self.recognizer.recognize_google(audio, language=lang_code)
            
            # Clean up temp file
            if isinstance(audio_file, bytes):
                os.unlink(audio_file_path)
            
            return text
            
        except sr.UnknownValueError:
            return "⚠️ Could not understand audio."
        except sr.RequestError as e:
            return f"⚠️ Speech recognition error: {e}"
        except Exception as e:
            return f"⚠️ Error: {e}"
    
    def is_microphone_available(self):
        """Check if microphone is available"""
        try:
            sr.Microphone.list_microphone_names()
            return True
        except:
            return False


# Singleton instance
_voice_input_instance = None

def get_voice_input():
    """Get or create voice input instance"""
    global _voice_input_instance
    if _voice_input_instance is None:
        _voice_input_instance = VoiceInput()
    return _voice_input_instance