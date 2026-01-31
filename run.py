"""
Launcher script for the news scraper application.

This script serves as the entry point for running the news scraper from the
project root directory. It properly sets up the Python path and delegates to
the main application module.

Usage (from project root after activating .venv):
    py run.py                        # Run full pipeline
    py run.py --step scrape          # Run specific step
    py run.py --help                 # Show help

Or simply run:
    run_scraper.bat                  # Windows batch file (activates .venv automatically)
"""
import sys
from pathlib import Path
from dotenv import load_dotenv

# Setup Python path and environment BEFORE any local imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Load environment variables from .env file
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

from main import main
if __name__ == "__main__":
    main()
