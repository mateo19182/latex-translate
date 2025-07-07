"""Simple LaTeX translator that lets the LLM handle structure preservation."""

import logging
import re
from pathlib import Path
from typing import List
import time
import tiktoken
from concurrent.futures import ThreadPoolExecutor, as_completed

from .config import Config
from .llm_client import LLMClient


class SimpleLatexTranslator:
    """Simple translator that chunks text naturally and lets LLM preserve LaTeX."""
    
    def __init__(self, config: Config, max_workers: int = 3):
        self.config = config
        self.max_workers = max_workers
        self.logger = logging.getLogger(__name__)
        self.llm_client = LLMClient(config)
        
        # Initialize tokenizer for chunk size estimation
        try:
            self.tokenizer = tiktoken.encoding_for_model(config.model)
        except KeyError:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
        
        # Test API connection
        if not self.llm_client.test_connection():
            raise ConnectionError("Failed to connect to LLM API")
    
    def translate_file(self, input_file: Path, output_file: Path) -> bool:
        """Translate a LaTeX file using simple chunking."""
        try:
            self.logger.info(f"Starting translation: {input_file} -> {output_file}")
            
            # Read the file
            content = self._read_file(input_file)
            
            # Create chunks
            chunks = self._create_simple_chunks(content)
            self.logger.info(f"Created {len(chunks)} chunks")
            
            # Translate chunks in parallel
            translated_chunks = self._translate_chunks_parallel(chunks)
            
            # Combine translated chunks
            translated_content = ''.join(translated_chunks)
            
            # Write output
            self._write_file(output_file, translated_content)
            
            self.logger.info(f"Translation completed: {output_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Translation failed: {e}")
            if self.config.dry_run:
                return True
            raise
    
    def _create_simple_chunks(self, content: str) -> List[str]:
        """Create chunks by natural boundaries - sections, then paragraphs."""
        
        # First try to split by LaTeX sections
        section_pattern = r'(\\(?:chapter|section|subsection|subsubsection)\{[^}]*\})'
        sections = re.split(section_pattern, content)
        
        chunks = []
        current_chunk = ""
        
        for section in sections:
            if not section.strip():
                continue
            
            # Check if adding this section would exceed chunk size
            potential_chunk = current_chunk + section
            if self._count_tokens(potential_chunk) > self.config.chunk_size and current_chunk:
                # Current chunk is big enough, save it and start new one
                chunks.append(current_chunk)
                current_chunk = section
            else:
                current_chunk += section
        
        # Add the last chunk
        if current_chunk.strip():
            chunks.append(current_chunk)
        
        # If we only got one chunk and it's too big, split by paragraphs
        if len(chunks) == 1 and self._count_tokens(chunks[0]) > self.config.chunk_size:
            return self._split_by_paragraphs(chunks[0])
        
        return chunks
    
    def _split_by_paragraphs(self, text: str) -> List[str]:
        """Split text by paragraphs when section splitting isn't enough."""
        # Split by double newlines (paragraph breaks)
        paragraphs = re.split(r'\n\s*\n', text)
        
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            if not paragraph.strip():
                continue
            
            # Add paragraph separator back
            paragraph_with_separator = paragraph + "\n\n"
            
            # Check if adding this paragraph would exceed chunk size
            potential_chunk = current_chunk + paragraph_with_separator
            if self._count_tokens(potential_chunk) > self.config.chunk_size and current_chunk:
                chunks.append(current_chunk.rstrip())
                current_chunk = paragraph_with_separator
            else:
                current_chunk += paragraph_with_separator
        
        # Add the last chunk
        if current_chunk.strip():
            chunks.append(current_chunk.rstrip())
        
        return chunks
    
    def _translate_chunks_parallel(self, chunks: List[str]) -> List[str]:
        """Translate chunks in parallel using ThreadPoolExecutor."""
        if self.config.dry_run:
            # For dry run, just simulate translation
            for i, chunk in enumerate(chunks, 1):
                self.logger.info(f"[DRY RUN] Translating chunk {i}/{len(chunks)}")
                if chunk.strip():
                    self.llm_client.translate_text(chunk)  # This will log the dry run message
            return chunks
        
        translated_chunks = [None] * len(chunks)  # Pre-allocate list to maintain order
        
        def translate_chunk_with_index(chunk_info):
            index, chunk = chunk_info
            if not chunk.strip():
                return index, chunk
            
            self.logger.info(f"Translating chunk {index + 1}/{len(chunks)}")
            translated = self.llm_client.translate_text(chunk)
            return index, translated
        
        # Use ThreadPoolExecutor for parallel translation
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all translation tasks
            chunk_infos = [(i, chunk) for i, chunk in enumerate(chunks)]
            future_to_index = {
                executor.submit(translate_chunk_with_index, chunk_info): chunk_info[0] 
                for chunk_info in chunk_infos
            }
            
            # Collect results as they complete
            completed = 0
            for future in as_completed(future_to_index):
                try:
                    index, translated_chunk = future.result()
                    translated_chunks[index] = translated_chunk
                    completed += 1
                    self.logger.info(f"Completed {completed}/{len(chunks)} chunks")
                except Exception as e:
                    index = future_to_index[future]
                    self.logger.error(f"Failed to translate chunk {index + 1}: {e}")
                    # Use original chunk as fallback
                    translated_chunks[index] = chunks[index]
        
        self.logger.info(f"Parallel translation completed for {len(chunks)} chunks")
        return translated_chunks
    
    def _count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        try:
            return len(self.tokenizer.encode(text))
        except:
            # Fallback estimate
            return len(text.split()) * 1.3
    
    def _read_file(self, file_path: Path) -> str:
        """Read file content."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
    
    def _write_file(self, file_path: Path, content: str) -> None:
        """Write file content."""
        if self.config.dry_run:
            self.logger.info(f"[DRY RUN] Would write {len(content)} characters to {file_path}")
            return
        
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content) 