#!/bin/bash

echo "🚀 Setting up Django environment..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install required Python packages
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "⚠️ No requirements.txt found, skipping dependency installation."
fi

 
# Apply database migrations
python manage.py migrate

# Populate the database with fake ESP32 data
python scripts/populate_fake_data.py

echo "✅ Django setup complete!"
