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

# Check if migrations need to be made
echo "⚙️ Running database migrations..."
python manage.py makemigrations
#python manage.py migrate

# OPTIONAL: If you want a fresh database, uncomment below:
echo "🔥 Resetting database..."
python manage.py flush --no-input  # Clears all data but keeps tables
rm db.sqlite3 && python manage.py migrate  # Wipes everything (Use with caution)

# Populate the database with test ESP32 data
if [ -f "scripts/populate_fake_data.py" ]; then
    echo "📡 Populating fake ESP32 data..."
    python scripts/populate_fake_data.py
else
    echo "⚠️ No populate_fake_data.py script found, skipping."
fi

echo "✅ Django setup complete!"
