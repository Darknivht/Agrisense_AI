"""
AgriSense AI - Language Detection Utility
Intelligent language detection for Nigerian languages
"""

import re
from typing import Dict, List, Tuple, Any
import logging

class LanguageDetector:
    """Advanced language detection for Nigerian languages and English"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Language-specific keywords and patterns
        self.language_patterns = {
            'ha': {  # Hausa
                'keywords': [
                    'sannu', 'yaya', 'nawa', 'ina', 'yanayi', 'shuke', 'kwari', 'kasuwa',
                    'noma', 'gona', 'shinkafa', 'masara', 'rogo', 'wake', 'gyada',
                    'taki', 'ruwa', 'yashi', 'ciyawa', 'girbi', 'shuka', 'damina',
                    'rani', 'bazara', 'hunturu', 'farashin', 'sayar', 'siya', 'talla',
                    'shawara', 'tambaya', 'amsa', 'taimako', 'gargadi', 'sanarwa',
                    'da', 'na', 'ta', 'ya', 'mu', 'ku', 'su', 'ni', 'kai', 'ita'
                ],
                'common_words': ['da', 'na', 'ta', 'ya', 'mu', 'ku', 'su', 'a', 'don'],
                'greeting_patterns': [r'sannu\s+da\s+\w+', r'barka\s+da\s+\w+', r'ina\s+kwana'],
                'question_patterns': [r'yaya\s+\w+', r'me\s+\w+', r'wane\s+\w+', r'ina\s+\w+']
            },
            'yo': {  # Yoruba
                'keywords': [
                    'bawo', 'elo', 'nibi', 'oju ojo', 'eweko', 'kokoro', 'oja',
                    'agbe', 'oko', 'iresi', 'agbado', 'ata', 'ewa', 'epa',
                    'ajile', 'omi', 'ile', 'korikori', 'ikore', 'gbin', 'ojo',
                    'igba gbigbe', 'igba tutututu', 'owo', 'ta', 'ra', 'taja',
                    'imoran', 'beere', 'dahun', 'iranlowo', 'ikilọ', 'iwifun',
                    'ati', 'ni', 'ti', 'ko', 'wa', 'yin', 'won', 'mi', 'e', 'o'
                ],
                'common_words': ['ati', 'ni', 'ti', 'ko', 'wa', 'yin', 'won', 'si', 'fun'],
                'greeting_patterns': [r'bawo\s+\w+', r'pele\s+\w+', r'kaaro', r'kaale'],
                'question_patterns': [r'bawo\s+\w+', r'kini\s+\w+', r'ibo\s+\w+', r'elo\s+\w+']
            },
            'ig': {  # Igbo
                'keywords': [
                    'ndewo', 'kedu', 'ebe', 'ihu igwe', 'ihe okuku', 'umu ahuhu', 'ahia',
                    'oru ugbo', 'ubi', 'ji', 'oka', 'ose', 'akidi', 'ukwa',
                    'fatilayza', 'mmiri', 'ala', 'ahihia', 'owuwe', 'kuo', 'udu mmiri',
                    'oge okpomoku', 'oge oyi', 'ego', 're', 'zuo', 'ahia',
                    'ndumodu', 'ajuju', 'aziza', 'enyemaka', 'okwa', 'ozi',
                    'na', 'nke', 'ya', 'ndi', 'anyi', 'unu', 'ha', 'm', 'gi', 'o'
                ],
                'common_words': ['na', 'nke', 'ya', 'ndi', 'anyi', 'unu', 'ha', 'ka', 'maka'],
                'greeting_patterns': [r'ndewo\s+\w+', r'kedu\s+\w+', r'ututu oma', r'ehihie oma'],
                'question_patterns': [r'kedu\s+\w+', r'gini\s+\w+', r'ebe\s+\w+', r'mgbe\s+\w+']
            },
            'ff': {  # Fulfulde
                'keywords': [
                    'jam', 'hol', 'to', 'jemma', 'jiijal', 'marawle', 'luumo',
                    'wuurnde', 'galle', 'mbaɗi', 'mbari', 'koose', 'niebe', 'gerte',
                    'takka', 'ndiyam', 'leydi', 'ceeɗe', 'mbaɗde', 'hoor', 'ndungu',
                    'ceeɗu', 'dabbunde', 'keewɗe', 'jaar', 'sood', 'luul',
                    'waɗde', 'naamno', 'jaabol', 'wallita', 'haɓɓere', 'haal',
                    'e', 'no', 'o', 'men', 'en', 'on', 'ɓe', 'mi', 'a', 'maa'
                ],
                'common_words': ['e', 'no', 'o', 'men', 'en', 'on', 'ɓe', 'ko', 'ngam'],
                'greeting_patterns': [r'jam\s+\w+', r'on\s+jaɓa', r'hol\s+no'],
                'question_patterns': [r'hol\s+\w+', r'ko\s+\w+', r'to\s+\w+', r'hay\s+\w+']
            },
            'en': {  # English
                'keywords': [
                    'hello', 'how', 'what', 'where', 'weather', 'crop', 'pest', 'market',
                    'farming', 'agriculture', 'rice', 'maize', 'tomato', 'bean', 'groundnut',
                    'fertilizer', 'water', 'soil', 'grass', 'harvest', 'plant', 'rain',
                    'dry season', 'wet season', 'price', 'sell', 'buy', 'trade',
                    'advice', 'question', 'answer', 'help', 'alert', 'information',
                    'the', 'of', 'and', 'to', 'a', 'in', 'is', 'it', 'you', 'that'
                ],
                'common_words': ['the', 'of', 'and', 'to', 'a', 'in', 'is', 'it', 'you', 'for'],
                'greeting_patterns': [r'hello\s+\w+', r'good\s+\w+', r'hi\s+\w*'],
                'question_patterns': [r'how\s+\w+', r'what\s+\w+', r'where\s+\w+', r'when\s+\w+']
            }
        }
        
        # Agricultural domain keywords for context awareness
        self.agricultural_keywords = [
            'farm', 'crop', 'plant', 'soil', 'water', 'fertilizer', 'pest', 'disease',
            'harvest', 'yield', 'seed', 'irrigation', 'weather', 'rain', 'drought',
            'market', 'price', 'sell', 'buy', 'profit', 'livestock', 'cattle', 'poultry'
        ]
    
    def detect(self, text: str) -> str:
        """
        Detect the primary language of the given text
        
        Args:
            text (str): Text to analyze
            
        Returns:
            str: Language code ('en', 'ha', 'yo', 'ig', 'ff')
        """
        if not text or len(text.strip()) < 3:
            return 'en'  # Default to English for very short texts
        
        text_lower = text.lower().strip()
        
        # Calculate scores for each language
        language_scores = {}
        
        for lang_code, patterns in self.language_patterns.items():
            score = self._calculate_language_score(text_lower, patterns)
            language_scores[lang_code] = score
        
        # Get the language with the highest score
        detected_language = max(language_scores, key=language_scores.get)
        
        # If no clear winner and score is very low, default to English
        if language_scores[detected_language] < 0.1:
            detected_language = 'en'
        
        self.logger.info(f"Language detection: '{text[:50]}...' -> {detected_language} (scores: {language_scores})")
        
        return detected_language
    
    def detect_with_confidence(self, text: str) -> Tuple[str, float]:
        """
        Detect language with confidence score
        
        Args:
            text (str): Text to analyze
            
        Returns:
            Tuple[str, float]: (language_code, confidence_score)
        """
        if not text or len(text.strip()) < 3:
            return 'en', 0.5
        
        text_lower = text.lower().strip()
        language_scores = {}
        
        for lang_code, patterns in self.language_patterns.items():
            score = self._calculate_language_score(text_lower, patterns)
            language_scores[lang_code] = score
        
        # Sort scores and get top two
        sorted_scores = sorted(language_scores.items(), key=lambda x: x[1], reverse=True)
        top_language, top_score = sorted_scores[0]
        second_score = sorted_scores[1][1] if len(sorted_scores) > 1 else 0
        
        # Calculate confidence based on score difference
        confidence = min(1.0, max(0.1, top_score / max(second_score + 0.1, 0.1)))
        
        if top_score < 0.1:
            return 'en', 0.3
        
        return top_language, confidence
    
    def _calculate_language_score(self, text: str, patterns: Dict) -> float:
        """Calculate language score based on various patterns"""
        words = text.split()
        total_words = len(words)
        
        if total_words == 0:
            return 0.0
        
        score = 0.0
        
        # Keyword matching (weighted heavily)
        keyword_matches = 0
        for keyword in patterns['keywords']:
            if keyword in text:
                keyword_matches += text.count(keyword)
        
        keyword_score = keyword_matches / max(total_words, 1)
        score += keyword_score * 3.0
        
        # Common words frequency
        common_word_matches = 0
        for word in words:
            if word in patterns['common_words']:
                common_word_matches += 1
        
        common_word_score = common_word_matches / total_words
        score += common_word_score * 2.0
        
        # Greeting patterns
        greeting_score = 0.0
        for pattern in patterns['greeting_patterns']:
            if re.search(pattern, text):
                greeting_score += 1.0
        
        score += greeting_score * 1.5
        
        # Question patterns
        question_score = 0.0
        for pattern in patterns['question_patterns']:
            if re.search(pattern, text):
                question_score += 1.0
        
        score += question_score * 1.0
        
        # Normalize score
        return min(score, 5.0) / 5.0
    
    def is_agricultural_context(self, text: str) -> bool:
        """Check if text is related to agriculture"""
        text_lower = text.lower()
        agricultural_word_count = 0
        
        for keyword in self.agricultural_keywords:
            if keyword in text_lower:
                agricultural_word_count += text_lower.count(keyword)
        
        words = text_lower.split()
        return agricultural_word_count / max(len(words), 1) > 0.1
    
    def get_language_name(self, language_code: str) -> str:
        """Get full language name from code"""
        language_names = {
            'en': 'English',
            'ha': 'Hausa',
            'yo': 'Yoruba',
            'ig': 'Igbo',
            'ff': 'Fulfulde'
        }
        return language_names.get(language_code, 'English')
    
    def get_supported_languages(self) -> List[Dict[str, str]]:
        """Get list of supported languages with codes and names"""
        return [
            {'code': 'en', 'name': 'English', 'native_name': 'English'},
            {'code': 'ha', 'name': 'Hausa', 'native_name': 'Hausa'},
            {'code': 'yo', 'name': 'Yoruba', 'native_name': 'Yorùbá'},
            {'code': 'ig', 'name': 'Igbo', 'native_name': 'Igbo'},
            {'code': 'ff', 'name': 'Fulfulde', 'native_name': 'Fulfulde'}
        ]
    
    def detect_mixed_language(self, text: str) -> Dict[str, float]:
        """Detect multiple languages in text and return proportions"""
        sentences = re.split(r'[.!?]+', text)
        language_counts = {}
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10:  # Only process substantial sentences
                lang = self.detect(sentence)
                language_counts[lang] = language_counts.get(lang, 0) + 1
        
        total_sentences = sum(language_counts.values())
        if total_sentences == 0:
            return {'en': 1.0}
        
        # Convert to proportions
        language_proportions = {
            lang: count / total_sentences 
            for lang, count in language_counts.items()
        }
        
        return language_proportions
    
    def suggest_language_switch(self, text: str, current_language: str) -> str:
        """Suggest language switch if text is in different language"""
        detected_language = self.detect(text)
        
        if detected_language != current_language:
            return detected_language
        
        return current_language
    
    def validate_language_code(self, language_code: str) -> bool:
        """Validate if language code is supported"""
        return language_code in self.language_patterns
    
    def get_language_statistics(self, texts: List[str]) -> Dict[str, Any]:
        """Analyze language usage across multiple texts"""
        if not texts:
            return {}
        
        language_counts = {}
        total_texts = len(texts)
        
        for text in texts:
            lang = self.detect(text)
            language_counts[lang] = language_counts.get(lang, 0) + 1
        
        statistics = {
            'total_texts': total_texts,
            'languages_detected': len(language_counts),
            'language_distribution': {
                lang: {
                    'count': count,
                    'percentage': (count / total_texts) * 100
                }
                for lang, count in language_counts.items()
            },
            'dominant_language': max(language_counts, key=language_counts.get),
            'multilingual': len(language_counts) > 1
        }
        
        return statistics