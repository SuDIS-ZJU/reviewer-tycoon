#!/bin/bash
# start.sh - Easy startup script for i-am-your-reviewer

set -e

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$APP_DIR/.venv"

echo "======================================================="
echo " Starting Paper Review & Refinement Agent"
echo "======================================================="

cd "$APP_DIR"

if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment in $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
fi

echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

echo "Installing dependencies..."
pip install -r requirements.txt

# Create output directory for reviews
mkdir -p "$APP_DIR/review_outputs"

echo "Verifying LiteLLM status..."
python3 -c "import litellm; print('✅ LiteLLM successfully loaded.')" || {
    echo "❌ Failed to load LiteLLM. Please check your dependencies."
    exit 1
}

echo "Starting Streamlit App..."
python3 -m streamlit run app.py
