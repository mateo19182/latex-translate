"""Configuration management for LaTeX translation tool."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """Configuration for LaTeX translation."""
    
    # Required fields (no defaults)
    api_key: str
    source_lang: str
    target_lang: str
    
    # API Configuration (with defaults)
    endpoint: str = "https://openrouter.ai/api/v1"
    model: str = "google/gemini-2.0-flash-001"
    
    # Processing Configuration
    chunk_size: int = 3000
    max_tokens: int = 4000
    temperature: float = 0.1
    
    # Utility
    dry_run: bool = False
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if not self.api_key:
            raise ValueError("API key is required")
        
        if not self.source_lang or not self.target_lang:
            raise ValueError("Both source and target languages are required")
        
        if self.chunk_size <= 0:
            raise ValueError("Chunk size must be positive")
        
        if self.max_tokens <= 0:
            raise ValueError("Max tokens must be positive")
        
        if not 0 <= self.temperature <= 2:
            raise ValueError("Temperature must be between 0 and 2")
    
    @property
    def headers(self) -> dict:
        """Get HTTP headers for API requests."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        } 