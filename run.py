#!/usr/bin/env python3
"""
Launcher script for the news scraper application.

This script serves as the entry point for running the news scraper from the
project root directory. It properly sets up the Python path and delegates to
the main application module.

Usage:
    python run.py                    # Run full pipeline
    python run.py --step scrape      # Run specific step
    python run.py --help             # Show help
"""
import sys
from pathlib import Path

# Add src directory to Python path BEFORE importing
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from main import main
# Import and run the main application

if __name__ == "__main__":
    main()
