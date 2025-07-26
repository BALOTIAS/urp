#!/bin/bash

# Unofficial Retro Patch Setup Script
# This script helps set up the development environment

set -e

echo "🎮 Unofficial Retro Patch Setup"
echo "================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "✅ Python $PYTHON_VERSION detected"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
if [ -f "Pipfile" ]; then
    pipenv install --dev
else
    pip install -e ".[dev]"
fi

# Install pre-commit hooks
if command -v pre-commit &> /dev/null; then
    echo "🔗 Installing pre-commit hooks..."
    pre-commit install
else
    echo "⚠️  pre-commit not found. Install it with: pip install pre-commit"
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your game paths"
echo "2. Run tests: make test"
echo "3. Start development: make help"
echo ""
echo "For help: make help"