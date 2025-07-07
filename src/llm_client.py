"""LLM client for translation using OpenAI-compatible APIs."""

import json
import logging
import time
from typing import Dict, List, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .config import Config


class LLMClient:
    """Client for interacting with OpenAI-compatible LLM APIs."""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Setup session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def translate_text(self, text: str) -> str:
        """Translate a piece of text using the LLM."""
        if self.config.dry_run:
            self.logger.info(f"[DRY RUN] Would translate: {text[:100]}...")
            return f"[TRANSLATED] {text}"
        
        prompt = self._create_translation_prompt(text)
        
        try:
            response = self._make_api_call(prompt)
            translated_text = self._extract_translation(response)
            
            self.logger.debug(f"Translated: '{text[:50]}...' -> '{translated_text[:50]}...'")
            return translated_text
            
        except Exception as e:
            self.logger.error(f"Translation failed for text: {text[:100]}...")
            self.logger.error(f"Error: {e}")
            # Return original text on failure
            return text
    
    def translate_batch(self, texts: List[str]) -> Dict[str, str]:
        """Translate multiple texts in a batch."""
        translations = {}
        
        for text in texts:
            if text.strip():  # Only translate non-empty text
                translations[text] = self.translate_text(text)
            else:
                translations[text] = text
        
        return translations
    
    def _create_translation_prompt(self, text: str) -> str:
        """Create a prompt for translating text while preserving LaTeX structure."""
        return f"""Translate from {self.config.source_lang} to {self.config.target_lang}. Preserve ALL LaTeX commands, citations, references, labels, and math exactly as they are. Only translate the readable text content.

Return ONLY the translated LaTeX code with no explanations, no "Here is the translation:", no prefixes - just start directly with the translated content.

{text}"""
    
    def _make_api_call(self, prompt: str) -> dict:
        """Make API call to the LLM service."""
        payload = {
            "model": self.config.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
        }
        
        # Add OpenRouter specific headers if using OpenRouter
        headers = self.config.headers.copy()
        if "openrouter.ai" in self.config.endpoint:
            headers["HTTP-Referer"] = "https://github.com/latex-translate/latex-translate"
            headers["X-Title"] = "LaTeX Translation Tool"
        
        self.logger.debug(f"Making API call to {self.config.endpoint}")
        
        response = self.session.post(
            f"{self.config.endpoint}/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code == 429:
            # Rate limited, wait and retry
            retry_after = int(response.headers.get('Retry-After', 60))
            self.logger.warning(f"Rate limited. Waiting {retry_after} seconds...")
            time.sleep(retry_after)
            return self._make_api_call(prompt)
        
        response.raise_for_status()
        return response.json()
    
    def _extract_translation(self, response: dict) -> str:
        """Extract the translated text from the API response."""
        try:
            content = response['choices'][0]['message']['content']
            
            # Clean up the response
            content = content.strip()
            
            # Remove common prefixes that models might add
            prefixes_to_remove = [
                "TRANSLATION:",
                "Translation:",
                "Here is the translation:",
                "The translation is:",
            ]
            
            for prefix in prefixes_to_remove:
                if content.startswith(prefix):
                    content = content[len(prefix):].strip()
            
            return content
            
        except (KeyError, IndexError) as e:
            self.logger.error(f"Failed to extract translation from response: {e}")
            self.logger.error(f"Response: {response}")
            raise ValueError("Invalid API response format")
    
    def test_connection(self) -> bool:
        """Test if the API connection is working."""
        if self.config.dry_run:
            self.logger.info("[DRY RUN] Skipping connection test")
            return True
        
        try:
            test_prompt = self._create_translation_prompt("Hello world")
            response = self._make_api_call(test_prompt)
            self.logger.info("API connection test successful")
            return True
            
        except Exception as e:
            self.logger.error(f"API connection test failed: {e}")
            return False 