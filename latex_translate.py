#!/usr/bin/env python3
"""
LaTeX Translation CLI Tool

A command-line tool that translates LaTeX files using LLM APIs while preserving
mathematical formulas, citations, labels, and LaTeX structure.
"""

import argparse
import sys
import os
import logging
from pathlib import Path
from typing import List

from src.simple_translator import SimpleLatexTranslator
from src.config import Config


def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def validate_files(file_paths: List[str]) -> List[Path]:
    """Validate inputs and collect all .tex files (from files and directories)."""
    valid_files = []
    
    for file_path in file_paths:
        path = Path(file_path)
        
        if not path.exists():
            logging.error(f"Path not found: {file_path}")
            sys.exit(1)
        
        if path.is_file():
            # It's a file - check if it's a .tex file
            if not path.suffix.lower() == '.tex':
                logging.error(f"File must have .tex extension: {file_path}")
                sys.exit(1)
            valid_files.append(path)
            
        elif path.is_dir():
            # It's a directory - find all .tex files recursively
            tex_files = list(path.rglob("*.tex"))
            if not tex_files:
                logging.warning(f"No .tex files found in directory: {file_path}")
            else:
                logging.info(f"Found {len(tex_files)} .tex files in {file_path}")
                valid_files.extend(tex_files)
        else:
            logging.error(f"Path is neither file nor directory: {file_path}")
            sys.exit(1)
    
    return valid_files


def main():
    parser = argparse.ArgumentParser(
        description="Translate LaTeX files using LLM APIs while preserving structure",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -i file1.tex file2.tex -o translated/ --source-lang galician --target-lang english
  %(prog)s -i chapter_directory/ --api-key sk-xxx --source-lang spanish --target-lang english
  %(prog)s -i *.tex --api-key sk-xxx --endpoint https://openrouter.ai/api/v1 --model gpt-4
        """
    )
    
    # Input/Output arguments
    parser.add_argument(
        '-i', '--input',
        nargs='+',
        required=True,
        help='Input .tex files or directories containing .tex files to translate'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='./translated',
        help='Output directory for translated files (default: ./translated)'
    )
    
    # Language arguments
    parser.add_argument(
        '--source-lang',
        required=True,
        help='Source language (e.g., "galician", "spanish", "english")'
    )
    
    parser.add_argument(
        '--target-lang', 
        required=True,
        help='Target language (e.g., "english", "spanish", "french")'
    )
    
    # API Configuration
    parser.add_argument(
        '--api-key',
        required=True,
        help='API key for the LLM service'
    )
    
    parser.add_argument(
        '--endpoint',
        default='https://openrouter.ai/api/v1',
        help='API endpoint URL (default: OpenRouter)'
    )
    
    parser.add_argument(
        '--model',
        default='anthropic/claude-3.5-sonnet',
        help='Model to use for translation (default: claude-3.5-sonnet)'
    )
    
    # Chunking and processing arguments
    parser.add_argument(
        '--chunk-size',
        type=int,
        default=3000,
        help='Target chunk size in tokens (default: 3000)'
    )
    
    parser.add_argument(
        '--max-tokens',
        type=int,
        default=4000,
        help='Maximum tokens for API response (default: 4000)'
    )
    
    parser.add_argument(
        '--temperature',
        type=float,
        default=0.1,
        help='Temperature for translation (default: 0.1)'
    )
    
    parser.add_argument(
        '--parallel',
        type=int,
        default=3,
        help='Number of parallel translation workers (default: 3)'
    )
    
    # Utility arguments
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be translated without making API calls'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Validate input files
    input_files = validate_files(args.input)
    logging.info(f"Found {len(input_files)} .tex files to translate")
    
    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    logging.info(f"Output directory: {output_dir}")
    
    # Create configuration
    config = Config(
        api_key=args.api_key,
        endpoint=args.endpoint,
        model=args.model,
        source_lang=args.source_lang,
        target_lang=args.target_lang,
        chunk_size=args.chunk_size,
        max_tokens=args.max_tokens,
        temperature=args.temperature,
        dry_run=args.dry_run
    )
    
    # Initialize translator
    translator = SimpleLatexTranslator(config, max_workers=args.parallel)
    
    try:
        # Process each file
        for input_file in input_files:
            logging.info(f"Processing: {input_file}")
            
            # Generate output filename
            output_file = output_dir / f"{input_file.stem}_{args.target_lang}{input_file.suffix}"
            
            # Translate the file
            translator.translate_file(input_file, output_file)
            
        logging.info("Translation completed successfully!")
        
    except KeyboardInterrupt:
        logging.info("Translation interrupted by user")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Translation failed: {e}")
        if args.verbose:
            logging.exception("Full error details:")
        sys.exit(1)


if __name__ == '__main__':
    main() 