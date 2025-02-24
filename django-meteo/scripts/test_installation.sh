#!/bin/bash

echo "🚀 Running Django Installation Tests..."

# Move to the Django project root directory
cd "$(dirname "$0")/.." || exit

# 1️⃣ Check if Virtual Environment Exists
if [ -d "venv" ]; then
    echo "✅ Virtual environment exists."
else
    echo "❌ Virtual environment missing! Run ./scripts/setup_production.sh to set up Django."
    exit 1
fi

# 2️⃣ Activate Virtual Environment
source venv/bin/activate

# 3️⃣ Check if Django is Installed
if python -c "import django" &> /dev/null; then
    echo "✅ Django is installed."
else
    echo "❌ Django is NOT installed! Run ./scripts/setup_production.sh"
    exit 1
fi

# 4️⃣ Check Database Tables
echo "🔍 Checking database tables..."
python manage.py showmigrations api | grep '[X]'
if [ $? -eq 0 ]; then
    echo "✅ Database tables are migrated."
else
    echo "❌ Database migrations are missing! Run: python manage.py migrate"
    exit 1
fi

echo "🔍 Checking for fake ESP32 data..."

# Capture the output of the Python script
FAKE_DATA_CHECK=$(python manage.py shell <<EOF
from api.models import Station
stations = ["esp32-001", "esp32-002", "esp32-003"]
existing_stations = [s for s in stations if Station.objects.filter(station_ref=s).exists()]
print(len(existing_stations))
EOF
)

# Check if we have all 3 stations
if [[ "$FAKE_DATA_CHECK" -eq 3 ]]; then
    echo "✅ All 3 ESP32 stations exist in the database."
else
    echo "❌ Missing stations! Expected 3, but found $FAKE_DATA_CHECK. Run: python scripts/populate_fake_data.py"
    exit 1
fi


# 6️⃣ Check If Django Can Start
echo "🔍 Starting Django server test..."
python manage.py check

if [ $? -eq 0 ]; then
    echo "✅ Django application is running properly!"
else
    echo "❌ Django check failed! Fix any errors before proceeding."
    exit 1
fi

echo "🎉 All tests passed! Django installation is correct."
exit 0
