"""
Multilingual Support Module
Handles translation between English and Indian languages
"""

from googletrans import Translator
import os
from gtts import gTTS
import base64

class MultilingualSupport:
    """Handles translation and voice support for multiple Indian languages"""
    
    # Supported languages
    LANGUAGES = {
        'en': 'English',
        'hi': 'हिंदी (Hindi)',
        'kn': 'ಕನ್ನಡ (Kannada)',
        'te': 'తెలుగు (Telugu)',
        'ta': 'தமிழ் (Tamil)',
        'bn': 'বাংলা (Bengali)',
        'mr': 'मराठी (Marathi)',
        'pa': 'ਪੰਜਾਬੀ (Punjabi)',
        'gu': 'ગુજરાતી (Gujarati)',
        'ml': 'മലയാളം (Malayalam)',
        'or': 'ଓଡ଼ିଆ (Odia)',
        'ur': 'اردو (Urdu)'
    }
    
    def __init__(self):
        self.translator = Translator()
    
    def translate_text(self, text, source_lang='en', target_lang='hi'):
        """
        Translate text from source language to target language
        
        Args:
            text: Text to translate
            source_lang: Source language code (default: 'en')
            target_lang: Target language code (default: 'hi')
            
        Returns:
            Translated text
        """
        try:
            if source_lang == target_lang:
                return text
            
            translation = self.translator.translate(
                text, 
                src=source_lang, 
                dest=target_lang
            )
            return translation.text
            
        except Exception as e:
            print(f"Translation error: {e}")
            return text
    
    def detect_language(self, text):
        """
        Detect the language of given text
        
        Args:
            text: Text to detect language for
            
        Returns:
            Language code (e.g., 'hi', 'en', 'kn')
        """
        try:
            detection = self.translator.detect(text)
            return detection.lang
        except Exception as e:
            print(f"Language detection error: {e}")
            return 'en'
    
    def text_to_speech(self, text, lang='en', slow=False):
        """
        Convert text to speech audio
        
        Args:
            text: Text to convert to speech
            lang: Language code
            slow: If True, speaks slowly (helpful for low literacy)
            
        Returns:
            Path to generated audio file
        """
        try:
            # Create temp directory if it doesn't exist
            os.makedirs('temp_audio', exist_ok=True)
            
            # Generate speech
            tts = gTTS(text=text, lang=lang, slow=slow)
            
            # Save to file
            audio_file = f'temp_audio/speech_{lang}.mp3'
            tts.save(audio_file)
            
            return audio_file
            
        except Exception as e:
            print(f"Text-to-speech error: {e}")
            return None
    
    def get_audio_base64(self, audio_file):
        """
        Convert audio file to base64 for embedding in HTML
        
        Args:
            audio_file: Path to audio file
            
        Returns:
            Base64 encoded audio string
        """
        try:
            with open(audio_file, 'rb') as f:
                audio_bytes = f.read()
            audio_base64 = base64.b64encode(audio_bytes).decode()
            return audio_base64
        except Exception as e:
            print(f"Audio encoding error: {e}")
            return None
    
    def translate_query_and_response(self, user_query, bot_response, user_lang='hi'):
        """
        Handle complete translation workflow:
        1. Translate user query from regional language to English
        2. Process with RAG (in English)
        3. Translate response back to regional language
        
        Args:
            user_query: User's query in regional language
            bot_response: Bot's response in English
            user_lang: User's language code
            
        Returns:
            dict with English query and translated response
        """
        # Translate query to English for processing
        english_query = self.translate_text(user_query, source_lang=user_lang, target_lang='en')
        
        # Translate response back to user's language
        translated_response = self.translate_text(bot_response, source_lang='en', target_lang=user_lang)
        
        return {
            'english_query': english_query,
            'translated_response': translated_response
        }
    
    def get_simple_prompts(self, lang='hi'):
        """
        Get UI prompts in specified language for low literacy users
        
        Args:
            lang: Language code
            
        Returns:
            Dictionary of common UI prompts
        """
        prompts = {
            'en': {
                'ask_question': 'Ask your question',
                'speak_button': '🎤 Speak',
                'send_button': 'Send',
                'listen_button': '🔊 Listen',
                'clear_button': 'Clear',
                'examples_title': 'Example Questions',
                'thinking': 'Thinking...',
                'loading': 'Loading...'
            },
            'hi': {
                'ask_question': 'अपना सवाल पूछें',
                'speak_button': '🎤 बोलें',
                'send_button': 'भेजें',
                'listen_button': '🔊 सुनें',
                'clear_button': 'साफ करें',
                'examples_title': 'उदाहरण प्रश्न',
                'thinking': 'सोच रहा हूँ...',
                'loading': 'लोड हो रहा है...'
            },
            'kn': {
                'ask_question': 'ನಿಮ್ಮ ಪ್ರಶ್ನೆ ಕೇಳಿ',
                'speak_button': '🎤 ಮಾತನಾಡಿ',
                'send_button': 'ಕಳುಹಿಸಿ',
                'listen_button': '🔊 ಕೇಳಿ',
                'clear_button': 'ಅಳಿಸಿ',
                'examples_title': 'ಉದಾಹರಣೆ ಪ್ರಶ್ನೆಗಳು',
                'thinking': 'ಯೋಚಿಸುತ್ತಿದೆ...',
                'loading': 'ಲೋಡ್ ಆಗುತ್ತಿದೆ...'
            },
            'te': {
                'ask_question': 'మీ ప్రశ్న అడగండి',
                'speak_button': '🎤 మాట్లాడండి',
                'send_button': 'పంపండి',
                'listen_button': '🔊 వినండి',
                'clear_button': 'తొలగించు',
                'examples_title': 'ఉదాహరణ ప్రశ్నలు',
                'thinking': 'ఆలోచిస్తోంది...',
                'loading': 'లోడ్ అవుతోంది...'
            },
            'ta': {
                'ask_question': 'உங்கள் கேள்வியைக் கேளுங்கள்',
                'speak_button': '🎤 பேசுங்கள்',
                'send_button': 'அனுப்பு',
                'listen_button': '🔊 கேளுங்கள்',
                'clear_button': 'அழி',
                'examples_title': 'உதாரண கேள்விகள்',
                'thinking': 'சிந்திக்கிறது...',
                'loading': 'ஏற்றுகிறது...'
            },
            'mr': {
                'ask_question': 'तुमचा प्रश्न विचारा',
                'speak_button': '🎤 बोला',
                'send_button': 'पाठवा',
                'listen_button': '🔊 ऐका',
                'clear_button': 'साफ करा',
                'examples_title': 'उदाहरण प्रश्न',
                'thinking': 'विचार करत आहे...',
                'loading': 'लोड होत आहे...'
            },
            'pa': {
                'ask_question': 'ਆਪਣਾ ਸਵਾਲ ਪੁੱਛੋ',
                'speak_button': '🎤 ਬੋਲੋ',
                'send_button': 'ਭੇਜੋ',
                'listen_button': '🔊 ਸੁਣੋ',
                'clear_button': 'ਸਾਫ਼ ਕਰੋ',
                'examples_title': 'ਉਦਾਹਰਨ ਸਵਾਲ',
                'thinking': 'ਸੋਚ ਰਿਹਾ ਹੈ...',
                'loading': 'ਲੋਡ ਹੋ ਰਿਹਾ ਹੈ...'
            }
        }
        
        return prompts.get(lang, prompts['en'])
    
    def get_example_questions(self, lang='hi'):
        """
        Get example questions in specified language
        
        Args:
            lang: Language code
            
        Returns:
            List of example questions
        """
        examples = {
            'en': [
                "What schemes are available for wheat farmers?",
                "Tell me about PM-KISAN eligibility",
                "How to grow rice organically?",
                "What is the price of cotton?",
                "Which subsidies are available in my state?"
            ],
            'hi': [
                "गेहूं किसानों के लिए कौन सी योजनाएं उपलब्ध हैं?",
                "पीएम-किसान पात्रता के बारे में बताएं",
                "जैविक तरीके से धान कैसे उगाएं?",
                "कपास की कीमत क्या है?",
                "मेरे राज्य में कौन सी सब्सिडी उपलब्ध हैं?"
            ],
            'kn': [
                "ಗೋಧಿ ರೈತರಿಗೆ ಯಾವ ಯೋಜನೆಗಳು ಲಭ್ಯವಿದೆ?",
                "ಪಿಎಂ-ಕಿಸಾನ್ ಅರ್ಹತೆ ಬಗ್ಗೆ ತಿಳಿಸಿ",
                "ಸಾವಯವ ವಿಧಾನದಿಂದ ಭತ್ತ ಬೆಳೆಯುವುದು ಹೇಗೆ?",
                "ಹತ್ತಿ ಬೆಲೆ ಎಷ್ಟು?",
                "ನನ್ನ ರಾಜ್ಯದಲ್ಲಿ ಯಾವ ಸಬ್ಸಿಡಿಗಳು ಲಭ್ಯವಿದೆ?"
            ],
            'te': [
                "గోధుమ రైతులకు ఏ పథకాలు అందుబాటులో ఉన్నాయి?",
                "పిఎం-కిసాన్ అర్హత గురించి చెప్పండి",
                "సేంద్రీయ పద్ధతిలో వరిని ఎలా పండించాలి?",
                "పత్తి ధర ఎంత?",
                "నా రాష్ట్రంలో ఏ సబ్సిడీలు అందుబాటులో ఉన్నాయి?"
            ],
            'ta': [
                "கோதுமை விவசாயிகளுக்கு என்ன திட்டங்கள் கிடைக்கின்றன?",
                "பிஎம்-கிசான் தகுதி பற்றி சொல்லுங்கள்",
                "இயற்கை முறையில் நெல் எவ்வாறு வளர்க்கலாம்?",
                "பருத்தி விலை என்ன?",
                "எனது மாநிலத்தில் என்ன மானியங்கள் கிடைக்கின்றன?"
            ]
        }
        
        return examples.get(lang, examples['en'])


# Singleton instance
_multilingual_instance = None

def get_multilingual_support():
    """Get or create multilingual support instance"""
    global _multilingual_instance
    if _multilingual_instance is None:
        _multilingual_instance = MultilingualSupport()
    return _multilingual_instance