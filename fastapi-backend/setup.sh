#!/bin/bash

# CTMS FastAPI Backend Setup Script

echo "🚀 Setting up CTMS FastAPI Backend..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.10 or higher."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

echo "✅ uv found: $(uv --version)"

# Create virtual environment with uv
echo "📦 Creating virtual environment with uv..."
uv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies with uv
echo "📚 Installing dependencies with uv..."
uv pip install -e ".[dev]"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "⚙️  Creating .env file..."
    cp .env.example .env
    
    # Generate a secure secret key
    SECRET_KEY=$(openssl rand -hex 32)
    
    # Update SECRET_KEY in .env
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/your-secret-key-here-change-this-in-production-use-openssl-rand-hex-32/$SECRET_KEY/" .env
    else
        # Linux
        sed -i "s/your-secret-key-here-change-this-in-production-use-openssl-rand-hex-32/$SECRET_KEY/" .env
    fi
    
    echo "✅ .env file created with secure secret key"
else
    echo "ℹ️  .env file already exists, skipping..."
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the server:"
echo "  1. Activate virtual environment: source .venv/bin/activate"
echo "  2. Run the server: python run.py"
echo ""
echo "Or run directly: .venv/bin/python run.py"
echo ""
echo "API will be available at: http://localhost:8000"
echo "API docs: http://localhost:8000/docs"
