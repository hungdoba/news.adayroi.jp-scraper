#!/usr/bin/env python3
"""
Development setup script for the news scraper project.
"""
import os
import sys
import subprocess
from pathlib import Path


def run_command(command: str, description: str) -> bool:
    """Run a shell command and return success status."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False


def setup_environment():
    """Set up the development environment."""
    print("🚀 Setting up news scraper development environment")

    # Check if Python 3.10+ is available
    try:
        result = subprocess.run(
            [sys.executable, "--version"], capture_output=True, text=True)
        version = result.stdout.strip()
        print(f"📍 Using Python: {version}")

        # Extract version number
        version_parts = version.split()[1].split('.')
        major, minor = int(version_parts[0]), int(version_parts[1])
        if major < 3 or (major == 3 and minor < 10):
            print("❌ Python 3.10 or higher is required")
            return False
    except Exception as e:
        print(f"❌ Could not check Python version: {e}")
        return False

    # Create .env file if it doesn't exist
    env_file = Path(".env")
    env_example = Path(".env.example")

    if not env_file.exists() and env_example.exists():
        print("📝 Creating .env file from template...")
        with open(env_example, 'r') as src, open(env_file, 'w') as dst:
            dst.write(src.read())
        print("✅ .env file created. Please edit it with your configuration.")

    # Create logs directory
    logs_dir = Path("logs")
    if not logs_dir.exists():
        logs_dir.mkdir(parents=True, exist_ok=True)
        print("✅ Created logs directory")

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
        print("⚠️  pre-commit not available, skipping hook setup")

    print("\n🎉 Development environment setup complete!")
    print("\n📋 Next steps:")
    print("1. Edit .env file with your configuration")
    print("2. Run 'python src/main.py --help' to see available options")
    print("3. Run 'python src/main.py' to start the pipeline")
    print("4. Run 'python -m pytest tests/' to run tests")

    return True


if __name__ == "__main__":
    success = setup_environment()
    sys.exit(0 if success else 1)
