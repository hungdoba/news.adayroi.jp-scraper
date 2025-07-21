#!/usr/bin/env python3
"""
Development setup script for the news scraper project.
"""
import os
import sys
import subprocess
from pathlib import Path
import logging
logger = logging.getLogger(__name__)


def run_command(command: str, description: str) -> bool:
    """Run a shell command and return success status."""
    logger.info(f"🔄 {description}...")
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        logger.info(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ {description} failed: {e}")
        logger.error(f"Error output: {e.stderr}")
        return False


def setup_environment():
    """Set up the development environment."""
    logger.info("🚀 Setting up news scraper development environment")

    # Check if Python 3.10+ is available
    try:
        result = subprocess.run(
            [sys.executable, "--version"], capture_output=True, text=True)
        version = result.stdout.strip()
        logger.info(f"📍 Using Python: {version}")

        # Extract version number
        version_parts = version.split()[1].split('.')
        major, minor = int(version_parts[0]), int(version_parts[1])
        if major < 3 or (major == 3 and minor < 10):
            logger.error("❌ Python 3.10 or higher is required")
            return False
    except Exception as e:
        logger.error(f"❌ Could not check Python version: {e}")
        return False

    # Create .env file if it doesn't exist
    env_file = Path(".env")
    env_example = Path(".env.example")

    if not env_file.exists() and env_example.exists():
        logger.info("📝 Creating .env file from template...")
        with open(env_example, 'r') as src, open(env_file, 'w') as dst:
            dst.write(src.read())
        logger.info(
            "✅ .env file created. Please edit it with your configuration.")

    # Create logs directory
    logs_dir = Path("logs")
    if not logs_dir.exists():
        logs_dir.mkdir(parents=True, exist_ok=True)
        logger.info("✅ Created logs directory")

    # Install dependencies
    commands = [
        ("pip install --upgrade pip", "Upgrading pip"),
        ("pip install -e .", "Installing project in development mode"),
        ("pip install -e .[dev]", "Installing development dependencies"),
    ]

    for command, description in commands:
        if not run_command(command, description):
            return False

    # Setup pre-commit hooks if available
    try:
        subprocess.run(["pre-commit", "--version"],
                       capture_output=True, check=True)
        run_command("pre-commit install", "Setting up pre-commit hooks")
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.warning("⚠️  pre-commit not available, skipping hook setup")

    logger.info("\n🎉 Development environment setup complete!")
    logger.info("\n📋 Next steps:")
    logger.info("1. Edit .env file with your configuration")
    logger.info("2. Run 'python src/main.py --help' to see available options")
    logger.info("3. Run 'python src/main.py' to start the pipeline")
    logger.info("4. Run 'python -m pytest tests/' to run tests")

    return True


if __name__ == "__main__":
    success = setup_environment()
    sys.exit(0 if success else 1)
